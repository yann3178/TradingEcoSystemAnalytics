"""
Module de Corrélation V2 - Analyse des corrélations entre stratégies.
Basé sur la méthodologie Kevin Davey.
"""

from .config import (
    DEFAULT_CONFIG,
    SCORE_THRESHOLDS,
    STATUS_DIVERSIFYING,
    STATUS_MODERATE,
    STATUS_CORRELATED,
    STATUS_HIGHLY_CORRELATED,
    get_correlation_status,
)
from .correlation_calculator import (
    CorrelationAnalyzer,
    build_profit_matrix,
    calculate_correlation_matrix,
    calculate_davey_scores,
)

__all__ = [
    # Config
    'DEFAULT_CONFIG',
    'SCORE_THRESHOLDS',
    'STATUS_DIVERSIFYING',
    'STATUS_MODERATE',
    'STATUS_CORRELATED',
    'STATUS_HIGHLY_CORRELATED',
    'get_correlation_status',
    # Calculator
    'CorrelationAnalyzer',
    'build_profit_matrix',
    'calculate_correlation_matrix',
    'calculate_davey_scores',
]
