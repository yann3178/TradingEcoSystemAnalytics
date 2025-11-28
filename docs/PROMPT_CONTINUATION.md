# Prompt de Continuation - Trading EcoSystem Analytics

**Repository GitHub:** https://github.com/yann3178/TradingEcoSystemAnalytics

## Contexte du Projet

Je travaille sur la réorganisation d'un système complet d'analyse de stratégies de trading MultiCharts. Le projet couvre :

1. **Analyse IA** : Classification automatique des stratégies avec Claude
2. **Enrichissement HTML** : Ajout KPIs + Equity curves aux rapports
3. **Monte Carlo** : Simulation de risque et capital optimal (méthode Kevin Davey)
4. **Corrélation** : Matrices de corrélation LT/CT avec scoring (méthode Kevin Davey)
5. **Dashboard** : Interface web interactive avec filtres
6. **Accès distant** : Tunnel Cloudflare pour mobile

Le travail initial était réparti entre deux projets Claude :
- "Automatisation Strategy ID Card generation and DB"
- "Trading Strategy Dashboard and Database"

Nous avons créé une nouvelle structure V2 dans `C:\TradeData\V2\` sans toucher à l'ancienne structure.

---

## Ce qui a été fait (V2)

### Structure créée
```
C:\TradeData\V2\
├── config/settings.py           ✅ Configuration centralisée
├── data/                        📦 Répertoires vides (à migrer)
├── src/
│   ├── utils/                   ✅ Utilitaires (file_utils, matching, constants)
│   ├── enrichers/               ✅ Modules d'enrichissement (kpi, equity, styles)
│   ├── analyzers/               🔲 À porter
│   ├── consolidators/           🔲 À porter
│   ├── monte_carlo/             🔲 À porter ← NOUVEAU
│   └── generators/              🔲 À porter
├── outputs/html_reports/        📦 Vide (à migrer)
├── server/                      🔲 À développer
├── docs/
│   └── DOCUMENTATION_COMPLETE.md  ✅ Documentation exhaustive
├── migrate_data.py              ✅ Script de migration
├── run_enrich.py                ✅ Script d'enrichissement
└── requirements.txt             ✅ Dépendances
```

### Modules développés en V2
1. **`src/utils/`** : Lecture fichiers, fuzzy matching, constantes (patterns, symbols)
2. **`src/enrichers/`** : Ajout KPIs + Equity curves aux HTML
3. **`migrate_data.py`** : Copie les données sans toucher aux originaux
4. **`run_enrich.py`** : Script principal d'enrichissement

---

## Composants existants à intégrer

### Monte Carlo (FONCTIONNEL - à porter)

**Localisation** : `C:\TradeData\scripts\monte_carlo_simulator\`

| Fichier | Description |
|---------|-------------|
| `monte_carlo.py` | Moteur MC (classe `MonteCarloSimulator`) |
| `batch_monte_carlo.py` | Traitement batch toutes stratégies |
| `individual_visualizer.py` | Rapport HTML individuel |
| `batch_visualizer.py` | Dashboard HTML global |
| `data_loader.py` | Parsing fichiers trades |
| `config.py` | Paramètres Kevin Davey |

**Outputs générés** : `C:\TradeData\Results\MonteCarlo\`
- ~250 rapports individuels (CSV + HTML)
- Dashboard global `MC_Report_latest.html`
- Liens bidirectionnels avec les fiches AI

**Paramètres Kevin Davey** :
```python
'capital_minimum': 5000
'capital_increment': 2500
'nb_capital_levels': 11
'nb_simulations': 2500
'ruin_threshold_pct': 0.40
'max_acceptable_ruin': 0.10
'min_return_dd_ratio': 2.0
'min_prob_positive': 0.80
```

### Corrélation (FONCTIONNEL - à porter)

**Localisation** : `C:\TradeData\scripts\correlation_analysis_v2.py` (~63 KB)

**Méthode Kevin Davey** :
- Deux matrices : Long Terme (2012→) + Court Terme (12 mois)
- Méthode R² (Pearson²) avec seuils 0.70/0.85
- Scoring par stratégie (somme des corrélations > seuil)
- Pondération LT/CT 50/50

### Autres scripts à porter

| Script | Localisation | Taille |
|--------|--------------|--------|
| `ai_strategy_analyzer_v2.py` | `mc_ai_analysis/scripts/` | 73 KB |
| `dashboard_v4_enhanced.py` | `mc_ai_analysis/scripts/` | 51 KB |
| `consolidate_strategies_v7.py` | `scripts/` | 21 KB |
| `serve_reports.ps1` | `mc_ai_analysis/` | 3.5 KB |

---

## Intégration actuelle AI ↔ Monte Carlo

Des scripts ont été créés pour l'intégration :
- `sync_mc_to_site.py` : Copie MC vers `html_reports/MonteCarlo/`
- `add_mc_link.py` : Ajoute liens MC dans les fiches AI
- Liens bidirectionnels entre fiches AI et fiches MC

---

## Prochaines étapes à réaliser

### Étape 1 : Migration des données
```bash
cd C:\TradeData\V2
python migrate_data.py --dry-run
python migrate_data.py
```

### Étape 2 : Tester enrichissement
```bash
python run_enrich.py
```

### Étape 3 : Porter Monte Carlo vers V2
- Créer `src/monte_carlo/`
- Adapter les chemins vers la config centralisée
- Créer `run_monte_carlo.py`

### Étape 4 : Porter Corrélation vers V2
- Créer `src/consolidators/correlation_calculator.py`
- Créer `run_correlation.py`

### Étape 5 : Dashboard et Serveur
- Porter `dashboard_v4_enhanced.py`
- Créer serveur HTTP Python + Cloudflare

### Étape 6 : Pipeline unifié
- Créer `run_pipeline.py` orchestrateur

---

## Fichiers clés à lire

**Documentation** :
- `C:\TradeData\V2\docs\DOCUMENTATION_COMPLETE.md` - Doc exhaustive avec Monte Carlo et Corrélation

**Configuration V2** :
- `C:\TradeData\V2\config\settings.py`

**Monte Carlo existant** :
- `C:\TradeData\scripts\monte_carlo_simulator\monte_carlo.py`
- `C:\TradeData\scripts\monte_carlo_simulator\batch_monte_carlo.py`
- `C:\TradeData\scripts\monte_carlo_simulator\config.py`

**Corrélation existante** :
- `C:\TradeData\scripts\correlation_analysis_v2.py`

**Pour les anciens scripts AI** :
- `C:\TradeData\mc_ai_analysis\scripts\ai_strategy_analyzer_v2.py`
- `C:\TradeData\mc_ai_analysis\scripts\dashboard_v4_enhanced.py`

---

## Demande

Continue le développement du pipeline V2 en suivant cette priorité :

1. **Exécute la migration** (`python migrate_data.py`)
2. **Teste l'enrichissement** (`python run_enrich.py`)
3. **Porte le système Monte Carlo** vers `src/monte_carlo/`
4. **Porte le système de Corrélation** vers `src/consolidators/`
5. **Crée le pipeline unifié** `run_pipeline.py`

**Important** : 
- Les fichiers volumineux (>50 KB) nécessitent une lecture partielle
- Garde la rétrocompatibilité avec l'ancienne structure en fallback
- Les rapports MC existants dans `Results/MonteCarlo/` fonctionnent déjà

---

## Informations techniques

- **OS** : Windows
- **Python** : 3.10+
- **API** : Claude (Anthropic) pour l'analyse IA
- **Serveur** : Cloudflare Tunnel pour accès mobile
- **Données** : ~800 stratégies, 245 equity curves, ~400 rapports HTML, ~250 rapports MC
- **Volume consolidé** : ~200 MB (fichier avec coûts)

---

## Tests de Validation

### Structure des Tests
```
tests/
├── conftest.py                    # Fixtures partagées
├── pytest.ini                     # Configuration pytest
├── create_test_reference.py       # Script création données référence
├── TEST_STRATEGY.md               # Documentation stratégie de tests
├── data/
│   ├── samples/                   # Échantillons d'entrée (10 stratégies)
│   └── expected/                  # Résultats référence V1
├── unit/                          # Tests unitaires
│   └── test_matching.py           # Tests fuzzy matching
└── validation/                    # Tests régression V1 vs V2
    ├── test_kpi_regression.py
    └── test_monte_carlo_regression.py
```

### Commandes de Test
```bash
# Créer les données de référence (une fois)
python tests/create_test_reference.py

# Tous les tests
pytest

# Tests unitaires uniquement
pytest tests/unit/ -v

# Tests de validation V1 vs V2
pytest tests/validation/ -v

# Avec couverture
pytest --cov=src --cov-report=html
```

### Toléances pour Tests Stochastiques (Monte Carlo)
- Capital recommandé : ± 1 niveau (2500$)
- Probabilité ruine : ± 2%
- Return/DD ratio : ± 10%
- Seed fixe (42) pour reproductibilité

---

## Git et Versioning

### Structure Git
```
C:\TradeData\V2\
├── .gitignore                     # Exclut données sensibles
├── .github/workflows/tests.yml    # CI/CD GitHub Actions
├── README.md                      # README pour GitHub
├── CHANGELOG.md                   # Historique des versions
└── config/credentials.template.json  # Template (sans secrets)
```

### Commandes Git
```bash
# Initialiser le repo (depuis C:\TradeData\V2)
cd C:\TradeData\V2
git init
git add .
git commit -m "Initial commit V2.0.0"

# Connecter au repository GitHub
git remote add origin https://github.com/yann3178/TradingEcoSystemAnalytics.git
git branch -M main
git push -u origin main
```

### Ce qui est versionné
- Code source (`src/`)
- Tests et données de test échantillons (`tests/`)
- Documentation (`docs/`)
- Configuration (sans credentials)
- Scripts d'exécution

### Ce qui N'EST PAS versionné
- `config/credentials.json` (secrets)
- `data/` (données volumineuses)
- `outputs/` (résultats générés)
- `logs/`
