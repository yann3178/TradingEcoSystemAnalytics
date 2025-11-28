"""
Utilitaires pour le matching de noms de stratégies
==================================================
Algorithmes de correspondance floue (fuzzy matching).
"""

from typing import Optional, Tuple, List
import re


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calcule la distance de Levenshtein entre deux chaînes.
    
    Args:
        s1, s2: Chaînes à comparer
    
    Returns:
        Distance (nombre d'opérations pour transformer s1 en s2)
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def similarity_ratio(s1: str, s2: str) -> float:
    """
    Calcule le ratio de similarité entre deux chaînes (0.0 à 1.0).
    
    Args:
        s1, s2: Chaînes à comparer
    
    Returns:
        Ratio de similarité (1.0 = identiques)
    """
    if not s1 or not s2:
        return 0.0
    
    distance = levenshtein_distance(s1.lower(), s2.lower())
    max_len = max(len(s1), len(s2))
    
    return 1.0 - (distance / max_len)


def normalize_strategy_name(name: str) -> str:
    """
    Normalise un nom de stratégie pour la comparaison.
    
    Transformations:
        - Minuscules
        - Supprime préfixes courants (TOP_, SOM_, $PS_, etc.)
        - Supprime suffixes de timeframe (_15, _60, _1440, etc.)
        - Supprime symboles redondants (_ES_, _NQ_, _GC_, etc.)
        - Remplace caractères spéciaux par underscore
    
    Args:
        name: Nom de stratégie brut
    
    Returns:
        Nom normalisé
    """
    if not name:
        return ""
    
    normalized = name.lower().strip()
    
    # Retirer préfixes courants
    prefixes = [
        r'^(top_ua_|som_ua_|ua_|\$ps_|\$cata_|my_?script_?|my_?study_?)',
        r'^(s_|sa_|sb_|sc_|sd_)',
    ]
    for pattern in prefixes:
        normalized = re.sub(pattern, '', normalized, flags=re.IGNORECASE)
    
    # Retirer suffixes de timeframe (_15, _30, _60, _1440, etc.)
    normalized = re.sub(r'_+\d+(_+\d+)*$', '', normalized)
    
    # Retirer suffixes de symbole redondants à la fin
    symbols = ['es', 'nq', 'gc', 'cl', 'fdax', 'fgbl', 'ym', 'rty', 'hg', 'ng', 
               'rb', 'si', 'zb', 'zn', 'ec', 'jy', 'bp', 'ad', 'cd', 'sf']
    for sym in symbols:
        normalized = re.sub(rf'_{sym}$', '', normalized, flags=re.IGNORECASE)
    
    # Remplacer caractères spéciaux par underscore
    normalized = re.sub(r'[^a-z0-9]', '_', normalized)
    
    # Nettoyer underscores multiples
    normalized = re.sub(r'_+', '_', normalized)
    normalized = normalized.strip('_')
    
    return normalized


def extract_strategy_core_name(name: str) -> str:
    """
    Extrait le "cœur" du nom de stratégie (sans préfixes/suffixes numériques).
    
    Exemples:
        "TOP_UA_287_GC_5" -> "287"
        "SOM_UA_2305_Y_5" -> "2305_y_5"
        "ATS_Strategy_v0.8" -> "ats_strategy_v0.8"
    
    Args:
        name: Nom de stratégie
    
    Returns:
        Partie centrale du nom
    """
    normalized = normalize_strategy_name(name)
    
    # Pour les stratégies UA, extraire le code
    match = re.search(r'(\d{2,4}_[a-z]_?\d*)', normalized)
    if match:
        return match.group(1)
    
    return normalized


def find_best_match(
    target: str,
    candidates: List[str],
    threshold: float = 0.80,
    min_chars: int = 5
) -> Optional[Tuple[str, float]]:
    """
    Trouve la meilleure correspondance pour un nom dans une liste.
    
    Args:
        target: Nom à rechercher
        candidates: Liste de candidats
        threshold: Seuil minimum de similarité (0.0-1.0)
        min_chars: Minimum de caractères pour éviter faux positifs
    
    Returns:
        Tuple (meilleur_candidat, score) ou None si aucun match
    """
    if not target or len(target) < min_chars:
        return None
    
    target_norm = normalize_strategy_name(target)
    target_core = extract_strategy_core_name(target)
    
    best_match = None
    best_score = 0.0
    
    for candidate in candidates:
        if not candidate or len(candidate) < min_chars:
            continue
        
        candidate_norm = normalize_strategy_name(candidate)
        candidate_core = extract_strategy_core_name(candidate)
        
        # Score 1: Similarité des noms normalisés
        score_norm = similarity_ratio(target_norm, candidate_norm)
        
        # Score 2: Similarité des cœurs
        score_core = similarity_ratio(target_core, candidate_core)
        
        # Score final: moyenne pondérée (cœur plus important)
        score = 0.4 * score_norm + 0.6 * score_core
        
        # Bonus si correspondance exacte du cœur
        if target_core == candidate_core:
            score = max(score, 0.95)
        
        if score > best_score and score >= threshold:
            best_score = score
            best_match = candidate
    
    if best_match:
        return (best_match, best_score)
    
    return None


def match_strategies_to_reports(
    strategy_names: List[str],
    report_names: List[str],
    threshold: float = 0.80
) -> dict:
    """
    Fait correspondre une liste de stratégies avec une liste de rapports.
    
    Args:
        strategy_names: Noms des stratégies (depuis code)
        report_names: Noms des rapports (depuis Portfolio Report)
        threshold: Seuil de similarité
    
    Returns:
        Dict {strategy_name: (matched_report_name, score)}
    """
    matches = {}
    
    for strat in strategy_names:
        result = find_best_match(strat, report_names, threshold)
        if result:
            matches[strat] = result
    
    return matches
