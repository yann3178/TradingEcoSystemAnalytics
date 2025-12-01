# 🚀 PROMPT RAPIDE - INTÉGRATION DASHBOARDS V2.3.0

## Contexte
Projet **Trading EcoSystem Analytics V2** - Pipeline d'analyse de ~800 stratégies trading.

**Version actuelle** : V2.2.0 (AI Analysis intégré)  
**Version cible** : V2.3.0 (Intégration tri-système)

## Architecture V2.2.0

```
C:\TradeData\V2\
├── run_pipeline.py (6 étapes : 0→0A→1→1B→2→3)
├── src/
│   ├── analyzers/      # AI Classification
│   ├── monte_carlo/    # Simulations MC
│   ├── consolidators/  # Correlation
│   └── generators/     # Dashboards (À COMPLÉTER)
└── outputs/
    ├── ai_analysis/html_reports/    # Rapports IA
    ├── monte_carlo/{timestamp}/     # CSV Monte Carlo
    └── correlation/{timestamp}/     # Dashboard Correlation
```

## Problème
**3 systèmes isolés** → AI, MC, Correlation ne communiquent pas

## Objectif
**Intégration complète** avec liens croisés et indicateurs partagés

## Roadmap

### 1. Migration Correlation Generator
- Porter `C:\TradeData\scripts\generate_correlation_pages.py` → `src/generators/`
- ⚠️ Fichier potentiellement gros (lire par sections)

### 2. Migration Monte Carlo Generator  
- Porter `C:\TradeData\scripts\monte_carlo_simulator\batch_monte_carlo.py` → `src/generators/`
- Générer pages HTML depuis outputs JSON

### 3. Intégration Dashboards
- 3.1: Onglet MC dans `ai_analysis/html_reports/index.html`
- 3.2: Bandeau MC dans pages stratégies (Capital min, Risque ruine, Proba gain)
- 3.3: Onglet Correlation dans AI dashboard
- 3.4: Bandeau Correlation dans pages stratégies (Top 15 peu/très corrélées)

### 4. Pipeline Integration
- Ajouter steps 2A, 3A, 4 dans `run_pipeline.py`

### 5. Documentation
- Mettre à jour docs + CHANGELOG + Git (V2.3.0)

## ⚠️ CONTRAINTES CRITIQUES

**Fichiers volumineux** :
```python
# ❌ NE JAMAIS
content = file.read_text()  # Si > 1000 lignes

# ✅ TOUJOURS
view(filepath, view_range=[1, 100])  # Par sections
```

**Encodage CSV** : `sep=';', decimal=',', encoding='utf-8-sig'`

**Nommage** :
- AI : `{StrategyName}.html`
- MC : `{Symbol}_{Strategy}_mc.csv`
- HTML enrichis : `{Symbol}_{StrategyName}.html`

## Démarrage

**Étape 1 :**
```bash
# Analyser generate_correlation_pages.py PAR SECTIONS
ls -lh C:\TradeData\scripts\generate_correlation_pages.py
view C:\TradeData\scripts\generate_correlation_pages.py --view-range [1, 50]
```

**Question pour Claude :**
"Je vais commencer par l'Étape 1 (migration correlation generator). Avant de lire le fichier complet, je vais d'abord vérifier sa taille et le lire par sections. OK ?"

## Docs Disponibles
- `docs/README.md` - Guide complet
- `docs/AI_ANALYSIS_INTEGRATION.md` - AI Analysis
- `docs/NEXT_SESSION_PROMPT.md` - Prompt détaillé (version complète)
- `config/settings.py` - Configuration

## Résultat Attendu

```
AI Dashboard (index.html)
├── [Strategies] [Monte Carlo] [Correlation]  ← Onglets
│
Pages Stratégies
├── Performance KPIs (existant)
├── Monte Carlo Banner (NOUVEAU)
│   └── Capital min | Risque | Proba → Lien page MC
├── Correlation Banner (NOUVEAU)
│   └── Top 15 peu/très corrélées → Lien dashboard
└── Code Source
```

---

**Version** : Quick Start  
**Projet** : Trading EcoSystem Analytics V2  
**V2.2.0 → V2.3.0**
