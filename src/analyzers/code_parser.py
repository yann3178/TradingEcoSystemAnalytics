"""
Parser de Code PowerLanguage
============================
Extraction et analyse du code source des stratégies MultiCharts.
"""

import re
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

import sys
V2_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(V2_ROOT))

from src.utils.file_utils import safe_read, clean_strategy_name


# =============================================================================
# STRUCTURES DE DONNÉES
# =============================================================================

@dataclass
class StrategyCode:
    """Représente le code source d'une stratégie analysée."""
    
    name: str  # Nom nettoyé de la stratégie
    filename: str  # Nom du fichier original
    filepath: Path  # Chemin complet
    code: str  # Code source brut
    code_hash: str  # Hash SHA-256 pour détection de modifications
    
    # Métadonnées extraites
    inputs: Dict[str, float] = field(default_factory=dict)
    variables: Dict[str, float] = field(default_factory=dict)
    
    # Indicateurs de risque
    has_stoploss: bool = False
    has_profittarget: bool = False
    has_exitonclose: bool = False
    has_time_exit: bool = False
    
    # Valeurs extraites
    stoploss_values: List[float] = field(default_factory=list)
    profittarget_values: List[float] = field(default_factory=list)
    
    # Complexité
    nb_lines: int = 0
    nb_code_lines: int = 0
    nb_comments: int = 0
    nb_inputs: int = 0
    nb_conditions: int = 0


# =============================================================================
# PARSER DE CODE
# =============================================================================

class CodeParser:
    """Parser pour le code PowerLanguage MultiCharts."""
    
    # Regex patterns précompilés
    RE_INPUT = re.compile(r'(?is)\bInputs?\s*:(.*?);')
    RE_VAR = re.compile(r'(?is)\bVars?\s*:(.*?);')
    RE_NAMED_VALUE = re.compile(r'([A-Za-z_]\w*)\s*\(\s*([-+]?\d*\.?\d+)\s*\)')
    RE_STOPLOSS = re.compile(r'SetStopLoss(?:_pt)?\s*\(\s*([-+]?\d*\.?\d+|[A-Za-z_]\w*)', re.IGNORECASE)
    RE_PROFITTARGET = re.compile(r'SetProfitTarget(?:_pt)?\s*\(\s*([-+]?\d*\.?\d+|[A-Za-z_]\w*)', re.IGNORECASE)
    RE_EXITONCLOSE = re.compile(r'SetExitOnClose', re.IGNORECASE)
    RE_CONDITION = re.compile(r'\b(if|and|or)\b', re.IGNORECASE)
    
    def __init__(self, strategies_dir: Path, functions_dir: Optional[Path] = None):
        """
        Initialise le parser.
        
        Args:
            strategies_dir: Répertoire contenant les stratégies
            functions_dir: Répertoire contenant les fonctions (optionnel)
        """
        self.strategies_dir = Path(strategies_dir)
        self.functions_dir = Path(functions_dir) if functions_dir else None
        
        # Cache des fonctions clés
        self._functions_cache: Dict[str, str] = {}
        self._functions_context: str = ""
        
        # Charger les fonctions clés si disponibles
        if self.functions_dir and self.functions_dir.exists():
            self._load_key_functions()
    
    def _load_key_functions(self):
        """Charge les fonctions clés (_OHLCMulti5, PatternFast)."""
        target_names = ['ohlcmulti', 'patternfast', '_ohlcmulti']
        
        for func_file in self.functions_dir.glob("*.txt"):
            func_name_clean = clean_strategy_name(func_file.name).lower()
            
            # Vérifier si c'est une fonction clé
            if any(target in func_name_clean for target in target_names):
                func_code = safe_read(func_file)
                original_name = clean_strategy_name(func_file.name)
                self._functions_cache[original_name] = func_code
        
        # Construire le contexte pour le prompt
        if self._functions_cache:
            self._functions_context = "# KEY FUNCTIONS AVAILABLE\n\n"
            self._functions_context += "These critical functions are used in many strategies:\n\n"
            
            for func_name, func_code in self._functions_cache.items():
                self._functions_context += f"## Function: {func_name}\n\n"
                self._functions_context += "```powerlanguage\n"
                self._functions_context += func_code
                self._functions_context += "\n```\n\n"
    
    @property
    def functions_context(self) -> str:
        """Retourne le contexte des fonctions pour le prompt."""
        return self._functions_context
    
    def list_strategy_files(self) -> List[Path]:
        """Liste tous les fichiers de stratégies disponibles."""
        if not self.strategies_dir.exists():
            return []
        
        files = list(self.strategies_dir.glob("*.txt"))
        # Trier par nom
        files.sort(key=lambda p: p.name.lower())
        return files
    
    def parse_file(self, filepath: Path) -> StrategyCode:
        """
        Parse un fichier de stratégie.
        
        Args:
            filepath: Chemin du fichier
            
        Returns:
            StrategyCode avec toutes les métadonnées extraites
        """
        code = safe_read(filepath)
        code_hash = hashlib.sha256(code.encode('utf-8')).hexdigest()
        
        strategy = StrategyCode(
            name=clean_strategy_name(filepath.name),
            filename=filepath.name,
            filepath=filepath,
            code=code,
            code_hash=code_hash,
        )
        
        # Analyser le code
        self._parse_inputs_and_vars(strategy)
        self._parse_risk_management(strategy)
        self._parse_complexity(strategy)
        
        return strategy
    
    def _parse_inputs_and_vars(self, strategy: StrategyCode):
        """Extrait les inputs et variables avec leurs valeurs par défaut."""
        code = strategy.code
        
        # Inputs
        for match in self.RE_INPUT.finditer(code):
            block = match.group(1)
            for m in self.RE_NAMED_VALUE.finditer(block):
                name = m.group(1).lower()
                try:
                    value = float(m.group(2))
                    strategy.inputs[name] = value
                except ValueError:
                    pass
        
        # Variables
        for match in self.RE_VAR.finditer(code):
            block = match.group(1)
            for m in self.RE_NAMED_VALUE.finditer(block):
                name = m.group(1).lower()
                try:
                    value = float(m.group(2))
                    strategy.variables[name] = value
                except ValueError:
                    pass
        
        strategy.nb_inputs = len(strategy.inputs)
    
    def _parse_risk_management(self, strategy: StrategyCode):
        """Extrait les informations de gestion du risque."""
        code = strategy.code
        code_lower = code.lower()
        
        # Combiné: inputs + variables pour résolution des noms
        name_map = {**strategy.inputs, **strategy.variables}
        
        # StopLoss
        strategy.has_stoploss = 'setstoploss' in code_lower
        if strategy.has_stoploss:
            for match in self.RE_STOPLOSS.finditer(code):
                value = match.group(1)
                try:
                    strategy.stoploss_values.append(float(value))
                except ValueError:
                    # C'est un nom de variable
                    var_name = value.lower()
                    if var_name in name_map:
                        strategy.stoploss_values.append(name_map[var_name])
        
        # ProfitTarget
        strategy.has_profittarget = 'setprofittarget' in code_lower
        if strategy.has_profittarget:
            for match in self.RE_PROFITTARGET.finditer(code):
                value = match.group(1)
                try:
                    strategy.profittarget_values.append(float(value))
                except ValueError:
                    var_name = value.lower()
                    if var_name in name_map:
                        strategy.profittarget_values.append(name_map[var_name])
        
        # ExitOnClose
        strategy.has_exitonclose = bool(self.RE_EXITONCLOSE.search(code))
        
        # Time Exit (détection heuristique)
        time_patterns = [
            r'time\s*>=?\s*\d{3,4}',
            r'time\s*<=?\s*\d{3,4}',
            r't\s*>=?\s*\d{3,4}',
            r'exittime',
            r'closetime',
        ]
        for pattern in time_patterns:
            if re.search(pattern, code_lower):
                strategy.has_time_exit = True
                break
    
    def _parse_complexity(self, strategy: StrategyCode):
        """Calcule les métriques de complexité."""
        lines = strategy.code.splitlines()
        
        strategy.nb_lines = len(lines)
        strategy.nb_comments = sum(1 for l in lines if l.strip().startswith('//'))
        strategy.nb_code_lines = sum(
            1 for l in lines 
            if l.strip() and not l.strip().startswith('//')
        )
        
        # Nombre de conditions
        strategy.nb_conditions = len(self.RE_CONDITION.findall(strategy.code))
    
    def find_strategy_file(
        self, 
        strategy_name: str, 
        strategy_files: Optional[List[Path]] = None
    ) -> Optional[Path]:
        """
        Trouve le fichier correspondant à un nom de stratégie.
        
        Utilise le matching flou si nécessaire.
        
        Args:
            strategy_name: Nom de la stratégie recherchée
            strategy_files: Liste de fichiers (optionnel, sinon rechargé)
            
        Returns:
            Path du fichier trouvé ou None
        """
        if strategy_files is None:
            strategy_files = self.list_strategy_files()
        
        if not strategy_files:
            return None
        
        # Import du module matching
        from src.utils.matching import normalize_strategy_name, find_best_match
        
        target_norm = normalize_strategy_name(strategy_name)
        
        # Phase 1: Match exact
        for f in strategy_files:
            file_norm = normalize_strategy_name(clean_strategy_name(f.name))
            if target_norm == file_norm:
                return f
        
        # Phase 2: Fuzzy match
        file_names = [f.name for f in strategy_files]
        match, score = find_best_match(strategy_name, file_names, threshold=0.80)
        
        if match:
            for f in strategy_files:
                if f.name == match:
                    return f
        
        return None
    
    def get_code_summary(self, strategy: StrategyCode) -> Dict:
        """
        Retourne un résumé du code pour l'affichage.
        
        Args:
            strategy: StrategyCode à résumer
            
        Returns:
            Dict avec les métriques clés
        """
        return {
            'name': strategy.name,
            'lines_total': strategy.nb_lines,
            'lines_code': strategy.nb_code_lines,
            'lines_comments': strategy.nb_comments,
            'nb_inputs': strategy.nb_inputs,
            'has_stoploss': strategy.has_stoploss,
            'has_profittarget': strategy.has_profittarget,
            'has_exitonclose': strategy.has_exitonclose,
            'has_time_exit': strategy.has_time_exit,
            'stoploss_min': min(strategy.stoploss_values) if strategy.stoploss_values else None,
            'profittarget_min': min(strategy.profittarget_values) if strategy.profittarget_values else None,
            'nb_conditions': strategy.nb_conditions,
            'code_hash': strategy.code_hash[:12],
        }


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def compute_code_hash(code: str) -> str:
    """Calcule le hash SHA-256 du code."""
    return hashlib.sha256(code.encode('utf-8')).hexdigest()


def extract_function_calls(code: str) -> List[str]:
    """
    Extrait les appels de fonction du code.
    
    Retourne les noms de fonctions avec leurs paramètres.
    """
    # Pattern pour les appels de fonction PowerLanguage
    pattern = re.compile(r'([A-Za-z_]\w*)\s*\(([^)]*)\)', re.IGNORECASE)
    
    # Mots-clés à exclure (pas des fonctions)
    keywords = {
        'if', 'then', 'else', 'begin', 'end', 'for', 'to', 'downto',
        'while', 'repeat', 'until', 'and', 'or', 'not', 'true', 'false',
        'buy', 'sell', 'exitlong', 'exitshort', 'var', 'vars', 'input',
        'inputs', 'array', 'once', 'mod'
    }
    
    functions = []
    for match in pattern.finditer(code):
        func_name = match.group(1)
        if func_name.lower() not in keywords:
            full_call = f"{func_name}({match.group(2).strip()})"
            if full_call not in functions:
                functions.append(full_call)
    
    return functions


if __name__ == "__main__":
    # Test du parser
    from pathlib import Path
    
    # Chemins de test
    strategies_dir = Path(r"C:\MC_Export_Code\clean\Strategies")
    functions_dir = Path(r"C:\MC_Export_Code\clean\Functions")
    
    if strategies_dir.exists():
        parser = CodeParser(strategies_dir, functions_dir)
        
        print(f"📚 {len(parser._functions_cache)} fonctions clés chargées")
        
        files = parser.list_strategy_files()
        print(f"📁 {len(files)} fichiers de stratégies trouvés")
        
        if files:
            # Analyser la première stratégie
            strat = parser.parse_file(files[0])
            summary = parser.get_code_summary(strat)
            
            print(f"\n📊 Première stratégie: {strat.name}")
            for key, value in summary.items():
                print(f"   {key}: {value}")
    else:
        print(f"❌ Répertoire introuvable: {strategies_dir}")
