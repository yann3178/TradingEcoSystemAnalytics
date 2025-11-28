# -*- coding: utf-8 -*-
"""
Tests de validation V1 vs V2 pour les KPIs.
Compare les KPIs extraits par V2 avec les valeurs de référence V1.
"""

import pytest
import pandas as pd
from pathlib import Path


class TestKPIRegression:
    """
    Vérifie que les KPIs extraits par V2 correspondent à ceux de V1.
    """
    
    @pytest.mark.validation
    def test_net_profit_matches(self, v1_reference_kpis, sample_portfolio_report):
        """Le Net Profit V2 doit correspondre à V1 (tolérance 0.01%)."""
        from src.enrichers.kpi_enricher import KPIEnricher
        
        enricher = KPIEnricher(sample_portfolio_report)
        
        mismatches = []
        for _, row in v1_reference_kpis.iterrows():
            strategy = row["Strategy_Name"]
            expected_np = row.get("Net_Profit", 0)
            
            if pd.isna(expected_np):
                continue
            
            kpis = enricher.find_kpis_for_strategy(strategy)
            if kpis:
                actual_np = kpis.get("net_profit", 0)
                if expected_np != 0:
                    diff = abs(actual_np - expected_np) / abs(expected_np)
                    if diff > 0.0001:
                        mismatches.append({
                            "strategy": strategy,
                            "expected": expected_np,
                            "actual": actual_np,
                            "diff_pct": diff * 100
                        })
        
        assert len(mismatches) == 0, \
            f"Net Profit mismatch pour {len(mismatches)} stratégies: {mismatches[:5]}"
    
    @pytest.mark.validation
    def test_max_drawdown_matches(self, v1_reference_kpis, sample_portfolio_report):
        """Le Max Drawdown V2 doit correspondre à V1."""
        from src.enrichers.kpi_enricher import KPIEnricher
        
        enricher = KPIEnricher(sample_portfolio_report)
        
        mismatches = []
        for _, row in v1_reference_kpis.iterrows():
            strategy = row["Strategy_Name"]
            expected_dd = row.get("Max_Drawdown", 0)
            
            if pd.isna(expected_dd):
                continue
            
            kpis = enricher.find_kpis_for_strategy(strategy)
            if kpis:
                actual_dd = kpis.get("max_drawdown", 0)
                if expected_dd != 0:
                    diff = abs(actual_dd - expected_dd) / abs(expected_dd)
                    if diff > 0.01:  # 1% tolérance pour DD
                        mismatches.append({
                            "strategy": strategy,
                            "expected": expected_dd,
                            "actual": actual_dd,
                            "diff_pct": diff * 100
                        })
        
        assert len(mismatches) == 0, \
            f"Max Drawdown mismatch pour {len(mismatches)} stratégies"
    
    @pytest.mark.validation
    def test_all_strategies_have_kpis(self, v1_reference_kpis, sample_portfolio_report):
        """Toutes les stratégies V1 doivent avoir des KPIs en V2."""
        from src.enrichers.kpi_enricher import KPIEnricher
        
        enricher = KPIEnricher(sample_portfolio_report)
        
        missing = []
        for strategy in v1_reference_kpis["Strategy_Name"]:
            kpis = enricher.find_kpis_for_strategy(strategy)
            if not kpis:
                missing.append(strategy)
        
        # Tolérance: max 5% de stratégies non matchées
        max_missing = len(v1_reference_kpis) * 0.05
        assert len(missing) <= max_missing, \
            f"{len(missing)} stratégies sans KPIs (max {max_missing}): {missing[:10]}"
    
    @pytest.mark.validation
    def test_kpi_fields_present(self, v1_reference_kpis, sample_portfolio_report):
        """Tous les champs KPI requis doivent être présents."""
        from src.enrichers.kpi_enricher import KPIEnricher
        
        required_fields = [
            "net_profit",
            "max_drawdown",
            "total_trades",
            "avg_trade",
        ]
        
        enricher = KPIEnricher(sample_portfolio_report)
        
        # Tester sur la première stratégie disponible
        for strategy in v1_reference_kpis["Strategy_Name"]:
            kpis = enricher.find_kpis_for_strategy(strategy)
            if kpis:
                missing_fields = [f for f in required_fields if f not in kpis]
                assert len(missing_fields) == 0, \
                    f"Champs manquants pour {strategy}: {missing_fields}"
                break


class TestKPIEnricherUnit:
    """Tests unitaires pour KPIEnricher."""
    
    def test_enricher_initialization(self, sample_portfolio_report):
        """L'enricher s'initialise correctement."""
        from src.enrichers.kpi_enricher import KPIEnricher
        
        enricher = KPIEnricher(sample_portfolio_report)
        assert enricher is not None
    
    def test_enricher_with_empty_df(self):
        """L'enricher gère un DataFrame vide."""
        from src.enrichers.kpi_enricher import KPIEnricher
        
        empty_df = pd.DataFrame()
        enricher = KPIEnricher(empty_df)
        
        kpis = enricher.find_kpis_for_strategy("AnyStrategy")
        assert kpis is None or kpis == {}
    
    def test_generate_kpi_html_not_empty(self, sample_portfolio_report, sample_strategies):
        """Le HTML généré n'est pas vide."""
        from src.enrichers.kpi_enricher import KPIEnricher
        
        enricher = KPIEnricher(sample_portfolio_report)
        
        for strategy in sample_strategies:
            kpis = enricher.find_kpis_for_strategy(strategy)
            if kpis:
                html = enricher.generate_kpi_html(kpis)
                assert len(html) > 100, f"HTML trop court pour {strategy}"
                assert "kpi-dashboard" in html or "kpi" in html.lower()
                break
