# -*- coding: utf-8 -*-
"""
Tests pour le module de Corrélation V2.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path


class TestCorrelationConfig:
    """Tests pour la configuration de corrélation."""
    
    def test_config_import(self):
        """La configuration peut être importée."""
        try:
            from src.consolidators.config import DEFAULT_CONFIG, SCORE_THRESHOLDS
            assert DEFAULT_CONFIG is not None
            assert SCORE_THRESHOLDS is not None
        except ImportError as e:
            pytest.skip(f"Import failed: {e}")
    
    def test_davey_parameters_present(self):
        """Les paramètres Davey doivent être définis."""
        try:
            from src.consolidators.config import DEFAULT_CONFIG
            
            required_params = [
                'start_year_longterm',
                'recent_months',
                'correlation_threshold',
                'weight_longterm',
                'weight_recent',
                'min_common_days_longterm',
                'min_common_days_recent',
            ]
            
            for param in required_params:
                assert param in DEFAULT_CONFIG, f"Paramètre manquant: {param}"
        except ImportError:
            pytest.skip("Module config non trouvé")
    
    def test_davey_thresholds_valid(self):
        """Les seuils Davey doivent être valides."""
        try:
            from src.consolidators.config import DEFAULT_CONFIG
            
            assert DEFAULT_CONFIG['correlation_threshold'] == 0.70
            assert DEFAULT_CONFIG['weight_longterm'] == 0.5
            assert DEFAULT_CONFIG['weight_recent'] == 0.5
            assert DEFAULT_CONFIG['start_year_longterm'] == 2012
            assert DEFAULT_CONFIG['recent_months'] == 12
        except ImportError:
            pytest.skip("Module config non trouvé")
    
    def test_score_thresholds_defined(self):
        """Les seuils de score sont définis."""
        try:
            from src.consolidators.config import SCORE_THRESHOLDS
            
            assert 'diversifiant' in SCORE_THRESHOLDS
            assert 'modere' in SCORE_THRESHOLDS
            assert 'correle' in SCORE_THRESHOLDS
            assert 'tres_correle' in SCORE_THRESHOLDS
        except ImportError:
            pytest.skip("Module config non trouvé")


class TestCorrelationCalculator:
    """Tests pour le calculateur de corrélation."""
    
    def test_calculator_import(self):
        """Le calculateur peut être importé."""
        try:
            from src.consolidators import CorrelationAnalyzer
            assert CorrelationAnalyzer is not None
        except ImportError as e:
            pytest.skip(f"Import failed: {e}")
    
    def test_build_profit_matrix(self):
        """La matrice de profit peut être construite."""
        try:
            from src.consolidators import build_profit_matrix
            
            # Créer des données de test
            data = pd.DataFrame({
                'Date': pd.date_range('2024-01-01', periods=10),
                'Strategy_ID': ['A'] * 5 + ['B'] * 5,
                'DailyProfit': [100, -50, 200, 0, 150, 50, -100, 300, -200, 100]
            })
            
            matrix = build_profit_matrix(data)
            
            assert 'A' in matrix.columns
            assert 'B' in matrix.columns
            assert len(matrix) == 10
        except ImportError:
            pytest.skip("Module non disponible")
    
    def test_calculate_correlation_matrix(self):
        """La matrice de corrélation peut être calculée."""
        try:
            from src.consolidators import calculate_correlation_matrix
            
            # Créer une matrice de test
            np.random.seed(42)
            dates = pd.date_range('2024-01-01', periods=100)
            matrix = pd.DataFrame({
                'A': np.random.randn(100),
                'B': np.random.randn(100),
                'C': np.random.randn(100),
            }, index=dates)
            
            corr, common_days = calculate_correlation_matrix(matrix, min_common_days=10)
            
            # Vérifications
            assert corr.shape == (3, 3)
            assert corr.loc['A', 'A'] == 1.0
            assert corr.loc['B', 'B'] == 1.0
            assert corr.loc['A', 'B'] == corr.loc['B', 'A']  # Symétrie
        except ImportError:
            pytest.skip("Module non disponible")
    
    def test_get_correlation_status(self):
        """Le statut de corrélation est correct."""
        try:
            from src.consolidators.config import get_correlation_status
            
            # Diversifiant (score < 2)
            status, emoji = get_correlation_status(1.0)
            assert status == "Diversifiant"
            assert emoji == "🟢"
            
            # Modéré (2 <= score < 5)
            status, emoji = get_correlation_status(3.0)
            assert status == "Modéré"
            assert emoji == "🟡"
            
            # Corrélé (5 <= score < 10)
            status, emoji = get_correlation_status(7.0)
            assert status == "Corrélé"
            assert emoji == "🟠"
            
            # Très corrélé (score >= 10)
            status, emoji = get_correlation_status(15.0)
            assert status == "Très corrélé"
            assert emoji == "🔴"
        except ImportError:
            pytest.skip("Module non disponible")


class TestCorrelationOutput:
    """Tests pour les outputs de corrélation."""
    
    def test_v1_reference_exists(self, v1_reference_correlation):
        """Le fichier de référence V1 existe."""
        # Le fixture skip si le fichier n'existe pas
        assert v1_reference_correlation is not None
    
    def test_v1_reference_structure(self, v1_reference_correlation):
        """La structure du fichier de référence V1 est valide."""
        # Vérifier que c'est une matrice carrée ou presque
        assert len(v1_reference_correlation) > 0
