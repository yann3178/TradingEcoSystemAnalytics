# Trading Strategy Analysis Pipeline V2

## 🎯 Vue d'ensemble

Système unifié d'analyse, documentation et suivi de **~800 stratégies de trading** MultiCharts avec **preprocessing automatisé**, harmonisation des noms, analyse IA, et dashboards interactifs.

### Fonctionnalités Principales

- **🔄 Preprocessing Intégré** : Mapping + Harmonisation automatique dans le pipeline ⭐ **NOUVEAU V2.1.1**
- **Mapping Stratégies** : Association automatique stratégie ↔ symbole(s) depuis Portfolio Report
- **Harmonisation Noms** : Convention unifiée `{Symbol}_{StrategyName}.html` avec backup/rollback
- **Analyse IA** : Classification automatique des stratégies (8 catégories) avec Claude API
- **Enrichissement KPI** : Ajout automatique des métriques de performance aux rapports HTML
- **Equity Curves** : Graphiques interactifs Chart.js avec distinction IS/OOS
- **Monte Carlo** : Simulation pour validation statistique des stratégies
- **Corrélation** : Analyse de corrélation (Pearson + R² Kevin Davey) avec filtres temporels
- **Dashboard Mobile** : Interface responsive avec authentification Cloudflare

---

## 📁 Structure Complète

```
C:\TradeData\V2\
│
├── config/                          # Configuration centralisée
│   ├── settings.py                  # Tous les paramètres système
│   ├── credentials.json             # Clés API Google Drive
│   └── instruments_mapping.csv      # Référentiel instruments
│
├── data/                            # Données sources (read-only)
│   ├── mc_export/                   # Export MultiCharts
│   │   ├── strategies/              # Fichiers PowerLanguage (.txt)
│   │   └── functions/               # Fonctions custom
│   ├── equity_curves/               # DataSources (profits journaliers)
│   └── portfolio_reports/           # CSV Portfolio Reports
│       └── Portfolio_Report_V2_27112025.csv  ← Source de vérité
│
├── src/                             # Code source modulaire
│   ├── analyzers/                   # Analyse IA
│   │   ├── ai_analyzer.py           # Classification stratégies (Claude)
│   │   └── html_generator.py        # Génération rapports HTML
│   ├── enrichers/                   # Enrichissement HTML
│   │   ├── kpi_enricher.py          # Ajout KPIs de performance
│   │   ├── equity_enricher.py       # Ajout equity curves interactives
│   │   └── styles.py                # Styles CSS pour dashboards
│   ├── consolidators/               # Consolidation données
│   │   └── correlation_calculator.py # Analyse de corrélation
│   ├── generators/                  # Génération dashboards
│   │   ├── index_generator.py       # Dashboard principal
│   │   └── correlation_dashboard.py # Dashboard corrélation
│   ├── monte_carlo/                 # Simulation Monte Carlo
│   │   ├── simulator.py             # Simulateur MC
│   │   └── data_loader.py           # Chargement données
│   └── utils/                       # Utilitaires
│       ├── strategy_mapper.py       # Mapping stratégie→symbole
│       └── matching.py              # Fuzzy matching Levenshtein
│
├── outputs/                         # Résultats générés
│   ├── html_reports/                # Rapports enrichis
│   │   ├── {Symbol}_{Strategy}.html         # Rapports harmonisés
│   │   ├── {Symbol}_{Strategy}_correlation.html
│   │   └── index.html               # Dashboard principal
│   ├── csv/                         # Exports tabulaires
│   ├── monte_carlo/                 # Simulations MC
│   │   └── {timestamp}/             # Résultats par exécution
│   ├── correlation/                 # Matrices de corrélation
│   │   └── {timestamp}/             # Dashboards par exécution
│   └── consolidated/                # Données consolidées
│       ├── strategy_mapping.json            # Mapping complet
│       ├── migration_report.json            # Rapport migration
│       └── non_renamed_analysis.json        # Analyse fichiers non migrés
│
├── backups/                         # Backups automatiques
│   └── {timestamp}/                 # Backup horodaté
│       ├── html_reports/            # Fichiers sauvegardés
│       └── manifest.json            # Métadonnées backup
│
├── logs/                            # Logs d'exécution
├── server/                          # Serveur web + tunnel Cloudflare
├── docs/                            # Documentation (ce dossier)
│   ├── README.md                    # Ce fichier
│   ├── STRATEGY_HARMONIZATION.md    # Guide harmonisation
│   ├── TOOLS_REFERENCE.md           # Référence outils
│   └── PROJECT_STATUS.md            # État du projet
│
├── run_pipeline.py                  # ⭐ Pipeline complet avec preprocessing ⭐
├── run_enrich.py                    # Enrichissement HTML seul
├── migrate_ai_html_names.py         # Migration noms fichiers (standalone)
├── rollback_migration.py            # Restauration backup
├── verify_migration.py              # Vérification post-migration
├── analyze_non_renamed.py           # Analyse fichiers non migrés
├── migrate_data.py                  # Migration V1 → V2
└── requirements.txt                 # Dépendances Python
```

---

## 🚀 Démarrage Rapide

### ⭐ Option 1 : Pipeline Automatisé Complet (RECOMMANDÉ - V2.1.1)

**Le pipeline gère maintenant tout automatiquement !**

```bash
cd C:\TradeData\V2

# Pipeline complet avec preprocessing intégré
python run_pipeline.py

# Ce pipeline exécute automatiquement :
# 0A. Strategy Mapping (génération mapping.json)
# 1.  KPI Enrichment (ajout KPIs aux HTML)
# 1B. Name Harmonization (renommage SYMBOL_Strategy.html)
# 2.  Monte Carlo (simulations statistiques)
# 3.  Correlation (analyse corrélation Long Terme / Court Terme)
```

**Résultat attendu :**
```
🚀 TRADING STRATEGY ANALYSIS PIPELINE V2
======================================================================
🗺️  ÉTAPE 0A: STRATEGY MAPPING
📊 243 stratégies mappées
✅ Mapping généré: outputs/consolidated/strategy_mapping.json

📊 ÉTAPE 1: ENRICHISSEMENT KPI
📄 581 fichiers HTML trouvés
✅ 235 enrichis

📝 ÉTAPE 1B: NAME HARMONIZATION
✅ 235 fichiers renommés → SYMBOL_Strategy.html

🎲 ÉTAPE 2: SIMULATION MONTE CARLO
📁 245 fichiers d'equity curves trouvés
✅ Simulations terminées

📊 ÉTAPE 3: ANALYSE DE CORRÉLATION
📥 1,514,882 lignes chargées
✅ Dashboard généré

✅ PIPELINE TERMINÉ
⏱️  Durée totale: ~2-5 minutes
```

### Option 2 : Pipeline Sans Preprocessing

Si tu veux sauter le mapping et l'harmonisation :

```bash
python run_pipeline.py --skip-preprocessing
```

### Option 3 : Étapes Individuelles

```bash
# Enrichissement KPI uniquement
python run_pipeline.py --step enrich

# Monte Carlo uniquement
python run_pipeline.py --step montecarlo

# Corrélation uniquement
python run_pipeline.py --step correlation

# Dry-run (prévisualisation)
python run_pipeline.py --dry-run
```

### Option 4 : Outils Standalone (Ancien Workflow)

```bash
# Si tu préfères utiliser les scripts séparés
python migrate_ai_html_names.py --dry-run   # Prévisualisation
python migrate_ai_html_names.py             # Exécution
python verify_migration.py                  # Vérification
```

---

## 📊 Architecture du Pipeline V2.1.1

### Pipeline Complet Automatisé

```
┌────────────────────────────────────────────────────────────────┐
│                    RUN_PIPELINE.PY V2.1.1                      │
│  Preprocessing → Enrichissement → Monte Carlo → Corrélation   │
└────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼──────────────────────┬─────────────┐
        ▼                     ▼                      ▼             ▼
  ┌───────────┐        ┌────────────┐        ┌───────────┐  ┌──────────┐
  │ ÉTAPE 0A  │        │  ÉTAPE 1   │        │ ÉTAPE 1B  │  │ ÉTAPE 2  │
  │  MAPPING  │───────▶│ ENRICH KPI │───────▶│HARMONIZE  │  │MONTE CARLO│
  │(2 sec)    │        │(~30 sec)   │        │(~5 sec)   │  │(variable)│
  └───────────┘        └────────────┘        └───────────┘  └────┬─────┘
                                                                  │
                                                                  ▼
                                                           ┌──────────────┐
                                                           │   ÉTAPE 3    │
                                                           │ CORRELATION  │
                                                           │  (~60 sec)   │
                                                           └──────────────┘
```

### Ordre d'Exécution Critique

```
┌─────────────────────────────────────────┐
│ 0A. STRATEGY MAPPING                    │ ← Lit Portfolio Report
│     → Génère strategy_mapping.json      │   Mappe 243 stratégies
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 1. KPI ENRICHMENT                       │ ← Utilise noms ORIGINAUX
│    → Ajoute KPIs aux fichiers HTML      │   Important pour matching
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 1B. NAME HARMONIZATION                  │ ← Renomme fichiers
│     → Strategy.html → SYMBOL_Strategy.html  Après enrichissement
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 2. MONTE CARLO                          │ ← Indépendant des HTML
│    → Simulations sur equity curves      │   Utilise fichiers .txt/.csv
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 3. CORRELATION                          │ ← Indépendant des HTML
│    → Analyse sur fichier consolidé CSV  │   Génère dashboard séparé
└─────────────────────────────────────────┘
```

### Workflow Harmonisation des Noms

```
┌────────────────────────────────────────────────────────────┐
│              SYSTÈME D'HARMONISATION                       │
└────────────────────────────────────────────────────────────┘
                            │
      ┌─────────────────────┼──────────────────────┐
      ▼                     ▼                      ▼
┌────────────┐      ┌───────────────┐     ┌──────────────┐
│  MAPPING   │      │   MIGRATION   │     │ VÉRIFICATION │
│ (mapper.py)│─────▶│ (migrate.py)  │────▶│ (verify.py)  │
└────────────┘      └───────────────┘     └──────────────┘
      │                     │                      │
      │                     ▼                      ▼
      │              ┌───────────┐          ┌──────────┐
      │              │  BACKUP   │          │ ANALYSIS │
      │              │ (rollback)│          │ (analyze)│
      │              └───────────┘          └──────────┘
      │
      ▼
┌─────────────────────────────────────────┐
│ Portfolio Report CSV (Source de vérité) │
│  243 stratégies → symboles mappées      │
└─────────────────────────────────────────┘
```

---

## 🔧 Options de Ligne de Commande

### run_pipeline.py (V2.1.1)

```bash
# Pipeline complet
python run_pipeline.py

# Options principales
python run_pipeline.py --dry-run                # Prévisualisation
python run_pipeline.py --skip-preprocessing     # Sauter étapes 0A et 1B
python run_pipeline.py --quiet                  # Mode silencieux

# Étapes individuelles
python run_pipeline.py --step enrich            # Étape 1 uniquement
python run_pipeline.py --step montecarlo        # Étape 2 uniquement
python run_pipeline.py --step correlation       # Étape 3 uniquement

# Monte Carlo options
python run_pipeline.py --mc-max 10              # Limiter à 10 stratégies
python run_pipeline.py --mc-sims 5000           # 5000 simulations/niveau

# Forcer ré-enrichissement
python run_pipeline.py --force                  # Re-enrichir même si déjà fait
```

**Options complètes :**

| Option | Description | Défaut |
|--------|-------------|--------|
| `--step {enrich,montecarlo,correlation,all}` | Étape à exécuter | `all` |
| `--dry-run` `-n` | Mode simulation (aucune modification) | `False` |
| `--quiet` `-q` | Mode silencieux | `False` |
| `--mc-max N` | Max stratégies Monte Carlo (0=toutes) | `0` |
| `--mc-sims N` | Nb simulations MC par niveau | `1000` |
| `--force` | Forcer ré-enrichissement | `False` |
| `--skip-preprocessing` | Sauter mapping + harmonisation | `False` |

---

## 🔧 Modules Principaux

### 1. Pipeline Unifié (`run_pipeline.py`) ⭐ NOUVEAU V2.1.1

**Orchestrateur complet avec preprocessing intégré**

```python
# Configuration
class PipelineConfig:
    run_preprocessing = True     # Activer étapes 0A et 1B
    run_enrich = True            # Enrichissement KPI
    run_monte_carlo = True       # Simulations MC
    run_correlation = True       # Analyse corrélation
    
    mc_nb_simulations = 1000
    corr_threshold = 0.70
    # ... autres paramètres
```

**Fonctionnalités :**
- Preprocessing automatique (mapping + harmonisation)
- Enrichissement KPI avec matching fuzzy
- Monte Carlo sur equity curves
- Corrélation Long Terme / Court Terme
- Rapport JSON d'exécution
- Gestion d'erreurs non-bloquante

### 2. Strategy Mapper (`src/utils/strategy_mapper.py`)

**Mapping stratégie → symbole(s) depuis Portfolio Report**

```python
from src.utils.strategy_mapper import StrategyMapper

mapper = StrategyMapper()
mapper.load_portfolio_report()

# Récupérer symbole(s) pour une stratégie
symbols = mapper.get_symbols_for_strategy("SOM_UA_2302_G_5")
# Retourne: ["CL"]

# Recherche floue
result = mapper.find_strategy_fuzzy("SOM UA 2302")
# Retourne la meilleure correspondance

# Statistiques
mapper.print_statistics()
# 243 stratégies uniques, ratio 1:1 stratégie-symbole

# Export
mapper.export_mapping()  # → outputs/consolidated/strategy_mapping.json
```

**Fonctionnalités :**
- Chargement automatique du Portfolio Report
- Mapping bidirectionnel (stratégie ↔ symbole)
- Recherche floue avec Levenshtein
- Export JSON pour réutilisation
- Gestion stratégies multi-symboles

### 3. Migration des Noms (`migrate_ai_html_names.py`)

**Renommage automatique avec sécurité maximale**

```bash
# Prévisualisation (sans modification)
python migrate_ai_html_names.py --dry-run

# Exécution réelle (avec backup automatique)
python migrate_ai_html_names.py

# Sans backup (non recommandé)
python migrate_ai_html_names.py --no-backup
```

**Fonctionnalités :**
- Backup automatique complet avant migration
- Détection intelligente des fichiers à traiter
- Exclusion automatique : `*_correlation.html`, `*.bak`, `index*.html`
- Format cible : `{Symbol}_{StrategyName}.html`
- Rapport JSON détaillé : succès, warnings, erreurs
- Mode dry-run pour vérification

**Exemple de transformation :**
```
Avant : SOM_UA_2302_G_5.html
Après : CL_SOM_UA_2302_G_5.html
```

### 4. Rollback (`rollback_migration.py`)

**Restauration instantanée en cas de problème**

```bash
# Lister les backups disponibles
python rollback_migration.py --list

# Prévisualiser la restauration
python rollback_migration.py --backup 20251128_232216 --dry-run

# Restaurer
python rollback_migration.py --backup 20251128_232216
```

### 5. Vérification (`verify_migration.py`)

**5 checks automatiques post-migration**

```bash
python verify_migration.py
```

Vérifie :
1. ✅ Existence et validité du rapport de migration
2. ✅ Comptage des fichiers (total, main, correlation, index)
3. ✅ Patterns de nommage (% avec préfixe symbole)
4. ✅ Existence d'un backup récent
5. ✅ Distribution des symboles

### 6. Enrichissement KPI (`enrichers/kpi_enricher.py`)

**Ajoute les indicateurs de performance aux rapports HTML**

Métriques ajoutées :
- Net Profit, Max Drawdown, Ratio NP/DD
- IS/OOS Monthly Returns, Efficiency Ratio
- YTD Profit, Avg Trade, % Exposition
- Performance par période (M, M-1, W, YTD, Y-1)

### 7. Enrichissement Equity (`enrichers/equity_enricher.py`)

**Ajoute les graphiques d'equity curve interactifs**

Fonctionnalités :
- Chart.js responsive
- Distinction visuelle IS/OOS
- Ligne de démarcation OOS
- Tooltips interactifs
- Cleanup automatique pour ré-enrichissement

### 8. Analyse IA (`analyzers/ai_analyzer.py`)

**Classification automatique avec Claude API**

8 catégories de stratégies :
1. BREAKOUT - Cassures de niveaux
2. MEAN_REVERSION - Retour à la moyenne
3. TREND_FOLLOWING - Suivi de tendance
4. MOMENTUM - Dynamique des prix
5. PATTERN - Patterns chartistes
6. VOLATILITY - Exploitation volatilité
7. TIME_BASED - Basées sur horaires
8. HYBRID - Approches mixtes

---

## ⚙️ Configuration

### Variables d'environnement

```bash
# Windows
set ANTHROPIC_API_KEY=sk-ant-...

# Linux/Mac
export ANTHROPIC_API_KEY=sk-ant-...
```

### Paramètres Système (`config/settings.py`)

| Paramètre | Description | Défaut |
|-----------|-------------|--------|
| **Général** |
| `MAX_STRATEGIES` | Limite de stratégies (0=toutes) | `0` |
| `FUZZY_MATCH_THRESHOLD` | Seuil de matching | `0.80` |
| `MIN_MATCH_CHARS` | Min caractères pour matching | `5` |
| **IA** |
| `CLAUDE_MODEL` | Modèle Claude | `claude-sonnet-4-20250514` |
| `ANTHROPIC_API_KEY` | Clé API Claude | Var. env. |
| **Harmonisation** |
| `PORTFOLIO_REPORT_PATH` | Chemin Portfolio Report | Auto-détecté |
| `HTML_REPORTS_DIR` | Dossier rapports HTML | `outputs/html_reports` |
| `BACKUP_DIR` | Dossier backups | `backups/` |
| **Monte Carlo** |
| `MC_NB_SIMULATIONS` | Nb simulations | `1000` |
| `MC_CAPITAL_MIN` | Capital minimum | `10000` |
| `MC_CAPITAL_INCREMENT` | Incrément capital | `5000` |
| **Corrélation** |
| `CORR_START_YEAR` | Année début LT | `2012` |
| `CORR_RECENT_MONTHS` | Mois pour CT | `12` |
| `CORR_THRESHOLD` | Seuil corrélation | `0.70` |

---

## 📚 Documentation Détaillée

### Guides Disponibles

- **[STRATEGY_HARMONIZATION.md](STRATEGY_HARMONIZATION.md)** - Guide complet du système d'harmonisation
  - Concepts et architecture
  - Workflows détaillés
  - Cas d'usage et exemples
  - Troubleshooting

- **[TOOLS_REFERENCE.md](TOOLS_REFERENCE.md)** - Référence complète des outils
  - Tous les scripts Python
  - Options de ligne de commande
  - APIs et fonctions
  - Exemples d'utilisation

- **[PROJECT_STATUS.md](PROJECT_STATUS.md)** - État actuel du projet
  - Fonctionnalités implémentées
  - Statistiques système
  - Roadmap et prochaines étapes

---

## 🎯 Cas d'Usage Courants

### Cas 1 : Workflow Quotidien (Automatisé) ⭐ NOUVEAU

```bash
# Une seule commande fait tout !
python run_pipeline.py

# Résultat :
# ✅ Mapping créé/mis à jour
# ✅ KPIs ajoutés aux HTML
# ✅ Fichiers renommés SYMBOL_Strategy.html
# ✅ Monte Carlo simulé
# ✅ Corrélations calculées
```

### Cas 2 : Enrichissement Seul (Sans Preprocessing)

```bash
# Si fichiers déjà harmonisés
python run_pipeline.py --skip-preprocessing --step enrich
```

### Cas 3 : Problème Après Migration

```bash
# 1. Lister les backups
python rollback_migration.py --list

# 2. Restaurer
python rollback_migration.py --backup 20251128_232216

# 3. Vérifier
python verify_migration.py
```

### Cas 4 : Monte Carlo Limité (Tests Rapides)

```bash
# Tester sur 10 stratégies seulement
python run_pipeline.py --mc-max 10

# Ou Monte Carlo seul
python run_pipeline.py --step montecarlo --mc-max 10
```

### Cas 5 : Dry-Run Complet (Vérification)

```bash
# Voir ce qui serait fait sans rien modifier
python run_pipeline.py --dry-run
```

---

## 📊 Statistiques du Système

### Données Actuelles (28 Nov 2025)

- **Stratégies totales** : ~800 stratégies MultiCharts
- **Stratégies backtestées** : 243 (Portfolio Report)
- **Stratégies avec rapports HTML** : 581
- **Stratégies harmonisées** : 235 (96.7% des backtestées)
- **Symboles traités** : 39 (FDAX, NQ, ES, GC, CL, etc.)
- **Fichiers de corrélation** : 245
- **Equity curves disponibles** : 245

### Performance Pipeline V2.1.1

- **Étape 0A (Mapping)** : ~2 secondes
- **Étape 1 (Enrichissement)** : ~30 secondes (581 fichiers)
- **Étape 1B (Harmonisation)** : ~5 secondes (235 fichiers)
- **Étape 2 (Monte Carlo)** : variable (dépend nb stratégies)
- **Étape 3 (Corrélation)** : ~60 secondes
- **Pipeline complet** : ~2-5 minutes

---

## 🔄 Workflow Complet Recommandé

### Setup Initial (Une fois)

```bash
# 1. Cloner/Installer
cd C:\TradeData\V2

# 2. Installer dépendances
pip install -r requirements.txt

# 3. Configurer
# Éditer config/settings.py si besoin
# Set ANTHROPIC_API_KEY si utilisation IA

# 4. Migrer données V1 (si applicable)
python migrate_data.py
```

### Utilisation Quotidienne (V2.1.1) ⭐

```bash
# Pipeline complet automatisé
python run_pipeline.py

# C'est tout ! Le pipeline gère :
# - Mapping des nouvelles stratégies
# - Enrichissement KPI
# - Harmonisation des noms
# - Monte Carlo
# - Corrélation
```

### Maintenance Mensuelle

```bash
# Nettoyer anciens backups (>30 jours)
dir C:\TradeData\V2\backups

# Mettre à jour Portfolio Report
# Copier nouveau CSV vers data/portfolio_reports/

# Re-générer mapping
python run_pipeline.py --step enrich
```

---

## 🐛 Troubleshooting

### Problème : Import Error dans Pipeline

**Symptôme :** `ImportError: cannot import name 'get_kpi_styles'`

**Solution :** Vérifie que `src/enrichers/styles.py` contient :
```python
def get_kpi_styles() -> str:
    return KPI_DASHBOARD_CSS
```

### Problème : Fichiers non renommés

**Symptôme :** `verify_migration.py` montre beaucoup de fichiers sans préfixe symbole

**Solution :**
```bash
# Analyser les fichiers non renommés
python analyze_non_renamed.py

# Vérifier s'ils sont dans le Portfolio Report
findstr "NomStrategie" C:\TradeData\V2\data\portfolio_reports\Portfolio_Report_V2_27112025.csv
```

**Cause courante :** Stratégies non backtestées (normal, à conserver telles quelles)

### Problème : Erreur de matching

**Symptôme :** "No symbol found for strategy: XYZ"

**Solution :**
```python
# Vérifier le mapping
from src.utils.strategy_mapper import StrategyMapper
mapper = StrategyMapper()
mapper.load_portfolio_report()

# Recherche floue
result = mapper.find_strategy_fuzzy("XYZ")
print(result)
```

### Problème : Pipeline échoue à l'étape 0A

**Symptôme :** Erreur lors du mapping

**Solution :**
```bash
# Sauter le preprocessing temporairement
python run_pipeline.py --skip-preprocessing

# Vérifier Portfolio Report existe
dir C:\TradeData\V2\data\portfolio_reports\*.csv
```

---

## 📝 Changelog

### V2.1.1 (2025-11-28) 🐛 BUGFIX

**Corrections**
- ✅ Fixed: Import error `enrich_html_with_equity_curve` (unused import removed)
- ✅ Fixed: Missing function `get_kpi_styles()` in `styles.py`
- ✅ Tests: Dry-run validation complète
- ✅ Docs: Documentation mise à jour

### V2.1.0 (2025-11-28) ⭐ MAJOR UPDATE

**Preprocessing Intégré dans Pipeline**
- ✅ Étape 0A: Strategy Mapping automatique
- ✅ Étape 1B: Name Harmonization automatique
- ✅ CLI: Option `--skip-preprocessing`
- ✅ Gestion erreurs non-bloquante
- ✅ Pipeline 100% automatisé de bout en bout

**Harmonisation des Noms de Fichiers**
- ✅ Système de mapping stratégie → symbole (`strategy_mapper.py`)
- ✅ Migration automatique avec backup (`migrate_ai_html_names.py`)
- ✅ Rollback instantané (`rollback_migration.py`)
- ✅ Vérification post-migration (`verify_migration.py`)
- ✅ Analyse fichiers non migrés (`analyze_non_renamed.py`)
- ✅ Convention unifiée : `{Symbol}_{StrategyName}.html`
- ✅ 235/243 stratégies backtestées harmonisées (96.7%)

### V2.0.0 (2025-11-27)

**Refactorisation Complète**
- ✅ Architecture modulaire (analyzers, enrichers, consolidators, generators)
- ✅ Configuration centralisée (`config/settings.py`)
- ✅ Enrichissement KPI automatique
- ✅ Equity curves Chart.js interactives
- ✅ Dashboard mobile-friendly
- ✅ Migration V1 → V2 sans perte

---

## 📞 Support

### Logs

Tous les logs dans `logs/` avec horodatage :
```
logs/
├── migration_20251128_232216.log
├── enrichment_20251127_141500.log
└── pipeline_20251127_093000.log
```

### Rapports

Rapports JSON détaillés dans `outputs/` :
```
outputs/
├── consolidated/
│   ├── strategy_mapping.json          # Mapping complet
│   ├── migration_report.json          # Détails migration
│   └── non_renamed_analysis.json      # Analyse fichiers non migrés
└── pipeline_reports/
    └── pipeline_report_{timestamp}.json  # Rapports d'exécution
```

---

## 🎓 Ressources

- **Documentation MultiCharts** : https://www.multicharts.com/documentation
- **Claude API** : https://docs.anthropic.com/claude/reference
- **Chart.js** : https://www.chartjs.org/docs/
- **Kevin Davey** : *Building Winning Algorithmic Trading Systems*

---

**Version** : 2.1.1  
**Dernière mise à jour** : 28 novembre 2025  
**Auteur** : Trading Analytics V2 Pipeline
