# =============================================================================
# MODIFICATIONS À APPORTER À run_pipeline.py
# =============================================================================

"""
FICHIER: run_pipeline.py
ACTION: Remplacer et ajouter les sections suivantes
"""

# =============================================================================
# 1. IMPORTS (ajouter à la ligne ~295)
# =============================================================================

# AVANT:
from src.enrichers.kpi_enricher import KPIEnricher
from src.enrichers.styles import get_kpi_styles

# APRÈS:
from src.enrichers.kpi_enricher import KPIEnricher
from src.enrichers.equity_enricher import EquityCurveEnricher  # 👈 NOUVEAU
from src.enrichers.styles import get_kpi_styles


# =============================================================================
# 2. CONFIGURATION PIPELINE (classe PipelineConfig, ligne ~50)
# =============================================================================

# AVANT:
class PipelineConfig:
    def __init__(self):
        # ...
        # Paramètres d'enrichissement
        self.enrich_backup = True
        self.enrich_force = False  # Ré-enrichir même si déjà fait

# APRÈS:
class PipelineConfig:
    def __init__(self):
        # ...
        # Paramètres d'enrichissement
        self.enrich_backup = True
        self.enrich_force = False  # Ré-enrichir même si déjà fait
        self.enrich_include_equity = True  # 👈 NOUVEAU - Enrichir avec equity curves


# =============================================================================
# 3. REMPLACER LA FONCTION step_enrich_kpis (ligne ~291)
# =============================================================================

# ACTION: 
# - Supprimer ENTIÈREMENT la fonction step_enrich_kpis() (lignes ~291-390)
# - La remplacer par le contenu du fichier step_enrich_html_reports_NOUVEAU.py


# =============================================================================
# 4. APPEL DANS run_pipeline() (ligne ~800)
# =============================================================================

# AVANT:
if config.run_enrich:
    results['steps']['enrich'] = step_enrich_kpis(config)

# APRÈS:
if config.run_enrich:
    results['steps']['enrich'] = step_enrich_html_reports(config)  # 👈 RENOMMÉ


# =============================================================================
# 5. ARGUMENTS CLI (fonction main(), ligne ~920)
# =============================================================================

# AJOUTER après l'argument --force (ligne ~960):

parser.add_argument(
    '--no-equity',
    action='store_true',
    help="Enrichissement KPI uniquement (sans equity curves)"
)

# PUIS dans la section de configuration (ligne ~1030), AJOUTER:

# Configuration enrichissement
config.enrich_include_equity = not args.no_equity  # 👈 NOUVEAU


# =============================================================================
# 6. DOCSTRING DU MODULE (ligne ~1)
# =============================================================================

# AVANT:
"""
1. Enrichissement HTML avec KPIs du Portfolio Report
"""

# APRÈS:
"""
1. Enrichissement HTML avec KPIs + Equity Curves
"""


# =============================================================================
# 7. USAGE DANS DOCSTRING (ligne ~10)
# =============================================================================

# AJOUTER:
"""
    python run_pipeline.py --step enrich --no-equity  # KPI uniquement
"""


# =============================================================================
# RÉSUMÉ DES MODIFICATIONS
# =============================================================================

"""
FICHIERS MODIFIÉS:
- run_pipeline.py

CHANGEMENTS:
1. Import de EquityCurveEnricher ajouté
2. PipelineConfig.enrich_include_equity = True (par défaut)
3. Fonction step_enrich_kpis() → step_enrich_html_reports() (renommée et réécrite)
4. Fonctions utilitaires ajoutées (_generate_equity_warning_banner, etc.)
5. Argument CLI --no-equity ajouté
6. Appel dans run_pipeline() mis à jour
7. Documentation mise à jour

COMPORTEMENT:
- Par défaut: enrichit KPI + Equity
- Avec --no-equity: enrichit KPI seulement
- Si DataSource manquant: préserve equity existante avec warning
- Si aucune equity: affiche section N/A
- Stats détaillées: enriched_both, equity_preserved_with_warning, missing_equity_data

COMPATIBILITÉ:
- Backward: fichiers déjà enrichis restent valides
- Forward: nouveaux fichiers ont les deux sections
- Dry-run: compatible
"""
