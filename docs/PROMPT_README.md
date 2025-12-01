# 📋 PROMPTS POUR SESSION SUIVANTE V2.3.0

## ✅ Fichiers Créés

Les fichiers suivants ont été créés dans `C:\TradeData\V2\docs\` :

1. ✅ **NEXT_SESSION_PROMPT_QUICK.md** - Prompt rapide (100 lignes)
2. ✅ **PROMPT_USAGE_GUIDE.md** - Guide utilisation prompts
3. ✅ **GIT_PUBLISH_GUIDE.md** - Guide Git pour V2.2.0

## ⚠️ Fichier Principal Manquant

Le fichier **NEXT_SESSION_PROMPT.md** (prompt complet ~400 lignes) n'a pas pu être créé automatiquement car trop volumineux.

## 🚀 ACTION REQUISE

### Méthode 1 : Copier depuis Conversation

1. **Remonter dans cette conversation Claude**
2. **Chercher** : "PROMPT CLAUDE - TRADING ECOSYSTEM ANALYTICS V2"
3. **Copier** tout le contenu du prompt complet
4. **Créer fichier** : `C:\TradeData\V2\docs\NEXT_SESSION_PROMPT_FULL.md`
5. **Coller** le contenu

### Méthode 2 : Utiliser Version Rapide

Si tu veux démarrer rapidement :

```powershell
# Ouvrir le prompt rapide
notepad C:\TradeData\V2\docs\NEXT_SESSION_PROMPT_QUICK.md
```

Ce fichier contient l'essentiel pour démarrer.

---

## 📖 CONTENU DU PROMPT COMPLET

Le prompt complet (~400 lignes) contient :

### 1. Contexte Projet
- Objectif global
- Architecture V2.2.0
- Pipeline actuel (6 étapes : 0→0A→1→1B→2→3)

### 2. État des Lieux V2.2.0
- Composants opérationnels
- Sorties actuelles (AI, Monte Carlo, Correlation)
- Problème : **3 systèmes isolés**

### 3. Roadmap Détaillée V2.3.0

**Étape 1 : Migration Correlation Pages Generator**
- Porter `C:\TradeData\scripts\generate_correlation_pages.py` 
- Vers `C:\TradeData\V2\src\generators\correlation_pages_generator.py`
- ⚠️ Lire par sections (fichier potentiellement gros)
- Tests unitaires
- Documentation

**Étape 2 : Migration Monte Carlo Batch Generator**
- Porter `C:\TradeData\scripts\monte_carlo_simulator\batch_monte_carlo.py`
- Vers `C:\TradeData\V2\src\generators\monte_carlo_pages_generator.py`
- Générer pages HTML depuis outputs JSON
- Dashboard global MC
- Tests + docs

**Étape 3 : Intégration Tri-Système**

**3.1 - Onglet Monte Carlo dans AI Dashboard**
- Fichier : `outputs/ai_analysis/html_reports/index.html`
- Ajouter onglet "Monte Carlo Analysis"
- Pointer vers dashboard MC global

**3.2 - Bandeau Monte Carlo dans Pages Stratégies**
- Fichiers : `outputs/ai_analysis/html_reports/{StrategyName}.html`
- Ajouter sous "Performance Dashboard" :
  - Capital Minimum
  - Risque de Ruine (Année 1)
  - Probabilité de Gain (Année 1)
  - Lien vers page MC détaillée

**3.3 - Onglet Correlation dans AI Dashboard**
- Fichier : `outputs/ai_analysis/html_reports/index.html`
- Ajouter onglet "Correlation Dashboard"
- Pointer vers dernier dashboard correlation
- Auto-détection `correlation_dashboard_{LATEST}.html`

**3.4 - Bandeau Correlation dans Pages Stratégies**
- Fichiers : `outputs/ai_analysis/html_reports/{StrategyName}.html`
- Ajouter avant "Code Source" :
  - Top 15 stratégies MOINS corrélées (diversification)
  - Top 15 stratégies PLUS corrélées (redondance)
  - Lien vers dashboard correlation

**Étape 4 : Intégration Pipeline**
- Ajouter steps dans `run_pipeline.py` :
  - 2A. Monte Carlo Pages Generation
  - 3A. Correlation Pages Generation
  - 4. Dashboard Integration
- Nouveaux CLI arguments
- Tests end-to-end

**Étape 5 : Documentation**
- `docs/DASHBOARD_INTEGRATION.md` (NOUVEAU)
- `docs/CHANGELOG.md` → V2.3.0
- `docs/PROJECT_STATUS.md` → Mise à jour
- `VERSION` → 2.3.0
- Git commit + tag

### 4. Contraintes Techniques CRITIQUES

**⚠️ FICHIERS VOLUMINEUX - DANGER CRASH**

Fichiers à risque :
- `C:\TradeData\scripts\generate_correlation_pages.py`
- `C:\TradeData\scripts\monte_carlo_simulator\batch_monte_carlo.py`
- CSV consolidés (>1M lignes)

**RÈGLE ABSOLUE :**
```python
# ❌ NE JAMAIS FAIRE
content = file.read_text()  # Si > 1000 lignes

# ✅ TOUJOURS FAIRE
view(filepath, view_range=[1, 100])   # Par sections
view(filepath, view_range=[500, 600])
```

**Méthodologie :**
1. Vérifier taille : `ls -lh fichier`
2. Lire header : `view fichier --view-range [1, 50]`
3. Lire footer : `view fichier --view-range [-50, -1]`
4. Comprendre structure AVANT lecture complète
5. Parser par chunks si nécessaire

**Encodage CSV Européen :**
```python
df = pd.read_csv(
    filepath,
    sep=';',           # Point-virgule
    decimal=',',       # Virgule décimale
    encoding='utf-8-sig'
)
```

**Nommage Stratégies :**
- AI Reports : `{StrategyName}.html`
- HTML Enrichis : `{Symbol}_{StrategyName}.html`
- Monte Carlo : `{Symbol}_{Strategy}_mc.csv`

### 5. Données Disponibles

**AI Analysis Outputs :**
```
outputs/ai_analysis/
├── strategies_ai_analysis.csv
├── strategy_tracking.json
└── html_reports/
    ├── index.html
    └── {StrategyName}.html
```

**Monte Carlo Outputs :**
```
outputs/monte_carlo/{timestamp}/
├── {Symbol}_{Strategy}_mc.csv
└── monte_carlo_summary.csv
```

**Correlation Outputs :**
```
outputs/correlation/{timestamp}/
├── correlation_longterm_matrix.csv
├── correlation_shortterm_matrix.csv
├── correlation_scores.csv
└── correlation_dashboard_{timestamp}.html
```

### 6. Planning (8 jours)

- **Phase 1** : Analyse (2 jours)
- **Phase 2** : Migration (2 jours)
- **Phase 3** : Intégration (2 jours)
- **Phase 4** : Pipeline (1 jour)
- **Phase 5** : Documentation (1 jour)

### 7. Résultat Attendu

```
AI Dashboard (index.html)
├── [Strategies] [Monte Carlo] [Correlation]  ← Onglets
│
Pages Stratégies ({Strategy}.html)
├── Performance KPIs (existant)
├── Monte Carlo Banner (NOUVEAU)
│   ├── Capital Minimum
│   ├── Risque Ruine Année 1
│   ├── Proba Gain Année 1
│   └── → Lien page MC détaillée
├── Correlation Banner (NOUVEAU)
│   ├── Top 15 Peu Corrélées
│   ├── Top 15 Très Corrélées
│   └── → Lien dashboard Correlation
└── Code Source (existant)
```

---

## 🚀 UTILISATION

### Option 1 : Version Rapide (Disponible)

```powershell
notepad C:\TradeData\V2\docs\NEXT_SESSION_PROMPT_QUICK.md
```

Copier/coller dans nouvelle session Claude.

### Option 2 : Recréer Version Complète

Copier le contenu complet depuis cette conversation et créer :
```powershell
notepad C:\TradeData\V2\docs\NEXT_SESSION_PROMPT_FULL.md
```

---

## 📚 Documentation Support

- `docs/README.md` - Guide complet V2
- `docs/AI_ANALYSIS_INTEGRATION.md` - Guide AI
- `docs/CHANGELOG.md` - Historique versions
- `docs/PROJECT_STATUS.md` - État projet
- `config/settings.py` - Configuration

---

## ✅ PRÊT POUR DÉMARRAGE

Fichiers disponibles :
- [x] NEXT_SESSION_PROMPT_QUICK.md ✅
- [x] PROMPT_USAGE_GUIDE.md ✅
- [x] GIT_PUBLISH_GUIDE.md ✅
- [ ] NEXT_SESSION_PROMPT_FULL.md (à créer manuellement)

**Pour démarrer rapidement** : Utilise **NEXT_SESSION_PROMPT_QUICK.md**

---

**Version** : 2.2.0 → 2.3.0  
**Date** : 28 novembre 2025  
**Objectif** : Intégration Dashboards AI + MC + Correlation
