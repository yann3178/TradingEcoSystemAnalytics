# GUIDE DE NETTOYAGE MANUEL - Dashboard Monte Carlo V2.1

Date: 2025-12-01
Statut: ✅ Dashboard V2.1 validé et fonctionnel

---

## 🎯 Objectif

Nettoyer les fichiers temporaires et établir une baseline propre après la migration vers le dashboard interactif V2.1.

---

## ✅ PLAN DE NETTOYAGE (Recommandé)

### Étape 1: Analyser l'État Actuel

```bash
cd C:\TradeData\V2
python PLAN_NETTOYAGE.py
```

Ce script analyse tous les fichiers et génère un rapport détaillé.

---

### Étape 2A: Nettoyage AUTOMATIQUE (Recommandé)

```bash
cd C:\TradeData\V2
NETTOYAGE_AUTO.bat
```

Le script automatique va :
1. ✅ Migrer le générateur vers V2.1
2. ✅ Créer les backups de sécurité
3. ✅ Archiver les versions intermédiaires
4. ✅ Archiver les scripts de migration
5. ✅ Tester la génération (optionnel)

**Durée**: 30 secondes

---

### Étape 2B: Nettoyage MANUEL (Alternative)

Si vous préférez le contrôle total, voici les commandes exactes :

#### 1. Migration du générateur principal

```bash
cd C:\TradeData\V2\src\monte_carlo

# Backup de l'ancien générateur
copy monte_carlo_html_generator.py monte_carlo_html_generator_v2.0_BACKUP.py

# Remplacer par V2.1
copy monte_carlo_html_generator_v2.1.py monte_carlo_html_generator.py
```

#### 2. Archivage des versions intermédiaires

```bash
cd C:\TradeData\V2\src\monte_carlo

# Créer le dossier d'archives
mkdir archive

# Archiver les versions intermédiaires
move monte_carlo_html_generator_v2.py archive\
move monte_carlo_html_generator_v3.py archive\
move monte_carlo_html_generator_v2.1.py archive\
move html_templates_NEW.py archive\
move html_templates_FINAL.py archive\
move v1_batch_monte_carlo.py archive\
move v1_batch_visualizer.py archive\
```

#### 3. Archivage des scripts de migration (racine)

```bash
cd C:\TradeData\V2

# Créer le dossier de migration
mkdir migration_v2.1

# Archiver les scripts de migration
move finalize_templates.py migration_v2.1\
move test_config_import.py migration_v2.1\
move create_backups.py migration_v2.1\
move GUIDE_VALIDATION.py migration_v2.1\
move PLAN_NETTOYAGE.py migration_v2.1\
```

#### 4. Vérification des backups

```bash
cd C:\TradeData\V2\src\monte_carlo

# Vérifier la présence des backups
dir *.backup
dir *_BACKUP.py
```

**Vous devez voir** :
- ✅ config.py.backup
- ✅ html_templates.py.backup
- ✅ monte_carlo_html_generator_v2.0_BACKUP.py

---

### Étape 3: Test de Génération

```bash
cd C:\TradeData\V2\src\monte_carlo
python monte_carlo_html_generator.py
```

**Résultat attendu** :
- ✅ 245 pages individuelles générées
- ✅ Page de synthèse avec dashboard interactif
- ✅ Aucune erreur

---

### Étape 4: Vérification du Dashboard

Ouvrir dans le navigateur :
```
C:\TradeData\V2\outputs\html_reports\montecarlo\all_strategies_montecarlo.html
```

**Vérifier** :
- ✅ Dashboard s'affiche correctement
- ✅ Sliders fonctionnent
- ✅ Recalcul dynamique fonctionne
- ✅ Graphiques s'affichent
- ✅ Tableau interactif fonctionne

---

## 📊 STRUCTURE FINALE (Après Nettoyage)

```
C:\TradeData\V2\
│
├── src/monte_carlo/
│   ├── config.py                              [PROD - V2.1]
│   ├── config.py.backup                       [BACKUP]
│   ├── data_loader.py                         [PROD]
│   ├── simulator.py                           [PROD]
│   ├── monte_carlo_html_generator.py          [PROD - V2.1] ⭐
│   ├── monte_carlo_html_generator_v2.0_BACKUP.py [BACKUP]
│   ├── html_templates.py                      [PROD - V2.1] ⭐
│   ├── html_templates.py.backup               [BACKUP]
│   ├── __init__.py                            [PROD]
│   ├── README_*.md                            [DOC]
│   │
│   └── archive/                               [ARCHIVE]
│       ├── monte_carlo_html_generator_v2.py
│       ├── monte_carlo_html_generator_v3.py
│       ├── monte_carlo_html_generator_v2.1.py
│       ├── html_templates_NEW.py
│       ├── html_templates_FINAL.py
│       ├── v1_batch_monte_carlo.py
│       └── v1_batch_visualizer.py
│
├── MODIFICATIONS_DASHBOARD_MC.md              [DOC]
├── CHANGELOG.md                               [DOC]
├── README.md                                  [DOC]
├── run_pipeline.py                            [PROD]
│
└── migration_v2.1/                            [ARCHIVE]
    ├── finalize_templates.py
    ├── test_config_import.py
    ├── create_backups.py
    ├── GUIDE_VALIDATION.py
    ├── PLAN_NETTOYAGE.py
    └── NETTOYAGE_AUTO.bat
```

**Légende** :
- ⭐ = Fichiers modifiés dans cette version
- [PROD] = Fichiers de production actifs
- [BACKUP] = Backups de sécurité (NE PAS SUPPRIMER)
- [ARCHIVE] = Versions archivées (peuvent être supprimées après validation)
- [DOC] = Documentation

---

## 🗑️ FICHIERS POUVANT ÊTRE SUPPRIMÉS (Optionnel)

**Après validation complète (1-2 semaines d'utilisation)**, vous pouvez supprimer :

### Dans `src/monte_carlo/archive/`
- Toutes les anciennes versions du générateur
- Tous les templates intermédiaires

### Dans `migration_v2.1/`
- Tous les scripts de migration

**Commande de suppression** :
```bash
cd C:\TradeData\V2

# Supprimer les archives (ATTENTION: irréversible)
rmdir /s /q src\monte_carlo\archive
rmdir /s /q migration_v2.1
```

⚠️ **ATTENTION** : Ne supprimez JAMAIS les fichiers `.backup` !

---

## 🔄 ROLLBACK (En Cas de Problème)

Si le dashboard V2.1 pose problème, vous pouvez revenir en arrière :

```bash
cd C:\TradeData\V2\src\monte_carlo

# Restaurer l'ancien générateur
copy monte_carlo_html_generator_v2.0_BACKUP.py monte_carlo_html_generator.py

# Restaurer l'ancien template
copy html_templates.py.backup html_templates.py

# Restaurer l'ancienne config
copy config.py.backup config.py

# Tester
python monte_carlo_html_generator.py
```

---

## 📈 STATISTIQUES

### Gain d'Espace Disque (Estimé)

**Avant nettoyage** :
- src/monte_carlo/ : ~400 KB (7 versions du générateur)
- Racine V2/ : ~50 KB (scripts de migration)
- **Total** : ~450 KB

**Après archivage** :
- Fichiers actifs : ~150 KB
- Archives : ~300 KB (peuvent être supprimées)
- **Gain potentiel** : ~300 KB après suppression des archives

### Clarté

**Avant** :
- 15+ fichiers dans monte_carlo/
- Confusion entre versions
- Scripts temporaires mélangés

**Après** :
- 8 fichiers de production
- 3 backups
- Archives séparées
- ✅ Structure claire et maintenable

---

## ✅ CHECKLIST FINALE

Après le nettoyage, vérifiez :

- [ ] Le générateur principal est bien la version V2.1
- [ ] Les 3 backups sont présents (.backup)
- [ ] Les versions intermédiaires sont archivées
- [ ] La génération fonctionne sans erreur
- [ ] Le dashboard s'affiche correctement
- [ ] Les pages individuelles sont inchangées
- [ ] La documentation est à jour

---

## 🎯 PROCHAINES ÉTAPES

Une fois le nettoyage terminé :

1. **Commiter dans Git** :
```bash
cd C:\TradeData\V2
git add .
git commit -m "feat: Dashboard Monte Carlo V2.1 - Recalcul dynamique des capitaux"
git push
```

2. **Mettre à jour CHANGELOG.md** avec les nouvelles fonctionnalités

3. **Utiliser le dashboard** pendant 1-2 semaines pour valider la stabilité

4. **Supprimer les archives** si tout fonctionne parfaitement

---

## 📞 SUPPORT

En cas de problème :
- Consulter `MODIFICATIONS_DASHBOARD_MC.md` pour les détails techniques
- Utiliser les backups pour rollback
- Vérifier la console F12 du navigateur pour les erreurs JS

---

**Date de création** : 2025-12-01
**Version** : V2.1 - Dashboard Interactif
**Statut** : ✅ Validé et Stable
