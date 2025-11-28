"""
KPI Enricher - Module d'enrichissement avec indicateurs de performance
======================================================================
Ajoute les KPIs du Portfolio Report aux rapports HTML.

Version: 2.1.0
"""

import csv
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

from src.utils.matching import find_best_match, normalize_strategy_name

# Import conditionnel des settings (peut ne pas exister dans les tests)
try:
    from config.settings import (
        PORTFOLIO_REPORTS_DIR, HTML_REPORTS_DIR, 
        FUZZY_MATCH_THRESHOLD, MIN_MATCH_CHARS,
        get_latest_portfolio_report
    )
except ImportError:
    PORTFOLIO_REPORTS_DIR = None
    HTML_REPORTS_DIR = None
    FUZZY_MATCH_THRESHOLD = 0.80
    MIN_MATCH_CHARS = 3
    def get_latest_portfolio_report():
        raise FileNotFoundError("Settings not configured")


class KPIEnricher:
    """
    Enrichit les rapports HTML avec les KPIs de performance.
    
    Accepte soit:
    - Un chemin vers un fichier CSV (Path ou str)
    - Un DataFrame pandas déjà chargé
    - None pour auto-détection du dernier Portfolio Report
    """
    
    # Mapping des noms de colonnes (DataFrame -> interne)
    COLUMN_MAPPING = {
        # Colonnes de référence V1
        'Strategy_Name': 'Strategie',
        'Symbol': 'Symbol',
        'Total_Trades': 'Nombre_Trades',
        'Net_Profit': 'Net_Profit_Total',
        'Max_Drawdown': 'Net_Max_Drawdown',
        'Avg_Trade': 'Net_Average_Trade',
        'Ratio_NP_DD': 'Net_Ratio_NP_DD',
    }
    
    def __init__(self, source: Optional[Union[Path, str, "pd.DataFrame"]] = None):
        """
        Initialise l'enrichisseur avec un Portfolio Report.
        
        Args:
            source: Chemin du fichier CSV, DataFrame pandas, ou None (auto-détection)
        """
        self.portfolio_data: Dict[str, Dict] = {}
        self.strategy_names: List[str] = []
        
        if source is None:
            # Auto-détection du dernier Portfolio Report
            try:
                source = get_latest_portfolio_report()
            except FileNotFoundError:
                print("⚠️  Aucun Portfolio Report trouvé")
                return
        
        # Déterminer le type de source et charger
        if HAS_PANDAS and isinstance(source, pd.DataFrame):
            self._load_from_dataframe(source)
        elif isinstance(source, (Path, str)):
            path = Path(source) if isinstance(source, str) else source
            if path.exists():
                self._load_portfolio_report(path)
            else:
                print(f"⚠️  Fichier non trouvé: {path}")
        else:
            print(f"⚠️  Type de source non supporté: {type(source)}")
    
    def _load_from_dataframe(self, df: "pd.DataFrame") -> None:
        """Charge les données depuis un DataFrame pandas."""
        if df.empty:
            return
        
        # Déterminer la colonne du nom de stratégie
        strategy_col = None
        for col in ['Strategie', 'Strategy_Name', 'strategy_name', 'Strategy']:
            if col in df.columns:
                strategy_col = col
                break
        
        if strategy_col is None:
            print("⚠️  Colonne de nom de stratégie non trouvée dans le DataFrame")
            return
        
        for _, row in df.iterrows():
            strategy_name = str(row.get(strategy_col, '')).strip()
            if not strategy_name:
                continue
            
            # Convertir la ligne en dict avec normalisation des valeurs
            processed_row = {}
            for col in df.columns:
                value = row.get(col)
                
                # Gérer les NaN pandas
                if HAS_PANDAS and pd.isna(value):
                    processed_row[col] = None
                elif isinstance(value, str):
                    # Essayer de convertir en nombre (virgule -> point)
                    try:
                        processed_row[col] = float(value.replace(',', '.'))
                    except ValueError:
                        processed_row[col] = value
                else:
                    processed_row[col] = value
            
            # Mapper les colonnes si nécessaire (pour compatibilité avec les tests)
            mapped_row = self._map_columns(processed_row)
            
            self.portfolio_data[strategy_name] = mapped_row
            self.strategy_names.append(strategy_name)
        
        print(f"   ✓ {len(self.portfolio_data)} stratégies chargées depuis DataFrame")
    
    def _map_columns(self, row: Dict) -> Dict:
        """
        Mappe les colonnes du format test vers le format interne.
        Préserve aussi les colonnes originales.
        """
        mapped = dict(row)  # Copie
        
        # Ajouter les mappings inverses pour compatibilité
        reverse_mapping = {v: k for k, v in self.COLUMN_MAPPING.items()}
        
        for original, internal in self.COLUMN_MAPPING.items():
            if original in row and internal not in row:
                mapped[internal] = row[original]
        
        for internal, original in reverse_mapping.items():
            if internal in row and original not in row:
                mapped[original] = row[internal]
        
        # Mappings spécifiques pour les KPIs de test (valeurs NETTES prioritaires)
        # Net Profit: priorité à Net_Profit_Total
        if 'Net_Profit_Total' in row and 'net_profit' not in mapped:
            mapped['net_profit'] = row['Net_Profit_Total']
        elif 'Net_Profit' in row and 'net_profit' not in mapped:
            mapped['net_profit'] = row['Net_Profit']
        
        # Max Drawdown: priorité à Net_Max_Drawdown (pas Max_Drawdown qui est brut)
        if 'Net_Max_Drawdown' in row and 'max_drawdown' not in mapped:
            mapped['max_drawdown'] = row['Net_Max_Drawdown']
        # Ne PAS utiliser Max_Drawdown car c'est la valeur brute
        
        # Total Trades
        if 'Nombre_Trades' in row and 'total_trades' not in mapped:
            mapped['total_trades'] = row['Nombre_Trades']
        elif 'Total_Trades' in row and 'total_trades' not in mapped:
            mapped['total_trades'] = row['Total_Trades']
        
        # Avg Trade: priorité à Net_Average_Trade
        if 'Net_Average_Trade' in row and 'avg_trade' not in mapped:
            mapped['avg_trade'] = row['Net_Average_Trade']
        elif 'Avg_Trade' in row and 'avg_trade' not in mapped:
            mapped['avg_trade'] = row['Avg_Trade']
        
        return mapped
    
    def _load_portfolio_report(self, filepath: Path) -> None:
        """Charge le Portfolio Report CSV."""
        print(f"📊 Chargement de {filepath.name}...")
        
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            
            for row in reader:
                strategy_name = row.get('Strategie', '').strip()
                if not strategy_name:
                    continue
                
                # Convertir les valeurs numériques (virgule -> point)
                processed_row = {}
                for key, value in row.items():
                    if value:
                        try:
                            processed_row[key] = float(value.replace(',', '.'))
                        except ValueError:
                            processed_row[key] = value
                    else:
                        processed_row[key] = None
                
                # Ajouter les mappings pour compatibilité
                mapped_row = self._map_columns(processed_row)
                
                self.portfolio_data[strategy_name] = mapped_row
                self.strategy_names.append(strategy_name)
        
        print(f"   ✓ {len(self.portfolio_data)} stratégies chargées")
    
    def find_kpis_for_strategy(self, strategy_name: str) -> Optional[Dict]:
        """
        Trouve les KPIs correspondant à une stratégie.
        
        Args:
            strategy_name: Nom de la stratégie ou du fichier HTML
        
        Returns:
            Dict des KPIs ou None si non trouvé
        """
        if not self.portfolio_data:
            return None
        
        # Nettoyer le nom (enlever .html, .bak, etc.)
        base_name = strategy_name.replace('.html', '').replace('.bak', '').strip()
        
        # 1. Match exact
        if base_name in self.portfolio_data:
            return self.portfolio_data[base_name]
        
        # 2. Match exact insensible à la casse
        for name in self.strategy_names:
            if name.lower() == base_name.lower():
                return self.portfolio_data[name]
        
        # 3. Match fuzzy
        match_result = find_best_match(
            base_name, 
            self.strategy_names,
            threshold=FUZZY_MATCH_THRESHOLD,
            min_chars=MIN_MATCH_CHARS
        )
        
        if match_result and match_result[0] is not None:
            matched_name, score = match_result
            return self.portfolio_data[matched_name]
        
        return None
    
    @staticmethod
    def format_currency(value, currency: str = "USD", decimals: int = 0) -> str:
        """Formate une valeur monétaire."""
        if value is None:
            return "N/A"
        
        try:
            num = float(value)
            sign = "+" if num > 0 else ""
            
            if currency == "EUR":
                return f"{sign}{num:,.{decimals}f} €".replace(',', ' ')
            else:
                return f"{sign}${num:,.{decimals}f}".replace(',', ' ')
        except (ValueError, TypeError):
            return "N/A"
    
    @staticmethod
    def format_number(value, decimals: int = 2) -> str:
        """Formate un nombre."""
        if value is None:
            return "N/A"
        
        try:
            return f"{float(value):,.{decimals}f}".replace(',', ' ')
        except (ValueError, TypeError):
            return "N/A"
    
    @staticmethod
    def format_percent(value, decimals: int = 1) -> str:
        """Formate un pourcentage."""
        if value is None:
            return "N/A"
        
        try:
            return f"{float(value):.{decimals}f}%"
        except (ValueError, TypeError):
            return "N/A"
    
    @staticmethod
    def get_value_class(value) -> str:
        """Retourne la classe CSS (positive/negative/neutral)."""
        try:
            num = float(value)
            if num > 0:
                return "positive"
            elif num < 0:
                return "negative"
        except (ValueError, TypeError):
            pass
        return "neutral"
    
    def generate_kpi_html(self, kpis: Dict) -> str:
        """
        Génère le HTML de la section KPI Dashboard.
        
        Args:
            kpis: Dictionnaire des KPIs
        
        Returns:
            Code HTML de la section
        """
        if not kpis:
            return self._generate_no_data_section("KPIs")
        
        currency = kpis.get('Currency', 'USD')
        
        # Compatibilité avec différents noms de colonnes
        net_profit = kpis.get('Net_Profit_Total') or kpis.get('net_profit') or kpis.get('Net_Profit')
        max_dd = kpis.get('Net_Max_Drawdown') or kpis.get('max_drawdown') or kpis.get('Max_Drawdown')
        ratio = kpis.get('Net_Ratio_NP_DD') or kpis.get('Ratio_NP_DD')
        total_trades = kpis.get('Nombre_Trades') or kpis.get('total_trades') or kpis.get('Total_Trades')
        avg_trade = kpis.get('Net_Average_Trade') or kpis.get('avg_trade') or kpis.get('Avg_Trade')
        
        return f'''
    <div class="kpi-dashboard">
        <h2>📈 Performance Dashboard</h2>
        
        <!-- Header Info -->
        <div class="kpi-header-row">
            <div class="kpi-chip">
                <span class="chip-label">Symbol</span>
                <span class="chip-value">{kpis.get('Symbol', 'N/A')}</span>
            </div>
            <div class="kpi-chip">
                <span class="chip-label">Currency</span>
                <span class="chip-value">{currency}</span>
            </div>
            <div class="kpi-chip">
                <span class="chip-label">Timeframe</span>
                <span class="chip-value">{kpis.get('Timeframe', 'N/A')}</span>
            </div>
            <div class="kpi-chip">
                <span class="chip-label">Period</span>
                <span class="chip-value">{kpis.get('Date_Debut', 'N/A')} → {kpis.get('Date_Fin', 'N/A')}</span>
            </div>
        </div>
        
        <!-- Main KPIs -->
        <div class="kpi-main-grid">
            <div class="kpi-card main">
                <div class="kpi-title">Net Profit</div>
                <div class="kpi-value {self.get_value_class(net_profit)}">{self.format_currency(net_profit, currency)}</div>
            </div>
            <div class="kpi-card main">
                <div class="kpi-title">Max Drawdown</div>
                <div class="kpi-value negative">{self.format_currency(max_dd, currency)}</div>
            </div>
            <div class="kpi-card main">
                <div class="kpi-title">Ratio NP/DD</div>
                <div class="kpi-value">{self.format_number(ratio)}</div>
            </div>
            <div class="kpi-card main">
                <div class="kpi-title">Total Trades</div>
                <div class="kpi-value">{self.format_number(total_trades, 0)}</div>
            </div>
        </div>
        
        <!-- Secondary KPIs -->
        <div class="kpi-secondary-grid">
            <div class="kpi-card">
                <div class="kpi-title">Avg Trade</div>
                <div class="kpi-value {self.get_value_class(avg_trade)}">{self.format_currency(avg_trade, currency)}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">YTD Profit</div>
                <div class="kpi-value {self.get_value_class(kpis.get('YTD_Net_Profit'))}">{self.format_currency(kpis.get('YTD_Net_Profit'), currency)}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">IS/OOS Efficiency</div>
                <div class="kpi-value">{self.format_number(kpis.get('IS_OOS_Efficiency'))}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">% Exposition</div>
                <div class="kpi-value">{self.format_percent(kpis.get('Pct_Exposition'))}</div>
            </div>
        </div>
        
        <!-- IS/OOS Section -->
        {self._generate_isoos_section(kpis, currency)}
        
        <!-- Period Table -->
        {self._generate_period_table(kpis, currency)}
    </div>
    '''
    
    def _generate_isoos_section(self, kpis: Dict, currency: str) -> str:
        """Génère la section IS/OOS."""
        oos_start = kpis.get('Date_Debut_OOS') or 'N/A'
        oos_days = kpis.get('Duree_OOS_Jours')
        oos_days_str = f"({self.format_number(oos_days, 0)} days)" if oos_days else ""
        
        return f'''
        <div class="isoos-section">
            <h3>📊 In Sample / Out of Sample Analysis</h3>
            <div class="isoos-info">
                <div class="isoos-badge is">
                    <span class="badge-label">In Sample</span>
                    <span class="badge-value">{kpis.get('Date_Debut', 'N/A')} → {oos_start}</span>
                </div>
                <div class="isoos-badge oos">
                    <span class="badge-label">Out of Sample</span>
                    <span class="badge-value">{oos_start} → {kpis.get('Date_Fin', 'N/A')}</span>
                    <span class="badge-duration">{oos_days_str}</span>
                </div>
            </div>
            <div class="isoos-metrics">
                <div class="kpi-card">
                    <div class="kpi-title">IS Monthly Return</div>
                    <div class="kpi-value {self.get_value_class(kpis.get('Backtest_Avg_Monthly_Return'))}">{self.format_currency(kpis.get('Backtest_Avg_Monthly_Return'), currency)}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">OOS Monthly Return</div>
                    <div class="kpi-value {self.get_value_class(kpis.get('OOS_Avg_Monthly_Return'))}">{self.format_currency(kpis.get('OOS_Avg_Monthly_Return'), currency)}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">IS/OOS Ratio</div>
                    <div class="kpi-value">{self.format_number(kpis.get('IS_OOS_Efficiency'))}</div>
                </div>
            </div>
        </div>
        '''
    
    def _generate_period_table(self, kpis: Dict, currency: str) -> str:
        """Génère le tableau des performances par période."""
        periods = [
            ('YTD', 'YTD'),
            ('Current Month', 'Dernier_Mois'),
            ('Previous Month', 'Mois_Precedent'),
            ('Current Week', 'Derniere_Semaine'),
            ('Previous Year', 'Annee_Precedente'),
        ]
        
        rows = ""
        for label, prefix in periods:
            gross = kpis.get(f'{prefix}_Profit')
            net = kpis.get(f'{prefix}_Net_Profit')
            trades = kpis.get(f'{prefix}_Trades')
            dd = kpis.get(f'{prefix}_Net_Max_DD')
            
            rows += f'''
                <tr>
                    <td>{label}</td>
                    <td class="{self.get_value_class(gross)}">{self.format_currency(gross, currency)}</td>
                    <td class="{self.get_value_class(net)}">{self.format_currency(net, currency)}</td>
                    <td>{self.format_number(trades, 0)}</td>
                    <td class="negative">{self.format_currency(dd, currency)}</td>
                </tr>
            '''
        
        return f'''
        <div class="period-section">
            <h3>📅 Performance by Period</h3>
            <table class="period-table">
                <thead>
                    <tr>
                        <th>Period</th>
                        <th>Gross Profit</th>
                        <th>Net Profit</th>
                        <th>Trades</th>
                        <th>Max DD</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
        '''
    
    @staticmethod
    def _generate_no_data_section(data_type: str) -> str:
        """Génère une section N/A."""
        return f'''
        <div class="kpi-dashboard">
            <h2>📈 Performance Dashboard</h2>
            <div class="no-data">
                <p>⚠️ {data_type} not available for this strategy in Portfolio Report.</p>
            </div>
        </div>
        '''


# =============================================================================
# FONCTIONS PUBLIQUES
# =============================================================================

def create_kpi_enricher(source: Optional[Union[Path, str, "pd.DataFrame"]] = None) -> KPIEnricher:
    """
    Factory function pour créer un KPIEnricher.
    
    Args:
        source: Chemin CSV, DataFrame pandas, ou None (auto-détection)
    
    Returns:
        Instance de KPIEnricher
    """
    return KPIEnricher(source)
