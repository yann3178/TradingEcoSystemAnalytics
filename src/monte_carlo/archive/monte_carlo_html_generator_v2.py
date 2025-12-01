#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monte Carlo HTML Generator V2 - Version Améliorée
==================================================

Génère des rapports HTML pour les simulations Monte Carlo avec:
- Calcul du capital recommandé basé UNIQUEMENT sur le seuil de ruine
- Pas besoin que tous les critères Kevin Davey soient satisfaits

Usage:
    python monte_carlo_html_generator_v2.py                 # Dernier run
    python monte_carlo_html_generator_v2.py --run 20251201_1130   # Run spécifique
    python monte_carlo_html_generator_v2.py --max-ruin 10   # Seuil de ruine personnalisé

Auteur: Yann
Date: 2025-12-01
"""

# Importer depuis le fichier original
from monte_carlo_html_generator import *

# Surcharger certaines fonctions


def find_capital_for_ruin_threshold(df: pd.DataFrame, max_ruin_pct: float) -> Optional[float]:
    """
    Trouve le capital minimum pour atteindre un seuil de ruine donné.
    
    Args:
        df: DataFrame avec les résultats par niveau de capital
        max_ruin_pct: Seuil de ruine maximum acceptable (en %)
    
    Returns:
        Capital minimum ou None si aucun niveau ne satisfait le critère
    """
    # Filtrer les niveaux où le risque de ruine est acceptable
    acceptable = df[df['Ruin_Pct'] <= max_ruin_pct]
    
    if len(acceptable) > 0:
        # Retourner le capital minimum
        return float(acceptable['Start_Equity'].min())
    
    return None


def recalculate_recommended_capitals(summary_df: pd.DataFrame, run_dir: Path, max_ruin_pct: float = 10.0) -> pd.DataFrame:
    """
    Recalcule les capitaux recommandés basés uniquement sur le seuil de ruine.
    
    Args:
        summary_df: DataFrame avec les données summary
        run_dir: Répertoire contenant les CSV individuels
        max_ruin_pct: Seuil de ruine maximum acceptable (défaut: 10%)
    
    Returns:
        DataFrame mis à jour
    """
    print(f"🔄 Recalcul des capitaux recommandés (seuil de ruine ≤ {max_ruin_pct}%)...")
    
    for idx, row in summary_df.iterrows():
        strategy_name = row['strategy_name']
        
        # Charger le CSV individuel
        csv_file = run_dir / f"{strategy_name}_mc.csv"
        
        if not csv_file.exists():
            continue
        
        try:
            # Lire les données
            df = pd.read_csv(csv_file, comment='#')
            
            # Trouver le capital pour le seuil de ruine
            recommended_capital = find_capital_for_ruin_threshold(df, max_ruin_pct)
            
            if recommended_capital:
                # Mettre à jour le capital recommandé
                summary_df.at[idx, 'recommended_capital'] = recommended_capital
                
                # Trouver les métriques pour ce niveau de capital
                capital_row = df[df['Start_Equity'] == recommended_capital].iloc[0]
                
                # Mettre à jour les métriques
                summary_df.at[idx, 'ruin_pct'] = capital_row['Ruin_Pct']
                summary_df.at[idx, 'return_dd_ratio'] = capital_row['Return_DD_Ratio']
                summary_df.at[idx, 'prob_positive'] = capital_row['Prob_Positive_Pct']
                summary_df.at[idx, 'median_dd_pct'] = capital_row['Median_DD_Pct']
                summary_df.at[idx, 'median_profit'] = capital_row['Median_Profit']
                
                # Recalculer le statut
                ruin_ok = capital_row['Ruin_Pct'] <= max_ruin_pct
                ratio_ok = capital_row['Return_DD_Ratio'] >= 2.0
                prob_ok = capital_row['Prob_Positive_Pct'] >= 80.0
                
                if ruin_ok and ratio_ok and prob_ok:
                    summary_df.at[idx, 'status'] = 'OK'
                elif ruin_ok:
                    summary_df.at[idx, 'status'] = 'WARNING'
                else:
                    summary_df.at[idx, 'status'] = 'HIGH_RISK'
            else:
                # Aucun niveau ne satisfait le seuil de ruine
                summary_df.at[idx, 'status'] = 'HIGH_RISK'
                
        except Exception as e:
            print(f"   ⚠ Erreur pour {strategy_name}: {e}")
            continue
    
    print(f"   ✓ Capitaux recalculés")
    return summary_df


def main_v2(run_dir: Optional[Path] = None, max_ruin_pct: float = 10.0):
    """
    Point d'entrée principal avec recalcul des capitaux.
    """
    print("=" * 80)
    print("GÉNÉRATEUR DE RAPPORTS HTML MONTE CARLO V2 - VERSION AMÉLIORÉE")
    print("=" * 80)
    print()
    
    # 1. Déterminer le répertoire de run
    if run_dir is None:
        run_dir = find_latest_monte_carlo_run()
    
    print(f"📁 Répertoire de run: {run_dir.name}")
    print(f"⚙️  Seuil de ruine: {max_ruin_pct}%")
    print()
    
    # 2. Vérifier les fichiers requis
    summary_file = run_dir / "monte_carlo_summary.csv"
    if not summary_file.exists():
        raise FileNotFoundError(f"Fichier summary introuvable: {summary_file}")
    
    # 3. Charger les données summary
    print("📊 Chargement du fichier summary...")
    summary_df = load_summary_data(summary_file)
    print(f"   ✓ {len(summary_df)} stratégies chargées")
    print()
    
    # 4. Recalculer les capitaux recommandés
    summary_df = recalculate_recommended_capitals(summary_df, run_dir, max_ruin_pct)
    print()
    
    # Afficher les statistiques recalculées
    status_counts = summary_df['status'].value_counts().to_dict()
    print(f"📊 Statistiques après recalcul:")
    print(f"   • OK: {status_counts.get('OK', 0)}")
    print(f"   • WARNING: {status_counts.get('WARNING', 0)}")
    print(f"   • HIGH_RISK: {status_counts.get('HIGH_RISK', 0)}")
    print()
    
    # 5. Créer les répertoires de sortie
    individual_dir = HTML_MONTECARLO_DIR / "Individual"
    individual_dir.mkdir(parents=True, exist_ok=True)
    HTML_MONTECARLO_DIR.mkdir(parents=True, exist_ok=True)
    
    # 6. Générer les pages individuelles
    print("🔨 Génération des pages HTML individuelles...")
    success_count = 0
    error_count = 0
    
    for idx, row in summary_df.iterrows():
        strategy_name = row['strategy_name']
        symbol = row['symbol']
        
        # Trouver le fichier CSV correspondant
        csv_file = run_dir / f"{strategy_name}_mc.csv"
        
        if not csv_file.exists():
            print(f"   ⚠ CSV introuvable: {csv_file.name}")
            error_count += 1
            continue
        
        try:
            # Charger les données détaillées
            detail_data = load_individual_strategy_data(csv_file)
            
            # Générer la page HTML
            output_file = individual_dir / f"{symbol}_{strategy_name}_MC.html"
            generate_individual_html(
                strategy_name=strategy_name,
                symbol=symbol,
                summary_row=row.to_dict(),
                detail_data=detail_data,
                output_file=output_file
            )
            
            success_count += 1
            
            if (idx + 1) % 50 == 0:
                print(f"   Progression: {idx + 1}/{len(summary_df)}")
        
        except Exception as e:
            print(f"   ✗ Erreur pour {strategy_name}: {e}")
            error_count += 1
    
    print(f"   ✓ {success_count} pages individuelles générées")
    if error_count > 0:
        print(f"   ⚠ {error_count} erreurs")
    print()
    
    # 7. Générer la page de synthèse
    print("🔨 Génération de la page de synthèse...")
    summary_html_file = HTML_MONTECARLO_DIR / "all_strategies_montecarlo.html"
    
    run_info = {
        'run_name': run_dir.name,
        'nb_simulations': '1000',
    }
    
    generate_summary_html(
        summary_df=summary_df,
        output_file=summary_html_file,
        run_info=run_info
    )
    
    print(f"   ✓ Page de synthèse générée: {summary_html_file.name}")
    print()
    
    # 8. Résumé final
    print("=" * 80)
    print("✅ GÉNÉRATION TERMINÉE")
    print("=" * 80)
    print(f"📊 Stratégies traitées: {success_count}/{len(summary_df)}")
    print(f"📁 Répertoire de sortie: {HTML_MONTECARLO_DIR}")
    print(f"   • Page de synthèse: all_strategies_montecarlo.html")
    print(f"   • Pages individuelles: Individual/ ({success_count} fichiers)")
    print()
    print(f"💡 Capitaux calculés pour un seuil de ruine ≤ {max_ruin_pct}%")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Génère des rapports HTML Monte Carlo (version améliorée)")
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
    
    args = parser.parse_args()
    
    run_dir = None
    if args.run:
        run_dir = OUTPUT_ROOT / "monte_carlo" / args.run
        if not run_dir.exists():
            print(f"❌ Erreur: Run introuvable: {run_dir}")
            sys.exit(1)
    
    try:
        main_v2(run_dir, args.max_ruin)
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
