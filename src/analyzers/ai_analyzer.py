"""
Analyseur IA avec Claude API
=============================
Intégration avec l'API Anthropic pour l'analyse des stratégies.
"""

import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime
from dataclasses import dataclass, field

import sys
V2_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(V2_ROOT))

# Import Anthropic avec gestion d'erreur
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    anthropic = None

from .config import (
    AIAnalyzerConfig, 
    STRATEGY_CATEGORIES, 
    normalize_category,
    ANALYSIS_SYSTEM_PROMPT,
    ANALYSIS_USER_PROMPT_TEMPLATE,
)
from .code_parser import CodeParser, StrategyCode


# =============================================================================
# LOGGING
# =============================================================================

def setup_logger(output_dir: Path) -> logging.Logger:
    """Configure le logger pour l'analyseur."""
    log_file = output_dir / "ai_analyzer.log"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger("ai_analyzer")
    logger.setLevel(logging.INFO)
    
    # Éviter les handlers dupliqués
    if logger.handlers:
        logger.handlers.clear()
    
    # Handler fichier
    fh = logging.FileHandler(log_file, encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    
    # Handler console
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger


# =============================================================================
# TRACKING SYSTEM
# =============================================================================

@dataclass
class AnalysisTracking:
    """Système de tracking pour éviter les ré-analyses inutiles."""
    
    tracking_file: Path
    analysis_version: str = "2.0"
    
    metadata: Dict = field(default_factory=dict)
    strategies: Dict[str, Dict] = field(default_factory=dict)
    
    def __post_init__(self):
        self.load()
    
    def load(self):
        """Charge le tracking depuis le fichier."""
        if not self.tracking_file.exists():
            self.metadata = {
                "last_full_run": None,
                "tracking_version": "2.0",
                "analysis_version": self.analysis_version,
            }
            self.strategies = {}
            return
        
        try:
            with self.tracking_file.open('r', encoding='utf-8') as f:
                data = json.load(f)
                self.metadata = data.get("metadata", {})
                self.strategies = data.get("strategies", {})
        except Exception:
            self.metadata = {"analysis_version": self.analysis_version}
            self.strategies = {}
    
    def save(self):
        """Sauvegarde le tracking."""
        self.tracking_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "metadata": self.metadata,
            "strategies": self.strategies,
        }
        
        with self.tracking_file.open('w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    def should_process(
        self, 
        strategy_name: str, 
        code_hash: str, 
        mode: str = "delta"
    ) -> Tuple[bool, str]:
        """
        Détermine si une stratégie doit être analysée.
        
        Returns:
            (should_process, reason)
        """
        if mode == "full":
            return True, "full_mode"
        
        if strategy_name not in self.strategies:
            return True, "new_strategy"
        
        stored = self.strategies[strategy_name]
        
        # Version d'analyse changée
        if self.metadata.get("analysis_version") != self.analysis_version:
            return True, "version_changed"
        
        # Code modifié
        if stored.get("code_hash") != code_hash:
            return True, "code_modified"
        
        # Analyse en erreur précédemment
        if stored.get("strategy_type") == "Error":
            return True, "previous_error"
        
        return False, "unchanged"
    
    def update_strategy(self, strategy_name: str, data: Dict):
        """Met à jour les données d'une stratégie."""
        self.strategies[strategy_name] = {
            **data,
            "last_analyzed": datetime.now().isoformat(),
        }
    
    def get_error_strategies(self) -> Set[str]:
        """Retourne les stratégies en erreur."""
        errors = set()
        for name, data in self.strategies.items():
            if data.get("strategy_type") == "Error":
                errors.add(name)
        return errors


# =============================================================================
# ANALYSEUR IA
# =============================================================================

class AIAnalyzer:
    """Analyseur de stratégies utilisant Claude API."""
    
    def __init__(self, config: Optional[AIAnalyzerConfig] = None):
        """
        Initialise l'analyseur.
        
        Args:
            config: Configuration (défaut si non fournie)
        """
        self.config = config or AIAnalyzerConfig()
        
        # Validation
        errors = self.config.validate()
        if errors and not self.config.api_key:
            raise ValueError(f"Configuration invalide: {errors}")
        
        # Logger
        self.logger = setup_logger(self.config.output_dir)
        
        # Parser de code
        self.parser = CodeParser(
            self.config.strategies_dir,
            self.config.functions_dir
        )
        
        # Tracking
        self.tracking = AnalysisTracking(
            self.config.tracking_file,
            self.config.analysis_version
        )
        
        # Client API
        self.client = None
        if ANTHROPIC_AVAILABLE and self.config.api_key:
            self.client = anthropic.Anthropic(api_key=self.config.api_key)
        
        # Statistiques
        self.stats = {
            "total_scope": 0,
            "processed": 0,
            "new": 0,
            "modified": 0,
            "unchanged": 0,
            "errors": 0,
            "not_found": 0,
        }
        
        # Résultats
        self.results: List[Dict] = []
    
    def _call_claude(
        self, 
        strategy: StrategyCode, 
        retry_count: int = 0
    ) -> Dict:
        """
        Appelle l'API Claude pour analyser une stratégie.
        
        Args:
            strategy: Code de la stratégie
            retry_count: Compteur de tentatives
            
        Returns:
            Dict avec l'analyse
        """
        if not self.client:
            return self._create_error_analysis("API client non initialisé")
        
        # Construire le prompt
        prompt = ANALYSIS_USER_PROMPT_TEMPLATE.format(
            functions_context=self.parser.functions_context,
            strategy_name=strategy.name,
            strategy_code=strategy.code,
        )
        
        try:
            # Délai entre requêtes
            time.sleep(self.config.delay_between_requests)
            
            # Appel API
            message = self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                system=ANALYSIS_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parser la réponse
            response_text = message.content[0].text.strip()
            
            # Nettoyer le JSON (enlever les balises code si présentes)
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            response_text = response_text.strip()
            
            analysis = json.loads(response_text)
            
            # Normaliser la catégorie
            if "strategy_type" in analysis:
                analysis["strategy_type"] = normalize_category(
                    analysis["strategy_type"]
                )
            
            return analysis
            
        except anthropic.RateLimitError as e:
            self.logger.warning(f"⚠️  Rate limit! Attente {self.config.retry_delay}s...")
            if retry_count < self.config.max_retries:
                time.sleep(self.config.retry_delay)
                return self._call_claude(strategy, retry_count + 1)
            return self._create_error_analysis(f"Rate limit après {self.config.max_retries} tentatives")
        
        except json.JSONDecodeError as e:
            self.logger.warning(f"⚠️  Erreur JSON: {e}")
            if retry_count < self.config.max_retries:
                time.sleep(2)
                return self._call_claude(strategy, retry_count + 1)
            return self._create_error_analysis(f"Erreur JSON: {e}")
        
        except Exception as e:
            self.logger.error(f"⚠️  Erreur: {e}")
            if "rate" in str(e).lower() and retry_count < self.config.max_retries:
                time.sleep(self.config.retry_delay)
                return self._call_claude(strategy, retry_count + 1)
            return self._create_error_analysis(str(e))
    
    def _create_error_analysis(self, error_msg: str) -> Dict:
        """Crée une analyse d'erreur."""
        return {
            "strategy_type": "OTHER",
            "strategy_subtype": "Analysis Failed",
            "summary": f"Analyse échouée: {error_msg}",
            "entry_conditions": "N/A",
            "exit_conditions": "N/A",
            "stop_loss_level": "N/A",
            "take_profit_level": "N/A",
            "exit_on_close": "N/A",
            "time_exit_condition": "N/A",
            "time_exit_details": "N/A",
            "function_patterns": [],
            "pattern_details": "N/A",
            "number_of_patterns": "N/A",
            "complexity_score": "N/A",
            "quality_score": "N/A",
            "quality_analysis": error_msg,
            "_error": True,
        }
    
    def analyze_strategy(self, strategy: StrategyCode) -> Dict:
        """
        Analyse une stratégie unique.
        
        Args:
            strategy: StrategyCode à analyser
            
        Returns:
            Dict avec l'analyse complète
        """
        should_process, reason = self.tracking.should_process(
            strategy.name,
            strategy.code_hash,
            self.config.mode
        )
        
        if not should_process:
            # Retourner les données existantes
            stored = self.tracking.strategies.get(strategy.name, {})
            return stored
        
        self.logger.info(f"   🔄 Analyse ({reason}): {strategy.name}")
        
        # Appeler Claude
        analysis = self._call_claude(strategy)
        
        # Enrichir avec les métadonnées du code
        result = {
            "strategy_name": strategy.name,
            "file_name": strategy.filename,
            "code_hash": strategy.code_hash,
            **analysis,
        }
        
        # Mettre à jour le tracking
        self.tracking.update_strategy(strategy.name, result)
        self.tracking.save()
        
        return result
    
    def run(
        self, 
        strategy_scope: Optional[Set[str]] = None,
        max_strategies: Optional[int] = None,
    ) -> List[Dict]:
        """
        Exécute l'analyse sur un ensemble de stratégies.
        
        Args:
            strategy_scope: Ensemble de noms à analyser (None = tous)
            max_strategies: Limite le nombre (None = config)
            
        Returns:
            Liste des résultats d'analyse
        """
        self.logger.info("\n" + "=" * 70)
        self.logger.info("  🚀 AI Strategy Analyzer V2")
        self.logger.info("=" * 70)
        
        # Lister les fichiers disponibles
        strategy_files = self.parser.list_strategy_files()
        self.logger.info(f"\n📁 {len(strategy_files)} fichiers de stratégies trouvés")
        
        # Filtrer par scope si fourni
        if strategy_scope:
            # Matcher les fichiers avec le scope
            filtered_files = []
            for f in strategy_files:
                from src.utils.file_utils import clean_strategy_name
                name = clean_strategy_name(f.name)
                if name in strategy_scope or f.stem in strategy_scope:
                    filtered_files.append(f)
            strategy_files = filtered_files
            self.logger.info(f"   → {len(strategy_files)} après filtrage par scope")
        
        # Limiter le nombre
        limit = max_strategies or self.config.max_strategies
        if limit and limit > 0:
            strategy_files = strategy_files[:limit]
            self.logger.info(f"   → Limité à {limit} stratégies")
        
        self.stats["total_scope"] = len(strategy_files)
        
        # Vérifier le client API
        if not self.client:
            self.logger.error("❌ Client API non initialisé (vérifier ANTHROPIC_API_KEY)")
            return []
        
        self.logger.info(f"\n📊 Modèle: {self.config.model}")
        self.logger.info(f"📊 Mode: {self.config.mode.upper()}")
        self.logger.info(f"📚 Fonctions clés: {len(self.parser._functions_cache)}")
        
        # Traiter chaque stratégie
        start_time = time.time()
        self.results = []
        
        for idx, filepath in enumerate(strategy_files, 1):
            try:
                # Parser le code
                strategy = self.parser.parse_file(filepath)
                
                self.logger.info(f"\n[{idx}/{len(strategy_files)}] {strategy.name}")
                
                # Vérifier si doit être traité
                should_process, reason = self.tracking.should_process(
                    strategy.name,
                    strategy.code_hash,
                    self.config.mode
                )
                
                if not should_process:
                    self.logger.info(f"   ⏭️  Skip ({reason})")
                    self.stats["unchanged"] += 1
                    
                    # Récupérer les données existantes
                    stored = self.tracking.strategies.get(strategy.name, {})
                    if stored:
                        self.results.append(stored)
                    continue
                
                # Incrémenter selon la raison
                if reason == "new_strategy":
                    self.stats["new"] += 1
                elif reason in ("code_modified", "version_changed", "previous_error"):
                    self.stats["modified"] += 1
                
                # Analyser
                result = self._call_claude(strategy)
                
                if result.get("_error"):
                    self.stats["errors"] += 1
                    self.logger.info(f"   ❌ Erreur")
                else:
                    self.logger.info(f"   ✅ {result.get('strategy_type', 'N/A')}")
                
                # Enrichir le résultat
                full_result = {
                    "strategy_name": strategy.name,
                    "file_name": strategy.filename,
                    "code_hash": strategy.code_hash,
                    **result,
                }
                
                self.results.append(full_result)
                
                # Mettre à jour le tracking
                self.tracking.update_strategy(strategy.name, full_result)
                self.tracking.save()
                
                self.stats["processed"] += 1
                
                # Estimation du temps restant
                elapsed = time.time() - start_time
                if self.stats["processed"] > 0:
                    avg_time = elapsed / self.stats["processed"]
                    remaining = (len(strategy_files) - idx) * avg_time
                    self.logger.info(f"   ⏱️  ~{remaining / 60:.1f} min restantes")
                
            except Exception as e:
                self.logger.error(f"   ❌ Exception: {e}")
                self.stats["errors"] += 1
        
        # Mise à jour finale du tracking
        if self.config.mode == "full":
            self.tracking.metadata["last_full_run"] = datetime.now().isoformat()
        self.tracking.metadata["analysis_version"] = self.config.analysis_version
        self.tracking.save()
        
        # Résumé
        total_time = time.time() - start_time
        self._print_summary(total_time)
        
        return self.results
    
    def _print_summary(self, total_time: float):
        """Affiche le résumé de l'analyse."""
        self.logger.info("\n" + "=" * 70)
        self.logger.info(f"✅ ANALYSE TERMINÉE EN {total_time / 60:.1f} MINUTES")
        self.logger.info("=" * 70)
        self.logger.info(f"\n📊 Statistiques:")
        self.logger.info(f"   Périmètre total    : {self.stats['total_scope']}")
        self.logger.info(f"   Analysées          : {self.stats['processed']}")
        self.logger.info(f"      ├─ Nouvelles    : {self.stats['new']}")
        self.logger.info(f"      └─ Modifiées    : {self.stats['modified']}")
        self.logger.info(f"   Inchangées (skip)  : {self.stats['unchanged']}")
        self.logger.info(f"   Erreurs            : {self.stats['errors']}")
        
        if self.stats["processed"] > 0:
            avg = total_time / self.stats["processed"]
            self.logger.info(f"   Temps moyen        : {avg:.1f}s/stratégie")
    
    def export_csv(self, output_path: Optional[Path] = None) -> Path:
        """
        Exporte les résultats en CSV.
        
        Args:
            output_path: Chemin du fichier (défaut: config)
            
        Returns:
            Path du fichier créé
        """
        import csv
        
        output_path = output_path or self.config.csv_output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.results:
            self.logger.warning("Aucun résultat à exporter")
            return output_path
        
        # Colonnes à exporter
        columns = [
            "strategy_name", "file_name", "strategy_type", "strategy_subtype",
            "summary", "entry_conditions", "exit_conditions",
            "stop_loss_level", "take_profit_level",
            "exit_on_close", "time_exit_condition", "time_exit_details",
            "function_patterns", "pattern_details",
            "number_of_patterns", "complexity_score", "quality_score",
            "quality_analysis", "code_hash",
        ]
        
        with output_path.open('w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(
                f, 
                fieldnames=columns, 
                delimiter=';',
                extrasaction='ignore'
            )
            writer.writeheader()
            
            for result in self.results:
                # Convertir les listes en strings
                row = dict(result)
                if isinstance(row.get("function_patterns"), list):
                    row["function_patterns"] = "; ".join(row["function_patterns"])
                writer.writerow(row)
        
        self.logger.info(f"📄 CSV exporté: {output_path}")
        return output_path
    
    def get_summary(self) -> Dict[str, Any]:
        """Retourne un résumé de l'analyse."""
        # Distribution par type
        type_counts = {}
        for r in self.results:
            stype = r.get("strategy_type", "OTHER")
            type_counts[stype] = type_counts.get(stype, 0) + 1
        
        # Scores moyens
        quality_scores = []
        complexity_scores = []
        for r in self.results:
            try:
                q = float(r.get("quality_score", 0))
                if q > 0:
                    quality_scores.append(q)
            except (ValueError, TypeError):
                pass
            try:
                c = float(r.get("complexity_score", 0))
                if c > 0:
                    complexity_scores.append(c)
            except (ValueError, TypeError):
                pass
        
        return {
            "total_analyzed": len(self.results),
            "stats": self.stats,
            "type_distribution": type_counts,
            "avg_quality_score": sum(quality_scores) / len(quality_scores) if quality_scores else 0,
            "avg_complexity_score": sum(complexity_scores) / len(complexity_scores) if complexity_scores else 0,
        }


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def run_ai_analysis(
    mode: str = "delta",
    max_strategies: int = 0,
    strategy_list: Optional[List[str]] = None,
) -> List[Dict]:
    """
    Fonction de commodité pour lancer une analyse.
    
    Args:
        mode: "delta" ou "full"
        max_strategies: Limite (0 = toutes)
        strategy_list: Liste spécifique de stratégies
        
    Returns:
        Liste des résultats
    """
    config = AIAnalyzerConfig(
        mode=mode,
        max_strategies=max_strategies,
    )
    
    analyzer = AIAnalyzer(config)
    
    scope = set(strategy_list) if strategy_list else None
    results = analyzer.run(strategy_scope=scope)
    
    # Exporter
    analyzer.export_csv()
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Strategy Analyzer V2")
    parser.add_argument("--mode", choices=["delta", "full"], default="delta")
    parser.add_argument("--max", type=int, default=0, help="Max strategies (0=all)")
    parser.add_argument("--dry-run", action="store_true", help="Test sans API")
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("🔍 Mode dry-run: test de configuration uniquement")
        config = AIAnalyzerConfig(mode=args.mode, max_strategies=args.max)
        errors = config.validate()
        if errors:
            print(f"❌ Erreurs: {errors}")
        else:
            print("✅ Configuration valide")
            print(f"   Strategies dir: {config.strategies_dir}")
            print(f"   API Key: {'définie' if config.api_key else 'manquante'}")
    else:
        results = run_ai_analysis(mode=args.mode, max_strategies=args.max)
        print(f"\n✅ {len(results)} stratégies analysées")
