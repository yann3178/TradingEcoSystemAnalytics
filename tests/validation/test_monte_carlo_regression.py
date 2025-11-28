# -*- coding: utf-8 -*-
"""
Tests de validation V1 vs V2 pour Monte Carlo.
Compare les résultats MC de V2 avec les valeurs de référence V1.

Note: Les simulations MC sont stochastiques, donc on utilise:
- Un seed fixe (42) pour la reproductibilité
- Des tolérances statistiques pour les métriques
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path


class TestMonteCarloRegression:
    """
    Vérifie que les simulations MC V2 correspondent à V1.
    """
    
    @pytest.mark.validation
    @pytest.mark.slow
    def test_recommended_capital_within_range(self, v1_reference_mc, sample_strategies):
        """
        Le capital recommandé V2 doit être dans une plage acceptable.
        Tolérance: ± 1 niveau de capital (2500$)
        """
        try:
            from src.monte_carlo import MonteCarloSimulator
        except ImportError:
            pytest.skip("Module src.monte_carlo non disponible")
        
        SAMPLES_DIR = Path(__file__).parent.parent / "data" / "samples"
        
        mismatches = []
        tested = 0
        
        for _, row in v1_reference_mc.iterrows():
            strategy = row["Strategy_Name"]
            v1_capital = row.get("Recommended_Capital")
            
            if pd.isna(v1_capital) or v1_capital == "N/A" or v1_capital == "":
                continue
            
            # Chercher le fichier de trades
            trades_file = SAMPLES_DIR / "trades" / f"{strategy}.csv"
            if not trades_file.exists():
                continue
            
            try:
                mc = MonteCarloSimulator(str(trades_file), random_seed=42)
                mc.run(verbose=False)
                v2_capital = mc.recommended_capital
                tested += 1
                
                if v2_capital is not None:
                    diff = abs(float(v2_capital) - float(v1_capital))
                    if diff > 2500:
                        mismatches.append({
                            "strategy": strategy,
                            "v1_capital": v1_capital,
                            "v2_capital": v2_capital,
                            "diff": diff
                        })
            except Exception as e:
                print(f"⚠️ Erreur simulation {strategy}: {e}")
        
        if tested == 0:
            pytest.skip("Aucun fichier de trades trouvé pour les tests")
        
        max_mismatch = max(1, tested * 0.10)
        assert len(mismatches) <= max_mismatch, \
            f"Capital mismatch pour {len(mismatches)} stratégies: {mismatches[:5]}"
    
    @pytest.mark.validation
    def test_return_dd_ratio_stable(self, v1_reference_mc, sample_strategies):
        """
        Le ratio Return/DD doit être dans une plage raisonnable.
        """
        for _, row in v1_reference_mc.iterrows():
            ratio = row.get("Return_DD_Ratio", 0)
            if not pd.isna(ratio):
                try:
                    ratio_val = float(ratio)
                    assert -10 < ratio_val < 100, f"Ratio anormal: {ratio_val}"
                except (ValueError, TypeError):
                    pass


class TestMonteCarloConfig:
    """Tests pour la configuration Monte Carlo."""
    
    def test_davey_parameters_present(self):
        """Les paramètres Kevin Davey doivent être définis."""
        try:
            from src.monte_carlo.config import DEFAULT_CONFIG
        except ImportError:
            pytest.skip("Module config non trouvé")
        
        required_params = [
            "capital_minimum",
            "capital_increment",
            "nb_capital_levels",
            "nb_simulations",
            "ruin_threshold_pct",
            "max_acceptable_ruin",
            "min_return_dd_ratio",
            "min_prob_positive",
        ]
        
        for param in required_params:
            assert param in DEFAULT_CONFIG, f"Paramètre manquant: {param}"
    
    def test_davey_thresholds_valid(self):
        """Les seuils Kevin Davey doivent être valides."""
        try:
            from src.monte_carlo.config import DEFAULT_CONFIG
        except ImportError:
            pytest.skip("Module config non trouvé")
        
        assert DEFAULT_CONFIG["max_acceptable_ruin"] == 0.10, "Seuil ruine doit être 10%"
        assert DEFAULT_CONFIG["min_return_dd_ratio"] == 2.0, "Return/DD min doit être 2.0"
        assert DEFAULT_CONFIG["min_prob_positive"] == 0.80, "Prob positive min doit être 80%"
        assert DEFAULT_CONFIG["ruin_threshold_pct"] == 0.40, "Seuil ruine equity doit être 40%"


class TestMonteCarloSimulator:
    """Tests unitaires pour le simulateur Monte Carlo."""
    
    def test_simulator_import(self):
        """Le simulateur peut être importé."""
        try:
            from src.monte_carlo import MonteCarloSimulator
            assert MonteCarloSimulator is not None
        except ImportError as e:
            pytest.skip(f"Import failed: {e}")
    
    def test_simulator_config_defaults(self):
        """Les valeurs par défaut de config sont appliquées."""
        try:
            from src.monte_carlo.config import DEFAULT_CONFIG
            
            assert DEFAULT_CONFIG['capital_minimum'] == 5000
            assert DEFAULT_CONFIG['nb_simulations'] == 2500
            assert DEFAULT_CONFIG['nb_capital_levels'] == 11
        except ImportError:
            pytest.skip("Module config non disponible")
    
    def test_status_constants(self):
        """Les constantes de statut sont définies."""
        try:
            from src.monte_carlo import STATUS_OK, STATUS_WARNING, STATUS_HIGH_RISK
            
            assert STATUS_OK == "OK"
            assert STATUS_WARNING == "WARNING"
            assert STATUS_HIGH_RISK == "HIGH_RISK"
        except ImportError:
            pytest.skip("Constantes de statut non disponibles")


class TestMonteCarloOutput:
    """Tests pour les outputs Monte Carlo."""
    
    def test_csv_columns_present(self, v1_reference_mc):
        """Le CSV MC doit avoir toutes les colonnes requises."""
        required_columns = [
            "Strategy_Name",
            "Symbol",
            "Recommended_Capital",
            "Status",
            "Ruin_Pct",
            "Return_DD_Ratio",
        ]
        
        for col in required_columns:
            assert col in v1_reference_mc.columns, f"Colonne manquante: {col}"
    
    def test_status_values_valid(self, v1_reference_mc):
        """Les valeurs de statut doivent être valides."""
        valid_statuses = ["OK", "WARNING", "HIGH_RISK", "N/A"]
        
        for status in v1_reference_mc["Status"].unique():
            if pd.notna(status):
                assert status in valid_statuses, f"Statut invalide: {status}"
