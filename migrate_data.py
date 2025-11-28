#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migration Script - Migre les données de l'ancienne structure vers V2
====================================================================
Ce script copie les fichiers nécessaires sans toucher aux originaux.

Usage:
    python migrate_data.py [--dry-run]

Version: 2.0.0
"""

import shutil
import sys
from pathlib import Path
from datetime import datetime

# Configuration
LEGACY_ROOT = Path(r"C:\TradeData")
LEGACY_MC_EXPORT = Path(r"C:\MC_Export_Code\clean")
V2_ROOT = LEGACY_ROOT / "V2"


def log(msg: str, level: str = "INFO"):
    """Affiche un message avec timestamp."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    icons = {"INFO": "ℹ️", "OK": "✅", "WARN": "⚠️", "ERROR": "❌", "COPY": "📄"}
    icon = icons.get(level, "•")
    print(f"[{timestamp}] {icon} {msg}")


def copy_file(src: Path, dst: Path, dry_run: bool = False) -> bool:
    """Copie un fichier."""
    try:
        if dry_run:
            log(f"[DRY-RUN] Would copy: {src.name} -> {dst}", "COPY")
            return True
        
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return True
    except Exception as e:
        log(f"Erreur copie {src.name}: {e}", "ERROR")
        return False


def copy_directory(src: Path, dst: Path, pattern: str = "*", dry_run: bool = False) -> int:
    """Copie tous les fichiers d'un répertoire."""
    if not src.exists():
        log(f"Source non trouvée: {src}", "WARN")
        return 0
    
    count = 0
    files = list(src.glob(pattern))
    
    for f in files:
        if f.is_file():
            if copy_file(f, dst / f.name, dry_run):
                count += 1
    
    return count


def migrate_mc_export(dry_run: bool = False) -> dict:
    """Migre le code MultiCharts exporté."""
    stats = {"strategies": 0, "functions": 0}
    
    log("Migration du code MultiCharts...")
    
    # Stratégies
    src_strategies = LEGACY_MC_EXPORT / "Strategies"
    dst_strategies = V2_ROOT / "data" / "mc_export" / "strategies"
    
    if src_strategies.exists():
        stats["strategies"] = copy_directory(src_strategies, dst_strategies, "*.txt", dry_run)
        log(f"Stratégies: {stats['strategies']} fichiers", "OK")
    
    # Fonctions
    src_functions = LEGACY_MC_EXPORT / "Functions"
    dst_functions = V2_ROOT / "data" / "mc_export" / "functions"
    
    if src_functions.exists():
        stats["functions"] = copy_directory(src_functions, dst_functions, "*.txt", dry_run)
        log(f"Fonctions: {stats['functions']} fichiers", "OK")
    
    return stats


def migrate_equity_curves(dry_run: bool = False) -> int:
    """Migre les fichiers DataSources (equity curves)."""
    log("Migration des equity curves...")
    
    src = LEGACY_ROOT / "DataSources"
    dst = V2_ROOT / "data" / "equity_curves"
    
    count = copy_directory(src, dst, "*.txt", dry_run)
    log(f"Equity curves: {count} fichiers", "OK")
    
    return count


def migrate_portfolio_reports(dry_run: bool = False) -> int:
    """Migre les derniers Portfolio Reports."""
    log("Migration des Portfolio Reports...")
    
    src = LEGACY_ROOT / "Results"
    dst = V2_ROOT / "data" / "portfolio_reports"
    
    # Ne copier que les fichiers les plus récents
    patterns = ["Portfolio_Report_V2_*.csv", "Portfolio_Report_NET_*.csv"]
    count = 0
    
    for pattern in patterns:
        files = sorted(src.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
        if files:
            # Copier seulement le plus récent de chaque type
            if copy_file(files[0], dst / files[0].name, dry_run):
                count += 1
                log(f"Portfolio Report: {files[0].name}", "COPY")
    
    log(f"Portfolio Reports: {count} fichiers", "OK")
    return count


def migrate_config_files(dry_run: bool = False) -> int:
    """Migre les fichiers de configuration."""
    log("Migration des fichiers de configuration...")
    
    count = 0
    dst = V2_ROOT / "config"
    
    # credentials.json
    for src_path in [
        LEGACY_ROOT / "scripts" / "credentials.json",
        LEGACY_ROOT / "mc_ai_analysis" / "scripts" / "credentials.json",
    ]:
        if src_path.exists():
            if copy_file(src_path, dst / "credentials.json", dry_run):
                count += 1
                break
    
    # instruments_specifications.csv
    src_instruments = LEGACY_ROOT / "Reference" / "instruments_specifications.csv"
    if src_instruments.exists():
        if copy_file(src_instruments, dst / "instruments_specifications.csv", dry_run):
            count += 1
    
    # fx_rates
    src_fx = LEGACY_ROOT / "Reference" / "fx_rates_usd_eur.csv"
    if src_fx.exists():
        if copy_file(src_fx, dst / "fx_rates_usd_eur.csv", dry_run):
            count += 1
    
    log(f"Config: {count} fichiers", "OK")
    return count


def migrate_html_reports(dry_run: bool = False) -> int:
    """Migre les rapports HTML (sans les backups)."""
    log("Migration des rapports HTML...")
    
    src = LEGACY_ROOT / "mc_ai_analysis" / "html_reports"
    dst = V2_ROOT / "outputs" / "html_reports"
    
    if not src.exists():
        log("Répertoire HTML source non trouvé", "WARN")
        return 0
    
    count = 0
    for f in src.glob("*.html"):
        # Exclure les backups et l'index (sera régénéré)
        if f.name.endswith('.bak') or f.name == 'index.html':
            continue
        
        if copy_file(f, dst / f.name, dry_run):
            count += 1
    
    log(f"Rapports HTML: {count} fichiers (sans backups)", "OK")
    return count


def migrate_csv_analysis(dry_run: bool = False) -> int:
    """Migre le CSV d'analyse IA."""
    log("Migration du CSV d'analyse...")
    
    src = LEGACY_ROOT / "mc_ai_analysis" / "strategies_ai_analysis.csv"
    dst = V2_ROOT / "outputs" / "csv" / "strategies_analysis.csv"
    
    if src.exists():
        if copy_file(src, dst, dry_run):
            log(f"CSV analyse: {src.name}", "OK")
            return 1
    
    return 0


def migrate_monte_carlo(dry_run: bool = False) -> dict:
    """Migre les résultats Monte Carlo."""
    log("Migration des résultats Monte Carlo...")
    
    stats = {"summary": 0, "details": 0, "html_global": 0, "individual": 0}
    
    src_mc = LEGACY_ROOT / "Results" / "MonteCarlo"
    dst_mc = V2_ROOT / "outputs" / "monte_carlo"
    
    if not src_mc.exists():
        log("Répertoire Monte Carlo non trouvé", "WARN")
        return stats
    
    # Fichiers globaux (CSV et HTML)
    for pattern, key in [("MC_Summary_*.csv", "summary"), ("MC_Details_*.csv", "details")]:
        files = sorted(src_mc.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
        if files:
            if copy_file(files[0], dst_mc / files[0].name, dry_run):
                stats[key] = 1
                log(f"MC {key}: {files[0].name}", "COPY")
    
    # HTML global (le plus récent + latest)
    html_files = sorted(src_mc.glob("MC_Report_*.html"), key=lambda p: p.stat().st_mtime, reverse=True)
    for hf in html_files[:2]:  # Les 2 plus récents
        if copy_file(hf, dst_mc / hf.name, dry_run):
            stats["html_global"] += 1
    
    # Fichiers individuels
    src_indiv = src_mc / "Individual"
    dst_indiv = dst_mc / "Individual"
    
    if src_indiv.exists():
        for f in src_indiv.glob("*_MC.html"):
            if copy_file(f, dst_indiv / f.name, dry_run):
                stats["individual"] += 1
        for f in src_indiv.glob("*_MC.csv"):
            if copy_file(f, dst_indiv / f.name, dry_run):
                pass  # Compté avec HTML
    
    log(f"Monte Carlo: {stats['summary']} summary, {stats['individual']} individuels", "OK")
    return stats


def migrate_correlation(dry_run: bool = False) -> int:
    """Migre les résultats de corrélation."""
    log("Migration des résultats Corrélation...")
    
    src_corr = LEGACY_ROOT / "Results" / "Correlation"
    dst_corr = V2_ROOT / "outputs" / "correlation"
    
    count = 0
    if src_corr.exists():
        for f in src_corr.glob("*.html"):
            if copy_file(f, dst_corr / f.name, dry_run):
                count += 1
        for f in src_corr.glob("*.csv"):
            if copy_file(f, dst_corr / f.name, dry_run):
                count += 1
    
    log(f"Corrélation: {count} fichiers", "OK")
    return count


def main():
    """Point d'entrée principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migre les données vers V2")
    parser.add_argument("--dry-run", action="store_true", help="Simulation sans copie")
    args = parser.parse_args()
    
    dry_run = args.dry_run
    
    print("=" * 80)
    print("🚀 MIGRATION DES DONNÉES VERS V2")
    if dry_run:
        print("   ⚠️  MODE SIMULATION (aucune copie effectuée)")
    print("=" * 80)
    print()
    
    stats = {
        "mc_export": {},
        "equity_curves": 0,
        "portfolio_reports": 0,
        "config": 0,
        "html_reports": 0,
        "csv": 0
    }
    
    # Exécuter les migrations
    stats["mc_export"] = migrate_mc_export(dry_run)
    print()
    
    stats["equity_curves"] = migrate_equity_curves(dry_run)
    print()
    
    stats["portfolio_reports"] = migrate_portfolio_reports(dry_run)
    print()
    
    stats["config"] = migrate_config_files(dry_run)
    print()
    
    stats["html_reports"] = migrate_html_reports(dry_run)
    print()
    
    stats["csv"] = migrate_csv_analysis(dry_run)
    print()
    
    stats["monte_carlo"] = migrate_monte_carlo(dry_run)
    print()
    
    stats["correlation"] = migrate_correlation(dry_run)
    print()
    
    # Rapport final
    print("=" * 80)
    print("📊 RAPPORT DE MIGRATION")
    print("=" * 80)
    print(f"   Code MC (strategies):   {stats['mc_export'].get('strategies', 0)}")
    print(f"   Code MC (functions):    {stats['mc_export'].get('functions', 0)}")
    print(f"   Equity curves:          {stats['equity_curves']}")
    print(f"   Portfolio Reports:      {stats['portfolio_reports']}")
    print(f"   Config:                 {stats['config']}")
    print(f"   Rapports HTML:          {stats['html_reports']}")
    print(f"   CSV analyse:            {stats['csv']}")
    mc_stats = stats.get('monte_carlo', {})
    print(f"   Monte Carlo (indiv):    {mc_stats.get('individual', 0)}")
    print(f"   Corrélation:            {stats.get('correlation', 0)}")
    print()
    
    total = (
        stats["mc_export"].get("strategies", 0) +
        stats["mc_export"].get("functions", 0) +
        stats["equity_curves"] +
        stats["portfolio_reports"] +
        stats["config"] +
        stats["html_reports"] +
        stats["csv"] +
        stats.get("monte_carlo", {}).get("individual", 0) +
        stats.get("correlation", 0)
    )
    
    print(f"   TOTAL:                  {total} fichiers")
    print()
    
    if dry_run:
        print("💡 Relancez sans --dry-run pour effectuer la migration")
    else:
        print(f"✅ Migration terminée vers: {V2_ROOT}")
    
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
