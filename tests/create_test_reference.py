# -*- coding: utf-8 -*-
"""
Script pour créer les données de référence V1 pour les tests.

À exécuter UNE FOIS quand la V1 est stable pour créer les fichiers
de référence utilisés par les tests de régression.

Usage:
    python create_test_reference.py
"""

import pandas as pd
from pathlib import Path
import shutil

# Chemins
V1_ROOT = Path(r"C:\TradeData")
TEST_DIR = Path(r"C:\TradeData\V2\tests\data")

# Stratégies échantillon (représentatives)
SAMPLE_STRATEGIES = [
    # TOP_UA
    "TOP_UA_287_GC_5",
    "TOP_UA_556_ES_15",
    "TOP_UA_152_NQ_5",
    "TOP_UA_228_FDAX_30",
    # SOM_UA
    "SOM_UA_2303_Y_3",
    "SOM_UA_2305_G_1",
    "SOM_UA_2311_G_1",
    "SOM_UA_2302_G_1",
    # Custom
    "EasterGold",
    "Casey_strategy_v0.1",
]

# Mapping avec symboles pour fichiers MC
STRATEGY_SYMBOLS = {
    "TOP_UA_287_GC_5": "GC",
    "TOP_UA_556_ES_15": "ES",
    "TOP_UA_152_NQ_5": "NQ",
    "TOP_UA_228_FDAX_30": "FDAX",
    "SOM_UA_2303_Y_3": "ES",
    "SOM_UA_2305_G_1": "GC",
    "SOM_UA_2311_G_1": "GC",
    "SOM_UA_2302_G_1": "FDAX",
    "EasterGold": "GC",
    "Casey_strategy_v0.1": "ES",
}


def create_directories():
    """Crée la structure de répertoires pour les tests."""
    dirs = [
        TEST_DIR / "samples" / "strategies",
        TEST_DIR / "samples" / "equity_curves",
        TEST_DIR / "samples" / "trades",
        TEST_DIR / "expected" / "v1_kpis",
        TEST_DIR / "expected" / "v1_monte_carlo",
        TEST_DIR / "expected" / "v1_correlation",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
    print(f"✓ Répertoires créés dans {TEST_DIR}")


def extract_portfolio_report_sample():
    """Extrait un sous-ensemble du Portfolio Report."""
    # Trouver le fichier le plus récent
    pr_files = list((V1_ROOT / "Results").glob("Portfolio_Report_V2_*.csv"))
    if not pr_files:
        print("⚠ Portfolio Report non trouvé")
        return
    
    pr_file = max(pr_files, key=lambda p: p.stat().st_mtime)
    print(f"  Source: {pr_file.name}")
    
    pr = pd.read_csv(pr_file, sep=";", decimal=",")
    
    # Filtrer par stratégies échantillon
    sample = pr[pr["Strategy"].str.contains("|".join(SAMPLE_STRATEGIES), na=False, case=False)]
    
    if len(sample) == 0:
        print(f"⚠ Aucune stratégie trouvée dans Portfolio Report")
        # Prendre les 50 premières lignes comme fallback
        sample = pr.head(50)
    
    output_file = TEST_DIR / "samples" / "portfolio_report.csv"
    sample.to_csv(output_file, sep=";", index=False)
    print(f"✓ Portfolio Report: {len(sample)} lignes → {output_file.name}")


def extract_mc_results():
    """Extrait les résultats Monte Carlo pour les stratégies test."""
    mc_dir = V1_ROOT / "Results" / "MonteCarlo"
    
    if not mc_dir.exists():
        print("⚠ Répertoire Monte Carlo non trouvé")
        return
    
    # Trouver le fichier Summary le plus récent
    summary_files = list(mc_dir.glob("MC_Summary_*.csv"))
    if not summary_files:
        print("⚠ MC_Summary non trouvé")
        return
    
    summary_file = max(summary_files, key=lambda p: p.stat().st_mtime)
    print(f"  Source: {summary_file.name}")
    
    mc_summary = pd.read_csv(summary_file, sep=";", decimal=",")
    
    # Filtrer par stratégies échantillon
    sample = mc_summary[mc_summary["Strategy_Name"].str.contains(
        "|".join(SAMPLE_STRATEGIES), na=False, case=False
    )]
    
    if len(sample) == 0:
        print(f"⚠ Aucune stratégie trouvée dans MC Summary")
        sample = mc_summary.head(20)
    
    output_file = TEST_DIR / "expected" / "v1_monte_carlo" / "mc_summary.csv"
    sample.to_csv(output_file, sep=";", index=False)
    print(f"✓ MC Summary: {len(sample)} stratégies → {output_file.name}")


def extract_kpis_reference():
    """
    Extrait les KPIs de référence depuis le Portfolio Report.
    Ces valeurs serviront de référence pour les tests de régression.
    """
    pr_file = TEST_DIR / "samples" / "portfolio_report.csv"
    if not pr_file.exists():
        print("⚠ Portfolio Report échantillon non trouvé")
        return
    
    pr = pd.read_csv(pr_file, sep=";", decimal=",")
    
    # Extraire les colonnes KPI pertinentes
    kpi_columns = [
        "Strategy", "Net Profit", "Max Drawdown", "Max Drawdown %",
        "Total Trades", "Avg Trade", "Profit Factor", "Sharpe Ratio"
    ]
    
    # Filtrer les colonnes existantes
    available_columns = [c for c in kpi_columns if c in pr.columns]
    kpis = pr[available_columns].copy()
    
    # Renommer pour cohérence
    kpis = kpis.rename(columns={
        "Strategy": "Strategy_Name",
        "Net Profit": "Net_Profit",
        "Max Drawdown": "Max_Drawdown",
        "Max Drawdown %": "Max_Drawdown_Pct",
        "Total Trades": "Total_Trades",
        "Avg Trade": "Avg_Trade",
        "Profit Factor": "Profit_Factor",
        "Sharpe Ratio": "Sharpe_Ratio",
    })
    
    output_file = TEST_DIR / "expected" / "v1_kpis" / "kpis_reference.csv"
    kpis.to_csv(output_file, sep=";", index=False)
    print(f"✓ KPIs référence: {len(kpis)} entrées → {output_file.name}")


def extract_equity_curves():
    """Copie quelques equity curves pour les tests."""
    eq_src = V1_ROOT / "DataSources"
    eq_dst = TEST_DIR / "samples" / "equity_curves"
    
    if not eq_src.exists():
        print("⚠ Répertoire DataSources non trouvé")
        return
    
    count = 0
    for strategy in SAMPLE_STRATEGIES:
        symbol = STRATEGY_SYMBOLS.get(strategy, "")
        # Chercher le fichier DataSource
        patterns = [
            f"DataSource_{symbol}_{strategy}*.txt",
            f"DataSource_{strategy}*.txt",
            f"*{strategy}*.txt",
        ]
        
        found = False
        for pattern in patterns:
            files = list(eq_src.glob(pattern))
            if files:
                src_file = files[0]
                dst_file = eq_dst / src_file.name
                shutil.copy2(src_file, dst_file)
                count += 1
                found = True
                break
        
        if not found:
            print(f"  ⚠ Equity curve non trouvée: {strategy}")
    
    print(f"✓ Equity curves: {count} fichiers copiés")


def extract_strategy_code():
    """Copie quelques fichiers de code stratégie pour les tests."""
    code_src = V1_ROOT / "MC_Export_Code" / "clean" / "Strategies"
    code_dst = TEST_DIR / "samples" / "strategies"
    
    if not code_src.exists():
        # Essayer l'autre emplacement
        code_src = Path(r"C:\MC_Export_Code\clean\Strategies")
    
    if not code_src.exists():
        print("⚠ Répertoire Strategies non trouvé")
        return
    
    count = 0
    for strategy in SAMPLE_STRATEGIES[:5]:  # Limiter à 5
        patterns = [f"*{strategy}*.txt", f"*{strategy.replace('_', '')}*.txt"]
        
        found = False
        for pattern in patterns:
            files = list(code_src.glob(pattern))
            if files:
                src_file = files[0]
                dst_file = code_dst / src_file.name
                shutil.copy2(src_file, dst_file)
                count += 1
                found = True
                break
    
    print(f"✓ Code stratégies: {count} fichiers copiés")


def main():
    """Point d'entrée principal."""
    print("=" * 60)
    print("CRÉATION DES DONNÉES DE RÉFÉRENCE POUR LES TESTS")
    print("=" * 60)
    print()
    
    print("📁 Création des répertoires...")
    create_directories()
    print()
    
    print("📊 Extraction Portfolio Report...")
    extract_portfolio_report_sample()
    print()
    
    print("🎲 Extraction résultats Monte Carlo...")
    extract_mc_results()
    print()
    
    print("📈 Extraction KPIs de référence...")
    extract_kpis_reference()
    print()
    
    print("📉 Extraction equity curves...")
    extract_equity_curves()
    print()
    
    print("📝 Extraction code stratégies...")
    extract_strategy_code()
    print()
    
    print("=" * 60)
    print("✅ DONNÉES DE RÉFÉRENCE CRÉÉES")
    print("=" * 60)
    print(f"📍 Emplacement: {TEST_DIR}")
    print()
    print("Pour exécuter les tests:")
    print("  cd C:\\TradeData\\V2")
    print("  pytest tests/ -v")


if __name__ == "__main__":
    main()
