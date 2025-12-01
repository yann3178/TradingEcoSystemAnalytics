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

# =============================================================================
# CONFIGURATION DASHBOARD HTML
# =============================================================================
# Configuration pour la page de synthèse interactive (all_strategies_montecarlo.html)
# Permet le recalcul dynamique des capitaux recommandés selon différents profils de risque

# Critères par défaut (Kevin Davey standard)
DASHBOARD_DEFAULT_CRITERIA = {
    'max_ruin': 0.10,              # Risque de ruine max (10%)
    'min_return_dd': 2.0,          # Return/DD ratio min
    'min_prob_positive': 0.80,     # Probabilité positive min (80%)
}

# Presets de configuration prédéfinis
DASHBOARD_PRESETS = {
    'simple': {
        'name': 'Simple (Ruine seule)',
        'description': 'Uniquement le critère de risque de ruine',
        'max_ruin': 0.10,
        'min_return_dd': None,     # Désactivé
        'min_prob_positive': None, # Désactivé
    },
    'kevin_davey': {
        'name': 'Kevin Davey Standard',
        'description': 'Critères recommandés par Kevin Davey',
        'max_ruin': 0.10,
        'min_return_dd': 2.0,
        'min_prob_positive': 0.80,
    },
    'conservative': {
        'name': 'Conservateur',
        'description': 'Critères stricts pour traders prudents',
        'max_ruin': 0.05,          # 5% max
        'min_return_dd': 2.5,
        'min_prob_positive': 0.85,
    },
    'aggressive': {
        'name': 'Agressif',
        'description': 'Critères souples pour traders actifs',
        'max_ruin': 0.20,          # 20% max
        'min_return_dd': 1.5,
        'min_prob_positive': 0.70,
    },
}

# Plages de valeurs pour les sliders d'interface
SLIDER_RANGES = {
    'max_ruin': {
        'min': 0,
        'max': 0.30,     # 30%
        'step': 0.005,   # 0.5%
        'default': 0.10,
    },
    'min_return_dd': {
        'min': 0,
        'max': 5.0,
        'step': 0.1,
        'default': 2.0,
    },
    'min_prob_positive': {
        'min': 0,
        'max': 1.0,      # 100%
        'step': 0.01,    # 1%
        'default': 0.80,
    },
}

# Paramètres d'affichage et d'interaction
DASHBOARD_DISPLAY = {
    'min_trades_default': 20,      # Filtre min trades par défaut
    'animation_duration_ms': 500,  # Durée animation highlight (ms)
    'table_page_size': 50,         # Nombre de lignes par page (pagination)
    'decimal_places': {
        'currency': 0,             # Pas de décimales pour les $
        'percentage': 1,           # 1 décimale pour les %
        'ratio': 2,                # 2 décimales pour les ratios
    },
}

# Palette de couleurs (Dark Theme)
DASHBOARD_COLORS = {
    'bg_primary': '#0f0f1a',      # Fond principal de la page
    'bg_secondary': '#1a1a2e',    # Fond des headers et cartes secondaires
    'bg_card': '#16213e',         # Fond des cartes principales
    'text_primary': '#eaeaea',    # Texte principal
    'text_secondary': '#a0a0a0',  # Texte secondaire
    'accent_green': '#00d4aa',    # Statut OK / Positif
    'accent_red': '#ff6b6b',      # Statut HIGH_RISK / Négatif
    'accent_blue': '#4ecdc4',     # Accent principal / Liens
    'accent_yellow': '#ffe66d',   # Statut WARNING
    'border_live': '#ffd700',     # Bordure des stats live (or)
}

# Configuration Chart.js pour les graphiques statiques
CHART_CONFIG = {
    'font_family': "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    'font_size': 12,
    'legend_position': 'top',
    'responsive': True,
    'maintain_aspect_ratio': True,
    'animation_duration': 750,
}

# Patterns de nommage des fichiers
FILE_PATTERNS = {
    'summary_csv': 'monte_carlo_summary.csv',
    'individual_csv': '{strategy_name}_mc.csv',
    'summary_html': 'all_strategies_montecarlo.html',
    'individual_html': 'Individual/{symbol}_{strategy_name}_MC.html',
}

# Configuration des graphiques de synthèse
SUMMARY_CHARTS = {
    'pie_chart': {
        'title': 'Distribution par Statut',
        'enabled': True,
    },
    'scatter_chart': {
        'title': 'Return/DD vs Risque de Ruine',
        'enabled': True,
        'x_axis': 'ruin_pct',
        'y_axis': 'return_dd_ratio',
    },
    'top_pnl_chart': {
        'title': 'Top 10 P&L Total',
        'enabled': True,
        'limit': 10,
    },
    'top_return_dd_chart': {
        'title': 'Top 10 Return/DD Ratio',
        'enabled': True,
        'limit': 10,
    },
}

# Messages d'information pour l'utilisateur
DASHBOARD_MESSAGES = {
    'no_capital_found': "Aucun niveau de capital ne satisfait les critères",
    'recalculating': "Recalcul en cours...",
    'recalculation_complete': "Recalcul terminé",
    'criteria_too_strict': "Les critères sont peut-être trop stricts. Essayez de les assouplir.",
}
