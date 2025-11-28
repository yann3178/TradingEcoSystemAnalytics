"""
Module de chargement des fichiers de stratégie pour Monte Carlo V2.
Gère le parsing des fichiers:
- Titan/MultiCharts (.txt avec 6 colonnes)
- Fichiers extraits pour Monte Carlo (.csv avec Net_Profit par trade)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Optional, Dict, Any

from .config import FILE_FORMAT_TITAN, FILE_FORMAT_EXTRACTED


def detect_file_format(filepath: str) -> str:
    """
    Détecte le format du fichier de stratégie.
    
    Args:
        filepath: Chemin vers le fichier
        
    Returns:
        'titan' pour fichier Titan/MultiCharts original
        'extracted' pour fichier CSV extrait avec trades reconstitués
    """
    path = Path(filepath)
    
    # Lire les premières lignes pour détecter le format
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            first_line = f.readline().strip()
    except UnicodeDecodeError:
        with open(filepath, 'r', encoding='latin-1') as f:
            first_line = f.readline().strip()
    
    # Si la première ligne contient des headers avec Net_Profit, c'est un fichier extrait
    if 'Net_Profit' in first_line or 'Strategy_Name' in first_line:
        return 'extracted'
    
    # Sinon c'est un fichier Titan (6 colonnes numériques)
    return 'titan'


def load_extracted_trades_file(filepath: str) -> pd.DataFrame:
    """
    Charge un fichier CSV de trades extraits.
    
    Args:
        filepath: Chemin vers le fichier CSV
        
    Returns:
        DataFrame avec les trades
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Fichier non trouvé: {filepath}")
    
    # Format français: ; comme séparateur, , comme décimal
    df = pd.read_csv(
        filepath,
        sep=FILE_FORMAT_EXTRACTED['separator'],
        encoding=FILE_FORMAT_EXTRACTED['encoding'],
        decimal=FILE_FORMAT_EXTRACTED['decimal']
    )
    
    # Convertir les dates
    date_format = FILE_FORMAT_EXTRACTED['date_format']
    if 'Start_Date' in df.columns:
        df['Start_Date'] = pd.to_datetime(df['Start_Date'], format=date_format, errors='coerce')
    if 'End_Date' in df.columns:
        df['End_Date'] = pd.to_datetime(df['End_Date'], format=date_format, errors='coerce')
    
    return df


def load_strategy_file(filepath: str) -> pd.DataFrame:
    """
    Charge un fichier de stratégie au format Titan/MultiCharts.
    
    Args:
        filepath: Chemin vers le fichier .txt
        
    Returns:
        DataFrame avec les colonnes: Date, DailyProfit, Contracts, Gap, Range, CumulativeTrades
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Fichier non trouvé: {filepath}")
    
    df = pd.read_csv(
        filepath,
        sep=FILE_FORMAT_TITAN['separator'],
        header=None,
        names=FILE_FORMAT_TITAN['columns'],
        encoding=FILE_FORMAT_TITAN['encoding']
    )
    
    # Convertir la date
    df['Date'] = pd.to_datetime(df['Date'], format=FILE_FORMAT_TITAN['date_format'])
    
    return df


def extract_daily_pnl(df: pd.DataFrame) -> np.ndarray:
    """
    Extrait les P&L journaliers non-nuls pour la simulation Monte Carlo.
    
    Args:
        df: DataFrame de la stratégie
        
    Returns:
        Array numpy des P&L journaliers non-nuls
    """
    daily_pnl = df[df['DailyProfit'] != 0]['DailyProfit'].values
    return daily_pnl


def get_strategy_name(filepath: str) -> str:
    """
    Extrait le nom de la stratégie depuis le chemin du fichier.
    
    Args:
        filepath: Chemin vers le fichier
        
    Returns:
        Nom de la stratégie
    """
    path = Path(filepath)
    return path.stem


def calculate_trades_stats(trades_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calcule les statistiques descriptives depuis un DataFrame de trades.
    
    Args:
        trades_df: DataFrame avec les trades
        
    Returns:
        Dictionnaire de statistiques
    """
    # Période
    if 'Start_Date' in trades_df.columns:
        start_date = trades_df['Start_Date'].min()
        end_date = trades_df['End_Date'].max()
    elif 'End_Date' in trades_df.columns:
        start_date = trades_df['End_Date'].min()
        end_date = trades_df['End_Date'].max()
    else:
        start_date = pd.Timestamp.now()
        end_date = pd.Timestamp.now()
    
    total_days = (end_date - start_date).days if pd.notna(start_date) and pd.notna(end_date) else 0
    years = total_days / 365.25 if total_days > 0 else 1
    
    # Nombre de trades
    total_trades = len(trades_df)
    trades_per_year = total_trades / years if years > 0 else total_trades
    
    # Statistiques P&L
    net_profit = trades_df['Net_Profit'].values
    total_profit = net_profit.sum()
    avg_pnl = net_profit.mean() if len(net_profit) > 0 else 0
    std_pnl = net_profit.std() if len(net_profit) > 0 else 0
    
    # Win rate
    winners = (net_profit > 0).sum()
    losers = (net_profit < 0).sum()
    win_rate = winners / len(net_profit) if len(net_profit) > 0 else 0
    
    # Profit factor
    gross_profit = net_profit[net_profit > 0].sum()
    gross_loss = abs(net_profit[net_profit < 0].sum())
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
    
    # Coûts si disponibles
    total_costs = 0
    if 'Trading_Costs' in trades_df.columns:
        total_costs = trades_df['Trading_Costs'].sum()
    
    return {
        'start_date': start_date.strftime('%Y-%m-%d') if pd.notna(start_date) else 'N/A',
        'end_date': end_date.strftime('%Y-%m-%d') if pd.notna(end_date) else 'N/A',
        'total_days': total_days,
        'years': round(years, 2),
        'total_trades': total_trades,
        'trades_per_year': round(trades_per_year, 1),
        'total_profit': round(total_profit, 2),
        'avg_pnl_trade': round(avg_pnl, 2),
        'std_pnl_trade': round(std_pnl, 2),
        'min_pnl_trade': round(net_profit.min(), 2) if len(net_profit) > 0 else 0,
        'max_pnl_trade': round(net_profit.max(), 2) if len(net_profit) > 0 else 0,
        'winning_trades': int(winners),
        'losing_trades': int(losers),
        'win_rate': round(win_rate * 100, 2),
        'profit_factor': round(profit_factor, 2),
        'total_trading_costs': round(total_costs, 2),
    }


def reconstruct_trades_from_titan(df: pd.DataFrame) -> Tuple[np.ndarray, pd.DataFrame]:
    """
    Reconstitue les trades depuis un fichier Titan (P&L journaliers → P&L par trade).
    
    Args:
        df: DataFrame au format Titan
        
    Returns:
        Tuple (array des P&L par trade, DataFrame des trades reconstitués)
    """
    df = df.copy()
    df['Daily_Trades'] = df['CumulativeTrades'].diff().fillna(0).clip(lower=0).astype(int)
    df = df.sort_values('Date').reset_index(drop=True)
    
    trades = []
    current_pnl = 0.0
    current_start_date = None
    trade_days = 0
    
    for idx, row in df.iterrows():
        daily_profit = row['DailyProfit']
        daily_trades = row['Daily_Trades']
        contracts = row['Contracts']
        
        has_activity = (daily_profit != 0) or (contracts != 0) or (daily_trades > 0)
        
        if has_activity:
            if current_start_date is None:
                current_start_date = row['Date']
            
            current_pnl += daily_profit
            trade_days += 1
            
            if daily_trades > 0:
                trades.append({
                    'Start_Date': current_start_date,
                    'End_Date': row['Date'],
                    'Duration_Days': trade_days,
                    'Net_Profit': current_pnl,
                    'Nb_Trades_Closed': daily_trades,
                })
                
                current_pnl = 0.0
                current_start_date = None
                trade_days = 0
    
    trades_df = pd.DataFrame(trades)
    trades_pnl = trades_df['Net_Profit'].values if len(trades_df) > 0 else np.array([])
    
    return trades_pnl, trades_df


def load_trades_for_monte_carlo(
    filepath: str,
    strategy_name: Optional[str] = None,
    symbol: Optional[str] = None
) -> Tuple[np.ndarray, Dict[str, Any], str]:
    """
    Charge les trades pour une simulation Monte Carlo.
    Détecte automatiquement le format du fichier.
    
    Args:
        filepath: Chemin vers le fichier (Titan .txt ou CSV extrait)
        strategy_name: Nom de la stratégie (requis pour fichiers multi-stratégies)
        symbol: Symbole de l'instrument (requis pour fichiers multi-stratégies)
        
    Returns:
        Tuple (trades_pnl, stats_dict, detected_format)
    """
    file_format = detect_file_format(filepath)
    
    if file_format == 'extracted':
        df = load_extracted_trades_file(filepath)
        
        # Filtrer si nécessaire
        if strategy_name and 'Strategy_Name' in df.columns:
            df = df[df['Strategy_Name'] == strategy_name]
        if symbol and 'Symbol' in df.columns:
            df = df[df['Symbol'] == symbol]
        
        if len(df) == 0:
            raise ValueError(f"Aucun trade trouvé pour Strategy='{strategy_name}', Symbol='{symbol}'")
        
        trades_pnl = df['Net_Profit'].values
        stats = calculate_trades_stats(df)
        
        # Récupérer le nom de la stratégie
        if strategy_name is None and 'Strategy_Name' in df.columns:
            strategy_name = df['Strategy_Name'].iloc[0]
        if symbol is None and 'Symbol' in df.columns:
            symbol = df['Symbol'].iloc[0]
        
        stats['strategy_name'] = f"{symbol}_{strategy_name}" if symbol and strategy_name else Path(filepath).stem
        
    else:
        # Fichier Titan original
        df = load_strategy_file(filepath)
        trades_pnl, trades_df = reconstruct_trades_from_titan(df)
        stats = calculate_trades_stats(trades_df)
        stats['strategy_name'] = get_strategy_name(filepath)
    
    return trades_pnl, stats, file_format
