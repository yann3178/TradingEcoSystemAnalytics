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
            
            # Conversion explicite en float
            try:
                expected_np = float(expected_np)
            except (ValueError, TypeError):
                continue
            
            kpis = enricher.find_kpis_for_strategy(strategy)
            if kpis:
                # Chercher dans plusieurs noms de colonnes possibles
                actual_np = (
                    kpis.get("net_profit") or 
                    kpis.get("Net_Profit") or 
                    kpis.get("Net_Profit_Total") or 
                    0
                )
                
                # Conversion explicite en float
                try:
                    actual_np = float(actual_np) if actual_np else 0
                except (ValueError, TypeError):
                    actual_np = 0
                
                if expected_np != 0 and actual_np:
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
            expected_dd = row.get("Net_Max_Drawdown", 0)
            
            if pd.isna(expected_dd):
                continue
            
            # Conversion explicite en float
            try:
                expected_dd = float(expected_dd)
            except (ValueError, TypeError):
                continue
            
            kpis = enricher.find_kpis_for_strategy(strategy)
            if kpis:
                # Chercher dans plusieurs noms de colonnes possibles
                actual_dd = (
                    kpis.get("max_drawdown") or 
                    kpis.get("Max_Drawdown") or 
                    kpis.get("Net_Max_Drawdown") or 
                    0
                )
                
                # Conversion explicite en float
                try:
                    actual_dd = float(actual_dd) if actual_dd else 0
                except (ValueError, TypeError):
                    actual_dd = 0
                
                if expected_dd != 0 and actual_dd:
                    diff = abs(actual_dd - expected_dd) / abs(expected_dd)
                    if diff > 0.01:  # 1% tolérance pour DD
                        mismatches.append({
                            "strategy": strategy,
                            "expected": expected_dd,
                            "actual": actual_dd,
                            "diff_pct": diff * 100
                        })
        
        assert len(mismatches) == 0, \
            f"Max Drawdown mismatch pour {len(mismatches)} stratégies: {mismatches}"
    
    @pytest.mark.validation
    def test_all_strategies_have_kpis(self, v1_reference_kpis, sample_portfolio_report):
        """Toutes les stratégies V1 doivent avoir des KPIs en V2."""
        from src.enrichers.kpi_enricher import KPIEnricher
        
        enricher = KPIEnricher(sample_portfolio_report)
        
        missing = []
        found = []
        for strategy in v1_reference_kpis["Strategy_Name"]:
            kpis = enricher.find_kpis_for_strategy(strategy)
            if not kpis:
                missing.append(strategy)
            else:
                found.append(strategy)
        
        # Tolérance: max 5% de stratégies non matchées
        max_missing = len(v1_reference_kpis) * 0.05
        assert len(missing) <= max_missing, \
            f"{len(missing)} stratégies sans KPIs (max {max_missing}): {missing[:10]}"
    
    @pytest.mark.validation
    def test_kpi_fields_present(self, v1_reference_kpis, sample_portfolio_report):
        """Tous les champs KPI requis doivent être présents."""
        from src.enrichers.kpi_enricher import KPIEnricher
        
        # Champs requis (avec variantes de nommage)
        required_fields_variants = [
            ["net_profit", "Net_Profit", "Net_Profit_Total"],
            ["max_drawdown", "Max_Drawdown", "Net_Max_Drawdown"],
            ["total_trades", "Total_Trades", "Nombre_Trades"],
            ["avg_trade", "Avg_Trade", "Net_Average_Trade"],
        ]
        
        enricher = KPIEnricher(sample_portfolio_report)
        
        # Tester sur la première stratégie disponible
        for strategy in v1_reference_kpis["Strategy_Name"]:
            kpis = enricher.find_kpis_for_strategy(strategy)
            if kpis:
                missing_fields = []
                for variants in required_fields_variants:
                    if not any(v in kpis for v in variants):
                        missing_fields.append(variants[0])
                
                assert len(missing_fields) == 0, \
                    f"Champs manquants pour {strategy}: {missing_fields}. KPIs disponibles: {list(kpis.keys())[:15]}"
                break


class TestKPIEnricherUnit:
    """Tests unitaires pour KPIEnricher."""
    
    def test_enricher_initialization_with_dataframe(self, sample_portfolio_report):
        """L'enricher s'initialise correctement avec un DataFrame."""
        from src.enrichers.kpi_enricher import KPIEnricher
        
        enricher = KPIEnricher(sample_portfolio_report)
        assert enricher is not None
        assert len(enricher.portfolio_data) > 0
        assert len(enricher.strategy_names) > 0
    
    def test_enricher_initialization_with_path(self):
        """L'enricher s'initialise correctement avec un chemin de fichier."""
        from src.enrichers.kpi_enricher import KPIEnricher
        
        csv_path = Path(__file__).parent.parent / "data" / "samples" / "portfolio_report.csv"
        if csv_path.exists():
            enricher = KPIEnricher(csv_path)
            assert enricher is not None
            assert len(enricher.portfolio_data) > 0
    
    def test_enricher_with_empty_df(self):
        """L'enricher gère un DataFrame vide."""
        from src.enrichers.kpi_enricher import KPIEnricher
        
        empty_df = pd.DataFrame()
        enricher = KPIEnricher(empty_df)
        
        kpis = enricher.find_kpis_for_strategy("AnyStrategy")
        assert kpis is None
    
    def test_find_strategy_exact_match(self, sample_portfolio_report):
        """Trouve une stratégie par correspondance exacte."""
        from src.enrichers.kpi_enricher import KPIEnricher
        
        enricher = KPIEnricher(sample_portfolio_report)
        
        # Nom exact tel qu'il apparaît dans le CSV
        kpis = enricher.find_kpis_for_strategy("EasterGold")
        assert kpis is not None
    
    def test_find_strategy_with_html_extension(self, sample_portfolio_report):
        """Trouve une stratégie même avec l'extension .html."""
        from src.enrichers.kpi_enricher import KPIEnricher
        
        enricher = KPIEnricher(sample_portfolio_report)
        
        kpis = enricher.find_kpis_for_strategy("EasterGold.html")
        assert kpis is not None
    
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
    
    def test_generate_kpi_html_contains_values(self, sample_portfolio_report):
        """Le HTML généré contient les valeurs KPI."""
        from src.enrichers.kpi_enricher import KPIEnricher
        
        enricher = KPIEnricher(sample_portfolio_report)
        
        kpis = enricher.find_kpis_for_strategy("EasterGold")
        if kpis:
            html = enricher.generate_kpi_html(kpis)
            
            # Vérifier que le HTML contient des éléments clés
            assert "Net Profit" in html
            assert "Max Drawdown" in html
            assert "Total Trades" in html
