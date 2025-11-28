#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de test rapide pour le module Monte Carlo V2.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))


def test_monte_carlo_imports():
    """Test les imports du module Monte Carlo."""
    print("\n" + "="*60)
    print("TEST: Imports Monte Carlo")
    print("="*60)
    
    try:
        from src.monte_carlo import (
            DEFAULT_CONFIG,
            STATUS_OK,
            STATUS_WARNING,
            STATUS_HIGH_RISK,
            MonteCarloSimulator,
        )
        print("   ✓ Tous les imports réussis")
        
        print(f"\n   Config par défaut:")
        print(f"      capital_minimum: ${DEFAULT_CONFIG['capital_minimum']:,}")
        print(f"      nb_simulations: {DEFAULT_CONFIG['nb_simulations']:,}")
        print(f"      max_acceptable_ruin: {DEFAULT_CONFIG['max_acceptable_ruin']*100}%")
        print(f"      min_return_dd_ratio: {DEFAULT_CONFIG['min_return_dd_ratio']}")
        
        print(f"\n   Statuts disponibles: {STATUS_OK}, {STATUS_WARNING}, {STATUS_HIGH_RISK}")
        
        return True
    except ImportError as e:
        print(f"   ❌ Erreur d'import: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_loader():
    """Test le data loader."""
    print("\n" + "="*60)
    print("TEST: Data Loader")
    print("="*60)
    
    try:
        from src.monte_carlo.data_loader import (
            detect_file_format,
            load_extracted_trades_file,
            calculate_trades_stats,
        )
        print("   ✓ Imports data_loader réussis")
        
        # Test avec fichier de référence MC existant
        mc_ref_path = ROOT / "tests" / "data" / "expected" / "v1_monte_carlo" / "mc_summary.csv"
        if mc_ref_path.exists():
            format_detected = detect_file_format(str(mc_ref_path))
            print(f"   ✓ Format détecté pour mc_summary.csv: {format_detected}")
        
        return True
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Exécute tous les tests Monte Carlo."""
    print("="*60)
    print("TESTS MONTE CARLO V2")
    print("="*60)
    
    results = []
    
    results.append(("imports", test_monte_carlo_imports()))
    results.append(("data_loader", test_data_loader()))
    
    # Résumé
    print("\n" + "="*60)
    print("RÉSUMÉ")
    print("="*60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {name}")
        all_passed = all_passed and passed
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 Module Monte Carlo V2 correctement porté!")
    else:
        print("⚠️ Certains tests ont échoué")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
