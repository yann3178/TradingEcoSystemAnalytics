# 🗂️ SPEC COMPLÈTE: Migration Architecture Directories V2

**Version:** 1.0.0  
**Date:** 2025-11-30  
**Statut:** ✅ **SCRIPTS GÉNÉRÉS - PRÊT À UTILISER**

---

## 📊 **ANALYSE EXHAUSTIVE**

### **Fichiers config.py identifiés:**
1. ✅ `config/settings.py` - Configuration centrale (PRINCIPAL)
2. ❌ `src/analyzers/config.py` - Définit chemins AI Analysis (À CORRIGER)
3. ✅ `src/consolidators/config.py` - Pas de chemins (seulement paramètres métier)
4. ✅ `src/monte_carlo/config.py` - Pas de chemins (seulement paramètres métier)

### **Générateurs HTML identifiés:**
1. 🟢 `src/generators/correlation_pages.py` - VERSION ACTUELLE (26KB)
2. ✅ `src/generators/correlation_pages_generator.py` - **SUPPRIMÉ PAR L'UTILISATEUR**
3. 📊 `src/generators/correlation_dashboard.py` - Reçoit chemin via paramètre
4. 🎲 `src/monte_carlo/simulator.py` - Export CSV uniquement

---

## 🎯 **ARCHITECTURE CIBLE**

```
C:\TradeData\V2\outputs\
│
├── html_reports\                          ← TOUT LE HTML ICI
│   ├── index.html                         (index principal - à créer)
│   │
│   ├── ES_TrendFollower.html              (AI Analysis)
│   ├── NQ_BreakoutV2.html
│   └── ... (toutes les stratégies)
│   │
│   ├── correlation\
│   │   ├── dashboards\
│   │   │   └── correlation_dashboard_20251130.html
│   │   └── pages\
│   │       ├── ES_TrendFollower_correlation.html
│   │       └── ...
│   │
│   └── montecarlo\
│       ├── dashboards\
│       │   └── montecarlo_dashboard_20251130.html
│       └── individual\
│           ├── ES_TrendFollower_mc.html
│           └── ...
│
├── ai_analysis\                           ← CSV SEULEMENT
│   └── strategies_ai_analysis.csv
│
├── correlation\                           ← CSV SEULEMENT
│   └── correlation_matrix_*.csv
│
└── monte_carlo\                           ← CSV SEULEMENT
    └── *.csv
```

---

## 🚀 **GUIDE D'UTILISATION - 5 ÉTAPES**

### **ÉTAPE 1: Backup (Sécurité)** ⚠️

```bash
cd C:\TradeData\V2\outputs

# Créer backup complet
mkdir _BACKUP_MIGRATION_20251130

# Sauvegarder structure actuelle (si HTML existent)
xcopy ai_analysis _BACKUP_MIGRATION_20251130\ai_analysis /E /I /Y
xcopy correlation _BACKUP_MIGRATION_20251130\correlation /E /I /Y
xcopy correlation_pages_full _BACKUP_MIGRATION_20251130\correlation_pages_full /E /I /Y
xcopy monte_carlo _BACKUP_MIGRATION_20251130\monte_carlo /E /I /Y
```

---

### **ÉTAPE 2: Modification des fichiers Python** 🐍

```bash
cd C:\TradeData\V2\pipeline_modifications

# Dry-run (aperçu seulement)
python apply_directory_migration.py

# Vérifier l'aperçu, puis appliquer
python apply_directory_migration.py --apply
```

**Ce que fait ce script:**
- ✅ Modifie `config/settings.py` (ajoute nouveaux chemins)
- ✅ Modifie `src/analyzers/config.py` (utilise HTML_REPORTS_DIR)
- ✅ Modifie `src/generators/correlation_pages.py` (nouveaux imports)
- ✅ Modifie `run_pipeline.py` (imports mis à jour)
- ✅ Crée des backups timestampés dans `pipeline_modifications/backups/`

**Résultat attendu:**
```
✅ Fichiers traités: 4/4
📝 Modifications appliquées: 10-12
💾 Backups créés dans: pipeline_modifications/backups/
```

---

### **ÉTAPE 3: Migration physique des fichiers HTML** 📁

```bash
# Toujours dans pipeline_modifications/

# Dry-run (aperçu seulement)
python migrate_html_files.py

# Vérifier l'aperçu, puis appliquer
python migrate_html_files.py --apply
```

**Ce que fait ce script:**
- ✅ Déplace `ai_analysis/html_reports/*.html` → `html_reports/`
- ✅ Sépare correlation dashboards → `html_reports/correlation/dashboards/`
- ✅ Sépare correlation pages → `html_reports/correlation/pages/`
- ✅ Déplace Monte Carlo HTML → `html_reports/montecarlo/individual/`
- ✅ Nettoie répertoires vides (sauf backups)

**Résultat attendu:**
```
✅ Total fichiers déplacés: 50-250 (selon votre système)
🗑️  Répertoires nettoyés: 1-2
📁 Structure créée: html_reports/ avec sous-dossiers
```

---

### **ÉTAPE 4: Validation complète** ✅

```bash
# Toujours dans pipeline_modifications/

python validate_directory_migration.py
```

**Ce que fait ce script (7 tests):**
1. ✅ Structure répertoires (7 dossiers créés)
2. ✅ Fichiers HTML présents dans html_reports/
3. ✅ Pas de HTML orphelins dans anciens emplacements
4. ✅ config/settings.py contient nouveaux chemins
5. ✅ Compatibilité legacy (AI_HTML_REPORTS_DIR redirige)
6. ✅ src/analyzers/config.py utilise HTML_REPORTS_DIR
7. ✅ CSV restés dans bons emplacements

**Résultat attendu:**
```
✅ Tests réussis: 7/7 (100%)
🎉 Tous les tests sont réussis!
✅ Migration complète et validée
```

**Si échec:**
- Le script indique exactement quoi corriger
- Exit code 1 (pour intégration CI/CD)

---

### **ÉTAPE 5: Test du pipeline** 🧪

```bash
cd C:\TradeData\V2

# Test enrichissement (dry-run)
python run_pipeline.py --step enrich --dry-run

# Test génération correlation (dry-run)
python run_pipeline.py --step correlation --dry-run

# Si OK, générer réellement
python run_pipeline.py --step enrich
python run_pipeline.py --step correlation
```

**Vérifications manuelles:**
1. Ouvrir `outputs/html_reports/ES_TrendFollower.html` (stratégie)
2. Ouvrir `outputs/html_reports/correlation/pages/ES_TrendFollower_correlation.html`
3. Vérifier que tous les liens fonctionnent
4. Aucun lien cassé vers anciens chemins

---

## 📋 **CHECKLIST COMPLÈTE**

### **Avant migration:**
- [ ] Backup créé (`_BACKUP_MIGRATION_20251130/`)
- [ ] Scripts téléchargés dans `pipeline_modifications/`

### **Modification Python:**
- [ ] `python apply_directory_migration.py` (dry-run vérifié)
- [ ] `python apply_directory_migration.py --apply` (exécuté)
- [ ] 4 fichiers modifiés, backups créés

### **Migration HTML:**
- [ ] `python migrate_html_files.py` (dry-run vérifié)
- [ ] `python migrate_html_files.py --apply` (exécuté)
- [ ] Fichiers déplacés dans `html_reports/`

### **Validation:**
- [ ] `python validate_directory_migration.py` (7/7 tests réussis)

### **Tests pipeline:**
- [ ] `run_pipeline.py --step enrich --dry-run` (OK)
- [ ] `run_pipeline.py --step correlation --dry-run` (OK)
- [ ] Génération réelle testée

### **Vérification manuelle:**
- [ ] HTML s'ouvrent correctement
- [ ] Aucun lien cassé
- [ ] Structure complète en place

---

## ⚠️ **EN CAS DE PROBLÈME**

### **Restauration depuis backup:**

```bash
cd C:\TradeData\V2

# Restaurer fichiers Python (si apply_directory_migration a échoué)
copy pipeline_modifications\backups\settings_backup_YYYYMMDD_HHMMSS.py config\settings.py
copy pipeline_modifications\backups\config_backup_YYYYMMDD_HHMMSS.py src\analyzers\config.py
# etc.

# Restaurer HTML (si migrate_html_files a échoué)
cd outputs
xcopy _BACKUP_MIGRATION_20251130\* . /E /I /Y
```

### **Problèmes courants:**

| Problème | Solution |
|----------|----------|
| Import HTML_CORRELATION_DIR non trouvé | Vérifier config/settings.py modifié |
| HTML non déplacés | Re-exécuter migrate_html_files.py --apply |
| Test 3 échoue (HTML orphelins) | Déplacer manuellement les HTML restants |
| Pipeline génère dans ancien emplacement | Vérifier imports dans run_pipeline.py |

---

## 📊 **DÉTAILS TECHNIQUES**

### **Fichiers modifiés (apply_directory_migration.py):**

| Fichier | Modifications |
|---------|---------------|
| `config/settings.py` | 3 modifications (nouveaux chemins, legacy redirect, ensure_directories) |
| `src/analyzers/config.py` | 4 modifications (imports + 4 chemins) |
| `src/generators/correlation_pages.py` | 2 modifications (import + config) |
| `run_pipeline.py` | 1 modification (imports) |

### **Fichiers déplacés (migrate_html_files.py):**

| Source | Destination |
|--------|-------------|
| `ai_analysis/html_reports/*.html` | `html_reports/` |
| `correlation/*dashboard*.html` | `html_reports/correlation/dashboards/` |
| `correlation/*.html` | `html_reports/correlation/pages/` |
| `correlation_pages_full/*.html` | `html_reports/correlation/pages/` |
| `monte_carlo/*dashboard*.html` | `html_reports/montecarlo/dashboards/` |
| `monte_carlo/*.html` | `html_reports/montecarlo/individual/` |

---

## 🎯 **COMPATIBILITÉ**

### **Backward:**
- ✅ `AI_HTML_REPORTS_DIR` redirige vers `HTML_REPORTS_DIR`
- ✅ Scripts existants continuent de fonctionner

### **Forward:**
- ✅ Nouveaux scripts utilisent architecture unifiée
- ✅ Chemins explicites (correlation/, montecarlo/)

### **Impact minimal:**
- ✅ CSV restent dans leurs emplacements
- ✅ Aucun changement dans données brutes

---

## 📁 **FICHIERS GÉNÉRÉS**

```
C:\TradeData\V2\pipeline_modifications\
├── SPEC_MIGRATION_DIRECTORIES.md          (cette spec)
├── apply_directory_migration.py           (modifie Python)
├── migrate_html_files.py                  (déplace HTML)
├── validate_directory_migration.py        (7 tests validation)
└── backups\
    ├── settings_backup_YYYYMMDD_HHMMSS.py
    ├── config_backup_YYYYMMDD_HHMMSS.py
    └── ...
```

---

## ⏱️ **TEMPS ESTIMÉ**

| Étape | Durée | Risque |
|-------|-------|--------|
| 1. Backup | 2 min | Nul |
| 2. Modification Python | 5 min | Faible (backups auto) |
| 3. Migration HTML | 5 min | Faible (dry-run first) |
| 4. Validation | 1 min | Nul |
| 5. Tests pipeline | 5 min | Faible |
| **TOTAL** | **~20 min** | **Faible** |

---

## ✅ **PRÊT À COMMENCER ?**

```bash
# Étape 1: Backup
cd C:\TradeData\V2\outputs
mkdir _BACKUP_MIGRATION_20251130
xcopy ai_analysis _BACKUP_MIGRATION_20251130\ai_analysis /E /I /Y
xcopy correlation _BACKUP_MIGRATION_20251130\correlation /E /I /Y

# Étape 2: Migration Python
cd ..\pipeline_modifications
python apply_directory_migration.py             # Dry-run
python apply_directory_migration.py --apply     # Appliquer

# Étape 3: Migration HTML
python migrate_html_files.py                     # Dry-run
python migrate_html_files.py --apply             # Appliquer

# Étape 4: Validation
python validate_directory_migration.py           # 7 tests

# Étape 5: Tests pipeline
cd ..
python run_pipeline.py --step enrich --dry-run

# 🎉 C'est parti !
```

---

**Auteur:** Assistant Claude  
**Support:** Spec complète + 3 scripts automatiques  
**Statut:** ✅ Prêt à l'emploi
