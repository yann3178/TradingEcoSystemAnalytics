# 🎯 PROMPT DE CONTINUATION - Trading EcoSystem Analytics V2

## 📋 CONTEXTE DU PROJET

Je développe un système d'analyse automatisé pour mes ~800 stratégies de trading algorithmique MultiCharts. 

**Repository GitHub:** https://github.com/yann3178/TradingEcoSystemAnalytics  
**Dossier local:** `C:\TradeData\V2`  
**Documentation cible:** `C:\TradeData\V2\docs\DOCUMENTATION_COMPLETE.md`

### Objectif Final

Pipeline unifié pour analyser ~800 stratégies avec :
- **Analyse IA** : Classification automatique via Claude API (Anthropic)
- **Enrichissement HTML** : KPIs + equity curves interactives
- **Monte Carlo** : Simulation risque/capital (méthode Kevin Davey)
- **Corrélation** : Matrices LT/CT avec scoring Davey
- **Dashboards** : Interfaces web interactives mobile-friendly
- **Accès distant** : Tunnel Cloudflare pour consultation mobile

---

## ✅ ÉTAT ACTUEL (28/11/2025) - ~65% COMPLÉTÉ

### Modules Implémentés et Fonctionnels

```
C:\TradeData\V2\src\
├── utils/
│   ├── matching.py                   # ✅ Fuzzy matching Levenshtein (23 tests PASS)
│   ├── file_utils.py                 # ✅ Lecture robuste multi-encodage
│   └── constants.py                  # ✅ Constantes partagées
├── enrichers/
│   ├── kpi_enricher.py               # ✅ Injection KPIs dans HTML (11 tests PASS)
│   ├── equity_enricher.py            # ✅ Courbes equity Chart.js
│   └── styles.py                     # ✅ CSS centralisé
├── monte_carlo/
│   ├── config.py                     # ✅ Paramètres Kevin Davey
│   ├── data_loader.py                # ✅ Lecture formats Titan/CSV
│   └── simulator.py                  # ✅ Moteur MC (8 tests PASS)
├── consolidators/
│   ├── config.py                     # ✅ Config corrélation Davey
│   └── correlation_calculator.py     # ✅ Matrices LT/CT, scores, export dashboard
├── generators/
│   └── correlation_dashboard.py      # ✅ Dashboard HTML 6 onglets responsive
└── analyzers/                        # ✅ NOUVEAU - Porté le 28/11/2025
    ├── __init__.py                   # ✅ Module exports
    ├── config.py                     # ✅ 8 catégories standardisées + prompts
    ├── code_parser.py                # ✅ Parser PowerLanguage + hash + fonctions clés
    ├── ai_analyzer.py                # ✅ Intégration Claude API + tracking delta
    └── html_generator.py             # ✅ Rapports individuels + dashboard
```

### Scripts Principaux

```
C:\TradeData\V2\
├── run_pipeline.py          # ✅ Pipeline unifié (3 étapes: enrich, MC, correlation)
├── run_enrich.py            # ✅ Enrichissement standalone
├── run_ai_analysis.py       # ✅ NOUVEAU - Analyse IA standalone
├── config/settings.py       # ✅ Configuration centralisée
├── migrate_data.py          # ✅ Migration données
└── tests/
    ├── test_ai_analyzer.py  # ✅ NOUVEAU - Tests module analyzers
    └── ...autres tests
```

### Dernier Test Réussi (28/11/2025)

```
python run_pipeline.py --step correlation
→ 244 stratégies analysées en 27.7 secondes
→ 84% diversifiantes, 0 très corrélées
→ Dashboard HTML 71 KB généré avec succès
```

---

## ✅ PRIORITÉ 1 : Analyse IA - COMPLÉTÉ

**Module porté:** `src/analyzers/`

**Fonctionnalités implémentées:**
- ✅ Classification automatique en 8 catégories : BREAKOUT, MEAN_REVERSION, TREND_FOLLOWING, PATTERN, VOLATILITY, SEASONAL, MOMENTUM, OTHER
- ✅ Génération de rapports HTML par stratégie
- ✅ Gestion rate limits API Anthropic avec retry
- ✅ Mode delta (incrémental) pour ne pas ré-analyser les stratégies inchangées
- ✅ Système de tracking avec hash de code pour détecter les modifications
- ✅ Support des fonctions clés (_OHLCMulti5, PatternFast)
- ✅ Dashboard index.html avec filtres et statistiques

**Usage:**
```powershell
cd C:\TradeData\V2

# Mode delta (incrémental)
python run_ai_analysis.py

# Ré-analyser tout
python run_ai_analysis.py --mode full

# Limiter à 10 stratégies (test)
python run_ai_analysis.py --max 10

# Test sans appel API
python run_ai_analysis.py --dry-run

# Retraiter les erreurs
python run_ai_analysis.py --retry-errors
```

**Fichiers générés:**
- CSV: `outputs/ai_analysis/strategies_ai_analysis.csv`
- HTML: `outputs/ai_analysis/html_reports/*.html`
- Dashboard: `outputs/ai_analysis/html_reports/index.html`
- Tracking: `outputs/ai_analysis/strategy_tracking.json`
- Log: `outputs/ai_analysis/ai_analyzer.log`

---

## 🔴 CE QUI RESTE À FAIRE (par priorité)

### PRIORITÉ 2 : Dashboard Principal Amélioré (`src/generators/dashboard_generator.py`)

**Objectif:** Améliorer le dashboard principal avec plus de fonctionnalités

**Source de référence:** `C:\TradeData\mc_ai_analysis\scripts\dashboard_v4_enhanced.py` (51 KB)

**Améliorations à apporter:**
- Ajouter les liens vers Monte Carlo
- Ajouter les liens vers corrélation
- Améliorer le responsive mobile
- Ajouter plus de filtres (symbole, score min/max...)

### PRIORITÉ 3 : Liens Inter-Dashboards

**Objectif:** Relier tous les dashboards entre eux

**Liens à implémenter:**
- Dashboard corrélation → Rapports HTML détaillés par stratégie
- Fiche AI → Fiche Monte Carlo
- Fiche MC → Fiche AI
- Dashboard principal → Toutes les fiches

**Chemins des rapports:**
- Rapports AI: `C:\TradeData\V2\outputs\ai_analysis\html_reports\{strategy}.html`
- Rapports MC: `C:\TradeData\Results\MonteCarlo\Individual\{symbol}_{strategy}_MC.html`
- Dashboard corrélation: `C:\TradeData\V2\outputs\correlation\{timestamp}\correlation_dashboard_*.html`

### PRIORITÉ 4 : Monte Carlo Batch + Visualizer

**Objectif:** Compléter le module Monte Carlo avec traitement batch et rapports HTML

**Sources à porter:**
- `C:\TradeData\scripts\monte_carlo_simulator\batch_monte_carlo.py` (~500 lignes)
- `C:\TradeData\scripts\monte_carlo_simulator\individual_visualizer.py` (~300 lignes)
- `C:\TradeData\scripts\monte_carlo_simulator\batch_visualizer.py` (~400 lignes)

**Modules à créer:**
```
src/monte_carlo/
├── simulator.py          # ✅ EXISTE
├── config.py             # ✅ EXISTE
├── data_loader.py        # ✅ EXISTE
├── batch_processor.py    # 🔴 À CRÉER
└── visualizer.py         # 🔴 À CRÉER
```

### PRIORITÉ 5 : Serveur + Cloudflare Tunnel

**Objectif:** Accès distant sécurisé aux dashboards

**Modules à créer:**
```
server/
├── serve.py              # Serveur HTTP Python
└── cloudflare_tunnel.py  # Gestion tunnel Zero Trust
```

**Source existante:** `C:\TradeData\mc_ai_analysis\serve_reports.ps1`

---

## 📋 CONVENTIONS TECHNIQUES

### Format CSV Français
- Séparateur: `;`
- Décimal: `,`
- Encodage: `utf-8-sig`

### Catégories de Stratégies (8 catégories standardisées)
```python
STRATEGY_CATEGORIES = [
    "BREAKOUT",        # Cassures de niveaux, range breakouts
    "MEAN_REVERSION",  # Retour à la moyenne, RSI, Bollinger
    "TREND_FOLLOWING", # Suivi de tendance, momentum directionnel
    "PATTERN",         # Patterns chartistes, candlesticks
    "VOLATILITY",      # Basé sur la volatilité, ATR
    "SEASONAL",        # Saisonnalité, timing intraday, bias
    "MOMENTUM",        # Momentum pur, force relative
    "OTHER",           # Autres, hybrides, inclassables
]
```

### Seuils Kevin Davey - Monte Carlo
```python
DEFAULT_MC_CONFIG = {
    'capital_minimum': 5000,
    'capital_increment': 2500,
    'nb_capital_levels': 11,
    'nb_simulations': 2500,
    'ruin_threshold_pct': 0.40,      # Ruine si equity <= 40%
    'max_acceptable_ruin': 0.10,     # Max 10% risque ruine
    'min_return_dd_ratio': 2.0,      # Return/DD minimum
    'min_prob_positive': 0.80,       # 80% prob finir positif
}
```

### Seuils Kevin Davey - Corrélation
```python
DEFAULT_CORR_CONFIG = {
    'start_year_longterm': 2012,
    'recent_months': 12,
    'correlation_threshold': 0.70,
    'weight_longterm': 0.5,
    'weight_recent': 0.5,
}
```

---

## 🗂️ FICHIERS DE RÉFÉRENCE (V1/Legacy)

### Scripts Restants à Porter

| Fichier | Taille | Priorité | Module V2 Cible |
|---------|--------|----------|-----------------|
| `dashboard_v4_enhanced.py` | 51 KB | 🔴 P2 | `src/generators/` |
| `batch_monte_carlo.py` | ~20 KB | 🟡 P4 | `src/monte_carlo/` |
| `individual_visualizer.py` | ~15 KB | 🟡 P4 | `src/monte_carlo/` |
| `batch_visualizer.py` | ~15 KB | 🟡 P4 | `src/monte_carlo/` |

### Chemins Importants

```
C:\TradeData\
├── V2\                              # Projet V2 actuel
│   ├── src\analyzers\               # ✅ Module AI porté
│   └── outputs\ai_analysis\         # Sorties analyse IA
├── mc_ai_analysis\scripts\          # Scripts AI originaux
├── scripts\monte_carlo_simulator\   # Scripts MC originaux
├── scripts\correlation_analysis_v2.py  # Script corrélation original
├── MC_Export_Code\clean\Strategies\ # 830 fichiers de stratégies
└── Results\
    ├── HTML_Reports\                # ~400 rapports HTML AI (legacy)
    ├── MonteCarlo\Individual\       # ~250 rapports MC
    ├── Portfolio_Report_V2_*.csv    # KPIs stratégies
    └── Consolidated_Strategies_*.txt # 1.5M lignes données
```

---

## 🚀 COMMANDES UTILES

```powershell
cd C:\TradeData\V2

# Tests
pytest tests/ -v                      # Tous les tests
pytest tests/test_ai_analyzer.py -v   # Tests module AI
python tests/test_ai_analyzer.py      # Exécution directe tests AI

# Analyse IA
python run_ai_analysis.py             # Mode delta
python run_ai_analysis.py --mode full # Tout ré-analyser
python run_ai_analysis.py --max 10    # Test avec 10 stratégies
python run_ai_analysis.py --dry-run   # Test config sans API

# Pipeline
python run_pipeline.py                # Pipeline complet
python run_pipeline.py --step correlation  # Corrélation seule
python run_pipeline.py --dry-run      # Aperçu sans exécuter

# Enrichissement
python run_enrich.py                  # Enrichir HTML avec KPIs
```

---

## 📊 MÉTRIQUES ACTUELLES

| Métrique | Valeur |
|----------|--------|
| Stratégies totales (code) | ~830 |
| Stratégies analysables (corrélation) | 244 |
| Lignes données consolidées | 1,514,882 |
| Temps analyse corrélation | ~28 secondes |
| Couverture tests | Bonne (50+ tests) |

---

## 🎯 PROCHAINE TÂCHE

**Continuer avec la PRIORITÉ 2 : Améliorer le Dashboard Principal**

1. Ajouter les liens vers les rapports Monte Carlo
2. Ajouter les liens vers le dashboard de corrélation
3. Améliorer le responsive pour mobile
4. Ajouter des filtres supplémentaires

---

**Note:** Les fichiers du projet sont accessibles via les outils `view` ou `Filesystem:read_text_file`. La documentation complète est dans `C:\TradeData\V2\docs\DOCUMENTATION_COMPLETE.md`.
