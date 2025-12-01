#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnostic pour vérifier les fichiers CSV Monte Carlo
"""
from pathlib import Path
import pandas as pd

def diagnose_mc_files():
    """Diagnostiquer les fichiers Monte Carlo."""
    
    outputs_dir = Path("C:/TradeData/V2/outputs/monte_carlo")
    
    if not outputs_dir.exists():
        print(f"❌ Le répertoire {outputs_dir} n'existe pas")
        return
    
    # Trouver le dernier run
    run_dirs = sorted([d for d in outputs_dir.iterdir() if d.is_dir()], reverse=True)
    
    if not run_dirs:
        print("❌ Aucun run Monte Carlo trouvé")
        return
    
    latest_run = run_dirs[0]
    print(f"📁 Dernier run: {latest_run.name}")
    print()
    
    # Lister les fichiers CSV
    csv_files = list(latest_run.glob("*_mc.csv"))
    print(f"📊 {len(csv_files)} fichiers CSV trouvés")
    print()
    
    # Analyser quelques fichiers
    for i, csv_file in enumerate(csv_files[:5]):
        print(f"[{i+1}] {csv_file.name}")
        try:
            df = pd.read_csv(csv_file, comment='#')
            print(f"    ✓ {len(df)} lignes (niveaux de capital)")
            print(f"    Colonnes: {', '.join(df.columns.tolist())}")
            
            # Vérifier le contenu
            if 'Start_Equity' in df.columns:
                print(f"    Capitaux: ${df['Start_Equity'].min():.0f} - ${df['Start_Equity'].max():.0f}")
            if 'Ruin_Pct' in df.columns:
                print(f"    Ruine: {df['Ruin_Pct'].min():.1f}% - {df['Ruin_Pct'].max():.1f}%")
        except Exception as e:
            print(f"    ❌ Erreur: {e}")
        print()
    
    # Vérifier le fichier summary
    summary_file = latest_run / "summary.csv"
    if summary_file.exists():
        print("📋 Fichier summary.csv")
        df = pd.read_csv(summary_file, sep=';')
        print(f"    ✓ {len(df)} stratégies")
        print(f"    Colonnes: {', '.join(df.columns.tolist()[:5])}...")
        print()
        print("Exemple de noms de stratégies:")
        for name in df['strategy_name'].head(3):
            print(f"    - {name}")
    else:
        print("❌ Fichier summary.csv non trouvé")

if __name__ == "__main__":
    diagnose_mc_files()
