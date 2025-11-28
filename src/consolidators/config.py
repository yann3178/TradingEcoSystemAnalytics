"""
Configuration du module de Corrélation V2.
Basé sur la méthodologie Kevin Davey.
"""

from pathlib import Path

# ==============================================================================
# PARAMÈTRES PAR DÉFAUT
# ==============================================================================

DEFAULT_CONFIG = {
    # Périodes
    'start_year_longterm': 2012,      # Début historique long terme
    'recent_months': 12,               # Fenêtre court terme (mois)
    
    # Seuils de corrélation
    'correlation_threshold': 0.70,     # Seuil pour considérer "corrélé"
    'high_correlation_threshold': 0.85, # Seuil critique
    
    # Filtres
    'min_common_days_longterm': 100,   # Jours communs minimum (LT)
    'min_common_days_recent': 30,      # Jours communs minimum (CT)
    'min_active_days': 50,             # Activité minimum pour inclure
    
    # Scoring (pondération Davey)
    'weight_longterm': 0.5,            # Poids matrice long terme
    'weight_recent': 0.5,              # Poids matrice court terme
    
    # Méthode
    'correlation_method': 'pearson',   # 'pearson', 'spearman', 'kendall'
}

# Classification des scores Davey
SCORE_THRESHOLDS = {
    'diversifiant': 2,    # Score < 2 → Diversifiant 🟢
    'modere': 5,          # 2 <= Score < 5 → Modéré 🟡
    'correle': 10,        # 5 <= Score < 10 → Corrélé 🟠
    'tres_correle': 999   # Score >= 10 → Très corrélé 🔴
}

# Statuts de corrélation
STATUS_DIVERSIFYING = "Diversifiant"
STATUS_MODERATE = "Modéré"
STATUS_CORRELATED = "Corrélé"
STATUS_HIGHLY_CORRELATED = "Très corrélé"


def get_correlation_status(score: float) -> tuple:
    """
    Retourne le statut et l'emoji basé sur le score Davey.
    
    Args:
        score: Score de corrélation Davey
        
    Returns:
        Tuple (status, emoji)
    """
    if score < SCORE_THRESHOLDS['diversifiant']:
        return STATUS_DIVERSIFYING, '🟢'
    elif score < SCORE_THRESHOLDS['modere']:
        return STATUS_MODERATE, '🟡'
    elif score < SCORE_THRESHOLDS['correle']:
        return STATUS_CORRELATED, '🟠'
    else:
        return STATUS_HIGHLY_CORRELATED, '🔴'
