#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wrapper pour lancer le générateur de rapports HTML Monte Carlo (Version 3)

Version 3 permet de paramétrer TOUS les critères Kevin Davey:
- Risque de ruine maximum
- Return/DD minimum
- Probabilité positive minimum

Usage:
    # Défaut: seulement ruine ≤10%
    python run_monte_carlo_html_generator.py
    
    # Kevin Davey complet
    python run_monte_carlo_html_generator.py --max-ruin 10 --min-return-dd 2 --min-prob-positive 80
    
    # Conservateur
    python run_monte_carlo_html_generator.py --max-ruin 5 --min-return-dd 2.5 --min-prob-positive 85
    
    # Agressif
    python run_monte_carlo_html_generator.py --max-ruin 20 --min-return-dd 1.5 --min-prob-positive 70
"""

import sys
import os
from pathlib import Path

# Configurer l'environnement
V2_ROOT = Path(__file__).parent.absolute()
os.chdir(V2_ROOT)
sys.path.insert(0, str(V2_ROOT))

# Maintenant on peut importer
from config.settings import HTML_MONTECARLO_DIR, OUTPUT_ROOT

# Ajouter le répertoire monte_carlo au path
sys.path.insert(0, str(V2_ROOT / "src" / "monte_carlo"))

# Importer le générateur V3 (version entièrement paramétrable)
import monte_carlo_html_generator_v3 as generator

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Génère des rapports HTML Monte Carlo (version entièrement paramétrable)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:

  # Configuration par défaut (Ruine ≤10% seulement)
  python run_monte_carlo_html_generator.py

  # Kevin Davey complet
  python run_monte_carlo_html_generator.py --max-ruin 10 --min-return-dd 2.0 --min-prob-positive 80

  # Conservateur
  python run_monte_carlo_html_generator.py --max-ruin 5 --min-return-dd 2.5 --min-prob-positive 85

  # Agressif
  python run_monte_carlo_html_generator.py --max-ruin 15 --min-return-dd 1.5 --min-prob-positive 70
        """
    )
    
    parser.add_argument(
        '--run',
        type=str,
        help="Nom du run (ex: 20251201_1130). Par défaut: le plus récent"
    )
    
    parser.add_argument(
        '--max-ruin',
        type=float,
        default=10.0,
        help="Seuil de ruine maximum acceptable en %% (défaut: 10)"
    )
    
    parser.add_argument(
        '--min-return-dd',
        type=float,
        default=None,
        help="Return/DD Ratio minimum requis (défaut: aucune contrainte)"
    )
    
    parser.add_argument(
        '--min-prob-positive',
        type=float,
        default=None,
        help="Probabilité positive minimum en %% (défaut: aucune contrainte)"
    )
    
    args = parser.parse_args()
    
    run_dir = None
    if args.run:
        run_dir = OUTPUT_ROOT / "monte_carlo" / args.run
        if not run_dir.exists():
            print(f"❌ Erreur: Run introuvable: {run_dir}")
            sys.exit(1)
    
    try:
        generator.main_v3(
            run_dir, 
            args.max_ruin,
            args.min_return_dd,
            args.min_prob_positive
        )
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
