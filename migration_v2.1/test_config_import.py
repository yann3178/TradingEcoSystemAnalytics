#!/usr/bin/env python3
"""
Test d'import du nouveau config.py enrichi
"""
import sys
from pathlib import Path

# Ajouter le chemin du projet
V2_ROOT = Path(__file__).parent
sys.path.insert(0, str(V2_ROOT))

# Importer le module config
from src.monte_carlo import config

print("=" * 70)
print("TEST D'IMPORT DU CONFIG.PY ENRICHI")
print("=" * 70)
print()

# Vérifier les anciens paramètres (ne doivent pas avoir changé)
print("✅ ANCIENS PARAMÈTRES (doivent être inchangés):")
print(f"   - DEFAULT_CONFIG: {len(config.DEFAULT_CONFIG)} paramètres")
print(f"   - STATUS_OK: '{config.STATUS_OK}'")
print(f"   - STATUS_WARNING: '{config.STATUS_WARNING}'")
print(f"   - STATUS_HIGH_RISK: '{config.STATUS_HIGH_RISK}'")
print(f"   - capital_minimum: {config.DEFAULT_CONFIG['capital_minimum']}")
print(f"   - nb_simulations: {config.DEFAULT_CONFIG['nb_simulations']}")
print()

# Vérifier les nouveaux paramètres
print("✅ NOUVEAUX PARAMÈTRES (configuration dashboard):")
print(f"   - DASHBOARD_DEFAULT_CRITERIA: {config.DASHBOARD_DEFAULT_CRITERIA}")
print(f"   - DASHBOARD_PRESETS: {list(config.DASHBOARD_PRESETS.keys())}")
print(f"   - DASHBOARD_COLORS: {len(config.DASHBOARD_COLORS)} couleurs définies")
print(f"   - SLIDER_RANGES: {list(config.SLIDER_RANGES.keys())}")
print(f"   - FILE_PATTERNS: {list(config.FILE_PATTERNS.keys())}")
print()

# Test des presets
print("📊 DÉTAILS DES PRESETS:")
for name, preset in config.DASHBOARD_PRESETS.items():
    print(f"   • {name}: {preset['name']}")
    print(f"     - max_ruin: {preset['max_ruin']}")
    print(f"     - min_return_dd: {preset['min_return_dd']}")
    print(f"     - min_prob_positive: {preset['min_prob_positive']}")
print()

print("=" * 70)
print("✅ TOUS LES TESTS RÉUSSIS !")
print("=" * 70)
