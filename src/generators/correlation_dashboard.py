"""
Générateur de Dashboard HTML pour l'Analyse de Corrélation
==========================================================
Crée un dashboard interactif avec onglets pour visualiser:
- Résumé et candidats à l'élimination
- Scores de corrélation par stratégie (méthode Kevin Davey)
- Matrices de corrélation Long Terme et Court Terme
- Comparaison LT vs CT (détection de changements de régime)
- Documentation méthodologique

Adapté pour consultation mobile avec design responsive.

Auteur: Trading Analytics Pipeline V2
Date: Novembre 2025
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np


class CorrelationDashboardGenerator:
    """
    Génère un dashboard HTML interactif pour l'analyse de corrélation.
    
    Attributes:
        config: Configuration de l'analyse
        timestamp: Horodatage pour les noms de fichiers
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialise le générateur.
        
        Args:
            config: Configuration optionnelle (seuils, poids, etc.)
        """
        self.config = config or self._default_config()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    
    def _default_config(self) -> Dict[str, Any]:
        """Configuration par défaut."""
        return {
            'start_year_longterm': 2012,
            'recent_months': 12,
            'correlation_threshold': 0.70,
            'high_correlation_threshold': 0.85,
            'weight_longterm': 0.5,
            'weight_recent': 0.5,
            'min_common_days_longterm': 100,
            'min_common_days_recent': 30,
        }
    
    def generate(
        self,
        corr_lt: pd.DataFrame,
        corr_ct: pd.DataFrame,
        scores: pd.DataFrame,
        stats_lt: Dict[str, Any],
        stats_ct: Dict[str, Any],
        pairs_lt: Dict[str, List],
        pairs_ct: Dict[str, List],
        biggest_changes: List[Dict],
        output_path: Path
    ) -> Path:
        """
        Génère le dashboard HTML complet.
        
        Args:
            corr_lt: Matrice de corrélation Long Terme
            corr_ct: Matrice de corrélation Court Terme
            scores: DataFrame des scores par stratégie
            stats_lt: Statistiques Long Terme
            stats_ct: Statistiques Court Terme
            pairs_lt: Paires extrêmes Long Terme
            pairs_ct: Paires extrêmes Court Terme
            biggest_changes: Plus grands changements de corrélation
            output_path: Chemin du fichier de sortie
            
        Returns:
            Path du fichier généré
        """
        # Calculer la matrice delta
        delta_matrix = self._calculate_delta(corr_lt, corr_ct)
        
        # Préparer les données pour JavaScript
        data = self._prepare_js_data(
            corr_lt, corr_ct, delta_matrix, scores,
            stats_lt, stats_ct, pairs_lt, pairs_ct, biggest_changes
        )
        
        # Générer le HTML
        html_content = self._build_html(data, stats_lt, stats_ct)
        
        # Écrire le fichier
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html_content, encoding='utf-8')
        
        return output_path
    
    def _calculate_delta(
        self,
        corr_lt: pd.DataFrame,
        corr_ct: pd.DataFrame
    ) -> pd.DataFrame:
        """Calcule la matrice de différence CT - LT."""
        common = corr_lt.columns.intersection(corr_ct.columns)
        if len(common) == 0:
            return pd.DataFrame()
        
        lt_aligned = corr_lt.loc[common, common]
        ct_aligned = corr_ct.loc[common, common]
        
        return ct_aligned - lt_aligned
    
    def _prepare_js_data(
        self,
        corr_lt: pd.DataFrame,
        corr_ct: pd.DataFrame,
        delta_matrix: pd.DataFrame,
        scores: pd.DataFrame,
        stats_lt: Dict,
        stats_ct: Dict,
        pairs_lt: Dict,
        pairs_ct: Dict,
        biggest_changes: List
    ) -> Dict[str, Any]:
        """Prépare les données pour injection JavaScript."""
        
        # Convertir scores en liste de dicts
        scores_list = []
        if scores is not None and len(scores) > 0:
            for _, row in scores.iterrows():
                score_val = row.get('Score_Davey', row.get('score_davey', 0))
                
                # Déterminer le statut
                if score_val < 2:
                    status = "Diversifiant"
                    emoji = "🟢"
                elif score_val < 5:
                    status = "Modéré"
                    emoji = "🟡"
                elif score_val < 10:
                    status = "Corrélé"
                    emoji = "🟠"
                else:
                    status = "Très corrélé"
                    emoji = "🔴"
                
                scores_list.append({
                    'Strategy': row.get('Strategy', row.get('strategy', str(row.name))),
                    'Score_Davey': float(score_val),
                    'N_Corr_LT': int(row.get('N_Corr_LT', row.get('n_corr_lt', 0))),
                    'N_Corr_CT': int(row.get('N_Corr_CT', row.get('n_corr_ct', 0))),
                    'Avg_Corr_LT': float(row.get('Avg_Corr_LT', row.get('avg_corr_lt', 0))),
                    'Avg_Corr_CT': float(row.get('Avg_Corr_CT', row.get('avg_corr_ct', 0))),
                    'Delta_Corr': float(row.get('Delta_Corr', row.get('delta_corr', 0))),
                    'Max_Corr_LT': float(row.get('Max_Corr_LT', row.get('max_corr_lt', 0))),
                    'Max_Corr_CT': float(row.get('Max_Corr_CT', row.get('max_corr_ct', 0))),
                    'Max_Corr_LT_With': row.get('Max_Corr_LT_With', row.get('max_corr_lt_with', '')),
                    'Max_Corr_CT_With': row.get('Max_Corr_CT_With', row.get('max_corr_ct_with', '')),
                    'Status': status,
                    'Status_Emoji': emoji
                })
        
        # Convertir matrices en format pour heatmap
        def matrix_to_heatmap_data(matrix: pd.DataFrame):
            if matrix is None or matrix.empty:
                return [], [], []
            
            strategies = list(matrix.columns)
            # Créer noms courts (max 15 chars)
            short_names = [s[:15] + '...' if len(s) > 15 else s for s in strategies]
            
            data_points = []
            for i, row_name in enumerate(matrix.index):
                for j, col_name in enumerate(matrix.columns):
                    val = matrix.loc[row_name, col_name]
                    if pd.notna(val):
                        data_points.append({'x': j, 'y': i, 'v': round(float(val), 4)})
            
            return strategies, short_names, data_points
        
        strat_lt, short_lt, data_lt = matrix_to_heatmap_data(corr_lt)
        strat_ct, short_ct, data_ct = matrix_to_heatmap_data(corr_ct)
        strat_delta, short_delta, data_delta = matrix_to_heatmap_data(delta_matrix)
        
        # Convertir paires
        def format_pairs(pairs_dict: Dict, key: str) -> List[Dict]:
            if not pairs_dict or key not in pairs_dict:
                return []
            return [
                {
                    'Strategy_1': p.get('Strategy_1', p.get('strategy_1', '')),
                    'Strategy_2': p.get('Strategy_2', p.get('strategy_2', '')),
                    'Correlation': float(p.get('Correlation', p.get('correlation', 0)))
                }
                for p in pairs_dict[key][:15]
            ]
        
        most_lt = format_pairs(pairs_lt, 'most_correlated')
        least_lt = format_pairs(pairs_lt, 'least_correlated')
        most_ct = format_pairs(pairs_ct, 'most_correlated')
        least_ct = format_pairs(pairs_ct, 'least_correlated')
        
        # Changements
        changes_list = []
        for c in (biggest_changes or [])[:15]:
            changes_list.append({
                'Strategy_1': c.get('Strategy_1', c.get('strategy_1', '')),
                'Strategy_2': c.get('Strategy_2', c.get('strategy_2', '')),
                'Delta': float(c.get('Delta', c.get('delta', 0)))
            })
        
        return {
            'scores_list': scores_list,
            'config': self.config,
            'stats_lt': stats_lt,
            'stats_ct': stats_ct,
            'strat_lt': strat_lt,
            'short_lt': short_lt,
            'data_lt': data_lt,
            'strat_ct': strat_ct,
            'short_ct': short_ct,
            'data_ct': data_ct,
            'strat_delta': strat_delta,
            'short_delta': short_delta,
            'data_delta': data_delta,
            'most_lt': most_lt,
            'least_lt': least_lt,
            'most_ct': most_ct,
            'least_ct': least_ct,
            'changes_list': changes_list
        }
    
    def _build_html(
        self,
        data: Dict[str, Any],
        stats_lt: Dict,
        stats_ct: Dict
    ) -> str:
        """Construit le HTML complet du dashboard."""
        
        # Extraire les données
        scores_list = data['scores_list']
        config = data['config']
        
        # Compter distribution
        n_total = len(scores_list)
        n_diversifiant = sum(1 for s in scores_list if s['Score_Davey'] < 2)
        n_modere = sum(1 for s in scores_list if 2 <= s['Score_Davey'] < 5)
        n_correle = sum(1 for s in scores_list if 5 <= s['Score_Davey'] < 10)
        n_tres_correle = sum(1 for s in scores_list if s['Score_Davey'] >= 10)
        
        # Générer les sections
        css = self._generate_css()
        nav_html = self._generate_nav()
        summary_html = self._generate_summary_tab(
            n_total, n_diversifiant, n_modere, n_correle, n_tres_correle,
            stats_lt, stats_ct, config
        )
        scores_html = self._generate_scores_tab()
        longterm_html = self._generate_matrix_tab('longterm', 'Long Terme', stats_lt, config)
        recent_html = self._generate_matrix_tab('recent', 'Court Terme', stats_ct, config)
        comparison_html = self._generate_comparison_tab(stats_lt, stats_ct)
        methodology_html = self._generate_methodology_tab(config)
        js_code = self._generate_javascript(data)
        
        return f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analyse de Corrélation - Dashboard V2</title>
    {css}
</head>
<body>
    <div id="tooltip" class="tooltip"></div>
    
    {nav_html}
    
    {summary_html}
    {scores_html}
    {longterm_html}
    {recent_html}
    {comparison_html}
    {methodology_html}
    
    {js_code}
</body>
</html>'''
    
    def _generate_css(self) -> str:
        """Génère les styles CSS."""
        return '''<style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0d1117;
            color: #c9d1d9;
            line-height: 1.6;
        }
        
        .nav {
            position: sticky;
            top: 0;
            z-index: 100;
            background: #161b22;
            padding: 8px 16px;
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            border-bottom: 1px solid #30363d;
        }
        
        .tab {
            padding: 8px 16px;
            border: none;
            background: transparent;
            color: #8b949e;
            cursor: pointer;
            border-radius: 6px;
            font-size: 14px;
            transition: all 0.2s;
        }
        
        .tab:hover { background: #21262d; color: #c9d1d9; }
        .tab.active { background: #238636; color: white; }
        
        .tab-content { display: none; padding: 20px; }
        .tab-content.active { display: block; }
        
        .container { max-width: 1400px; margin: 0 auto; }
        
        h1 { font-size: 1.8em; margin-bottom: 8px; }
        h2 { font-size: 1.4em; margin: 24px 0 12px; color: #58a6ff; }
        h3 { font-size: 1.1em; margin: 16px 0 8px; color: #8b949e; }
        
        .subtitle { color: #8b949e; margin-bottom: 20px; }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 12px;
            margin: 16px 0;
        }
        
        .stat-card {
            background: #21262d;
            border-radius: 8px;
            padding: 16px;
            text-align: center;
            border: 1px solid #30363d;
        }
        
        .stat-value { font-size: 1.8em; font-weight: bold; color: #58a6ff; }
        .stat-label { font-size: 0.85em; color: #8b949e; margin-top: 4px; }
        .stat-card.highlight { border-color: #f0883e; }
        .stat-card.highlight .stat-value { color: #f0883e; }
        
        .dist-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            margin: 16px 0;
        }
        
        .dist-item {
            padding: 16px;
            border-radius: 8px;
            text-align: center;
        }
        
        .dist-item.green { background: rgba(46, 160, 67, 0.2); border: 1px solid #2ea043; }
        .dist-item.yellow { background: rgba(187, 128, 9, 0.2); border: 1px solid #bb8009; }
        .dist-item.orange { background: rgba(219, 109, 40, 0.2); border: 1px solid #db6d28; }
        .dist-item.red { background: rgba(248, 81, 73, 0.2); border: 1px solid #f85149; }
        
        .dist-count { font-size: 2em; font-weight: bold; }
        .dist-label { font-size: 0.9em; margin-top: 4px; }
        
        .table-container {
            overflow-x: auto;
            margin: 12px 0;
            border-radius: 8px;
            border: 1px solid #30363d;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9em;
        }
        
        th, td {
            padding: 10px 12px;
            text-align: left;
            border-bottom: 1px solid #21262d;
        }
        
        th {
            background: #161b22;
            font-weight: 600;
            cursor: pointer;
            user-select: none;
        }
        
        th:hover { background: #21262d; }
        
        tr:hover { background: #161b22; }
        
        .status-diversifiant { color: #2ea043; font-weight: bold; }
        .status-modere { color: #bb8009; font-weight: bold; }
        .status-correle { color: #db6d28; font-weight: bold; }
        .status-tres-correle { color: #f85149; font-weight: bold; }
        
        .controls {
            display: flex;
            gap: 16px;
            flex-wrap: wrap;
            align-items: center;
            margin: 16px 0;
            padding: 12px;
            background: #161b22;
            border-radius: 8px;
        }
        
        .control-group { display: flex; align-items: center; gap: 8px; }
        .control-group label { font-size: 0.9em; color: #8b949e; }
        
        input[type="text"], select {
            padding: 8px 12px;
            border: 1px solid #30363d;
            border-radius: 6px;
            background: #0d1117;
            color: #c9d1d9;
            font-size: 14px;
        }
        
        button {
            padding: 8px 16px;
            border: 1px solid #238636;
            border-radius: 6px;
            background: #238636;
            color: white;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.2s;
        }
        
        button:hover { background: #2ea043; }
        
        .heatmap-container {
            margin: 20px 0;
            padding: 16px;
            background: #161b22;
            border-radius: 8px;
            overflow-x: auto;
        }
        
        canvas { max-width: 100%; }
        
        .legend {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            margin-top: 12px;
            font-size: 0.85em;
        }
        
        .legend-gradient {
            width: 200px;
            height: 16px;
            border-radius: 4px;
        }
        
        .legend-corr {
            background: linear-gradient(to right, #d32f2f, #ffeb3b, #4caf50);
        }
        
        .legend-delta {
            background: linear-gradient(to right, #2196f3, #ffffff, #f44336);
        }
        
        .tooltip {
            position: fixed;
            display: none;
            background: #21262d;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 10px 14px;
            font-size: 12px;
            z-index: 1000;
            pointer-events: none;
            max-width: 300px;
        }
        
        .methodology {
            background: #161b22;
            border-radius: 8px;
            padding: 24px;
            border: 1px solid #30363d;
        }
        
        .methodology h3 { color: #58a6ff; margin-top: 20px; }
        .methodology p { margin: 12px 0; }
        .methodology ul { margin: 12px 0 12px 24px; }
        .methodology li { margin: 6px 0; }
        
        .formula {
            background: #0d1117;
            padding: 12px 16px;
            border-radius: 6px;
            font-family: monospace;
            margin: 12px 0;
            overflow-x: auto;
        }
        
        .note {
            background: rgba(88, 166, 255, 0.1);
            border-left: 3px solid #58a6ff;
            padding: 12px 16px;
            margin: 16px 0;
            border-radius: 0 6px 6px 0;
        }
        
        @media (max-width: 768px) {
            .nav { justify-content: center; }
            .tab { padding: 6px 12px; font-size: 12px; }
            .stats-grid { grid-template-columns: repeat(2, 1fr); }
            .dist-grid { grid-template-columns: repeat(2, 1fr); }
            h1 { font-size: 1.4em; }
            .controls { flex-direction: column; align-items: stretch; }
            .control-group { justify-content: space-between; }
        }
    </style>'''
    
    def _generate_nav(self) -> str:
        """Génère la barre de navigation."""
        return '''<nav class="nav">
        <button class="tab active" onclick="showTab('summary')">📊 Résumé</button>
        <button class="tab" onclick="showTab('scores')">🎯 Scores</button>
        <button class="tab" onclick="showTab('longterm')">📈 Long Terme</button>
        <button class="tab" onclick="showTab('recent')">📉 Court Terme</button>
        <button class="tab" onclick="showTab('comparison')">⚖️ Comparaison</button>
        <button class="tab" onclick="showTab('methodology')">📖 Méthodologie</button>
    </nav>'''
    
    def _generate_summary_tab(
        self,
        n_total: int,
        n_diversifiant: int,
        n_modere: int,
        n_correle: int,
        n_tres_correle: int,
        stats_lt: Dict,
        stats_ct: Dict,
        config: Dict
    ) -> str:
        """Génère l'onglet Résumé."""
        return f'''<div id="summary" class="tab-content active">
        <div class="container">
            <h1>📊 Analyse de Corrélation - Résumé</h1>
            <p class="subtitle">Méthode Kevin Davey - Long Terme vs Court Terme</p>
            
            <h2>Distribution des stratégies</h2>
            <div class="dist-grid" id="distributionGrid">
                <div class="dist-item green">
                    <div class="dist-count">{n_diversifiant}</div>
                    <div class="dist-label">🟢 Diversifiant</div>
                </div>
                <div class="dist-item yellow">
                    <div class="dist-count">{n_modere}</div>
                    <div class="dist-label">🟡 Modéré</div>
                </div>
                <div class="dist-item orange">
                    <div class="dist-count">{n_correle}</div>
                    <div class="dist-label">🟠 Corrélé</div>
                </div>
                <div class="dist-item red">
                    <div class="dist-count">{n_tres_correle}</div>
                    <div class="dist-label">🔴 Très corrélé</div>
                </div>
            </div>
            
            <h2>🔴 Candidats à l'élimination</h2>
            <p class="subtitle">Stratégies avec Score ≥ 10 (forte redondance)</p>
            <div class="table-container">
                <table id="eliminationTable">
                    <thead>
                        <tr>
                            <th>Stratégie</th>
                            <th>Score</th>
                            <th>N Corr LT</th>
                            <th>N Corr CT</th>
                            <th>Max Corr</th>
                            <th>Plus corrélée avec</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
            
            <h2>Configuration de l'analyse</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{config.get('start_year_longterm', 2012)}</div>
                    <div class="stat-label">Année début (LT)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{config.get('recent_months', 12)} mois</div>
                    <div class="stat-label">Fenêtre Court Terme</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{config.get('weight_longterm', 0.5)}/{config.get('weight_recent', 0.5)}</div>
                    <div class="stat-label">Poids LT/CT</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{config.get('correlation_threshold', 0.70)}</div>
                    <div class="stat-label">Seuil corrélation</div>
                </div>
            </div>
        </div>
    </div>'''
    
    def _generate_scores_tab(self) -> str:
        """Génère l'onglet Scores."""
        return '''<div id="scores" class="tab-content">
        <div class="container">
            <h1>🎯 Scores de Corrélation par Stratégie</h1>
            <p class="subtitle">Méthode Kevin Davey : somme pondérée des stratégies corrélées</p>
            
            <div class="controls">
                <div class="control-group">
                    <label>🔍 Recherche:</label>
                    <input type="text" id="searchInput" placeholder="Nom de stratégie..." onkeyup="filterScoresTable()">
                </div>
                <div class="control-group">
                    <label>Statut:</label>
                    <select id="statusFilter" onchange="filterScoresTable()">
                        <option value="">Tous</option>
                        <option value="Très corrélé">🔴 Très corrélé</option>
                        <option value="Corrélé">🟠 Corrélé</option>
                        <option value="Modéré">🟡 Modéré</option>
                        <option value="Diversifiant">🟢 Diversifiant</option>
                    </select>
                </div>
                <button onclick="exportScoresCSV()">📥 Export CSV</button>
            </div>
            
            <div class="table-container">
                <table id="scoresTable">
                    <thead>
                        <tr>
                            <th onclick="sortScoresTable(0)">Stratégie ↕</th>
                            <th onclick="sortScoresTable(1)">Score ↕</th>
                            <th onclick="sortScoresTable(2)">N Corr LT ↕</th>
                            <th onclick="sortScoresTable(3)">N Corr CT ↕</th>
                            <th onclick="sortScoresTable(4)">Avg LT ↕</th>
                            <th onclick="sortScoresTable(5)">Avg CT ↕</th>
                            <th onclick="sortScoresTable(6)">Delta ↕</th>
                            <th onclick="sortScoresTable(7)">Max LT ↕</th>
                            <th onclick="sortScoresTable(8)">Max CT ↕</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>
    </div>'''
    
    def _generate_matrix_tab(
        self,
        tab_id: str,
        title: str,
        stats: Dict,
        config: Dict
    ) -> str:
        """Génère un onglet de matrice de corrélation."""
        icon = "📈" if tab_id == "longterm" else "📉"
        canvas_id = "heatmapLT" if tab_id == "longterm" else "heatmapCT"
        most_table = "mostCorrLT" if tab_id == "longterm" else "mostCorrCT"
        least_table = "leastCorrLT" if tab_id == "longterm" else "leastCorrCT"
        
        period_desc = f"Depuis {config.get('start_year_longterm', 2012)}" if tab_id == "longterm" else f"{config.get('recent_months', 12)} derniers mois"
        
        return f'''<div id="{tab_id}" class="tab-content">
        <div class="container">
            <h1>{icon} Matrice de Corrélation - {title}</h1>
            <p class="subtitle">{period_desc} - {stats.get('nb_strategies', 0)} stratégies - {stats.get('nb_pairs_valid', 0):,} paires valides</p>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{stats.get('corr_mean', 0):.3f}</div>
                    <div class="stat-label">Moyenne</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{stats.get('corr_median', 0):.3f}</div>
                    <div class="stat-label">Médiane</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{stats.get('corr_min', 0):.3f}</div>
                    <div class="stat-label">Minimum</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{stats.get('corr_max', 0):.3f}</div>
                    <div class="stat-label">Maximum</div>
                </div>
            </div>
            
            <div class="heatmap-container">
                <canvas id="{canvas_id}"></canvas>
                <div class="legend">
                    <span>-1</span>
                    <div class="legend-gradient legend-corr"></div>
                    <span>+1</span>
                </div>
            </div>
            
            <h3>🔝 Paires les plus corrélées</h3>
            <div class="table-container">
                <table id="{most_table}">
                    <thead><tr><th>Stratégie 1</th><th>Stratégie 2</th><th>Corrélation</th></tr></thead>
                    <tbody></tbody>
                </table>
            </div>
            
            <h3>🔻 Paires les moins corrélées (diversification)</h3>
            <div class="table-container">
                <table id="{least_table}">
                    <thead><tr><th>Stratégie 1</th><th>Stratégie 2</th><th>Corrélation</th></tr></thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>
    </div>'''
    
    def _generate_comparison_tab(self, stats_lt: Dict, stats_ct: Dict) -> str:
        """Génère l'onglet Comparaison."""
        return f'''<div id="comparison" class="tab-content">
        <div class="container">
            <h1>⚖️ Comparaison Long Terme vs Court Terme</h1>
            <p class="subtitle">Détection des changements de régime de corrélation</p>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{stats_lt.get('corr_mean', 0):.3f}</div>
                    <div class="stat-label">Moyenne LT</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{stats_ct.get('corr_mean', 0):.3f}</div>
                    <div class="stat-label">Moyenne CT</div>
                </div>
                <div class="stat-card highlight">
                    <div class="stat-value" id="deltaMean"></div>
                    <div class="stat-label">Delta moyen (CT-LT)</div>
                </div>
            </div>
            
            <h2>Matrice des Changements (CT - LT)</h2>
            <p class="subtitle">Rouge = corrélation augmentée | Bleu = corrélation diminuée</p>
            
            <div class="heatmap-container">
                <canvas id="heatmapDelta"></canvas>
                <div class="legend">
                    <span>-0.5 (diminué)</span>
                    <div class="legend-gradient legend-delta"></div>
                    <span>+0.5 (augmenté)</span>
                </div>
            </div>
            
            <h2>🔄 Plus grands changements de corrélation</h2>
            <div class="table-container">
                <table id="biggestChanges">
                    <thead><tr><th>Stratégie 1</th><th>Stratégie 2</th><th>Delta</th><th>Interprétation</th></tr></thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>
    </div>'''
    
    def _generate_methodology_tab(self, config: Dict) -> str:
        """Génère l'onglet Méthodologie."""
        return f'''<div id="methodology" class="tab-content">
        <div class="container">
            <h1>📖 Méthodologie</h1>
            <p class="subtitle">Documentation complète de l'analyse de corrélation</p>
            
            <div class="methodology">
                <h3>1. Objectif de l'analyse</h3>
                <p>L'analyse de corrélation vise à identifier les stratégies de trading qui présentent des comportements similaires (corrélées) ou opposés (anti-corrélées). Une forte corrélation entre stratégies indique une <strong>redondance</strong> qui peut amplifier les risques du portefeuille.</p>
                
                <h3>2. Coefficient de corrélation de Pearson</h3>
                <p>Le coefficient de corrélation de Pearson mesure la relation linéaire entre deux variables :</p>
                <div class="formula">
                    r = Σ[(xᵢ - x̄)(yᵢ - ȳ)] / √[Σ(xᵢ - x̄)² × Σ(yᵢ - ȳ)²]
                </div>
                <p>Où xᵢ, yᵢ sont les profits journaliers des stratégies X et Y.</p>
                
                <h3>3. Interprétation des valeurs</h3>
                <ul>
                    <li><strong>r = +1</strong> : Corrélation parfaite positive (stratégies identiques)</li>
                    <li><strong>r > +0.7</strong> : Forte corrélation positive → Redondance probable</li>
                    <li><strong>r ≈ 0</strong> : Pas de corrélation linéaire → Bonne diversification</li>
                    <li><strong>r < -0.7</strong> : Forte corrélation négative → Couverture potentielle</li>
                </ul>
                
                <h3>4. Score de corrélation (méthode Kevin Davey)</h3>
                <div class="formula">
                    Score_Davey = N_corr_LT × W_LT + N_corr_CT × W_CT
                </div>
                <p>Où :</p>
                <ul>
                    <li><strong>N_corr_LT</strong> : Nombre de stratégies avec |corrélation| > {config.get('correlation_threshold', 0.70)} (Long Terme)</li>
                    <li><strong>N_corr_CT</strong> : Nombre de stratégies avec |corrélation| > seuil (Court Terme)</li>
                    <li><strong>W_LT = {config.get('weight_longterm', 0.5)}</strong> : Poids Long Terme</li>
                    <li><strong>W_CT = {config.get('weight_recent', 0.5)}</strong> : Poids Court Terme</li>
                </ul>
                
                <h3>5. Classification des stratégies</h3>
                <ul>
                    <li><strong>🟢 Diversifiant</strong> (Score &lt; 2) : Stratégie peu corrélée, à conserver</li>
                    <li><strong>🟡 Modéré</strong> (2 ≤ Score &lt; 5) : Quelques corrélations, à surveiller</li>
                    <li><strong>🟠 Corrélé</strong> (5 ≤ Score &lt; 10) : Corrélations significatives, évaluer</li>
                    <li><strong>🔴 Très corrélé</strong> (Score ≥ 10) : Forte redondance, candidat à l'élimination</li>
                </ul>
                
                <h3>6. Recommandations</h3>
                <ul>
                    <li>Éliminer en priorité les stratégies 🔴 avec le score le plus élevé</li>
                    <li>Garder la stratégie avec le meilleur ratio rendement/risque dans chaque groupe corrélé</li>
                    <li>Surveiller les stratégies dont le Delta de corrélation > 0.2</li>
                    <li>Les corrélations négatives peuvent être conservées comme couverture</li>
                </ul>
                
                <div class="note">
                    <strong>Référence :</strong> Davey, K. (2014). <em>Building Winning Algorithmic Trading Systems</em>
                </div>
            </div>
        </div>
    </div>'''
    
    def _generate_javascript(self, data: Dict[str, Any]) -> str:
        """Génère le code JavaScript."""
        return f'''<script>
        // ===== DONNÉES =====
        const scoresData = {json.dumps(data['scores_list'], ensure_ascii=False)};
        const configData = {json.dumps(data['config'])};
        const statsLT = {json.dumps(data['stats_lt'])};
        const statsCT = {json.dumps(data['stats_ct'])};
        
        // Matrices
        const stratLT = {json.dumps(data['strat_lt'], ensure_ascii=False)};
        const shortLT = {json.dumps(data['short_lt'], ensure_ascii=False)};
        const dataLT = {json.dumps(data['data_lt'])};
        
        const stratCT = {json.dumps(data['strat_ct'], ensure_ascii=False)};
        const shortCT = {json.dumps(data['short_ct'], ensure_ascii=False)};
        const dataCT = {json.dumps(data['data_ct'])};
        
        const stratDelta = {json.dumps(data['strat_delta'], ensure_ascii=False)};
        const shortDelta = {json.dumps(data['short_delta'], ensure_ascii=False)};
        const dataDelta = {json.dumps(data['data_delta'])};
        
        // Paires
        const mostCorrLTData = {json.dumps(data['most_lt'], ensure_ascii=False)};
        const leastCorrLTData = {json.dumps(data['least_lt'], ensure_ascii=False)};
        const mostCorrCTData = {json.dumps(data['most_ct'], ensure_ascii=False)};
        const leastCorrCTData = {json.dumps(data['least_ct'], ensure_ascii=False)};
        const biggestChangesData = {json.dumps(data['changes_list'], ensure_ascii=False)};
        
        // ===== NAVIGATION =====
        function showTab(tabId) {{
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            document.querySelector(`[onclick="showTab('${{tabId}}')"]`).classList.add('active');
            document.getElementById(tabId).classList.add('active');
            
            if (tabId === 'longterm') renderHeatmap('heatmapLT', stratLT, shortLT, dataLT, 'corr');
            if (tabId === 'recent') renderHeatmap('heatmapCT', stratCT, shortCT, dataCT, 'corr');
            if (tabId === 'comparison') renderHeatmap('heatmapDelta', stratDelta, shortDelta, dataDelta, 'delta');
        }}
        
        // ===== HEATMAP =====
        function getColorCorr(value) {{
            if (isNaN(value) || value === null) return 'rgba(128,128,128,0.3)';
            let r, g, b;
            if (value < 0) {{
                const t = (value + 1);
                r = 211; g = Math.round(47 + t * 188); b = Math.round(47 + t * 12);
            }} else {{
                const t = value;
                r = Math.round(255 - t * 179); g = Math.round(235 - t * 60); b = Math.round(59 + t * 21);
            }}
            return `rgb(${{r}},${{g}},${{b}})`;
        }}
        
        function getColorDelta(value) {{
            if (isNaN(value) || value === null) return 'rgba(128,128,128,0.3)';
            const clamped = Math.max(-0.5, Math.min(0.5, value));
            const t = (clamped + 0.5);
            let r, g, b;
            if (t < 0.5) {{
                const s = t * 2;
                r = Math.round(33 + s * 222); g = Math.round(150 + s * 105); b = Math.round(243 + s * 12);
            }} else {{
                const s = (t - 0.5) * 2;
                r = 255; g = Math.round(255 - s * 111); b = Math.round(255 - s * 187);
            }}
            return `rgb(${{r}},${{g}},${{b}})`;
        }}
        
        function renderHeatmap(canvasId, strategies, shortNames, dataPoints, colorType) {{
            const canvas = document.getElementById(canvasId);
            if (!canvas) return;
            const ctx = canvas.getContext('2d');
            const tooltip = document.getElementById('tooltip');
            const n = shortNames.length;
            
            if (n === 0) {{
                canvas.width = 400; canvas.height = 100;
                ctx.fillStyle = '#90a4ae';
                ctx.font = '14px sans-serif';
                ctx.fillText('Aucune donnée disponible', 50, 50);
                return;
            }}
            
            const cellSize = Math.max(5, Math.min(16, 850 / n));
            const margin = {{ top: 10, right: 10, bottom: 150, left: 180 }};
            
            canvas.width = margin.left + n * cellSize + margin.right;
            canvas.height = margin.top + n * cellSize + margin.bottom;
            
            const matrix = {{}};
            dataPoints.forEach(p => {{
                if (!matrix[p.y]) matrix[p.y] = {{}};
                matrix[p.y][p.x] = p.v;
            }});
            
            const getColor = colorType === 'delta' ? getColorDelta : getColorCorr;
            
            for (let i = 0; i < n; i++) {{
                for (let j = 0; j < n; j++) {{
                    const val = matrix[i]?.[j];
                    ctx.fillStyle = getColor(val);
                    ctx.fillRect(margin.left + j * cellSize, margin.top + i * cellSize, cellSize - 1, cellSize - 1);
                }}
            }}
            
            ctx.fillStyle = '#90a4ae';
            ctx.font = `${{Math.max(6, Math.min(9, cellSize - 1))}}px sans-serif`;
            ctx.textAlign = 'right';
            ctx.textBaseline = 'middle';
            if (n <= 70) {{
                for (let i = 0; i < n; i++) {{
                    ctx.fillText(shortNames[i].substring(0, 20), margin.left - 5, margin.top + i * cellSize + cellSize / 2);
                }}
            }}
            
            ctx.textAlign = 'left';
            if (n <= 70) {{
                for (let j = 0; j < n; j++) {{
                    ctx.save();
                    ctx.translate(margin.left + j * cellSize + cellSize / 2, margin.top + n * cellSize + 5);
                    ctx.rotate(Math.PI / 4);
                    ctx.fillText(shortNames[j].substring(0, 20), 0, 0);
                    ctx.restore();
                }}
            }}
            
            canvas.onmousemove = function(e) {{
                const rect = canvas.getBoundingClientRect();
                const x = e.clientX - rect.left - margin.left;
                const y = e.clientY - rect.top - margin.top;
                const col = Math.floor(x / cellSize);
                const row = Math.floor(y / cellSize);
                
                if (col >= 0 && col < n && row >= 0 && row < n) {{
                    const val = matrix[row]?.[col];
                    if (val !== undefined) {{
                        tooltip.style.display = 'block';
                        tooltip.style.left = (e.clientX + 15) + 'px';
                        tooltip.style.top = (e.clientY + 15) + 'px';
                        const label = colorType === 'delta' ? 'Delta' : 'Corrélation';
                        tooltip.innerHTML = `<strong>${{strategies[row]}}</strong><br>vs<br><strong>${{strategies[col]}}</strong><br><br>${{label}}: <strong>${{val.toFixed(3)}}</strong>`;
                    }} else {{
                        tooltip.style.display = 'none';
                    }}
                }} else {{
                    tooltip.style.display = 'none';
                }}
            }};
            canvas.onmouseleave = () => tooltip.style.display = 'none';
        }}
        
        // ===== TABLES =====
        function populateScoresTable() {{
            const tbody = document.querySelector('#scoresTable tbody');
            tbody.innerHTML = '';
            scoresData.forEach(row => {{
                const tr = document.createElement('tr');
                const statusClass = 'status-' + row.Status.toLowerCase().replace(/ /g, '-').replace(/é/g, 'e');
                tr.innerHTML = `
                    <td>${{row.Strategy}}</td>
                    <td><strong>${{row.Score_Davey}}</strong></td>
                    <td>${{row.N_Corr_LT}}</td>
                    <td>${{row.N_Corr_CT}}</td>
                    <td>${{row.Avg_Corr_LT.toFixed(3)}}</td>
                    <td>${{row.Avg_Corr_CT.toFixed(3)}}</td>
                    <td>${{row.Delta_Corr >= 0 ? '+' : ''}}${{row.Delta_Corr.toFixed(3)}}</td>
                    <td>${{row.Max_Corr_LT.toFixed(3)}}</td>
                    <td>${{row.Max_Corr_CT.toFixed(3)}}</td>
                    <td class="${{statusClass}}">${{row.Status_Emoji}} ${{row.Status}}</td>
                `;
                tbody.appendChild(tr);
            }});
        }}
        
        function populateEliminationTable() {{
            const tbody = document.querySelector('#eliminationTable tbody');
            tbody.innerHTML = '';
            const candidates = scoresData.filter(s => s.Score_Davey >= 10);
            if (candidates.length === 0) {{
                tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:#66bb6a;">✓ Aucune stratégie à éliminer</td></tr>';
                return;
            }}
            candidates.forEach(row => {{
                const tr = document.createElement('tr');
                const maxWith = row.Max_Corr_CT > row.Max_Corr_LT ? row.Max_Corr_CT_With : row.Max_Corr_LT_With;
                const maxVal = Math.max(row.Max_Corr_LT, row.Max_Corr_CT);
                tr.innerHTML = `
                    <td>${{row.Strategy}}</td>
                    <td><strong style="color:#ef5350;">${{row.Score_Davey}}</strong></td>
                    <td>${{row.N_Corr_LT}}</td>
                    <td>${{row.N_Corr_CT}}</td>
                    <td>${{maxVal.toFixed(3)}}</td>
                    <td style="font-size:0.85em;">${{maxWith || 'N/A'}}</td>
                `;
                tbody.appendChild(tr);
            }});
        }}
        
        function populatePairsTable(tableId, data) {{
            const tbody = document.querySelector(`#${{tableId}} tbody`);
            if (!tbody || !data) return;
            tbody.innerHTML = '';
            data.slice(0, 15).forEach(row => {{
                const tr = document.createElement('tr');
                const corr = row.Correlation !== undefined ? row.Correlation : row.Delta;
                const colorClass = corr > 0.7 ? 'color:#ef5350;' : corr < -0.3 ? 'color:#42a5f5;' : '';
                tr.innerHTML = `
                    <td style="font-size:0.85em;">${{row.Strategy_1}}</td>
                    <td style="font-size:0.85em;">${{row.Strategy_2}}</td>
                    <td style="${{colorClass}}font-weight:bold;">${{corr.toFixed(3)}}</td>
                `;
                if (row.Delta !== undefined) {{
                    const interp = row.Delta > 0.2 ? '⚠️ Corrélation augmentée' : row.Delta < -0.2 ? '✅ Décorrélation' : '→ Stable';
                    tr.innerHTML += `<td>${{interp}}</td>`;
                }}
                tbody.appendChild(tr);
            }});
        }}
        
        // ===== FILTERING & SORTING =====
        let sortColumn = 1;
        let sortAsc = false;
        
        function filterScoresTable() {{
            const search = document.getElementById('searchInput').value.toLowerCase();
            const status = document.getElementById('statusFilter').value;
            const rows = document.querySelectorAll('#scoresTable tbody tr');
            rows.forEach(row => {{
                const name = row.cells[0].textContent.toLowerCase();
                const rowStatus = row.cells[9].textContent;
                const matchSearch = name.includes(search);
                const matchStatus = !status || rowStatus.includes(status);
                row.style.display = matchSearch && matchStatus ? '' : 'none';
            }});
        }}
        
        function sortScoresTable(col) {{
            if (sortColumn === col) sortAsc = !sortAsc;
            else {{ sortColumn = col; sortAsc = true; }}
            
            const tbody = document.querySelector('#scoresTable tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            
            rows.sort((a, b) => {{
                let va = a.cells[col].textContent;
                let vb = b.cells[col].textContent;
                if (col > 0 && col < 9) {{ va = parseFloat(va) || 0; vb = parseFloat(vb) || 0; }}
                if (va < vb) return sortAsc ? -1 : 1;
                if (va > vb) return sortAsc ? 1 : -1;
                return 0;
            }});
            
            rows.forEach(row => tbody.appendChild(row));
        }}
        
        function exportScoresCSV() {{
            const headers = ['Strategy','Score_Davey','N_Corr_LT','N_Corr_CT','Avg_Corr_LT','Avg_Corr_CT','Delta_Corr','Max_Corr_LT','Max_Corr_CT','Status'];
            let csv = headers.join(';') + '\\n';
            scoresData.forEach(row => {{
                csv += headers.map(h => row[h]).join(';') + '\\n';
            }});
            const blob = new Blob([csv], {{type: 'text/csv;charset=utf-8;'}});
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = 'correlation_scores.csv';
            link.click();
        }}
        
        // ===== INITIALIZATION =====
        document.addEventListener('DOMContentLoaded', function() {{
            populateScoresTable();
            populateEliminationTable();
            populatePairsTable('mostCorrLT', mostCorrLTData);
            populatePairsTable('leastCorrLT', leastCorrLTData);
            populatePairsTable('mostCorrCT', mostCorrCTData);
            populatePairsTable('leastCorrCT', leastCorrCTData);
            populatePairsTable('biggestChanges', biggestChangesData);
            
            const deltaMean = (statsCT.corr_mean - statsLT.corr_mean).toFixed(3);
            document.getElementById('deltaMean').textContent = (deltaMean >= 0 ? '+' : '') + deltaMean;
        }});
    </script>'''
