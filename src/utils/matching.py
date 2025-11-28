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
        - Supprime extensions (.html, .txt, .csv)
        - Supprime préfixes de symbole (GC_, ES_, NQ_, etc.)
        - Supprime préfixes courants (TOP_UA_, SOM_UA_, $PS_, etc.)
        - Supprime suffixes _MC
        - Remplace caractères spéciaux par underscore
    
    Args:
        name: Nom de stratégie brut
    
    Returns:
        Nom normalisé
    """
    if not name:
        return ""
    
    normalized = name.lower().strip()
    
    # Retirer extensions
    normalized = re.sub(r'\.(html|txt|csv)$', '', normalized)
    
    # Retirer préfixes de symbole au début (GC_, ES_, NQ_, etc.)
    symbols = ['gc', 'es', 'nq', 'cl', 'fdax', 'fgbl', 'ym', 'rty', 'hg', 'ng', 
               'rb', 'si', 'zb', 'zn', 'ec', 'jy', 'bp', 'ad', 'cd', 'sf', 'fdxm']
    for sym in symbols:
        normalized = re.sub(rf'^{sym}_', '', normalized)
    
    # Retirer suffixes _MC
    normalized = re.sub(r'_mc$', '', normalized)
    
    # Retirer préfixes courants de stratégie
    prefixes = [
        r'^(top_ua_|som_ua_|ua_|\$ps_|\$cata_|my_?script_?|my_?study_?)',
        r'^(s_|sa_|sb_|sc_|sd_)',
        r'^yann_',
    ]
    for pattern in prefixes:
        normalized = re.sub(pattern, '', normalized, flags=re.IGNORECASE)
    
    # Retirer suffixes de symbole redondants à la fin
    for sym in symbols:
        normalized = re.sub(rf'_{sym}$', '', normalized)
    
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
        "TOP_UA_287_GC_5" -> "287_gc_5"
        "SOM_UA_2305_Y_5" -> "2305_y_5"
        "EasterGold" -> "eastergold"
    
    Args:
        name: Nom de stratégie
    
    Returns:
        Partie centrale du nom
    """
    normalized = normalize_strategy_name(name)
    return normalized


def find_best_match(
    target: str,
    candidates: List[str],
    threshold: float = 0.80,
    min_chars: int = 3
) -> Tuple[Optional[str], float]:
    """
    Trouve la meilleure correspondance pour un nom dans une liste.
    
    Args:
        target: Nom à rechercher
        candidates: Liste de candidats
        threshold: Seuil minimum de similarité (0.0-1.0)
        min_chars: Minimum de caractères pour éviter faux positifs
    
    Returns:
        Tuple (meilleur_candidat, score) - candidat est None si aucun match au-dessus du seuil
    """
    if not target or not candidates:
        return (None, 0.0)
    
    target_norm = normalize_strategy_name(target)
    
    best_match = None
    best_score = 0.0
    
    for candidate in candidates:
        if not candidate:
            continue
        
        candidate_norm = normalize_strategy_name(candidate)
        
        # Score basé sur la similarité des noms normalisés
        score = similarity_ratio(target_norm, candidate_norm)
        
        # Bonus si le target est contenu dans le candidat ou vice-versa
        if target_norm in candidate_norm or candidate_norm in target_norm:
            score = max(score, 0.85)
        
        # Bonus si correspondance exacte
        if target_norm == candidate_norm:
            score = 1.0
        
        if score > best_score:
            best_score = score
            best_match = candidate
    
    # Appliquer le seuil
    if best_score >= threshold:
        return (best_match, best_score)
    
    return (None, best_score)


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
        if result[0] is not None:
            matches[strat] = result
    
    return matches
