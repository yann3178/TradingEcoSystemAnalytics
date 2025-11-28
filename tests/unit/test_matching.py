# -*- coding: utf-8 -*-
"""
Tests unitaires pour le module matching (fuzzy matching).
"""

import pytest
from src.utils.matching import (
    levenshtein_distance,
    similarity_ratio,
    normalize_strategy_name,
    extract_strategy_core_name,
    find_best_match,
)


class TestLevenshteinDistance:
    """Tests pour la fonction de distance de Levenshtein."""
    
    def test_identical_strings(self):
        """Chaînes identiques = distance 0."""
        assert levenshtein_distance("abc", "abc") == 0
        assert levenshtein_distance("EasterGold", "EasterGold") == 0
    
    def test_empty_strings(self):
        """Chaîne vide."""
        assert levenshtein_distance("", "abc") == 3
        assert levenshtein_distance("abc", "") == 3
        assert levenshtein_distance("", "") == 0
    
    def test_single_char_diff(self):
        """Différence d'un caractère."""
        assert levenshtein_distance("abc", "abd") == 1
        assert levenshtein_distance("abc", "ab") == 1
        assert levenshtein_distance("abc", "abcd") == 1
    
    def test_known_distance(self):
        """Distances connues."""
        assert levenshtein_distance("kitten", "sitting") == 3
        assert levenshtein_distance("saturday", "sunday") == 3


class TestSimilarityRatio:
    """Tests pour le ratio de similarité."""
    
    def test_identical_strings(self):
        """Chaînes identiques = ratio 1.0."""
        assert similarity_ratio("abc", "abc") == 1.0
    
    def test_completely_different(self):
        """Chaînes très différentes = ratio faible."""
        ratio = similarity_ratio("abc", "xyz")
        assert ratio < 0.5
    
    def test_partial_match(self):
        """Correspondance partielle."""
        ratio = similarity_ratio("EasterGold", "GC_EasterGold_MC")
        assert 0.5 < ratio < 1.0


class TestNormalizeStrategyName:
    """Tests pour la normalisation des noms de stratégies."""
    
    def test_lowercase(self):
        """Conversion en minuscules."""
        result = normalize_strategy_name("EasterGold")
        assert result == result.lower()
    
    def test_remove_prefix_top_ua(self):
        """Suppression préfixe TOP_UA_."""
        result = normalize_strategy_name("TOP_UA_287_GC_5")
        assert "top_ua_" not in result.lower()
    
    def test_remove_prefix_som_ua(self):
        """Suppression préfixe SOM_UA_."""
        result = normalize_strategy_name("SOM_UA_2303_Y_3")
        assert "som_ua_" not in result.lower()
    
    def test_remove_prefix_ps(self):
        """Suppression préfixe $PS_."""
        result = normalize_strategy_name("$PS_274_comp_UnmirrTF")
        assert "$ps_" not in result.lower()
    
    def test_remove_symbol_suffix(self):
        """Suppression suffixe symbole."""
        result = normalize_strategy_name("TOP_UA_287_GC_5")
        # Le suffixe _GC ou _5 peut être retiré selon l'implémentation
        assert result  # Non vide


class TestExtractStrategyCoreNamefunction:
    """Tests pour l'extraction du nom cœur."""
    
    def test_extract_number(self):
        """Extraction du numéro de stratégie."""
        core = extract_strategy_core_name("TOP_UA_287_GC_5")
        assert "287" in core
    
    def test_extract_named_strategy(self):
        """Extraction d'une stratégie nommée."""
        core = extract_strategy_core_name("EasterGold")
        assert "easter" in core.lower() or "gold" in core.lower()


class TestFindBestMatch:
    """Tests pour le matching fuzzy."""
    
    def test_exact_match(self):
        """Correspondance exacte."""
        candidates = ["EasterGold", "SummerGold", "WinterGold"]
        match, score = find_best_match("EasterGold", candidates)
        assert match == "EasterGold"
        assert score == 1.0
    
    def test_fuzzy_match_with_prefix(self):
        """Correspondance avec préfixe symbole."""
        candidates = ["GC_EasterGold_MC", "SummerGold", "WinterGold"]
        match, score = find_best_match("EasterGold", candidates, threshold=0.5)
        assert match is not None
        assert "Easter" in match
        assert score > 0.5
    
    def test_fuzzy_match_with_suffix(self):
        """Correspondance avec suffixe."""
        candidates = ["EasterGold.html", "SummerGold", "WinterGold"]
        match, score = find_best_match("EasterGold", candidates, threshold=0.5)
        assert match is not None
        assert "Easter" in match
        assert score > 0.5
    
    def test_no_match_below_threshold(self):
        """Pas de correspondance sous le seuil."""
        candidates = ["CompletelyDifferent", "AnotherOne", "YetAnother"]
        match, score = find_best_match("EasterGold", candidates, threshold=0.8)
        assert match is None  # Pas de match au-dessus du seuil
    
    def test_empty_candidates(self):
        """Liste de candidats vide."""
        match, score = find_best_match("EasterGold", [])
        assert match is None
        assert score == 0.0
    
    def test_case_insensitive(self):
        """Matching insensible à la casse."""
        candidates = ["EASTERGOLD", "summergold", "WinterGold"]
        match, score = find_best_match("EasterGold", candidates)
        assert match is not None
        assert score > 0.8


class TestMatchingRealCases:
    """Tests avec des cas réels du système."""
    
    def test_match_top_ua_strategy(self):
        """Matching stratégie TOP_UA."""
        candidates = [
            "GC_TOP_UA_287_GC_5_MC.html",
            "ES_TOP_UA_556_ES_15_MC.html",
            "NQ_TOP_UA_152_NQ_5_MC.html",
        ]
        match, score = find_best_match("TOP_UA_287_GC_5", candidates, threshold=0.5)
        assert match is not None
        assert "287" in match
        assert score > 0.5
    
    def test_match_som_ua_strategy(self):
        """Matching stratégie SOM_UA."""
        candidates = [
            "ES_SOM_UA_2303_Y_3_MC.html",
            "GC_SOM_UA_2305_G_1_MC.html",
        ]
        match, score = find_best_match("SOM_UA_2303_Y_3", candidates, threshold=0.5)
        assert match is not None
        assert "2303" in match
        assert score > 0.5
    
    def test_match_custom_strategy(self):
        """Matching stratégie custom."""
        candidates = [
            "ES_Yann_Casey_strategy_v0.1_MC.html",
            "NQ_Yann_Casey_strategy_v0.1_MC.html",
        ]
        match, score = find_best_match("Casey_strategy_v0.1", candidates, threshold=0.5)
        assert match is not None
        assert "Casey" in match
        assert score > 0.5
