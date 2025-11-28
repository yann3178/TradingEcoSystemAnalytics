# Trading EcoSystem Analytics

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-Private-red.svg)]()
[![Status](https://img.shields.io/badge/Status-Active-green.svg)]()
[![Strategies](https://img.shields.io/badge/Strategies-281_migrated-blue.svg)]()

**Repository:** https://github.com/yann3178/TradingEcoSystemAnalytics

Système unifié d'analyse, documentation et suivi de stratégies de trading algorithmique MultiCharts.

## 🎯 Fonctionnalités

- **Analyse IA** : Classification automatique des stratégies via Claude API (281 stratégies analysées)
- **Catégorisation V2** : 8 types standardisés (BREAKOUT, MEAN_REVERSION, TREND_FOLLOWING, etc.)
- **Enrichissement HTML** : KPIs de performance + equity curves interactives Chart.js
- **Monte Carlo** : Simulation de risque et capital optimal (méthode Kevin Davey)
- **Corrélation** : Matrices Pearson + R² rolling avec scoring
- **Dashboard** : Interface web avec filtres et statistiques
- **Accès distant** : Tunnel Cloudflare pour consultation mobile

## 📊 État Actuel

| Métrique | Valeur |
|----------|--------|
| Stratégies migrées V1→V2 | 281 |
| Rapports HTML générés | 281 |
| Types V2 standardisés | 8 |
| Equity curves disponibles | 241 |
| Stratégies total estimé | ~800 |

### Distribution par Type
| Type | Count |
|------|-------|
| BREAKOUT | 183 |
| MEAN_REVERSION | 39 |
| BIAS_TEMPORAL | 23 |
| TREND_FOLLOWING | 19 |
| PATTERN_PURE | 8 |
| HYBRID | 6 |
| GAP_TRADING | 2 |
| VOLATILITY | 1 |

## 📁 Structure

```
V2/
├── config/              # Configuration centralisée
│   └── settings.py      # Tous les paramètres
├── src/                 # Code source modulaire
│   ├── analyzers/       # Analyse IA + HTML Generator
│   ├── enrichers/       # KPI + Equity Enricher
│   ├── consolidators/   # Correlation Calculator
│   ├── generators/      # Dashboard Generators
│   ├── monte_carlo/     # Simulations MC
│   └── utils/           # Matching, Constants, File Utils
├── docs/                # Documentation
│   ├── PROJECT_STATUS.md
│   └── NEXT_SESSION_PROMPT.md
├── tests/               # Tests automatisés
├── server/              # Serveur HTTP Cloudflare
├── outputs/             # Résultats (non versionnés)
│   ├── ai_analysis/     # 281 analyses + HTML
│   ├── html_reports/    # Rapports enrichis
│   ├── correlation/     # Dashboards corrélation
│   └── monte_carlo/     # Simulations MC
└── data/                # Données sources (non versionnées)
    ├── equity_curves/   # 241 fichiers
    └── portfolio_reports/
```

## 🚀 Installation

```bash
# Cloner le repo
git clone https://github.com/yann3178/TradingEcoSystemAnalytics.git
cd TradingEcoSystemAnalytics

# Créer environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows

# Installer dépendances
pip install -r requirements.txt

# Configurer les credentials (non versionnés)
# Créer config/credentials.json avec vos clés API
```

## 🔧 Usage

### Migration V1 → V2
```powershell
python migrate_v1_analysis.py --force --verbose
```

### Enrichissement des rapports
```powershell
# Rapports AI Analysis V2
python run_enrich_ai_reports.py --force

# Rapports généraux
python run_enrich.py --force
```

### Analyse de nouvelles stratégies
```powershell
python run_ai_analysis.py
```

### Pipeline complet
```powershell
python run_pipeline.py
```

## 📖 Documentation

- [État du Projet](docs/PROJECT_STATUS.md)
- [Prompt pour Continuation](docs/NEXT_SESSION_PROMPT.md)
- [Changelog](CHANGELOG.md)

## 🔐 Données Privées

Les données de trading ne sont PAS versionnées (voir `.gitignore`) :
- `data/` : Equity curves, Portfolio Reports
- `outputs/` : Rapports générés, corrélations, Monte Carlo
- `config/credentials.json` : Clés API

## 📝 Changelog

Voir [CHANGELOG.md](CHANGELOG.md)

## 📄 License

Propriétaire - Usage personnel uniquement.

---

*Dernière mise à jour : 28 Novembre 2025*
