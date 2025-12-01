# Version 3 - Générateur HTML Monte Carlo Entièrement Paramétrable

## 🎯 Nouveauté V3

La **Version 3** vous permet de paramétrer **TOUS** les critères Kevin Davey pour trouver le capital minimum qui satisfait vos exigences:

| Critère | Paramètre CLI | Défaut |
|---------|---------------|---------|
| **Risque de ruine** | `--max-ruin` | 10% |
| **Return/DD Ratio** | `--min-return-dd` | Aucune contrainte |
| **Probabilité positive** | `--min-prob-positive` | Aucune contrainte |

**Flexibilité maximale**: Vous pouvez activer/désactiver chaque critère indépendamment!

## 🚀 Utilisation Rapide

### Scripts Batch Pré-configurés (Windows)

Double-cliquez simplement sur le fichier batch correspondant à votre profil:

| Fichier | Configuration | Recommandé pour |
|---------|---------------|-----------------|
| `generate_mc_html_simple.bat` | Ruine ≤10% seule | Découverte, vue d'ensemble |
| `generate_mc_html_kevin_davey.bat` | Ruine ≤10% + Return/DD ≥2 + Prob>0 ≥80% | Kevin Davey standard |
| `generate_mc_html_conservateur.bat` | Ruine ≤5% + Return/DD ≥2.5 + Prob>0 ≥85% | Capital important, risque minimal |
| `generate_mc_html_agressif.bat` | Ruine ≤20% + Return/DD ≥1.5 + Prob>0 ≥70% | Maximiser les opportunités |
| `generate_mc_html.bat` | Paramètres personnalisés | Expérimentations |

### Ligne de Commande Python

```bash
# Configuration par défaut (ruine seule ≤10%)
python run_monte_carlo_html_generator.py

# Kevin Davey complet
python run_monte_carlo_html_generator.py --max-ruin 10 --min-return-dd 2.0 --min-prob-positive 80

# Conservateur
python run_monte_carlo_html_generator.py --max-ruin 5 --min-return-dd 2.5 --min-prob-positive 85

# Agressif
python run_monte_carlo_html_generator.py --max-ruin 20 --min-return-dd 1.5 --min-prob-positive 70

# Seulement ruine + Return/DD (sans contrainte sur probabilité)
python run_monte_carlo_html_generator.py --max-ruin 10 --min-return-dd 2.5

# Run spécifique + configuration personnalisée
python run_monte_carlo_html_generator.py --run 20251201_1130 --max-ruin 12 --min-return-dd 2.2 --min-prob-positive 75
```

## 📊 Configurations Recommandées

### 1. Configuration Simple (Débutant)
```bash
python run_monte_carlo_html_generator.py --max-ruin 10
```
**Objectif**: Voir toutes les stratégies avec un risque de ruine acceptable  
**Avantages**: Maximum de stratégies disponibles  
**Résultats attendus**: ~95% des stratégies ont un capital recommandé

### 2. Configuration Kevin Davey Classique (Standard)
```bash
python run_monte_carlo_html_generator.py --max-ruin 10 --min-return-dd 2.0 --min-prob-positive 80
```
**Objectif**: Appliquer strictement les critères Kevin Davey  
**Avantages**: Stratégies de haute qualité uniquement  
**Résultats attendus**: ~20-30% des stratégies passent tous les critères

### 3. Configuration Conservatrice (Capital Important)
```bash
python run_monte_carlo_html_generator.py --max-ruin 5 --min-return-dd 2.5 --min-prob-positive 85
```
**Objectif**: Minimiser le risque, cibler les meilleures stratégies  
**Avantages**: Risque très faible, performance élevée  
**Résultats attendus**: ~10-15% des stratégies, capitaux plus élevés

### 4. Configuration Agressive (Opportunités Maximales)
```bash
python run_monte_carlo_html_generator.py --max-ruin 20 --min-return-dd 1.5 --min-prob-positive 70
```
**Objectif**: Maximiser le nombre de stratégies disponibles  
**Avantages**: Plus d'opportunités de trading  
**Résultats attendus**: ~50-60% des stratégies, capitaux plus faibles

### 5. Configuration Hybride (Ruine + Return/DD)
```bash
python run_monte_carlo_html_generator.py --max-ruin 10 --min-return-dd 2.5
```
**Objectif**: Équilibre entre sécurité et performance  
**Avantages**: Bon compromis  
**Résultats attendus**: ~30-40% des stratégies

## 📈 Exemples Concrets

### Exemple 1: Analyse Progressive

```bash
# Étape 1: Vue d'ensemble (ruine seule)
python run_monte_carlo_html_generator.py --max-ruin 10
# Résultat: 200 stratégies sur 245 ont un capital

# Étape 2: Ajouter Return/DD
python run_monte_carlo_html_generator.py --max-ruin 10 --min-return-dd 2.0
# Résultat: 85 stratégies sur 245 satisfont les deux critères

# Étape 3: Ajouter probabilité positive
python run_monte_carlo_html_generator.py --max-ruin 10 --min-return-dd 2.0 --min-prob-positive 80
# Résultat: 65 stratégies sur 245 satisfont tous les critères
```

### Exemple 2: Comparaison de Configurations

Testez différentes configurations et comparez:

```bash
# Configuration A: Standard
python run_monte_carlo_html_generator.py --max-ruin 10 --min-return-dd 2.0 --min-prob-positive 80
# → Sauvegardez: outputs/html_reports/montecarlo_A/

# Configuration B: Légèrement assouplie
python run_monte_carlo_html_generator.py --max-ruin 12 --min-return-dd 1.8 --min-prob-positive 75
# → Compare avec A pour voir l'impact
```

## 🔍 Comprendre les Résultats

### Sortie Console

```
================================================================================
GÉNÉRATEUR DE RAPPORTS HTML MONTE CARLO V3 - VERSION PARAMÉTRABLE
================================================================================

📁 Répertoire de run: 20251201_1130

⚙️  Critères de sélection du capital:
   • Risque de ruine ≤ 10.0%
   • Return/DD Ratio ≥ 2.0
   • Probabilité positive ≥ 80.0%

🔄 Recalcul des capitaux recommandés avec critères:
   Ruine ≤ 10.0% ET Return/DD ≥ 2.0 ET Prob>0 ≥ 80.0%

   ✓ Capitaux recalculés

📊 Statistiques après recalcul:
   • OK (tous critères satisfaits): 65
   • WARNING (ruine OK, autres critères non): 135
   • HIGH_RISK (aucun niveau satisfait): 45

💰 Capitaux recommandés:
   • Stratégies avec capital: 200/245 (81.6%)
   • Capital moyen: $18,750
   • Capital médian: $15,000
   • Capital min: $10,000
   • Capital max: $50,000
```

### Interprétation

| Statut | Signification | Action Recommandée |
|--------|---------------|-------------------|
| **OK** ✅ | Tous les critères satisfaits | ✅ Trader en confiance |
| **WARNING** ⚠️ | Ruine OK, mais autres critères non optimaux | ⚠️ Évaluer les compromis |
| **HIGH_RISK** ❌ | Aucun niveau ne satisfait les critères | ❌ Éviter ou revoir la stratégie |

### Stratégies WARNING - Décision

Pour les stratégies en WARNING, analysez:

1. **Si Return/DD < seuil**: Acceptez-vous un ratio moins bon?
2. **Si Prob>0 < seuil**: Acceptez-vous plus de volatilité?
3. **Capital recommandé**: Est-il dans vos moyens?

**Exemple**:
- Critères: Ruine ≤10%, Return/DD ≥2.5, Prob>0 ≥85%
- Stratégie X: Capital $15,000, Ruine 8%, Return/DD 2.2, Prob>0 82%
- **Statut**: WARNING
- **Décision**: Si vous acceptez Return/DD 2.2 et Prob 82%, cette stratégie est viable!

## 🛠️ Workflow Recommandé

### Workflow 1: Découverte

```bash
# 1. Vue d'ensemble
python run_monte_carlo_html_generator.py --max-ruin 10

# 2. Analyser les résultats HTML
# 3. Identifier les stratégies prometteuses
# 4. Affiner avec des critères supplémentaires
python run_monte_carlo_html_generator.py --max-ruin 10 --min-return-dd 2.0
```

### Workflow 2: Sélection Stricte

```bash
# 1. Kevin Davey complet
python run_monte_carlo_html_generator.py --max-ruin 10 --min-return-dd 2.0 --min-prob-positive 80

# 2. Si trop peu de stratégies, assouplir progressivement
python run_monte_carlo_html_generator.py --max-ruin 12 --min-return-dd 1.8 --min-prob-positive 75

# 3. Trouver le bon équilibre
python run_monte_carlo_html_generator.py --max-ruin 10 --min-return-dd 1.8 --min-prob-positive 80
```

### Workflow 3: Optimisation de Capital

```bash
# 1. Tester plusieurs seuils de ruine
python run_monte_carlo_html_generator.py --max-ruin 5
python run_monte_carlo_html_generator.py --max-ruin 10
python run_monte_carlo_html_generator.py --max-ruin 15

# 2. Comparer les capitaux recommandés
# 3. Choisir selon votre budget et tolérance au risque
```

## 📋 Tableau de Référence Rapide

| Profil de Trader | max-ruin | min-return-dd | min-prob-positive | Commande |
|------------------|----------|---------------|-------------------|----------|
| Débutant | 10% | - | - | `--max-ruin 10` |
| Standard (Kevin Davey) | 10% | 2.0 | 80% | `--max-ruin 10 --min-return-dd 2.0 --min-prob-positive 80` |
| Conservateur | 5% | 2.5 | 85% | `--max-ruin 5 --min-return-dd 2.5 --min-prob-positive 85` |
| Très conservateur | 5% | 3.0 | 90% | `--max-ruin 5 --min-return-dd 3.0 --min-prob-positive 90` |
| Modéré | 12% | 1.8 | 75% | `--max-ruin 12 --min-return-dd 1.8 --min-prob-positive 75` |
| Agressif | 15% | 1.5 | 70% | `--max-ruin 15 --min-return-dd 1.5 --min-prob-positive 70` |
| Très agressif | 20% | 1.2 | 65% | `--max-ruin 20 --min-return-dd 1.2 --min-prob-positive 65` |

## ⚡ Astuces Pro

### Astuce 1: Test A/B de Configurations

Créez vos propres scripts batch pour vos configurations favorites:

```batch
@echo off
REM Ma configuration personnelle
python run_monte_carlo_html_generator.py --max-ruin 8 --min-return-dd 2.2 --min-prob-positive 78
pause
```

### Astuce 2: Analyse de Sensibilité

Testez comment vos stratégies réagissent aux changements de critères:

```bash
# Baseline
python run_monte_carlo_html_generator.py --max-ruin 10 --min-return-dd 2.0

# +10% sur ruine
python run_monte_carlo_html_generator.py --max-ruin 11 --min-return-dd 2.0

# +5% sur Return/DD
python run_monte_carlo_html_generator.py --max-ruin 10 --min-return-dd 2.1
```

### Astuce 3: Pipeline Automatisé

Créez un script pour tester plusieurs configurations d'un coup:

```bash
# test_configurations.bat
@echo off
echo Testing configuration 1: Simple
python run_monte_carlo_html_generator.py --max-ruin 10

echo Testing configuration 2: Kevin Davey
python run_monte_carlo_html_generator.py --max-ruin 10 --min-return-dd 2.0 --min-prob-positive 80

echo Testing configuration 3: Conservative
python run_monte_carlo_html_generator.py --max-ruin 5 --min-return-dd 2.5 --min-prob-positive 85

echo Done! Check outputs/html_reports/montecarlo/
```

## 🎓 Cas d'Usage Avancés

### Cas 1: Portfolio Mixte

Sélectionnez différentes stratégies selon leur profil:

```bash
# Stratégies core: très sûres
python run_monte_carlo_html_generator.py --max-ruin 5 --min-return-dd 2.5 --min-prob-positive 85
# → Sélectionner 5-10 stratégies

# Stratégies satellite: plus dynamiques
python run_monte_carlo_html_generator.py --max-ruin 15 --min-return-dd 1.8 --min-prob-positive 75
# → Sélectionner 10-15 stratégies
```

### Cas 2: Allocation de Capital Optimale

```bash
# 1. Identifier toutes les stratégies viables (ruine seule)
python run_monte_carlo_html_generator.py --max-ruin 10

# 2. Noter les capitaux recommandés
# 3. Sommer les capitaux nécessaires
# 4. Si > budget, augmenter les critères pour filtrer
python run_monte_carlo_html_generator.py --max-ruin 10 --min-return-dd 2.2
```

### Cas 3: Backtesting de Configurations

```bash
# Tester une théorie: "Return/DD 2.5 est-il trop strict?"
python run_monte_carlo_html_generator.py --max-ruin 10 --min-return-dd 2.5
# → Note: X stratégies

python run_monte_carlo_html_generator.py --max-ruin 10 --min-return-dd 2.0
# → Note: Y stratégies (Y > X)

# Décision: Équilibre entre quantité et qualité
```

## ❓ FAQ

### Q: Dois-je toujours spécifier tous les critères?

**Non!** Vous pouvez en spécifier un, deux ou trois. Les non-spécifiés ne sont pas appliqués.

### Q: Quelle est la différence entre V2 et V3?

- **V2**: Seuil de ruine seul paramétrable
- **V3**: **Tous** les critères paramétrables

### Q: Comment choisir mes valeurs?

1. **Commencez avec défaut** (ruine 10% seule)
2. **Analysez les résultats**
3. **Ajoutez progressivement** d'autres critères
4. **Affinez** jusqu'à avoir le bon équilibre

### Q: Que faire si aucune stratégie ne passe?

- **Assouplir les critères**: Augmenter max-ruin, diminuer min-return-dd
- **Revoir les stratégies**: Peut-être que votre collection nécessite plus de travail
- **Augmenter les niveaux de capital testés**: Peut-être que les stratégies ont besoin de plus de capital

## 📞 Support

Pour questions ou problèmes:
1. Vérifier ce README
2. Tester avec configuration simple: `--max-ruin 10`
3. Consulter `README_V2.md` et `README_HTML_GENERATOR.md`

---

**Version**: 3.0.0  
**Date**: 2025-12-01  
**Auteur**: Yann

**Versions disponibles**:
- V1: Critères Kevin Davey fixes (tous ou rien)
- V2: Ruine seule paramétrable
- **V3: Tous critères paramétrables** ⭐
