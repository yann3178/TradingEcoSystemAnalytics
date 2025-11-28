# Changelog - Trading EcoSystem Analytics

Toutes les modifications notables de ce projet sont documentées dans ce fichier.

**Repository:** https://github.com/yann3178/TradingEcoSystemAnalytics

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### À faire
- Porter Monte Carlo vers `src/monte_carlo/`
- Porter Corrélation vers `src/consolidators/`
- Porter Dashboard vers `src/generators/`
- Créer `run_pipeline.py` orchestrateur
- Tests de validation V1 vs V2

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
- **Scripts** :
  - `migrate_data.py` : Migration données avec Monte Carlo et Corrélation
  - `run_enrich.py` : Enrichissement HTML batch
- **Documentation** :
  - `docs/DOCUMENTATION_COMPLETE.md` : Documentation exhaustive
  - `docs/PROMPT_CONTINUATION.md` : Contexte pour continuation
- **Tests** :
  - Structure `tests/` avec validation V1 vs V2
  - Échantillons de données pour tests reproductibles
- **Git** :
  - `.gitignore` configuré pour exclure données sensibles
  - `CHANGELOG.md` pour suivi des versions

### Modifié
- Refactorisation de `enrich_html_with_kpis.py` (1200 lignes) en 3 modules distincts

### Intégré (depuis ancienne structure)
- Monte Carlo : ~250 rapports individuels fonctionnels
- Corrélation : Matrices LT/CT avec méthode Kevin Davey
- Dashboard AI : ~400 fiches stratégies enrichies

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
