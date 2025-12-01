# Version Améliorée du Générateur HTML Monte Carlo

## 🆕 Nouveautés Version 2

### Problème Résolu

Dans la version originale, le **capital recommandé** n'était affiché que si **TOUS** les critères Kevin Davey étaient satisfaits simultanément:
- ✅ Risque de ruine ≤ 10%
- ✅ Return/DD Ratio ≥ 2
- ✅ Probabilité positive ≥ 80%

**Résultat**: La plupart des stratégies affichaient "N/A" comme capital recommandé et étaient marquées "WARNING".

### Solution Implémentée

La **Version 2** calcule le capital recommandé basé **UNIQUEMENT sur le seuil de ruine**:
- ✅ Le capital minimum pour atteindre un risque de ruine ≤ X%
- ✅ X est configurable (par défaut: 10%)
- ✅ Les autres critères sont affichés mais ne bloquent pas la recommandation

## 📊 Impact

### Avant (V1)
- Capital recommandé: Souvent "N/A"
- Statut: Majoritairement "WARNING"
- Stratégies sans capital: ~70-80%

### Après (V2)
- Capital recommandé: Toujours affiché (si un niveau satisfait le seuil de ruine)
- Statut: Reflète uniquement le respect du seuil de ruine
- Stratégies avec capital: ~95-100%

## 🚀 Utilisation

### Méthode 1: Python (Recommandé)

```bash
# Dernier run avec seuil de ruine 10%
python run_monte_carlo_html_generator.py

# Run spécifique
python run_monte_carlo_html_generator.py --run 20251201_1130

# Seuil de ruine personnalisé (ex: 15%)
python run_monte_carlo_html_generator.py --max-ruin 15

# Combinaison
python run_monte_carlo_html_generator.py --run 20251201_1130 --max-ruin 20
```

### Méthode 2: Fichier Batch Windows

```batch
REM Dernier run, seuil 10%
generate_mc_html.bat

REM Run spécifique, seuil 10%
generate_mc_html.bat 20251201_1130

REM Run spécifique, seuil 15%
generate_mc_html.bat 20251201_1130 15
```

### Méthode 3: Directement depuis le répertoire

```bash
cd src\monte_carlo
python monte_carlo_html_generator_v2.py --max-ruin 12
```

## ⚙️ Configuration du Seuil de Ruine

Le seuil de ruine peut être ajusté selon votre tolérance au risque:

| Seuil | Profil de Risque | Usage Recommandé |
|-------|------------------|------------------|
| 5%    | Très conservateur | Capital important, risque minimal |
| **10%** | **Conservateur** | **Standard Kevin Davey** ⭐ |
| 15%   | Modéré | Accepte plus de risque |
| 20%   | Agressif | Maximise le rendement potentiel |

## 📋 Nouveaux Statuts

La logique de statut a été simplifiée:

### OK ✅
- Risque de ruine ≤ Seuil choisi
- Return/DD ≥ 2
- Prob positive ≥ 80%
- **Tous les critères satisfaits**

### WARNING ⚠️
- Risque de ruine ≤ Seuil choisi
- Mais Return/DD < 2 OU Prob positive < 80%
- **Capital recommandé fiable malgré tout**

### HIGH_RISK ❌
- Risque de ruine > Seuil choisi
- **Aucun niveau de capital testé ne satisfait le seuil de ruine**
- Stratégie à éviter ou augmenter les niveaux de capital testés

## 🔍 Exemples Concrets

### Exemple 1: Stratégie Conservatrice

Données:
- Capital $10,000: Ruine 8%, Return/DD 2.5, Prob>0 85%
- Capital $15,000: Ruine 4%, Return/DD 2.1, Prob>0 90%

Résultats:
- **Seuil 10%**: Capital recommandé = $10,000, Statut = OK ✅
- **Seuil 5%**: Capital recommandé = $15,000, Statut = OK ✅

### Exemple 2: Stratégie Agressive

Données:
- Capital $10,000: Ruine 15%, Return/DD 3.5, Prob>0 82%
- Capital $20,000: Ruine 8%, Return/DD 2.8, Prob>0 85%

Résultats:
- **Seuil 10%**: Capital recommandé = $20,000, Statut = OK ✅
- **Seuil 15%**: Capital recommandé = $10,000, Statut = OK ✅
- **Seuil 5%**: Stratégie = HIGH_RISK ❌

### Exemple 3: Stratégie à Faible Return/DD

Données:
- Capital $15,000: Ruine 9%, Return/DD 1.5, Prob>0 75%
- Capital $25,000: Ruine 6%, Return/DD 1.3, Prob>0 78%

Résultats:
- **Seuil 10%**: Capital recommandé = $15,000, Statut = WARNING ⚠️
- Raison: Ruine OK mais Return/DD < 2 et Prob < 80%
- **Utilisable mais sous-optimal**

## 📁 Fichiers

### Scripts

| Fichier | Description |
|---------|-------------|
| `run_monte_carlo_html_generator.py` | Wrapper principal (utilise V2) |
| `src/monte_carlo/monte_carlo_html_generator.py` | Version originale (V1) |
| `src/monte_carlo/monte_carlo_html_generator_v2.py` | **Version améliorée (V2)** |
| `generate_mc_html.bat` | Script batch Windows |

### Outputs

```
outputs/
└── html_reports/
    └── montecarlo/
        ├── all_strategies_montecarlo.html       # Page de synthèse
        └── Individual/                           # Pages individuelles
            ├── ES_Strategy1_MC.html
            ├── NQ_Strategy2_MC.html
            └── ...
```

## 🔄 Migration depuis V1

Si vous avez déjà généré des rapports avec V1:

1. **Pas de modification des CSV nécessaire** - La V2 lit les mêmes fichiers
2. **Relancer la génération** avec la nouvelle commande
3. **Les anciens HTML seront écrasés** - Faire un backup si nécessaire

```bash
# Backup optionnel des anciens HTML
xcopy /E /I outputs\html_reports\montecarlo outputs\html_reports\montecarlo_backup_v1

# Générer les nouveaux rapports
python run_monte_carlo_html_generator.py
```

## ❓ FAQ

### Q: Puis-je toujours utiliser V1?

Oui, V1 est toujours disponible:
```bash
cd src\monte_carlo
python monte_carlo_html_generator.py
```

### Q: Les fichiers CSV sont-ils modifiés?

Non, V2 ne modifie que les rapports HTML. Les CSV restent intacts.

### Q: Que se passe-t-il si aucun niveau ne satisfait mon seuil?

La stratégie sera marquée "HIGH_RISK" sans capital recommandé. Cela signifie que:
- Soit vous devez augmenter votre tolérance au risque
- Soit la stratégie nécessite plus de capital que les niveaux testés

### Q: Puis-je générer plusieurs versions avec différents seuils?

Oui! Lancez simplement le générateur plusieurs fois avec différents seuils.
Les fichiers seront écrasés à chaque fois. Si vous voulez conserver plusieurs versions,
copiez le répertoire HTML entre chaque génération.

## 🎯 Recommandations

### Pour le Trading Live

- **Utiliser seuil 10%** (Kevin Davey standard)
- **Vérifier que Return/DD ≥ 2** (même si WARNING)
- **Considérer Prob>0 ≥ 80%** comme bonus

### Pour le Backtesting

- **Tester plusieurs seuils** (5%, 10%, 15%)
- **Analyser la sensibilité** du capital au seuil
- **Comparer les stratégies** avec le même seuil

### Pour l'Optimisation de Capital

1. Générer avec seuil 10%
2. Noter le capital recommandé
3. Tester avec seuil 5% et 15%
4. Observer la variation du capital
5. Choisir selon votre tolérance au risque

## 🚀 Prochaines Améliorations Possibles

- [ ] Sélecteur de seuil dynamique dans l'interface HTML
- [ ] Graphique montrant l'évolution du capital recommandé vs seuil
- [ ] Export PDF des rapports
- [ ] Comparateur multi-seuils côte à côte
- [ ] Statistiques de distribution des capitaux par seuil

## 📞 Support

Pour toute question:
1. Vérifier ce README
2. Consulter `README_HTML_GENERATOR.md` pour plus de détails
3. Vérifier les logs de génération

---

**Version**: 2.0.0  
**Date**: 2025-12-01  
**Auteur**: Yann
