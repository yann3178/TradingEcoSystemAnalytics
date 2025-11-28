# CHANGELOG

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

---

## [2.1.1] - 2025-11-28 (23:30)

### 🐛 Corrigé

- **Import Error** : Suppression import inutilisé `enrich_html_with_equity_curve` dans `run_pipeline.py`
  - Causait : `ImportError: cannot import name 'enrich_html_with_equity_curve'`
  - Impact : Étape 1 (KPI Enrichment) échouait
  - Solution : Import supprimé (fonction non utilisée)

- **Missing Function** : Ajout de la fonction `get_kpi_styles()` dans `src/enrichers/styles.py`
  - Causait : `ImportError: cannot import name 'get_kpi_styles'`
  - Impact : Étape 1 (KPI Enrichment) échouait
  - Solution : Fonction wrapper ajoutée pour retourner `KPI_DASHBOARD_CSS`

### ✅ Testé

- Pipeline complet en mode `--dry-run` : ✅ Succès
- Toutes les étapes s'exécutent sans erreur
- Imports validés sur tous les modules

### 📝 Documentation

- Mise à jour `docs/README.md` avec version 2.1.1
- Mise à jour `docs/PROJECT_STATUS.md` avec bugs corrigés
- Ajout `docs/CHANGELOG.md` (ce fichier)

---

## [2.1.0] - 2025-11-28 (23:00)

### ⭐ Ajouté - MAJOR UPDATE

#### Preprocessing Intégré dans Pipeline

**Nouveau système automatisé de bout en bout**

- **Étape 0A : Strategy Mapping**
  - Fonction `step_0a_mapping()` dans `run_pipeline.py`
  - Génération automatique de `strategy_mapping.json`
  - Mapping de 243 stratégies → symboles
  - Durée : ~2 secondes

- **Étape 1B : Name Harmonization**
  - Fonction `step_1b_harmonization()` dans `run_pipeline.py`
  - Renommage automatique : `Strategy.html` → `SYMBOL_Strategy.html`
  - Exécution après enrichissement KPI (ordre critique)
  - Backup automatique dans `backups/{timestamp}/`
  - Rapport JSON : `outputs/consolidated/migration_report.json`
  - Durée : ~5 secondes

- **Nouvelles Options CLI**
  - `--skip-preprocessing` : Désactiver mapping + harmonisation
  - Options existantes conservées (rétrocompatibilité 100%)

#### Configuration Pipeline

- `PipelineConfig.run_preprocessing = True` : Active/désactive preprocessing
- Gestion d'erreurs non-bloquante : Warnings si échec, pipeline continue
- Rapports JSON détaillés : `outputs/pipeline_reports/pipeline_report_{timestamp}.json`

### 🔄 Modifié

#### Ordre d'Exécution Pipeline

```
AVANT (V2.0.0):
1. KPI Enrichment
2. Monte Carlo
3. Correlation

APRÈS (V2.1.0):
0A. Strategy Mapping      ← NOUVEAU
1.  KPI Enrichment
1B. Name Harmonization    ← NOUVEAU
2.  Monte Carlo
3.  Correlation
```

**Raison de l'ordre :**
- KPI Enricher cherche fichiers par nom **original** (avant harmonisation)
- Harmonisation APRÈS enrichissement évite échec de matching
- Monte Carlo et Correlation indépendants des noms HTML

#### Documentation

- `docs/README.md` : Section "Pipeline Automatisé Complet" ajoutée
- `docs/PROJECT_STATUS.md` : Section "Pipeline Unifié" ajoutée
- Architecture diagrammes mis à jour

### 📊 Statistiques V2.1.0

- **Fichiers modifiés** : 3 (`run_pipeline.py`, `README.md`, `PROJECT_STATUS.md`)
- **Lignes ajoutées** : +190 (code) + 500 (docs)
- **Nouvelles fonctions** : 2 (`step_0a_mapping`, `step_1b_harmonization`)
- **Nouvelles options CLI** : 1 (`--skip-preprocessing`)
- **Durée pipeline** : +7 secondes (~2s mapping + ~5s harmonization)

### 🔒 Sécurité

- Triple backup système maintenu :
  1. Git tag v2.0.0-stable
  2. Backup manuel `backups/run_pipeline_BACKUP_20251128_231216.py`
  3. Backup automatique migration dans `backups/{timestamp}/`

### ✅ Tests

- Dry-run complet : ✅ Validé
- Étape individuelle : ✅ Validé
- Skip preprocessing : ✅ Validé
- Rétrocompatibilité : ✅ 100%

---

## [2.0.0] - 2025-11-27

### ⭐ Ajouté - REFACTORISATION COMPLÈTE

#### Architecture V2

**Structure modulaire complète**

```
src/
├── analyzers/      # Analyse IA
├── enrichers/      # Enrichissement HTML
├── consolidators/  # Consolidation données
├── generators/     # Génération dashboards
├── monte_carlo/    # Simulations MC
└── utils/          # Utilitaires
```

#### Modules Core

- **Analyzers**
  - `ai_analyzer.py` : Classification IA avec Claude API
  - `html_generator.py` : Génération rapports HTML
  - 8 catégories standardisées (BREAKOUT, MEAN_REVERSION, etc.)

- **Enrichers**
  - `kpi_enricher.py` : Injection KPIs depuis Portfolio Report
  - `equity_enricher.py` : Graphiques Chart.js interactifs
  - `styles.py` : CSS responsive pour dashboards

- **Consolidators**
  - `correlation_calculator.py` : Pearson + R² Kevin Davey
  - Analyse Long Terme (depuis 2012) + Court Terme (12 mois)

- **Generators**
  - `index_generator.py` : Dashboard principal
  - `correlation_dashboard.py` : Dashboard corrélation interactif

- **Monte Carlo**
  - `simulator.py` : Simulation Kevin Davey
  - `data_loader.py` : Détection format automatique

- **Utils**
  - `strategy_mapper.py` : Mapping stratégie→symbole ⭐
  - `matching.py` : Fuzzy matching Levenshtein

#### Configuration

- `config/settings.py` : Configuration centralisée
- Variables d'environnement : `ANTHROPIC_API_KEY`
- Chemins auto-détectés avec Path()

#### Scripts

- `run_pipeline.py` : Orchestration complète
- `run_enrich.py` : Enrichissement seul
- `migrate_data.py` : Migration V1→V2

### 🔄 Migration V1 → V2

- ✅ 281 stratégies migrées depuis `mc_ai_analysis`
- ✅ Mapping 66 types V1 → 8 catégories V2
- ✅ 281 fichiers HTML générés
- ✅ Tracking JSON avec code hash
- ✅ Aucune perte de données

### 📊 Statistiques V2.0.0

- **Stratégies backtestées** : 243
- **Fichiers HTML** : 581
- **Equity curves** : 245
- **Symboles** : 39
- **Modules Python** : 12

### 🐛 Corrigé

- **Canvas cleanup** : Chart.js réutilisation canvas corrigée
- **Encoding** : Gestion UTF-8 avec BOM
- **Path handling** : Windows paths avec pathlib.Path()

---

## [1.x] - 2025-11-26 et avant

### Système Legacy (Pré-V2)

- Analyse IA non structurée dans `mc_ai_analysis/`
- 66 types de stratégies non standardisés
- Scripts dispersés sans architecture claire
- Enrichissement HTML manuel
- Pas de système de mapping
- Pas de pipeline automatisé

---

## Légende

- **⭐ Ajouté** : Nouvelles fonctionnalités
- **🔄 Modifié** : Changements dans fonctionnalités existantes
- **🐛 Corrigé** : Corrections de bugs
- **🔒 Sécurité** : Corrections de vulnérabilités
- **📝 Documentation** : Mises à jour documentation
- **✅ Testé** : Validations et tests
- **📊 Statistiques** : Métriques et chiffres clés

---

## Versions à Venir

### [2.2.0] - Prévue pour Décembre 2025

**User Experience Integration**

- Navigation inter-dashboards
- Look & feel harmonisé
- Liens croisés entre rapports

### [2.3.0] - Prévue pour Q1 2026

**Optimisations Performance**

- Cache strategy_mapping.json
- Incremental updates
- Parallélisation Monte Carlo

### [3.0.0] - Prévue pour Q2 2026

**Production & Extensions**

- Cloudflare Zero Trust permanent
- API REST
- Export PDF
- Notifications

---

*Dernière mise à jour : 28 novembre 2025 23:30*
