#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de test rapide pour le module Corrélation V2.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))


def test_correlation_imports():
    """Test les imports du module Corrélation."""
    print("\n" + "="*60)
    print("TEST: Imports Corrélation")
    print("="*60)
    
    try:
        from src.consolidators import (
            DEFAULT_CONFIG,
            SCORE_THRESHOLDS,
            CorrelationAnalyzer,
            build_profit_matrix,
            calculate_correlation_matrix,
            calculate_davey_scores,
            get_correlation_status,
        )
        print("   ✓ Tous les imports réussis")
        
        print(f"\n   Config par défaut:")
        print(f"      start_year_longterm: {DEFAULT_CONFIG['start_year_longterm']}")
        print(f"      recent_months: {DEFAULT_CONFIG['recent_months']}")
        print(f"      correlation_threshold: {DEFAULT_CONFIG['correlation_threshold']}")
        print(f"      weight_longterm: {DEFAULT_CONFIG['weight_longterm']}")
        print(f"      weight_recent: {DEFAULT_CONFIG['weight_recent']}")
        
        print(f"\n   Seuils de score: {SCORE_THRESHOLDS}")
        
        return True
    except ImportError as e:
        print(f"   ❌ Erreur d'import: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_status_function():
    """Test la fonction de statut."""
    print("\n" + "="*60)
    print("TEST: Fonction get_correlation_status")
    print("="*60)
    
    try:
        from src.consolidators.config import get_correlation_status
        
        test_cases = [
            (0.5, "Diversifiant", "🟢"),
            (3.0, "Modéré", "🟡"),
            (7.0, "Corrélé", "🟠"),
            (15.0, "Très corrélé", "🔴"),
        ]
        
        all_passed = True
        for score, expected_status, expected_emoji in test_cases:
            status, emoji = get_correlation_status(score)
            if status == expected_status and emoji == expected_emoji:
                print(f"   ✓ Score {score} → {emoji} {status}")
            else:
                print(f"   ❌ Score {score} → attendu {expected_emoji} {expected_status}, obtenu {emoji} {status}")
                all_passed = False
        
        return all_passed
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False


def test_build_profit_matrix():
    """Test la construction de matrice de profit."""
    print("\n" + "="*60)
    print("TEST: build_profit_matrix")
    print("="*60)
    
    try:
        import pandas as pd
        from src.consolidators import build_profit_matrix
        
        # Créer des données de test
        data = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=10),
            'Strategy_ID': ['A'] * 5 + ['B'] * 5,
            'DailyProfit': [100, -50, 200, 0, 150, 50, -100, 300, -200, 100]
        })
        
        matrix = build_profit_matrix(data)
        
        print(f"   ✓ Matrice construite: {matrix.shape}")
        print(f"   ✓ Colonnes: {list(matrix.columns)}")
        print(f"   ✓ Période: {matrix.index.min()} → {matrix.index.max()}")
        
        return True
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_correlation_calculation():
    """Test le calcul de corrélation."""
    print("\n" + "="*60)
    print("TEST: calculate_correlation_matrix")
    print("="*60)
    
    try:
        import pandas as pd
        import numpy as np
        from src.consolidators import calculate_correlation_matrix
        
        # Créer une matrice de test
        np.random.seed(42)
        dates = pd.date_range('2024-01-01', periods=100)
        matrix = pd.DataFrame({
            'A': np.random.randn(100),
            'B': np.random.randn(100),
            'C': np.random.randn(100),
        }, index=dates)
        
        corr, common_days = calculate_correlation_matrix(matrix, min_common_days=10)
        
        print(f"   ✓ Matrice de corrélation: {corr.shape}")
        print(f"   ✓ Diagonale = 1.0: {corr.loc['A', 'A'] == 1.0}")
        print(f"   ✓ Symétrique: {corr.loc['A', 'B'] == corr.loc['B', 'A']}")
        print(f"   ✓ Corr A-B: {corr.loc['A', 'B']:.3f}")
        print(f"   ✓ Corr A-C: {corr.loc['A', 'C']:.3f}")
        print(f"   ✓ Corr B-C: {corr.loc['B', 'C']:.3f}")
        
        return True
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Exécute tous les tests de corrélation."""
    print("="*60)
    print("TESTS CORRÉLATION V2")
    print("="*60)
    
    results = []
    
    results.append(("imports", test_correlation_imports()))
    results.append(("status_function", test_status_function()))
    results.append(("build_matrix", test_build_profit_matrix()))
    results.append(("correlation_calc", test_correlation_calculation()))
    
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
        print("🎉 Module Corrélation V2 correctement porté!")
    else:
        print("⚠️ Certains tests ont échoué")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
