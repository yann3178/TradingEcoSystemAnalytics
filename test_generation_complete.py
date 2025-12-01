#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test complet de génération HTML Monte Carlo
"""
import sys
from pathlib import Path

# Ajouter le chemin src au PYTHONPATH
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from monte_carlo.monte_carlo_html_generator import main

if __name__ == "__main__":
    print("=" * 80)
    print("TEST GÉNÉRATION HTML MONTE CARLO")
    print("=" * 80)
    print()
    
    try:
        # Lancer la génération
        main()
        
        print("\n" + "=" * 80)
        print("✅ SUCCÈS - Génération terminée!")
        print("=" * 80)
        print()
        print("📂 Ouvrez maintenant le fichier HTML:")
        print("   C:\\TradeData\\V2\\outputs\\html_reports\\montecarlo\\all_strategies_montecarlo.html")
        print()
        print("🔍 Vérifiez dans la console du navigateur (F12) :")
        print("   - 'Strategies detailed data loaded: X strategies'")
        print("   - Pas d'erreurs JavaScript")
        print()
        
    except Exception as e:
        print("\n" + "=" * 80)
        print(f"❌ ERREUR: {e}")
        print("=" * 80)
        import traceback
        traceback.print_exc()
