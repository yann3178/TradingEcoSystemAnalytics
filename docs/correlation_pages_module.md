# Module de Génération de Pages de Corrélation Individuelles

## 📋 Vue d'ensemble

Le module `correlation_pages.py` génère des pages HTML individuelles pour chaque stratégie, affichant son profil de corrélation détaillé.

## 🏗️ Architecture

```
src/
├── consolidators/
│   └── correlation_calculator.py    ← Calculs de corrélation (inchangé)
├── generators/
│   ├── correlation_dashboard.py     ← Dashboard global (existant)
│   └── correlation_pages.py         ← Pages individuelles (NOUVEAU)
└── templates/
    └── README.md                     ← Documentation templates
```

### Séparation des responsabilités

- **CorrelationAnalyzer** : Calcule les matrices de corrélation, scores Davey, statistiques
- **CorrelationPagesGenerator** : Génère le HTML à partir des résultats de l'analyzer

## 🚀 Utilisation

### Usage Basique

```python
from pathlib import Path
from src.consolidators.correlation_calculator import CorrelationAnalyzer
from src.generators.correlation_pages import CorrelationPagesGenerator
import pandas as pd

# 1. Charger les données
df = pd.read_csv("consolidated_strategies.csv", sep=';', encoding='utf-8-sig', decimal=',')

# 2. Analyser les corrélations
analyzer = CorrelationAnalyzer(df)
analyzer.run()

# 3. Générer les pages individuelles
generator = CorrelationPagesGenerator(analyzer)
stats = generator.generate_all(
    output_dir=Path("outputs/correlation_pages"),
    top_n=15,
    verbose=True
)

print(f"✅ {stats['generated']} pages générées")
```

### Paramètres

**CorrelationPagesGenerator.generate_all()**

- `output_dir` : Répertoire de sortie pour les pages HTML
- `top_n` : Nombre de stratégies dans les listes top/bottom (défaut: 15)
- `verbose` : Afficher la progression (défaut: True)

**Retour** : Dict avec `{'generated': int, 'errors': int, 'total': int}`

## 📄 Contenu des Pages Générées

Chaque page contient :

### 1. En-tête
- Nom de la stratégie et symbole
- Score Davey avec badge coloré (Diversifiant/Modéré/Corrélé/Très corrélé)
- Alertes contextuelles

### 2. Profil de Corrélation
- Nombre de stratégies corrélées (LT et CT)
- Corrélation moyenne (LT et CT)
- Delta (évolution CT - LT)
- Corrélation maximale

### 3. Distribution des Corrélations
- Graphique en barres horizontal
- 5 buckets : très négative, négative, neutre, positive, très positive

### 4. Top Stratégies Corrélées
- Table des 15 stratégies les plus corrélées
- Corrélations LT et CT
- Delta d'évolution

### 5. Top Stratégies Diversifiantes
- Table des 15 stratégies les moins corrélées
- Étoiles de diversification (⭐⭐⭐ = excellente)

### 6. Navigation
- Lien vers le rapport stratégie principal
- Lien vers le dashboard de corrélation

## 🎨 Personnalisation

### Template Externe (Optionnel)

Par défaut, le générateur utilise un template HTML inline. Pour personnaliser le design :

1. Créer `src/templates/correlation_page.html`
2. Utiliser les placeholders `{{variable}}`
3. Le générateur détectera automatiquement le template

Voir `src/templates/README.md` pour la liste complète des placeholders.

## 🧪 Tests

```bash
cd C:\TradeData\V2
python test_correlation_pages.py
```

Le script de test :
1. Charge les données consolidées
2. Exécute l'analyse de corrélation
3. Génère 5 pages (échantillon test)
4. Propose de générer toutes les pages

## 📊 Intégration au Pipeline

### Ajouter au run_pipeline.py

```python
# Après l'étape de corrélation existante
if args.step in ['all', 'correlation']:
    from src.generators.correlation_pages import CorrelationPagesGenerator
    
    # analyzer déjà créé dans l'étape correlation
    pages_gen = CorrelationPagesGenerator(analyzer)
    stats = pages_gen.generate_all(
        output_dir=CORRELATION_DIR / "pages",
        top_n=15,
        verbose=True
    )
    
    print(f"✅ {stats['generated']} pages de corrélation générées")
```

### Nouvelle Étape Pipeline (Option Alternative)

```python
# Étape 6A: Pages de corrélation individuelles
if args.step in ['all', '6A', 'correlation_pages']:
    print_step_header("6A", "Génération Pages Corrélation")
    
    # Charger les résultats de l'analyse
    from src.generators.correlation_pages import CorrelationPagesGenerator
    
    # Recréer l'analyzer ou charger les résultats sauvegardés
    # ...
    
    generator = CorrelationPagesGenerator(analyzer)
    stats = generator.generate_all(
        output_dir=CORRELATION_DIR / "pages",
        verbose=True
    )
```

## 📁 Sorties

### Structure des fichiers

```
outputs/correlation_pages/
├── StrategyName_Symbol_correlation.html
├── AnotherStrategy_ES_correlation.html
├── ...
```

### Nomenclature

- Format : `{StrategyName}_{Symbol}_correlation.html`
- Caractères spéciaux remplacés par `_`
- Conforme au standard V2

## ⚙️ Configuration

Les paramètres de corrélation sont hérités de `CorrelationAnalyzer` :

- `start_year_longterm` : Année de début LT (défaut: 2012)
- `recent_months` : Nombre de mois CT (défaut: 12)
- `correlation_threshold` : Seuil de corrélation (défaut: 0.7)
- `weight_longterm` : Poids LT dans score Davey (défaut: 0.5)
- `weight_recent` : Poids CT dans score Davey (défaut: 0.5)

## 🔧 Dépannage

### Erreur: "L'analyzer doit avoir exécuté run() avant"

```python
# Solution: Exécuter run() avant de créer le générateur
analyzer.run()
generator = CorrelationPagesGenerator(analyzer)
```

### Erreur: Module not found

```python
# Solution: Ajouter le répertoire V2 au path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
```

### Pages vides ou erreurs JavaScript

- Vérifier que les données de l'analyzer sont complètes
- Vérifier l'encodage UTF-8 du fichier HTML
- Ouvrir la console développeur du navigateur

## 📈 Performance

- **Temps** : ~50-100 ms par page
- **Mémoire** : ~200 MB pour 800 stratégies
- **Disque** : ~50-80 KB par page HTML

Pour 800 stratégies :
- Temps total : ~1 minute
- Espace disque : ~40-60 MB

## 🔄 Version History

### v2.3.0 (Actuel)
- Création du module `correlation_pages.py`
- Architecture séparée (calculs vs génération)
- Template inline avec support template externe
- Intégration avec CorrelationAnalyzer

## 🎯 Prochaines Étapes

1. ✅ Module créé et testé
2. ⏳ Intégration au pipeline
3. ⏳ Enrichissement index.html avec liens vers pages de corrélation
4. ⏳ Cross-linking avec pages AI Analysis et Monte Carlo
