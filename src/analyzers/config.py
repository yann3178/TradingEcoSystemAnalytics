"""
Configuration de l'Analyseur IA
================================
Paramètres et constantes pour l'analyse des stratégies.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional
import sys

# Ajouter le chemin parent pour les imports
V2_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(V2_ROOT))

from config.settings import (
    V2_ROOT, DATA_ROOT, OUTPUT_ROOT,
    LEGACY_ROOT, LEGACY_MC_EXPORT,
    ANTHROPIC_API_KEY, CLAUDE_MODEL,
    API_RETRY_ATTEMPTS, API_RETRY_DELAY,
)


# =============================================================================
# CATÉGORIES DE STRATÉGIES (8 catégories standardisées)
# =============================================================================

STRATEGY_CATEGORIES = [
    "BREAKOUT",        # Cassures de niveaux, range breakouts
    "MEAN_REVERSION",  # Retour à la moyenne, RSI, Bollinger
    "TREND_FOLLOWING", # Suivi de tendance, momentum directionnel
    "PATTERN_PURE",    # Patterns chartistes, candlesticks
    "VOLATILITY",      # Basé sur la volatilité, ATR, Bollinger
    "BIAS_TEMPORAL",   # Timing, day-of-week, session, saisonnalité
    "GAP_TRADING",     # Gap breakout, gap fade, overnight gaps
    "HYBRID",          # Combinaisons multi-logiques
]

# Mapping des anciens types vers les nouveaux (8 catégories V2)
CATEGORY_MAPPING = {
    # BREAKOUT variants
    'breakout': 'BREAKOUT',
    'breakout strategy': 'BREAKOUT',
    'range breakout': 'BREAKOUT',
    'channel breakout': 'BREAKOUT',
    'session breakout': 'BREAKOUT',
    'session-based breakout': 'BREAKOUT',
    'intraday breakout': 'BREAKOUT',
    'level breakout': 'BREAKOUT',
    'swing point breakout': 'BREAKOUT',
    'range expansion breakout': 'BREAKOUT',
    'pivot-based breakout': 'BREAKOUT',
    'volatility breakout': 'BREAKOUT',
    'high/low breakout': 'BREAKOUT',
    'momentum breakout': 'BREAKOUT',
    'bollinger band breakout': 'BREAKOUT',
    'multi-timeframe breakout': 'BREAKOUT',
    'trend following breakout': 'BREAKOUT',
    'trend following / breakout': 'BREAKOUT',
    'breakout/deviation': 'BREAKOUT',
    
    # MEAN_REVERSION variants
    'reversal': 'MEAN_REVERSION',
    'mean reversion': 'MEAN_REVERSION',
    'mean reverting': 'MEAN_REVERSION',
    'mean reversal': 'MEAN_REVERSION',
    'counter-trend': 'MEAN_REVERSION',
    'countertrend': 'MEAN_REVERSION',
    'countertrend/reversal': 'MEAN_REVERSION',
    'counter-trend reversal': 'MEAN_REVERSION',
    'reversal/fading': 'MEAN_REVERSION',
    'reversal/counter-trend': 'MEAN_REVERSION',
    'reversal/mean reversion': 'MEAN_REVERSION',
    'pullback': 'MEAN_REVERSION',
    'bounce': 'MEAN_REVERSION',
    'bollinger band reversal': 'MEAN_REVERSION',
    'pivot point reversal': 'MEAN_REVERSION',
    'multi-timeframe mean reversion': 'MEAN_REVERSION',
    
    # TREND_FOLLOWING variants
    'trend following': 'TREND_FOLLOWING',
    'trend': 'TREND_FOLLOWING',
    'directional': 'TREND_FOLLOWING',
    'trend continuation': 'TREND_FOLLOWING',
    'trend following / momentum': 'TREND_FOLLOWING',
    
    # PATTERN_PURE variants
    'pattern': 'PATTERN_PURE',
    'pattern-based': 'PATTERN_PURE',
    'candlestick': 'PATTERN_PURE',
    'chart pattern': 'PATTERN_PURE',
    'price pattern': 'PATTERN_PURE',
    'pattern-based bias': 'PATTERN_PURE',
    'pattern-based day trading': 'PATTERN_PURE',
    'pattern-based reversal': 'PATTERN_PURE',
    'intraday pattern-based': 'PATTERN_PURE',
    'stochastic oscillator with pattern': 'PATTERN_PURE',
    
    # VOLATILITY variants
    'volatility': 'VOLATILITY',
    'volatility-based': 'VOLATILITY',
    'atr': 'VOLATILITY',
    'hybrid breakout/volatility': 'VOLATILITY',
    
    # BIAS_TEMPORAL variants
    'seasonal': 'BIAS_TEMPORAL',
    'bias': 'BIAS_TEMPORAL',
    'bias trading': 'BIAS_TEMPORAL',
    'time-based': 'BIAS_TEMPORAL',
    'time-based bias': 'BIAS_TEMPORAL',
    'time-based breakout': 'BIAS_TEMPORAL',
    'time-based directional bias': 'BIAS_TEMPORAL',
    'time-based pattern': 'BIAS_TEMPORAL',
    'time-based weekly bias': 'BIAS_TEMPORAL',
    'bias/session-based': 'BIAS_TEMPORAL',
    'bias/time-based': 'BIAS_TEMPORAL',
    'bias/trend following': 'BIAS_TEMPORAL',
    'bias/seasonal': 'BIAS_TEMPORAL',
    'bias-based breakout': 'BIAS_TEMPORAL',
    'bias/breakout hybrid': 'BIAS_TEMPORAL',
    'day-of-week bias': 'BIAS_TEMPORAL',
    'seasonal/day-of-week bias': 'BIAS_TEMPORAL',
    'session-based bias': 'BIAS_TEMPORAL',
    'channel breakout / time-based bias': 'BIAS_TEMPORAL',
    
    # GAP_TRADING variants
    'gap': 'GAP_TRADING',
    'gap trading': 'GAP_TRADING',
    'breakout/gap trading': 'GAP_TRADING',
    'gap breakout': 'GAP_TRADING',
    'gap fade': 'GAP_TRADING',
    
    # HYBRID variants
    'hybrid': 'HYBRID',
    'dual-mode': 'HYBRID',
    'hybrid breakout/reversal': 'HYBRID',
    'hybrid breakout/mean reversion': 'HYBRID',
    'breakout/mean reversion hybrid': 'HYBRID',
    'breakout/reversal hybrid': 'HYBRID',
    'pivot point breakout/reversal': 'HYBRID',
    'unknown': 'HYBRID',
    'error': 'HYBRID',
}


def normalize_category(category: str) -> str:
    """Normalise une catégorie vers les 8 catégories standard."""
    if not category:
        return "OTHER"
    
    cat_lower = category.lower().strip()
    
    # Si déjà dans les catégories standard
    if cat_lower.upper() in STRATEGY_CATEGORIES:
        return cat_lower.upper()
    
    # Chercher dans le mapping
    for old, new in CATEGORY_MAPPING.items():
        if old in cat_lower:
            return new
    
    return "OTHER"


# =============================================================================
# CONFIGURATION DE L'ANALYSEUR
# =============================================================================

@dataclass
class AIAnalyzerConfig:
    """Configuration pour l'analyseur IA."""
    
    # API Claude
    api_key: str = field(default_factory=lambda: ANTHROPIC_API_KEY)
    model: str = CLAUDE_MODEL
    max_tokens: int = 6000
    
    # Rate limiting
    delay_between_requests: float = 2.5  # secondes
    max_retries: int = API_RETRY_ATTEMPTS
    retry_delay: int = API_RETRY_DELAY
    
    # Chemins sources
    strategies_dir: Path = field(default_factory=lambda: LEGACY_MC_EXPORT / "Strategies")
    functions_dir: Path = field(default_factory=lambda: LEGACY_MC_EXPORT / "Functions")
    
    # Chemins outputs
    output_dir: Path = field(default_factory=lambda: OUTPUT_ROOT / "ai_analysis")
    html_reports_dir: Path = field(default_factory=lambda: OUTPUT_ROOT / "ai_analysis" / "html_reports")
    csv_output: Path = field(default_factory=lambda: OUTPUT_ROOT / "ai_analysis" / "strategies_ai_analysis.csv")
    tracking_file: Path = field(default_factory=lambda: OUTPUT_ROOT / "ai_analysis" / "strategy_tracking.json")
    
    # Mode d'analyse
    mode: str = "delta"  # delta = incrémental, full = tout ré-analyser
    analysis_version: str = "2.0"  # Incrémenter pour forcer ré-analyse
    
    # Options
    clean_orphans: bool = False  # Supprimer HTML des stratégies hors périmètre
    generate_dashboard: bool = True
    verbose: bool = True
    
    # Limites
    max_strategies: int = 0  # 0 = toutes
    
    def __post_init__(self):
        """Validation et création des répertoires."""
        # Créer les répertoires de sortie
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.html_reports_dir.mkdir(parents=True, exist_ok=True)
        self.csv_output.parent.mkdir(parents=True, exist_ok=True)
    
    def validate(self) -> List[str]:
        """Valide la configuration, retourne la liste des erreurs."""
        errors = []
        
        if not self.api_key:
            errors.append("ANTHROPIC_API_KEY non définie")
        
        if not self.strategies_dir.exists():
            # Essayer le chemin V2
            v2_strategies = DATA_ROOT / "mc_export" / "strategies"
            if v2_strategies.exists():
                self.strategies_dir = v2_strategies
            else:
                errors.append(f"Répertoire strategies introuvable: {self.strategies_dir}")
        
        if not self.functions_dir.exists():
            # Essayer le chemin V2
            v2_functions = DATA_ROOT / "mc_export" / "functions"
            if v2_functions.exists():
                self.functions_dir = v2_functions
            else:
                # Les fonctions sont optionnelles, juste un warning
                pass
        
        return errors
    
    @classmethod
    def from_env(cls) -> 'AIAnalyzerConfig':
        """Crée une config depuis les variables d'environnement."""
        return cls(
            api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
            max_strategies=int(os.environ.get("MAX_STRATEGIES", "0")),
            mode=os.environ.get("ANALYSIS_MODE", "delta"),
        )


# =============================================================================
# PROMPTS POUR CLAUDE
# =============================================================================

ANALYSIS_SYSTEM_PROMPT = """You are a MultiCharts PowerLanguage expert. Your task is to analyze trading strategy code and provide detailed, structured analysis.

KEY RULES:
1. Always specify whether stop/profit levels are in CURRENCY (SetStopLoss) or POINTS (SetStopLoss_pt)
2. When you see PatternFast(XX), look up the exact definition in the provided code
3. Use proper formatting with **bold** for emphasis and bullet points for lists
4. Be precise about entry/exit conditions - differentiate LONG vs SHORT
5. Score complexity and quality honestly from 1-10
"""

ANALYSIS_USER_PROMPT_TEMPLATE = """Analyze this MultiCharts PowerLanguage trading strategy in detail.

{functions_context}

# IMPORTANT CONVENTIONS

**Stop/Profit Units:**
- SetStopLoss(xxx) or SetProfitTarget(xxx) → xxx in CURRENCY (dollars/euros)
- SetStopLoss_pt(zzz) or SetProfitTarget_pt(zzz) → zzz in POINTS

**PatternFast Function:**
When you see PatternFast(XX), find the definition in the code above and explain:
- The pattern number and its formula
- What market condition it detects
- How it's used in the strategy

# STRATEGY TO ANALYZE

**Strategy Name:** {strategy_name}

```powerlanguage
{strategy_code}
```

# REQUIRED JSON RESPONSE

{{
  "strategy_type": "One of: BREAKOUT, MEAN_REVERSION, TREND_FOLLOWING, PATTERN, VOLATILITY, SEASONAL, MOMENTUM, OTHER",
  "strategy_subtype": "More specific variant (e.g., 'Channel Breakout with ATR Filter')",
  "summary": "Concise 2-3 sentence summary using **bold** for key concepts",
  
  "entry_conditions": "**LONG:**\\n• Condition 1\\n• Condition 2\\n\\n**SHORT:**\\n• Condition 1\\n• Condition 2",
  "exit_conditions": "**Stops:**\\n• Details\\n\\n**Targets:**\\n• Details\\n\\n**Time:**\\n• Details",
  
  "stop_loss_level": "SetStopLoss(**100**) = 100 in **currency** or 'None'",
  "take_profit_level": "SetProfitTarget(**200**) = 200 in **currency** or 'None'",
  
  "exit_on_close": "YES or NO",
  "time_exit_condition": "YES or NO",
  "time_exit_details": "Exit at **15:45** or 'None'",
  
  "function_patterns": ["RSI(14)", "PatternFast(23)", "ATR(10)"],
  "pattern_details": "**PatternFast(23):**\\n• Formula: body5d < 0.1 * range5d\\n• Meaning: Consolidation setup\\n\\nRepeat for each pattern or 'None'",
  
  "number_of_patterns": "Integer count",
  "complexity_score": "1-10 (1=very simple, 10=very complex)",
  "quality_score": "1-10 (based on risk management, logic clarity, robustness)",
  
  "quality_analysis": "**STRENGTHS:**\\n• Point 1\\n• Point 2\\n\\n**WEAKNESSES:**\\n• Point 1\\n• Point 2\\n\\n**RECOMMENDATIONS:**\\n• Improvement 1"
}}

CRITICAL: Respond ONLY with valid JSON. Use \\n for newlines. Escape quotes properly.
"""


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def get_default_config() -> AIAnalyzerConfig:
    """Retourne une configuration par défaut."""
    return AIAnalyzerConfig()


if __name__ == "__main__":
    # Test de la config
    config = AIAnalyzerConfig()
    print(f"API Key définie: {'Oui' if config.api_key else 'Non'}")
    print(f"Modèle: {config.model}")
    print(f"Strategies dir: {config.strategies_dir}")
    print(f"Exists: {config.strategies_dir.exists()}")
    
    errors = config.validate()
    if errors:
        print("\n❌ Erreurs de configuration:")
        for e in errors:
            print(f"   • {e}")
    else:
        print("\n✅ Configuration valide")
