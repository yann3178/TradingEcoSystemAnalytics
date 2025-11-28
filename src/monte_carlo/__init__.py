"""
Module Monte Carlo V2 pour l'analyse de stratégies de trading.
"""

from .config import DEFAULT_CONFIG, STATUS_OK, STATUS_WARNING, STATUS_HIGH_RISK
from .simulator import MonteCarloSimulator
from .data_loader import (
    load_trades_for_monte_carlo,
    detect_file_format,
    load_extracted_trades_file,
)

__all__ = [
    'DEFAULT_CONFIG',
    'STATUS_OK',
    'STATUS_WARNING', 
    'STATUS_HIGH_RISK',
    'MonteCarloSimulator',
    'load_trades_for_monte_carlo',
    'detect_file_format',
    'load_extracted_trades_file',
]
