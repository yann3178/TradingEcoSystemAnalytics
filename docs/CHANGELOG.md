# CHANGELOG

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

---

## [2.2.0] - 2025-11-28 ⭐ MAJOR UPDATE

### ⭐ Ajouté - AI ANALYSIS INTÉGRATION

**AI Analysis est maintenant intégré dans le pipeline principal !**

#### Nouvelle Étape 0 : AI Analysis (Optionnelle)

- **Fonction** : `step_0_ai_analysis()` dans `run_pipeline.py`
- **Caractéristiques** :
  - Classification automatique via Claude API
  - 8 catégories de stratégies (BREAKOUT, MEAN_REVERSION, etc.)
  - Scores qualité et complexité
  - Génération dashboard HTML
  - Mode delta (incrémental) et full (complet)
  - Gestion tracking avec code hash
  - Retry automatique des erreurs

#### 7 Nouveaux Paramètres CLI

| Paramètre | Description | Défaut |
|-----------|-------------|--------|
| `--run-ai-analysis` | Activer AI dans pipeline complet | Désactivé |
| `--step ai-analysis` | AI Analysis seule | - |
| `--ai-mode {delta\|full}` | Mode incrémental ou complet | `delta` |
| `--ai-max N` | Limiter à N stratégies | `0` (toutes) |
| `--ai-retry-errors` | Retry stratégies en erreur | Désactivé |
| `--ai-from-file FILE` | Charger liste depuis fichier | `None` |
| `--ai-no-dashboard` | Ne pas générer dashboard | Génère |

#### Configuration Étendue

```python
class PipelineConfig:
    # AI Analysis (NOUVEAU)
    run_ai_analysis = False          # Désactivé par défaut
    ai_mode = "delta"                # "delta" ou "full"
    ai_max_strategies = 0            # 0 = toutes
    ai_retry_errors = False
    ai_from_file = None
    ai_generate_dashboard = True
```

#### Sécurités Intégrées

- **Confirmation requise** pour analyse complète
- **Dry-run** pour prévisualisation
- **Estimation coûts/temps** affichée
- **Gestion interruption** (Ctrl+C)
- **Import dynamique** de run_ai_analysis.py

### 🔄 Modifié

#### Architecture Pipeline

```
AVANT (V2.1.1):
0A. Mapping → 1. Enrich → 1B. Harmonize → 2. MC → 3. Corr

APRÈS (V2.2.0):
0.  AI Analysis (optionnel) ← NOUVEAU
0A. Mapping → 1. Enrich → 1B. Harmonize → 2. MC → 3. Corr
```

### 📊 Statistiques

- **Lignes ajoutées** : +150 (code)
- **Nouvelles fonctions** : 1 (`step_0_ai_analysis`)
- **Nouveaux paramètres CLI** : 7
- **Durée AI** : ~2-3 min/stratégie
- **Coût API** : ~$0.003/stratégie

### 📝 Documentation

- ✅ `docs/AI_ANALYSIS_INTEGRATION.md` - Guide complet
- ✅ `docs/CHANGELOG.md` - Cette section
- ✅ `VERSION` - 2.2.0

### ⚠️ Notes

**AI Analysis DÉSACTIVÉ par défaut** :
- Coût : ~$2.40 pour 800 stratégies
- Temps : ~40+ heures pour analyse complète
- Activation explicite requise

---

## [2.1.1] - 2025-11-28

### 🐛 Corrigé

- **Import Error** : Suppression import inutilisé `enrich_html_with_equity_curve`
- **Missing Function** : Ajout `get_kpi_styles()` dans `styles.py`

### ✅ Testé

- Pipeline complet en `--dry-run` : ✅

---

## [2.1.0] - 2025-11-28

### ⭐ Ajouté

**Preprocessing Intégré dans Pipeline**

- **Étape 0A** : Strategy Mapping automatique
- **Étape 1B** : Name Harmonization automatique
- **CLI** : Option `--skip-preprocessing`

**Harmonisation des Noms**
- Convention : `{Symbol}_{StrategyName}.html`
- 235/243 stratégies harmonisées (96.7%)
- Backup automatique complet
- Rollback instantané

### 📊 Résultats

- Mapping : 243 stratégies → symboles
- Harmonisation : 235 fichiers renommés
- Durée preprocessing : ~7 secondes

---

**Format** : [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/)  
**Versioning** : [Semantic Versioning](https://semver.org/lang/fr/)
