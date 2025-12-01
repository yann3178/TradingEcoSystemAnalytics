# RAPPORT DE MODIFICATIONS - Dashboard Monte Carlo Interactif
## Version 2.1 - Dashboard avec Recalcul Dynamique

Date: 2025-12-01
Statut: ✅ Configuration enrichie - EN COURS: Réécriture du template

---

## 🎯 Objectif

Transformer la page de synthèse Monte Carlo en un dashboard interactif permettant de recalculer en temps réel les capitaux recommandés selon différents profils de risque (Simple, Kevin Davey, Conservateur, Agressif).

---

## ✅ ÉTAPES COMPLÉTÉES

### 1. Enrichissement de la Configuration ✅

**Fichier**: `src/monte_carlo/config.py`

**Backup créé**: `src/monte_carlo/config.py.backup`

**Nouveaux paramètres ajoutés**:

```python
# Critères par défaut (Kevin Davey)
DASHBOARD_DEFAULT_CRITERIA = {
    'max_ruin': 0.10,
    'min_return_dd': 2.0,
    'min_prob_positive': 0.80,
}

# 4 Presets prédéfinis
DASHBOARD_PRESETS = {
    'simple': {...},          # Ruine seule
    'kevin_davey': {...},     # Standard
    'conservative': {...},    # Strict
    'aggressive': {...},      # Souple
}

# Configuration des sliders
SLIDER_RANGES = {
    'max_ruin': {'min': 0, 'max': 0.30, 'step': 0.005},
    'min_return_dd': {'min': 0, 'max': 5.0, 'step': 0.1},
    'min_prob_positive': {'min': 0, 'max': 1.0, 'step': 0.01},
}

# Palette de couleurs (Dark Theme)
DASHBOARD_COLORS = {
    'bg_primary': '#0f0f1a',
    'accent_green': '#00d4aa',    # OK
    'accent_yellow': '#ffe66d',    # WARNING
    'accent_red': '#ff6b6b',       # HIGH_RISK
    # ... 10 couleurs au total
}

# + DASHBOARD_DISPLAY, CHART_CONFIG, FILE_PATTERNS, etc.
```

**Test de validation**: ✅ RÉUSSI

```bash
python test_config_import.py
# ✅ Tous les imports fonctionnent
# ✅ Anciens paramètres préservés
# ✅ Nouveaux paramètres accessibles
```

---

### 2. Modification du Générateur HTML ✅

**Fichier créé**: `src/monte_carlo/monte_carlo_html_generator_v2.1.py`

**Changements principaux**:

1. **Import des nouveaux paramètres de config**:
```python
from src.monte_carlo.config import (
    STATUS_OK, STATUS_WARNING, STATUS_HIGH_RISK,
    DASHBOARD_DEFAULT_CRITERIA,
    DASHBOARD_PRESETS,
    DASHBOARD_COLORS,
    SLIDER_RANGES,
    DASHBOARD_DISPLAY,
    FILE_PATTERNS,
)
```

2. **Utilisation des constantes de statut**:
   - Remplacé les chaînes hardcodées "OK", "WARNING", "HIGH_RISK"
   - Utilisé `STATUS_OK`, `STATUS_WARNING`, `STATUS_HIGH_RISK`

3. **Ajout de placeholders dans `generate_summary_html()`**:
```python
presets_json = json.dumps(DASHBOARD_PRESETS)
colors_json = json.dumps(DASHBOARD_COLORS)
slider_ranges_json = json.dumps(SLIDER_RANGES)
default_criteria_json = json.dumps(DASHBOARD_DEFAULT_CRITERIA)

html_content = HTML_SUMMARY_TEMPLATE.format(
    # ... placeholders existants ...
    presets_json=presets_json,           # NOUVEAU
    colors_json=colors_json,             # NOUVEAU
    slider_ranges_json=slider_ranges_json, # NOUVEAU
    default_criteria_json=default_criteria_json, # NOUVEAU
)
```

4. **Fallback gracieux**:
   - Si l'import échoue, utilise des valeurs par défaut
   - Empêche l'échec total du script

**Points d'attention**:
- ✅ Fonction `generate_individual_html()` **INCHANGÉE**
- ✅ Génération des pages individuelles **PRÉSERVÉE**
- ⚠️ Le template `SUMMARY_TEMPLATE` doit être réécrit pour utiliser ces nouveaux placeholders

---

## 🚧 PROCHAINES ÉTAPES

### 3. Réécriture du SUMMARY_TEMPLATE ⏳ EN COURS

**Fichier à modifier**: `src/monte_carlo/html_templates.py`

**Backup à créer**: `html_templates.py.backup`

**Objectifs**:
1. Créer un nouveau `SUMMARY_TEMPLATE` complet avec:
   - Panneau de critères dynamiques (3 sliders + 3 boutons)
   - Stats live qui se mettent à jour en temps réel
   - 4 graphiques Chart.js statiques
   - Tableau interactif avec tri et animation
   - JavaScript pour le recalcul dynamique

2. Placeholders à utiliser:
```python
# Existants
{generation_date}, {total_strategies}, {ok_count}, {warning_count},
{high_risk_count}, {total_trades}, {total_pnl}, {symbol_options},
{table_rows}, {strategies_json}, {strategies_detailed_json}, {config_info}

# NOUVEAUX
{presets_json}, {colors_json}, {slider_ranges_json}, {default_criteria_json}
```

3. **IMPORTANT**: Doubler toutes les accolades JavaScript `{ }` → `{{ }}`
   - Sinon Python `.format()` va chercher des variables inexistantes
   - Exemple: `function test() {{ return {{ value: 10 }}; }}`

---

## 📊 Comparaison Avant/Après

### Avant (V2.0)
- Page de synthèse **statique**
- Capitaux recommandés calculés une fois
- Critères fixés à: Ruine 10% + Return/DD 2.0 + Prob 80%
- Aucun moyen de tester d'autres profils de risque

### Après (V2.1)
- Page de synthèse **interactive**
- Capitaux recalculés en temps réel via JavaScript
- 4 presets + configuration libre des critères
- Visualisation immédiate de l'impact des critères
- Animations et feedback visuel

---

## 🔄 Migration Progressive

### Option 1: Migration Directe (Recommandée)
1. Remplacer `monte_carlo_html_generator.py` par la v2.1
2. Réécrire `SUMMARY_TEMPLATE` dans `html_templates.py`
3. Tester la génération
4. Si OK, supprimer les backups

### Option 2: Cohabitation Temporaire
1. Garder les deux versions en parallèle
2. Tester la v2.1 sur un run de test
3. Comparer les résultats
4. Basculer définitivement une fois validé

---

## 🧪 Tests de Validation

### Tests à effectuer après réécriture du template:

1. **Test de génération**:
```bash
cd C:\TradeData\V2\src\monte_carlo
python monte_carlo_html_generator_v2.1.py
```

2. **Vérifications visuelles**:
   - [ ] La page de synthèse s'affiche correctement
   - [ ] Les 4 graphiques Chart.js sont visibles
   - [ ] Le tableau contient 245 lignes
   - [ ] Les sliders sont fonctionnels

3. **Test du recalcul dynamique**:
   - [ ] Déplacer le slider "Ruine Max" → Les valeurs changent
   - [ ] Activer "Return/DD Min" → Recalcul OK
   - [ ] Cliquer "Kevin Davey" → Configuration appliquée
   - [ ] Vérifier console (F12): Aucune erreur JavaScript

4. **Test de non-régression**:
   - [ ] Les 245 pages individuelles sont identiques à avant
   - [ ] Les liens vers pages individuelles fonctionnent
   - [ ] Les filtres d'affichage fonctionnent

---

## 📁 Fichiers Créés/Modifiés

```
C:\TradeData\V2\
├── src/monte_carlo/
│   ├── config.py                           ✅ MODIFIÉ
│   ├── config.py.backup                    ✅ CRÉÉ
│   ├── monte_carlo_html_generator.py       ⚠️ À REMPLACER
│   ├── monte_carlo_html_generator_v2.1.py  ✅ CRÉÉ
│   └── html_templates.py                   ⏳ À RÉÉCRIRE
│
├── test_config_import.py                   ✅ CRÉÉ
└── create_backups.py                       ✅ CRÉÉ
```

---

## 🎯 Résultat Final Attendu

Une page HTML `all_strategies_montecarlo.html` qui permet de:
- ✅ Tester 4 profils de risque prédéfinis
- ✅ Configurer librement les 3 critères via sliders
- ✅ Voir en temps réel l'impact sur les capitaux recommandés
- ✅ Visualiser combien de stratégies passent les critères
- ✅ Identifier rapidement les stratégies OK/WARNING/HIGH_RISK
- ✅ Utiliser sur mobile et desktop

---

## 💡 Prochaine Action

**Réécrire le `SUMMARY_TEMPLATE` dans `html_templates.py`**

Cette étape nécessite:
1. Créer un backup de `html_templates.py`
2. Réécrire complètement le `SUMMARY_TEMPLATE`
3. Vérifier que toutes les accolades JS sont doublées
4. Tester la génération

**Temps estimé**: 30-45 minutes

**Risque**: Faible (backup disponible + pages individuelles préservées)

---

## 📞 Support

En cas de problème:
1. Restaurer les backups: `cp *.backup fichier_original`
2. Vérifier les logs dans la console
3. Tester avec un petit subset de stratégies d'abord

---

**Status**: 🟢 Prêt pour l'étape suivante
**Prochaine étape**: Réécriture du SUMMARY_TEMPLATE
