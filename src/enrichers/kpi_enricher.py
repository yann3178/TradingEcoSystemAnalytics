"""
KPI Enricher - Module d'enrichissement avec indicateurs de performance
======================================================================
Ajoute les KPIs du Portfolio Report aux rapports HTML.

Version: 2.0.0
"""

import csv
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.settings import (
    PORTFOLIO_REPORTS_DIR, HTML_REPORTS_DIR, 
    FUZZY_MATCH_THRESHOLD, MIN_MATCH_CHARS,
    get_latest_portfolio_report
)
from src.utils.file_utils import safe_read
from src.utils.matching import find_best_match, normalize_strategy_name


class KPIEnricher:
    """
    Enrichit les rapports HTML avec les KPIs de performance.
    """
    
    def __init__(self, portfolio_report_path: Optional[Path] = None):
        """
        Initialise l'enrichisseur avec un Portfolio Report.
        
        Args:
            portfolio_report_path: Chemin du fichier Portfolio Report (auto-détecté si None)
        """
        self.portfolio_data: Dict[str, Dict] = {}
        self.strategy_names: List[str] = []
        
        if portfolio_report_path is None:
            try:
                portfolio_report_path = get_latest_portfolio_report()
            except FileNotFoundError:
                print("⚠️  Aucun Portfolio Report trouvé")
                return
        
        if portfolio_report_path and portfolio_report_path.exists():
            self._load_portfolio_report(portfolio_report_path)
    
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
                
                self.portfolio_data[strategy_name] = processed_row
                self.strategy_names.append(strategy_name)
        
        print(f"   ✓ {len(self.portfolio_data)} stratégies chargées")
    
    def find_kpis_for_strategy(self, html_filename: str) -> Optional[Dict]:
        """
        Trouve les KPIs correspondant à un fichier HTML.
        
        Args:
            html_filename: Nom du fichier HTML (ex: "EasterGold.html")
        
        Returns:
            Dict des KPIs ou None si non trouvé
        """
        if not self.portfolio_data:
            return None
        
        base_name = html_filename.replace('.html', '').replace('.bak', '')
        
        # 1. Match exact
        if base_name in self.portfolio_data:
            return self.portfolio_data[base_name]
        
        # 2. Match fuzzy
        match_result = find_best_match(
            base_name, 
            self.strategy_names,
            threshold=FUZZY_MATCH_THRESHOLD,
            min_chars=MIN_MATCH_CHARS
        )
        
        if match_result:
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
                <div class="kpi-value {self.get_value_class(kpis.get('Net_Profit_Total'))}">{self.format_currency(kpis.get('Net_Profit_Total'), currency)}</div>
            </div>
            <div class="kpi-card main">
                <div class="kpi-title">Max Drawdown</div>
                <div class="kpi-value negative">{self.format_currency(kpis.get('Net_Max_Drawdown'), currency)}</div>
            </div>
            <div class="kpi-card main">
                <div class="kpi-title">Ratio NP/DD</div>
                <div class="kpi-value">{self.format_number(kpis.get('Net_Ratio_NP_DD'))}</div>
            </div>
            <div class="kpi-card main">
                <div class="kpi-title">Total Trades</div>
                <div class="kpi-value">{self.format_number(kpis.get('Nombre_Trades'), 0)}</div>
            </div>
        </div>
        
        <!-- Secondary KPIs -->
        <div class="kpi-secondary-grid">
            <div class="kpi-card">
                <div class="kpi-title">Avg Trade</div>
                <div class="kpi-value {self.get_value_class(kpis.get('Net_Average_Trade'))}">{self.format_currency(kpis.get('Net_Average_Trade'), currency)}</div>
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

def create_kpi_enricher(portfolio_report_path: Optional[Path] = None) -> KPIEnricher:
    """Factory function pour créer un KPIEnricher."""
    return KPIEnricher(portfolio_report_path)
