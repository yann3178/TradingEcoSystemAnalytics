"""
Simulateur Monte Carlo V2 pour stratégies de trading.
Basé sur la méthodologie Kevin Davey.

Évalue le risque de ruine et détermine le capital minimum requis
pour trader avec un risque acceptable.
"""

import numpy as np
import pandas as pd
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from datetime import datetime
import json
import random
from pathlib import Path

from .config import DEFAULT_CONFIG, STATUS_OK, STATUS_WARNING, STATUS_HIGH_RISK
from .data_loader import (
    load_trades_for_monte_carlo,
    detect_file_format,
    get_strategy_name,
)


@dataclass
class SimulationResult:
    """Résultat d'une simulation individuelle."""
    ruined: bool
    final_equity: float
    max_drawdown: float
    max_drawdown_pct: float
    profit: float
    return_pct: float
    equity_curve: np.ndarray = field(default_factory=lambda: np.array([]))


@dataclass
class CapitalLevelResult:
    """Résultats agrégés pour un niveau de capital."""
    start_equity: float
    ruin_probability: float
    median_drawdown_pct: float
    median_profit: float
    median_return_pct: float
    return_dd_ratio: float
    prob_positive: float
    
    # Statistiques supplémentaires
    mean_profit: float = 0.0
    std_profit: float = 0.0
    percentile_5_profit: float = 0.0
    percentile_95_profit: float = 0.0
    
    # Pour la visualisation
    all_final_equities: np.ndarray = field(default_factory=lambda: np.array([]))
    all_drawdowns: np.ndarray = field(default_factory=lambda: np.array([]))


class MonteCarloSimulator:
    """
    Simulateur Monte Carlo pour évaluer le risque d'une stratégie de trading.
    
    Utilisation:
        mc = MonteCarloSimulator('path/to/strategy.txt')
        results = mc.run()
        mc.print_summary()
        mc.export_csv('results.csv')
    """
    
    def __init__(
        self,
        strategy_file: str,
        capital_minimum: float = None,
        capital_increment: float = None,
        nb_capital_levels: int = None,
        nb_simulations: int = None,
        ruin_threshold_pct: float = None,
        trades_per_year: Optional[int] = None,
        random_seed: Optional[int] = None,
        strategy_name: Optional[str] = None,
        symbol: Optional[str] = None,
    ):
        """
        Initialise le simulateur.
        
        Args:
            strategy_file: Chemin vers le fichier de stratégie
            capital_minimum: Capital de départ minimum
            capital_increment: Incrément entre niveaux de capital
            nb_capital_levels: Nombre de niveaux de capital à tester
            nb_simulations: Nombre de simulations par niveau
            ruin_threshold_pct: Seuil de ruine en % du capital
            trades_per_year: Nombre de trades à simuler par an (auto si None)
            random_seed: Seed pour reproductibilité (None = aléatoire)
            strategy_name: Nom de la stratégie (pour fichiers multi-stratégies)
            symbol: Symbole de l'instrument (pour fichiers multi-stratégies)
        """
        # Paramètres avec valeurs par défaut
        self.capital_minimum = capital_minimum or DEFAULT_CONFIG['capital_minimum']
        self.capital_increment = capital_increment or DEFAULT_CONFIG['capital_increment']
        self.nb_capital_levels = nb_capital_levels or DEFAULT_CONFIG['nb_capital_levels']
        self.nb_simulations = nb_simulations or DEFAULT_CONFIG['nb_simulations']
        self.ruin_threshold_pct = ruin_threshold_pct or DEFAULT_CONFIG['ruin_threshold_pct']
        self.random_seed = random_seed if random_seed is not None else DEFAULT_CONFIG['random_seed']
        
        # Charger les données
        self.strategy_file = strategy_file
        self.file_format = detect_file_format(strategy_file)
        
        self.trades_pnl, self.strategy_stats, detected_format = load_trades_for_monte_carlo(
            filepath=strategy_file,
            strategy_name=strategy_name,
            symbol=symbol
        )
        
        self.strategy_name = self.strategy_stats.get('strategy_name', get_strategy_name(strategy_file))
        
        # Nombre de trades par an
        if trades_per_year is not None:
            self.trades_per_year = trades_per_year
        else:
            self.trades_per_year = int(self.strategy_stats.get('trades_per_year', 30))
        
        # Résultats
        self.results: List[CapitalLevelResult] = []
        self.run_timestamp: Optional[datetime] = None
        self.recommended_capital: Optional[float] = None
        self.status: str = STATUS_HIGH_RISK
        
        # Seed aléatoire
        if self.random_seed is not None:
            np.random.seed(self.random_seed)
            random.seed(self.random_seed)
    
    def _simulate_one_year(
        self, 
        start_equity: float, 
        ruin_level: float,
        store_curve: bool = False
    ) -> SimulationResult:
        """
        Simule une année de trading.
        """
        trades = np.random.choice(self.trades_pnl, size=self.trades_per_year, replace=True)
        
        equity = start_equity
        max_equity = start_equity
        min_equity_from_peak = start_equity
        ruined = False
        
        if store_curve:
            equity_curve = [start_equity]
        
        for trade in trades:
            equity += trade
            
            if equity > max_equity:
                max_equity = equity
            
            if equity < min_equity_from_peak:
                min_equity_from_peak = equity
            
            if store_curve:
                equity_curve.append(equity)
            
            if equity <= ruin_level:
                ruined = True
                break
        
        max_drawdown = max_equity - min_equity_from_peak
        max_drawdown_pct = max_drawdown / max_equity if max_equity > 0 else 0
        profit = equity - start_equity
        return_pct = profit / start_equity if start_equity > 0 else 0
        
        return SimulationResult(
            ruined=ruined,
            final_equity=equity,
            max_drawdown=max_drawdown,
            max_drawdown_pct=max_drawdown_pct,
            profit=profit,
            return_pct=return_pct,
            equity_curve=np.array(equity_curve) if store_curve else np.array([])
        )
    
    def _simulate_capital_level(
        self, 
        start_equity: float,
        store_sample_curves: int = 0
    ) -> CapitalLevelResult:
        """
        Lance toutes les simulations pour un niveau de capital donné.
        """
        ruin_level = start_equity * self.ruin_threshold_pct
        
        results = []
        sample_curves = []
        
        for i in range(self.nb_simulations):
            store_curve = i < store_sample_curves
            result = self._simulate_one_year(start_equity, ruin_level, store_curve)
            results.append(result)
            
            if store_curve:
                sample_curves.append(result.equity_curve)
        
        # Agréger les résultats
        ruined_count = sum(1 for r in results if r.ruined)
        final_equities = np.array([r.final_equity for r in results])
        drawdowns = np.array([r.max_drawdown_pct for r in results])
        profits = np.array([r.profit for r in results])
        returns = np.array([r.return_pct for r in results])
        
        ruin_probability = ruined_count / self.nb_simulations
        median_drawdown_pct = np.median(drawdowns)
        median_profit = np.median(profits)
        median_return_pct = np.median(returns)
        
        return_dd_ratio = median_return_pct / median_drawdown_pct if median_drawdown_pct > 0 else float('inf')
        prob_positive = (profits > 0).sum() / self.nb_simulations
        
        return CapitalLevelResult(
            start_equity=start_equity,
            ruin_probability=ruin_probability,
            median_drawdown_pct=median_drawdown_pct,
            median_profit=median_profit,
            median_return_pct=median_return_pct,
            return_dd_ratio=return_dd_ratio,
            prob_positive=prob_positive,
            mean_profit=np.mean(profits),
            std_profit=np.std(profits),
            percentile_5_profit=np.percentile(profits, 5),
            percentile_95_profit=np.percentile(profits, 95),
            all_final_equities=final_equities,
            all_drawdowns=drawdowns,
        )
    
    def run(self, verbose: bool = True) -> List[CapitalLevelResult]:
        """
        Lance la simulation Monte Carlo complète.
        """
        self.run_timestamp = datetime.now()
        self.results = []
        
        if verbose:
            print(f"🎲 Simulation Monte Carlo - {self.strategy_name}")
            print(f"   Format détecté: {self.file_format}")
            print(f"   {self.nb_simulations} simulations × {self.nb_capital_levels} niveaux de capital")
            print(f"   {self.trades_per_year} trades/an simulés (basé sur {len(self.trades_pnl)} trades historiques)")
            print(f"   Seuil de ruine: {self.ruin_threshold_pct*100:.0f}% du capital")
            print()
        
        for k in range(self.nb_capital_levels):
            start_equity = self.capital_minimum + k * self.capital_increment
            
            if verbose:
                print(f"   Niveau {k+1}/{self.nb_capital_levels}: ${start_equity:,.0f}...", end=" ", flush=True)
            
            result = self._simulate_capital_level(start_equity)
            self.results.append(result)
            
            if verbose:
                print(f"Ruine: {result.ruin_probability*100:.1f}%, Return/DD: {result.return_dd_ratio:.2f}")
        
        self._find_recommended_capital()
        
        if verbose:
            print()
            print(f"✅ Simulation terminée en {(datetime.now() - self.run_timestamp).total_seconds():.1f}s")
        
        return self.results
    
    def _find_recommended_capital(self):
        """Trouve le capital minimum satisfaisant les critères Kevin Davey."""
        for result in self.results:
            if (result.ruin_probability <= DEFAULT_CONFIG['max_acceptable_ruin'] and
                result.return_dd_ratio >= DEFAULT_CONFIG['min_return_dd_ratio'] and
                result.prob_positive >= DEFAULT_CONFIG['min_prob_positive']):
                self.recommended_capital = result.start_equity
                self.status = STATUS_OK
                return
        
        # Vérifier si au moins un niveau passe le test de ruine
        for result in self.results:
            if result.ruin_probability <= DEFAULT_CONFIG['max_acceptable_ruin']:
                self.status = STATUS_WARNING
                return
        
        # Aucun niveau ne satisfait les critères
        self.recommended_capital = None
        self.status = STATUS_HIGH_RISK
    
    def get_results_dataframe(self) -> pd.DataFrame:
        """Retourne les résultats sous forme de DataFrame."""
        if not self.results:
            raise ValueError("Aucun résultat. Lancez run() d'abord.")
        
        data = []
        for r in self.results:
            data.append({
                'Start_Equity': r.start_equity,
                'Ruin_Pct': round(r.ruin_probability * 100, 2),
                'Median_DD_Pct': round(r.median_drawdown_pct * 100, 2),
                'Median_Profit': round(r.median_profit, 2),
                'Median_Return_Pct': round(r.median_return_pct * 100, 2),
                'Return_DD_Ratio': round(r.return_dd_ratio, 2),
                'Prob_Positive_Pct': round(r.prob_positive * 100, 2),
                'Mean_Profit': round(r.mean_profit, 2),
                'Std_Profit': round(r.std_profit, 2),
                'P5_Profit': round(r.percentile_5_profit, 2),
                'P95_Profit': round(r.percentile_95_profit, 2),
            })
        
        return pd.DataFrame(data)
    
    def get_summary(self) -> Dict[str, Any]:
        """Retourne un résumé des résultats pour intégration."""
        if not self.results:
            return {}
        
        best_result = None
        if self.recommended_capital:
            best_result = next(
                (r for r in self.results if r.start_equity == self.recommended_capital),
                self.results[0]
            )
        else:
            best_result = min(self.results, key=lambda r: r.ruin_probability)
        
        return {
            'strategy_name': self.strategy_name,
            'symbol': self.strategy_stats.get('symbol', ''),
            'nb_trades': self.strategy_stats.get('total_trades', len(self.trades_pnl)),
            'trades_per_year': self.trades_per_year,
            'years': self.strategy_stats.get('years', 0),
            'total_pnl': self.strategy_stats.get('total_profit', 0),
            'avg_pnl_trade': self.strategy_stats.get('avg_pnl_trade', 0),
            'std_pnl_trade': self.strategy_stats.get('std_pnl_trade', 0),
            'win_rate': self.strategy_stats.get('win_rate', 0),
            'profit_factor': self.strategy_stats.get('profit_factor', 0),
            'trading_costs': self.strategy_stats.get('total_trading_costs', 0),
            'recommended_capital': self.recommended_capital,
            'status': self.status,
            'ruin_pct': round(best_result.ruin_probability * 100, 2) if best_result else None,
            'return_dd_ratio': round(best_result.return_dd_ratio, 2) if best_result else None,
            'prob_positive': round(best_result.prob_positive * 100, 1) if best_result else None,
            'median_dd_pct': round(best_result.median_drawdown_pct * 100, 1) if best_result else None,
            'median_profit': round(best_result.median_profit, 2) if best_result else None,
            'start_date': self.strategy_stats.get('start_date', ''),
            'end_date': self.strategy_stats.get('end_date', ''),
        }
    
    def print_summary(self):
        """Affiche un résumé des résultats."""
        if not self.results:
            print("Aucun résultat. Lancez run() d'abord.")
            return
        
        print()
        print("=" * 100)
        print(f"📊 RÉSULTATS MONTE CARLO - {self.strategy_name}")
        print("=" * 100)
        print()
        
        stats = self.strategy_stats
        print(f"📈 Stratégie: {self.strategy_name}")
        print(f"   Période: {stats.get('start_date', 'N/A')} → {stats.get('end_date', 'N/A')} ({stats.get('years', 0)} ans)")
        print(f"   Trades: {stats.get('total_trades', 'N/A')} ({stats.get('trades_per_year', 'N/A')}/an)")
        print(f"   Profit total: ${stats.get('total_profit', 0):,.2f}")
        print(f"   Win rate: {stats.get('win_rate', 0):.1f}%")
        print(f"   Profit factor: {stats.get('profit_factor', 0):.2f}")
        print()
        
        print(f"⚙️  Paramètres de simulation:")
        print(f"   Simulations par niveau: {self.nb_simulations}")
        print(f"   Trades simulés/an: {self.trades_per_year}")
        print(f"   Seuil de ruine: {self.ruin_threshold_pct*100:.0f}% du capital")
        print()
        
        print(f"📋 Résultats par niveau de capital:")
        print("-" * 100)
        print(f"{'Start Equity':>14} | {'Ruin %':>8} | {'Med. DD %':>10} | {'Med. Profit':>12} | "
              f"{'Med. Return':>12} | {'Ret/DD':>8} | {'Prob>0':>8}")
        print("-" * 100)
        
        for r in self.results:
            marker = " ✓" if r.start_equity == self.recommended_capital else ""
            
            print(f"${r.start_equity:>12,.0f} | {r.ruin_probability*100:>7.2f}% | "
                  f"{r.median_drawdown_pct*100:>9.2f}% | ${r.median_profit:>10,.0f} | "
                  f"{r.median_return_pct*100:>10.2f}% | {r.return_dd_ratio:>8.2f} | "
                  f"{r.prob_positive*100:>6.1f}%{marker}")
        
        print("-" * 100)
        print()
        
        if self.recommended_capital:
            print(f"✅ CAPITAL RECOMMANDÉ: ${self.recommended_capital:,.0f}")
            print(f"   (Risque ruine ≤10%, Return/DD ≥2, Prob>0 ≥80%)")
        else:
            print("⚠️  AUCUN CAPITAL ne satisfait les critères Kevin Davey")
            best = min(self.results, key=lambda r: r.ruin_probability)
            print(f"   Meilleur niveau testé: ${best.start_equity:,.0f} "
                  f"(Ruine: {best.ruin_probability*100:.1f}%, Return/DD: {best.return_dd_ratio:.2f})")
        
        print()
    
    def export_csv(self, filepath: str, include_metadata: bool = True):
        """Exporte les résultats en CSV."""
        df = self.get_results_dataframe()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            if include_metadata:
                f.write(f"# Monte Carlo Simulation Results\n")
                f.write(f"# Strategy: {self.strategy_name}\n")
                f.write(f"# Generated: {self.run_timestamp.isoformat() if self.run_timestamp else 'N/A'}\n")
                f.write(f"# Simulations per level: {self.nb_simulations}\n")
                f.write(f"# Trades per year: {self.trades_per_year}\n")
                f.write(f"# Ruin threshold: {self.ruin_threshold_pct*100:.0f}%\n")
                if self.recommended_capital:
                    f.write(f"# Recommended capital: {self.recommended_capital}\n")
                f.write(f"#\n")
            
            df.to_csv(f, index=False)
        
        print(f"📁 Résultats exportés: {filepath}")
    
    def export_json(self, filepath: str):
        """Exporte les résultats en JSON."""
        output = {
            'strategy_name': self.strategy_name,
            'strategy_file': self.strategy_file,
            'run_timestamp': self.run_timestamp.isoformat() if self.run_timestamp else None,
            'parameters': {
                'capital_minimum': self.capital_minimum,
                'capital_increment': self.capital_increment,
                'nb_capital_levels': self.nb_capital_levels,
                'nb_simulations': self.nb_simulations,
                'ruin_threshold_pct': self.ruin_threshold_pct,
                'trades_per_year': self.trades_per_year,
            },
            'strategy_stats': self.strategy_stats,
            'recommended_capital': self.recommended_capital,
            'status': self.status,
            'results': [
                {
                    'start_equity': r.start_equity,
                    'ruin_probability': r.ruin_probability,
                    'median_drawdown_pct': r.median_drawdown_pct,
                    'median_profit': r.median_profit,
                    'median_return_pct': r.median_return_pct,
                    'return_dd_ratio': r.return_dd_ratio,
                    'prob_positive': r.prob_positive,
                    'mean_profit': r.mean_profit,
                    'std_profit': r.std_profit,
                    'percentile_5_profit': r.percentile_5_profit,
                    'percentile_95_profit': r.percentile_95_profit,
                }
                for r in self.results
            ]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"📁 Résultats exportés: {filepath}")
