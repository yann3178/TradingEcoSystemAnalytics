"""
Constantes Globales
===================
Valeurs constantes utilisées dans tout le pipeline.
"""

# =============================================================================
# PATTERNS POWERLANGUAGE
# =============================================================================

# Patterns de prix (PatternFast function)
PATTERN_DEFINITIONS = {
    1: "body1d < 0.1 * range1d (Doji - very small body)",
    2: "body1d < 0.25 * range1d (Small body candle)",
    3: "body1d < 0.5 * range1d (Medium-small body)",
    4: "body1d < 0.75 * range1d (Medium body)",
    5: "body1d > 0.25 * range1d (Not tiny body)",
    6: "body1d > 0.5 * range1d (Significant body)",
    7: "body1d > 0.75 * range1d (Large body)",
    8: "body1d > 0.9 * range1d (Marubozu - full body)",
    # ... (ajout complet à faire)
    47: "closed1>closed2 and closed2>closed3 and closed3>closed4 (3 higher closes)",
    48: "closed1<closed2 and closed2<closed3 and closed3<closed4 (3 lower closes)",
    67: "closed1>closed2 (Higher close)",
    68: "closed1<closed2 (Lower close)",
    69: "closed1<opend1 (Bearish day)",
    70: "closed1>opend1 (Bullish day)",
    # Pattern 152 = toujours vrai (catch-all)
    152: "Always true (default/catch-all)",
}

# =============================================================================
# TYPES DE STRATÉGIES
# =============================================================================

STRATEGY_TYPES = {
    "BREAKOUT": ["Session_Range", "Daily_Range", "Channel", "Donchian", 
                 "Bollinger", "Keltner", "Pivot", "Opening_Range", "Swing_Point", "Gap"],
    "MEAN_REVERSION": ["Bollinger_Bounce", "RSI_Extreme", "Pivot_Fade", 
                       "False_Breakout", "Gap_Fade", "VWAP"],
    "TREND_FOLLOWING": ["MA_Crossover", "Channel_Ride", "Donchian_Trend", 
                        "SuperTrend", "Momentum"],
    "BIAS_TEMPORAL": ["Day_of_Week", "Hour_of_Day", "Session_Open", 
                      "Session_Close", "Weekly_Cycle", "Seasonal"],
    "HYBRID": ["Breakout_Reversal", "Trend_MeanRev", "Multi_Mode", "Adaptive"],
    "VOLATILITY": ["Expansion", "Contraction", "ATR_Regime", "VIX_Based"],
    "PATTERN_PURE": ["Candlestick", "Price_Action", "Multi_Pattern"],
}

# =============================================================================
# SYMBOLES ET INSTRUMENTS
# =============================================================================

SYMBOL_MAPPING = {
    # Indices US
    "ES": {"name": "E-mini S&P 500", "exchange": "CME", "currency": "USD", "point_value": 50},
    "NQ": {"name": "E-mini Nasdaq 100", "exchange": "CME", "currency": "USD", "point_value": 20},
    "YM": {"name": "E-mini Dow", "exchange": "CBOT", "currency": "USD", "point_value": 5},
    "RTY": {"name": "E-mini Russell 2000", "exchange": "CME", "currency": "USD", "point_value": 50},
    # Micro indices
    "MES": {"name": "Micro E-mini S&P 500", "exchange": "CME", "currency": "USD", "point_value": 5},
    "MNQ": {"name": "Micro E-mini Nasdaq", "exchange": "CME", "currency": "USD", "point_value": 2},
    "MYM": {"name": "Micro E-mini Dow", "exchange": "CBOT", "currency": "USD", "point_value": 0.5},
    # Europe
    "FDAX": {"name": "DAX Futures", "exchange": "EUREX", "currency": "EUR", "point_value": 25},
    "FDXM": {"name": "Mini-DAX Futures", "exchange": "EUREX", "currency": "EUR", "point_value": 5},
    "FGBL": {"name": "Euro Bund", "exchange": "EUREX", "currency": "EUR", "point_value": 1000},
    # Commodities
    "GC": {"name": "Gold", "exchange": "COMEX", "currency": "USD", "point_value": 100},
    "MGC": {"name": "Micro Gold", "exchange": "COMEX", "currency": "USD", "point_value": 10},
    "CL": {"name": "Crude Oil", "exchange": "NYMEX", "currency": "USD", "point_value": 1000},
    "MCL": {"name": "Micro Crude Oil", "exchange": "NYMEX", "currency": "USD", "point_value": 100},
    "NG": {"name": "Natural Gas", "exchange": "NYMEX", "currency": "USD", "point_value": 10000},
    "HG": {"name": "Copper", "exchange": "COMEX", "currency": "USD", "point_value": 25000},
    "SI": {"name": "Silver", "exchange": "COMEX", "currency": "USD", "point_value": 5000},
    "PL": {"name": "Platinum", "exchange": "NYMEX", "currency": "USD", "point_value": 50},
    # Energies
    "RB": {"name": "RBOB Gasoline", "exchange": "NYMEX", "currency": "USD", "point_value": 42000},
    "HO": {"name": "Heating Oil", "exchange": "NYMEX", "currency": "USD", "point_value": 42000},
    # Agri
    "ZC": {"name": "Corn", "exchange": "CBOT", "currency": "USD", "point_value": 50},
    "ZS": {"name": "Soybeans", "exchange": "CBOT", "currency": "USD", "point_value": 50},
    "ZW": {"name": "Wheat", "exchange": "CBOT", "currency": "USD", "point_value": 50},
    "S": {"name": "Soybeans", "exchange": "CBOT", "currency": "USD", "point_value": 50},
    "C": {"name": "Corn", "exchange": "CBOT", "currency": "USD", "point_value": 50},
    # Meats
    "LC": {"name": "Live Cattle", "exchange": "CME", "currency": "USD", "point_value": 400},
    "LH": {"name": "Lean Hogs", "exchange": "CME", "currency": "USD", "point_value": 400},
    "FC": {"name": "Feeder Cattle", "exchange": "CME", "currency": "USD", "point_value": 500},
    # Forex
    "EC": {"name": "Euro FX", "exchange": "CME", "currency": "USD", "point_value": 125000},
    "JY": {"name": "Japanese Yen", "exchange": "CME", "currency": "USD", "point_value": 12500000},
    "BP": {"name": "British Pound", "exchange": "CME", "currency": "USD", "point_value": 62500},
    "AD": {"name": "Australian Dollar", "exchange": "CME", "currency": "USD", "point_value": 100000},
    "CD": {"name": "Canadian Dollar", "exchange": "CME", "currency": "USD", "point_value": 100000},
    "SF": {"name": "Swiss Franc", "exchange": "CME", "currency": "USD", "point_value": 125000},
    # Bonds
    "ZB": {"name": "30-Year T-Bond", "exchange": "CBOT", "currency": "USD", "point_value": 1000},
    "ZN": {"name": "10-Year T-Note", "exchange": "CBOT", "currency": "USD", "point_value": 1000},
    "US": {"name": "Ultra T-Bond", "exchange": "CBOT", "currency": "USD", "point_value": 1000},
    # Crypto
    "BTC": {"name": "Bitcoin", "exchange": "CME", "currency": "USD", "point_value": 5},
    "MBT": {"name": "Micro Bitcoin", "exchange": "CME", "currency": "USD", "point_value": 0.1},
    "ETH": {"name": "Ether", "exchange": "CME", "currency": "USD", "point_value": 50},
    "BTCUSDT": {"name": "Bitcoin/USDT", "exchange": "Binance", "currency": "USD", "point_value": 1},
    "ETHUSDT": {"name": "Ether/USDT", "exchange": "Binance", "currency": "USD", "point_value": 1},
    # Softs
    "KC": {"name": "Coffee", "exchange": "ICE", "currency": "USD", "point_value": 375},
    "CT": {"name": "Cotton", "exchange": "ICE", "currency": "USD", "point_value": 500},
    "SB": {"name": "Sugar", "exchange": "ICE", "currency": "USD", "point_value": 1120},
    "CC": {"name": "Cocoa", "exchange": "ICE", "currency": "USD", "point_value": 10},
    # Volatility
    "VX": {"name": "VIX Futures", "exchange": "CFE", "currency": "USD", "point_value": 1000},
    # Stocks
    "AAPL": {"name": "Apple Inc.", "exchange": "NASDAQ", "currency": "USD", "point_value": 1},
    "TSLA": {"name": "Tesla Inc.", "exchange": "NASDAQ", "currency": "USD", "point_value": 1},
    "AMZN": {"name": "Amazon", "exchange": "NASDAQ", "currency": "USD", "point_value": 1},
    "META": {"name": "Meta Platforms", "exchange": "NASDAQ", "currency": "USD", "point_value": 1},
    "MSFT": {"name": "Microsoft", "exchange": "NASDAQ", "currency": "USD", "point_value": 1},
}

# =============================================================================
# TIMEFRAMES
# =============================================================================

TIMEFRAME_NAMES = {
    1: "1 min",
    5: "5 min",
    10: "10 min",
    15: "15 min",
    30: "30 min",
    60: "1 hour",
    120: "2 hours",
    240: "4 hours",
    480: "8 hours",
    1440: "Daily",
    10080: "Weekly",
    43200: "Monthly",
}

# =============================================================================
# KPIs ET MÉTRIQUES
# =============================================================================

KPI_DEFINITIONS = {
    "net_profit": "Profit net total après commissions",
    "gross_profit": "Somme des trades gagnants",
    "gross_loss": "Somme des trades perdants (valeur absolue)",
    "max_drawdown": "Perte maximale depuis un pic",
    "profit_factor": "Gross Profit / Gross Loss",
    "win_rate": "Pourcentage de trades gagnants",
    "avg_trade": "Profit moyen par trade",
    "total_trades": "Nombre total de trades",
    "sharpe_ratio": "Rendement ajusté au risque",
    "sortino_ratio": "Sharpe avec volatilité négative uniquement",
    "calmar_ratio": "Rendement annualisé / Max Drawdown",
    "recovery_factor": "Net Profit / Max Drawdown",
    "expectancy": "Espérance mathématique par trade",
    "is_return": "Rendement mensuel In Sample",
    "oos_return": "Rendement mensuel Out of Sample",
    "is_oos_ratio": "OOS Return / IS Return (efficience)",
    "ytd_profit": "Profit Year To Date",
    "np_dd_ratio": "Net Profit / Max Drawdown",
}

# =============================================================================
# COULEURS ET STYLES
# =============================================================================

QUALITY_COLORS = {
    "excellent": "#22c55e",  # green-500
    "good": "#84cc16",       # lime-500
    "average": "#eab308",    # yellow-500
    "poor": "#f97316",       # orange-500
    "bad": "#ef4444",        # red-500
}

STRATEGY_TYPE_COLORS = {
    "BREAKOUT": "#3b82f6",       # blue
    "MEAN_REVERSION": "#8b5cf6", # purple
    "TREND_FOLLOWING": "#22c55e", # green
    "BIAS_TEMPORAL": "#f59e0b",  # amber
    "HYBRID": "#ec4899",         # pink
    "VOLATILITY": "#ef4444",     # red
    "PATTERN_PURE": "#06b6d4",   # cyan
}
