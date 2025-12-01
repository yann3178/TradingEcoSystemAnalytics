# PROMPT: Réécriture Complète du Générateur HTML Monte Carlo Dashboard

## 🎯 Objectif

Réécrire complètement le générateur de la page de synthèse Monte Carlo (`all_strategies_montecarlo.html`) en créant des scripts Python propres, maintenables et fonctionnels.

---

## 📁 Contexte du Projet

### Architecture V2

```
C:/TradeData/V2/
├── config/
│   └── settings.py                          # Configuration globale des chemins
├── src/
│   └── monte_carlo/
│       ├── simulator.py                     # Moteur de simulation Monte Carlo
│       ├── data_loader.py                   # Chargement des données de trading
│       ├── config.py                        # Configuration simulation (nb simulations, etc.)
│       ├── monte_carlo_html_generator.py    # SCRIPT À RÉÉCRIRE
│       └── html_templates.py                # TEMPLATES À RÉÉCRIRE
├── outputs/
│   ├── monte_carlo/
│   │   └── 20251201_1130/                   # Répertoire d'un run
│   │       ├── monte_carlo_summary.csv      # Résumé de toutes les stratégies
│   │       ├── AAPL_SOM_UA_2310_Y_2_mc.csv  # Résultats détaillés par stratégie
│   │       ├── BP_TOP_UA_452_BP_15_mc.csv
│   │       └── ...                          # 245 fichiers CSV au total
│   └── html_reports/
│       └── montecarlo/
│           ├── all_strategies_montecarlo.html        # PAGE À GÉNÉRER
│           └── Individual/
│               ├── AAPL_AAPL_SOM_UA_2310_Y_2_MC.html
│               └── ...                                # 245 pages individuelles
```

---

## 📊 Données Sources

### 1. Fichier `monte_carlo_summary.csv`

**Localisation**: `outputs/monte_carlo/{run}/monte_carlo_summary.csv`

**Colonnes principales**:
```csv
strategy_name,symbol,nb_trades,trades_per_year,years,total_pnl,avg_pnl_trade,std_pnl_trade,
win_rate,profit_factor,trading_costs,recommended_capital,status,ruin_pct,return_dd_ratio,
prob_positive,median_dd_pct,median_profit,start_date,end_date
```

**Exemples de données**:
```
strategy_name: AAPL_SOM_UA_2310_Y_2
symbol: nan (ou vide - le symbole est dans strategy_name)
nb_trades: 156
total_pnl: 45230.50
win_rate: 58.5
profit_factor: 1.85
recommended_capital: 15000
status: OK | WARNING | HIGH_RISK
ruin_pct: 8.5
return_dd_ratio: 2.3
prob_positive: 82.5
```

**Notes importantes**:
- La colonne `symbol` est souvent vide/NaN
- Le symbole est toujours le PREMIER élément de `strategy_name` (ex: AAPL dans AAPL_SOM_UA_2310_Y_2)
- 245 lignes = 245 stratégies

### 2. Fichiers CSV individuels `{strategy_name}_mc.csv`

**Localisation**: `outputs/monte_carlo/{run}/{strategy_name}_mc.csv`

**Exemple**: `AAPL_SOM_UA_2310_Y_2_mc.csv`

**Colonnes**:
```csv
Start_Equity,Ruin_Pct,Median_DD_Pct,Median_Profit,Median_Return_Pct,
Return_DD_Ratio,Prob_Positive_Pct,Mean_Profit,Std_Profit,P5_Profit,P95_Profit
```

**Contenu** (10 lignes typiques - niveaux de capital):
```
Start_Equity,Ruin_Pct,Return_DD_Ratio,Prob_Positive_Pct,...
10000,41.3,0.85,65.2,...
15000,8.5,2.3,82.5,...    <- Capital recommandé (premier où ruin ≤ 10%)
20000,2.1,3.8,91.2,...
25000,0.5,4.5,95.8,...
...
55000,0.0,8.2,99.1,...
```

**Usage**: Ces fichiers contiennent TOUS les niveaux de capital testés pour chaque stratégie, permettant le recalcul dynamique côté client.

---

## 🎨 Spécifications Fonctionnelles

### Page HTML à Générer: `all_strategies_montecarlo.html`

#### A. Vue d'Ensemble (Stats Globales)

**6 cartes statistiques** :
1. Total stratégies (245)
2. Stratégies OK (critères Kevin Davey satisfaits)
3. Stratégies WARNING (ruine OK mais autres critères non)
4. Stratégies HIGH_RISK (ruine > 10%)
5. Total trades (somme de tous nb_trades)
6. P&L total net (somme de tous total_pnl)

#### B. Panneau Critères Dynamiques (⭐ FONCTIONNALITÉ CLÉ)

**Critères configurables par sliders**:

1. **Risque de Ruine Max** (0-30%, défaut 10%)
   - TOUJOURS actif
   - Slider de 0 à 30% par pas de 0.5
   - Affichage temps réel de la valeur

2. **Return/DD Ratio Min** (0-5, défaut 2.0)
   - Activable via checkbox
   - Slider de 0 à 5 par pas de 0.1
   - Désactivé par défaut

3. **Probabilité Positive Min** (0-100%, défaut 80%)
   - Activable via checkbox
   - Slider de 0 à 100% par pas de 1
   - Désactivé par défaut

**3 boutons d'action**:
- 🔄 **Recalculer Maintenant** : Applique les critères et met à jour le tableau
- ↺ **Réinitialiser** : Ruine 10%, autres désactivés
- 📘 **Kevin Davey Standard** : Ruine 10% + Return/DD 2.0 + Prob 80%

#### C. Stats Live (Mise à Jour Dynamique)

**6 compteurs mis à jour en temps réel**:
1. Nombre de stratégies OK
2. Nombre de stratégies WARNING
3. Nombre de stratégies HIGH_RISK
4. Nombre de stratégies avec capital trouvé
5. Capital moyen recommandé
6. Capital médian recommandé

**Style**: Bordure jaune distinctive pour indiquer que c'est "live"

#### D. Filtres d'Affichage Standards

**3 filtres** (masquent les lignes sans recalculer):
1. Symbole (dropdown avec tous les symboles)
2. Statut (Tous | OK | WARNING | HIGH_RISK)
3. Trades minimum (input numérique, défaut 20)

**2 boutons**:
- Appliquer
- Reset

#### E. Graphiques Statiques (Chart.js)

**4 graphiques** (NE SE METTENT PAS À JOUR dynamiquement):

1. **Pie Chart** : Distribution OK/WARNING/HIGH_RISK
2. **Scatter Chart** : Return/DD vs Risque de Ruine (points colorés par statut)
3. **Bar Chart Horizontal** : Top 10 P&L Total
4. **Bar Chart Horizontal** : Top 10 Return/DD Ratio

**Important**: Les graphiques utilisent les données initiales et NE changent PAS quand on recalcule avec les sliders.

#### F. Tableau Détaillé

**11 colonnes**:
1. Stratégie (lien vers page individuelle)
2. Symbol
3. Statut (badge coloré)
4. Capital Recommandé ($)
5. Trades
6. P&L Net ($)
7. Win Rate (%)
8. Profit Factor
9. Risque Ruine (%)
10. Return/DD Ratio
11. Prob > 0 (%)

**Fonctionnalités**:
- Tri par colonne (clic sur header)
- Attribut `data-strategy="{strategy_name}"` sur chaque `<tr>` (ESSENTIEL pour le recalcul)
- Attribut `data-symbol="{symbol}"` sur chaque `<tr>`
- Attribut `data-status="{status}"` sur chaque `<tr>`
- Animation highlight (0.5s) lors du recalcul

**Liens vers pages individuelles**:
- Pattern: `Individual/{symbol}_{strategy_name}_MC.html`
- Exemple: `Individual/AAPL_AAPL_SOM_UA_2310_Y_2_MC.html`

---

## ⚙️ Logique de Recalcul Dynamique (JavaScript)

### Algorithme `findRecommendedCapital(strategyName)`

**Input**: Nom de la stratégie

**Données nécessaires**: Objet JavaScript `strategiesDetailed` contenant pour chaque stratégie:
```javascript
strategiesDetailed[strategyName] = {
    symbol: "AAPL",
    nb_trades: 156,
    total_pnl: 45230.50,
    win_rate: 58.5,
    profit_factor: 1.85,
    levels: [
        {
            capital: 10000,
            ruin_pct: 41.3,
            return_dd: 0.85,
            prob_positive: 65.2,
            median_dd_pct: 12.5,
            median_profit: 8500
        },
        // ... 10 niveaux au total
    ]
}
```

**Logique**:

```
Pour chaque niveau (trié par capital croissant):
    
    1. Vérifier Critère 1 (TOUJOURS actif):
       ruinOK = level.ruin_pct <= activeCriteria.maxRuin
    
    2. Vérifier Critère 2 (si activé):
       returnDDOK = activeCriteria.minReturnDD === null 
                    OU level.return_dd >= activeCriteria.minReturnDD
    
    3. Vérifier Critère 3 (si activé):
       probOK = activeCriteria.minProbPositive === null 
                OU level.prob_positive >= activeCriteria.minProbPositive
    
    4. Si TOUS les critères actifs sont OK:
       → Retourner { capital: level.capital, status: 'OK', metrics: {...} }
    
    5. Si SEULEMENT la ruine est OK (mais pas les autres):
       → Retourner { capital: level.capital, status: 'WARNING', metrics: {...} }

Si aucun niveau ne satisfait au moins la ruine:
    → Retourner { capital: null, status: 'HIGH_RISK', metrics: {} }
```

### Fonction `updateTableRow(strategyName, result)`

**Actions**:
1. Trouver la ligne: `document.querySelector(\`tr[data-strategy="${strategyName}"]\`)`
2. Mettre à jour le badge de statut (classe + texte)
3. Mettre à jour la cellule capital recommandé
4. Mettre à jour les cellules métriques (ruine%, return/dd, prob%)
5. Ajouter classe `highlight` pendant 500ms (animation)

### Fonction `recalculateAll()`

**Actions**:
1. Initialiser compteurs (okCount, warningCount, highRiskCount, capitals[])
2. Pour chaque stratégie dans `strategiesDetailed`:
   - Appeler `findRecommendedCapital()`
   - Appeler `updateTableRow()`
   - Incrémenter compteurs
   - Collecter capitaux
3. Mettre à jour les 6 stats live
4. Calculer et afficher capital moyen et médian

---

## 🛠️ Contraintes Techniques

### Python

**Version**: Python 3.10+

**Bibliothèques**:
- `pandas` : Manipulation des CSV
- `json` : Sérialisation des données pour JavaScript
- `pathlib` : Gestion des chemins
- `datetime` : Horodatage

**Encodage des fichiers**:
- CSV: UTF-8 avec BOM (utf-8-sig) ou latin-1 comme fallback
- HTML: UTF-8

**Format CSV européen**:
- Séparateur: point-virgule (`;`)
- Décimales: virgule (`,`) → convertir en point (`.`) pour JSON

### HTML/CSS

**Palette de couleurs (Dark Theme)**:
```css
--bg-primary: #0f0f1a      /* Fond page */
--bg-secondary: #1a1a2e    /* Fond header/cartes */
--bg-card: #16213e         /* Fond cartes */
--text-primary: #eaeaea    /* Texte principal */
--text-secondary: #a0a0a0  /* Texte secondaire */
--accent-green: #00d4aa    /* OK / Positif */
--accent-red: #ff6b6b      /* HIGH_RISK / Négatif */
--accent-blue: #4ecdc4     /* Accent principal */
--accent-yellow: #ffe66d   /* WARNING */
```

**Responsive**:
- Breakpoint: 768px
- Mobile: Grilles en 1 colonne
- Desktop: Grilles en multi-colonnes

### JavaScript

**Version**: ES6+ (compatibilité navigateurs modernes)

**Bibliothèques externes**:
- Chart.js 4.x (CDN): `https://cdn.jsdelivr.net/npm/chart.js`

**Pas de dépendances** : Vanilla JavaScript uniquement

**Structure des données embarquées**:

```javascript
// Données de synthèse (depuis monte_carlo_summary.csv)
const strategiesData = [
    {
        strategy_name: "AAPL_SOM_UA_2310_Y_2",
        symbol: "AAPL",
        status: "OK",
        nb_trades: 156,
        total_pnl: 45230.50,
        win_rate: 58.5,
        profit_factor: 1.85,
        recommended_capital: 15000,
        ruin_pct: 8.5,
        return_dd_ratio: 2.3,
        prob_positive: 82.5
    },
    // ... 245 stratégies
];

// Données détaillées (depuis fichiers individuels CSV)
const strategiesDetailed = {
    "AAPL_SOM_UA_2310_Y_2": {
        symbol: "AAPL",
        nb_trades: 156,
        total_pnl: 45230.50,
        win_rate: 58.5,
        profit_factor: 1.85,
        levels: [
            { capital: 10000, ruin_pct: 41.3, return_dd: 0.85, prob_positive: 65.2, median_dd_pct: 12.5, median_profit: 8500 },
            { capital: 15000, ruin_pct: 8.5, return_dd: 2.3, prob_positive: 82.5, median_dd_pct: 8.2, median_profit: 12750 },
            // ... 10 niveaux
        ]
    },
    // ... 245 stratégies
};
```

**Événements à gérer**:
- `input` sur les sliders (mise à jour affichage valeur)
- `change` sur les checkboxes (activation/désactivation sliders)
- `click` sur boutons (recalcul, reset, Kevin Davey)
- `click` sur headers de tableau (tri)
- `load` sur window (initialisation + premier recalcul)

---

## 📝 Structure des Scripts à Créer

### 1. `monte_carlo_html_generator.py`

**Responsabilités**:
- Trouver le dernier run Monte Carlo
- Charger `monte_carlo_summary.csv`
- Générer les pages individuelles (une par stratégie)
- Générer la page de synthèse
- Charger les données détaillées de TOUS les niveaux de capital pour le recalcul dynamique

**Fonctions principales**:

```python
def find_latest_monte_carlo_run() -> Path:
    """Trouve le répertoire de run le plus récent."""
    
def load_summary_data(run_dir: Path) -> pd.DataFrame:
    """Charge monte_carlo_summary.csv."""
    
def load_detailed_data(run_dir: Path, summary_df: pd.DataFrame) -> Dict:
    """
    Charge tous les fichiers {strategy_name}_mc.csv.
    Retourne un dict avec les 10 niveaux de capital pour chaque stratégie.
    """
    
def generate_individual_html(row: pd.Series, run_dir: Path, output_dir: Path):
    """Génère une page HTML individuelle pour une stratégie."""
    
def generate_summary_html(summary_df: pd.DataFrame, detailed_data: Dict, 
                          output_file: Path, run_dir: Path):
    """
    Génère all_strategies_montecarlo.html avec:
    - Stats globales
    - Panneau critères dynamiques
    - Graphiques statiques
    - Tableau détaillé
    - JavaScript pour recalcul dynamique
    """
    
def main(run_dir: Optional[Path] = None):
    """Point d'entrée principal."""
```

**Gestion des symboles**:
```python
# La colonne symbol est souvent vide, extraire depuis strategy_name
def extract_symbol(row: pd.Series) -> str:
    if pd.notna(row['symbol']) and row['symbol'] != '':
        return row['symbol']
    # Prendre le premier élément avant le premier underscore
    return row['strategy_name'].split('_')[0] if '_' in row['strategy_name'] else 'UNKNOWN'
```

**Pattern de nommage des fichiers CSV**:
- Summary: `monte_carlo_summary.csv`
- Individuels: `{strategy_name}_mc.csv` (PAS de symbole en préfixe !)
- Exemple: `AAPL_SOM_UA_2310_Y_2_mc.csv`

### 2. `html_templates.py`

**Contenu**:
- `INDIVIDUAL_TEMPLATE` : Template pour pages individuelles (ne pas toucher)
- `SUMMARY_TEMPLATE` : Template pour page de synthèse (À RÉÉCRIRE COMPLÈTEMENT)

**Structure du SUMMARY_TEMPLATE**:

```python
SUMMARY_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Monte Carlo Batch Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        /* CSS complet inline */
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <!-- Stats globales -->
        <!-- Panneau critères dynamiques -->
        <!-- Stats live -->
        <!-- Filtres d'affichage -->
        <!-- Graphiques (4 cartes) -->
        <!-- Tableau -->
        <!-- Footer -->
    </div>
    
    <script>
        // Données embarquées (via .format())
        const strategiesData = {strategies_json};
        const strategiesDetailed = {strategies_detailed_json};
        
        // Configuration Chart.js
        // Création des 4 graphiques STATIQUES
        // Logique de recalcul dynamique
        // Event listeners
        // Initialisation au chargement
    </script>
</body>
</html>
"""
```

**Placeholders Python `.format()`**:

```python
{generation_date}          # Date de génération
{total_strategies}         # Nombre total de stratégies
{ok_count}                 # Stratégies OK
{warning_count}            # Stratégies WARNING
{high_risk_count}          # Stratégies HIGH_RISK
{total_trades}             # Somme des trades
{total_pnl}                # Somme des P&L
{symbol_options}           # Options HTML pour dropdown symboles
{table_rows}               # Lignes HTML du tableau
{config_info}              # Info config Monte Carlo
{strategies_json}          # JSON de strategiesData
{strategies_detailed_json} # JSON de strategiesDetailed
```

**⚠️ ATTENTION CRITIQUE: Échappement des accolades JavaScript**

Dans un template Python `.format()`, TOUTES les accolades JavaScript `{ }` doivent être **doublées** en `{{ }}`.

**Exemple**:
```javascript
// ❌ ERREUR (Python va chercher une variable)
function myFunc() {
    return { value: 10 };
}

// ✅ CORRECT (accolades doublées)
function myFunc() {{
    return {{ value: 10 }};
}}
```

---

## ✅ Checklist de Validation

Avant de considérer la réécriture terminée, vérifier:

### Python
- [ ] Le script trouve automatiquement le dernier run
- [ ] Le chargement du CSV summary fonctionne avec encodage européen
- [ ] Les 245 fichiers CSV individuels sont chargés sans erreur
- [ ] Les symboles sont correctement extraits des strategy_names
- [ ] Les données JSON sont correctement formatées (pas de NaN/Infinity)
- [ ] Le fichier HTML est généré sans erreur `.format()`
- [ ] Les 245 pages individuelles sont générées

### HTML/CSS
- [ ] La page s'affiche correctement (pas d'erreur console)
- [ ] Les 6 stats globales affichent les bonnes valeurs
- [ ] Les 4 graphiques Chart.js s'affichent
- [ ] Le tableau contient 245 lignes
- [ ] Les liens vers pages individuelles fonctionnent
- [ ] Le design dark theme est appliqué
- [ ] La page est responsive (mobile + desktop)

### JavaScript
- [ ] `strategiesDetailed` contient 245 stratégies avec leurs niveaux
- [ ] Le slider Ruine met à jour l'affichage en temps réel
- [ ] Les checkboxes activent/désactivent les sliders
- [ ] Le bouton "Recalculer" déclenche `recalculateAll()`
- [ ] Les lignes du tableau clignotent (animation highlight)
- [ ] Les capitaux recommandés changent selon les critères
- [ ] Les stats live se mettent à jour
- [ ] Le bouton "Kevin Davey" configure: Ruine 10%, Return/DD 2.0, Prob 80%
- [ ] Le tri de colonne fonctionne
- [ ] Les filtres d'affichage masquent les bonnes lignes
- [ ] Console navigateur (F12): aucune erreur JavaScript

### Tests Fonctionnels
- [ ] Config Simple (Ruine 10% seule): ~150 stratégies OK
- [ ] Config Kevin Davey (10%/2.0/80%): ~80 stratégies OK
- [ ] Config Conservateur (5%/2.5/85%): ~40 stratégies OK
- [ ] Config Agressif (20%/1.5/70%): ~200 stratégies OK
- [ ] Tri décroissant par P&L: top stratégie en premier
- [ ] Filtre "Symbol = AAPL": affiche seulement stratégies AAPL

---

## 🚀 Instructions d'Exécution

### Génération
```bash
cd C:/TradeData/V2/src/monte_carlo
python monte_carlo_html_generator.py
```

### Ouverture
```
C:/TradeData/V2/outputs/html_reports/montecarlo/all_strategies_montecarlo.html
```

### Test dans le navigateur
1. Ouvrir la page HTML
2. Ouvrir la console (F12)
3. Vérifier: "Loaded: 245 strategies"
4. Déplacer le slider Ruine → voir les valeurs changer en temps réel
5. Cliquer "Recalculer" → voir les lignes clignoter
6. Vérifier les stats live mises à jour

---

## 📚 Ressources Additionnelles

### Méthodologie Kevin Davey

**Critères standards**:
- Risque de Ruine ≤ 10%
- Return/DD Ratio ≥ 2.0
- Probabilité > 0 ≥ 80%

**Référence**: Ces critères viennent du livre "Building Winning Algorithmic Trading Systems" de Kevin Davey.

### Exemple de Configuration settings.py

```python
from pathlib import Path

# Racine du projet
V2_ROOT = Path(__file__).parent.parent

# Répertoires de sortie
OUTPUT_ROOT = V2_ROOT / "outputs"
HTML_MONTECARLO_DIR = OUTPUT_ROOT / "html_reports" / "montecarlo"

# Configuration Monte Carlo
MONTE_CARLO_CONFIG = {
    'nb_simulations': 1000,      # Simulations par niveau de capital
    'ruin_threshold': 0.20,      # Seuil de ruine (20% du capital)
    'capital_levels': 10,        # Nombre de niveaux à tester
    'start_capital': 10000,      # Capital de départ
    'step_capital': 5000         # Incrément entre niveaux
}
```

---

## 💡 Conseils d'Implémentation

1. **Commencer simple**: D'abord faire fonctionner le tableau statique, puis ajouter le recalcul dynamique

2. **Tester par étapes**:
   - Étape 1: Générer HTML avec tableau statique
   - Étape 2: Ajouter les graphiques Chart.js
   - Étape 3: Ajouter le JavaScript de recalcul
   - Étape 4: Tester les différentes configurations

3. **Debugging JavaScript**:
   - Utiliser `console.log()` abondamment
   - Vérifier que `strategiesDetailed` est bien chargé
   - Tester `findRecommendedCapital()` sur une stratégie isolée

4. **Gestion des erreurs**:
   - Fichiers CSV manquants
   - Encodage CSV incorrect
   - Données NaN/Infinity dans le JSON
   - Accolades JavaScript non échappées

5. **Performance**:
   - 245 stratégies × 10 niveaux = 2450 lignes de données
   - Le recalcul doit être rapide (< 500ms)
   - Limiter les manipulations DOM (batch updates)

---

## 🎬 Résultat Attendu

Une page HTML autonome qui:
- ✅ Charge instantanément (tout est inline)
- ✅ Fonctionne offline (pas de dépendances externes sauf Chart.js CDN)
- ✅ Permet de tester différentes configurations de risque en temps réel
- ✅ Affiche visuellement l'impact des critères sur le nombre de stratégies validées
- ✅ Est utilisable sur mobile et desktop
- ✅ A un design professionnel dark theme
- ✅ Ne génère AUCUNE erreur console JavaScript

**Le tout en 2 fichiers Python** (`monte_carlo_html_generator.py` + `html_templates.py`) **propres, commentés et maintenables**.

---

Bonne chance ! 🚀
