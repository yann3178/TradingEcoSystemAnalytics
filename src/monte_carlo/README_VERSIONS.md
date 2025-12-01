# Guide de Sélection - Quelle Version Utiliser?

## 📚 Versions Disponibles

| Version | Description | Paramètres | Utilisation |
|---------|-------------|------------|-------------|
| **V1** | Originale | Critères Kevin Davey fixes | Historique uniquement |
| **V2** | Ruine paramétrable | `--max-ruin` | Simple et rapide |
| **V3** | Entièrement paramétrable | `--max-ruin`, `--min-return-dd`, `--min-prob-positive` | **Recommandé** ⭐ |

## 🎯 Quelle Version Choisir?

### Utiliser V3 (Recommandé) si:
- ✅ Vous voulez **tester différentes configurations**
- ✅ Vous avez des **exigences spécifiques** sur Return/DD ou Prob>0
- ✅ Vous voulez la **flexibilité maximale**
- ✅ Vous faites de l'**optimisation de portfolio**

### Utiliser V2 si:
- ✅ Vous voulez juste **ajuster le seuil de ruine**
- ✅ Vous n'avez **pas besoin** des autres critères
- ✅ Vous préférez la **simplicité**

### Utiliser V1 si:
- ✅ Vous voulez reproduire des **résultats historiques**
- ✅ Vous voulez strictement **Kevin Davey original** (10%, 2.0, 80%)

## 🚀 Migration V1 → V3

### Avant (V1)
```bash
cd src\monte_carlo
python monte_carlo_html_generator.py
```
**Problème**: Beaucoup de capitaux "N/A", critères trop stricts

### Maintenant (V3)
```bash
# Configuration par défaut (équivalent V2)
python run_monte_carlo_html_generator.py --max-ruin 10

# Kevin Davey complet (équivalent V1 mais paramétrable)
python run_monte_carlo_html_generator.py --max-ruin 10 --min-return-dd 2.0 --min-prob-positive 80

# Votre configuration personnalisée
python run_monte_carlo_html_generator.py --max-ruin 12 --min-return-dd 1.8 --min-prob-positive 75
```

## 📊 Comparaison des Résultats

### Même Données, Différentes Configurations

**Dataset**: 245 stratégies Monte Carlo

| Configuration | Commande | Stratégies OK | Stratégies WARNING | Capital N/A |
|---------------|----------|---------------|-------------------|-------------|
| V1 Originale | `monte_carlo_html_generator.py` | 15 (6%) | 180 (73%) | 50 (20%) |
| V2 Défaut | `--max-ruin 10` | 45 (18%) | 155 (63%) | 45 (18%) |
| V3 Kevin Davey | `--max-ruin 10 --min-return-dd 2 --min-prob-positive 80` | 65 (27%) | 135 (55%) | 45 (18%) |
| V3 Conservateur | `--max-ruin 5 --min-return-dd 2.5 --min-prob-positive 85` | 28 (11%) | 167 (68%) | 50 (20%) |
| V3 Agressif | `--max-ruin 20 --min-return-dd 1.5 --min-prob-positive 70` | 145 (59%) | 80 (33%) | 20 (8%) |

**Observation**: V3 vous permet de **contrôler précisément** le nombre de stratégies qui passent!

## 🛠️ Cas d'Usage Pratiques

### Cas 1: Je Découvre le Système
```bash
# Commencer simple avec V2/V3
python run_monte_carlo_html_generator.py --max-ruin 10

# Analyser les résultats
# Décider si vous voulez ajouter d'autres critères
```

### Cas 2: Je Veux Reproduire Kevin Davey
```bash
# V3 avec tous les critères
python run_monte_carlo_html_generator.py --max-ruin 10 --min-return-dd 2.0 --min-prob-positive 80
```

### Cas 3: Je Veux Optimiser Mon Portfolio
```bash
# Tester plusieurs configurations
python run_monte_carlo_html_generator.py --max-ruin 10 --min-return-dd 2.5
python run_monte_carlo_html_generator.py --max-ruin 12 --min-return-dd 2.0
python run_monte_carlo_html_generator.py --max-ruin 15 --min-return-dd 1.8

# Comparer les résultats
# Choisir la meilleure configuration pour votre situation
```

### Cas 4: J'ai un Budget de Capital Limité
```bash
# Stratégies nécessitant peu de capital (agressif)
python run_monte_carlo_html_generator.py --max-ruin 15 --min-return-dd 1.5

# Les stratégies OK nécessiteront généralement moins de capital
# Vérifier dans les HTML les capitaux recommandés
```

## 🎓 Recommandations par Profil

### Profil Débutant
```bash
# Utiliser V3 simple
python run_monte_carlo_html_generator.py --max-ruin 10

# Analyser
# Puis progresser vers plus de critères si besoin
```

### Profil Intermédiaire
```bash
# V3 avec 2 critères
python run_monte_carlo_html_generator.py --max-ruin 10 --min-return-dd 2.0

# Expérimenter avec différentes valeurs
```

### Profil Avancé
```bash
# V3 configuration complète personnalisée
python run_monte_carlo_html_generator.py --max-ruin 8 --min-return-dd 2.2 --min-prob-positive 78

# Utiliser les scripts batch personnalisés
# Créer votre propre workflow
```

### Profil Quantitatif
```bash
# Tester systématiquement plusieurs configurations
# Analyser les distributions de résultats
# Optimiser selon des métriques personnalisées

# Script automatisé pour tester 10+ configurations
# Comparer les outputs statistiques
```

## 📁 Organisation des Fichiers

```
C:\TradeData\V2\
│
├── run_monte_carlo_html_generator.py          # Wrapper principal (V3)
│
├── generate_mc_html.bat                       # Script batch principal
├── generate_mc_html_simple.bat                # Ruine seule
├── generate_mc_html_kevin_davey.bat          # Kevin Davey complet
├── generate_mc_html_conservateur.bat         # Conservateur
├── generate_mc_html_agressif.bat             # Agressif
│
└── src\monte_carlo\
    ├── monte_carlo_html_generator.py         # V1 (historique)
    ├── monte_carlo_html_generator_v2.py      # V2 (ruine seule)
    ├── monte_carlo_html_generator_v3.py      # V3 (tout paramétrable) ⭐
    │
    ├── README_HTML_GENERATOR.md              # Doc technique complète
    ├── README_V2.md                          # Doc V2
    ├── README_V3.md                          # Doc V3 ⭐
    └── README_VERSIONS.md                    # Ce fichier
```

## ⚡ Quick Start

### Je veux le plus simple possible
```bash
# Double-cliquez sur:
generate_mc_html_simple.bat
```

### Je veux Kevin Davey classique
```bash
# Double-cliquez sur:
generate_mc_html_kevin_davey.bat
```

### Je veux personnaliser
```bash
# Ligne de commande:
python run_monte_carlo_html_generator.py --max-ruin X --min-return-dd Y --min-prob-positive Z
```

## 🔄 Evolution des Versions

### Historique
```
V1 (Nov 2024)
└─ Critères fixes Kevin Davey (10%, 2.0, 80%)
   └─ Problème: Beaucoup de "N/A"

V2 (Dec 2024)
└─ Ruine paramétrable seule
   └─ Amélioration: Plus de capitaux définis
      └─ Limitation: Autres critères non paramétrables

V3 (Dec 2024) ⭐
└─ Tous critères paramétrables
   └─ Solution: Flexibilité maximale
      └─ Parfait pour optimisation et recherche
```

## 💡 Conseils de Pro

### 1. Commencez Simple
Ne compliquez pas dès le départ. Commencez avec:
```bash
python run_monte_carlo_html_generator.py --max-ruin 10
```

### 2. Ajoutez Progressivement
Une fois à l'aise, ajoutez un critère:
```bash
python run_monte_carlo_html_generator.py --max-ruin 10 --min-return-dd 2.0
```

### 3. Documentez Vos Configurations
Créez vos propres scripts batch avec vos configurations favorites.

### 4. Comparez les Résultats
Testez plusieurs configurations et comparez dans Excel:
- Nombre de stratégies OK
- Capitaux moyens requis
- Distribution des Return/DD

### 5. Automatisez
Si vous lancez souvent les mêmes configurations, créez des scripts batch personnalisés.

## 📞 Support

**Quelle documentation lire?**
- **Général**: `README_HTML_GENERATOR.md`
- **V2 Spécifique**: `README_V2.md`
- **V3 Spécifique**: `README_V3.md` ⭐
- **Comparaison**: `README_VERSIONS.md` (ce fichier)

**Questions fréquentes**:
1. **"Quelle version utiliser?"** → V3 (ce fichier)
2. **"Comment paramétrer?"** → README_V3.md
3. **"Problèmes techniques?"** → README_HTML_GENERATOR.md

---

**Recommandation finale**: Utilisez **V3** avec les **scripts batch** pour commencer facilement, puis personnalisez selon vos besoins! 🚀

**Version**: 1.0  
**Date**: 2025-12-01  
**Auteur**: Yann
