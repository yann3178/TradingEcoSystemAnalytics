#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch Monte Carlo Simulator - Traitement de toutes les stratégies

Ce script charge le fichier consolidé avec coûts UNE SEULE FOIS,
puis exécute les simulations Monte Carlo pour toutes les stratégies.

Performance: ~5 minutes pour 250 stratégies × 2500 simulations × 11 niveaux

Usage:
    python batch_monte_carlo.py                    # Toutes les stratégies
    python batch_monte_carlo.py --symbol GC        # Filtrer par symbole
    python batch_monte_carlo.py --parallel 4       # 4 workers parallèles

Auteur: Yann
Date: 2025-11-26
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
import argparse
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
import warnings

warnings.filterwarnings('ignore')

# Configuration par défaut
DEFAULT_CONFIG = {
    'capital_minimum': 5000,
    'capital_increment': 2500,
    'nb_capital_levels': 11,
    'nb_simulations': 2500,
    'ruin_threshold_pct': 0.40,
    'max_acceptable_ruin': 0.10,
    'min_return_dd_ratio': 2.0,
    'min_prob_positive': 0.80,
}


@dataclass
class StrategyMCResult:
    """Résultat Monte Carlo pour une stratégie."""
    strategy_name: str
    symbol: str
    nb_trades: int
    trades_per_year: float
    total_pnl: float
    avg_pnl_per_trade: float
    std_pnl_per_trade: float
    win_rate: float
    profit_factor: float
    total_trading_costs: float
    
    # Résultats MC
    recommended_capital: Optional[float]
    status: str  # 'OK', 'WARNING', 'HIGH_RISK'
    
    # Détails par niveau de capital
    levels_results: List[Dict] = field(default_factory=list)
    
    # Métadonnées
    start_date: str = ''
    end_date: str = ''
    years: float = 0.0


def find_latest_costs_file(results_dir: Path) -> Path:
    """Trouve le fichier Consolidated_Strategies_COSTS_*.txt le plus récent."""
    pattern = 'Consolidated_Strategies_COSTS_*.txt'
    files = list(results_dir.glob(pattern))
    
    if not files:
        raise FileNotFoundError(
            f"Aucun fichier {pattern} trouvé dans {results_dir}\n"
            "Avez-vous exécuté enrich_with_costs.py ?"
        )
    
    files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return files[0]


def load_all_strategies_data(costs_file: Path) -> pd.DataFrame:
    """
    Charge le fichier consolidé complet en mémoire.
    
    Args:
        costs_file: Chemin vers le fichier avec coûts
        
    Returns:
        DataFrame avec toutes les stratégies
    """
    print(f"📂 Chargement de {costs_file.name}...")
    start_time = time.time()
    
    df = pd.read_csv(
        costs_file,
        sep=';',
        encoding='utf-8-sig',
        decimal=',',
        low_memory=False
    )
    
    # Convertir les colonnes numériques
    numeric_cols = ['DailyProfit', 'Net_Profit', 'Trading_Costs', 'Commission', 
                    'Slippage', 'Daily_Trades', 'Total_Strategy_Trades']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Convertir les dates
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
    
    elapsed = time.time() - start_time
    print(f"   ✓ {len(df):,} lignes chargées en {elapsed:.1f}s")
    print(f"   ✓ {df['Strategy_Name'].nunique()} stratégies détectées")
    
    return df


def reconstruct_trades_for_strategy(strategy_df: pd.DataFrame) -> Tuple[np.ndarray, Dict]:
    """
    Reconstitue les trades pour une stratégie.
    
    Args:
        strategy_df: DataFrame filtré pour une stratégie (déjà trié par date)
        
    Returns:
        Tuple (array des P&L par trade, dict des stats)
    """
    # S'assurer du tri par date
    strategy_df = strategy_df.sort_values('Date').reset_index(drop=True)
    
    trades = []
    current_pnl = 0.0
    current_costs = 0.0
    current_start_date = None
    trade_days = 0
    
    for idx, row in strategy_df.iterrows():
        net_profit = row['Net_Profit']
        daily_trades = row['Daily_Trades']
        trading_costs = row.get('Trading_Costs', 0)
        
        has_activity = (net_profit != 0) or (daily_trades > 0)
        
        if has_activity:
            if current_start_date is None:
                current_start_date = row['Date']
            
            current_pnl += net_profit
            current_costs += trading_costs
            trade_days += 1
            
            if daily_trades > 0:
                trades.append({
                    'start_date': current_start_date,
                    'end_date': row['Date'],
                    'net_profit': current_pnl,
                    'trading_costs': current_costs,
                    'duration': trade_days,
                })
                
                current_pnl = 0.0
                current_costs = 0.0
                current_start_date = None
                trade_days = 0
    
    if not trades:
        return np.array([]), {}
    
    trades_df = pd.DataFrame(trades)
    net_profits = trades_df['net_profit'].values
    
    # Calculer les stats
    start_date = trades_df['start_date'].min()
    end_date = trades_df['end_date'].max()
    total_days = (end_date - start_date).days if pd.notna(start_date) and pd.notna(end_date) else 1
    years = max(total_days / 365.25, 0.1)
    
    winners = (net_profits > 0).sum()
    losers = (net_profits < 0).sum()
    gross_profit = net_profits[net_profits > 0].sum()
    gross_loss = abs(net_profits[net_profits < 0].sum())
    
    stats = {
        'nb_trades': len(trades),
        'trades_per_year': len(trades) / years,
        'total_pnl': net_profits.sum(),
        'avg_pnl': net_profits.mean(),
        'std_pnl': net_profits.std() if len(net_profits) > 1 else 0,
        'win_rate': winners / len(trades) * 100 if trades else 0,
        'profit_factor': gross_profit / gross_loss if gross_loss > 0 else float('inf'),
        'total_costs': trades_df['trading_costs'].sum(),
        'start_date': start_date.strftime('%Y-%m-%d') if pd.notna(start_date) else 'N/A',
        'end_date': end_date.strftime('%Y-%m-%d') if pd.notna(end_date) else 'N/A',
        'years': years,
    }
    
    return net_profits, stats


def run_monte_carlo_simulation(
    trades_pnl: np.ndarray,
    trades_per_year: int,
    config: Dict
) -> List[Dict]:
    """
    Exécute la simulation Monte Carlo pour une stratégie.
    
    Args:
        trades_pnl: Array des P&L par trade
        trades_per_year: Nombre de trades à simuler par an
        config: Configuration (capital_min, increment, etc.)
        
    Returns:
        Liste des résultats par niveau de capital
    """
    results = []
    
    capital_min = config['capital_minimum']
    increment = config['capital_increment']
    nb_levels = config['nb_capital_levels']
    nb_sims = config['nb_simulations']
    ruin_pct = config['ruin_threshold_pct']
    
    for k in range(nb_levels):
        start_equity = capital_min + k * increment
        ruin_level = start_equity * ruin_pct
        
        # Vectorisation: générer toutes les simulations d'un coup
        # Shape: (nb_sims, trades_per_year)
        all_trades = np.random.choice(trades_pnl, size=(nb_sims, trades_per_year), replace=True)
        
        # Calculer les equity curves cumulées
        equity_curves = start_equity + np.cumsum(all_trades, axis=1)
        
        # Détecter les ruines (equity passe sous le seuil)
        ruined = np.any(equity_curves <= ruin_level, axis=1)
        ruin_count = ruined.sum()
        
        # Calculer les drawdowns max pour chaque simulation
        running_max = np.maximum.accumulate(equity_curves, axis=1)
        drawdowns = (running_max - equity_curves) / running_max
        max_drawdowns = np.max(drawdowns, axis=1)
        
        # Profits finaux
        final_equities = equity_curves[:, -1]
        profits = final_equities - start_equity
        returns = profits / start_equity
        
        # Métriques agrégées
        ruin_probability = ruin_count / nb_sims
        median_dd = np.median(max_drawdowns)
        median_profit = np.median(profits)
        median_return = np.median(returns)
        return_dd_ratio = median_return / median_dd if median_dd > 0 else float('inf')
        prob_positive = (profits > 0).sum() / nb_sims
        
        results.append({
            'start_equity': start_equity,
            'ruin_probability': ruin_probability,
            'median_drawdown_pct': median_dd,
            'median_profit': median_profit,
            'median_return_pct': median_return,
            'return_dd_ratio': return_dd_ratio,
            'prob_positive': prob_positive,
            'mean_profit': np.mean(profits),
            'std_profit': np.std(profits),
            'p5_profit': np.percentile(profits, 5),
            'p95_profit': np.percentile(profits, 95),
        })
    
    return results


def determine_recommendation(levels_results: List[Dict], config: Dict) -> Tuple[Optional[float], str]:
    """
    Détermine le capital recommandé et le statut.
    
    Args:
        levels_results: Résultats par niveau de capital
        config: Configuration avec les seuils
        
    Returns:
        Tuple (capital_recommandé, statut)
    """
    max_ruin = config['max_acceptable_ruin']
    min_return_dd = config['min_return_dd_ratio']
    min_prob_pos = config['min_prob_positive']
    
    for result in levels_results:
        if (result['ruin_probability'] <= max_ruin and
            result['return_dd_ratio'] >= min_return_dd and
            result['prob_positive'] >= min_prob_pos):
            return result['start_equity'], 'OK'
    
    # Pas de capital satisfaisant tous les critères
    # Chercher le meilleur compromis
    best = min(levels_results, key=lambda r: r['ruin_probability'])
    
    if best['ruin_probability'] <= max_ruin:
        return best['start_equity'], 'WARNING'  # Ruine OK mais Return/DD ou Prob faible
    else:
        return None, 'HIGH_RISK'  # Même le plus haut capital a trop de risque


def process_single_strategy(
    strategy_name: str,
    symbol: str,
    strategy_df: pd.DataFrame,
    config: Dict
) -> Optional[StrategyMCResult]:
    """
    Traite une stratégie complète (reconstitution + MC).
    
    Args:
        strategy_name: Nom de la stratégie
        symbol: Symbole de l'instrument
        strategy_df: DataFrame de la stratégie
        config: Configuration MC
        
    Returns:
        StrategyMCResult ou None si erreur
    """
    try:
        # Reconstituer les trades
        trades_pnl, stats = reconstruct_trades_for_strategy(strategy_df)
        
        if len(trades_pnl) < 10:
            return None  # Pas assez de trades
        
        # Nombre de trades par an à simuler
        trades_per_year = max(1, int(stats['trades_per_year']))
        
        # Lancer la simulation MC
        levels_results = run_monte_carlo_simulation(trades_pnl, trades_per_year, config)
        
        # Déterminer la recommandation
        recommended_capital, status = determine_recommendation(levels_results, config)
        
        return StrategyMCResult(
            strategy_name=strategy_name,
            symbol=symbol,
            nb_trades=stats['nb_trades'],
            trades_per_year=stats['trades_per_year'],
            total_pnl=stats['total_pnl'],
            avg_pnl_per_trade=stats['avg_pnl'],
            std_pnl_per_trade=stats['std_pnl'],
            win_rate=stats['win_rate'],
            profit_factor=stats['profit_factor'],
            total_trading_costs=stats['total_costs'],
            recommended_capital=recommended_capital,
            status=status,
            levels_results=levels_results,
            start_date=stats['start_date'],
            end_date=stats['end_date'],
            years=stats['years'],
        )
        
    except Exception as e:
        print(f"      ⚠️ Erreur {strategy_name}: {e}")
        return None


def run_batch_monte_carlo(
    df: pd.DataFrame,
    config: Dict,
    symbol_filter: str = None,
    verbose: bool = True
) -> List[StrategyMCResult]:
    """
    Exécute le Monte Carlo pour toutes les stratégies.
    
    Args:
        df: DataFrame complet avec toutes les stratégies
        config: Configuration MC
        symbol_filter: Filtrer par symbole (optionnel)
        verbose: Afficher la progression
        
    Returns:
        Liste des résultats par stratégie
    """
    # Filtrer par symbole si demandé
    if symbol_filter:
        df = df[df['Symbol'] == symbol_filter]
        if verbose:
            print(f"   Filtré par Symbol='{symbol_filter}': {len(df):,} lignes")
    
    # Identifier les stratégies uniques
    strategies = df.groupby(['Symbol', 'Strategy_Name']).size().reset_index(name='count')
    n_strategies = len(strategies)
    
    if verbose:
        print(f"\n🎲 Lancement Monte Carlo pour {n_strategies} stratégies")
        print(f"   {config['nb_simulations']} simulations × {config['nb_capital_levels']} niveaux")
        print()
    
    results = []
    start_time = time.time()
    
    for idx, row in strategies.iterrows():
        symbol = row['Symbol']
        strategy_name = row['Strategy_Name']
        
        if verbose:
            progress = (idx + 1) / n_strategies * 100
            print(f"\r   [{progress:5.1f}%] {symbol}_{strategy_name}...", end="", flush=True)
        
        # Filtrer les données de cette stratégie
        mask = (df['Symbol'] == symbol) & (df['Strategy_Name'] == strategy_name)
        strategy_df = df[mask].copy()
        
        # Traiter la stratégie
        result = process_single_strategy(strategy_name, symbol, strategy_df, config)
        
        if result:
            results.append(result)
    
    elapsed = time.time() - start_time
    
    if verbose:
        print()
        print()
        print(f"✅ {len(results)}/{n_strategies} stratégies traitées en {elapsed:.1f}s")
        
        # Résumé par statut
        status_counts = {}
        for r in results:
            status_counts[r.status] = status_counts.get(r.status, 0) + 1
        
        print(f"   📊 OK: {status_counts.get('OK', 0)}, "
              f"WARNING: {status_counts.get('WARNING', 0)}, "
              f"HIGH_RISK: {status_counts.get('HIGH_RISK', 0)}")
    
    return results


def export_summary_csv(results: List[StrategyMCResult], output_file: Path):
    """
    Exporte le résumé (1 ligne par stratégie).
    
    Args:
        results: Liste des résultats MC
        output_file: Fichier de sortie
    """
    data = []
    for r in results:
        # Trouver le niveau correspondant au capital recommandé
        rec_level = None
        if r.recommended_capital:
            for lvl in r.levels_results:
                if lvl['start_equity'] == r.recommended_capital:
                    rec_level = lvl
                    break
        
        # Si pas de capital recommandé, prendre le dernier niveau testé
        if rec_level is None and r.levels_results:
            rec_level = r.levels_results[-1]
        
        data.append({
            'Strategy_Name': r.strategy_name,
            'Symbol': r.symbol,
            'Nb_Trades': r.nb_trades,
            'Trades_Year': round(r.trades_per_year, 1),
            'Years': round(r.years, 1),
            'Total_PnL': round(r.total_pnl, 2),
            'Avg_PnL_Trade': round(r.avg_pnl_per_trade, 2),
            'Std_PnL_Trade': round(r.std_pnl_per_trade, 2),
            'Win_Rate': round(r.win_rate, 1),
            'Profit_Factor': round(r.profit_factor, 2),
            'Trading_Costs': round(r.total_trading_costs, 2),
            'Recommended_Capital': r.recommended_capital or 'N/A',
            'Status': r.status,
            'Ruin_Pct': round(rec_level['ruin_probability'] * 100, 2) if rec_level else 'N/A',
            'Return_DD_Ratio': round(rec_level['return_dd_ratio'], 2) if rec_level else 'N/A',
            'Prob_Positive': round(rec_level['prob_positive'] * 100, 1) if rec_level else 'N/A',
            'Median_DD_Pct': round(rec_level['median_drawdown_pct'] * 100, 1) if rec_level else 'N/A',
            'Median_Profit': round(rec_level['median_profit'], 2) if rec_level else 'N/A',
            'Start_Date': r.start_date,
            'End_Date': r.end_date,
        })
    
    df = pd.DataFrame(data)
    
    # Trier par statut puis par Return/DD
    status_order = {'OK': 0, 'WARNING': 1, 'HIGH_RISK': 2}
    df['_status_order'] = df['Status'].map(status_order)
    df = df.sort_values(['_status_order', 'Return_DD_Ratio'], ascending=[True, False])
    df = df.drop('_status_order', axis=1)
    
    # Sauvegarder en format français
    df.to_csv(output_file, sep=';', index=False, decimal=',', encoding='utf-8-sig')
    
    print(f"📁 Summary exporté: {output_file.name}")


def export_details_csv(results: List[StrategyMCResult], output_file: Path):
    """
    Exporte les détails (11 lignes par stratégie).
    
    Args:
        results: Liste des résultats MC
        output_file: Fichier de sortie
    """
    data = []
    for r in results:
        for lvl in r.levels_results:
            data.append({
                'Strategy_Name': r.strategy_name,
                'Symbol': r.symbol,
                'Start_Equity': lvl['start_equity'],
                'Ruin_Pct': round(lvl['ruin_probability'] * 100, 2),
                'Median_DD_Pct': round(lvl['median_drawdown_pct'] * 100, 2),
                'Median_Profit': round(lvl['median_profit'], 2),
                'Median_Return_Pct': round(lvl['median_return_pct'] * 100, 2),
                'Return_DD_Ratio': round(lvl['return_dd_ratio'], 2),
                'Prob_Positive_Pct': round(lvl['prob_positive'] * 100, 1),
                'Mean_Profit': round(lvl['mean_profit'], 2),
                'Std_Profit': round(lvl['std_profit'], 2),
                'P5_Profit': round(lvl['p5_profit'], 2),
                'P95_Profit': round(lvl['p95_profit'], 2),
            })
    
    df = pd.DataFrame(data)
    df.to_csv(output_file, sep=';', index=False, decimal=',', encoding='utf-8-sig')
    
    print(f"📁 Details exporté: {output_file.name}")


def export_individual_csv(result: StrategyMCResult, output_dir: Path) -> Path:
    """
    Exporte le CSV individuel pour une stratégie.
    
    Args:
        result: Résultat MC d'une stratégie
        output_dir: Répertoire de sortie
        
    Returns:
        Path du fichier créé
    """
    filename = f"{result.symbol}_{result.strategy_name}_MC.csv"
    output_file = output_dir / filename
    
    # Construire les données
    data = []
    for lvl in result.levels_results:
        data.append({
            'Start_Equity': lvl['start_equity'],
            'Ruin_Pct': round(lvl['ruin_probability'] * 100, 2),
            'Median_DD_Pct': round(lvl['median_drawdown_pct'] * 100, 2),
            'Median_Profit': round(lvl['median_profit'], 2),
            'Median_Return_Pct': round(lvl['median_return_pct'] * 100, 2),
            'Return_DD_Ratio': round(lvl['return_dd_ratio'], 2),
            'Prob_Positive_Pct': round(lvl['prob_positive'] * 100, 1),
            'Mean_Profit': round(lvl['mean_profit'], 2),
            'Std_Profit': round(lvl['std_profit'], 2),
            'P5_Profit': round(lvl['p5_profit'], 2),
            'P95_Profit': round(lvl['p95_profit'], 2),
        })
    
    df = pd.DataFrame(data)
    
    # Écrire avec métadonnées en commentaires
    with open(output_file, 'w', encoding='utf-8-sig') as f:
        f.write(f"# Monte Carlo Simulation - {result.symbol}_{result.strategy_name}\n")
        f.write(f"# Trades: {result.nb_trades} ({result.trades_per_year:.1f}/an)\n")
        f.write(f"# Period: {result.start_date} to {result.end_date}\n")
        f.write(f"# Total P&L: {result.total_pnl:.2f}\n")
        f.write(f"# Win Rate: {result.win_rate:.1f}%\n")
        f.write(f"# Recommended Capital: {result.recommended_capital or 'N/A'}\n")
        f.write(f"# Status: {result.status}\n")
        f.write(f"#\n")
        df.to_csv(f, sep=';', index=False, decimal=',')
    
    return output_file


def export_all_individual_reports(
    results: List[StrategyMCResult],
    output_dir: Path,
    config: Dict,
    generate_html: bool = True,
    verbose: bool = True
):
    """
    Exporte les rapports individuels (CSV + HTML) pour chaque stratégie.
    
    Args:
        results: Liste des résultats MC
        output_dir: Répertoire de sortie
        config: Configuration utilisée
        generate_html: Générer aussi les fichiers HTML
        verbose: Afficher la progression
    """
    # Créer le sous-répertoire pour les rapports individuels
    individual_dir = output_dir / 'Individual'
    individual_dir.mkdir(parents=True, exist_ok=True)
    
    if verbose:
        print(f"\n📂 Génération des rapports individuels dans: {individual_dir.name}/")
    
    # Import conditionnel pour éviter les dépendances circulaires
    if generate_html:
        from individual_visualizer import generate_individual_html_report
    
    csv_count = 0
    html_count = 0
    
    for i, result in enumerate(results):
        if verbose:
            progress = (i + 1) / len(results) * 100
            print(f"\r   [{progress:5.1f}%] {result.symbol}_{result.strategy_name}...", end="", flush=True)
        
        # CSV individuel
        try:
            export_individual_csv(result, individual_dir)
            csv_count += 1
        except Exception as e:
            if verbose:
                print(f"\n      ⚠️ Erreur CSV: {e}")
        
        # HTML individuel
        if generate_html:
            try:
                html_file = individual_dir / f"{result.symbol}_{result.strategy_name}_MC.html"
                generate_individual_html_report(result, str(html_file), config)
                html_count += 1
            except Exception as e:
                if verbose:
                    print(f"\n      ⚠️ Erreur HTML: {e}")
    
    if verbose:
        print()
        print(f"   ✓ {csv_count} fichiers CSV générés")
        if generate_html:
            print(f"   ✓ {html_count} fichiers HTML générés")


def main():
    """Point d'entrée principal."""
    
    parser = argparse.ArgumentParser(
        description='Batch Monte Carlo Simulator pour toutes les stratégies',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python batch_monte_carlo.py                     # Toutes les stratégies
  python batch_monte_carlo.py --symbol GC         # Stratégies Gold uniquement
  python batch_monte_carlo.py --simulations 5000  # Plus de simulations
        """
    )
    
    parser.add_argument('--base-dir', default=r'C:\TradeData',
                        help='Répertoire de base')
    parser.add_argument('--symbol', help='Filtrer par symbole')
    parser.add_argument('--capital-min', type=float, default=DEFAULT_CONFIG['capital_minimum'],
                        help='Capital minimum')
    parser.add_argument('--increment', type=float, default=DEFAULT_CONFIG['capital_increment'],
                        help='Incrément de capital')
    parser.add_argument('--levels', type=int, default=DEFAULT_CONFIG['nb_capital_levels'],
                        help='Nombre de niveaux de capital')
    parser.add_argument('--simulations', type=int, default=DEFAULT_CONFIG['nb_simulations'],
                        help='Nombre de simulations par niveau')
    parser.add_argument('--ruin-threshold', type=float, default=DEFAULT_CONFIG['ruin_threshold_pct'] * 100,
                        help='Seuil de ruine en %%')
    parser.add_argument('--html', action='store_true', help='Générer rapport HTML global')
    parser.add_argument('--individual', action='store_true', 
                        help='Générer rapports individuels (CSV + HTML) pour chaque stratégie')
    parser.add_argument('--all-reports', action='store_true',
                        help='Générer tous les rapports (global + individuels)')
    parser.add_argument('-q', '--quiet', action='store_true', help='Mode silencieux')
    
    args = parser.parse_args()
    
    # Configuration
    config = {
        'capital_minimum': args.capital_min,
        'capital_increment': args.increment,
        'nb_capital_levels': args.levels,
        'nb_simulations': args.simulations,
        'ruin_threshold_pct': args.ruin_threshold / 100,
        'max_acceptable_ruin': DEFAULT_CONFIG['max_acceptable_ruin'],
        'min_return_dd_ratio': DEFAULT_CONFIG['min_return_dd_ratio'],
        'min_prob_positive': DEFAULT_CONFIG['min_prob_positive'],
    }
    
    base_dir = Path(args.base_dir)
    results_dir = base_dir / 'Results'
    output_dir = results_dir / 'MonteCarlo'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    verbose = not args.quiet
    
    if verbose:
        print("=" * 70)
        print("🎲 BATCH MONTE CARLO SIMULATOR")
        print("=" * 70)
        print()
        print(f"📂 Base directory: {base_dir}")
        print(f"📂 Output directory: {output_dir}")
        print()
        print(f"⚙️  Configuration:")
        print(f"   Capital: {config['capital_minimum']:,} → "
              f"{config['capital_minimum'] + (config['nb_capital_levels']-1) * config['capital_increment']:,}")
        print(f"   Simulations: {config['nb_simulations']:,} × {config['nb_capital_levels']} niveaux")
        print(f"   Seuil ruine: {config['ruin_threshold_pct']*100:.0f}%")
        print()
    
    try:
        # Trouver et charger le fichier
        costs_file = find_latest_costs_file(results_dir)
        df = load_all_strategies_data(costs_file)
        
        # Lancer le batch MC
        results = run_batch_monte_carlo(df, config, args.symbol, verbose)
        
        if not results:
            print("❌ Aucune stratégie traitée")
            return 1
        
        # Exporter les résultats
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        
        summary_file = output_dir / f"MC_Summary_{timestamp}.csv"
        export_summary_csv(results, summary_file)
        
        details_file = output_dir / f"MC_Details_{timestamp}.csv"
        export_details_csv(results, details_file)
        
        # Rapport HTML global
        if args.html or args.all_reports:
            from batch_visualizer import generate_batch_html_report
            html_file = output_dir / f"MC_Report_{timestamp}.html"
            generate_batch_html_report(results, html_file, config)
            
            # Créer un lien symbolique vers le dernier rapport (pour les liens retour)
            latest_link = output_dir / "MC_Report_latest.html"
            try:
                if latest_link.exists():
                    latest_link.unlink()
                # Sur Windows, copier au lieu de symlink
                import shutil
                shutil.copy(html_file, latest_link)
            except Exception:
                pass  # Ignorer les erreurs de lien
        
        # Rapports individuels (CSV + HTML pour chaque stratégie)
        if args.individual or args.all_reports:
            export_all_individual_reports(
                results=results,
                output_dir=output_dir,
                config=config,
                generate_html=True,
                verbose=verbose
            )
        
        if verbose:
            print()
            print("=" * 70)
            print("✅ BATCH MONTE CARLO TERMINÉ")
            print("=" * 70)
            print(f"📁 Fichiers générés dans: {output_dir}")
        
        return 0
        
    except FileNotFoundError as e:
        print(f"❌ ERREUR: {e}")
        return 1
    except Exception as e:
        print(f"❌ ERREUR INATTENDUE: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
