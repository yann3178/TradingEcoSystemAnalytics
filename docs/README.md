# Trading Strategy Analysis Pipeline V2

## 🎯 Vue d'ensemble

Système unifié d'analyse, documentation et suivi des stratégies de trading MultiCharts.

### Fonctionnalités

- **Analyse IA** : Classification automatique des stratégies avec Claude
- **Enrichissement** : Ajout des KPIs et equity curves aux rapports HTML
- **Dashboard** : Interface web interactive avec filtres et statistiques
- **Corrélation** : Matrice de corrélation des performances
- **Accès distant** : Tunnel Cloudflare pour consultation mobile

## 📁 Structure

```
C:\TradeData\V2\
│
├── config/                     # Configuration centralisée
│   ├── settings.py             # Tous les paramètres
│   ├── credentials.json        # Clés API Google
│   └── instruments_*.csv       # Référentiels
│
├── data/                       # Données sources (read-only)
│   ├── mc_export/              # Code PowerLanguage
│   │   ├── strategies/         # Fichiers .txt des stratégies
│   │   └── functions/          # Fonctions custom
│   ├── equity_curves/          # DataSources (profits journaliers)
│   └── portfolio_reports/      # CSV MultiCharts
│
├── src/                        # Code source
│   ├── analyzers/              # Analyse IA
│   ├── enrichers/              # Enrichissement HTML
│   ├── consolidators/          # Consolidation données
│   ├── generators/             # Génération outputs
│   └── utils/                  # Utilitaires communs
│
├── outputs/                    # Résultats générés
│   ├── html_reports/           # Rapports + index.html
│   ├── csv/                    # Exports tabulaires
│   ├── correlation/            # Matrices de corrélation
│   └── consolidated/           # Données consolidées
│
├── logs/                       # Logs d'exécution
├── server/                     # Serveur web + tunnel
├── docs/                       # Documentation
│
├── run_pipeline.py             # Script principal
├── run_enrich.py               # Enrichissement seul
├── migrate_data.py             # Migration depuis V1
└── requirements.txt            # Dépendances Python
```

## 🚀 Démarrage Rapide

### 1. Migration des données

```bash
# Simulation (sans copie)
python migrate_data.py --dry-run

# Migration réelle
python migrate_data.py
```

### 2. Configuration

Éditer `config/settings.py` si nécessaire :

```python
# Clé API Claude
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

# Mode prototype (limiter le nombre de stratégies)
MAX_STRATEGIES = 10  # 0 = toutes
```

### 3. Exécution

```bash
# Pipeline complet
python run_pipeline.py

# Enrichissement seul
python run_enrich.py

# Avec options
python run_enrich.py --force --no-backup
```

## 📊 Pipeline

```
┌─────────────────────────────────────────────────────────┐
│                    RUN_PIPELINE.PY                      │
└─────────────────────────────────────────────────────────┘
                          │
    ┌─────────────────────┼─────────────────────┐
    ▼                     ▼                     ▼
┌─────────┐        ┌─────────────┐       ┌───────────┐
│ ANALYZE │        │ CONSOLIDATE │       │  ENRICH   │
│ (IA)    │        │             │       │           │
└────┬────┘        └──────┬──────┘       └─────┬─────┘
     │                    │                    │
     └──────────┬─────────┘────────────────────┘
                ▼
         ┌─────────────┐
         │  DASHBOARD  │
         │  (index)    │
         └─────────────┘
```

## 🔧 Modules

### enrichers/kpi_enricher.py

Ajoute les indicateurs de performance :
- Net Profit, Max Drawdown, Ratio NP/DD
- IS/OOS Monthly Returns, Efficiency Ratio
- YTD Profit, Avg Trade, % Exposition
- Performance par période (M, M-1, W, YTD, Y-1)

### enrichers/equity_enricher.py

Ajoute les graphiques d'equity curve :
- Chart.js interactif
- Distinction visuelle IS/OOS
- Ligne de démarcation OOS

### utils/matching.py

Algorithmes de correspondance :
- Distance de Levenshtein
- Normalisation des noms
- Fuzzy matching avec seuil configurable

## ⚙️ Configuration

### Variables d'environnement

```bash
set ANTHROPIC_API_KEY=sk-ant-...
```

### settings.py

| Paramètre | Description | Défaut |
|-----------|-------------|--------|
| `MAX_STRATEGIES` | Limite (0=toutes) | 0 |
| `FUZZY_MATCH_THRESHOLD` | Seuil matching | 0.80 |
| `MIN_MATCH_CHARS` | Min caractères | 5 |
| `CLAUDE_MODEL` | Modèle IA | claude-sonnet-4-20250514 |

## 📝 Changelog

### V2.0.0 (2025-11-27)
- Refactorisation complète de la structure
- Modules séparés et réutilisables
- Configuration centralisée
- Migration depuis V1 sans perte

## 📞 Support

Voir les logs dans `logs/` pour le diagnostic.
