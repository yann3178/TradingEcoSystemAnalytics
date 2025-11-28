# Changelog - Trading EcoSystem Analytics

Toutes les modifications notables de ce projet sont documentées dans ce fichier.

**Repository:** https://github.com/yann3178/TradingEcoSystemAnalytics

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### À faire
- Enrichir les 281 rapports AI Analysis avec KPIs et equity curves
- Analyser les ~550 stratégies restantes (total ~800)
- Configurer Cloudflare Zero Trust tunnel permanent
- Générer matrices de corrélation sur dataset complet

---

## [2.1.0] - 2025-11-28

### Ajouté
- **Migration V1→V2 complète** : 281 stratégies migrées depuis `mc_ai_analysis`
- **Script `run_enrich_ai_reports.py`** : Enrichissement dédié pour rapports AI Analysis V2
- **Chemins AI Analysis** dans `config/settings.py` :
  - `AI_ANALYSIS_DIR` : `outputs/ai_analysis/`
  - `AI_HTML_REPORTS_DIR` : `outputs/ai_analysis/html_reports/`
  - `AI_INDEX_FILE` : Dashboard index.html

### Modifié
- **`migrate_v1_analysis.py`** : Génération HTML complète avec dashboard
- **`config/settings.py`** : Ajout chemins AI Analysis V2
- **`docs/PROJECT_STATUS.md`** : État complet du projet mis à jour
- **`docs/NEXT_SESSION_PROMPT.md`** : Instructions pour continuation

### Statistiques Migration
| Métrique | Valeur |
|----------|--------|
| Stratégies migrées | 281 |
| Fichiers HTML générés | 281 |
| Types V2 standardisés | 8 |
| Subtypes définis | 35+ |
| Equity curves disponibles | 241 |

### Catégorisation V2
| Catégorie | Count |
|-----------|-------|
| BREAKOUT | 183 |
| MEAN_REVERSION | 39 |
| BIAS_TEMPORAL | 23 |
| TREND_FOLLOWING | 19 |
| PATTERN_PURE | 8 |
| HYBRID | 6 |
| GAP_TRADING | 2 |
| VOLATILITY | 1 |

---

## [2.0.0] - 2025-11-28

### Ajouté
- **Architecture V2** : Nouvelle structure modulaire dans `C:\TradeData\V2\`
- **Configuration centralisée** : `config/settings.py` avec tous les paramètres
- **Modules utilitaires** :
  - `src/utils/file_utils.py` : Lecture multi-encodage, extraction code PowerLanguage
  - `src/utils/matching.py` : Fuzzy matching Levenshtein pour correspondance stratégies
  - `src/utils/constants.py` : 152 patterns, types de stratégies, symboles, KPIs
- **Modules d'enrichissement** :
  - `src/enrichers/kpi_enricher.py` : Injection KPIs dans HTML
  - `src/enrichers/equity_enricher.py` : Graphiques Chart.js IS/OOS
  - `src/enrichers/styles.py` : CSS centralisé responsive
- **Analyseur IA** :
  - `src/analyzers/ai_analyzer.py` : Analyse via Claude API
  - `src/analyzers/html_generator.py` : Génération rapports HTML
  - `src/analyzers/config.py` : Configuration et mapping types
- **Consolidation** :
  - `src/consolidators/correlation_calculator.py` : Calcul Pearson + R² Davey
- **Générateurs** :
  - `src/generators/correlation_dashboard.py` : Dashboard corrélation interactif
- **Monte Carlo** :
  - `src/monte_carlo/simulator.py` : Simulation Monte Carlo
  - `src/monte_carlo/data_loader.py` : Chargement données
- **Scripts** :
  - `migrate_data.py` : Migration données
  - `migrate_v1_analysis.py` : Migration analyses IA V1→V2
  - `run_ai_analysis.py` : Lancement analyses IA
  - `run_enrich.py` : Enrichissement HTML batch
  - `run_pipeline.py` : Orchestration complète
- **Documentation** :
  - `docs/DOCUMENTATION_COMPLETE.md` : Documentation exhaustive
  - `docs/PROJECT_STATUS.md` : Point d'avancement
  - `docs/NEXT_SESSION_PROMPT.md` : Contexte pour continuation
- **Tests** :
  - Structure `tests/` avec validation
  - Scripts de test rapides

### Modifié
- Refactorisation de `enrich_html_with_kpis.py` (1200 lignes) en 3 modules distincts
- Architecture modulaire Python avec imports propres

### Intégré (depuis ancienne structure)
- Monte Carlo : ~250 rapports individuels fonctionnels
- Corrélation : Matrices LT/CT avec méthode Kevin Davey
- Dashboard AI : ~700 fiches stratégies enrichies

---

## [1.x] - Versions antérieures (non versionnées Git)

### Composants développés
- `ai_strategy_analyzer_v2.py` : Analyse IA avec Claude
- `dashboard_v4_enhanced.py` : Dashboard interactif
- `enrich_html_with_kpis.py` : Enrichissement HTML
- `monte_carlo.py` + `batch_monte_carlo.py` : Simulations MC
- `correlation_analysis_v2.py` : Matrices de corrélation
- `consolidate_strategies_v7.py` : Consolidation données
- `serve_reports.ps1` : Serveur Cloudflare

### Localisations historiques
- `C:\TradeData\mc_ai_analysis\` : Analyses IA
- `C:\TradeData\scripts\` : Scripts divers
- `C:\TradeData\Results\` : Outputs MC et Corrélation
