"""
Module Analyseurs IA - Trading Strategy Analysis V2
====================================================
Classification et analyse automatique des stratégies via Claude API.

Modules:
    - config: Configuration de l'analyseur IA
    - code_parser: Parsing du code PowerLanguage
    - ai_analyzer: Intégration Claude API
    - html_generator: Génération des rapports HTML

Catégories de stratégies:
    - BREAKOUT: Cassures de niveaux
    - MEAN_REVERSION: Retour à la moyenne  
    - TREND_FOLLOWING: Suivi de tendance
    - PATTERN: Patterns chartistes/candlesticks
    - VOLATILITY: Basé sur la volatilité
    - SEASONAL: Saisonnalité/timing
    - MOMENTUM: Momentum/force
    - OTHER: Autres/hybrides
"""

from .config import AIAnalyzerConfig, STRATEGY_CATEGORIES
from .code_parser import CodeParser
from .ai_analyzer import AIAnalyzer
from .html_generator import HTMLReportGenerator

__all__ = [
    'AIAnalyzerConfig',
    'STRATEGY_CATEGORIES', 
    'CodeParser',
    'AIAnalyzer',
    'HTMLReportGenerator',
]
