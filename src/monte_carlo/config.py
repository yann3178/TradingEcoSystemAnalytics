"""
Configuration du simulateur Monte Carlo V2.
Basé sur la méthodologie Kevin Davey.
"""

# Paramètres de simulation
DEFAULT_CONFIG = {
    # Capital
    'capital_minimum': 5000,           # Capital de départ minimum
    'capital_increment': 2500,         # Incrément entre niveaux
    'nb_capital_levels': 11,           # Nombre de niveaux à tester
    
    # Simulation
    'nb_simulations': 2500,            # Nombre de simulations par niveau
    'ruin_threshold_pct': 0.40,        # Seuil de ruine = 40% du capital restant
    'trading_days_per_year': 252,      # Jours de trading par an
    
    # Critères de sélection Kevin Davey
    'max_acceptable_ruin': 0.10,       # Risque de ruine max acceptable (10%)
    'min_return_dd_ratio': 2.0,        # Ratio Return/DD minimum
    'min_prob_positive': 0.80,         # Probabilité min de finir positif (80%)
    
    # Random seed (None = aléatoire)
    'random_seed': None,
}

# Statuts de validation
STATUS_OK = "OK"
STATUS_WARNING = "WARNING"
STATUS_HIGH_RISK = "HIGH_RISK"

# Format des fichiers de stratégie (Titan/MultiCharts)
FILE_FORMAT_TITAN = {
    'separator': ' ',
    'columns': ['Date', 'DailyProfit', 'Contracts', 'Gap', 'Range', 'CumulativeTrades'],
    'date_format': '%d/%m/%Y',
    'encoding': 'utf-8',
}

# Format des fichiers extraits (CSV français)
FILE_FORMAT_EXTRACTED = {
    'separator': ';',
    'decimal': ',',
    'encoding': 'utf-8-sig',
    'date_format': '%d/%m/%Y',
}
