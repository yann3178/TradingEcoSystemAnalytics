# Trading Strategy Pipeline V2 - Stratégie de Tests

## Vue d'ensemble

Le système de tests vise à garantir que :
1. **Régression** : La V2 produit les mêmes résultats que la V1 (là où applicable)
2. **Qualité** : Les nouveaux modules fonctionnent correctement
3. **Intégration** : Les composants interagissent correctement

---

## 1. Structure des Tests

```
tests/
├── __init__.py
├── conftest.py                    # Fixtures pytest partagées
├── pytest.ini                     # Configuration pytest
│
├── data/                          # Données de test
│   ├── samples/                   # Échantillons d'entrée (versionnés)
│   │   ├── strategies/            # 5-10 fichiers .txt PowerLanguage
│   │   ├── equity_curves/         # 5-10 fichiers DataSource
│   │   ├── portfolio_report.csv   # Sous-ensemble du Portfolio Report
│   │   └── consolidated.csv       # Sous-ensemble consolidé avec coûts
│   │
│   └── expected/                  # Résultats attendus (versionnés)
│       ├── v1_kpis/               # KPIs extraits de la V1
│       ├── v1_monte_carlo/        # Résultats MC de la V1
│       └── v1_correlation/        # Matrices de la V1
│
├── unit/                          # Tests unitaires
│   ├── test_file_utils.py
│   ├── test_matching.py
│   ├── test_constants.py
│   ├── test_kpi_enricher.py
│   ├── test_equity_enricher.py
│   └── test_monte_carlo.py
│
├── integration/                   # Tests d'intégration
│   ├── test_enrichment_pipeline.py
│   ├── test_monte_carlo_batch.py
│   └── test_correlation_pipeline.py
│
└── validation/                    # Tests de validation V1 vs V2
    ├── test_kpi_regression.py
    ├── test_monte_carlo_regression.py
    ├── test_correlation_regression.py
    └── test_html_structure.py
```

---

## 2. Données de Test

### 2.1 Échantillons Sélectionnés

On sélectionne **10 stratégies représentatives** couvrant :

| Stratégie | Symbole | Type | Particularité |
|-----------|---------|------|---------------|
| TOP_UA_287_GC_5 | GC | BREAKOUT | Haute fréquence |
| SOM_UA_2303_Y_3 | ES | TREND | Long terme |
| EasterGold | GC | SEASONAL | Pattern saisonnier |
| Casey_strategy_v0.1 | NQ | HYBRID | Custom |
| $PS_274_comp_UnmirrTF | FDAX | TREND | Multi-timeframe |
| ... | ... | ... | ... |

### 2.2 Extraction des Données de Test

Script pour extraire les données de test depuis la V1 :

```python
# extract_test_data.py
"""
Extrait un sous-ensemble de données pour les tests.
À exécuter UNE FOIS pour créer les fichiers de référence.
"""

SAMPLE_STRATEGIES = [
    "TOP_UA_287_GC_5",
    "SOM_UA_2303_Y_3", 
    "EasterGold",
    "Casey_strategy_v0.1",
    # ...
]
```

---

## 3. Types de Tests

### 3.1 Tests Unitaires

Vérifient chaque fonction individuellement.

```python
# tests/unit/test_matching.py

import pytest
from src.utils.matching import (
    levenshtein_distance,
    similarity_ratio,
    normalize_strategy_name,
    find_best_match
)

class TestLevenshteinDistance:
    def test_identical_strings(self):
        assert levenshtein_distance("abc", "abc") == 0
    
    def test_empty_strings(self):
        assert levenshtein_distance("", "abc") == 3
    
    def test_known_distance(self):
        assert levenshtein_distance("kitten", "sitting") == 3

class TestNormalizeStrategyName:
    def test_remove_prefix(self):
        assert "287" in normalize_strategy_name("TOP_UA_287_GC_5")
    
    def test_lowercase(self):
        result = normalize_strategy_name("EasterGold")
        assert result == result.lower()

class TestFindBestMatch:
    def test_exact_match(self):
        candidates = ["EasterGold", "SummerGold", "WinterGold"]
        match, score = find_best_match("EasterGold", candidates)
        assert match == "EasterGold"
        assert score == 1.0
    
    def test_fuzzy_match(self):
        candidates = ["GC_EasterGold_MC", "SummerGold"]
        match, score = find_best_match("EasterGold", candidates)
        assert "Easter" in match
        assert score > 0.7
```

### 3.2 Tests de Validation V1 vs V2

**Principe** : Comparer les outputs de la V2 avec ceux de la V1 (résultats de référence).

```python
# tests/validation/test_kpi_regression.py

import pytest
import pandas as pd
from pathlib import Path

# Chemins
SAMPLES_DIR = Path(__file__).parent.parent / "data" / "samples"
EXPECTED_DIR = Path(__file__).parent.parent / "data" / "expected"

class TestKPIRegression:
    """
    Vérifie que les KPIs extraits par V2 correspondent à ceux de V1.
    """
    
    @pytest.fixture
    def v1_kpis(self):
        """Charge les KPIs de référence V1."""
        return pd.read_csv(EXPECTED_DIR / "v1_kpis" / "kpis_reference.csv", sep=";")
    
    @pytest.fixture
    def sample_portfolio_report(self):
        """Charge le Portfolio Report échantillon."""
        return pd.read_csv(SAMPLES_DIR / "portfolio_report.csv", sep=";")
    
    def test_net_profit_matches(self, v1_kpis, sample_portfolio_report):
        """Le Net Profit V2 doit correspondre à V1 (tolérance 0.01%)."""
        from src.enrichers.kpi_enricher import KPIEnricher
        
        enricher = KPIEnricher(sample_portfolio_report)
        
        for _, row in v1_kpis.iterrows():
            strategy = row["Strategy_Name"]
            expected_np = row["Net_Profit"]
            
            kpis = enricher.find_kpis_for_strategy(strategy)
            if kpis:
                actual_np = kpis.get("net_profit", 0)
                assert abs(actual_np - expected_np) / abs(expected_np) < 0.0001, \
                    f"Net Profit mismatch for {strategy}: {actual_np} vs {expected_np}"
    
    def test_max_drawdown_matches(self, v1_kpis, sample_portfolio_report):
        """Le Max Drawdown V2 doit correspondre à V1."""
        # ... similar logic
        pass
    
    def test_all_kpis_present(self, v1_kpis, sample_portfolio_report):
        """Toutes les stratégies V1 doivent avoir des KPIs en V2."""
        from src.enrichers.kpi_enricher import KPIEnricher
        
        enricher = KPIEnricher(sample_portfolio_report)
        
        missing = []
        for strategy in v1_kpis["Strategy_Name"]:
            kpis = enricher.find_kpis_for_strategy(strategy)
            if not kpis:
                missing.append(strategy)
        
        assert len(missing) == 0, f"Stratégies sans KPIs: {missing}"
```

### 3.3 Tests Monte Carlo

```python
# tests/validation/test_monte_carlo_regression.py

import pytest
import pandas as pd
import numpy as np
from pathlib import Path

EXPECTED_DIR = Path(__file__).parent.parent / "data" / "expected"
SAMPLES_DIR = Path(__file__).parent.parent / "data" / "samples"

class TestMonteCarloRegression:
    """
    Vérifie que les simulations MC V2 correspondent à V1.
    Note: Les simulations MC sont stochastiques, donc on compare
    avec une tolérance statistique.
    """
    
    @pytest.fixture
    def v1_mc_results(self):
        """Résultats MC de référence V1."""
        return pd.read_csv(EXPECTED_DIR / "v1_monte_carlo" / "mc_summary.csv", sep=";")
    
    def test_recommended_capital_within_range(self, v1_mc_results):
        """
        Le capital recommandé V2 doit être dans une plage acceptable.
        Tolérance: ± 1 niveau de capital (2500$)
        """
        from src.monte_carlo.simulator import MonteCarloSimulator
        
        for _, row in v1_mc_results.iterrows():
            strategy = row["Strategy_Name"]
            v1_capital = row["Recommended_Capital"]
            
            if pd.isna(v1_capital) or v1_capital == "N/A":
                continue
            
            # Charger les trades de test
            trades_file = SAMPLES_DIR / "trades" / f"{strategy}.csv"
            if not trades_file.exists():
                continue
            
            # Simuler avec seed fixe pour reproductibilité
            mc = MonteCarloSimulator(str(trades_file), random_seed=42)
            mc.run(verbose=False)
            
            v2_capital = mc.recommended_capital
            
            if v2_capital is not None:
                diff = abs(float(v2_capital) - float(v1_capital))
                assert diff <= 2500, \
                    f"Capital mismatch for {strategy}: V2={v2_capital} vs V1={v1_capital}"
    
    def test_ruin_probability_stable(self, v1_mc_results):
        """
        La probabilité de ruine doit être stable (± 2%).
        """
        # ... implementation
        pass
    
    def test_return_dd_ratio_stable(self, v1_mc_results):
        """
        Le ratio Return/DD doit être stable (± 10%).
        """
        # ... implementation
        pass
```

### 3.4 Tests de Structure HTML

```python
# tests/validation/test_html_structure.py

import pytest
from bs4 import BeautifulSoup
from pathlib import Path

class TestHTMLStructure:
    """
    Vérifie que les HTML enrichis ont la bonne structure.
    """
    
    def test_kpi_dashboard_present(self, enriched_html):
        """Le dashboard KPI doit être présent."""
        soup = BeautifulSoup(enriched_html, "html.parser")
        dashboard = soup.find("div", class_="kpi-dashboard")
        assert dashboard is not None, "KPI dashboard manquant"
    
    def test_equity_chart_present(self, enriched_html):
        """Le graphique equity doit être présent."""
        soup = BeautifulSoup(enriched_html, "html.parser")
        chart = soup.find("canvas", id="equityChart")
        assert chart is not None, "Equity chart manquant"
    
    def test_chartjs_script_present(self, enriched_html):
        """Le script Chart.js doit être inclus."""
        assert "cdn.jsdelivr.net/npm/chart.js" in enriched_html
    
    def test_no_broken_tags(self, enriched_html):
        """Pas de balises HTML cassées."""
        soup = BeautifulSoup(enriched_html, "html.parser")
        # BeautifulSoup corrige automatiquement, donc on vérifie
        # que le re-parsing donne le même résultat
        reparsed = str(soup)
        assert len(reparsed) > 100  # Document non vide
    
    def test_mc_link_present_if_exists(self, enriched_html, mc_exists):
        """Lien MC présent si fiche MC existe."""
        if mc_exists:
            assert "MonteCarlo" in enriched_html or "monte-carlo" in enriched_html.lower()
```

---

## 4. Fixtures Pytest Partagées

```python
# tests/conftest.py

import pytest
import pandas as pd
from pathlib import Path
import sys

# Ajouter src au path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

SAMPLES_DIR = Path(__file__).parent / "data" / "samples"
EXPECTED_DIR = Path(__file__).parent / "data" / "expected"


@pytest.fixture(scope="session")
def sample_portfolio_report():
    """Portfolio Report échantillon."""
    return pd.read_csv(SAMPLES_DIR / "portfolio_report.csv", sep=";", decimal=",")


@pytest.fixture(scope="session")
def sample_consolidated():
    """Données consolidées échantillon."""
    return pd.read_csv(SAMPLES_DIR / "consolidated.csv", sep=";", decimal=",")


@pytest.fixture(scope="session")
def sample_strategies():
    """Liste des stratégies de test."""
    return [
        "TOP_UA_287_GC_5",
        "SOM_UA_2303_Y_3",
        "EasterGold",
        "Casey_strategy_v0.1",
        "$PS_274_comp_UnmirrTF_jumper_nofilter_FDXM120",
    ]


@pytest.fixture(scope="function")
def temp_html_dir(tmp_path):
    """Répertoire temporaire pour les HTML de test."""
    html_dir = tmp_path / "html_reports"
    html_dir.mkdir()
    return html_dir


@pytest.fixture
def v1_reference_kpis():
    """KPIs de référence V1."""
    return pd.read_csv(EXPECTED_DIR / "v1_kpis" / "kpis_reference.csv", sep=";")


@pytest.fixture
def v1_reference_mc():
    """Résultats MC de référence V1."""
    return pd.read_csv(EXPECTED_DIR / "v1_monte_carlo" / "mc_summary.csv", sep=";")
```

---

## 5. Configuration Pytest

```ini
# tests/pytest.ini

[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Marqueurs personnalisés
markers =
    slow: Tests lents (MC batch, corrélation complète)
    validation: Tests de validation V1 vs V2
    unit: Tests unitaires
    integration: Tests d'intégration

# Options par défaut
addopts = -v --tb=short

# Ignorer les warnings
filterwarnings =
    ignore::DeprecationWarning
    ignore::UserWarning
```

---

## 6. Exécution des Tests

### Commandes

```bash
# Tous les tests
pytest

# Tests unitaires uniquement
pytest tests/unit/ -v

# Tests de validation V1 vs V2
pytest tests/validation/ -v

# Tests avec couverture
pytest --cov=src --cov-report=html --cov-report=term

# Exclure les tests lents
pytest -m "not slow"

# Un test spécifique
pytest tests/validation/test_kpi_regression.py::TestKPIRegression::test_net_profit_matches -v
```

### Intégration CI/CD (GitHub Actions)

```yaml
# .github/workflows/tests.yml

name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: pytest --cov=src --cov-report=xml -m "not slow"
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

---

## 7. Création des Données de Référence

Script pour extraire les données V1 et créer les fichiers de référence :

```python
# scripts/create_test_reference.py
"""
Crée les fichiers de référence pour les tests.
À exécuter UNE FOIS quand la V1 est stable.
"""

import pandas as pd
from pathlib import Path

V1_ROOT = Path(r"C:\TradeData")
TEST_DIR = Path(r"C:\TradeData\V2\tests\data")

SAMPLE_STRATEGIES = [
    "TOP_UA_287_GC_5",
    "SOM_UA_2303_Y_3",
    "EasterGold",
    "Casey_strategy_v0.1",
    "$PS_274_comp_UnmirrTF_jumper_nofilter_FDXM120",
    "SOM_UA_2302_G_1",
    "TOP_UA_556_ES_15",
    "SOM_UA_2305_G_1",
    "TOP_UA_152_NQ_5",
    "SOM_UA_2311_G_1",
]

def extract_portfolio_report_sample():
    """Extrait un sous-ensemble du Portfolio Report."""
    pr = pd.read_csv(
        V1_ROOT / "Results" / "Portfolio_Report_V2_20251127.csv",
        sep=";", decimal=","
    )
    sample = pr[pr["Strategy"].isin(SAMPLE_STRATEGIES)]
    sample.to_csv(TEST_DIR / "samples" / "portfolio_report.csv", sep=";", index=False)
    print(f"Portfolio Report: {len(sample)} lignes")

def extract_mc_results():
    """Extrait les résultats MC pour les stratégies test."""
    mc_summary = pd.read_csv(
        V1_ROOT / "Results" / "MonteCarlo" / "MC_Summary_20251127_0050.csv",
        sep=";", decimal=","
    )
    sample = mc_summary[mc_summary["Strategy_Name"].isin(SAMPLE_STRATEGIES)]
    sample.to_csv(TEST_DIR / "expected" / "v1_monte_carlo" / "mc_summary.csv", sep=";", index=False)
    print(f"MC Summary: {len(sample)} stratégies")

def extract_kpis():
    """Extrait les KPIs de référence."""
    # Logique d'extraction depuis les HTML existants ou le Portfolio Report
    pass

if __name__ == "__main__":
    (TEST_DIR / "samples").mkdir(parents=True, exist_ok=True)
    (TEST_DIR / "expected" / "v1_kpis").mkdir(parents=True, exist_ok=True)
    (TEST_DIR / "expected" / "v1_monte_carlo").mkdir(parents=True, exist_ok=True)
    (TEST_DIR / "expected" / "v1_correlation").mkdir(parents=True, exist_ok=True)
    
    extract_portfolio_report_sample()
    extract_mc_results()
    extract_kpis()
    print("✅ Données de référence créées")
```

---

## 8. Toléances pour Tests Stochastiques

Pour Monte Carlo (stochastique), on utilise des **tolérances statistiques** :

| Métrique | Tolérance | Justification |
|----------|-----------|---------------|
| Capital recommandé | ± 1 niveau (2500$) | Variabilité bootstrap |
| Probabilité ruine | ± 2% | 2500 simulations |
| Return/DD ratio | ± 10% | Sensible aux extremes |
| Median profit | ± 5% | Plus stable |

On peut aussi utiliser un **seed fixe** (`random_seed=42`) pour des tests reproductibles.

---

## 9. Checklist Validation V2

- [ ] Tous les tests unitaires passent
- [ ] Tests de validation KPI : écart < 0.01%
- [ ] Tests de validation MC : capital ± 2500$
- [ ] Tests de validation Corrélation : matrices identiques
- [ ] Tests de structure HTML : tous les éléments présents
- [ ] Couverture de code > 80%
- [ ] Pas de régression de performance (temps d'exécution)
