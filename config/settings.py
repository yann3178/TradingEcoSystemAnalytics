"""
Configuration Centralisée - Trading Strategy Analysis Pipeline V2
=================================================================
Tous les chemins et paramètres du système en un seul endroit.

Version: 2.0.0
Date: 2025-11-27
"""

import os
from pathlib import Path

# =============================================================================
# CHEMINS RACINES
# =============================================================================

# Racine du système V2
V2_ROOT = Path(r"C:\TradeData\V2")

# Ancienne structure (pour migration/référence)
LEGACY_ROOT = Path(r"C:\TradeData")
LEGACY_MC_EXPORT = Path(r"C:\MC_Export_Code\clean")

# =============================================================================
# CHEMINS DONNÉES SOURCE (data/)
# =============================================================================

DATA_ROOT = V2_ROOT / "data"

# Code MultiCharts exporté
MC_EXPORT_ROOT = DATA_ROOT / "mc_export"
STRATEGIES_DIR = MC_EXPORT_ROOT / "strategies"
FUNCTIONS_DIR = MC_EXPORT_ROOT / "functions"

# Données de performance
EQUITY_CURVES_DIR = DATA_ROOT / "equity_curves"
PORTFOLIO_REPORTS_DIR = DATA_ROOT / "portfolio_reports"

# =============================================================================
# CHEMINS OUTPUTS (outputs/)
# =============================================================================

OUTPUT_ROOT = V2_ROOT / "outputs"

# Rapports HTML
HTML_REPORTS_DIR = OUTPUT_ROOT / "html_reports"
HTML_INDEX_FILE = HTML_REPORTS_DIR / "index.html"

# AI Analysis HTML Reports (V2 migration)
AI_ANALYSIS_DIR = OUTPUT_ROOT / "ai_analysis"
AI_HTML_REPORTS_DIR = HTML_REPORTS_DIR # AI_ANALYSIS_DIR / "html_reports"
AI_INDEX_FILE = HTML_INDEX_FILE # AI_HTML_REPORTS_DIR / "index.html"

# Exports CSV
CSV_OUTPUT_DIR = OUTPUT_ROOT / "csv"
STRATEGIES_ANALYSIS_CSV = CSV_OUTPUT_DIR / "strategies_analysis.csv"
STRATEGY_SUMMARY_CSV = CSV_OUTPUT_DIR / "strategy_summary.csv"

# Données consolidées
CONSOLIDATED_DIR = OUTPUT_ROOT / "consolidated"
CORRELATION_DIR = OUTPUT_ROOT / "correlation"
HTML_CORRELATION_DIR = HTML_REPORTS_DIR / "correlation"
HTML_MONTECARLO_DIR = HTML_REPORTS_DIR / "montecarlo"

# =============================================================================
# CHEMINS LOGS
# =============================================================================

LOGS_DIR = V2_ROOT / "logs"

# =============================================================================
# CHEMINS CONFIG
# =============================================================================

CONFIG_DIR = V2_ROOT / "config"
CREDENTIALS_FILE = CONFIG_DIR / "credentials.json"
INSTRUMENTS_FILE = CONFIG_DIR / "instruments_specifications.csv"
FX_RATES_FILE = CONFIG_DIR / "fx_rates_usd_eur.csv"

# =============================================================================
# API ANTHROPIC (Claude)
# =============================================================================

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = "claude-sonnet-4-20250514"  # Modèle recommandé
# Alternatives:
# CLAUDE_MODEL = "claude-opus-4-20250514"   # Plus puissant, plus cher
# CLAUDE_MODEL = "claude-haiku-4-20250514"  # Plus rapide, moins détaillé

# =============================================================================
# PARAMÈTRES PIPELINE
# =============================================================================

# Analyse IA
MAX_STRATEGIES = 0  # 0 = toutes les stratégies, N = limiter à N (prototype)
REPROCESS_EXISTING = False  # True = ré-analyser même si HTML existe déjà
API_RETRY_ATTEMPTS = 3
API_RETRY_DELAY = 60  # secondes entre les tentatives

# Enrichissement
FUZZY_MATCH_THRESHOLD = 0.80  # Seuil similarité pour matching noms stratégies
MIN_MATCH_CHARS = 5  # Minimum caractères pour éviter faux positifs

# Consolidation
MIN_YEAR_FILTER = 2015  # Ignorer données avant cette année
COMMISSION_PER_CONTRACT = 0.88  # USD par contrat pour calcul Net Profit

# Corrélation
MIN_COMMON_DAYS = 100  # Minimum jours communs pour corrélation fiable
CORRELATION_METHOD = "pearson"  # pearson, spearman, kendall

# =============================================================================
# PARAMÈTRES SERVEUR (Cloudflare Tunnel)
# =============================================================================

SERVER_PORT = 8080
SERVER_HOST = "127.0.0.1"
CLOUDFLARE_TUNNEL_NAME = "trading-reports"

# =============================================================================
# GOOGLE SHEETS (pour export)
# =============================================================================

GOOGLE_SHEET_ID = "1aJ_1gtc-qjetGTh5xKv8wPBsIuhjkaD-5HcITEix0pU"
STRATEGIES_TAB = "Strategies"
INSTRUMENTS_TAB = "Instruments"

# =============================================================================
# LOGGING
# =============================================================================

LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def ensure_directories():
    """Crée tous les répertoires nécessaires s'ils n'existent pas."""
    directories = [
        DATA_ROOT, MC_EXPORT_ROOT, STRATEGIES_DIR, FUNCTIONS_DIR,
        EQUITY_CURVES_DIR, PORTFOLIO_REPORTS_DIR,
        OUTPUT_ROOT, HTML_REPORTS_DIR, CSV_OUTPUT_DIR, 
        CONSOLIDATED_DIR, CORRELATION_DIR,
        LOGS_DIR, CONFIG_DIR
    ]
    for d in directories:
        d.mkdir(parents=True, exist_ok=True)


def get_latest_portfolio_report() -> Path:
    """Retourne le fichier Portfolio Report le plus récent."""
    pattern = "Portfolio_Report_V2_*.csv"
    files = list(PORTFOLIO_REPORTS_DIR.glob(pattern))
    if not files:
        # Fallback sur ancienne structure
        files = list(LEGACY_ROOT.glob(f"Results/{pattern}"))
    if not files:
        raise FileNotFoundError(f"Aucun fichier {pattern} trouvé")
    return max(files, key=lambda p: p.stat().st_mtime)


def get_latest_consolidated() -> Path:
    """Retourne le fichier consolidé le plus récent."""
    pattern = "Consolidated_Strategies_*.txt"
    files = list(CONSOLIDATED_DIR.glob(pattern))
    if not files:
        # Fallback sur ancienne structure
        files = list(LEGACY_ROOT.glob(f"Results/{pattern}"))
    if not files:
        raise FileNotFoundError(f"Aucun fichier {pattern} trouvé")
    # Exclure les fichiers COSTS, Filtered, Part
    files = [f for f in files if "COSTS" not in f.name 
             and "Filtered" not in f.name and "Part" not in f.name]
    return max(files, key=lambda p: p.stat().st_mtime)


def validate_config():
    """Vérifie que la configuration est valide."""
    errors = []
    
    if not ANTHROPIC_API_KEY:
        errors.append("ANTHROPIC_API_KEY non définie (variable d'environnement)")
    
    if not CREDENTIALS_FILE.exists():
        errors.append(f"Fichier credentials.json manquant: {CREDENTIALS_FILE}")
    
    # Vérifier sources de données (avec fallback)
    if not STRATEGIES_DIR.exists() and not LEGACY_MC_EXPORT.exists():
        errors.append("Aucun répertoire de stratégies trouvé")
    
    if errors:
        print("❌ Erreurs de configuration:")
        for e in errors:
            print(f"   • {e}")
        return False
    
    print("✅ Configuration valide")
    return True


# =============================================================================
# INITIALISATION
# =============================================================================

if __name__ == "__main__":
    print("=== Configuration Trading Strategy Pipeline V2 ===\n")
    print(f"V2_ROOT: {V2_ROOT}")
    print(f"DATA_ROOT: {DATA_ROOT}")
    print(f"OUTPUT_ROOT: {OUTPUT_ROOT}")
    print(f"CLAUDE_MODEL: {CLAUDE_MODEL}")
    print(f"MAX_STRATEGIES: {MAX_STRATEGIES or 'Toutes'}")
    print()
    validate_config()
