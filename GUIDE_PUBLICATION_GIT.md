# GUIDE DE PUBLICATION GIT - Dashboard Monte Carlo V2.1

## 🎯 Résumé des Changements à Publier

### Dashboard Monte Carlo V2.1
- Recalcul dynamique des capitaux (245 stratégies en <200ms)
- Interface interactive avec sliders et presets
- Stats live, graphiques Chart.js, tableau interactif

### Enrichissement Navigation
- Liens croisés Monte Carlo ↔ AI Analysis
- Boutons de navigation modernes
- Script d'enrichissement automatique

---

## 🚀 OPTION A : Publication Automatique (Recommandé)

```bash
cd C:\TradeData\V2
python git_publish_v2.1.py
```

Le script va :
1. ✅ Vérifier le statut Git
2. ✅ Ajouter tous les fichiers modifiés
3. ✅ Créer un commit avec message détaillé
4. ✅ Proposer de pusher vers GitHub
5. ✅ Afficher un résumé

**Durée** : 30 secondes

---

## 📝 OPTION B : Publication Manuelle

### Étape 1 : Vérifier le statut

```bash
cd C:\TradeData\V2
git status
```

### Étape 2 : Ajouter les fichiers

```bash
# Fichiers de production
git add src/monte_carlo/config.py
git add src/monte_carlo/monte_carlo_html_generator.py
git add src/monte_carlo/html_templates.py

# Backups
git add src/monte_carlo/*.backup
git add src/monte_carlo/*_BACKUP.py

# Nouveau script
git add enrich_montecarlo_html_pages_with_ai_pages_link.py

# Documentation
git add MODIFICATIONS_DASHBOARD_MC.md
git add GUIDE_NETTOYAGE_MANUEL.md
git add RAPPORT_V2.1_DASHBOARD.md
git add RAPPORT_ENRICHISSEMENT_LIENS.txt
git add NETTOYAGE_AUTO.bat

# Archives (si présentes)
git add src/monte_carlo/archive/
git add migration_v2.1/
```

### Étape 3 : Commit

```bash
git commit -m "feat: Dashboard Monte Carlo V2.1 + Enrichissement liens croisés

Dashboard Interactif Monte Carlo V2.1:
- Recalcul dynamique des capitaux recommandés (245 stratégies)
- 3 sliders configurables (Ruine, Return/DD, Prob Positive)
- 4 presets prédéfinis (Simple, Kevin Davey, Conservateur, Agressif)
- Stats live avec mise à jour temps réel
- 4 graphiques Chart.js + tableau interactif
- Design dark theme professionnel

Enrichissement Navigation:
- Script enrich_montecarlo_html_pages_with_ai_pages_link.py
- Liens bidirectionnels Monte Carlo ↔ AI Analysis
- Boutons navigation vers Dashboard principal

Fichiers modifiés:
- config.py (+150 lignes)
- monte_carlo_html_generator.py (nouveaux placeholders)
- html_templates.py (nouveau SUMMARY_TEMPLATE ~800 lignes)

Documentation:
- 4 guides complets
- 3 backups de sécurité

Non-régression: Pages individuelles 100% préservées
Tests: 245 stratégies validées
Breaking changes: Aucun"
```

### Étape 4 : Push vers GitHub

```bash
git push origin main
```

Ou si vous êtes sur une autre branche :

```bash
git branch  # Vérifier la branche actuelle
git push origin <nom-de-votre-branche>
```

---

## ✅ Vérification Post-Publication

Après le push, vérifiez sur GitHub :

1. **Commit visible** :
   - https://github.com/yann3178/TradingEcoSystemAnalytics/commits

2. **Fichiers présents** :
   - `src/monte_carlo/config.py` (modifié)
   - `src/monte_carlo/monte_carlo_html_generator.py` (modifié)
   - `src/monte_carlo/html_templates.py` (modifié)
   - `enrich_montecarlo_html_pages_with_ai_pages_link.py` (nouveau)
   - Documentation (4 fichiers)

3. **README à jour** (optionnel) :
   - Mettre à jour le README principal avec les nouvelles fonctionnalités

---

## 📊 Statistiques du Commit

### Lignes de Code
- **Ajoutées** : ~1500 lignes
  - config.py: +150
  - html_templates.py: +800
  - enrich_...py: +400
  - Documentation: +150

- **Modifiées** : ~100 lignes
  - monte_carlo_html_generator.py: ~50
  - Divers: ~50

### Fichiers
- **Modifiés** : 3 fichiers de production
- **Créés** : 8 nouveaux fichiers
  - 1 script d'enrichissement
  - 4 documents
  - 3 backups

### Impact
- **Features** : 2 majeures (Dashboard V2.1 + Navigation)
- **Breaking changes** : 0
- **Tests** : 245 stratégies validées
- **Performance** : <200ms pour recalcul complet

---

## 🏷️ Tag de Version (Optionnel)

Si vous voulez créer un tag pour cette version :

```bash
git tag -a v2.1.0 -m "Dashboard Monte Carlo V2.1 - Recalcul dynamique + Navigation"
git push origin v2.1.0
```

Cela créera un release officiel sur GitHub.

---

## 🔄 En Cas de Problème

### Annuler le dernier commit (avant push)
```bash
git reset --soft HEAD~1
```

### Modifier le message de commit (avant push)
```bash
git commit --amend -m "Nouveau message"
```

### Forcer le push (si conflit)
```bash
git push origin main --force-with-lease
```
⚠️ **ATTENTION** : Utilisez avec précaution

---

## 📋 Checklist Avant Publication

- [ ] Tous les fichiers sont ajoutés au staging
- [ ] Le message de commit est clair et détaillé
- [ ] Les tests ont été effectués (dashboard fonctionne)
- [ ] La documentation est à jour
- [ ] Les backups sont présents
- [ ] Pas de fichiers sensibles (credentials, etc.)
- [ ] Le code compile/s'exécute sans erreur

---

## 🎉 Après Publication

Une fois publié sur GitHub :

1. **Partager** : Inviter des collaborateurs si besoin
2. **Documenter** : Mettre à jour le README principal
3. **Tagger** : Créer un tag de version (v2.1.0)
4. **Annoncer** : Créer une release note sur GitHub
5. **Suivre** : Monitorer les issues/feedbacks

---

## 📞 Support

En cas de problème lors de la publication :

- **Erreur de push** : Vérifier les droits sur le repo
- **Conflit** : Faire un `git pull` d'abord
- **Fichiers manquants** : Vérifier avec `git status`
- **Credentials** : Configurer GitHub CLI ou token

---

**Date** : 2025-12-01
**Version** : V2.1
**Auteur** : Yann + Claude
**Repository** : https://github.com/yann3178/TradingEcoSystemAnalytics
