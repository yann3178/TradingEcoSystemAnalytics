# Trading EcoSystem Analytics V2

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-Private-red.svg)]()
[![Status](https://img.shields.io/badge/Status-Active-green.svg)]()
[![Version](https://img.shields.io/badge/Version-2.3.0-blue.svg)]()
[![Strategies](https://img.shields.io/badge/Strategies-245_analyzed-blue.svg)]()

**Repository:** https://github.com/yann3178/TradingEcoSystemAnalytics

Système unifié d'analyse, documentation et suivi de stratégies de trading algorithmique MultiCharts.

## 🎯 Fonctionnalités

### Module d'Analyse
- **Analyse IA** : Classification automatique des stratégies via Claude API
- **Catégorisation V2** : 8 types standardisés (BREAKOUT, MEAN_REVERSION, TREND_FOLLOWING, etc.)
- **Enrichissement HTML** : KPIs de performance + equity curves interactives Chart.js
- **Monte Carlo** : Simulation de risque et capital optimal (méthode Kevin Davey)

### Module de Corrélation ⭐ NOUVEAU v2.3.0
- **Dashboard Global** : Vue d'ensemble des corrélations (matrices LT/CT, paires extrêmes)
- **Pages Individuelles** : 245 pages HTML par stratégie avec :
  - Score Davey avec badge coloré (🟢🟡🟠🔴)
  - Top 15 stratégies corrélées / diversifiantes
  - Distribution des corrélations
  - Alertes contextuelles
  - Navigation inter-rapports

### Infrastructure
- **Dashboard** : Interface web avec filtres et statistiques
- **Accès distant** : Tunnel Cloudflare pour consultation mobile
- **Pipeline unifié** : `run_pipeline.py` orchestrant tous les modules

## 📊 État Actuel (v2.3.0)

| Métrique | Valeur |
|----------|--------|
| Version actuelle | 2.3.0 |
| Stratégies analysées | 245 |
| Pages HTML AI | 245 |
| Pages corrélation | 245 ⭐ NEW |
| Simulations Monte Carlo | 245 |
| Dashboard corrélation | 1 global + 245 individuels ⭐ NEW |
| Types V2 standardisés | 8 |

### Distribution par Corrélation
| Status | Count | % |
|--------|-------|---|
| 🟢 Diversifiant (<2) | Variable | ~15% |
| 🟡 Modéré (2-5) | Variable | ~45% |
| 🟠 Corrélé (5-10) | Variable | ~25% |
| 🔴 Très corrélé (≥10) | Variable | ~15% |

### Distribution par Type Stratégie
| Type | Description |
|------|-------------|
| BREAKOUT | Cassure de niveaux clés |
| MEAN_REVERSION | Retour à la moyenne |
| TREND_FOLLOWING | Suivi de tendance |
| BIAS_TEMPORAL | Biais temporels (jour/heure) |
| PATTERN_PURE | Patterns chartistes purs |
| HYBRID | Combinaison de plusieurs approches |
| GAP_TRADING | Trading de gaps |
| VOLATILITY | Stratégies basées volatilité |

## 📁 Structure

```
V2/
├── config/              # Configuration centralisée
│   ├── settings.py      # Paramètres globaux
│   └── credentials.json # Clés API (non versionné)
├── src/                 # Code source modulaire
│   ├── analyzers/       # Analyse IA + HTML Generator
│   ├── enrichers/       # KPI + Equity Enricher
│   ├── consolidators/   # Correlation Calculator
│   ├── generators/      # Dashboard + Pages Generators ⭐
│   │   ├── correlation_dashboard.py
│   │   └── correlation_pages.py      # ⭐ NOUVEAU v2.3.0
│   ├── monte_carlo/     # Simulations MC
│   ├── templates/       # Templates HTML ⭐ NOUVEAU
│   └── utils/           # Utilitaires
├── docs/                # Documentation
│   ├── correlation_pages_module.md   # ⭐ NOUVEAU
│   ├── PROJECT_STATUS.md
│   └── CHANGELOG.md                  # ⭐ Mis à jour
├── tests/               # Tests automatisés
├── outputs/             # Résultats (non versionnés)
│   ├── ai_analysis/
│   │   └── html_reports/             # 245 pages AI
│   ├── correlation/
│   │   └── {timestamp}/
│   │       ├── correlation_dashboard_*.html
│   │       └── pages/                # ⭐ 245 pages individuelles
│   └── monte_carlo/                  # Simulations MC
├── run_pipeline.py      # Pipeline principal (v2.3.0) ⭐
└── CHANGELOG.md         # Historique des versions ⭐
```

## 🚀 Installation

```bash
# Cloner le repo
git clone https://github.com/yann3178/TradingEcoSystemAnalytics.git
cd TradingEcoSystemAnalytics/V2

# Créer environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows

# Installer dépendances
pip install -r requirements.txt

# Configurer les credentials (non versionnés)
# Créer config/credentials.json avec vos clés API
```

## 🔧 Usage

### Pipeline Complet
```powershell
# Exécuter tout le pipeline (recommandé)
python run_pipeline.py

# Étapes individuelles
python run_pipeline.py --step enrich       # Enrichissement KPI
python run_pipeline.py --step montecarlo   # Simulations Monte Carlo
python run_pipeline.py --step correlation  # Analyse + Pages corrélation ⭐

# Options
python run_pipeline.py --dry-run           # Mode simulation
python run_pipeline.py --mc-max 10         # Limiter MC à 10 stratégies
```

### Module Corrélation (v2.3.0) ⭐

#### Analyse Complète
```powershell
# Lance analyse + dashboard + 245 pages individuelles
python run_pipeline.py --step correlation
```

**Sorties** :
- `outputs/correlation/{timestamp}/correlation_dashboard_{timestamp}.html` (dashboard global)
- `outputs/correlation/{timestamp}/pages/*.html` (245 pages individuelles)
- `outputs/correlation/{timestamp}/correlation_scores_{timestamp}.csv` (données)

#### Génération Pages Seules
```powershell
# Tester avec 5 pages
python test_correlation_pages_simple.py

# Générer toutes les pages
python generate_all_correlation_pages.py
```

### Analyse IA (Optionnel - Coûteux)
```powershell
# Mode incrémental (recommandé)
python run_pipeline.py --run-ai-analysis --ai-mode delta --ai-max 50

# Analyse complète (long!)
python run_pipeline.py --run-ai-analysis --ai-mode full
```

### Monte Carlo
```powershell
# Simuler toutes les stratégies
python run_pipeline.py --step montecarlo

# Limiter le nombre
python run_pipeline.py --step montecarlo --mc-max 10

# Personnaliser simulations
python run_pipeline.py --mc-sims 5000  # 5000 simulations par niveau
```

## 📈 Workflow Recommandé

```mermaid
graph LR
    A[Données MC] --> B[AI Analysis Optionnel]
    B --> C[KPI Enrichment]
    C --> D[Monte Carlo]
    D --> E[Correlation Analysis]
    E --> F[Pages Individuelles]
    F --> G[Cross-Linking v2.4.0]
```

### Séquence Complète
1. **AI Analysis** (optionnel) : Classification stratégies
2. **KPI Enrichment** : Ajout KPIs aux rapports HTML
3. **Monte Carlo** : Simulations de risque
4. **Correlation** : Analyse + Dashboard global + Pages individuelles ⭐
5. **Cross-Linking** (v2.4.0 - à venir) : Intégration inter-systèmes

## 🎨 Captures d'Écran

### Dashboard Corrélation Global
- Vue d'ensemble toutes stratégies
- Matrices de corrélation LT/CT
- Top paires corrélées/diversifiantes
- Statistiques globales

### Page Corrélation Individuelle ⭐ NOUVEAU
- Badge Score Davey coloré
- 6 statistiques clés (LT/CT)
- Distribution graphique
- Top 15 corrélées/diversifiantes
- Alertes contextuelles
- Navigation inter-rapports

## 🔧 Configuration

### Fichier `config/settings.py`
```python
# Corrélation
CORRELATION_THRESHOLD = 0.70          # Seuil de corrélation
START_YEAR_LONGTERM = 2012            # Début analyse LT
RECENT_MONTHS = 12                    # Durée analyse CT

# Monte Carlo
MC_NB_SIMULATIONS = 1000              # Simulations par niveau
MC_CAPITAL_MINIMUM = 10000            # Capital minimum
MC_CAPITAL_INCREMENT = 5000           # Incrément capital

# AI Analysis
CLAUDE_MODEL = "claude-sonnet-4-20250514"
MAX_STRATEGIES = 0                    # 0 = toutes
```

## 📚 Documentation

- **[CHANGELOG.md](CHANGELOG.md)** : Historique complet des versions
- **[docs/correlation_pages_module.md](docs/correlation_pages_module.md)** : Guide module corrélation ⭐
- **[docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md)** : État détaillé du projet
- **[IMPLEMENTATION_RECAP.md](IMPLEMENTATION_RECAP.md)** : Récap implémentation v2.3.0

## 🐛 Dépannage

### Erreur : Fichier consolidé introuvable
```powershell
# Vérifier les fichiers disponibles
ls outputs/consolidated/

# Générer les données consolidées si nécessaire
python run_pipeline.py --step correlation
```

### Pages corrélation vides
```powershell
# Vérifier les logs
python run_pipeline.py --step correlation --verbose

# Tester avec échantillon
python test_correlation_pages_simple.py
```

### Problème Git large files
```bash
# Les outputs ne sont PAS versionnés (voir .gitignore)
# Seul le code source est versionné
```

## 🔜 Roadmap v2.4.0

### Cross-Linking (En Cours)
- [ ] Onglet "Monte Carlo" dans index AI
- [ ] Bandeau Monte Carlo dans pages AI
- [ ] Onglet "Correlation" dans index AI
- [ ] Bandeau Correlation dans pages AI
- [ ] Intégration pipeline (étape 4)

### Améliorations Futures
- [ ] Export Excel consolidé
- [ ] API REST pour requêtes
- [ ] Visualisations 3D
- [ ] Machine Learning pour prédictions

## 📊 Statistiques Projet

- **Lignes de code** : ~15,000
- **Modules Python** : 45+
- **Tests automatisés** : 20+
- **Documentation** : 10+ fichiers
- **Temps dev total** : ~200 heures

## 🤝 Contribution

Projet privé - Développement interne uniquement.

## 📝 License

Propriétaire - Tous droits réservés.

## 👤 Auteur

**Yann** - Trading System Developer

---

**Version** : 2.3.0  
**Dernière mise à jour** : 29 Novembre 2024  
**Python** : 3.10+  
**Status** : ✅ Production Ready
