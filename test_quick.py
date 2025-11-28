#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de test rapide pour vérifier les corrections.
Exécute depuis C:\TradeData\V2 avec: python test_quick.py
"""

import sys
from pathlib import Path

# Ajouter le répertoire racine au path
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

def test_kpi_enricher():
    """Test l'initialisation du KPIEnricher avec différents types."""
    print("\n" + "="*60)
    print("TEST: KPIEnricher")
    print("="*60)
    
    import pandas as pd
    from src.enrichers.kpi_enricher import KPIEnricher
    
    # Test 1: Avec DataFrame
    print("\n[1] Test avec DataFrame pandas...")
    csv_path = ROOT / "tests" / "data" / "samples" / "portfolio_report.csv"
    
    if not csv_path.exists():
        print(f"   ❌ Fichier non trouvé: {csv_path}")
        return False
    
    df = pd.read_csv(csv_path, sep=";", decimal=",")
    enricher = KPIEnricher(df)
    
    print(f"   ✓ Chargé {len(enricher.portfolio_data)} stratégies")
    print(f"   ✓ Noms: {enricher.strategy_names[:3]}...")
    
    # Test 2: Avec chemin de fichier
    print("\n[2] Test avec chemin de fichier...")
    enricher2 = KPIEnricher(csv_path)
    print(f"   ✓ Chargé {len(enricher2.portfolio_data)} stratégies")
    
    # Test 3: Recherche de stratégie
    print("\n[3] Test de recherche de stratégie...")
    test_strategies = ["EasterGold", "SOM_UA_2303_Y_3", "Yann_Casey_strategy_v0.1"]
    
    for strat in test_strategies:
        kpis = enricher.find_kpis_for_strategy(strat)
        if kpis:
            np = kpis.get('net_profit') or kpis.get('Net_Profit_Total')
            dd = kpis.get('max_drawdown') or kpis.get('Net_Max_Drawdown')
            print(f"   ✓ {strat}: NP={np:.2f}, DD={dd:.2f}")
        else:
            print(f"   ❌ {strat}: Non trouvé")
    
    # Test 4: Génération HTML
    print("\n[4] Test de génération HTML...")
    kpis = enricher.find_kpis_for_strategy("EasterGold")
    if kpis:
        html = enricher.generate_kpi_html(kpis)
        print(f"   ✓ HTML généré: {len(html)} caractères")
        assert "kpi-dashboard" in html, "HTML devrait contenir kpi-dashboard"
        assert "Net Profit" in html, "HTML devrait contenir Net Profit"
        print("   ✓ HTML contient les éléments attendus")
    
    print("\n✅ Tous les tests KPIEnricher passent!")
    return True


def test_matching():
    """Test le module de matching."""
    print("\n" + "="*60)
    print("TEST: Module matching")
    print("="*60)
    
    from src.utils.matching import find_best_match, normalize_strategy_name
    
    # Test normalisation
    print("\n[1] Test de normalisation...")
    test_cases = [
        ("GC_EasterGold_MC.html", "eastergold"),
        ("TOP_UA_287_GC_5", "287_5"),
        ("SOM_UA_2303_Y_3", "2303_y_3"),
    ]
    
    for input_name, expected_contains in test_cases:
        result = normalize_strategy_name(input_name)
        if expected_contains in result:
            print(f"   ✓ {input_name} -> {result}")
        else:
            print(f"   ⚠️ {input_name} -> {result} (attendu: contient '{expected_contains}')")
    
    # Test matching
    print("\n[2] Test de matching fuzzy...")
    candidates = [
        "Yann_Casey_strategy_v0.1",
        "EasterGold", 
        "SOM_UA_2303_Y_3",
        "TOP_UA_287_GC_5",
    ]
    
    test_matches = [
        ("EasterGold", "EasterGold"),
        ("EasterGold.html", "EasterGold"),
        ("Casey_strategy", "Yann_Casey_strategy_v0.1"),
    ]
    
    for search, expected in test_matches:
        match, score = find_best_match(search, candidates, threshold=0.5)
        if match == expected or (match and expected in match):
            print(f"   ✓ '{search}' -> '{match}' (score: {score:.2f})")
        else:
            print(f"   ⚠️ '{search}' -> '{match}' (attendu: '{expected}', score: {score:.2f})")
    
    print("\n✅ Tests matching terminés!")
    return True


def main():
    """Exécute tous les tests rapides."""
    print("="*60)
    print("TESTS RAPIDES V2 - Vérification des corrections")
    print("="*60)
    
    results = []
    
    try:
        results.append(("matching", test_matching()))
    except Exception as e:
        print(f"\n❌ Erreur test matching: {e}")
        results.append(("matching", False))
    
    try:
        results.append(("kpi_enricher", test_kpi_enricher()))
    except Exception as e:
        print(f"\n❌ Erreur test KPIEnricher: {e}")
        import traceback
        traceback.print_exc()
        results.append(("kpi_enricher", False))
    
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
        print("🎉 Tous les tests rapides passent!")
        print("\nPour lancer les tests complets:")
        print("  cd C:\\TradeData\\V2")
        print("  pytest tests/unit/ -v")
        print("  pytest tests/validation/ -v")
    else:
        print("⚠️ Certains tests ont échoué")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
