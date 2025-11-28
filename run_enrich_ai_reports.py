#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enrichissement des Rapports AI Analysis V2
==========================================
Enrichit les rapports HTML générés par la migration V1→V2 
avec KPIs et Equity Curves.

Usage:
    python run_enrich_ai_reports.py [--no-backup] [--force]
"""

import sys
from pathlib import Path

# Ajouter le répertoire racine au path
V2_ROOT = Path(__file__).parent
sys.path.insert(0, str(V2_ROOT))

from config.settings import (
    AI_HTML_REPORTS_DIR, PORTFOLIO_REPORTS_DIR, EQUITY_CURVES_DIR,
    get_latest_portfolio_report
)

# Importer le script d'enrichissement principal
from run_enrich import HTMLEnricher, main as enrich_main

def main():
    """Enrichit les rapports AI Analysis V2."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Enrichit les rapports HTML AI Analysis V2 avec KPIs et Equity Curves"
    )
    parser.add_argument(
        "--no-backup", 
        action="store_true",
        help="Ne pas créer de backup des fichiers"
    )
    parser.add_argument(
        "--force", 
        action="store_true",
        help="Réécrire même si déjà enrichi"
    )
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("🚀 ENRICHISSEMENT DES RAPPORTS AI ANALYSIS V2")
    print("=" * 80)
    print()
    print(f"📁 Répertoire HTML: {AI_HTML_REPORTS_DIR}")
    print(f"📁 Equity Curves:   {EQUITY_CURVES_DIR}")
    print(f"📁 Portfolio Reports: {PORTFOLIO_REPORTS_DIR}")
    print()
    
    # Vérifier que le répertoire existe
    if not AI_HTML_REPORTS_DIR.exists():
        print(f"❌ Répertoire non trouvé: {AI_HTML_REPORTS_DIR}")
        print("   Lancez d'abord: python migrate_v1_analysis.py")
        return 1
    
    # Trouver le Portfolio Report le plus récent
    try:
        portfolio_report = get_latest_portfolio_report()
        print(f"📊 Portfolio Report: {portfolio_report.name}")
    except FileNotFoundError:
        portfolio_report = None
        print("⚠️  Aucun Portfolio Report trouvé - KPIs non disponibles")
    
    print()
    
    # Créer et exécuter l'enrichisseur
    enricher = HTMLEnricher(
        html_dir=AI_HTML_REPORTS_DIR,
        portfolio_report_path=portfolio_report,
        datasources_dir=EQUITY_CURVES_DIR,
        backup=not args.no_backup,
        force=args.force
    )
    
    success = enricher.run()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
