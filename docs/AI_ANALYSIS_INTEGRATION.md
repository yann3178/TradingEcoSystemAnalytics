# 🤖 AI ANALYSIS - Guide d'Intégration V2.2.0

## 📋 Vue d'ensemble

AI Analysis est maintenant **intégré dans le pipeline principal** `run_pipeline.py` en tant qu'**étape 0 optionnelle**.

### ⚠️ IMPORTANT

- **Désactivé par défaut** (trop long et coûteux)
- **~40+ heures** pour analyser 800 stratégies
- **~$2.40** de coût API Claude
- **Confirmation requise** pour analyse complète

---

## 🚀 Utilisation

### Option 1 : Pipeline Complet avec AI

```bash
# Activer AI Analysis dans le pipeline
python run_pipeline.py --run-ai-analysis

# Le pipeline exécute automatiquement :
# 0.  AI Analysis (nouvelles stratégies uniquement)
# 0A. Strategy Mapping  
# 1.  KPI Enrichment
# 1B. Name Harmonization
# 2.  Monte Carlo
# 3.  Correlation
```

### Option 2 : AI Analysis Seule

```bash
# Mode delta (incrémental - recommandé)
python run_pipeline.py --step ai-analysis

# Mode full (ré-analyse tout - ATTENTION!)
python run_pipeline.py --step ai-analysis --ai-mode full

# Limiter à N stratégies (pour tests)
python run_pipeline.py --step ai-analysis --ai-max 10
```

### Option 3 : Script Standalone (Comme Avant)

```bash
# L'ancien workflow fonctionne toujours
python run_ai_analysis.py --max 10
```

---

## 📊 Paramètres CLI Complets

| Paramètre | Description | Défaut |
|-----------|-------------|--------|
| `--run-ai-analysis` | Activer AI dans pipeline complet | Désactivé |
| `--ai-mode {delta\|full}` | Mode incrémental ou complet | `delta` |
| `--ai-max N` | Limiter à N stratégies (0=toutes) | `0` |
| `--ai-retry-errors` | Retry stratégies en erreur | Désactivé |
| `--ai-from-file FILE` | Charger liste depuis fichier | `None` |
| `--ai-no-dashboard` | Ne pas générer dashboard HTML | Génère |

---

## 💡 Exemples Pratiques

### Test Rapide (5 stratégies)

```bash
python run_pipeline.py --step ai-analysis --ai-max 5
```

**Résultat :**
- Durée : ~10-15 minutes
- Coût : ~$0.015
- Rapports HTML générés dans `outputs/ai_analysis/html_reports/`

---

### Analyse Liste Spécifique

```bash
# Créer un fichier avec stratégies à analyser
echo SOM_UA_2302_G_5 > strategies.txt
echo DM_Breakout_V3 >> strategies.txt

# Analyser cette liste
python run_pipeline.py --step ai-analysis --ai-from-file strategies.txt
```

---

### Retry Erreurs Précédentes

```bash
# Retraiter uniquement les stratégies en erreur
python run_pipeline.py --step ai-analysis --ai-retry-errors
```

---

### Mode Dry-Run (Prévisualisation)

```bash
python run_pipeline.py --run-ai-analysis --dry-run
```

---

## ⚙️ Configuration

### PipelineConfig

```python
class PipelineConfig:
    # AI Analysis
    run_ai_analysis = False          # Activer/désactiver
    ai_mode = "delta"                # "delta" ou "full"
    ai_max_strategies = 0            # 0 = toutes
    ai_retry_errors = False
    ai_from_file = None
    ai_generate_dashboard = True
```

---

## 📂 Fichiers Générés

```
outputs/ai_analysis/
├── strategies_ai_analysis.csv          # Résultats analyse (CSV)
├── strategy_tracking.json              # Tracking avec hash et erreurs
└── html_reports/                       # Rapports HTML
    ├── index.html                      # Dashboard principal
    └── {StrategyName}.html             # Rapports individuels
```

---

## ⚠️ Estimation Coûts & Temps

| Nb Stratégies | Temps Estimé | Coût Estimé |
|--------------|--------------|-------------|
| 1 | 2-3 min | $0.003 |
| 10 | 25-30 min | $0.03 |
| 50 | 2-3 heures | $0.15 |
| 100 | 4-5 heures | $0.30 |
| **800 (complet)** | **40+ heures** | **$2.40** |

**Recommandation :** Toujours tester avec `--ai-max 5` d'abord !

---

## 🔍 Résultats d'Analyse

### 8 Catégories

1. **BREAKOUT** - Cassures de niveaux
2. **MEAN_REVERSION** - Retour à la moyenne
3. **TREND_FOLLOWING** - Suivi de tendance
4. **MOMENTUM** - Dynamique des prix
5. **PATTERN** - Patterns chartistes
6. **VOLATILITY** - Exploitation volatilité
7. **TIME_BASED** - Basées sur horaires
8. **HYBRID** - Approches mixtes

---

## 🆚 Comparaison : Pipeline vs Standalone

| Aspect | run_pipeline.py | run_ai_analysis.py |
|--------|----------------|-------------------|
| **Usage** | Intégré au workflow | Script séparé |
| **Commande** | `--run-ai-analysis` | Direct |
| **Étapes suivantes** | Automatiques | Manuelles |
| **Préfixe CLI** | `--ai-*` | `--*` |

---

## ✅ Checklist Avant Analyse Complète

- [ ] API Key configurée : `echo %ANTHROPIC_API_KEY%`
- [ ] Budget API disponible : ~$2.40
- [ ] Temps disponible : 40+ heures
- [ ] Backup analyses existantes
- [ ] Test sur échantillon : `--ai-max 5` réussi
- [ ] Vérifier erreurs : `strategy_tracking.json`

---

## 📞 Support & Troubleshooting

### Erreur : "API key not found"

```bash
set ANTHROPIC_API_KEY=sk-ant-...
echo %ANTHROPIC_API_KEY%
```

### Analyse Interrompue

Le mode delta reprendra où ça s'est arrêté.

---

**Version** : 2.2.0  
**Date** : 28 novembre 2025  
**Statut** : ✅ Intégration complète
