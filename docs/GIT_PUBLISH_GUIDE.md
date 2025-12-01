# 🚀 GIT PUBLISH V2.2.0 - COMMANDES MANUELLES

## Date: 28 novembre 2025

---

## 📋 MÉTHODE 1 : SCRIPT AUTOMATIQUE (RECOMMANDÉ)

```powershell
cd C:\TradeData\V2
.\git_publish_v2.2.0.ps1
```

**Le script fait tout automatiquement :**
- ✅ Vérifie le statut Git
- ✅ Ajoute tous les fichiers modifiés/créés
- ✅ Crée le commit avec message détaillé
- ✅ Crée le tag v2.2.0
- ✅ Pousse vers GitHub (avec confirmation)

---

## 📋 MÉTHODE 2 : COMMANDES MANUELLES

Si tu préfères exécuter les commandes à la main :

### 1. Vérifier le Statut

```bash
cd C:\TradeData\V2
git status
```

**Fichiers attendus :**
```
modified:   run_pipeline.py
modified:   VERSION
new file:   docs/AI_ANALYSIS_INTEGRATION.md
new file:   docs/CHANGELOG.md
new file:   docs/DEPLOYMENT_V2.2.0.md
new file:   patch_pipeline_add_ai.py (optionnel)
new file:   apply_patch.ps1 (optionnel)
```

---

### 2. Ajouter les Fichiers

```bash
# Fichiers principaux
git add run_pipeline.py
git add VERSION

# Documentation
git add docs/AI_ANALYSIS_INTEGRATION.md
git add docs/CHANGELOG.md
git add docs/DEPLOYMENT_V2.2.0.md

# Optionnel: Scripts de patch (utiles pour référence)
git add patch_pipeline_add_ai.py
git add apply_patch.ps1
```

---

### 3. Créer le Commit

```bash
git commit -m "feat: Integrate AI Analysis into pipeline v2.2.0

ADDED:
- Step 0: AI Analysis (optional, disabled by default)
- CLI: --run-ai-analysis, --ai-mode, --ai-max, --ai-retry-errors
- CLI: --ai-from-file, --ai-no-dashboard
- CLI: --step ai-analysis
- Confirmation prompt for full analysis (cost/time warning)

MODIFIED:
- PipelineConfig: Added AI Analysis parameters
- run_pipeline(): Added step_0_ai_analysis()
- Execution order: 0 (AI) → 0A (Mapping) → 1 (Enrich) → 1B (Harmonize) → 2 (MC) → 3 (Corr)

DOCUMENTED:
- docs/AI_ANALYSIS_INTEGRATION.md: Complete AI Analysis guide
- docs/CHANGELOG.md: Version 2.2.0 entry + history
- docs/DEPLOYMENT_V2.2.0.md: Deployment summary
- VERSION: 2.1.1 → 2.2.0

COSTS:
- Time: ~2-3 min/strategy (rate limiting)
- API: ~\$0.003/strategy
- 800 strategies: ~40 hours + \$2.40

Version: 2.1.1 → 2.2.0"
```

---

### 4. Créer le Tag

```bash
git tag -a v2.2.0 -m "Version 2.2.0 - AI Analysis Integration

Major update integrating AI-powered strategy classification directly into the pipeline.

Key Features:
• AI Analysis as optional Step 0
• 8 strategy categories with quality scoring
• Full CLI integration (7 new parameters)
• Delta (incremental) and full analysis modes
• Cost protection (disabled by default, confirmation required)
• Complete documentation

Performance:
• ~2-3 min per strategy
• ~\$0.003 per strategy
• 800 strategies: ~40 hours, ~\$2.40

100% backwards compatible with v2.1.1"
```

---

### 5. Vérifier Avant Push

```bash
# Voir le dernier commit
git log -1

# Voir les tags
git tag -l -n9 v2.2.0

# Voir ce qui sera poussé
git log origin/main..main --oneline
```

---

### 6. Pousser vers GitHub

```bash
# Pousser le commit
git push origin main

# Pousser le tag
git push origin v2.2.0
```

---

## 📊 VÉRIFICATION POST-PUSH

### Sur GitHub

1. **Commits** : https://github.com/yann3178/TradingEcoSystemAnalytics/commits/main
   - Vérifier que le commit "feat: Integrate AI Analysis" apparaît

2. **Releases** : https://github.com/yann3178/TradingEcoSystemAnalytics/releases
   - Vérifier que v2.2.0 apparaît dans les releases

3. **Tag** : https://github.com/yann3178/TradingEcoSystemAnalytics/releases/tag/v2.2.0
   - Vérifier le message du tag

---

## 📝 CHECKLIST PRE-PUSH

Vérifier avant de pousser :

- [ ] **Tests passent** : `python run_pipeline.py --dry-run`
- [ ] **VERSION correcte** : `type VERSION` → 2.2.0
- [ ] **CHANGELOG à jour** : `docs/CHANGELOG.md` contient v2.2.0
- [ ] **Backup existe** : `run_pipeline.py.v2.1.1.bak`
- [ ] **Git status clean** : Tous fichiers staged
- [ ] **Commit message complet** : Toutes sections présentes
- [ ] **Tag créé** : `git tag` liste v2.2.0

---

## ✅ RÉSUMÉ COMMANDES RAPIDES

```bash
# Tout en une fois
cd C:\TradeData\V2
git add run_pipeline.py VERSION docs/*.md patch_pipeline_add_ai.py apply_patch.ps1
git commit -m "feat: Integrate AI Analysis into pipeline v2.2.0"
git tag -a v2.2.0 -m "Version 2.2.0 - AI Analysis Integration"
git push origin main
git push origin v2.2.0
```

---

**Script Automatique Disponible** : `git_publish_v2.2.0.ps1`  
**Documentation Complète** : `docs/DEPLOYMENT_V2.2.0.md`
