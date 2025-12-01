#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch Visualizer - Rapport HTML interactif multi-stratégies

Génère un dashboard HTML avec:
- Vue d'ensemble des stratégies
- Filtres par symbole, statut, métriques
- Graphiques interactifs
- Tableau triable

Auteur: Yann
Date: 2025-11-26
"""

from pathlib import Path
from typing import List, Dict
from datetime import datetime
import json


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Monte Carlo Batch Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-primary: #0f0f1a;
            --bg-secondary: #1a1a2e;
            --bg-card: #16213e;
            --bg-hover: #1f3a5f;
            --text-primary: #eaeaea;
            --text-secondary: #a0a0a0;
            --accent-green: #00d4aa;
            --accent-red: #ff6b6b;
            --accent-blue: #4ecdc4;
            --accent-yellow: #ffe66d;
            --accent-orange: #ffa502;
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            padding: 20px;
        }}
        
        .container {{ max-width: 1600px; margin: 0 auto; }}
        
        header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 25px;
            background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-card) 100%);
            border-radius: 15px;
            border: 1px solid rgba(78, 205, 196, 0.2);
        }}
        
        h1 {{
            color: var(--accent-blue);
            font-size: 2.2em;
            margin-bottom: 10px;
        }}
        
        .subtitle {{ color: var(--text-secondary); font-size: 1.1em; }}
        
        /* Stats Cards */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }}
        
        .stat-card {{
            background: var(--bg-card);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.05);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        
        .stat-value {{
            font-size: 2.2em;
            font-weight: bold;
            color: var(--accent-blue);
        }}
        
        .stat-value.ok {{ color: var(--accent-green); }}
        .stat-value.warning {{ color: var(--accent-yellow); }}
        .stat-value.danger {{ color: var(--accent-red); }}
        
        .stat-label {{
            font-size: 0.9em;
            color: var(--text-secondary);
            margin-top: 5px;
        }}
        
        /* Filters */
        .filters {{
            background: var(--bg-card);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 25px;
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            align-items: center;
        }}
        
        .filter-group {{
            display: flex;
            flex-direction: column;
            gap: 5px;
        }}
        
        .filter-group label {{
            font-size: 0.85em;
            color: var(--text-secondary);
        }}
        
        .filter-group select, .filter-group input {{
            padding: 8px 12px;
            border-radius: 6px;
            border: 1px solid rgba(255,255,255,0.1);
            background: var(--bg-secondary);
            color: var(--text-primary);
            font-size: 0.95em;
            min-width: 150px;
        }}
        
        .filter-group select:focus, .filter-group input:focus {{
            outline: none;
            border-color: var(--accent-blue);
        }}
        
        .btn {{
            padding: 10px 20px;
            border-radius: 6px;
            border: none;
            cursor: pointer;
            font-size: 0.95em;
            transition: all 0.2s;
        }}
        
        .btn-primary {{
            background: var(--accent-blue);
            color: var(--bg-primary);
        }}
        
        .btn-primary:hover {{ background: var(--accent-green); }}
        
        .btn-secondary {{
            background: var(--bg-secondary);
            color: var(--text-primary);
            border: 1px solid rgba(255,255,255,0.1);
        }}
        
        /* Charts */
        .charts-row {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }}
        
        .chart-card {{
            background: var(--bg-card);
            border-radius: 12px;
            padding: 20px;
        }}
        
        .chart-card h3 {{
            color: var(--accent-blue);
            margin-bottom: 15px;
            font-size: 1.1em;
        }}
        
        .chart-container {{
            position: relative;
            height: 300px;
        }}
        
        /* Table */
        .table-container {{
            background: var(--bg-card);
            border-radius: 12px;
            padding: 20px;
            overflow-x: auto;
        }}
        
        .table-container h3 {{
            color: var(--accent-blue);
            margin-bottom: 15px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9em;
        }}
        
        th, td {{
            padding: 12px 10px;
            text-align: right;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }}
        
        th {{
            background: var(--bg-secondary);
            color: var(--accent-blue);
            font-weight: 600;
            position: sticky;
            top: 0;
            cursor: pointer;
            user-select: none;
        }}
        
        th:hover {{ background: var(--bg-hover); }}
        
        th:first-child, td:first-child {{ text-align: left; }}
        
        tr:hover {{ background: rgba(78, 205, 196, 0.05); }}
        
        .status-badge {{
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 500;
        }}
        
        .status-ok {{ background: rgba(0, 212, 170, 0.2); color: var(--accent-green); }}
        .status-warning {{ background: rgba(255, 230, 109, 0.2); color: var(--accent-yellow); }}
        .status-danger {{ background: rgba(255, 107, 107, 0.2); color: var(--accent-red); }}
        
        .highlight {{ background: rgba(78, 205, 196, 0.1); }}
        
        /* Strategy links */
        .strategy-link {{
            color: var(--accent-blue);
            text-decoration: none;
            font-weight: 500;
            transition: all 0.2s;
        }}
        
        .strategy-link:hover {{
            color: var(--accent-green);
            text-decoration: underline;
        }}
        
        /* Footer */
        footer {{
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            color: var(--text-secondary);
            font-size: 0.9em;
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            .filters {{ flex-direction: column; }}
            .charts-row {{ grid-template-columns: 1fr; }}
        }}
        
        /* Sort indicators */
        th .sort-indicator {{ margin-left: 5px; opacity: 0.5; }}
        th.sorted-asc .sort-indicator::after {{ content: '▲'; }}
        th.sorted-desc .sort-indicator::after {{ content: '▼'; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎲 Monte Carlo Batch Report</h1>
            <p class="subtitle">Analyse de risque multi-stratégies</p>
            <p class="subtitle">Généré le {generation_date}</p>
        </header>
        
        <!-- Stats Overview -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{total_strategies}</div>
                <div class="stat-label">Stratégies analysées</div>
            </div>
            <div class="stat-card">
                <div class="stat-value ok">{ok_count}</div>
                <div class="stat-label">✓ Critères OK</div>
            </div>
            <div class="stat-card">
                <div class="stat-value warning">{warning_count}</div>
                <div class="stat-label">⚠ Warning</div>
            </div>
            <div class="stat-card">
                <div class="stat-value danger">{high_risk_count}</div>
                <div class="stat-label">✗ High Risk</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{total_trades}</div>
                <div class="stat-label">Total Trades</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${total_pnl}</div>
                <div class="stat-label">P&L Total (Net)</div>
            </div>
        </div>
        
        <!-- Filters -->
        <div class="filters">
            <div class="filter-group">
                <label>Symbole</label>
                <select id="filter-symbol">
                    <option value="">Tous</option>
                    {symbol_options}
                </select>
            </div>
            <div class="filter-group">
                <label>Statut</label>
                <select id="filter-status">
                    <option value="">Tous</option>
                    <option value="OK">✓ OK</option>
                    <option value="WARNING">⚠ Warning</option>
                    <option value="HIGH_RISK">✗ High Risk</option>
                </select>
            </div>
            <div class="filter-group">
                <label>Min Trades</label>
                <input type="number" id="filter-min-trades" value="20" min="0">
            </div>
            <div class="filter-group">
                <label>Min Return/DD</label>
                <input type="number" id="filter-min-ratio" value="0" min="0" step="0.1">
            </div>
            <button class="btn btn-primary" onclick="applyFilters()">Appliquer</button>
            <button class="btn btn-secondary" onclick="resetFilters()">Reset</button>
        </div>
        
        <!-- Charts -->
        <div class="charts-row">
            <div class="chart-card">
                <h3>📊 Distribution par Statut</h3>
                <div class="chart-container">
                    <canvas id="statusChart"></canvas>
                </div>
            </div>
            <div class="chart-card">
                <h3>📈 Return/DD vs Risque de Ruine</h3>
                <div class="chart-container">
                    <canvas id="scatterChart"></canvas>
                </div>
            </div>
        </div>
        
        <div class="charts-row">
            <div class="chart-card">
                <h3>💰 Top 10 - P&L Total</h3>
                <div class="chart-container">
                    <canvas id="topPnlChart"></canvas>
                </div>
            </div>
            <div class="chart-card">
                <h3>🏆 Top 10 - Return/DD Ratio</h3>
                <div class="chart-container">
                    <canvas id="topRatioChart"></canvas>
                </div>
            </div>
        </div>
        
        <!-- Table -->
        <div class="table-container">
            <h3>📋 Détail des stratégies (<span id="visible-count">{total_strategies}</span> affichées)</h3>
            <table id="strategies-table">
                <thead>
                    <tr>
                        <th data-sort="strategy" class="sorted-desc">Stratégie <span class="sort-indicator"></span></th>
                        <th data-sort="symbol">Symbol <span class="sort-indicator"></span></th>
                        <th data-sort="status">Statut <span class="sort-indicator"></span></th>
                        <th data-sort="capital">Capital Reco <span class="sort-indicator"></span></th>
                        <th data-sort="trades">Trades <span class="sort-indicator"></span></th>
                        <th data-sort="pnl">P&L Net <span class="sort-indicator"></span></th>
                        <th data-sort="winrate">Win % <span class="sort-indicator"></span></th>
                        <th data-sort="pf">PF <span class="sort-indicator"></span></th>
                        <th data-sort="ruin">Ruine % <span class="sort-indicator"></span></th>
                        <th data-sort="ratio">Ret/DD <span class="sort-indicator"></span></th>
                        <th data-sort="prob">Prob>0 <span class="sort-indicator"></span></th>
                    </tr>
                </thead>
                <tbody id="table-body">
                    {table_rows}
                </tbody>
            </table>
        </div>
        
        <footer>
            <p>Monte Carlo Simulation - Méthodologie Kevin Davey</p>
            <p>Critères: Risque Ruine ≤ 10% | Return/DD ≥ 2 | Prob > 0 ≥ 80%</p>
            <p>{config_info}</p>
        </footer>
    </div>
    
    <script>
        // Data
        const strategiesData = {strategies_json};
        
        // Chart.js defaults
        Chart.defaults.color = '#a0a0a0';
        Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.1)';
        
        // Status Pie Chart
        new Chart(document.getElementById('statusChart'), {{
            type: 'doughnut',
            data: {{
                labels: ['OK', 'Warning', 'High Risk'],
                datasets: [{{
                    data: [{ok_count}, {warning_count}, {high_risk_count}],
                    backgroundColor: ['#00d4aa', '#ffe66d', '#ff6b6b'],
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ position: 'bottom' }}
                }}
            }}
        }});
        
        // Scatter Chart - Return/DD vs Ruin
        const scatterData = strategiesData.map(s => ({{
            x: s.ruin_pct,
            y: s.return_dd_ratio,
            label: s.strategy_name
        }}));
        
        new Chart(document.getElementById('scatterChart'), {{
            type: 'scatter',
            data: {{
                datasets: [{{
                    label: 'Stratégies',
                    data: scatterData,
                    backgroundColor: scatterData.map(d => 
                        d.x <= 10 && d.y >= 2 ? '#00d4aa' : 
                        d.x <= 10 ? '#ffe66d' : '#ff6b6b'
                    ),
                    pointRadius: 6,
                    pointHoverRadius: 8
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{
                        callbacks: {{
                            label: ctx => `${{ctx.raw.label}}: Ruine=${{ctx.raw.x.toFixed(1)}}%, Ret/DD=${{ctx.raw.y.toFixed(2)}}`
                        }}
                    }}
                }},
                scales: {{
                    x: {{
                        title: {{ display: true, text: 'Risque de Ruine (%)' }},
                        min: 0
                    }},
                    y: {{
                        title: {{ display: true, text: 'Return/DD Ratio' }},
                        min: 0
                    }}
                }}
            }}
        }});
        
        // Top PnL Chart
        const topPnl = [...strategiesData]
            .sort((a, b) => b.total_pnl - a.total_pnl)
            .slice(0, 10);
        
        new Chart(document.getElementById('topPnlChart'), {{
            type: 'bar',
            data: {{
                labels: topPnl.map(s => s.symbol + '_' + s.strategy_name.substring(0, 15)),
                datasets: [{{
                    data: topPnl.map(s => s.total_pnl),
                    backgroundColor: topPnl.map(s => s.status === 'OK' ? '#00d4aa' : s.status === 'WARNING' ? '#ffe66d' : '#ff6b6b'),
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    x: {{ title: {{ display: true, text: 'P&L Net ($)' }} }}
                }}
            }}
        }});
        
        // Top Ratio Chart
        const topRatio = [...strategiesData]
            .filter(s => s.return_dd_ratio < 100)
            .sort((a, b) => b.return_dd_ratio - a.return_dd_ratio)
            .slice(0, 10);
        
        new Chart(document.getElementById('topRatioChart'), {{
            type: 'bar',
            data: {{
                labels: topRatio.map(s => s.symbol + '_' + s.strategy_name.substring(0, 15)),
                datasets: [{{
                    data: topRatio.map(s => s.return_dd_ratio),
                    backgroundColor: topRatio.map(s => s.return_dd_ratio >= 2 ? '#00d4aa' : '#ffe66d'),
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    x: {{ title: {{ display: true, text: 'Return/DD Ratio' }} }}
                }}
            }}
        }});
        
        // Table sorting
        let currentSort = {{ column: 'strategy', direction: 'asc' }};
        
        document.querySelectorAll('th[data-sort]').forEach(th => {{
            th.addEventListener('click', () => {{
                const column = th.dataset.sort;
                const direction = currentSort.column === column && currentSort.direction === 'asc' ? 'desc' : 'asc';
                currentSort = {{ column, direction }};
                
                document.querySelectorAll('th').forEach(h => h.classList.remove('sorted-asc', 'sorted-desc'));
                th.classList.add(`sorted-${{direction}}`);
                
                sortTable(column, direction);
            }});
        }});
        
        function sortTable(column, direction) {{
            const tbody = document.getElementById('table-body');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            
            const getValue = (row, col) => {{
                const cells = row.querySelectorAll('td');
                const map = {{ strategy: 0, symbol: 1, status: 2, capital: 3, trades: 4, pnl: 5, winrate: 6, pf: 7, ruin: 8, ratio: 9, prob: 10 }};
                const text = cells[map[col]]?.textContent || '';
                if (col === 'status') return text;
                if (col === 'strategy' || col === 'symbol') return text.toLowerCase();
                return parseFloat(text.replace(/[^0-9.-]/g, '')) || 0;
            }};
            
            rows.sort((a, b) => {{
                const aVal = getValue(a, column);
                const bVal = getValue(b, column);
                if (typeof aVal === 'string') return direction === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
                return direction === 'asc' ? aVal - bVal : bVal - aVal;
            }});
            
            rows.forEach(row => tbody.appendChild(row));
        }}
        
        // Filters
        function applyFilters() {{
            const symbol = document.getElementById('filter-symbol').value;
            const status = document.getElementById('filter-status').value;
            const minTrades = parseInt(document.getElementById('filter-min-trades').value) || 0;
            const minRatio = parseFloat(document.getElementById('filter-min-ratio').value) || 0;
            
            const rows = document.querySelectorAll('#table-body tr');
            let visibleCount = 0;
            
            rows.forEach(row => {{
                const cells = row.querySelectorAll('td');
                const rowSymbol = cells[1].textContent;
                const rowStatus = cells[2].textContent.trim();
                const rowTrades = parseInt(cells[4].textContent) || 0;
                const rowRatio = parseFloat(cells[9].textContent) || 0;
                
                const show = (!symbol || rowSymbol === symbol) &&
                             (!status || rowStatus.includes(status.replace('_', ' '))) &&
                             rowTrades >= minTrades &&
                             rowRatio >= minRatio;
                
                row.style.display = show ? '' : 'none';
                if (show) visibleCount++;
            }});
            
            document.getElementById('visible-count').textContent = visibleCount;
        }}
        
        function resetFilters() {{
            document.getElementById('filter-symbol').value = '';
            document.getElementById('filter-status').value = '';
            document.getElementById('filter-min-trades').value = '20';
            document.getElementById('filter-min-ratio').value = '0';
            applyFilters();
        }}
    </script>
</body>
</html>
"""


def generate_batch_html_report(
    results: List,
    output_path: str,
    config: Dict
):
    """
    Génère un rapport HTML interactif multi-stratégies.
    
    Args:
        results: Liste des StrategyMCResult
        output_path: Chemin du fichier HTML de sortie
        config: Configuration utilisée pour la simulation
    """
    # Préparer les données pour JavaScript
    strategies_json_data = []
    for r in results:
        # Récupérer le niveau correspondant au capital recommandé
        rec_level = None
        if r.recommended_capital and r.levels_results:
            for lvl in r.levels_results:
                if lvl['start_equity'] == r.recommended_capital:
                    rec_level = lvl
                    break
        if rec_level is None and r.levels_results:
            rec_level = r.levels_results[-1]
        
        strategies_json_data.append({
            'strategy_name': r.strategy_name,
            'symbol': r.symbol,
            'status': r.status,
            'nb_trades': r.nb_trades,
            'total_pnl': round(r.total_pnl, 2),
            'win_rate': round(r.win_rate, 1),
            'profit_factor': min(round(r.profit_factor, 2), 99.99),
            'recommended_capital': r.recommended_capital or 0,
            'ruin_pct': round(rec_level['ruin_probability'] * 100, 2) if rec_level else 0,
            'return_dd_ratio': min(round(rec_level['return_dd_ratio'], 2), 99.99) if rec_level else 0,
            'prob_positive': round(rec_level['prob_positive'] * 100, 1) if rec_level else 0,
        })
    
    # Compteurs par statut
    status_counts = {'OK': 0, 'WARNING': 0, 'HIGH_RISK': 0}
    for r in results:
        status_counts[r.status] = status_counts.get(r.status, 0) + 1
    
    # Symboles uniques
    symbols = sorted(set(r.symbol for r in results))
    symbol_options = '\n'.join(f'<option value="{s}">{s}</option>' for s in symbols)
    
    # Générer les lignes du tableau avec liens
    table_rows = ""
    for r in results:
        rec_level = None
        if r.recommended_capital and r.levels_results:
            for lvl in r.levels_results:
                if lvl['start_equity'] == r.recommended_capital:
                    rec_level = lvl
                    break
        if rec_level is None and r.levels_results:
            rec_level = r.levels_results[-1]
        
        status_class = {
            'OK': 'status-ok',
            'WARNING': 'status-warning',
            'HIGH_RISK': 'status-danger'
        }.get(r.status, '')
        
        status_text = {
            'OK': '✓ OK',
            'WARNING': '⚠ Warning',
            'HIGH_RISK': '✗ High Risk'
        }.get(r.status, r.status)
        
        capital_str = f"${r.recommended_capital:,.0f}" if r.recommended_capital else "N/A"
        ruin_pct = rec_level['ruin_probability'] * 100 if rec_level else 0
        ratio = rec_level['return_dd_ratio'] if rec_level else 0
        prob = rec_level['prob_positive'] * 100 if rec_level else 0
        
        # Lien vers le rapport individuel
        individual_link = f"Individual/{r.symbol}_{r.strategy_name}_MC.html"
        
        table_rows += f"""
        <tr data-symbol="{r.symbol}" data-status="{r.status}">
            <td><a href="{individual_link}" class="strategy-link">{r.strategy_name}</a></td>
            <td>{r.symbol}</td>
            <td><span class="status-badge {status_class}">{status_text}</span></td>
            <td>{capital_str}</td>
            <td>{r.nb_trades:,}</td>
            <td>${r.total_pnl:,.0f}</td>
            <td>{r.win_rate:.1f}%</td>
            <td>{min(r.profit_factor, 99.99):.2f}</td>
            <td>{ruin_pct:.1f}%</td>
            <td>{min(ratio, 99.99):.2f}</td>
            <td>{prob:.1f}%</td>
        </tr>
        """
    
    # Config info
    config_info = (f"{config['nb_simulations']:,} simulations × {config['nb_capital_levels']} niveaux | "
                   f"Capital: ${config['capital_minimum']:,} → "
                   f"${config['capital_minimum'] + (config['nb_capital_levels']-1) * config['capital_increment']:,}")
    
    # Remplir le template
    html_content = HTML_TEMPLATE.format(
        generation_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        total_strategies=len(results),
        ok_count=status_counts.get('OK', 0),
        warning_count=status_counts.get('WARNING', 0),
        high_risk_count=status_counts.get('HIGH_RISK', 0),
        total_trades=f"{sum(r.nb_trades for r in results):,}",
        total_pnl=f"{sum(r.total_pnl for r in results):,.0f}",
        symbol_options=symbol_options,
        table_rows=table_rows,
        strategies_json=json.dumps(strategies_json_data),
        config_info=config_info,
    )
    
    # Écrire le fichier
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"📊 Rapport HTML généré: {Path(output_path).name}")