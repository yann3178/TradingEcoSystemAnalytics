# Trading EcoSystem Analytics - Pipeline V2
## Documentation Complète

**Repository GitHub:** https://github.com/yann3178/TradingEcoSystemAnalytics

**Version:** 2.0.0  
**Date:** 28 Novembre 2025  
**Auteur:** Yann  

---

# 📋 Table des Matières

1. [Vue d'ensemble](#1-vue-densemble)
2. [Architecture](#2-architecture)
3. [Structure des Fichiers](#3-structure-des-fichiers)
4. [Configuration](#4-configuration)
5. [Modules Développés](#5-modules-développés)
6. [Modules à Développer](#6-modules-à-développer)
7. [Système Monte Carlo](#7-système-monte-carlo)
8. [Système de Corrélation](#8-système-de-corrélation)
9. [Pipeline de Traitement](#9-pipeline-de-traitement)
10. [Scripts Disponibles](#10-scripts-disponibles)
11. [Guide de Migration](#11-guide-de-migration)
12. [Référence des Données](#12-référence-des-données)
13. [Roadmap](#13-roadmap)

---

# 1. Vue d'ensemble

## 1.1 Objectif

Système unifié d'analyse, documentation et suivi de ~800 stratégies de trading MultiCharts, avec :

- **Analyse IA** : Classification automatique via Claude (Anthropic)
- **Enrichissement** : KPIs de performance + equity curves interactives
- **Dashboard** : Interface web avec filtres et statistiques
- **Monte Carlo** : Simulation de risque et capital optimal (méthode Kevin Davey)
- **Corrélation** : Matrices de corrélation LT/CT avec scoring (méthode Kevin Davey)
- **Accès distant** : Tunnel Cloudflare pour consultation mobile

## 1.2 Composants Existants

| Composant | Localisation Actuelle | Statut |
|-----------|----------------------|--------|
| Analyse IA | `mc_ai_analysis/scripts/` | ✅ Fonctionnel |
| Enrichissement HTML | `mc_ai_analysis/scripts/` | ✅ Fonctionnel |
| Dashboard | `mc_ai_analysis/html_reports/` | ✅ Fonctionnel |
| **Monte Carlo** | `scripts/monte_carlo_simulator/` | ✅ Fonctionnel |
| **Corrélation** | `scripts/correlation_analysis_v2.py` | ✅ Fonctionnel |
| Serveur Cloudflare | `mc_ai_analysis/serve_reports.ps1` | ✅ Fonctionnel |

---

# 2. Architecture

## 2.1 Diagramme du Pipeline Complet

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          RUN_PIPELINE.PY                                │
│                       (Orchestrateur Central)                           │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
    ┌──────────┬──────────┬────────┼────────┬──────────┬──────────┐
    ▼          ▼          ▼        ▼        ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│ANALYZE │ │CONSOL- │ │ENRICH  │ │MONTE   │ │CORREL- │ │DASH-   │ │SERVE   │
│  (IA)  │ │IDATE   │ │        │ │CARLO   │ │ATION   │ │BOARD   │ │        │
├────────┤ ├────────┤ ├────────┤ ├────────┤ ├────────┤ ├────────┤ ├────────┤
│Parse   │ │Load    │ │Add KPIs│ │Bootstrap│ │Pearson │ │index   │ │HTTP    │
│Claude  │ │Portfolio│ │Add     │ │Ruin    │ │R²      │ │.html   │ │Cloud-  │
│Classify│ │Equity  │ │Equity  │ │Capital │ │LT/CT   │ │Filters │ │flare   │
│HTML    │ │Merge   │ │Charts  │ │Davey   │ │Score   │ │Stats   │ │Tunnel  │
└────────┘ └────────┘ └────────┘ └────────┘ └────────┘ └────────┘ └────────┘
```

## 2.2 Intégration Inter-Sites

```
┌─────────────────────────────┐     ┌─────────────────────────────┐
│   AI ANALYSIS DASHBOARD     │     │    MONTE CARLO DASHBOARD    │
│   (index.html)              │◄───►│    (MC_Report_latest.html)  │
├─────────────────────────────┤     ├─────────────────────────────┤
│ • Liste des stratégies      │     │ • Résumé MC toutes strats   │
│ • Filtres (type, score...)  │     │ • Statut (OK/WARNING/RISK)  │
│ • KPIs agrégés              │     │ • Capital recommandé        │
└──────────────┬──────────────┘     └──────────────┬──────────────┘
               │                                    │
               ▼                                    ▼
┌─────────────────────────────┐     ┌─────────────────────────────┐
│   FICHE STRATÉGIE AI        │◄───►│   FICHE MONTE CARLO         │
│   (Strategy.html)           │     │   (Symbol_Strategy_MC.html) │
├─────────────────────────────┤     ├─────────────────────────────┤
│ • Analyse IA du code        │     │ • Tableau 11 niveaux capital│
│ • Classification type       │     │ • Graphique Ruine vs Capital│
│ • KPIs + Equity Curve       │     │ • Recommandation Davey      │
│ • Lien → Fiche MC           │     │ • Lien → Fiche AI           │
└─────────────────────────────┘     └─────────────────────────────┘
```

---

# 3. Structure des Fichiers

## 3.1 Arborescence V2 Proposée

```
C:\TradeData\V2\
│
├── 📁 config/                          # Configuration centralisée
│   ├── settings.py                     # ✅ CRÉÉ - Tous les paramètres
│   ├── credentials.json                # 📦 À migrer
│   └── instruments_specifications.csv  # 📦 À migrer
│
├── 📁 data/                            # Données sources (read-only)
│   ├── 📁 mc_export/                   # Code PowerLanguage
│   │   ├── strategies/                 # 📦 ~800 fichiers
│   │   └── functions/                  # 📦 ~50 fichiers
│   ├── 📁 equity_curves/               # 📦 245 fichiers
│   └── 📁 portfolio_reports/           # 📦 CSV MultiCharts
│
├── 📁 src/                             # Code source
│   ├── 📁 analyzers/                   # 🔲 À PORTER
│   │   ├── ai_analyzer.py              # Analyse IA Claude
│   │   └── code_parser.py              # Parsing PowerLanguage
│   ├── 📁 enrichers/                   # ✅ CRÉÉ
│   │   ├── kpi_enricher.py             # Module KPIs
│   │   ├── equity_enricher.py          # Module Equity Curve
│   │   └── styles.py                   # CSS centralisé
│   ├── 📁 consolidators/               # 🔲 À PORTER
│   │   ├── strategy_consolidator.py    # Consolidation données
│   │   └── correlation_calculator.py   # Matrices corrélation
│   ├── 📁 monte_carlo/                 # 🔲 À PORTER ← NOUVEAU
│   │   ├── simulator.py                # Moteur MC (depuis monte_carlo.py)
│   │   ├── batch_processor.py          # Batch (depuis batch_monte_carlo.py)
│   │   ├── visualizer.py               # HTML reports
│   │   └── config.py                   # Paramètres Davey
│   ├── 📁 generators/                  # 🔲 À PORTER
│   │   ├── dashboard_generator.py      # Dashboard/index.html
│   │   └── csv_exporter.py             # Export CSV
│   └── 📁 utils/                       # ✅ CRÉÉ
│       ├── file_utils.py               # Lecture fichiers
│       ├── matching.py                 # Fuzzy matching
│       └── constants.py                # Constantes
│
├── 📁 outputs/                         # Résultats générés
│   ├── 📁 html_reports/                # Rapports AI + index
│   │   └── MonteCarlo/                 # Copie des rapports MC
│   │       └── Individual/             # Fiches MC individuelles
│   ├── 📁 csv/                         # Exports CSV
│   ├── 📁 correlation/                 # Matrices de corrélation
│   └── 📁 monte_carlo/                 # Résultats MC natifs
│
├── 📁 server/                          # Serveur web
│   ├── serve.py                        # Serveur HTTP Python
│   └── cloudflare_tunnel.py            # Gestion tunnel
│
├── 📁 docs/                            # Documentation
├── 📁 logs/                            # Logs d'exécution
│
├── 📄 run_pipeline.py                  # 🔲 Orchestrateur principal
├── 📄 run_enrich.py                    # ✅ CRÉÉ - Enrichissement
├── 📄 run_monte_carlo.py               # 🔲 À CRÉER - Monte Carlo
├── 📄 run_correlation.py               # 🔲 À CRÉER - Corrélation
├── 📄 migrate_data.py                  # ✅ CRÉÉ - Migration
└── 📄 requirements.txt                 # ✅ CRÉÉ
```

---

# 7. Système Monte Carlo

## 7.1 Vue d'ensemble

Le simulateur Monte Carlo évalue le risque de ruine et détermine le capital minimum requis pour trader une stratégie avec un risque acceptable, selon la **méthode Kevin Davey**.

### Fichiers Existants

| Fichier | Description | Taille |
|---------|-------------|--------|
| `monte_carlo.py` | Moteur de simulation (classe `MonteCarloSimulator`) | ~400 lignes |
| `batch_monte_carlo.py` | Traitement batch de toutes les stratégies | ~500 lignes |
| `individual_visualizer.py` | Génération rapport HTML individuel | ~300 lignes |
| `batch_visualizer.py` | Génération rapport HTML global | ~400 lignes |
| `data_loader.py` | Chargement et parsing des fichiers | ~200 lignes |
| `config.py` | Paramètres par défaut | ~30 lignes |

### Localisation Actuelle

```
C:\TradeData\scripts\monte_carlo_simulator\
├── monte_carlo.py
├── batch_monte_carlo.py
├── individual_visualizer.py
├── batch_visualizer.py
├── data_loader.py
├── config.py
└── extract_trades_for_mc.py
```

### Outputs Générés

```
C:\TradeData\Results\MonteCarlo\
├── MC_Summary_YYYYMMDD_HHMM.csv      # 1 ligne par stratégie
├── MC_Details_YYYYMMDD_HHMM.csv      # 11 lignes par stratégie
├── MC_Report_YYYYMMDD_HHMM.html      # Dashboard global
├── MC_Report_latest.html              # Lien vers dernier rapport
└── Individual/                        # ~250 fichiers
    ├── GC_EasterGold_MC.csv
    ├── GC_EasterGold_MC.html
    └── ...
```

## 7.2 Paramètres Kevin Davey

```python
DEFAULT_CONFIG = {
    # Capital
    'capital_minimum': 5000,           # Capital de départ minimum
    'capital_increment': 2500,         # Incrément entre niveaux
    'nb_capital_levels': 11,           # Nombre de niveaux (5K → 30K)
    
    # Simulation
    'nb_simulations': 2500,            # Simulations par niveau
    'ruin_threshold_pct': 0.40,        # Ruine si equity <= 40%
    
    # Critères de sélection Davey
    'max_acceptable_ruin': 0.10,       # Risque ruine max (10%)
    'min_return_dd_ratio': 2.0,        # Return/DD minimum
    'min_prob_positive': 0.80,         # Prob finir positif (80%)
}
```

## 7.3 Algorithme

1. **Bootstrap** : Tire N trades au hasard avec remise parmi les trades historiques
2. **Simulation** : Simule 1 an de trading (trades_per_year tirages)
3. **Ruine** : Vérifie si l'equity passe sous 40% du capital initial
4. **Répétition** : 2500 simulations par niveau de capital
5. **Métriques** : Probabilité de ruine, Return/DD ratio, etc.
6. **Recommandation** : Premier niveau satisfaisant les 3 critères Davey

## 7.4 Intégration avec le Site AI

Les liens bidirectionnels sont gérés par :
- `sync_mc_to_site.py` : Copie MC vers `html_reports/MonteCarlo/`
- `add_mc_link.py` : Ajoute liens MC dans les fiches AI

---

# 8. Système de Corrélation

## 8.1 Vue d'ensemble

Analyse de corrélation des stratégies avec comparaison Long Terme vs Court Terme, selon la **méthode Kevin Davey**.

### Fichier Existant

```
C:\TradeData\scripts\correlation_analysis_v2.py  (~63 KB)
```

## 8.2 Méthode Kevin Davey

1. **Deux matrices** : Long Terme (depuis 2012) + Court Terme (12 derniers mois)
2. **Méthode** : R² (coefficient de détermination) = Pearson²
3. **Scoring** : Somme des corrélations > seuil par stratégie
4. **Filtrage** : Éliminer stratégies avec trop de corrélations

### Paramètres

```python
# Périodes
START_YEAR_LONGTERM = 2012
RECENT_MONTHS = 12

# Seuils
CORRELATION_THRESHOLD = 0.70    # "Corrélé"
HIGH_CORRELATION = 0.85         # "Très corrélé"

# Scoring
WEIGHT_LONGTERM = 0.5
WEIGHT_RECENT = 0.5
```

## 8.3 Outputs

```
C:\TradeData\Results\Correlation\
├── correlation_longterm_YYYYMMDD.html
├── correlation_recent_YYYYMMDD.html
├── correlation_comparison_YYYYMMDD.html
├── correlation_scores_YYYYMMDD.csv
└── correlation_methodology.html
```

---

# 9. Pipeline de Traitement

## 9.1 Ordre d'Exécution Recommandé

```
1. MIGRATE        → Copier données vers V2 (une fois)
2. CONSOLIDATE    → Consolider données + enrichir avec coûts
3. ANALYZE        → Analyser code avec Claude (si nouvelles stratégies)
4. ENRICH         → Enrichir HTML avec KPIs + Equity
5. MONTE_CARLO    → Simuler risque et capital optimal
6. CORRELATION    → Calculer matrices de corrélation
7. DASHBOARD      → Régénérer index.html
8. SYNC_MC        → Synchroniser MC vers site principal
9. SERVE          → Démarrer serveur (optionnel)
```

## 9.2 Dépendances

```
                    ┌─────────────┐
                    │  MIGRATE    │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │ CONSOLIDATE │
                    └──────┬──────┘
           ┌───────────────┼───────────────┐
           │               │               │
    ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
    │   ANALYZE   │ │ MONTE_CARLO │ │ CORRELATION │
    └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
           │               │               │
    ┌──────▼──────┐        │               │
    │   ENRICH    │        │               │
    └──────┬──────┘        │               │
           │               │               │
           └───────────────┼───────────────┘
                           │
                    ┌──────▼──────┐
                    │  DASHBOARD  │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   SYNC_MC   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │    SERVE    │
                    └─────────────┘
```

---

# 10. Scripts Disponibles

## 10.1 Scripts V2 (Nouveaux)

| Script | Statut | Description |
|--------|--------|-------------|
| `migrate_data.py` | ✅ CRÉÉ | Migration données vers V2 |
| `run_enrich.py` | ✅ CRÉÉ | Enrichissement HTML |
| `run_pipeline.py` | 🔲 À CRÉER | Orchestrateur principal |
| `run_monte_carlo.py` | 🔲 À CRÉER | Wrapper Monte Carlo |
| `run_correlation.py` | 🔲 À CRÉER | Wrapper Corrélation |

## 10.2 Scripts Existants (à porter)

| Script Original | Localisation | Module V2 Cible |
|-----------------|--------------|-----------------|
| `ai_strategy_analyzer_v2.py` | `mc_ai_analysis/scripts/` | `src/analyzers/` |
| `dashboard_v4_enhanced.py` | `mc_ai_analysis/scripts/` | `src/generators/` |
| `enrich_html_with_kpis.py` | `mc_ai_analysis/scripts/` | `src/enrichers/` ✅ |
| `monte_carlo.py` | `scripts/monte_carlo_simulator/` | `src/monte_carlo/` |
| `batch_monte_carlo.py` | `scripts/monte_carlo_simulator/` | `src/monte_carlo/` |
| `correlation_analysis_v2.py` | `scripts/` | `src/consolidators/` |
| `consolidate_strategies_v7.py` | `scripts/` | `src/consolidators/` |
| `serve_reports.ps1` | `mc_ai_analysis/` | `server/` |

---

# 11. Guide de Migration

## 11.1 Étape 1 : Migration Données

```bash
cd C:\TradeData\V2
python migrate_data.py --dry-run   # Vérifier
python migrate_data.py              # Exécuter
```

## 11.2 Étape 2 : Tester Enrichissement

```bash
python run_enrich.py
```

## 11.3 Étape 3 : Intégration Monte Carlo

À développer : porter les scripts MC vers `src/monte_carlo/`

## 11.4 Étape 4 : Intégration Corrélation

À développer : porter `correlation_analysis_v2.py` vers `src/consolidators/`

---

# 12. Référence des Données

## 12.1 Volumes

| Données | Fichiers | Taille |
|---------|----------|--------|
| Stratégies PowerLanguage | ~800 | ~5 MB |
| Fonctions custom | ~50 | ~1 MB |
| Equity curves | 245 | 65 MB |
| Portfolio Report | 1 | ~400 KB |
| HTML AI reports | ~400 | 53 MB |
| HTML MC reports | ~250 | ~25 MB |
| Consolidé avec coûts | 1 | ~200 MB |

## 12.2 Résultats Monte Carlo Actuels

- **Stratégies traitées** : 250+
- **Rapports individuels** : 250 CSV + 250 HTML
- **Dashboard global** : MC_Report_latest.html

---

# 13. Roadmap

## Phase 1 : Fondations ✅ (Terminée)

- [x] Structure V2
- [x] Configuration centralisée
- [x] Utilitaires (file_utils, matching, constants)
- [x] Module enrichissement
- [x] Script de migration
- [x] Documentation

## Phase 2 : Migration et Tests (Prochaine)

- [ ] Exécuter migration des données
- [ ] Tester enrichissement
- [ ] Valider résultats

## Phase 3 : Intégration Monte Carlo

- [ ] Porter `monte_carlo.py` → `src/monte_carlo/simulator.py`
- [ ] Porter `batch_monte_carlo.py` → `src/monte_carlo/batch_processor.py`
- [ ] Porter visualizers → `src/monte_carlo/visualizer.py`
- [ ] Créer `run_monte_carlo.py`

## Phase 4 : Intégration Corrélation

- [ ] Porter `correlation_analysis_v2.py` → `src/consolidators/correlation_calculator.py`
- [ ] Créer `run_correlation.py`

## Phase 5 : Dashboard et Serveur

- [ ] Porter `dashboard_v4_enhanced.py` → `src/generators/dashboard_generator.py`
- [ ] Créer `server/serve.py`
- [ ] Intégrer Cloudflare Tunnel

## Phase 6 : Pipeline Unifié

- [ ] Créer `run_pipeline.py` orchestrateur
- [ ] Tests end-to-end
- [ ] Documentation finale

---

# Annexes

## A. Fichiers de l'Ancienne Structure

| Fichier | Taille | Module V2 |
|---------|--------|-----------|
| `ai_strategy_analyzer_v2.py` | 73 KB | `src/analyzers/` |
| `dashboard_v4_enhanced.py` | 51 KB | `src/generators/` |
| `enrich_html_with_kpis.py` | 47 KB | `src/enrichers/` ✅ |
| `monte_carlo.py` | ~15 KB | `src/monte_carlo/` |
| `batch_monte_carlo.py` | ~20 KB | `src/monte_carlo/` |
| `correlation_analysis_v2.py` | 63 KB | `src/consolidators/` |
| `consolidate_strategies_v7.py` | 21 KB | `src/consolidators/` |

## B. Commandes Utiles

```bash
# Monte Carlo - Batch complet
cd C:\TradeData\scripts\monte_carlo_simulator
python batch_monte_carlo.py --all-reports

# Monte Carlo - Par symbole
python batch_monte_carlo.py --symbol GC --all-reports

# Corrélation
cd C:\TradeData\scripts
python correlation_analysis_v2.py

# Sync MC vers site principal
cd C:\TradeData
python sync_mc_to_site.py

# Serveur avec Cloudflare
cd C:\TradeData\mc_ai_analysis
.\serve_reports.ps1
```

---

**Fin de la documentation**
