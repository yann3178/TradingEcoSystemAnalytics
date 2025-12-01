# Générateur de Rapports HTML Monte Carlo V2

## Description

Ce module génère des rapports HTML interactifs pour les simulations Monte Carlo de stratégies de trading, basées sur la méthodologie Kevin Davey.

## Fonctionnalités

### Pages HTML Générées

1. **Page de Synthèse** (`all_strategies_montecarlo.html`)
   - Vue d'ensemble de toutes les stratégies analysées
   - Statistiques globales (nombre de stratégies OK/Warning/High Risk, P&L total, etc.)
   - Graphiques interactifs:
     - Distribution par statut (pie chart)
     - Return/DD vs Risque de Ruine (scatter plot)
     - Top 10 stratégies par P&L
     - Top 10 stratégies par Return/DD Ratio
   - Tableau triable et filtrable avec toutes les stratégies
   - Liens vers les pages individuelles

2. **Pages Individuelles** (`Individual/{Symbol}_{Strategy}_MC.html`)
   - Statistiques détaillées de la stratégie
   - Paramètres de simulation
   - Recommandation de capital avec critères Kevin Davey
   - Tableau complet des résultats par niveau de capital
   - Graphiques interactifs:
     - Probabilité de ruine vs Capital
     - Return/DD Ratio vs Capital
     - Profit médian vs Capital
     - Probabilité positive vs Capital

### Critères Kevin Davey

Les stratégies sont évaluées selon 3 critères:
- ✅ Risque de ruine ≤ 10%
- ✅ Return/DD Ratio ≥ 2
- ✅ Probabilité de finir positif ≥ 80%

**Statuts:**
- **OK**: Tous les critères satisfaits
- **WARNING**: Au moins le critère de ruine satisfait
- **HIGH_RISK**: Aucun critère satisfait

## Structure des Fichiers

```
V2/
├── outputs/
│   └── monte_carlo/
│       └── YYYYMMDD_HHMM/              # Répertoire de run
│           ├── monte_carlo_summary.csv  # Résumé de toutes les stratégies
│           ├── {Symbol}_{Strategy}_mc.csv  # Résultats détaillés par stratégie
│           └── ...
└── outputs/
    └── html_reports/
        └── montecarlo/
            ├── all_strategies_montecarlo.html  # Page de synthèse
            └── Individual/                     # Pages individuelles
                ├── {Symbol}_{Strategy}_MC.html
                └── ...
```

## Utilisation

### Méthode 1: Script Wrapper (Recommandé)

Depuis la racine de V2:

```bash
# Générer les rapports pour le dernier run Monte Carlo
python run_monte_carlo_html_generator.py

# Générer les rapports pour un run spécifique
python run_monte_carlo_html_generator.py --run 20251201_1130
```

### Méthode 2: Script Direct

Depuis le répertoire `src/monte_carlo/`:

```bash
# Dernier run
python monte_carlo_html_generator.py

# Run spécifique
python monte_carlo_html_generator.py --run 20251201_1130
```

### Méthode 3: Import Python

```python
from src.monte_carlo.monte_carlo_html_generator import main

# Générer les rapports
main()  # Dernier run

# Ou pour un run spécifique
from pathlib import Path
from config.settings import OUTPUT_ROOT

run_dir = OUTPUT_ROOT / "monte_carlo" / "20251201_1130"
main(run_dir)
```

## Format des Données Sources

### Fichier Summary CSV

Format: CSV avec séparateur `;` et décimal `,` (format européen)

Colonnes requises:
- `strategy_name`: Nom de la stratégie
- `symbol`: Symbole de l'instrument (peut être vide, sera extrait du nom)
- `nb_trades`: Nombre total de trades
- `trades_per_year`: Nombre de trades par an
- `years`: Durée du backtest en années
- `total_pnl`: P&L total net
- `avg_pnl_trade`: P&L moyen par trade
- `std_pnl_trade`: Écart-type du P&L par trade
- `win_rate`: Taux de réussite (%)
- `profit_factor`: Profit factor
- `trading_costs`: Coûts de trading totaux
- `recommended_capital`: Capital recommandé (peut être vide/0)
- `status`: Statut (OK/WARNING/HIGH_RISK)
- `ruin_pct`: Probabilité de ruine (%)
- `return_dd_ratio`: Ratio Return/DD
- `prob_positive`: Probabilité de finir positif (%)
- `median_dd_pct`: Drawdown médian (%)
- `median_profit`: Profit médian
- `start_date`: Date de début du backtest
- `end_date`: Date de fin du backtest

### Fichiers CSV Individuels

Format: CSV standard avec métadonnées en commentaires

Métadonnées (lignes commençant par `#`):
- `Strategy`: Nom de la stratégie
- `Generated`: Date de génération
- `Simulations per level`: Nombre de simulations par niveau
- `Trades per year`: Trades simulés par an
- `Ruin threshold`: Seuil de ruine (%)

Colonnes de données:
- `Start_Equity`: Capital initial
- `Ruin_Pct`: Probabilité de ruine (%)
- `Median_DD_Pct`: Drawdown médian (%)
- `Median_Profit`: Profit médian
- `Median_Return_Pct`: Return médian (%)
- `Return_DD_Ratio`: Ratio Return/DD
- `Prob_Positive_Pct`: Probabilité positive (%)
- `Mean_Profit`: Profit moyen
- `Std_Profit`: Écart-type du profit
- `P5_Profit`: Percentile 5 du profit
- `P95_Profit`: Percentile 95 du profit

## Dépendances

- Python 3.8+
- pandas
- numpy (via simulator.py)

## Workflow Complet

1. **Exécuter les simulations Monte Carlo**
   ```bash
   python src/monte_carlo/simulator.py
   ```
   Cela génère les fichiers CSV dans `outputs/monte_carlo/YYYYMMDD_HHMM/`

2. **Générer les rapports HTML**
   ```bash
   python run_monte_carlo_html_generator.py
   ```
   Cela crée les pages HTML dans `outputs/html_reports/montecarlo/`

3. **Consulter les rapports**
   Ouvrir `outputs/html_reports/montecarlo/all_strategies_montecarlo.html` dans un navigateur

## Personnalisation

### Modifier les Templates HTML

Les templates HTML sont dans `src/monte_carlo/html_templates.py`:
- `INDIVIDUAL_TEMPLATE`: Template pour les pages individuelles
- `SUMMARY_TEMPLATE`: Template pour la page de synthèse

Vous pouvez modifier:
- Les styles CSS (variables CSS dans `:root`)
- Les couleurs des graphiques
- La structure des tableaux
- Les textes et labels

### Ajouter des Graphiques

Pour ajouter un graphique, modifiez le template approprié et ajoutez:
1. Un conteneur HTML pour le graphique
2. Le code JavaScript Chart.js correspondant
3. Les données nécessaires passées depuis Python

## Résolution de Problèmes

### Erreur: "Aucun run Monte Carlo trouvé"

Vérifiez que:
- Les simulations Monte Carlo ont bien été exécutées
- Le répertoire `outputs/monte_carlo/` existe
- Il contient au moins un sous-répertoire au format `YYYYMMDD_HHMM`

### Erreur: "Fichier summary introuvable"

Vérifiez que:
- Le fichier `monte_carlo_summary.csv` existe dans le répertoire de run
- Le simulateur Monte Carlo a bien terminé son exécution

### Symbole manquant ou incorrect

Si le symbole n'est pas présent dans le fichier summary, il sera automatiquement extrait du nom de la stratégie (première partie avant le `_`).

Pour les stratégies avec des noms non standards, vous pouvez:
- Modifier la fonction `extract_symbol_from_strategy_name()` dans le générateur
- Ou mettre à jour le fichier summary avec les bons symboles avant génération

### Pages HTML vides ou incomplètes

Vérifiez que:
- Les fichiers CSV individuels existent pour chaque stratégie
- Le nom du fichier CSV correspond au format `{strategy_name}_mc.csv`
- Les données CSV sont bien formatées

## Intégration avec le Pipeline V2

Le générateur HTML s'intègre dans le pipeline V2 via:

1. **Configuration**: Utilise `config/settings.py` pour les chemins
   - `HTML_MONTECARLO_DIR`: Répertoire de sortie des HTML
   - `OUTPUT_ROOT`: Racine des outputs

2. **Convention de nommage**: Compatible avec le système de nommage V2
   - Format des stratégies: `{Symbol}_{NomStratégie}`
   - Format des runs: `YYYYMMDD_HHMM`

3. **Séparation des préoccupations**:
   - Simulation: `simulator.py` (génère les CSV)
   - Visualisation: `monte_carlo_html_generator.py` (génère les HTML)

## Roadmap

Futures améliorations prévues:
- [ ] Intégration avec le dashboard principal
- [ ] Navigation par onglets avec AI Analysis et Correlation
- [ ] Export des graphiques en PNG
- [ ] Génération de PDF depuis les HTML
- [ ] Statistiques comparatives inter-symboles
- [ ] Filtrage avancé et recherche full-text

## Support

Pour toute question ou problème:
1. Vérifiez ce README
2. Consultez les logs de génération
3. Vérifiez les fichiers sources (CSV)

## Changelog

### Version 2.0.0 (2025-12-01)
- Création initiale du générateur HTML V2
- Support complet des critères Kevin Davey
- Pages individuelles et page de synthèse
- Graphiques interactifs Chart.js
- Filtrage et tri dynamiques
- Mobile-friendly responsive design
