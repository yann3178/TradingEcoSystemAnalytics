# 📊 Trading Analytics V2 - Strategy Name Harmonization System

## Vue d'ensemble

Ce système harmonise les conventions de nommage des stratégies de trading à travers tous les dashboards (AI Analysis, Monte Carlo, Correlation) en ajoutant systématiquement le symbole de l'instrument comme préfixe.

**Transformation:**
```
AVANT:  SOM_UA_2301_G_1.html
APRÈS:  NQ_SOM_UA_2301_G_1.html

AVANT:  ATS_Strategy_v0.8.html  
APRÈS:  FDAX_ATS_Strategy_v0.8.html
```

---

## 🎯 Objectifs

1. **Unifier** les conventions de nommage entre tous les dashboards
2. **Faciliter** la navigation inter-dashboards avec des clés uniques
3. **Éliminer** l'ambiguïté pour les stratégies multi-symboles
4. **Améliorer** la traçabilité et la maintenance

---

## 📦 Composants du système

### 1. Module de Mapping (`src/utils/strategy_mapper.py`)

**Rôle:** Centralise le mapping entre noms de stratégies et symboles

**API:**
```python
from src.utils.strategy_mapper import StrategyMapper

# Initialiser avec Portfolio Report
mapper = StrategyMapper("path/to/Portfolio_Report_V2.csv")

# Obtenir les symboles pour une stratégie
symbols = mapper.get_symbols_for_strategy("ATS_Strategy_v0.8")
# → ['FDAX']

# Obtenir les clés complètes (Symbol_StrategyName)
full_keys = mapper.get_full_keys_for_strategy("ATS_Strategy_v0.8")
# → ['FDAX_ATS_Strategy_v0.8']

# Recherche fuzzy
matches = mapper.find_strategy_fuzzy("ATS", min_similarity=0.8)

# Statistiques
stats = mapper.get_statistics()
mapper.print_statistics()

# Export JSON
mapper.export_to_json("outputs/strategy_mapping.json")
```

### 2. Script de Migration (`migrate_ai_html_names.py`)

**Rôle:** Renomme les fichiers HTML existants avec le préfixe symbole

**Usage:**
```bash
# Prévisualisation (recommandé en premier)
python migrate_ai_html_names.py --dry-run

# Migration effective avec backup automatique
python migrate_ai_html_names.py

# Sans backup (non recommandé)
python migrate_ai_html_names.py --no-backup
```

**Fonctionnalités:**
- ✅ Backup automatique avant modification
- ✅ Mode dry-run pour prévisualisation
- ✅ Filtrage intelligent (ignore correlation, backups, index)
- ✅ Rapport détaillé JSON
- ✅ Gestion des erreurs et warnings

### 3. Script de Rollback (`rollback_migration.py`)

**Rôle:** Restaure les fichiers depuis un backup

**Usage:**
```bash
# Lister les backups disponibles
python rollback_migration.py --list

# Prévisualiser la restauration
python rollback_migration.py --backup 20251128_140000 --dry-run

# Restaurer effectivement
python rollback_migration.py --backup 20251128_140000
```

### 4. Script de Vérification (`verify_migration.py`)

**Rôle:** Valide que la migration s'est bien déroulée

**Usage:**
```bash
python verify_migration.py
```

**Vérifications:**
- ✅ Existence du rapport de migration
- ✅ Nombre de fichiers (avant/après)
- ✅ Patterns de nommage conformes
- ✅ Existence du backup
- ✅ Distribution des symboles

---

## 📋 Workflow de migration complet

### Étape 1: Préparation

```bash
cd C:\TradeData\V2

# Tester le mapper
python src\utils\strategy_mapper.py
```

**Résultat attendu:**
```
✓ Loaded 243 strategies with symbol mappings
✓ Total strategy-symbol combinations: 243
```

### Étape 2: Prévisualisation

```bash
python migrate_ai_html_names.py --dry-run
```

**Vérifier:**
- ✅ Nombre de fichiers à migrer
- ✅ Transformations prévues
- ✅ Warnings éventuels

### Étape 3: Migration

```bash
python migrate_ai_html_names.py
```

**Confirmer:** Taper `y` quand demandé

**Attendu:**
- ✅ Backup créé dans `backups/<timestamp>/`
- ✅ Tous les fichiers renommés
- ✅ Rapport généré dans `outputs/consolidated/migration_report.json`

### Étape 4: Vérification

```bash
python verify_migration.py
```

**Résultat attendu:**
```
✅ MIGRATION SUCCESSFUL - All checks passed!
```

### Étape 5 (si problème): Rollback

```bash
# Lister les backups
python rollback_migration.py --list

# Restaurer
python rollback_migration.py --backup <timestamp>
```

---

## 📁 Structure des fichiers

```
C:\TradeData\V2\
│
├── src\
│   ├── utils\
│   │   └── strategy_mapper.py          # Module de mapping
│   ├── analyzers\
│   │   └── html_generator.py           # Générateur HTML (à adapter)
│   ├── enrichers\
│   │   ├── kpi_enricher.py             # Enrichisseur KPI (à adapter)
│   │   └── equity_enricher.py          # Enrichisseur equity (à adapter)
│   └── generators\
│       └── site_integrator.py          # Intégration inter-dashboards (à créer)
│
├── outputs\
│   ├── html_reports\                   # Fichiers HTML (destination migration)
│   └── consolidated\
│       ├── strategy_mapping.json       # Cache du mapping
│       └── migration_report.json       # Rapport de migration
│
├── backups\                             # Backups automatiques
│   └── <timestamp>\
│       ├── html_reports\
│       └── manifest.json
│
├── data\
│   └── portfolio_reports\
│       └── Portfolio_Report_V2_*.csv   # Source de vérité
│
├── migrate_ai_html_names.py            # Script de migration
├── rollback_migration.py               # Script de rollback
└── verify_migration.py                 # Script de vérification
```

---

## 🔍 Détails techniques

### Convention de nommage unifiée

**Format standard:** `{Symbol}_{StrategyName}.html`

**Exemples:**
- `NQ_SOM_UA_2301_G_1.html`
- `FDAX_ATS_Strategy_v0.8.html`
- `GC_TOP_UA_145_GC_5.html`
- `ES_MyStudies_Bollinger_Reversal_GL.html`

### Clé unique de stratégie

```python
strategy_key = f"{Symbol}_{StrategyName}"
```

Cette clé permet:
- ✅ Identification unique cross-dashboard
- ✅ Matching exact (pas de fuzzy)
- ✅ Navigation bidirectionnelle
- ✅ Traçabilité complète

### Source de vérité

Le **Portfolio Report** (`Portfolio_Report_V2_*.csv`) contient:
- `Strategie`: Nom de la stratégie
- `Symbol`: Instrument (ex: FDAX, NQ, GC)

**Relation:** 1 stratégie = 1 symbole (ratio 1:1 confirmé sur 243 stratégies)

---

## 📊 Statistiques système

**Données actuelles:**
- 243 stratégies uniques
- 243 combinaisons stratégie-symbole
- 0 stratégies multi-symboles
- 100% de ratio 1:1

**Distribution des symboles (top 5):**
- FDAX: ~45 stratégies
- NQ: ~40 stratégies
- GC: ~35 stratégies
- ES: ~30 stratégies
- CL: ~25 stratégies

---

## ⚠️ Points d'attention

### Fichiers exclus de la migration

- `*_correlation.html` - Déjà enrichis avec symbole
- `*.bak` - Backups
- `index*.html` - Pages d'index
- `mobile-enhancement.html` - Utilitaire

### Warnings possibles

1. **"No symbol found for: XYZ"**
   - Stratégie absente du Portfolio Report
   - Fichier conservé avec nom original
   - À vérifier manuellement

2. **"Multiple symbols found for XYZ"**
   - Stratégie sur plusieurs instruments
   - Premier symbole utilisé par défaut
   - **Très rare** (aucun cas détecté actuellement)

### Sécurité

✅ **Backup automatique** avant toute modification  
✅ **Mode dry-run** pour prévisualisation  
✅ **Script de rollback** pour restauration  
✅ **Vérification post-migration** automatisée  
✅ **Rapport détaillé** de toutes les opérations

---

## 🚀 Prochaines étapes (Phase 3 & 4)

### Phase 3: Adaptation des générateurs

**Fichiers à modifier:**

1. `src/analyzers/html_generator.py`
   - Générer avec `{symbol}_{strategy_name}.html`
   - Ajouter symbole dans le titre H1

2. `src/enrichers/kpi_enricher.py`
   - Utiliser `strategy_key` pour le matching
   - Remplacer fuzzy matching par exact matching

3. `src/enrichers/equity_enricher.py`
   - Utiliser `strategy_key` pour le matching

### Phase 4: Intégration inter-dashboards

**Créer:** `src/generators/site_integrator.py`

**Fonctionnalités:**
- Navigation unifiée entre dashboards
- Liens bidirectionnels (AI ↔ MC ↔ Correlation)
- Validation des liens
- Indicateurs de disponibilité

**Créer:** `outputs/html_reports/dashboard.html`

**Contenu:**
- Vue portfolio complète
- Filtres (symbole, type, status MC)
- KPIs agrégés
- Liens vers tous les dashboards

---

## 📚 Documentation

**Guides disponibles:**
- `IMPLEMENTATION_REPORT.md` - Rapport d'implémentation détaillé
- `MIGRATION_QUICK_GUIDE.md` - Guide rapide de migration

**Rapports générés:**
- `outputs/consolidated/strategy_mapping.json` - Mapping complet
- `outputs/consolidated/migration_report.json` - Détails de migration

---

## 💡 Commandes utiles

```bash
# Test complet du système
python src\utils\strategy_mapper.py

# Migration complète
python migrate_ai_html_names.py --dry-run
python migrate_ai_html_names.py
python verify_migration.py

# Recherche de fichiers
dir outputs\html_reports\*ATS*.html

# Statistiques
dir outputs\html_reports\*.html | measure

# Vérifier les backups
dir backups
```

---

## 📞 Support et troubleshooting

### Problème: Migration échoue

**Solution:**
1. Vérifier que Portfolio Report existe et est à jour
2. Vérifier les permissions sur `outputs/html_reports/`
3. Consulter le rapport de migration pour les détails

### Problème: Fichiers manquants après migration

**Solution:**
1. Utiliser `rollback_migration.py` immédiatement
2. Vérifier le backup dans `backups/<timestamp>/`
3. Relancer avec `--dry-run` pour diagnostiquer

### Problème: Warnings nombreux

**Solution:**
1. Consulter `migration_report.json` pour les détails
2. Vérifier que les stratégies sont dans Portfolio Report
3. Mettre à jour Portfolio Report si nécessaire

---

## ✅ Validation finale

**Checklist avant déploiement:**

- [ ] Mapping généré (`strategy_mapping.json`)
- [ ] Migration testée en dry-run
- [ ] Migration exécutée avec succès
- [ ] Backup créé et validé
- [ ] Vérification post-migration OK
- [ ] Tous les fichiers renommés
- [ ] Aucune perte de données
- [ ] Rapport de migration sans erreurs

---

## 📝 Changelog

**2025-11-28 - Version initiale**
- ✅ Module de mapping créé
- ✅ Script de migration créé
- ✅ Script de rollback créé
- ✅ Script de vérification créé
- ✅ Documentation complète

---

**Auteur:** Trading Analytics V2  
**Date:** 2025-11-28  
**Version:** 1.0.0
