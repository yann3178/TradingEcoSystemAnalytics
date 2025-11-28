# PROMPT POUR NOUVELLE SESSION - Trading EcoSystem Analytics V2

## Contexte

Je développe un système d'analyse automatisée de stratégies de trading algorithmique MultiCharts. Le projet est structuré dans `C:\TradeData\V2\` avec une architecture modulaire Python.

## État Actuel (Session 4 - 28/11/2025)

### ✅ Terminé
1. **Architecture V2** complète avec modules: analyzers, enrichers, consolidators, generators, monte_carlo, utils
2. **Migration V1→V2**: 281 stratégies analysées par IA migrées depuis l'ancien système
3. **HTML générés**: 281 fichiers HTML créés avec dashboard index.html
4. **Catégorisation**: 8 types standardisés (BREAKOUT, MEAN_REVERSION, TREND_FOLLOWING, PATTERN_PURE, VOLATILITY, BIAS_TEMPORAL, GAP_TRADING, HYBRID)
5. **Données disponibles**: 241 equity curves, Portfolio Report V2 avec KPIs

### 🔄 À Faire Maintenant
1. **Enrichir les rapports AI Analysis V2** avec KPIs et equity curves:
   ```powershell
   cd C:\TradeData\V2
   python run_enrich_ai_reports.py --force
   ```

2. **Analyser les ~550 stratégies restantes** (total ~800)

## Fichiers Clés

```
C:\TradeData\V2\
├── config/settings.py              # Configuration centralisée
├── run_enrich_ai_reports.py        # Script enrichissement AI Reports
├── migrate_v1_analysis.py          # Migration V1→V2 (terminé)
├── run_ai_analysis.py              # Analyse IA nouvelles stratégies
├── outputs/ai_analysis/
│   ├── html_reports/               # 281 HTML générés
│   ├── strategies_ai_analysis.csv  # 281 stratégies
│   └── strategy_tracking.json      # Tracking avec code_hash
├── data/
│   ├── equity_curves/              # 241 fichiers
│   └── portfolio_reports/          # Portfolio_Report_V2_27112025.csv
└── docs/PROJECT_STATUS.md          # Point d'avancement détaillé
```

## Prochaine Action Prioritaire

Lancer l'enrichissement des 281 rapports AI Analysis V2:
```powershell
cd C:\TradeData\V2
python run_enrich_ai_reports.py --force
```

Cela ajoutera:
- KPIs depuis le Portfolio Report
- Equity curves interactives avec Chart.js
- Distinction IS/OOS dans les graphiques

## Demande

[INSÉRER ICI TA DEMANDE SPÉCIFIQUE]

Exemples de demandes possibles:
- "Lance l'enrichissement des rapports HTML AI Analysis"
- "Prépare l'analyse des 550 stratégies restantes"
- "Configure le Cloudflare Tunnel permanent"
- "Génère les matrices de corrélation sur le dataset complet"
- "Montre-moi l'état du système et vérifie que tout fonctionne"

## Notes Techniques

- **API Claude**: modèle `claude-sonnet-4-20250514`, ~$0.003/stratégie
- **Matching**: Levenshtein avec seuil 80%, normalisation noms (hex decode, prefixes)
- **Corrélation**: Pearson + R² Kevin Davey (rolling 30/90/180 jours)
- **Chart.js**: Injection equity curves IS/OOS dans rapports HTML
