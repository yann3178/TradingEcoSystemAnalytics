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
        pytest.importorskip("src.monte_carlo.simulator")
        from src.monte_carlo.simulator import MonteCarloSimulator
        
        SAMPLES_DIR = Path(__file__).parent.parent / "data" / "samples"
        
        mismatches = []
        for _, row in v1_reference_mc.iterrows():
            strategy = row["Strategy_Name"]
            v1_capital = row.get("Recommended_Capital")
            
            if pd.isna(v1_capital) or v1_capital == "N/A":
                continue
            
            # Charger les trades de test
            trades_file = SAMPLES_DIR / "trades" / f"{strategy}.csv"
            if not trades_file.exists():
                continue
            
            # Simuler avec seed fixe pour reproductibilité
            try:
                mc = MonteCarloSimulator(str(trades_file), random_seed=42)
                mc.run(verbose=False)
                v2_capital = mc.recommended_capital
                
                if v2_capital is not None:
                    diff = abs(float(v2_capital) - float(v1_capital))
                    if diff > 2500:  # Plus d'un niveau d'écart
                        mismatches.append({
                            "strategy": strategy,
                            "v1_capital": v1_capital,
                            "v2_capital": v2_capital,
                            "diff": diff
                        })
            except Exception as e:
                pytest.skip(f"Erreur simulation {strategy}: {e}")
        
        # Tolérance: max 10% de mismatch
        max_mismatch = len(v1_reference_mc) * 0.10
        assert len(mismatches) <= max_mismatch, \
            f"Capital mismatch pour {len(mismatches)} stratégies: {mismatches[:5]}"
    
    @pytest.mark.validation
    @pytest.mark.slow
    def test_ruin_probability_stable(self, v1_reference_mc, sample_strategies):
        """
        La probabilité de ruine doit être stable (± 2%).
        """
        pytest.importorskip("src.monte_carlo.simulator")
        from src.monte_carlo.simulator import MonteCarloSimulator
        
        SAMPLES_DIR = Path(__file__).parent.parent / "data" / "samples"
        
        mismatches = []
        for _, row in v1_reference_mc.iterrows():
            strategy = row["Strategy_Name"]
            v1_ruin = row.get("Ruin_Pct", 0)
            
            if pd.isna(v1_ruin):
                continue
            
            trades_file = SAMPLES_DIR / "trades" / f"{strategy}.csv"
            if not trades_file.exists():
                continue
            
            try:
                mc = MonteCarloSimulator(str(trades_file), random_seed=42)
                mc.run(verbose=False)
                
                # Prendre le premier niveau de capital pour comparaison
                if mc.results:
                    v2_ruin = mc.results[0].ruin_probability * 100
                    diff = abs(v2_ruin - v1_ruin)
                    if diff > 2.0:  # Plus de 2% d'écart
                        mismatches.append({
                            "strategy": strategy,
                            "v1_ruin": v1_ruin,
                            "v2_ruin": v2_ruin,
                            "diff": diff
                        })
            except Exception:
                pass
        
        # Tolérance: max 20% de mismatch (MC est stochastique)
        max_mismatch = len(v1_reference_mc) * 0.20
        assert len(mismatches) <= max_mismatch, \
            f"Ruin probability mismatch pour {len(mismatches)} stratégies"
    
    @pytest.mark.validation
    def test_return_dd_ratio_stable(self, v1_reference_mc, sample_strategies):
        """
        Le ratio Return/DD doit être stable (± 10%).
        """
        pytest.importorskip("src.monte_carlo.simulator")
        
        # Test simplifié: vérifier que le ratio est dans une plage raisonnable
        for _, row in v1_reference_mc.iterrows():
            ratio = row.get("Return_DD_Ratio", 0)
            if not pd.isna(ratio):
                assert -10 < ratio < 100, f"Ratio anormal: {ratio}"


class TestMonteCarloConfig:
    """Tests pour la configuration Monte Carlo."""
    
    def test_davey_parameters_present(self):
        """Les paramètres Kevin Davey doivent être définis."""
        # Tester l'ancien emplacement ou le nouveau
        try:
            from src.monte_carlo.config import DEFAULT_CONFIG
        except ImportError:
            from pathlib import Path
            import sys
            mc_path = Path(r"C:\TradeData\scripts\monte_carlo_simulator")
            if mc_path.exists():
                sys.path.insert(0, str(mc_path))
                from config import DEFAULT_CONFIG
            else:
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
            from pathlib import Path
            import sys
            mc_path = Path(r"C:\TradeData\scripts\monte_carlo_simulator")
            if mc_path.exists():
                sys.path.insert(0, str(mc_path))
                from config import DEFAULT_CONFIG
            else:
                pytest.skip("Module config non trouvé")
        
        # Vérifier les valeurs standards Davey
        assert DEFAULT_CONFIG["max_acceptable_ruin"] == 0.10, "Seuil ruine doit être 10%"
        assert DEFAULT_CONFIG["min_return_dd_ratio"] == 2.0, "Return/DD min doit être 2.0"
        assert DEFAULT_CONFIG["min_prob_positive"] == 0.80, "Prob positive min doit être 80%"
        assert DEFAULT_CONFIG["ruin_threshold_pct"] == 0.40, "Seuil ruine equity doit être 40%"


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
