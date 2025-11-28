"""
Equity Curve Enricher - Module d'enrichissement avec courbes d'équité
=====================================================================
Ajoute les graphiques d'equity curve aux rapports HTML.

Version: 2.0.0
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.settings import EQUITY_CURVES_DIR
from src.utils.file_utils import safe_read
from src.utils.matching import normalize_strategy_name, similarity_ratio


class EquityCurveEnricher:
    """
    Enrichit les rapports HTML avec les courbes d'équité.
    """
    
    def __init__(self, datasources_dir: Optional[Path] = None):
        """
        Initialise l'enrichisseur.
        
        Args:
            datasources_dir: Répertoire des fichiers DataSource
        """
        self.datasources_dir = datasources_dir or EQUITY_CURVES_DIR
        self.available_files: Dict[str, Path] = {}
        
        if self.datasources_dir.exists():
            self._index_datasource_files()
    
    def _index_datasource_files(self) -> None:
        """Indexe les fichiers DataSource disponibles."""
        for f in self.datasources_dir.glob("*.txt"):
            normalized = normalize_strategy_name(f.stem)
            self.available_files[normalized] = f
            # Aussi indexer par nom de fichier brut
            self.available_files[f.stem.lower()] = f
    
    def find_datasource(self, strategy_name: str, symbol: str = "") -> Optional[Path]:
        """
        Trouve le fichier DataSource pour une stratégie.
        
        Args:
            strategy_name: Nom de la stratégie
            symbol: Symbole de l'instrument (optionnel)
        
        Returns:
            Chemin du fichier ou None
        """
        if not self.datasources_dir.exists():
            return None
        
        # Pattern 1: Match exact avec symbole
        if symbol:
            exact_path = self.datasources_dir / f"{symbol}_{strategy_name}.txt"
            if exact_path.exists():
                return exact_path
        
        # Pattern 2: Match dans l'index
        normalized = normalize_strategy_name(strategy_name)
        if normalized in self.available_files:
            return self.available_files[normalized]
        
        # Pattern 3: Match partiel avec symbole
        if symbol:
            for f in self.datasources_dir.glob(f"{symbol}_*.txt"):
                fname_clean = normalize_strategy_name(f.stem.replace(f"{symbol}_", ""))
                if fname_clean == normalized or normalized in fname_clean:
                    return f
        
        # Pattern 4: Match fuzzy
        best_match = None
        best_score = 0.0
        
        for indexed_name, filepath in self.available_files.items():
            score = similarity_ratio(normalized, indexed_name)
            if score > best_score and score >= 0.70:
                best_score = score
                best_match = filepath
        
        return best_match
    
    def parse_datasource_file(self, filepath: Path) -> Optional[Dict]:
        """
        Parse un fichier DataSource.
        
        Format attendu: date dailyProfit nbContracts gap range nbTradesCumul
        
        Returns:
            Dict avec dates, values, daily_profits, source_file
        """
        try:
            content = safe_read(filepath)
            lines = content.strip().split('\n')
            
            dates = []
            daily_profits = []
            equity_cumul = 0.0
            values = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                parts = re.split(r'\s+', line)
                if len(parts) < 2:
                    continue
                
                try:
                    date_str = parts[0]
                    daily_profit = float(parts[1])
                    
                    equity_cumul += daily_profit
                    
                    dates.append(date_str)
                    daily_profits.append(daily_profit)
                    values.append(equity_cumul)
                except (ValueError, IndexError):
                    continue
            
            if not dates:
                return None
            
            return {
                'dates': dates,
                'values': values,
                'daily_profits': daily_profits,
                'source_file': filepath.name
            }
        
        except Exception as e:
            print(f"   ⚠️ Erreur parsing {filepath.name}: {e}")
            return None
    
    def load_equity_data(self, strategy_name: str, symbol: str = "") -> Optional[Dict]:
        """
        Charge les données d'equity pour une stratégie.
        
        Args:
            strategy_name: Nom de la stratégie
            symbol: Symbole (optionnel)
        
        Returns:
            Dict avec les données ou None
        """
        datasource_file = self.find_datasource(strategy_name, symbol)
        
        if datasource_file is None:
            return None
        
        return self.parse_datasource_file(datasource_file)
    
    def generate_equity_html(
        self, 
        equity_data: Optional[Dict], 
        oos_date: Optional[str] = None
    ) -> str:
        """
        Génère le HTML de la section Equity Curve.
        
        Args:
            equity_data: Données d'equity ou None
            oos_date: Date de début OOS (format DD/MM/YYYY)
        
        Returns:
            Code HTML avec Chart.js
        """
        if not equity_data or not equity_data.get('dates'):
            return self._generate_no_data_section()
        
        dates = equity_data['dates']
        values = equity_data['values']
        
        # Trouver l'index OOS
        oos_index, has_oos = self._find_oos_index(dates, oos_date)
        
        # Sous-échantillonner si trop de points
        dates, values, oos_index = self._downsample_data(dates, values, oos_index)
        
        # Créer les séries IS et OOS
        is_values, oos_values = self._split_is_oos(values, oos_index, has_oos)
        
        # Générer le JavaScript
        return self._generate_chart_html(
            dates, is_values, oos_values, 
            oos_index, has_oos, oos_date,
            equity_data.get('source_file', 'DataSource')
        )
    
    def _find_oos_index(
        self, 
        dates: List[str], 
        oos_date: Optional[str]
    ) -> Tuple[int, bool]:
        """Trouve l'index de début OOS."""
        if not oos_date:
            return len(dates), False
        
        try:
            oos_parts = oos_date.split('/')
            if len(oos_parts) != 3:
                return len(dates), False
            
            oos_tuple = (int(oos_parts[2]), int(oos_parts[1]), int(oos_parts[0]))
            
            for i, date in enumerate(dates):
                date_parts = date.split('/')
                if len(date_parts) == 3:
                    date_tuple = (int(date_parts[2]), int(date_parts[1]), int(date_parts[0]))
                    if date_tuple >= oos_tuple:
                        return i, True
        except (ValueError, IndexError):
            pass
        
        return len(dates), False
    
    def _downsample_data(
        self, 
        dates: List[str], 
        values: List[float], 
        oos_index: int,
        max_points: int = 2000
    ) -> Tuple[List[str], List[float], int]:
        """Réduit le nombre de points si nécessaire."""
        if len(dates) <= max_points:
            return dates, values, oos_index
        
        step = len(dates) // max_points
        dates_ds = dates[::step]
        values_ds = values[::step]
        oos_index_ds = oos_index // step
        
        return dates_ds, values_ds, oos_index_ds
    
    def _split_is_oos(
        self, 
        values: List[float], 
        oos_index: int, 
        has_oos: bool
    ) -> Tuple[List, List]:
        """Sépare les données en IS et OOS."""
        is_values = []
        oos_values = []
        
        for i, v in enumerate(values):
            rounded = round(v, 2)
            
            if i <= oos_index:
                is_values.append(rounded)
                if i == oos_index and has_oos:
                    oos_values.append(rounded)  # Point de jonction
                else:
                    oos_values.append(None)
            else:
                is_values.append(None)
                oos_values.append(rounded)
        
        return is_values, oos_values
    
    def _generate_chart_html(
        self,
        dates: List[str],
        is_values: List,
        oos_values: List,
        oos_index: int,
        has_oos: bool,
        oos_date: Optional[str],
        source_file: str
    ) -> str:
        """Génère le HTML complet avec Chart.js."""
        
        dates_json = json.dumps(dates)
        is_values_json = json.dumps(is_values)
        oos_values_json = json.dumps(oos_values)
        
        oos_display = 'flex' if has_oos else 'none'
        oos_info = f'<span class="legend-item separator">OOS Start: {oos_date}</span>' if has_oos else ''
        
        return f'''
    <div class="equity-section">
        <h2>📈 Equity Curve</h2>
        <div class="equity-legend">
            <span class="legend-item is"><span class="legend-color"></span> In Sample</span>
            <span class="legend-item oos" style="display: {oos_display}"><span class="legend-color"></span> Out of Sample</span>
            {oos_info}
        </div>
        <div class="chart-container">
            <canvas id="equityChart"></canvas>
        </div>
        <div class="equity-source">
            <small>Source: {source_file}</small>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@2.0.0"></script>
    <script>
        // Détruire le chart existant s'il y en a un
        const existingChart = Chart.getChart('equityChart');
        if (existingChart) {{
            existingChart.destroy();
        }}
        
        const ctx = document.getElementById('equityChart').getContext('2d');
        const dates = {dates_json};
        const isValues = {is_values_json};
        const oosValues = {oos_values_json};
        const oosIndex = {oos_index};
        const hasOOS = {'true' if has_oos else 'false'};
        
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: dates,
                datasets: [
                    {{
                        label: 'In Sample',
                        data: isValues,
                        borderColor: 'rgba(52, 152, 219, 1)',
                        borderWidth: 2.5,
                        pointRadius: 0,
                        fill: true,
                        backgroundColor: 'rgba(52, 152, 219, 0.15)',
                        tension: 0.1,
                        spanGaps: false
                    }},
                    {{
                        label: 'Out of Sample',
                        data: oosValues,
                        borderColor: 'rgba(39, 174, 96, 1)',
                        borderWidth: 2.5,
                        pointRadius: 0,
                        fill: true,
                        backgroundColor: 'rgba(39, 174, 96, 0.15)',
                        tension: 0.1,
                        spanGaps: false
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                interaction: {{
                    intersect: false,
                    mode: 'index'
                }},
                plugins: {{
                    legend: {{
                        display: hasOOS,
                        position: 'top'
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                if (context.parsed.y === null) return null;
                                return context.dataset.label + ': ' + 
                                    context.parsed.y.toLocaleString('en-US', {{style: 'currency', currency: 'USD'}});
                            }}
                        }},
                        filter: function(item) {{
                            return item.parsed.y !== null;
                        }}
                    }},
                    annotation: hasOOS ? {{
                        annotations: {{
                            oosLine: {{
                                type: 'line',
                                xMin: oosIndex,
                                xMax: oosIndex,
                                borderColor: 'rgba(231, 76, 60, 0.9)',
                                borderWidth: 2,
                                borderDash: [8, 4],
                                label: {{
                                    display: true,
                                    content: '◀ OOS Start',
                                    position: 'start',
                                    backgroundColor: 'rgba(231, 76, 60, 0.9)',
                                    color: 'white',
                                    font: {{ size: 11, weight: 'bold' }},
                                    padding: 4
                                }}
                            }}
                        }}
                    }} : {{}}
                }},
                scales: {{
                    x: {{
                        display: true,
                        title: {{ display: true, text: 'Date', font: {{ weight: 'bold' }} }},
                        ticks: {{ maxTicksLimit: 10, maxRotation: 45 }},
                        grid: {{ display: false }}
                    }},
                    y: {{
                        display: true,
                        title: {{ display: true, text: 'Cumulative Equity', font: {{ weight: 'bold' }} }},
                        ticks: {{
                            callback: function(value) {{ return value.toLocaleString(); }}
                        }},
                        grid: {{ color: 'rgba(0,0,0,0.05)' }}
                    }}
                }}
            }}
        }});
    </script>
    '''
    
    @staticmethod
    def _generate_no_data_section() -> str:
        """Génère une section N/A."""
        return '''
    <div class="equity-section">
        <h2>📈 Equity Curve</h2>
        <div class="no-data">
            <p>⚠️ Equity curve data not available (no matching DataSource file).</p>
        </div>
    </div>
    '''


# =============================================================================
# FONCTIONS PUBLIQUES  
# =============================================================================

def create_equity_enricher(datasources_dir: Optional[Path] = None) -> EquityCurveEnricher:
    """Factory function pour créer un EquityCurveEnricher."""
    return EquityCurveEnricher(datasources_dir)
