#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test rapide pour la génération HTML Monte Carlo
"""
import sys
from pathlib import Path

# Ajouter le chemin src au PYTHONPATH
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from monte_carlo.monte_carlo_html_generator import generate_html_reports

if __name__ == "__main__":
    print("=" * 80)
    print("TEST - Génération HTML Monte Carlo avec logs détaillés")
    print("=" * 80)
    
    try:
        generate_html_reports()
        print("\n" + "=" * 80)
        print("✓ SUCCÈS - Vérifiez les logs ci-dessus pour les détails")
        print("=" * 80)
    except Exception as e:
        print("\n" + "=" * 80)
        print(f"✗ ERREUR: {e}")
        print("=" * 80)
        import traceback
        traceback.print_exc()
