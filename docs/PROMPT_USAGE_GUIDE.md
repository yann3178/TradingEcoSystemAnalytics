# 📖 GUIDE UTILISATION PROMPTS - SESSION SUIVANTE

## 🎯 Quel Prompt Utiliser ?

Tu disposes de **2 versions** du prompt pour démarrer la prochaine session Claude :

---

## 📚 VERSION COMPLÈTE (RECOMMANDÉE)

**Fichier** : `NEXT_SESSION_PROMPT.md`

**Quand l'utiliser :**
- Première session sur ce projet
- Besoin de contexte complet
- Claude doit comprendre toute l'architecture
- Projet complexe avec beaucoup de détails

**Contenu :**
- ✅ Contexte projet détaillé
- ✅ Architecture complète V2.2.0
- ✅ État des lieux exhaustif
- ✅ Roadmap détaillée (étapes 1-5)
- ✅ Contraintes techniques
- ✅ Exemples de code
- ✅ Pièges à éviter
- ✅ Checklist démarrage
- ✅ Documentation références

**Taille** : ~400 lignes

**Avantages :**
- Claude comprend TOUT le contexte
- Moins de questions de clarification
- Travail plus autonome
- Meilleure qualité de sortie

**Inconvénient :**
- Long à lire (mais vaut le coup)

---

## ⚡ VERSION RAPIDE

**Fichier** : `NEXT_SESSION_PROMPT_QUICK.md`

**Quand l'utiliser :**
- Session de continuation (Claude a déjà du contexte)
- Besoin de rappel rapide
- Contrainte de tokens
- Démarrage immédiat

**Contenu :**
- ✅ Contexte condensé
- ✅ Architecture schématique
- ✅ Roadmap simplifiée
- ✅ Contraintes essentielles
- ✅ Démarrage direct

**Taille** : ~100 lignes

**Avantages :**
- Rapide à lire
- Va droit au but
- Économise tokens

**Inconvénient :**
- Peut nécessiter clarifications
- Moins de contexte

---

## 🚀 UTILISATION

### Méthode 1 : Copier-Coller Direct

```bash
# Ouvrir le fichier
notepad C:\TradeData\V2\docs\NEXT_SESSION_PROMPT.md

# Copier tout le contenu
# Coller dans nouvelle conversation Claude
```

### Méthode 2 : Upload Fichier

Dans Claude.ai :
1. Nouvelle conversation
2. Upload fichier `NEXT_SESSION_PROMPT.md`
3. Message : "J'ai uploadé le contexte projet. Peux-tu le lire et me confirmer que tu as compris l'objectif ?"

---

## 📝 TEMPLATE MESSAGE INITIAL

### Version Complète

```
Bonjour Claude,

Je travaille sur le projet Trading EcoSystem Analytics V2.

J'ai préparé un prompt complet qui décrit :
- Le contexte du projet
- L'architecture actuelle (V2.2.0)
- La roadmap pour V2.3.0 (intégration dashboards)
- Les contraintes techniques importantes

Peux-tu lire le prompt ci-dessous et me confirmer que tu as bien compris :
1. L'objectif global (intégrer AI + Monte Carlo + Correlation)
2. Les 5 étapes de la roadmap
3. Les contraintes sur les fichiers volumineux

[COLLER LE CONTENU DE NEXT_SESSION_PROMPT.md ICI]

Merci !
```

### Version Rapide

```
Bonjour Claude,

Projet Trading EcoSystem Analytics V2 - Intégration dashboards.

Contexte rapide ci-dessous. On commence par l'Étape 1 : migration de generate_correlation_pages.py.

[COLLER LE CONTENU DE NEXT_SESSION_PROMPT_QUICK.md ICI]

Prêt à commencer ?
```

---

## 🎯 RECOMMANDATION

### Pour Session Suivante Immédiate

**Utiliser VERSION COMPLÈTE** (`NEXT_SESSION_PROMPT.md`)

**Raisons :**
1. Nouvelle instance Claude (pas de contexte précédent)
2. Projet complexe avec beaucoup d'interactions
3. Besoin de comprendre toute l'architecture
4. Éviter erreurs dues à manque de contexte

### Pour Session de Continuation

Si Claude a déjà travaillé sur ce projet dans sessions précédentes :
- **Version Rapide** suffit (rappel contexte)

---

## 📂 FICHIERS DISPONIBLES

| Fichier | Usage | Taille |
|---------|-------|--------|
| `NEXT_SESSION_PROMPT.md` | Prompt complet | ~400 lignes |
| `NEXT_SESSION_PROMPT_QUICK.md` | Prompt rapide | ~100 lignes |
| `README.md` | Guide général V2 | ~1000 lignes |
| `AI_ANALYSIS_INTEGRATION.md` | Guide AI | ~200 lignes |
| `CHANGELOG.md` | Historique | ~150 lignes |

---

## ✅ CHECKLIST AVANT SESSION

Avant de démarrer nouvelle session :

- [ ] Choisi version prompt (complète ou rapide)
- [ ] Copié contenu prompt
- [ ] Préparé message initial
- [ ] Documentation accessible (`docs/`)
- [ ] Fichiers projet disponibles (`C:\TradeData\V2\`)
- [ ] Git status clean (tout commité V2.2.0)

---

## 🎓 TIPS

### Pour Meilleurs Résultats

1. **Toujours donner contexte complet en début de session**
   - Même si ça semble long
   - Claude travaillera mieux après

2. **Référencer les docs existantes**
   - "Vois docs/README.md pour architecture complète"
   - "Config dans config/settings.py"

3. **Rappeler contraintes importantes**
   - Fichiers volumineux (lire par sections)
   - Encodage CSV européen
   - Tests unitaires obligatoires

4. **Valider compréhension**
   - Demander à Claude de résumer objectif
   - Confirmer approche avant de coder

5. **Documenter au fur et à mesure**
   - Mise à jour docs après chaque étape
   - Git commit réguliers

---

## 🚨 SI PROBLÈME

**Claude ne comprend pas le contexte :**
→ Utiliser version complète du prompt

**Claude fait erreurs répétées :**
→ Re-poster les contraintes techniques du prompt

**Claude lit fichiers trop gros :**
→ Rappeler section "Fichiers Volumineux" du prompt

**Architecture pas claire :**
→ Pointer vers `docs/README.md`

---

## 📞 SUPPORT

**Documentation complète :**
- `C:\TradeData\V2\docs\README.md`

**Configuration :**
- `C:\TradeData\V2\config\settings.py`

**Pipeline actuel :**
- `C:\TradeData\V2\run_pipeline.py`

---

**Bon travail avec Claude ! 🚀**

---

**Version Guide** : 1.0  
**Date** : 28 novembre 2025  
**Projet** : Trading EcoSystem Analytics V2
