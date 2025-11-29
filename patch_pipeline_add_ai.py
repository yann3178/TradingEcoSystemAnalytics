"""
Script pour ajouter AI Analysis au pipeline V2.1.1 → V2.2.0

Ce script modifie run_pipeline.py pour ajouter l'étape 0 AI Analysis.
"""

import re
from pathlib import Path

def patch_pipeline():
    """Applique le patch pour AI Analysis."""
    
    # Chemin du fichier
    pipeline_file = Path("C:/TradeData/V2/run_pipeline.py")
    
    if not pipeline_file.exists():
        print(f"❌ Fichier introuvable: {pipeline_file}")
        return False
    
    # Backup
    backup_file = pipeline_file.with_suffix(".py.v2.1.1.bak")
    if not backup_file.exists():
        import shutil
        shutil.copy2(pipeline_file, backup_file)
        print(f"✅ Backup créé: {backup_file}")
    
    # Lire le contenu
    content = pipeline_file.read_text(encoding='utf-8')
    
    # 1. Modifier le header
    content = content.replace(
        """Pipeline Unifié - Trading Strategy Analysis V2
==============================================
Script principal qui orchestre l'ensemble du pipeline d'analyse:
0. Preprocessing (Strategy Mapping + Name Harmonization)
1. Enrichissement HTML avec KPIs du Portfolio Report
2. Simulation Monte Carlo (méthode Kevin Davey)
3. Analyse de corrélation Long Terme / Court Terme

Usage:
    python run_pipeline.py                    # Exécute tout le pipeline
    python run_pipeline.py --step enrich      # Enrichissement KPI uniquement
    python run_pipeline.py --step montecarlo  # Monte Carlo uniquement
    python run_pipeline.py --step correlation # Corrélation uniquement
    python run_pipeline.py --dry-run          # Affiche ce qui serait fait
    python run_pipeline.py --skip-preprocessing  # Sauter mapping + harmonization

Version: 2.1.1
Date: 2025-11-28""",
        """Pipeline Unifié - Trading Strategy Analysis V2
==============================================
Script principal qui orchestre l'ensemble du pipeline d'analyse:
0. AI Analysis (Classification stratégies - optionnel)
0A. Preprocessing (Strategy Mapping + Name Harmonization)
1. Enrichissement HTML avec KPIs du Portfolio Report
2. Simulation Monte Carlo (méthode Kevin Davey)
3. Analyse de corrélation Long Terme / Court Terme

Usage:
    python run_pipeline.py                    # Exécute tout le pipeline (sans AI)
    python run_pipeline.py --run-ai-analysis  # Avec AI Analysis (long!)
    python run_pipeline.py --step ai-analysis # AI Analysis seule
    python run_pipeline.py --step enrich      # Enrichissement KPI uniquement
    python run_pipeline.py --step montecarlo  # Monte Carlo uniquement
    python run_pipeline.py --step correlation # Corrélation uniquement
    python run_pipeline.py --dry-run          # Affiche ce qui serait fait
    python run_pipeline.py --skip-preprocessing  # Sauter mapping + harmonization

Version: 2.2.0
Date: 2025-11-28"""
    )
    
    # 2. Modifier PipelineConfig __init__
    old_config = """    def __init__(self):
        # Preprocessing
        self.run_preprocessing = True  # Strategy Mapping + Name Harmonization
        
        # Étapes à exécuter
        self.run_enrich = True
        self.run_monte_carlo = True
        self.run_correlation = True"""
    
    new_config = """    def __init__(self):
        # AI Analysis (optionnel - coûteux en temps et API)
        self.run_ai_analysis = False  # Désactivé par défaut
        self.ai_mode = "delta"  # "delta" (incrémental) ou "full" (tout ré-analyser)
        self.ai_max_strategies = 0  # 0 = toutes
        self.ai_retry_errors = False  # Retry uniquement les erreurs
        self.ai_from_file = None  # Charger liste depuis fichier
        self.ai_generate_dashboard = True  # Générer dashboard HTML
        
        # Preprocessing
        self.run_preprocessing = True  # Strategy Mapping + Name Harmonization
        
        # Étapes à exécuter
        self.run_enrich = True
        self.run_monte_carlo = True
        self.run_correlation = True"""
    
    content = content.replace(old_config, new_config)
    
    # 3. Ajouter la fonction step_0_ai_analysis AVANT step_0a_mapping
    ai_analysis_function = '''

# =============================================================================
# ÉTAPE 0: AI ANALYSIS (OPTIONNEL)
# =============================================================================

def step_0_ai_analysis(config: PipelineConfig) -> Dict[str, Any]:
    """
    Étape 0: Analyse IA des stratégies avec Claude API (OPTIONNEL).
    
    ⚠️  ATTENTION: Étape longue et coûteuse!
    - Temps: ~2-3 min par stratégie (rate limiting API)
    - Coût: ~$0.003 par stratégie
    - Pour 800 stratégies: ~40 heures + $2.40
    
    Returns:
        Dict avec statistiques de l'étape
    """
    print("\\n" + "=" * 70)
    print("🤖 ÉTAPE 0: AI ANALYSIS (Claude API)")
    print("=" * 70)
    print("⚠️  Attention: Processus long et coûteux!")
    
    result = {
        'step': 'ai_analysis',
        'success': False,
        'analyzed': 0,
        'skipped': 0,
        'errors': 0,
        'duration_seconds': 0
    }
    
    start_time = time.time()
    
    try:
        # Import du module run_ai_analysis
        from run_ai_analysis import run_ai_analysis
        
        if config.dry_run:
            print("\\n🔍 Mode dry-run: aucune analyse")
            print(f"   Mode       : {config.ai_mode}")
            print(f"   Max        : {config.ai_max_strategies or 'Toutes'}")
            print(f"   Retry errors: {config.ai_retry_errors}")
            print(f"   From file  : {config.ai_from_file or 'Non'}")
            print(f"   Dashboard  : {'Non' if not config.ai_generate_dashboard else 'Oui'}")
            result['success'] = True
            return result
        
        # Vérifier si budget API acceptable
        if config.ai_max_strategies == 0 and not config.ai_retry_errors:
            print("\\n⚠️  ATTENTION: Analyse COMPLÈTE demandée!")
            print(f"   Estimation temps: ~40+ heures")
            print(f"   Estimation coût : ~$2.40 (API Claude)")
            
            # Demander confirmation
            response = input("\\n   Continuer? [y/N]: ").strip().lower()
            if response != 'y':
                print("   Analyse annulée par l'utilisateur")
                result['success'] = True
                result['skipped'] = 1
                return result
        
        print(f"\\n🚀 Lancement de l'analyse IA...")
        print(f"   Mode       : {config.ai_mode.upper()}")
        print(f"   Max        : {config.ai_max_strategies or 'Toutes'}")
        print(f"   From file  : {config.ai_from_file or 'Non'}")
        print(f"   Dashboard  : {'Oui' if config.ai_generate_dashboard else 'Non'}")
        
        # Préparer from_file
        from_file_path = None
        if config.ai_from_file:
            from_file_path = Path(config.ai_from_file)
            if not from_file_path.exists():
                print(f"   ⚠️  Fichier introuvable: {from_file_path}")
                from_file_path = None
        
        # Exécuter l'analyse
        run_ai_analysis(
            mode=config.ai_mode,
            max_strategies=config.ai_max_strategies,
            retry_errors=config.ai_retry_errors,
            from_file=from_file_path,
            dry_run=False,
            generate_dashboard=config.ai_generate_dashboard,
            verbose=config.verbose,
        )
        
        # Lire les résultats pour stats
        analysis_csv = OUTPUT_ROOT / "ai_analysis" / "strategies_ai_analysis.csv"
        if analysis_csv.exists():
            import pandas as pd
            df = pd.read_csv(analysis_csv, sep=';', encoding='utf-8')
            result['analyzed'] = len(df)
        
        result['success'] = True
        print(f"\\n✅ AI Analysis terminée")
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("   Vérifiez que run_ai_analysis.py et src/analyzers/ existent")
        result['errors'] += 1
    except KeyboardInterrupt:
        print(f"\\n⚠️  Analyse interrompue par l'utilisateur")
        result['errors'] += 1
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        result['errors'] += 1
    
    result['duration_seconds'] = round(time.time() - start_time, 1)
    
    print(f"\\n📈 Résumé: {result['analyzed']} analysées, {result['errors']} erreurs")
    print(f"⏱️  Durée: {result['duration_seconds']}s ({result['duration_seconds']/60:.1f} min)")
    
    return result

'''
    
    # Insérer avant step_0a_mapping
    marker = "# =============================================================================\n# ÉTAPE 0A: STRATEGY MAPPING\n# ============================================================================="
    content = content.replace(marker, ai_analysis_function + marker)
    
    # 4. Modifier run_pipeline() pour inclure step_0_ai_analysis
    old_pipeline_start = """    # Étape 0A: Strategy Mapping (NOUVEAU)
    if config.run_preprocessing:
        results['steps']['0a_mapping'] = step_0a_mapping(config)"""
    
    new_pipeline_start = """    # Étape 0: AI Analysis (OPTIONNEL - NOUVEAU)
    if config.run_ai_analysis:
        results['steps']['0_ai_analysis'] = step_0_ai_analysis(config)
        
        # Vérifier le succès avant de continuer
        if not results['steps']['0_ai_analysis'].get('success', False):
            print("\\n⚠️  AI Analysis a échoué, mais on continue...")
    
    # Étape 0A: Strategy Mapping
    if config.run_preprocessing:
        results['steps']['0a_mapping'] = step_0a_mapping(config)"""
    
    content = content.replace(old_pipeline_start, new_pipeline_start)
    
    # 5. Modifier les choices de --step
    content = content.replace(
        "choices=['enrich', 'montecarlo', 'correlation', 'all'],",
        "choices=['ai-analysis', 'enrich', 'montecarlo', 'correlation', 'all'],"
    )
    
    # 6. Ajouter les arguments CLI pour AI Analysis
    cli_args_marker = """    parser.add_argument(
        '--skip-preprocessing',
        action='store_true',
        help="Sauter les étapes de preprocessing (mapping + harmonisation)"
    )"""
    
    new_cli_args = """    parser.add_argument(
        '--skip-preprocessing',
        action='store_true',
        help="Sauter les étapes de preprocessing (mapping + harmonisation)"
    )
    
    # AI Analysis arguments
    parser.add_argument(
        '--run-ai-analysis',
        action='store_true',
        help="Exécuter l'analyse IA (LONG et COÛTEUX - voir --ai-max pour limiter)"
    )
    
    parser.add_argument(
        '--ai-mode',
        choices=['delta', 'full'],
        default='delta',
        help="Mode AI: delta (incrémental) ou full (tout ré-analyser)"
    )
    
    parser.add_argument(
        '--ai-max',
        type=int,
        default=0,
        help="Nombre max de stratégies pour AI (0 = toutes)"
    )
    
    parser.add_argument(
        '--ai-retry-errors',
        action='store_true',
        help="AI: Retraiter uniquement les stratégies en erreur"
    )
    
    parser.add_argument(
        '--ai-from-file',
        type=str,
        default=None,
        help="AI: Charger la liste des stratégies depuis un fichier"
    )
    
    parser.add_argument(
        '--ai-no-dashboard',
        action='store_true',
        help="AI: Ne pas générer le dashboard HTML"
    )"""
    
    content = content.replace(cli_args_marker, new_cli_args)
    
    # 7. Modifier la configuration depuis les args
    old_step_config = """    # Sélectionner les étapes
    if args.step == 'enrich':
        config.run_enrich = True
        config.run_monte_carlo = False
        config.run_correlation = False
    elif args.step == 'montecarlo':
        config.run_enrich = False
        config.run_monte_carlo = True
        config.run_correlation = False
    elif args.step == 'correlation':
        config.run_enrich = False
        config.run_monte_carlo = False
        config.run_correlation = True"""
    
    new_step_config = """    # Configuration AI Analysis
    if hasattr(args, 'run_ai_analysis') and args.run_ai_analysis:
        config.run_ai_analysis = True
    if hasattr(args, 'ai_mode'):
        config.ai_mode = args.ai_mode
    if hasattr(args, 'ai_max'):
        config.ai_max_strategies = args.ai_max
    if hasattr(args, 'ai_retry_errors'):
        config.ai_retry_errors = args.ai_retry_errors
    if hasattr(args, 'ai_from_file') and args.ai_from_file:
        config.ai_from_file = args.ai_from_file
    if hasattr(args, 'ai_no_dashboard') and args.ai_no_dashboard:
        config.ai_generate_dashboard = False
    
    # Sélectionner les étapes
    if args.step == 'ai-analysis':
        config.run_ai_analysis = True
        config.run_enrich = False
        config.run_monte_carlo = False
        config.run_correlation = False
    elif args.step == 'enrich':
        config.run_enrich = True
        config.run_monte_carlo = False
        config.run_correlation = False
    elif args.step == 'montecarlo':
        config.run_enrich = False
        config.run_monte_carlo = True
        config.run_correlation = False
    elif args.step == 'correlation':
        config.run_enrich = False
        config.run_monte_carlo = False
        config.run_correlation = True"""
    
    content = content.replace(old_step_config, new_step_config)
    
    # Sauvegarder
    pipeline_file.write_text(content, encoding='utf-8')
    print(f"✅ Pipeline patché: {pipeline_file}")
    print(f"   Version: 2.1.1 → 2.2.0")
    
    return True


if __name__ == "__main__":
    print("=" * 70)
    print("PATCH PIPELINE: Ajout AI Analysis V2.2.0")
    print("=" * 70)
    
    success = patch_pipeline()
    
    if success:
        print("\n✅ PATCH APPLIQUÉ AVEC SUCCÈS!")
        print("\nNouvelles fonctionnalités:")
        print("  • Étape 0: AI Analysis (optionnelle)")
        print("  • CLI: --run-ai-analysis")
        print("  • CLI: --step ai-analysis")
        print("  • CLI: --ai-mode {delta|full}")
        print("  • CLI: --ai-max N")
        print("  • CLI: --ai-retry-errors")
        print("  • CLI: --ai-from-file FICHIER")
        print("  • CLI: --ai-no-dashboard")
        print("\nTest recommandé:")
        print("  python run_pipeline.py --dry-run")
        print("  python run_pipeline.py --run-ai-analysis --dry-run")
    else:
        print("\n❌ ÉCHEC DU PATCH")
