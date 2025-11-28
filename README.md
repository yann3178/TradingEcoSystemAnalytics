# Trading EcoSystem Analytics

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-Private-red.svg)]()
[![Status](https://img.shields.io/badge/Status-Development-yellow.svg)]()

**Repository:** https://github.com/yann3178/TradingEcoSystemAnalytics

Système unifié d'analyse, documentation et suivi de stratégies de trading MultiCharts.

## 🎯 Fonctionnalités

- **Analyse IA** : Classification automatique des stratégies via Claude (Anthropic)
- **Enrichissement HTML** : KPIs de performance + equity curves interactives
- **Monte Carlo** : Simulation de risque et capital optimal (méthode Kevin Davey)
- **Corrélation** : Matrices de corrélation LT/CT avec scoring
- **Dashboard** : Interface web avec filtres et statistiques
- **Accès distant** : Tunnel Cloudflare pour consultation mobile

## 📁 Structure

```
V2/
├── config/          # Configuration centralisée
├── src/             # Code source modulaire
│   ├── analyzers/   # Analyse IA
│   ├── enrichers/   # Enrichissement HTML
│   ├── monte_carlo/ # Simulations MC
│   └── utils/       # Utilitaires
├── tests/           # Tests automatisés
├── docs/            # Documentation
└── outputs/         # Résultats (non versionnés)
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
cp config/credentials.template.json config/credentials.json
# Éditer avec vos clés API
```

## 📖 Documentation

- [Documentation Complète](docs/DOCUMENTATION_COMPLETE.md)
- [Guide de Continuation](docs/PROMPT_CONTINUATION.md)

## 🧪 Tests

```bash
# Tous les tests
pytest

# Tests avec couverture
pytest --cov=src --cov-report=html

# Tests de validation V1 vs V2
pytest tests/validation/ -v
```

## ⚠️ Données Privées

Les données de trading ne sont PAS versionnées (voir `.gitignore`).
Seuls les échantillons de test anonymisés sont inclus dans `tests/data/samples/`.

## 📝 Changelog

Voir [CHANGELOG.md](CHANGELOG.md)

## 📄 License

Propriétaire - Usage personnel uniquement.
