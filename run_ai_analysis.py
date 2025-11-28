"""
Script d'Exécution - Analyse IA des Stratégies
==============================================
Lance l'analyse IA des stratégies MultiCharts via Claude API.

Usage:
    python run_ai_analysis.py                    # Mode delta (incrémental)
    python run_ai_analysis.py --mode full        # Ré-analyser tout
    python run_ai_analysis.py --max 10           # Limiter à 10 stratégies
    python run_ai_analysis.py --retry-errors     # Re-traiter les erreurs
    python run_ai_analysis.py --dry-run          # Test sans appel API

Version: 2.0.0
Date: 2025-11-28
"""

import argparse
import sys
from pathlib import Path
from typing import Optional, Set

# Ajouter le répertoire racine au path
V2_ROOT = Path(__file__).parent
sys.path.insert(0, str(V2_ROOT))


def run_ai_analysis(
    mode: str = "delta",
    max_strategies: int = 0,
    retry_errors: bool = False,
    from_file: Optional[Path] = None,
    dry_run: bool = False,
    generate_dashboard: bool = True,
    verbose: bool = True,
):
    """
    Exécute l'analyse IA des stratégies.
    
    Args:
        mode: "delta" (incrémental) ou "full" (tout ré-analyser)
        max_strategies: Limite le nombre (0 = toutes)
        retry_errors: Retraiter uniquement les erreurs précédentes
        from_file: Charger la liste depuis un fichier
        dry_run: Test sans appel API
        generate_dashboard: Générer le dashboard HTML
        verbose: Afficher les détails
    """
    print("\n" + "=" * 70)
    print("  🤖 AI STRATEGY ANALYZER V2")
    print("=" * 70)
    
    # Import des modules
    try:
        from src.analyzers import AIAnalyzer, AIAnalyzerConfig, HTMLReportGenerator
        from src.analyzers.code_parser import CodeParser
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("   Vérifiez que vous êtes dans le bon répertoire (C:\\TradeData\\V2)")
        return
    
    # Configuration
    config = AIAnalyzerConfig(
        mode=mode,
        max_strategies=max_strategies,
        generate_dashboard=generate_dashboard,
        verbose=verbose,
    )
    
    # Validation
    errors = config.validate()
    
    if dry_run:
        print("\n🔍 MODE DRY-RUN: Test de configuration uniquement")
        print(f"\n📂 Configuration:")
        print(f"   Mode              : {mode.upper()}")
        print(f"   Max strategies    : {max_strategies or 'Toutes'}")
        print(f"   Strategies dir    : {config.strategies_dir}")
        print(f"   Functions dir     : {config.functions_dir}")
        print(f"   Output dir        : {config.output_dir}")
        print(f"   API Key           : {'✅ Définie' if config.api_key else '❌ Manquante'}")
        print(f"   Model             : {config.model}")
        
        if errors:
            print(f"\n❌ Erreurs de configuration:")
            for e in errors:
                print(f"   • {e}")
        else:
            print("\n✅ Configuration valide")
            
            # Compter les fichiers
            parser = CodeParser(config.strategies_dir, config.functions_dir)
            files = parser.list_strategy_files()
            print(f"\n📁 {len(files)} fichiers de stratégies trouvés")
            print(f"📚 {len(parser._functions_cache)} fonctions clés chargées")
        
        return
    
    # Vérifier les erreurs critiques
    if errors:
        for e in errors:
            if "API" in e:
                print(f"\n❌ Erreur critique: {e}")
                print("   Définissez la variable d'environnement ANTHROPIC_API_KEY")
                return
    
    # Charger le scope si nécessaire
    scope: Optional[Set[str]] = None
    
    if retry_errors:
        print("\n🔄 Mode retry-errors: chargement des erreurs précédentes...")
        from src.analyzers.ai_analyzer import AnalysisTracking
        tracking = AnalysisTracking(config.tracking_file, config.analysis_version)
        scope = tracking.get_error_strategies()
        print(f"   → {len(scope)} stratégies en erreur trouvées")
        
        if not scope:
            print("   ✅ Aucune erreur à retraiter!")
            return
    
    elif from_file:
        print(f"\n📄 Chargement de la liste depuis: {from_file}")
        if not from_file.exists():
            print(f"   ❌ Fichier introuvable: {from_file}")
            return
        
        scope = set()
        with from_file.open('r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    scope.add(line)
        
        print(f"   → {len(scope)} stratégies chargées")
    
    # Lancer l'analyse
    try:
        analyzer = AIAnalyzer(config)
        results = analyzer.run(strategy_scope=scope, max_strategies=max_strategies)
        
        if not results:
            print("\n⚠️ Aucun résultat d'analyse")
            return
        
        # Exporter CSV
        csv_path = analyzer.export_csv()
        
        # Générer les rapports HTML
        if generate_dashboard:
            print("\n📝 Génération des rapports HTML...")
            
            generator = HTMLReportGenerator(config.html_reports_dir)
            
            # Générer les rapports individuels
            for result in results:
                name = result.get("strategy_name", "Unknown")
                
                # Récupérer le code source
                strategy_file = analyzer.parser.find_strategy_file(name)
                if strategy_file:
                    from src.utils.file_utils import safe_read
                    code = safe_read(strategy_file)
                else:
                    code = "// Code source non disponible"
                
                try:
                    generator.generate_strategy_report(result, code)
                except Exception as e:
                    if verbose:
                        print(f"   ⚠️ Erreur HTML {name}: {e}")
            
            # Générer le dashboard
            dashboard_path = generator.generate_dashboard(results)
            print(f"\n📊 Dashboard généré: {dashboard_path}")
        
        # Résumé final
        summary = analyzer.get_summary()
        print("\n" + "=" * 70)
        print("✅ ANALYSE TERMINÉE")
        print("=" * 70)
        print(f"   Total analysé      : {summary['total_analyzed']}")
        print(f"   Qualité moyenne    : {summary['avg_quality_score']:.1f}/10")
        print(f"   Complexité moyenne : {summary['avg_complexity_score']:.1f}/10")
        print(f"\n📂 Fichiers générés:")
        print(f"   • CSV: {csv_path}")
        if generate_dashboard:
            print(f"   • HTML: {config.html_reports_dir / 'index.html'}")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description="AI Strategy Analyzer V2 - Analyse des stratégies MultiCharts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python run_ai_analysis.py                    # Mode delta (incrémental)
  python run_ai_analysis.py --mode full        # Ré-analyser tout
  python run_ai_analysis.py --max 10           # Limiter à 10 stratégies
  python run_ai_analysis.py --retry-errors     # Re-traiter les erreurs
  python run_ai_analysis.py --dry-run          # Test sans appel API
  python run_ai_analysis.py --from-file list.txt  # Depuis un fichier
        """
    )
    
    parser.add_argument(
        '--mode', '-m',
        choices=['delta', 'full'],
        default='delta',
        help="Mode d'analyse: delta (incrémental) ou full (tout)"
    )
    
    parser.add_argument(
        '--max',
        type=int,
        default=0,
        help="Nombre maximum de stratégies (0 = toutes)"
    )
    
    parser.add_argument(
        '--retry-errors',
        action='store_true',
        help="Retraiter uniquement les stratégies en erreur"
    )
    
    parser.add_argument(
        '--from-file',
        type=str,
        help="Charger la liste des stratégies depuis un fichier"
    )
    
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help="Test sans appel API"
    )
    
    parser.add_argument(
        '--no-dashboard',
        action='store_true',
        help="Ne pas générer le dashboard HTML"
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help="Mode silencieux"
    )
    
    args = parser.parse_args()
    
    # Convertir from_file en Path
    from_file = Path(args.from_file) if args.from_file else None
    
    run_ai_analysis(
        mode=args.mode,
        max_strategies=args.max,
        retry_errors=args.retry_errors,
        from_file=from_file,
        dry_run=args.dry_run,
        generate_dashboard=not args.no_dashboard,
        verbose=not args.quiet,
    )


if __name__ == "__main__":
    main()
