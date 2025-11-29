"""
Pipeline Unifié - Trading Strategy Analysis V2
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
Date: 2025-11-28
"""

import argparse
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
import json

# Ajouter le répertoire racine au path
V2_ROOT = Path(__file__).parent
sys.path.insert(0, str(V2_ROOT))

# Imports projet
from config.settings import (
    V2_ROOT, OUTPUT_ROOT, DATA_ROOT,
    PORTFOLIO_REPORTS_DIR, HTML_REPORTS_DIR, EQUITY_CURVES_DIR,
    CONSOLIDATED_DIR, CORRELATION_DIR, CSV_OUTPUT_DIR,
    FUZZY_MATCH_THRESHOLD, LEGACY_ROOT,
    ensure_directories, get_latest_portfolio_report, get_latest_consolidated
)


# =============================================================================
# CONFIGURATION DU PIPELINE
# =============================================================================

class PipelineConfig:
    """Configuration du pipeline."""
    
    def __init__(self):
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
        self.run_correlation = True
        
        # Paramètres d'enrichissement
        self.enrich_backup = True
        self.enrich_force = False  # Ré-enrichir même si déjà fait
        
        # Paramètres Monte Carlo
        self.mc_nb_simulations = 1000
        self.mc_nb_capital_levels = 10
        self.mc_capital_minimum = 10000
        self.mc_capital_increment = 5000
        self.mc_max_strategies = 0  # 0 = toutes
        
        # Paramètres Corrélation
        self.corr_start_year = 2012
        self.corr_recent_months = 12
        self.corr_threshold = 0.70
        
        # Options
        self.verbose = True
        self.dry_run = False
        self.generate_dashboard = True
        
        # Timestamp pour cette exécution
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M")




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
    print("\n" + "=" * 70)
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
            print("\n🔍 Mode dry-run: aucune analyse")
            print(f"   Mode       : {config.ai_mode}")
            print(f"   Max        : {config.ai_max_strategies or 'Toutes'}")
            print(f"   Retry errors: {config.ai_retry_errors}")
            print(f"   From file  : {config.ai_from_file or 'Non'}")
            print(f"   Dashboard  : {'Non' if not config.ai_generate_dashboard else 'Oui'}")
            result['success'] = True
            return result
        
        # Vérifier si budget API acceptable
        if config.ai_max_strategies == 0 and not config.ai_retry_errors:
            print("\n⚠️  ATTENTION: Analyse COMPLÈTE demandée!")
            print(f"   Estimation temps: ~40+ heures")
            print(f"   Estimation coût : ~$2.40 (API Claude)")
            
            # Demander confirmation
            response = input("\n   Continuer? [y/N]: ").strip().lower()
            if response != 'y':
                print("   Analyse annulée par l'utilisateur")
                result['success'] = True
                result['skipped'] = 1
                return result
        
        print(f"\n🚀 Lancement de l'analyse IA...")
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
        print(f"\n✅ AI Analysis terminée")
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("   Vérifiez que run_ai_analysis.py et src/analyzers/ existent")
        result['errors'] += 1
    except KeyboardInterrupt:
        print(f"\n⚠️  Analyse interrompue par l'utilisateur")
        result['errors'] += 1
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        result['errors'] += 1
    
    result['duration_seconds'] = round(time.time() - start_time, 1)
    
    print(f"\n📈 Résumé: {result['analyzed']} analysées, {result['errors']} erreurs")
    print(f"⏱️  Durée: {result['duration_seconds']}s ({result['duration_seconds']/60:.1f} min)")
    
    return result

# =============================================================================
# ÉTAPE 0A: STRATEGY MAPPING
# =============================================================================

def step_0a_mapping(config: PipelineConfig) -> Dict[str, Any]:
    """
    Étape 0A: Générer le mapping stratégie → symbole depuis Portfolio Report.
    
    Returns:
        Dict avec statistiques de l'étape
    """
    print("\n" + "=" * 70)
    print("🗺️  ÉTAPE 0A: STRATEGY MAPPING")
    print("=" * 70)
    
    result = {
        'step': 'strategy_mapping',
        'success': False,
        'nb_strategies': 0,
        'nb_mappings': 0,
        'errors': 0,
        'duration_seconds': 0
    }
    
    start_time = time.time()
    
    try:
        # Import du module
        from src.utils.strategy_mapper import StrategyMapper
        
        if config.dry_run:
            print("\n🔍 Mode dry-run: aucun fichier généré")
            result['success'] = True
            return result
        
        print("\n📊 Génération du mapping stratégie → symbole...")
        
        # Créer le mapper
        mapper = StrategyMapper()
        
        # Afficher les statistiques
        if config.verbose:
            mapper.print_statistics()
        
        # Exporter le mapping
        output_path = mapper.export_mapping()
        
        # Collecter les stats
        result['nb_strategies'] = len(mapper.strategy_map)
        result['nb_mappings'] = sum(len(data['symbols']) for data in mapper.strategy_map.values())
        result['success'] = True
        
        print(f"\n✅ Mapping généré: {output_path}")
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("   Vérifiez que src/utils/strategy_mapper.py existe")
        result['errors'] += 1
    except FileNotFoundError as e:
        print(f"❌ Portfolio Report introuvable: {e}")
        result['errors'] += 1
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        result['errors'] += 1
    
    result['duration_seconds'] = round(time.time() - start_time, 1)
    
    print(f"\n📈 Résumé: {result['nb_strategies']} stratégies mappées")
    print(f"⏱️  Durée: {result['duration_seconds']}s")
    
    return result


# =============================================================================
# ÉTAPE 1: ENRICHISSEMENT KPI
# =============================================================================

def step_enrich_kpis(config: PipelineConfig) -> Dict[str, Any]:
    """
    Étape 1: Enrichir les rapports HTML avec les KPIs du Portfolio Report.
    
    Returns:
        Dict avec statistiques de l'étape
    """
    print("\n" + "=" * 70)
    print("📊 ÉTAPE 1: ENRICHISSEMENT KPI")
    print("=" * 70)
    
    result = {
        'step': 'enrich_kpis',
        'success': False,
        'enriched': 0,
        'skipped': 0,
        'errors': 0,
        'duration_seconds': 0
    }
    
    start_time = time.time()
    
    try:
        # Import du module
        from src.enrichers.kpi_enricher import KPIEnricher
        from src.enrichers.styles import get_kpi_styles
        
        # Charger le Portfolio Report
        try:
            portfolio_path = get_latest_portfolio_report()
            print(f"\n📁 Portfolio Report: {portfolio_path.name}")
        except FileNotFoundError:
            # Essayer dans le dossier Results legacy
            legacy_reports = list(LEGACY_ROOT.glob("Results/Portfolio_Report_V2_*.csv"))
            if legacy_reports:
                portfolio_path = max(legacy_reports, key=lambda p: p.stat().st_mtime)
                print(f"\n📁 Portfolio Report (legacy): {portfolio_path.name}")
            else:
                print("⚠️  Aucun Portfolio Report trouvé")
                result['errors'] = 1
                return result
        
        enricher = KPIEnricher(portfolio_path)
        
        if not enricher.portfolio_data:
            print("⚠️  Aucune donnée dans le Portfolio Report")
            result['errors'] = 1
            return result
        
        # Trouver les rapports HTML à enrichir
        html_dirs = [
            HTML_REPORTS_DIR,
            LEGACY_ROOT / "Results" / "HTML_Reports",
        ]
        
        html_files = []
        for html_dir in html_dirs:
            if html_dir.exists():
                html_files.extend(html_dir.glob("*.html"))
        
        # Filtrer les index et fichiers déjà enrichis
        html_files = [f for f in html_files if f.name != "index.html"]
        
        print(f"\n📄 {len(html_files)} fichiers HTML trouvés")
        print(f"📊 {len(enricher.portfolio_data)} stratégies dans le Portfolio Report")
        
        if config.dry_run:
            print("\n🔍 Mode dry-run: aucune modification")
            result['success'] = True
            return result
        
        # Enrichir chaque fichier
        for html_file in html_files:
            try:
                strategy_name = html_file.stem
                kpis = enricher.find_kpis_for_strategy(strategy_name)
                
                if kpis is None:
                    if config.verbose:
                        print(f"   ⏭️  {strategy_name}: pas de KPIs trouvés")
                    result['skipped'] += 1
                    continue
                
                # Lire le HTML existant
                content = html_file.read_text(encoding='utf-8')
                
                # Vérifier si déjà enrichi
                if 'kpi-dashboard' in content and not config.enrich_force:
                    if config.verbose:
                        print(f"   ✓ {strategy_name}: déjà enrichi")
                    result['skipped'] += 1
                    continue
                
                # Générer le HTML des KPIs
                kpi_html = enricher.generate_kpi_html(kpis)
                kpi_styles = get_kpi_styles()
                
                # Injecter dans le HTML
                if '</head>' in content:
                    content = content.replace('</head>', f'{kpi_styles}\n</head>')
                
                if '<body>' in content:
                    content = content.replace('<body>', f'<body>\n{kpi_html}')
                elif '<body ' in content:
                    # Body avec attributs
                    import re
                    content = re.sub(r'(<body[^>]*>)', rf'\1\n{kpi_html}', content)
                
                # Sauvegarder
                if config.enrich_backup:
                    backup_path = html_file.with_suffix('.html.bak')
                    if not backup_path.exists():
                        html_file.rename(backup_path)
                        backup_path.rename(html_file)
                        # Copie du backup
                        import shutil
                        shutil.copy2(html_file, backup_path)
                
                html_file.write_text(content, encoding='utf-8')
                
                if config.verbose:
                    print(f"   ✅ {strategy_name}: enrichi")
                result['enriched'] += 1
                
            except Exception as e:
                print(f"   ❌ {html_file.name}: {e}")
                result['errors'] += 1
        
        result['success'] = True
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        result['errors'] += 1
    
    result['duration_seconds'] = round(time.time() - start_time, 1)
    
    print(f"\n📈 Résumé: {result['enriched']} enrichis, {result['skipped']} ignorés, {result['errors']} erreurs")
    print(f"⏱️  Durée: {result['duration_seconds']}s")
    
    return result


# =============================================================================
# ÉTAPE 1B: NAME HARMONIZATION
# =============================================================================

def step_1b_harmonization(config: PipelineConfig) -> Dict[str, Any]:
    """
    Étape 1B: Harmoniser les noms de fichiers HTML (ajouter préfixe symbole).
    
    Returns:
        Dict avec statistiques de l'étape
    """
    print("\n" + "=" * 70)
    print("📝 ÉTAPE 1B: NAME HARMONIZATION")
    print("=" * 70)
    
    result = {
        'step': 'name_harmonization',
        'success': False,
        'renamed': 0,
        'kept_original': 0,
        'errors': 0,
        'duration_seconds': 0
    }
    
    start_time = time.time()
    
    try:
        # Chemin du script de migration
        migration_script = V2_ROOT / 'migrate_ai_html_names.py'
        
        if not migration_script.exists():
            print(f"⚠️  Script de migration introuvable: {migration_script}")
            print("   L'harmonisation sera ignorée")
            result['errors'] += 1
            return result
        
        if config.dry_run:
            print("\n🔍 Mode dry-run: aucune harmonisation")
            print("   Utilisez: python migrate_ai_html_names.py --dry-run")
            result['success'] = True
            return result
        
        print("\n📝 Harmonisation des noms de fichiers HTML...")
        print("   Format cible: SYMBOL_StrategyName.html")
        
        # Exécuter le script de migration
        cmd = [sys.executable, str(migration_script)]
        
        # Ajouter --no-backup si pas besoin de backup (déjà fait par KPI enricher)
        # cmd.append('--no-backup')  # Décommentez si souhaité
        
        process_result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if process_result.returncode != 0:
            print(f"❌ Erreur lors de l'harmonisation:")
            print(process_result.stderr)
            result['errors'] += 1
            return result
        
        # Afficher la sortie
        if config.verbose and process_result.stdout:
            print(process_result.stdout)
        
        # Lire le rapport de migration pour les stats
        migration_report = CONSOLIDATED_DIR / 'migration_report.json'
        if migration_report.exists():
            with open(migration_report, 'r', encoding='utf-8') as f:
                report = json.load(f)
                result['renamed'] = report.get('renamed', 0)
                result['kept_original'] = report.get('kept_original', 0)
                result['errors'] = report.get('errors', 0)
        
        result['success'] = True
        print(f"\n✅ Harmonisation terminée")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        result['errors'] += 1
    
    result['duration_seconds'] = round(time.time() - start_time, 1)
    
    print(f"\n📈 Résumé: {result['renamed']} fichiers renommés, {result['kept_original']} conservés")
    print(f"⏱️  Durée: {result['duration_seconds']}s")
    
    return result


# =============================================================================
# ÉTAPE 2: SIMULATION MONTE CARLO
# =============================================================================

def step_monte_carlo(config: PipelineConfig) -> Dict[str, Any]:
    """
    Étape 2: Simulation Monte Carlo pour chaque stratégie.
    
    Returns:
        Dict avec statistiques de l'étape
    """
    print("\n" + "=" * 70)
    print("🎲 ÉTAPE 2: SIMULATION MONTE CARLO")
    print("=" * 70)
    
    result = {
        'step': 'monte_carlo',
        'success': False,
        'simulated': 0,
        'skipped': 0,
        'errors': 0,
        'duration_seconds': 0,
        'summaries': []
    }
    
    start_time = time.time()
    
    try:
        from src.monte_carlo.simulator import MonteCarloSimulator
        from src.monte_carlo.data_loader import detect_file_format
        
        # Trouver les fichiers d'equity curves
        equity_dirs = [
            EQUITY_CURVES_DIR,
            DATA_ROOT / "equity_curves",
            LEGACY_ROOT / "Results" / "Titan_Equity_Export",
        ]
        
        equity_files = []
        for eq_dir in equity_dirs:
            if eq_dir.exists():
                equity_files.extend(eq_dir.glob("*.txt"))
                equity_files.extend(eq_dir.glob("*.csv"))
        
        # Dédupliquer par nom
        seen_names = set()
        unique_files = []
        for f in equity_files:
            if f.stem not in seen_names:
                seen_names.add(f.stem)
                unique_files.append(f)
        equity_files = unique_files
        
        print(f"\n📁 {len(equity_files)} fichiers d'equity curves trouvés")
        
        if config.mc_max_strategies > 0:
            equity_files = equity_files[:config.mc_max_strategies]
            print(f"   ⚠️  Limité à {config.mc_max_strategies} stratégies")
        
        if config.dry_run:
            print("\n🔍 Mode dry-run: aucune simulation")
            result['success'] = True
            return result
        
        # Créer le répertoire de sortie
        mc_output_dir = OUTPUT_ROOT / "monte_carlo" / config.timestamp
        mc_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Simuler chaque stratégie
        for i, equity_file in enumerate(equity_files, 1):
            try:
                if config.verbose:
                    print(f"\n[{i}/{len(equity_files)}] {equity_file.stem}...", end=" ", flush=True)
                
                # Vérifier le format
                file_format = detect_file_format(str(equity_file))
                if file_format == "unknown":
                    if config.verbose:
                        print("format inconnu, ignoré")
                    result['skipped'] += 1
                    continue
                
                # Créer le simulateur
                mc = MonteCarloSimulator(
                    strategy_file=str(equity_file),
                    capital_minimum=config.mc_capital_minimum,
                    capital_increment=config.mc_capital_increment,
                    nb_capital_levels=config.mc_nb_capital_levels,
                    nb_simulations=config.mc_nb_simulations,
                )
                
                # Lancer la simulation
                mc.run(verbose=False)
                
                # Sauvegarder les résultats
                csv_path = mc_output_dir / f"{equity_file.stem}_mc.csv"
                mc.export_csv(str(csv_path), include_metadata=True)
                
                # Collecter le résumé
                summary = mc.get_summary()
                result['summaries'].append(summary)
                
                if config.verbose:
                    status_icon = "✅" if mc.status == "OK" else "⚠️" if mc.status == "WARNING" else "🔴"
                    capital_str = f"${mc.recommended_capital:,.0f}" if mc.recommended_capital else "N/A"
                    print(f"{status_icon} Capital recommandé: {capital_str}")
                
                result['simulated'] += 1
                
            except Exception as e:
                if config.verbose:
                    print(f"❌ Erreur: {e}")
                result['errors'] += 1
        
        # Exporter le résumé global
        if result['summaries']:
            import pandas as pd
            df_summary = pd.DataFrame(result['summaries'])
            summary_path = mc_output_dir / "monte_carlo_summary.csv"
            df_summary.to_csv(summary_path, sep=';', decimal=',', index=False, encoding='utf-8-sig')
            print(f"\n📊 Résumé exporté: {summary_path}")
        
        result['success'] = True
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        result['errors'] += 1
    
    result['duration_seconds'] = round(time.time() - start_time, 1)
    
    print(f"\n📈 Résumé: {result['simulated']} simulés, {result['skipped']} ignorés, {result['errors']} erreurs")
    print(f"⏱️  Durée: {result['duration_seconds']}s")
    
    return result


# =============================================================================
# ÉTAPE 3: ANALYSE DE CORRÉLATION
# =============================================================================

def step_correlation(config: PipelineConfig) -> Dict[str, Any]:
    """
    Étape 3: Analyse de corrélation Long Terme / Court Terme.
    
    Returns:
        Dict avec statistiques de l'étape
    """
    print("\n" + "=" * 70)
    print("📊 ÉTAPE 3: ANALYSE DE CORRÉLATION")
    print("=" * 70)
    
    result = {
        'step': 'correlation',
        'success': False,
        'nb_strategies': 0,
        'errors': 0,
        'duration_seconds': 0,
        'summary': {}
    }
    
    start_time = time.time()
    
    try:
        import pandas as pd
        from src.consolidators.correlation_calculator import CorrelationAnalyzer
        
        # Charger le fichier consolidé
        try:
            consolidated_path = get_latest_consolidated()
            print(f"\n📁 Fichier consolidé: {consolidated_path.name}")
        except FileNotFoundError:
            # Essayer dans le dossier Results legacy
            legacy_files = list(LEGACY_ROOT.glob("Results/Consolidated_Strategies_*.txt"))
            # Filtrer les fichiers COSTS, Filtered, Part
            legacy_files = [f for f in legacy_files 
                          if "COSTS" not in f.name 
                          and "Filtered" not in f.name 
                          and "Part" not in f.name]
            if legacy_files:
                consolidated_path = max(legacy_files, key=lambda p: p.stat().st_mtime)
                print(f"\n📁 Fichier consolidé (legacy): {consolidated_path.name}")
            else:
                print("⚠️  Aucun fichier consolidé trouvé")
                result['errors'] = 1
                return result
        
        # Charger les données
        print("\n📥 Chargement des données...")
        df = pd.read_csv(consolidated_path, sep=';', encoding='utf-8', decimal=',')
        print(f"   {len(df):,} lignes chargées")
        print(f"   Colonnes: {list(df.columns)}")
        
        if config.dry_run:
            print("\n🔍 Mode dry-run: aucune analyse")
            result['success'] = True
            return result
        
        # Créer l'analyseur
        analyzer = CorrelationAnalyzer(
            data=df,
            start_year_longterm=config.corr_start_year,
            recent_months=config.corr_recent_months,
            correlation_threshold=config.corr_threshold,
        )
        
        # Lancer l'analyse
        analyzer.run(verbose=config.verbose)
        
        # Afficher le résumé
        if config.verbose:
            analyzer.print_summary()
        
        # Exporter les résultats
        corr_output_dir = CORRELATION_DIR / config.timestamp
        corr_output_dir.mkdir(parents=True, exist_ok=True)
        
        exported_files = analyzer.export_csv(corr_output_dir, prefix="correlation")
        
        # Générer le dashboard HTML si demandé
        if config.generate_dashboard:
            try:
                dashboard_path = corr_output_dir / f"correlation_dashboard_{config.timestamp}.html"
                analyzer.export_dashboard(dashboard_path)
                exported_files['dashboard'] = dashboard_path
                result['dashboard_path'] = str(dashboard_path)
            except Exception as e:
                print(f"⚠️  Erreur lors de la génération du dashboard: {e}")
        
        # Collecter les statistiques
        result['summary'] = analyzer.get_summary()
        result['nb_strategies'] = len(analyzer.scores) if analyzer.scores is not None else 0
        result['success'] = True
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        result['errors'] += 1
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        result['errors'] += 1
    
    result['duration_seconds'] = round(time.time() - start_time, 1)
    
    print(f"\n📈 Résumé: {result['nb_strategies']} stratégies analysées, {result['errors']} erreurs")
    print(f"⏱️  Durée: {result['duration_seconds']}s")
    
    return result


# =============================================================================
# PIPELINE PRINCIPAL
# =============================================================================

def run_pipeline(config: PipelineConfig) -> Dict[str, Any]:
    """
    Exécute le pipeline complet.
    
    Args:
        config: Configuration du pipeline
        
    Returns:
        Dict avec les résultats de chaque étape
    """
    print("\n" + "=" * 70)
    print("🚀 TRADING STRATEGY ANALYSIS PIPELINE V2")
    print("=" * 70)
    print(f"⏰ Démarrage: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 V2_ROOT: {V2_ROOT}")
    
    if config.dry_run:
        print("🔍 MODE DRY-RUN: Aucune modification ne sera effectuée")
    
    # Créer les répertoires
    ensure_directories()
    
    start_time = time.time()
    results = {
        'timestamp': config.timestamp,
        'dry_run': config.dry_run,
        'steps': {}
    }
    
    # Étape 0: AI Analysis (OPTIONNEL - NOUVEAU)
    if config.run_ai_analysis:
        results['steps']['0_ai_analysis'] = step_0_ai_analysis(config)
        
        # Vérifier le succès avant de continuer
        if not results['steps']['0_ai_analysis'].get('success', False):
            print("\n⚠️  AI Analysis a échoué, mais on continue...")
    
    # Étape 0A: Strategy Mapping
    if config.run_preprocessing:
        results['steps']['0a_mapping'] = step_0a_mapping(config)
        
        # Vérifier le succès avant de continuer
        if not results['steps']['0a_mapping'].get('success', False):
            print("\n⚠️  Mapping a échoué, mais on continue...")
    
    # Étape 1: Enrichissement KPI
    if config.run_enrich:
        results['steps']['enrich'] = step_enrich_kpis(config)
    
    # Étape 1B: Name Harmonization (NOUVEAU - APRÈS enrichissement)
    if config.run_preprocessing:
        results['steps']['1b_harmonization'] = step_1b_harmonization(config)
        
        # Vérifier le succès
        if not results['steps']['1b_harmonization'].get('success', False):
            print("\n⚠️  Harmonisation a échoué, mais on continue...")
    
    # Étape 2: Monte Carlo
    if config.run_monte_carlo:
        results['steps']['monte_carlo'] = step_monte_carlo(config)
    
    # Étape 3: Corrélation
    if config.run_correlation:
        results['steps']['correlation'] = step_correlation(config)
    
    # Résumé final
    total_duration = round(time.time() - start_time, 1)
    results['total_duration_seconds'] = total_duration
    
    print("\n" + "=" * 70)
    print("✅ PIPELINE TERMINÉ")
    print("=" * 70)
    print(f"⏱️  Durée totale: {total_duration}s")
    
    # Afficher résumé par étape
    for step_name, step_result in results['steps'].items():
        status = "✅" if step_result.get('success', False) else "❌"
        duration = step_result.get('duration_seconds', 0)
        print(f"   {status} {step_name}: {duration}s")
    
    # Sauvegarder le rapport d'exécution
    if not config.dry_run:
        report_path = OUTPUT_ROOT / "pipeline_reports" / f"pipeline_report_{config.timestamp}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Nettoyer les données non-sérialisables
        clean_results = json.loads(json.dumps(results, default=str))
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(clean_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Rapport sauvegardé: {report_path}")
    
    return results


# =============================================================================
# POINT D'ENTRÉE
# =============================================================================

def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description="Pipeline d'analyse des stratégies de trading V2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python run_pipeline.py                      # Exécuter tout le pipeline
  python run_pipeline.py --step enrich        # Enrichissement KPI uniquement
  python run_pipeline.py --step montecarlo    # Monte Carlo uniquement
  python run_pipeline.py --step correlation   # Corrélation uniquement
  python run_pipeline.py --dry-run            # Mode simulation
  python run_pipeline.py --mc-max 10          # Limiter Monte Carlo à 10 stratégies
  python run_pipeline.py --skip-preprocessing # Sauter mapping + harmonization
        """
    )
    
    parser.add_argument(
        '--step', '-s',
        choices=['ai-analysis', 'enrich', 'montecarlo', 'correlation', 'all'],
        default='all',
        help="Étape à exécuter (défaut: all)"
    )
    
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help="Mode simulation (n'effectue aucune modification)"
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help="Mode silencieux (moins de logs)"
    )
    
    parser.add_argument(
        '--mc-max',
        type=int,
        default=0,
        help="Nombre maximum de stratégies pour Monte Carlo (0 = toutes)"
    )
    
    parser.add_argument(
        '--mc-sims',
        type=int,
        default=1000,
        help="Nombre de simulations Monte Carlo par niveau (défaut: 1000)"
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help="Forcer le ré-enrichissement même si déjà fait"
    )
    
    parser.add_argument(
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
    )
    
    args = parser.parse_args()
    
    # Configurer le pipeline
    config = PipelineConfig()
    config.dry_run = args.dry_run
    config.verbose = not args.quiet
    config.enrich_force = args.force
    config.mc_max_strategies = args.mc_max
    config.mc_nb_simulations = args.mc_sims
    
    # Configuration preprocessing
    if args.skip_preprocessing:
        config.run_preprocessing = False
    
    # Configuration AI Analysis
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
        config.run_correlation = True
    
    # Exécuter
    results = run_pipeline(config)
    
    # Code de sortie
    all_success = all(
        step.get('success', False) 
        for step in results.get('steps', {}).values()
    )
    sys.exit(0 if all_success else 1)


if __name__ == "__main__":
    main()
