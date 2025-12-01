#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Templates HTML pour les rapports Monte Carlo V2.1
Nouveau SUMMARY_TEMPLATE avec dashboard interactif
"""

INDIVIDUAL_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Monte Carlo - {strategy_full_name}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-primary: #1a1a2e;
            --bg-secondary: #16213e;
            --bg-card: #0f3460;
            --text-primary: #eaeaea;
            --text-secondary: #a0a0a0;
            --accent-green: #00d4aa;
            --accent-red: #ff6b6b;
            --accent-blue: #4ecdc4;
            --accent-yellow: #ffe66d;
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            padding: 20px;
        }}
        
        .container {{ max-width: 1400px; margin: 0 auto; }}
        
        header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: var(--bg-secondary);
            border-radius: 10px;
        }}
        
        h1 {{ color: var(--accent-blue); font-size: 2em; margin-bottom: 10px; }}
        .subtitle {{ color: var(--text-secondary); font-size: 1.1em; }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .card {{
            background: var(--bg-card);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }}
        
        .card h2 {{
            color: var(--accent-blue);
            font-size: 1.2em;
            margin-bottom: 15px;
            border-bottom: 2px solid var(--accent-blue);
            padding-bottom: 10px;
        }}
        
        .stat-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }}
        
        .stat {{
            background: var(--bg-secondary);
            padding: 12px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 1.5em;
            font-weight: bold;
            color: var(--accent-green);
        }}
        
        .stat-value.warning {{ color: var(--accent-yellow); }}
        .stat-value.danger {{ color: var(--accent-red); }}
        
        .stat-label {{
            font-size: 0.85em;
            color: var(--text-secondary);
            margin-top: 5px;
        }}
        
        .recommendation {{
            background: var(--bg-secondary);
            border-left: 4px solid var(--accent-green);
            padding: 15px 20px;
            margin: 20px 0;
            border-radius: 0 8px 8px 0;
        }}
        
        .recommendation.warning {{ border-left-color: var(--accent-yellow); }}
        .recommendation.danger {{ border-left-color: var(--accent-red); }}
        
        .recommendation h3 {{ margin-bottom: 5px; }}
        .recommendation h3.ok {{ color: var(--accent-green); }}
        .recommendation h3.warning {{ color: var(--accent-yellow); }}
        .recommendation h3.danger {{ color: var(--accent-red); }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        
        th, td {{
            padding: 12px;
            text-align: right;
            border-bottom: 1px solid var(--bg-secondary);
        }}
        
        th {{
            background: var(--bg-secondary);
            color: var(--accent-blue);
            font-weight: 600;
        }}
        
        th:first-child, td:first-child {{ text-align: left; }}
        
        tr:hover {{ background: rgba(78, 205, 196, 0.1); }}
        tr.recommended {{ background: rgba(0, 212, 170, 0.15); }}
        tr.recommended td:first-child::after {{
            content: " ✓";
            color: var(--accent-green);
        }}
        
        .chart-container {{
            position: relative;
            height: 350px;
            margin-top: 20px;
        }}
        
        .chart-row {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}
        
        @media (max-width: 768px) {{
            .chart-row {{ grid-template-columns: 1fr; }}
        }}
        
        footer {{
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            color: var(--text-secondary);
            font-size: 0.9em;
        }}
        
        .criteria-list {{
            list-style: none;
            margin-top: 10px;
        }}
        
        .criteria-list li {{
            padding: 5px 0;
            padding-left: 25px;
            position: relative;
        }}
        
        .criteria-list li::before {{
            content: "✓";
            position: absolute;
            left: 0;
            color: var(--accent-green);
        }}
        
        .criteria-list li.fail::before {{
            content: "✗";
            color: var(--accent-red);
        }}
        
        .back-link {{
            display: inline-block;
            margin-bottom: 20px;
            color: var(--accent-blue);
            text-decoration: none;
        }}
        
        .back-link:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <a href="../all_strategies_montecarlo.html" class="back-link">← Retour au tableau de bord</a>
        
        <header>
            <h1>🎲 Monte Carlo Report</h1>
            <p class="subtitle">{strategy_full_name}</p>
            <p class="subtitle">Généré le {generation_date}</p>
        </header>
        
        <!-- Strategy Stats -->
        <div class="grid">
            <div class="card">
                <h2>📈 Statistiques de la Stratégie</h2>
                <div class="stat-grid">
                    <div class="stat">
                        <div class="stat-value">{total_trades}</div>
                        <div class="stat-label">Total Trades</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{trades_per_year}</div>
                        <div class="stat-label">Trades/An</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">${total_profit}</div>
                        <div class="stat-label">P&L Net Total</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{profit_factor}</div>
                        <div class="stat-label">Profit Factor</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{win_rate}%</div>
                        <div class="stat-label">Win Rate</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{backtest_years} ans</div>
                        <div class="stat-label">Période</div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h2>⚙️ Paramètres de Simulation</h2>
                <div class="stat-grid">
                    <div class="stat">
                        <div class="stat-value">{nb_simulations}</div>
                        <div class="stat-label">Simulations/Niveau</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{nb_capital_levels}</div>
                        <div class="stat-label">Niveaux de Capital</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{simulated_trades}</div>
                        <div class="stat-label">Trades Simulés/An</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{ruin_threshold}%</div>
                        <div class="stat-label">Seuil de Ruine</div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Recommendation -->
        <div class="recommendation {recommendation_class}">
            <h3 class="{status_class}">{recommendation_title}</h3>
            <p>{recommendation_text}</p>
            <ul class="criteria-list">
                {criteria_html}
            </ul>
        </div>
        
        <!-- Results Table -->
        <div class="card">
            <h2>📋 Résultats par Niveau de Capital</h2>
            <table>
                <thead>
                    <tr>
                        <th>Capital Initial</th>
                        <th>Risque Ruine</th>
                        <th>DD Médian</th>
                        <th>Profit Médian</th>
                        <th>Return Médian</th>
                        <th>Return/DD</th>
                        <th>Prob > 0</th>
                    </tr>
                </thead>
                <tbody>
                    {results_rows}
                </tbody>
            </table>
        </div>
        
        <!-- Charts -->
        <div class="chart-row">
            <div class="card">
                <h2>📉 Probabilité de Ruine vs Capital</h2>
                <div class="chart-container">
                    <canvas id="ruinChart"></canvas>
                </div>
            </div>
            
            <div class="card">
                <h2>📊 Return/DD Ratio vs Capital</h2>
                <div class="chart-container">
                    <canvas id="ratioChart"></canvas>
                </div>
            </div>
        </div>
        
        <div class="chart-row">
            <div class="card">
                <h2>💰 Profit Médian vs Capital</h2>
                <div class="chart-container">
                    <canvas id="profitChart"></canvas>
                </div>
            </div>
            
            <div class="card">
                <h2>📈 Probabilité Positive vs Capital</h2>
                <div class="chart-container">
                    <canvas id="probChart"></canvas>
                </div>
            </div>
        </div>
        
        <footer>
            <p>Simulation Monte Carlo basée sur la méthodologie Kevin Davey</p>
            <p>Critères: Risque Ruine ≤ 10% | Return/DD ≥ 2 | Prob > 0 ≥ 80%</p>
        </footer>
    </div>
    
    <script>
        // Chart.js configuration
        Chart.defaults.color = '#a0a0a0';
        Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.1)';
        
        // Data from Python
        const capitalLevels = {capital_levels_json};
        const ruinProbs = {ruin_probs_json};
        const returnDDRatios = {return_dd_ratios_json};
        const medianProfits = {median_profits_json};
        const probPositives = {prob_positives_json};
        const recommendedCapital = {recommended_capital_json};
        
        // Find recommended index
        const recIndex = capitalLevels.indexOf(recommendedCapital);
        
        // Ruin Probability Chart
        new Chart(document.getElementById('ruinChart'), {{
            type: 'line',
            data: {{
                labels: capitalLevels.map(c => '$' + c.toLocaleString()),
                datasets: [{{
                    label: 'Probabilité de Ruine (%)',
                    data: ruinProbs.map(r => r * 100),
                    borderColor: '#ff6b6b',
                    backgroundColor: 'rgba(255, 107, 107, 0.1)',
                    fill: true,
                    tension: 0.3,
                    pointBackgroundColor: capitalLevels.map((c, i) => i === recIndex ? '#00d4aa' : '#ff6b6b'),
                    pointRadius: capitalLevels.map((c, i) => i === recIndex ? 8 : 4),
                }}, {{
                    label: 'Seuil 10%',
                    data: Array(capitalLevels.length).fill(10),
                    borderColor: '#ffe66d',
                    borderDash: [5, 5],
                    fill: false,
                    pointRadius: 0,
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ position: 'top' }} }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{ display: true, text: 'Probabilité (%)' }}
                    }}
                }}
            }}
        }});
        
        // Return/DD Ratio Chart
        new Chart(document.getElementById('ratioChart'), {{
            type: 'bar',
            data: {{
                labels: capitalLevels.map(c => '$' + c.toLocaleString()),
                datasets: [{{
                    label: 'Return/DD Ratio',
                    data: returnDDRatios,
                    backgroundColor: returnDDRatios.map((r, i) => 
                        i === recIndex ? '#00d4aa' : (r >= 2 ? 'rgba(0, 212, 170, 0.6)' : 'rgba(255, 107, 107, 0.6)')
                    ),
                    borderColor: returnDDRatios.map((r, i) => 
                        i === recIndex ? '#00d4aa' : (r >= 2 ? '#00d4aa' : '#ff6b6b')
                    ),
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{ display: true, text: 'Ratio' }}
                    }}
                }}
            }}
        }});
        
        // Median Profit Chart
        new Chart(document.getElementById('profitChart'), {{
            type: 'line',
            data: {{
                labels: capitalLevels.map(c => '$' + c.toLocaleString()),
                datasets: [{{
                    label: 'Profit Médian ($)',
                    data: medianProfits,
                    borderColor: '#4ecdc4',
                    backgroundColor: 'rgba(78, 205, 196, 0.1)',
                    fill: true,
                    tension: 0.3,
                    pointBackgroundColor: capitalLevels.map((c, i) => i === recIndex ? '#00d4aa' : '#4ecdc4'),
                    pointRadius: capitalLevels.map((c, i) => i === recIndex ? 8 : 4),
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ position: 'top' }} }},
                scales: {{
                    y: {{
                        title: {{ display: true, text: 'Profit ($)' }}
                    }}
                }}
            }}
        }});
        
        // Probability Positive Chart
        new Chart(document.getElementById('probChart'), {{
            type: 'line',
            data: {{
                labels: capitalLevels.map(c => '$' + c.toLocaleString()),
                datasets: [{{
                    label: 'Probabilité > 0 (%)',
                    data: probPositives.map(p => p * 100),
                    borderColor: '#00d4aa',
                    backgroundColor: 'rgba(0, 212, 170, 0.1)',
                    fill: true,
                    tension: 0.3,
                    pointBackgroundColor: capitalLevels.map((c, i) => i === recIndex ? '#ffe66d' : '#00d4aa'),
                    pointRadius: capitalLevels.map((c, i) => i === recIndex ? 8 : 4),
                }}, {{
                    label: 'Seuil 80%',
                    data: Array(capitalLevels.length).fill(80),
                    borderColor: '#ffe66d',
                    borderDash: [5, 5],
                    fill: false,
                    pointRadius: 0,
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ position: 'top' }} }},
                scales: {{
                    y: {{
                        min: 50,
                        max: 100,
                        title: {{ display: true, text: 'Probabilité (%)' }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

SUMMARY_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Monte Carlo Batch Report - Dashboard Interactif</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-primary: #0f0f1a;
            --bg-secondary: #1a1a2e;
            --bg-card: #16213e;
            --text-primary: #eaeaea;
            --text-secondary: #a0a0a0;
            --accent-green: #00d4aa;
            --accent-red: #ff6b6b;
            --accent-blue: #4ecdc4;
            --accent-yellow: #ffe66d;
            --border-live: #ffd700;
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
            padding: 30px;
            background: var(--bg-secondary);
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }}
        
        h1 {{ 
            color: var(--accent-blue); 
            font-size: 2.5em; 
            margin-bottom: 10px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }}
        
        .subtitle {{ 
            color: var(--text-secondary); 
            font-size: 1.1em;
            margin-top: 10px;
        }}
        
        /* Stats Globales */
        .stats-global {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: var(--bg-card);
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            transition: transform 0.2s;
        }}
        
        .stat-card:hover {{ transform: translateY(-5px); }}
        
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: var(--accent-blue);
            margin-bottom: 5px;
        }}
        
        .stat-value.green {{ color: var(--accent-green); }}
        .stat-value.yellow {{ color: var(--accent-yellow); }}
        .stat-value.red {{ color: var(--accent-red); }}
        
        .stat-label {{
            color: var(--text-secondary);
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        /* Panneau Critères Dynamiques */
        .criteria-panel {{
            background: var(--bg-card);
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }}
        
        .criteria-panel h2 {{
            color: var(--accent-blue);
            font-size: 1.5em;
            margin-bottom: 20px;
            border-bottom: 2px solid var(--accent-blue);
            padding-bottom: 10px;
        }}
        
        .criteria-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .criterion {{
            background: var(--bg-secondary);
            padding: 15px;
            border-radius: 8px;
        }}
        
        .criterion-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        
        .criterion-label {{
            font-weight: 600;
            color: var(--text-primary);
        }}
        
        .criterion-value {{
            color: var(--accent-blue);
            font-weight: bold;
            font-size: 1.1em;
        }}
        
        .criterion-slider {{
            width: 100%;
            height: 6px;
            border-radius: 3px;
            background: var(--bg-primary);
            outline: none;
            opacity: 0.9;
            transition: opacity 0.2s;
        }}
        
        .criterion-slider:hover {{ opacity: 1; }}
        
        .criterion-slider::-webkit-slider-thumb {{
            appearance: none;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: var(--accent-blue);
            cursor: pointer;
        }}
        
        .criterion-slider::-moz-range-thumb {{
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: var(--accent-blue);
            cursor: pointer;
            border: none;
        }}
        
        .criterion-slider:disabled {{
            opacity: 0.3;
            cursor: not-allowed;
        }}
        
        .criterion-checkbox {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-top: 8px;
        }}
        
        .criterion-checkbox input[type="checkbox"] {{
            width: 18px;
            height: 18px;
            cursor: pointer;
        }}
        
        .criterion-checkbox label {{
            color: var(--text-secondary);
            font-size: 0.9em;
            cursor: pointer;
        }}
        
        .action-buttons {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }}
        
        .btn {{
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }}
        
        .btn-primary {{
            background: var(--accent-blue);
            color: var(--bg-primary);
        }}
        
        .btn-primary:hover {{
            background: #3db3aa;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(78, 205, 196, 0.3);
        }}
        
        .btn-secondary {{
            background: var(--bg-secondary);
            color: var(--text-primary);
            border: 2px solid var(--text-secondary);
        }}
        
        .btn-secondary:hover {{
            border-color: var(--accent-blue);
            color: var(--accent-blue);
        }}
        
        .btn-success {{
            background: var(--accent-green);
            color: var(--bg-primary);
        }}
        
        .btn-success:hover {{
            background: #00b894;
            transform: translateY(-2px);
        }}
        
        /* Stats Live */
        .stats-live {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
            padding: 20px;
            background: var(--bg-card);
            border-radius: 10px;
            border: 3px solid var(--border-live);
            box-shadow: 0 0 20px rgba(255, 215, 0, 0.2);
        }}
        
        .stats-live .stat-card {{
            background: var(--bg-secondary);
        }}
        
        .stats-live-title {{
            grid-column: 1 / -1;
            text-align: center;
            color: var(--border-live);
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        /* Filtres d'Affichage */
        .filters-panel {{
            background: var(--bg-card);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        
        .filters-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 15px;
        }}
        
        .filter-group {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        
        .filter-group label {{
            color: var(--text-secondary);
            font-size: 0.9em;
            font-weight: 600;
        }}
        
        .filter-group select,
        .filter-group input {{
            padding: 10px;
            background: var(--bg-secondary);
            color: var(--text-primary);
            border: 1px solid var(--text-secondary);
            border-radius: 6px;
            font-size: 0.95em;
        }}
        
        .filter-group select:focus,
        .filter-group input:focus {{
            outline: none;
            border-color: var(--accent-blue);
        }}
        
        /* Graphiques */
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .chart-card {{
            background: var(--bg-card);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }}
        
        .chart-card h3 {{
            color: var(--accent-blue);
            font-size: 1.1em;
            margin-bottom: 15px;
            text-align: center;
        }}
        
        .chart-container {{
            position: relative;
            height: 300px;
        }}
        
        /* Tableau */
        .table-container {{
            background: var(--bg-card);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
            overflow-x: auto;
        }}
        
        .table-container h3 {{
            color: var(--accent-blue);
            font-size: 1.3em;
            margin-bottom: 15px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th {{
            background: var(--bg-secondary);
            color: var(--accent-blue);
            padding: 12px;
            text-align: right;
            font-weight: 600;
            cursor: pointer;
            user-select: none;
            position: relative;
        }}
        
        th:hover {{ background: #252538; }}
        
        th:first-child {{ text-align: left; }}
        
        th.sorted-asc::after {{ content: " ▲"; color: var(--accent-green); }}
        th.sorted-desc::after {{ content: " ▼"; color: var(--accent-green); }}
        
        td {{
            padding: 10px 12px;
            text-align: right;
            border-bottom: 1px solid var(--bg-secondary);
        }}
        
        td:first-child {{ text-align: left; }}
        
        tbody tr {{
            transition: all 0.3s;
        }}
        
        tbody tr:hover {{
            background: rgba(78, 205, 196, 0.1);
        }}
        
        tbody tr.highlight {{
            animation: highlight-pulse 0.5s ease;
            background: rgba(255, 215, 0, 0.2);
        }}
        
        @keyframes highlight-pulse {{
            0%, 100% {{ background: rgba(255, 215, 0, 0); }}
            50% {{ background: rgba(255, 215, 0, 0.3); }}
        }}
        
        .strategy-link {{
            color: var(--accent-blue);
            text-decoration: none;
            font-weight: 500;
        }}
        
        .strategy-link:hover {{
            text-decoration: underline;
            color: #6dd5ed;
        }}
        
        .status-badge {{
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
            display: inline-block;
        }}
        
        .status-badge.status-ok {{
            background: rgba(0, 212, 170, 0.2);
            color: var(--accent-green);
            border: 1px solid var(--accent-green);
        }}
        
        .status-badge.status-warning {{
            background: rgba(255, 230, 109, 0.2);
            color: var(--accent-yellow);
            border: 1px solid var(--accent-yellow);
        }}
        
        .status-badge.status-danger {{
            background: rgba(255, 107, 107, 0.2);
            color: var(--accent-red);
            border: 1px solid var(--accent-red);
        }}
        
        footer {{
            text-align: center;
            margin-top: 50px;
            padding: 20px;
            color: var(--text-secondary);
            border-top: 1px solid var(--bg-secondary);
        }}
        
        @media (max-width: 768px) {{
            .stats-global, .stats-live {{ grid-template-columns: 1fr; }}
            .criteria-grid {{ grid-template-columns: 1fr; }}
            .charts-grid {{ grid-template-columns: 1fr; }}
            .action-buttons {{ flex-direction: column; }}
            .btn {{ width: 100%; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- HEADER -->
        <header>
            <h1>🎲 Monte Carlo Batch Analysis Dashboard</h1>
            <p class="subtitle">Dashboard Interactif - Recalcul Dynamique des Capitaux</p>
            <p class="subtitle">Généré le {generation_date}</p>
        </header>
        
        <!-- STATS GLOBALES -->
        <div class="stats-global">
            <div class="stat-card">
                <div class="stat-value">{total_strategies}</div>
                <div class="stat-label">Total Stratégies</div>
            </div>
            <div class="stat-card">
                <div class="stat-value green">{ok_count}</div>
                <div class="stat-label">✓ OK</div>
            </div>
            <div class="stat-card">
                <div class="stat-value yellow">{warning_count}</div>
                <div class="stat-label">⚠ Warning</div>
            </div>
            <div class="stat-card">
                <div class="stat-value red">{high_risk_count}</div>
                <div class="stat-label">✗ High Risk</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{total_trades}</div>
                <div class="stat-label">Total Trades</div>
            </div>
            <div class="stat-card">
                <div class="stat-value green">${{total_pnl}}</div>
                <div class="stat-label">P&L Net Total</div>
            </div>
        </div>
        
        <!-- PANNEAU CRITÈRES DYNAMIQUES -->
        <div class="criteria-panel">
            <h2>⚙️ Configuration des Critères de Risque</h2>
            
            <div class="criteria-grid">
                <!-- Critère 1: Risque de Ruine -->
                <div class="criterion">
                    <div class="criterion-header">
                        <span class="criterion-label">🎯 Risque de Ruine Max</span>
                        <span class="criterion-value" id="ruin-value">10.0%</span>
                    </div>
                    <input type="range" id="max-ruin" class="criterion-slider" 
                           min="0" max="30" step="0.5" value="10">
                    <div style="display: flex; justify-content: space-between; margin-top: 5px; font-size: 0.85em; color: var(--text-secondary);">
                        <span>0%</span>
                        <span>Toujours actif</span>
                        <span>30%</span>
                    </div>
                </div>
                
                <!-- Critère 2: Return/DD Ratio -->
                <div class="criterion">
                    <div class="criterion-header">
                        <span class="criterion-label">📊 Return/DD Ratio Min</span>
                        <span class="criterion-value" id="returndd-value">Désactivé</span>
                    </div>
                    <input type="range" id="min-return-dd" class="criterion-slider" 
                           min="0" max="5" step="0.1" value="2.0" disabled>
                    <div class="criterion-checkbox">
                        <input type="checkbox" id="enable-returndd">
                        <label for="enable-returndd">Activer ce critère</label>
                    </div>
                </div>
                
                <!-- Critère 3: Probabilité Positive -->
                <div class="criterion">
                    <div class="criterion-header">
                        <span class="criterion-label">✅ Probabilité Positive Min</span>
                        <span class="criterion-value" id="prob-value">Désactivé</span>
                    </div>
                    <input type="range" id="min-prob-positive" class="criterion-slider" 
                           min="0" max="100" step="1" value="80" disabled>
                    <div class="criterion-checkbox">
                        <input type="checkbox" id="enable-prob">
                        <label for="enable-prob">Activer ce critère</label>
                    </div>
                </div>
            </div>
            
            <div class="action-buttons">
                <button class="btn btn-primary" onclick="recalculateAll()">
                    🔄 Recalculer Maintenant
                </button>
                <button class="btn btn-secondary" onclick="resetCriteria()">
                    ↺ Réinitialiser
                </button>
                <button class="btn btn-success" onclick="setKevinDavey()">
                    📘 Kevin Davey Standard
                </button>
            </div>
        </div>
        
        <!-- STATS LIVE -->
        <div class="stats-live">
            <div class="stats-live-title">📊 Stats Live (Mises à Jour en Temps Réel)</div>
            <div class="stat-card">
                <div class="stat-value green" id="live-ok-count">{ok_count}</div>
                <div class="stat-label">OK</div>
            </div>
            <div class="stat-card">
                <div class="stat-value yellow" id="live-warning-count">{warning_count}</div>
                <div class="stat-label">WARNING</div>
            </div>
            <div class="stat-card">
                <div class="stat-value red" id="live-highrisk-count">{high_risk_count}</div>
                <div class="stat-label">HIGH RISK</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="live-with-capital-count">-</div>
                <div class="stat-label">Avec Capital</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="live-avg-capital">-</div>
                <div class="stat-label">Capital Moyen</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="live-median-capital">-</div>
                <div class="stat-label">Capital Médian</div>
            </div>
        </div>
        
        <!-- FILTRES D'AFFICHAGE -->
        <div class="filters-panel">
            <h3 style="color: var(--accent-blue); margin-bottom: 15px;">🔍 Filtres d'Affichage</h3>
            <div class="filters-grid">
                <div class="filter-group">
                    <label>Symbole</label>
                    <select id="filter-symbol">
                        <option value="">Tous les symboles</option>
                        {symbol_options}
                    </select>
                </div>
                <div class="filter-group">
                    <label>Statut</label>
                    <select id="filter-status">
                        <option value="">Tous les statuts</option>
                        <option value="OK">OK</option>
                        <option value="WARNING">WARNING</option>
                        <option value="HIGH_RISK">HIGH_RISK</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Trades Minimum</label>
                    <input type="number" id="filter-min-trades" value="20" min="0">
                </div>
            </div>
            <div class="action-buttons">
                <button class="btn btn-primary" onclick="applyDisplayFilters()">Appliquer</button>
                <button class="btn btn-secondary" onclick="resetDisplayFilters()">Reset</button>
            </div>
        </div>
        
        <!-- GRAPHIQUES -->
        <div class="charts-grid">
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
            <div class="chart-card">
                <h3>💰 Top 10 P&L Total</h3>
                <div class="chart-container">
                    <canvas id="topPnlChart"></canvas>
                </div>
            </div>
            <div class="chart-card">
                <h3>🏆 Top 10 Return/DD Ratio</h3>
                <div class="chart-container">
                    <canvas id="topRatioChart"></canvas>
                </div>
            </div>
        </div>
        
        <!-- TABLEAU -->
        <div class="table-container">
            <h3>📋 Stratégies (<span id="visible-count">{total_strategies}</span> affichées)</h3>
            <table>
                <thead>
                    <tr>
                        <th data-sort="strategy">Stratégie</th>
                        <th data-sort="symbol">Symbol</th>
                        <th data-sort="status">Statut</th>
                        <th data-sort="capital">Capital</th>
                        <th data-sort="trades">Trades</th>
                        <th data-sort="pnl">P&L</th>
                        <th data-sort="winrate">Win%</th>
                        <th data-sort="pf">PF</th>
                        <th data-sort="ruin">Ruine%</th>
                        <th data-sort="ratio">Ret/DD</th>
                        <th data-sort="prob">Prob>0</th>
                    </tr>
                </thead>
                <tbody id="table-body">
                    {table_rows}
                </tbody>
            </table>
        </div>
        
        <footer>
            <p>{config_info}</p>
            <p style="margin-top: 10px;">Méthodologie Kevin Davey - Building Winning Algorithmic Trading Systems</p>
        </footer>
    </div>
    
    <script>
        // =====================================================================
        // DONNÉES EMBARQUÉES
        // =====================================================================
        const strategiesData = {strategies_json};
        const strategiesDetailed = {strategies_detailed_json};
        
        console.log('Dashboard chargé:', Object.keys(strategiesDetailed).length, 'stratégies avec données détaillées');
        
        // Configuration Chart.js
        Chart.defaults.color = '#a0a0a0';
        Chart.defaults.font.size = 12;
        
        // =====================================================================
        // GRAPHIQUES STATIQUES
        // =====================================================================
        
        // Pie Chart: Distribution par statut
        new Chart(document.getElementById('statusChart'), {{
            type: 'doughnut',
            data: {{
                labels: ['OK', 'WARNING', 'HIGH_RISK'],
                datasets: [{{
                    data: [{ok_count}, {warning_count}, {high_risk_count}],
                    backgroundColor: ['#00d4aa', '#ffe66d', '#ff6b6b'],
                    borderWidth: 2,
                    borderColor: '#0f0f1a'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'bottom',
                        labels: {{ 
                            color: '#a0a0a0',
                            padding: 15,
                            font: {{ size: 12 }}
                        }}
                    }}
                }}
            }}
        }});
        
        // Scatter Chart: Return/DD vs Ruine
        new Chart(document.getElementById('scatterChart'), {{
            type: 'scatter',
            data: {{
                datasets: [{{
                    data: strategiesData.map(s => ({{
                        x: s.ruin_pct,
                        y: Math.min(s.return_dd_ratio, 10)
                    }})),
                    backgroundColor: strategiesData.map(s => 
                        s.status === 'OK' ? '#00d4aa' : 
                        s.status === 'WARNING' ? '#ffe66d' : '#ff6b6b'
                    ),
                    pointRadius: 5,
                    pointHoverRadius: 7
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    x: {{
                        title: {{ display: true, text: 'Risque de Ruine (%)', color: '#4ecdc4' }},
                        grid: {{ color: 'rgba(255,255,255,0.1)' }}
                    }},
                    y: {{
                        title: {{ display: true, text: 'Return/DD Ratio', color: '#4ecdc4' }},
                        grid: {{ color: 'rgba(255,255,255,0.1)' }},
                        max: 10
                    }}
                }}
            }}
        }});
        
        // Bar Chart: Top 10 P&L
        const topPnl = strategiesData
            .sort((a, b) => b.total_pnl - a.total_pnl)
            .slice(0, 10);
        
        new Chart(document.getElementById('topPnlChart'), {{
            type: 'bar',
            data: {{
                labels: topPnl.map(s => s.strategy_name.substring(0, 25)),
                datasets: [{{
                    data: topPnl.map(s => s.total_pnl),
                    backgroundColor: '#4ecdc4',
                    borderColor: '#3db3aa',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    x: {{
                        title: {{ display: true, text: 'P&L Net ($)', color: '#4ecdc4' }},
                        grid: {{ color: 'rgba(255,255,255,0.1)' }}
                    }},
                    y: {{
                        grid: {{ color: 'rgba(255,255,255,0.1)' }}
                    }}
                }}
            }}
        }});
        
        // Bar Chart: Top 10 Return/DD
        const topRatio = strategiesData
            .filter(s => s.return_dd_ratio < 100)
            .sort((a, b) => b.return_dd_ratio - a.return_dd_ratio)
            .slice(0, 10);
        
        new Chart(document.getElementById('topRatioChart'), {{
            type: 'bar',
            data: {{
                labels: topRatio.map(s => s.strategy_name.substring(0, 25)),
                datasets: [{{
                    data: topRatio.map(s => s.return_dd_ratio),
                    backgroundColor: topRatio.map(s => 
                        s.return_dd_ratio >= 2 ? '#00d4aa' : '#ffe66d'
                    ),
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    x: {{
                        title: {{ display: true, text: 'Return/DD Ratio', color: '#4ecdc4' }},
                        grid: {{ color: 'rgba(255,255,255,0.1)' }}
                    }},
                    y: {{
                        grid: {{ color: 'rgba(255,255,255,0.1)' }}
                    }}
                }}
            }}
        }});
        
        // =====================================================================
        // LOGIQUE DE RECALCUL DYNAMIQUE
        // =====================================================================
        
        let activeCriteria = {{
            maxRuin: 10.0,
            minReturnDD: null,
            minProbPositive: null
        }};
        
        /**
         * Trouve le capital recommandé pour une stratégie selon les critères actifs
         */
        function findRecommendedCapital(strategyName) {{
            const strategy = strategiesDetailed[strategyName];
            if (!strategy || !strategy.levels) {{
                return {{ capital: null, status: 'HIGH_RISK', metrics: {{}} }};
            }}
            
            const levels = strategy.levels.sort((a, b) => a.capital - b.capital);
            
            for (let level of levels) {{
                // Vérifier critère 1 (TOUJOURS actif)
                const ruinOK = level.ruin_pct <= activeCriteria.maxRuin;
                
                // Vérifier critère 2 (si activé)
                const returnDDOK = activeCriteria.minReturnDD === null || 
                                   level.return_dd >= activeCriteria.minReturnDD;
                
                // Vérifier critère 3 (si activé)
                const probOK = activeCriteria.minProbPositive === null || 
                               level.prob_positive >= activeCriteria.minProbPositive;
                
                // Si TOUS les critères actifs sont OK
                if (ruinOK && returnDDOK && probOK) {{
                    return {{
                        capital: level.capital,
                        status: 'OK',
                        metrics: {{
                            ruin: level.ruin_pct,
                            returnDD: level.return_dd,
                            probPositive: level.prob_positive
                        }}
                    }};
                }}
                
                // Si SEULEMENT la ruine est OK
                if (ruinOK) {{
                    return {{
                        capital: level.capital,
                        status: 'WARNING',
                        metrics: {{
                            ruin: level.ruin_pct,
                            returnDD: level.return_dd,
                            probPositive: level.prob_positive
                        }}
                    }};
                }}
            }}
            
            // Aucun niveau ne satisfait même la ruine
            return {{ capital: null, status: 'HIGH_RISK', metrics: {{}} }};
        }}
        
        /**
         * Met à jour une ligne du tableau avec les nouveaux résultats
         */
        function updateTableRow(strategyName, result) {{
            const row = document.querySelector(`tr[data-strategy="${{strategyName}}"]`);
            if (!row) return;
            
            const cells = row.querySelectorAll('td');
            const badge = cells[2].querySelector('.status-badge');
            
            // Mettre à jour le badge de statut
            badge.className = 'status-badge';
            if (result.status === 'OK') {{
                badge.classList.add('status-ok');
                badge.textContent = '✓ OK';
            }} else if (result.status === 'WARNING') {{
                badge.classList.add('status-warning');
                badge.textContent = '⚠ WARNING';
            }} else {{
                badge.classList.add('status-danger');
                badge.textContent = '✗ HIGH RISK';
            }}
            
            // Mettre à jour le capital recommandé
            cells[3].textContent = result.capital ? `$$${{result.capital.toLocaleString()}}` : 'N/A';
            
            // Mettre à jour les métriques si disponibles
            if (result.capital && result.metrics.ruin !== undefined) {{
                cells[8].textContent = result.metrics.ruin.toFixed(1) + '%';
                cells[9].textContent = result.metrics.returnDD.toFixed(2);
                cells[10].textContent = result.metrics.probPositive.toFixed(1) + '%';
            }}
            
            // Mettre à jour l'attribut data-status
            row.setAttribute('data-status', result.status);
            
            // Animation highlight
            row.classList.add('highlight');
            setTimeout(() => row.classList.remove('highlight'), 500);
        }}
        
        /**
         * Recalcule TOUTES les stratégies et met à jour les stats live
         */
        function recalculateAll() {{
            console.log('Recalcul avec critères:', activeCriteria);
            
            let okCount = 0, warningCount = 0, highRiskCount = 0;
            let capitals = [];
            
            for (let strategyName in strategiesDetailed) {{
                const result = findRecommendedCapital(strategyName);
                updateTableRow(strategyName, result);
                
                if (result.status === 'OK') okCount++;
                else if (result.status === 'WARNING') warningCount++;
                else highRiskCount++;
                
                if (result.capital) capitals.push(result.capital);
            }}
            
            // Mettre à jour les stats live
            document.getElementById('live-ok-count').textContent = okCount;
            document.getElementById('live-warning-count').textContent = warningCount;
            document.getElementById('live-highrisk-count').textContent = highRiskCount;
            document.getElementById('live-with-capital-count').textContent = capitals.length;
            
            if (capitals.length > 0) {{
                const avg = capitals.reduce((a, b) => a + b, 0) / capitals.length;
                const sorted = capitals.sort((a, b) => a - b);
                const median = sorted[Math.floor(capitals.length / 2)];
                
                document.getElementById('live-avg-capital').textContent = 
                    '$' + Math.round(avg).toLocaleString();
                document.getElementById('live-median-capital').textContent = 
                    '$' + median.toLocaleString();
            }} else {{
                document.getElementById('live-avg-capital').textContent = 'N/A';
                document.getElementById('live-median-capital').textContent = 'N/A';
            }}
            
            console.log('Recalcul terminé:', okCount, 'OK,', warningCount, 'WARNING,', highRiskCount, 'HIGH_RISK');
        }}
        
        // =====================================================================
        // EVENT LISTENERS POUR LES SLIDERS ET BOUTONS
        // =====================================================================
        
        // Slider Ruine (toujours actif)
        document.getElementById('max-ruin').addEventListener('input', (e) => {{
            activeCriteria.maxRuin = parseFloat(e.target.value);
            document.getElementById('ruin-value').textContent = 
                activeCriteria.maxRuin.toFixed(1) + '%';
        }});
        
        // Checkbox Return/DD
        document.getElementById('enable-returndd').addEventListener('change', (e) => {{
            const slider = document.getElementById('min-return-dd');
            slider.disabled = !e.target.checked;
            activeCriteria.minReturnDD = e.target.checked ? parseFloat(slider.value) : null;
            document.getElementById('returndd-value').textContent = 
                e.target.checked ? activeCriteria.minReturnDD.toFixed(1) : 'Désactivé';
        }});
        
        // Slider Return/DD
        document.getElementById('min-return-dd').addEventListener('input', (e) => {{
            activeCriteria.minReturnDD = parseFloat(e.target.value);
            document.getElementById('returndd-value').textContent = 
                activeCriteria.minReturnDD.toFixed(1);
        }});
        
        // Checkbox Probabilité
        document.getElementById('enable-prob').addEventListener('change', (e) => {{
            const slider = document.getElementById('min-prob-positive');
            slider.disabled = !e.target.checked;
            activeCriteria.minProbPositive = e.target.checked ? parseFloat(slider.value) : null;
            document.getElementById('prob-value').textContent = 
                e.target.checked ? activeCriteria.minProbPositive.toFixed(0) + '%' : 'Désactivé';
        }});
        
        // Slider Probabilité
        document.getElementById('min-prob-positive').addEventListener('input', (e) => {{
            activeCriteria.minProbPositive = parseFloat(e.target.value);
            document.getElementById('prob-value').textContent = 
                activeCriteria.minProbPositive.toFixed(0) + '%';
        }});
        
        // =====================================================================
        // BOUTONS D'ACTION
        // =====================================================================
        
        /**
         * Réinitialise les critères (Ruine 10%, autres désactivés)
         */
        function resetCriteria() {{
            activeCriteria = {{ maxRuin: 10.0, minReturnDD: null, minProbPositive: null }};
            
            document.getElementById('max-ruin').value = 10;
            document.getElementById('ruin-value').textContent = '10.0%';
            
            document.getElementById('enable-returndd').checked = false;
            document.getElementById('min-return-dd').disabled = true;
            document.getElementById('returndd-value').textContent = 'Désactivé';
            
            document.getElementById('enable-prob').checked = false;
            document.getElementById('min-prob-positive').disabled = true;
            document.getElementById('prob-value').textContent = 'Désactivé';
            
            recalculateAll();
        }}
        
        /**
         * Configure les critères Kevin Davey standard
         */
        function setKevinDavey() {{
            activeCriteria = {{ maxRuin: 10.0, minReturnDD: 2.0, minProbPositive: 80.0 }};
            
            document.getElementById('max-ruin').value = 10;
            document.getElementById('ruin-value').textContent = '10.0%';
            
            document.getElementById('enable-returndd').checked = true;
            document.getElementById('min-return-dd').disabled = false;
            document.getElementById('min-return-dd').value = 2.0;
            document.getElementById('returndd-value').textContent = '2.0';
            
            document.getElementById('enable-prob').checked = true;
            document.getElementById('min-prob-positive').disabled = false;
            document.getElementById('min-prob-positive').value = 80;
            document.getElementById('prob-value').textContent = '80%';
            
            recalculateAll();
        }}
        
        // =====================================================================
        // FILTRES D'AFFICHAGE
        // =====================================================================
        
        function applyDisplayFilters() {{
            const symbol = document.getElementById('filter-symbol').value;
            const status = document.getElementById('filter-status').value;
            const minTrades = parseInt(document.getElementById('filter-min-trades').value) || 0;
            
            const rows = document.querySelectorAll('#table-body tr');
            let count = 0;
            
            rows.forEach(row => {{
                const rowSymbol = row.getAttribute('data-symbol');
                const rowStatus = row.getAttribute('data-status');
                const rowTrades = parseInt(
                    row.querySelectorAll('td')[4].textContent.replace(/,/g, '')
                );
                
                const matchSymbol = !symbol || rowSymbol === symbol;
                const matchStatus = !status || rowStatus === status;
                const matchTrades = rowTrades >= minTrades;
                
                const match = matchSymbol && matchStatus && matchTrades;
                row.style.display = match ? '' : 'none';
                if (match) count++;
            }});
            
            document.getElementById('visible-count').textContent = count;
        }}
        
        function resetDisplayFilters() {{
            document.getElementById('filter-symbol').value = '';
            document.getElementById('filter-status').value = '';
            document.getElementById('filter-min-trades').value = '20';
            applyDisplayFilters();
        }}
        
        // =====================================================================
        // TRI DE TABLEAU
        // =====================================================================
        
        document.querySelectorAll('th[data-sort]').forEach(th => {{
            th.addEventListener('click', () => {{
                const column = th.getAttribute('data-sort');
                const direction = th.classList.contains('sorted-asc') ? 'desc' : 'asc';
                
                // Retirer les indicateurs de tri
                document.querySelectorAll('th[data-sort]').forEach(h => 
                    h.classList.remove('sorted-asc', 'sorted-desc')
                );
                th.classList.add(`sorted-${{direction}}`);
                
                const tbody = document.getElementById('table-body');
                const rows = Array.from(tbody.querySelectorAll('tr'));
                
                const columnMap = {{
                    strategy: 0, symbol: 1, status: 2, capital: 3,
                    trades: 4, pnl: 5, winrate: 6, pf: 7,
                    ruin: 8, ratio: 9, prob: 10
                }};
                
                const colIndex = columnMap[column];
                
                rows.sort((a, b) => {{
                    const aCell = a.querySelectorAll('td')[colIndex];
                    const bCell = b.querySelectorAll('td')[colIndex];
                    
                    if (!aCell || !bCell) return 0;
                    
                    const aVal = aCell.textContent || '';
                    const bVal = bCell.textContent || '';
                    
                    // Pour les colonnes textuelles
                    if (column === 'strategy' || column === 'symbol' || column === 'status') {{
                        return direction === 'asc' ? 
                            aVal.localeCompare(bVal) : 
                            bVal.localeCompare(aVal);
                    }}
                    
                    // Pour les colonnes numériques
                    const aNum = parseFloat(aVal.replace(/[^0-9.-]/g, '')) || 0;
                    const bNum = parseFloat(bVal.replace(/[^0-9.-]/g, '')) || 0;
                    
                    return direction === 'asc' ? aNum - bNum : bNum - aNum;
                }});
                
                rows.forEach(row => tbody.appendChild(row));
            }});
        }});
        
        // =====================================================================
        // INITIALISATION AU CHARGEMENT
        // =====================================================================
        
        window.addEventListener('load', () => {{
            console.log('Dashboard initialisé');
            console.log('Stratégies chargées:', Object.keys(strategiesDetailed).length);
            
            // Premier recalcul avec les critères par défaut
            recalculateAll();
        }});
    </script>
</body>
</html>
"""