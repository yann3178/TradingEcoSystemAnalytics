#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monte Carlo HTML Generator V3 - Version Entièrement Paramétrable
================================================================

Génère des rapports HTML pour les simulations Monte Carlo avec:
- Tous les critères Kevin Davey paramétrables
- Recherche du capital minimum satisfaisant TOUS les critères choisis
- Flexibilité maximale pour tester différentes configurations

Usage:
    # Configuration par défaut (Kevin Davey standard)
    python monte_carlo_html_generator_v3.py
    
    # Personnaliser le seuil de ruine uniquement
    python monte_carlo_html_generator_v3.py --max-ruin 15
    
    # Personnaliser tous les critères
    python monte_carlo_html_generator_v3.py --max-ruin 10 --min-return-dd 2.5 --min-prob-positive 85
    
    # Très conservateur
    python monte_carlo_html_generator_v3.py --max-ruin 5 --min-return-dd 3.0 --min-prob-positive 90
    
    # Agressif (accepte plus de risque)
    python monte_carlo_html_generator_v3.py --max-ruin 20 --min-return-dd 1.5 --min-prob-positive 70

Auteur: Yann
Date: 2025-12-01
"""

# Importer depuis le fichier original
from monte_carlo_html_generator import *


def find_capital_for_criteria(
    df: pd.DataFrame, 
    max_ruin_pct: float,
    min_return_dd: Optional[float] = None,
    min_prob_positive: Optional[float] = None
) -> Optional[float]:
    """
    Trouve le capital minimum pour satisfaire tous les critères spécifiés.
    
    Args:
        df: DataFrame avec les résultats par niveau de capital
        max_ruin_pct: Seuil de ruine maximum acceptable (en %)
        min_return_dd: Ratio Return/DD minimum (None = pas de contrainte)
        min_prob_positive: Probabilité positive minimum (en %, None = pas de contrainte)
    
    Returns:
        Capital minimum ou None si aucun niveau ne satisfait tous les critères
    """
    # Commencer avec le filtre sur la ruine (obligatoire)
    acceptable = df[df['Ruin_Pct'] <= max_ruin_pct]
    
    # Ajouter le filtre Return/DD si spécifié
    if min_return_dd is not None:
        acceptable = acceptable[acceptable['Return_DD_Ratio'] >= min_return_dd]
    
    # Ajouter le filtre Probabilité positive si spécifié
    if min_prob_positive is not None:
        acceptable = acceptable[acceptable['Prob_Positive_Pct'] >= min_prob_positive]
    
    if len(acceptable) > 0:
        # Retourner le capital minimum
        return float(acceptable['Start_Equity'].min())
    
    return None


def recalculate_recommended_capitals_v3(
    summary_df: pd.DataFrame, 
    run_dir: Path, 
    max_ruin_pct: float = 10.0,
    min_return_dd: Optional[float] = None,
    min_prob_positive: Optional[float] = None
) -> pd.DataFrame:
    """
    Recalcule les capitaux recommandés avec des critères personnalisables.
    
    Args:
        summary_df: DataFrame avec les données summary
        run_dir: Répertoire contenant les CSV individuels
        max_ruin_pct: Seuil de ruine maximum acceptable (défaut: 10%)
        min_return_dd: Ratio Return/DD minimum (None = pas de contrainte)
        min_prob_positive: Probabilité positive minimum en % (None = pas de contrainte)
    
    Returns:
        DataFrame mis à jour
    """
    # Construire le message des critères
    criteria_parts = [f"Ruine ≤ {max_ruin_pct}%"]
    if min_return_dd is not None:
        criteria_parts.append(f"Return/DD ≥ {min_return_dd}")
    if min_prob_positive is not None:
        criteria_parts.append(f"Prob>0 ≥ {min_prob_positive}%")
    
    criteria_str = " ET ".join(criteria_parts)
    print(f"🔄 Recalcul des capitaux recommandés avec critères:")
    print(f"   {criteria_str}")
    print()
    
    for idx, row in summary_df.iterrows():
        strategy_name = row['strategy_name']
        
        # Charger le CSV individuel
        csv_file = run_dir / f"{strategy_name}_mc.csv"
        
        if not csv_file.exists():
            continue
        
        try:
            # Lire les données
            df = pd.read_csv(csv_file, comment='#')
            
            # Trouver le capital pour les critères spécifiés
            recommended_capital = find_capital_for_criteria(
                df, 
                max_ruin_pct,
                min_return_dd,
                min_prob_positive
            )
            
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
                
                # Calculer le statut
                # OK si tous les critères actifs sont satisfaits
                ruin_ok = capital_row['Ruin_Pct'] <= max_ruin_pct
                ratio_ok = (min_return_dd is None) or (capital_row['Return_DD_Ratio'] >= min_return_dd)
                prob_ok = (min_prob_positive is None) or (capital_row['Prob_Positive_Pct'] >= min_prob_positive)
                
                if ruin_ok and ratio_ok and prob_ok:
                    summary_df.at[idx, 'status'] = 'OK'
                elif ruin_ok:
                    summary_df.at[idx, 'status'] = 'WARNING'
                else:
                    summary_df.at[idx, 'status'] = 'HIGH_RISK'
            else:
                # Aucun niveau ne satisfait tous les critères
                summary_df.at[idx, 'recommended_capital'] = 0
                summary_df.at[idx, 'status'] = 'HIGH_RISK'
                
        except Exception as e:
            print(f"   ⚠ Erreur pour {strategy_name}: {e}")
            continue
    
    print(f"   ✓ Capitaux recalculés")
    return summary_df


def main_v3(
    run_dir: Optional[Path] = None, 
    max_ruin_pct: float = 10.0,
    min_return_dd: Optional[float] = None,
    min_prob_positive: Optional[float] = None
):
    """
    Point d'entrée principal avec critères entièrement paramétrables.
    """
    print("=" * 80)
    print("GÉNÉRATEUR DE RAPPORTS HTML MONTE CARLO V3 - VERSION PARAMÉTRABLE")
    print("=" * 80)
    print()
    
    # 1. Déterminer le répertoire de run
    if run_dir is None:
        run_dir = find_latest_monte_carlo_run()
    
    print(f"📁 Répertoire de run: {run_dir.name}")
    print()
    print("⚙️  Critères de sélection du capital:")
    print(f"   • Risque de ruine ≤ {max_ruin_pct}%")
    if min_return_dd is not None:
        print(f"   • Return/DD Ratio ≥ {min_return_dd}")
    else:
        print(f"   • Return/DD Ratio: Aucune contrainte")
    if min_prob_positive is not None:
        print(f"   • Probabilité positive ≥ {min_prob_positive}%")
    else:
        print(f"   • Probabilité positive: Aucune contrainte")
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
    
    # 4. Recalculer les capitaux recommandés avec les critères
    summary_df = recalculate_recommended_capitals_v3(
        summary_df, 
        run_dir, 
        max_ruin_pct,
        min_return_dd,
        min_prob_positive
    )
    print()
    
    # Afficher les statistiques recalculées
    status_counts = summary_df['status'].value_counts().to_dict()
    print(f"📊 Statistiques après recalcul:")
    print(f"   • OK (tous critères satisfaits): {status_counts.get('OK', 0)}")
    print(f"   • WARNING (ruine OK, autres critères non): {status_counts.get('WARNING', 0)}")
    print(f"   • HIGH_RISK (aucun niveau satisfait): {status_counts.get('HIGH_RISK', 0)}")
    
    # Statistiques sur les capitaux
    has_capital = summary_df[summary_df['recommended_capital'] > 0]
    print()
    print(f"💰 Capitaux recommandés:")
    print(f"   • Stratégies avec capital: {len(has_capital)}/{len(summary_df)} ({len(has_capital)/len(summary_df)*100:.1f}%)")
    if len(has_capital) > 0:
        print(f"   • Capital moyen: ${has_capital['recommended_capital'].mean():,.0f}")
        print(f"   • Capital médian: ${has_capital['recommended_capital'].median():,.0f}")
        print(f"   • Capital min: ${has_capital['recommended_capital'].min():,.0f}")
        print(f"   • Capital max: ${has_capital['recommended_capital'].max():,.0f}")
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
    print("💡 Configuration utilisée:")
    print(f"   • Risque de ruine ≤ {max_ruin_pct}%")
    if min_return_dd is not None:
        print(f"   • Return/DD Ratio ≥ {min_return_dd}")
    if min_prob_positive is not None:
        print(f"   • Probabilité positive ≥ {min_prob_positive}%")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Génère des rapports HTML Monte Carlo (version entièrement paramétrable)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:

  # Configuration par défaut (Kevin Davey: Ruine ≤10%)
  python monte_carlo_html_generator_v3.py

  # Personnaliser le seuil de ruine uniquement
  python monte_carlo_html_generator_v3.py --max-ruin 15

  # Configuration Kevin Davey complète
  python monte_carlo_html_generator_v3.py --max-ruin 10 --min-return-dd 2.0 --min-prob-positive 80

  # Configuration conservatrice
  python monte_carlo_html_generator_v3.py --max-ruin 5 --min-return-dd 2.5 --min-prob-positive 85

  # Configuration agressive
  python monte_carlo_html_generator_v3.py --max-ruin 15 --min-return-dd 1.5 --min-prob-positive 70

  # Ruine + Return/DD seulement (pas de contrainte sur probabilité)
  python monte_carlo_html_generator_v3.py --max-ruin 10 --min-return-dd 2.5
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
        main_v3(
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
