# Changelog - Trading EcoSystem Analytics V2

## [2.3.0] - 2024-11-29

### ✨ Nouveautés Majeures

#### Module Correlation Pages Individuelles
- **Nouveau module** : `src/generators/correlation_pages.py`
- Génération de pages HTML individuelles pour chaque stratégie (245 pages)
- Profil de corrélation détaillé par stratégie :
  - Score Davey avec badge coloré (🟢🟡🟠🔴)
  - 6 statistiques clés (LT/CT, moyennes, delta)
  - Distribution des corrélations (graphique barres horizontal)
  - Top 15 stratégies les plus corrélées
  - Top 15 stratégies les moins corrélées (opportunités diversification)
  - Alertes contextuelles (score élevé, corrélation critique, forte évolution)
- Design moderne GitHub Dark theme, mobile-friendly
- Navigation : liens vers rapport stratégie et dashboard global

#### Intégration Pipeline
- Pages de corrélation générées automatiquement après l'analyse de corrélation
- Intégration dans `run_pipeline.py` (étape correlation)
- Utilisation des vraies matrices de corrélation (pas de simulation)
- Output : `outputs/correlation/{timestamp}/pages/`

### 🏗️ Architecture

#### Séparation des Responsabilités
- `correlation_calculator.py` : Calculs purs (matrices, scores, statistiques)
- `correlation_pages.py` : Génération HTML uniquement
- Pas de duplication de code
- Architecture cohérente avec `correlation_dashboard.py`

#### Compatibilité
- Compatible avec format CSV européen (séparateur `;`, décimales `,`)
- Gestion flexible des noms de colonnes (`Strategy_ID` vs `Strategy`, `Delta_Avg` vs `Delta_Corr`)
- Extraction automatique de `Strategy_Name` et `Symbol` depuis CSV
- Génération automatique de `Status_Emoji` si absent

### 📝 Documentation

#### Nouveaux Documents
- `docs/correlation_pages_module.md` : Guide complet d'utilisation
- `src/templates/README.md` : Documentation templates HTML
- `IMPLEMENTATION_RECAP.md` : Récapitulatif détaillé de l'implémentation

#### Scripts de Test
- `test_correlation_pages_simple.py` : Test avec données existantes (mock analyzer)
- `generate_all_correlation_pages.py` : Génération complète des 245 pages
- `integrate_correlation_pages.py` : Script d'intégration automatique au pipeline

### 🔧 Améliorations Techniques

#### Gestion des Erreurs
- Try/except robuste pour chaque page générée
- Continuation en cas d'erreur sur une stratégie
- Statistiques détaillées (générées/erreurs/total)
- Logging verbeux avec progression

#### Performance
- Génération : ~50-100 ms par page
- 245 pages en ~1-2 minutes
- Taille par page : ~50-80 KB HTML

### 🔄 Migration

#### Suppression Code Redondant
- Supprimé : `src/generators/correlation_pages_generator.py` (duplication détectée)
- Évité la violation du principe de responsabilité unique
- Architecture propre maintenue

### 📊 Données

#### Format Pages HTML
- Template inline (pas de dépendance externe)
- Support futur pour template externe (`src/templates/correlation_page.html`)
- JSON data embedded pour interactivité JavaScript
- Graphiques avec distribution 5 niveaux

### ⚙️ Configuration

#### Paramètres Hérités
- `correlation_threshold` : 0.70 (seuil de corrélation)
- `start_year_longterm` : 2012 (début analyse LT)
- `recent_months` : 12 (durée analyse CT)
- `top_n` : 15 (nombre dans les tops)

### 🐛 Corrections

#### Gestion Colonnes CSV
- Fix : Adaptation aux colonnes réelles du CSV
- Fix : Renommage automatique `Strategy_ID` → `Strategy`
- Fix : Gestion colonnes optionnelles (`Max_Corr_LT_With`, `Max_Corr_CT_With`)
- Fix : Delta_Avg vs Delta_Corr

### 📦 Fichiers Modifiés

```
Modifié:
- run_pipeline.py (version 2.2.0 → 2.3.0)
  - Ajout import CorrelationPagesGenerator
  - Génération pages après dashboard dans step_correlation()
  - Gestion erreurs ImportError

Créé:
- src/generators/correlation_pages.py (~600 lignes)
- src/templates/README.md
- docs/correlation_pages_module.md
- test_correlation_pages_simple.py
- generate_all_correlation_pages.py
- integrate_correlation_pages.py
- IMPLEMENTATION_RECAP.md

Supprimé:
- src/generators/correlation_pages_generator.py (redondant)
```

### 🎯 Impact Utilisateur

#### Workflow Amélioré
- **Avant** : Dashboard global uniquement
- **Après** : Dashboard global + 245 pages individuelles détaillées
- Navigation intuitive entre les vues
- Accès rapide aux informations de corrélation par stratégie

#### Cas d'Usage
- Identifier rapidement les stratégies redondantes
- Trouver des opportunités de diversification
- Comprendre l'évolution des corrélations (LT vs CT)
- Décider quelles stratégies éliminer du portefeuille

### 📈 Statistiques

- **Stratégies analysées** : 245
- **Pages générées** : 245
- **Temps de génération** : ~90 secondes
- **Taille totale** : ~12-15 MB
- **Taux de réussite** : 100%

### 🚀 Prochaines Étapes (v2.4.0)

#### Cross-Linking Planifié
- Intégration AI Analysis ↔ Monte Carlo
- Intégration AI Analysis ↔ Correlation
- Onglets navigation dans index.html
- Bandeaux inter-systèmes dans pages individuelles

#### Documentation
- Captures d'écran des pages
- Guide utilisateur complet
- Tutoriels vidéo (optionnel)

---

## [2.2.0] - 2024-11-28

### Fonctionnalités Existantes
- AI Analysis avec Claude API
- KPI Enrichment (Portfolio Report → HTML)
- Monte Carlo Simulation (Kevin Davey)
- Correlation Dashboard (global)
- Pipeline unifié `run_pipeline.py`

---

## Notes de Version

### Compatibilité
- Python 3.8+
- Pandas, NumPy
- Anthropic Claude API (optionnel)

### Breaking Changes
- Aucun (rétrocompatible avec v2.2.0)

### Deprecations
- Aucun

### Sécurité
- Pas de problèmes de sécurité identifiés
