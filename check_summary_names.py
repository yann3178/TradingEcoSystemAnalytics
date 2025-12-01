#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vérifier le contenu du fichier summary
"""
import pandas as pd
from pathlib import Path

summary_file = Path("C:/TradeData/V2/outputs/monte_carlo/20251201_1130/monte_carlo_summary.csv")

if summary_file.exists():
    df = pd.read_csv(summary_file, sep=';', decimal=',', encoding='utf-8-sig')
    
    print(f"📊 Fichier: {summary_file.name}")
    print(f"Lignes: {len(df)}")
    print(f"Colonnes: {list(df.columns)}")
    print()
    
    print("Exemples de données:")
    print("=" * 100)
    for idx, row in df.head(5).iterrows():
        print(f"\nStratégie #{idx+1}:")
        print(f"  strategy_name: {row['strategy_name']}")
        print(f"  symbol: {row.get('symbol', 'N/A')}")
        
        # Essayer de trouver le fichier CSV correspondant
        run_dir = summary_file.parent
        
        # Pattern 1: symbol_strategy_mc.csv
        csv1 = run_dir / f"{row.get('symbol', '')}_{row['strategy_name']}_mc.csv"
        # Pattern 2: strategy_mc.csv
        csv2 = run_dir / f"{row['strategy_name']}_mc.csv"
        
        print(f"  Pattern 1 ({csv1.name}): {'✓ EXISTE' if csv1.exists() else '✗ N EXISTE PAS'}")
        print(f"  Pattern 2 ({csv2.name}): {'✓ EXISTE' if csv2.exists() else '✗ N EXISTE PAS'}")
else:
    print(f"❌ Fichier non trouvé: {summary_file}")
