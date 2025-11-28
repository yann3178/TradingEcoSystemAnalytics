# -*- coding: utf-8 -*-
"""
Fixtures Pytest partagées pour les tests du Trading Strategy Pipeline V2.
"""

import pytest
import pandas as pd
from pathlib import Path
import sys

# Ajouter src au path pour les imports
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "src"))

SAMPLES_DIR = Path(__file__).parent / "data" / "samples"
EXPECTED_DIR = Path(__file__).parent / "data" / "expected"


# =============================================================================
# STRATÉGIES DE TEST
# =============================================================================

# Stratégies qui correspondent aux données dans portfolio_report.csv
SAMPLE_STRATEGIES = [
    "Yann_Casey_strategy_v0.1",  # Nom exact dans le CSV
    "SOM_UA_2303_Y_3",
    "EasterGold",
    "TOP_UA_287_GC_5",
    "SOM_UA_2302_G_1",
    "SOM_UA_2311_G_1",
    "TOP_UA_152_NQ_5",
    "SOM_UA_2305_G_1",
    "TOP_UA_228_FDAX_30",
    "TOP_UA_556_ES_15",
]


@pytest.fixture(scope="session")
def sample_strategies():
    """Liste des stratégies de test."""
    return SAMPLE_STRATEGIES


# =============================================================================
# DONNÉES D'ENTRÉE
# =============================================================================

@pytest.fixture(scope="session")
def sample_portfolio_report():
    """Portfolio Report échantillon."""
    csv_path = SAMPLES_DIR / "portfolio_report.csv"
    if not csv_path.exists():
        pytest.skip(f"Fichier de test manquant: {csv_path}")
    return pd.read_csv(csv_path, sep=";", decimal=",")


@pytest.fixture(scope="session")
def sample_consolidated():
    """Données consolidées échantillon (avec coûts)."""
    csv_path = SAMPLES_DIR / "consolidated.csv"
    if not csv_path.exists():
        pytest.skip(f"Fichier de test manquant: {csv_path}")
    return pd.read_csv(csv_path, sep=";", decimal=",")


@pytest.fixture(scope="session")
def sample_equity_curves_dir():
    """Répertoire des equity curves échantillon."""
    eq_dir = SAMPLES_DIR / "equity_curves"
    if not eq_dir.exists():
        pytest.skip(f"Répertoire de test manquant: {eq_dir}")
    return eq_dir


# =============================================================================
# DONNÉES DE RÉFÉRENCE V1
# =============================================================================

@pytest.fixture(scope="session")
def v1_reference_kpis():
    """KPIs de référence V1."""
    csv_path = EXPECTED_DIR / "v1_kpis" / "kpis_reference.csv"
    if not csv_path.exists():
        pytest.skip(f"Fichier de référence V1 manquant: {csv_path}")
    # Format français: virgule comme séparateur décimal
    return pd.read_csv(csv_path, sep=";", decimal=",")


@pytest.fixture(scope="session")
def v1_reference_mc():
    """Résultats Monte Carlo de référence V1."""
    csv_path = EXPECTED_DIR / "v1_monte_carlo" / "mc_summary.csv"
    if not csv_path.exists():
        pytest.skip(f"Fichier de référence V1 manquant: {csv_path}")
    return pd.read_csv(csv_path, sep=";", decimal=",")


@pytest.fixture(scope="session")
def v1_reference_correlation():
    """Matrice de corrélation de référence V1."""
    csv_path = EXPECTED_DIR / "v1_correlation" / "correlation_matrix.csv"
    if not csv_path.exists():
        pytest.skip(f"Fichier de référence V1 manquant: {csv_path}")
    return pd.read_csv(csv_path, sep=";", decimal=",", index_col=0)


# =============================================================================
# FIXTURES UTILITAIRES
# =============================================================================

@pytest.fixture(scope="function")
def temp_html_dir(tmp_path):
    """Répertoire temporaire pour les HTML de test."""
    html_dir = tmp_path / "html_reports"
    html_dir.mkdir()
    return html_dir


@pytest.fixture(scope="function")
def temp_output_dir(tmp_path):
    """Répertoire temporaire pour les outputs de test."""
    output_dir = tmp_path / "outputs"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def sample_html_content():
    """Contenu HTML minimal pour tests d'enrichissement."""
    return """<!DOCTYPE html>
<html>
<head>
    <title>Test Strategy - Strategy Analysis</title>
    <style>
        body { font-family: Arial; }
    </style>
</head>
<body>
    <h1>Test Strategy - Strategy Analysis</h1>
    <div class="back-link"><a href="index.html">← Back to Dashboard</a></div>
    <h2>📝 Summary</h2>
    <p>Test content</p>
</body>
</html>"""


# =============================================================================
# HELPERS
# =============================================================================

def assert_dataframes_equal(df1, df2, tolerance=0.0001, columns=None):
    """
    Compare deux DataFrames avec tolérance pour les colonnes numériques.
    
    Args:
        df1, df2: DataFrames à comparer
        tolerance: Tolérance relative pour les valeurs numériques
        columns: Liste des colonnes à comparer (toutes si None)
    """
    if columns is None:
        columns = list(set(df1.columns) & set(df2.columns))
    
    for col in columns:
        if df1[col].dtype in ['float64', 'int64']:
            # Comparaison numérique avec tolérance
            diff = abs(df1[col] - df2[col]) / (abs(df1[col]) + 1e-10)
            max_diff = diff.max()
            assert max_diff < tolerance, f"Colonne {col}: diff max = {max_diff}"
        else:
            # Comparaison exacte pour les strings
            assert (df1[col] == df2[col]).all(), f"Colonne {col}: valeurs différentes"


def assert_values_close(v1, v2, tolerance=0.01, msg=""):
    """Vérifie que deux valeurs sont proches."""
    if v1 == 0 and v2 == 0:
        return
    diff = abs(v1 - v2) / max(abs(v1), abs(v2))
    assert diff < tolerance, f"{msg}: {v1} vs {v2} (diff={diff:.4f})"
