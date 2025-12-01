#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RESTAURATION PROPRE - Version qui marchait AVANT les graphiques dynamiques
"""
from pathlib import Path
import shutil

print("=" * 80)
print("RESTAURATION VERSION PROPRE")
print("=" * 80)

src_file = Path("C:/TradeData/V2/src/monte_carlo/html_templates.py")
backup_file = Path("C:/TradeData/V2/backups/html_templates.py.before_fix")

# Backup
print("\n📦 Sauvegarde...")
backup_file.parent.mkdir(exist_ok=True)
shutil.copy2(src_file, backup_file)
print(f"   ✓ Sauvegardé: {backup_file}")

# Écrire la BONNE version
print("\n✍️  Écriture de la version propre...")

# Je vais lire le template individuel qui n'a pas changé
with open(src_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Trouver où commence SUMMARY_TEMPLATE
summary_start = None
for i, line in enumerate(lines):
    if 'SUMMARY_TEMPLATE' in line and '=' in line:
        summary_start = i
        break

if summary_start is None:
    print("❌ Impossible de trouver SUMMARY_TEMPLATE")
    exit(1)

# Garder tout AVANT SUMMARY_TEMPLATE
individual_part = ''.join(lines[:summary_start])

# Le nouveau SUMMARY_TEMPLATE propre
summary_template = '''SUMMARY_TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Monte Carlo Batch Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-primary: #0f0f1a; --bg-secondary: #1a1a2e; --bg-card: #16213e;
            --text-primary: #eaeaea; --text-secondary: #a0a0a0;
            --accent-green: #00d4aa; --accent-red: #ff6b6b; --accent-blue: #4ecdc4; --accent-yellow: #ffe66d;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: var(--bg-primary); color: var(--text-primary); padding: 20px; }}
        .container {{ max-width: 1600px; margin: 0 auto; }}
        header {{ text-align: center; margin-bottom: 30px; padding: 25px; background: linear-gradient(135deg, var(--bg-secondary), var(--bg-card)); border-radius: 15px; }}
        h1 {{ color: var(--accent-blue); font-size: 2.2em; }}
        .subtitle {{ color: var(--text-secondary); }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 25px; }}
        .stat-card {{ background: var(--bg-card); border-radius: 12px; padding: 20px; text-align: center; }}
        .stat-value {{ font-size: 2.2em; font-weight: bold; color: var(--accent-blue); }}
        .stat-value.ok {{ color: var(--accent-green); }}
        .stat-value.warning {{ color: var(--accent-yellow); }}
        .stat-value.danger {{ color: var(--accent-red); }}
        .stat-label {{ font-size: 0.9em; color: var(--text-secondary); margin-top: 5px; }}
        .filters {{ background: var(--bg-card); border-radius: 12px; padding: 20px; margin-bottom: 25px; display: flex; flex-wrap: wrap; gap: 15px; }}
        .filter-group {{ display: flex; flex-direction: column; gap: 5px; }}
        .filter-group label {{ font-size: 0.85em; color: var(--text-secondary); }}
        .filter-group select, .filter-group input {{ padding: 8px 12px; border-radius: 6px; background: var(--bg-secondary); color: var(--text-primary); min-width: 150px; }}
        .btn {{ padding: 10px 20px; border-radius: 6px; border: none; cursor: pointer; }}
        .btn-primary {{ background: var(--accent-blue); color: var(--bg-primary); }}
        .btn-secondary {{ background: var(--bg-secondary); color: var(--text-primary); }}
        .charts-row {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; margin-bottom: 25px; }}
        .chart-card {{ background: var(--bg-card); border-radius: 12px; padding: 20px; }}
        .chart-card h3 {{ color: var(--accent-blue); margin-bottom: 15px; }}
        .chart-container {{ position: relative; height: 300px; }}
        .table-container {{ background: var(--bg-card); border-radius: 12px; padding: 20px; overflow-x: auto; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 0.9em; }}
        th, td {{ padding: 12px 10px; text-align: right; border-bottom: 1px solid rgba(255,255,255,0.05); }}
        th {{ background: var(--bg-secondary); color: var(--accent-blue); cursor: pointer; }}
        th:first-child, td:first-child {{ text-align: left; }}
        tr:hover {{ background: rgba(78, 205, 196, 0.05); }}
        .status-badge {{ padding: 4px 10px; border-radius: 20px; font-size: 0.85em; }}
        .status-ok {{ background: rgba(0, 212, 170, 0.2); color: var(--accent-green); }}
        .status-warning {{ background: rgba(255, 230, 109, 0.2); color: var(--accent-yellow); }}
        .status-danger {{ background: rgba(255, 107, 107, 0.2); color: var(--accent-red); }}
        .highlight {{ background: rgba(78, 205, 196, 0.2); animation: highlightFade 0.5s; }}
        @keyframes highlightFade {{ from {{ background: rgba(78, 205, 196, 0.5); }} to {{ background: rgba(78, 205, 196, 0.1); }} }}
        .strategy-link {{ color: var(--accent-blue); text-decoration: none; }}
        .strategy-link:hover {{ color: var(--accent-green); text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎲 Monte Carlo Batch Report</h1>
            <p class="subtitle">Généré le {generation_date}</p>
        </header>
        
        <div class="stats-grid">
            <div class="stat-card"><div class="stat-value">{total_strategies}</div><div class="stat-label">Stratégies</div></div>
            <div class="stat-card"><div class="stat-value ok">{ok_count}</div><div class="stat-label">✓ OK</div></div>
            <div class="stat-card"><div class="stat-value warning">{warning_count}</div><div class="stat-label">⚠ Warning</div></div>
            <div class="stat-card"><div class="stat-value danger">{high_risk_count}</div><div class="stat-label">✗ High Risk</div></div>
            <div class="stat-card"><div class="stat-value">{total_trades}</div><div class="stat-label">Total Trades</div></div>
            <div class="stat-card"><div class="stat-value">${total_pnl}</div><div class="stat-label">P&L Total</div></div>
        </div>
        
        <div class="filters" style="border: 2px solid var(--accent-blue);">
            <h3 style="width: 100%; color: var(--accent-blue);">🎯 Critères Dynamiques</h3>
            <div class="filter-group" style="flex: 1; min-width: 250px;">
                <label>Risque Ruine Max: <span id="ruin-value" style="color: var(--accent-green); font-weight: bold;">10.0</span>%</label>
                <input type="range" id="max-ruin" min="0" max="30" value="10" step="0.5" style="width: 100%;">
            </div>
            <div class="filter-group" style="flex: 1; min-width: 250px;">
                <label>Return/DD Min: <span id="returndd-value">Désactivé</span><input type="checkbox" id="enable-returndd" style="margin-left: 10px;"></label>
                <input type="range" id="min-return-dd" min="0" max="5" value="2.0" step="0.1" disabled style="width: 100%;">
            </div>
            <div class="filter-group" style="flex: 1; min-width: 250px;">
                <label>Prob Positive Min: <span id="prob-value">Désactivé</span><input type="checkbox" id="enable-prob" style="margin-left: 10px;"></label>
                <input type="range" id="min-prob-positive" min="0" max="100" value="80" step="1" disabled style="width: 100%;">
            </div>
            <div style="width: 100%; display: flex; gap: 10px; margin-top: 15px;">
                <button class="btn btn-primary" onclick="recalculateAll()">🔄 Recalculer</button>
                <button class="btn btn-secondary" onclick="resetCriteria()">↺ Réinitialiser</button>
                <button class="btn btn-secondary" onclick="setKevinDavey()">📘 Kevin Davey</button>
            </div>
        </div>
        
        <div class="stats-grid" style="border: 2px solid var(--accent-yellow); padding: 15px;">
            <div class="stat-card"><div class="stat-value ok" id="live-ok-count">{ok_count}</div><div class="stat-label">✓ OK</div></div>
            <div class="stat-card"><div class="stat-value warning" id="live-warning-count">{warning_count}</div><div class="stat-label">⚠ WARNING</div></div>
            <div class="stat-card"><div class="stat-value danger" id="live-highrisk-count">{high_risk_count}</div><div class="stat-label">✗ HIGH RISK</div></div>
            <div class="stat-card"><div class="stat-value" id="live-with-capital-count">{total_strategies}</div><div class="stat-label">Avec Capital</div></div>
            <div class="stat-card"><div class="stat-value" id="live-avg-capital">-</div><div class="stat-label">Capital Moyen</div></div>
            <div class="stat-card"><div class="stat-value" id="live-median-capital">-</div><div class="stat-label">Capital Médian</div></div>
        </div>
        
        <div class="filters">
            <div class="filter-group">
                <label>Symbole</label>
                <select id="filter-symbol"><option value="">Tous</option>{symbol_options}</select>
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
            <button class="btn btn-primary" onclick="applyDisplayFilters()">Appliquer</button>
            <button class="btn btn-secondary" onclick="resetDisplayFilters()">Reset</button>
        </div>
        
        <div class="charts-row">
            <div class="chart-card"><h3>📊 Distribution</h3><div class="chart-container"><canvas id="statusChart"></canvas></div></div>
            <div class="chart-card"><h3>📈 Return/DD vs Risque</h3><div class="chart-container"><canvas id="scatterChart"></canvas></div></div>
        </div>
        
        <div class="charts-row">
            <div class="chart-card"><h3>💰 Top 10 P&L</h3><div class="chart-container"><canvas id="topPnlChart"></canvas></div></div>
            <div class="chart-card"><h3>🏆 Top 10 Return/DD</h3><div class="chart-container"><canvas id="topRatioChart"></canvas></div></div>
        </div>
        
        <div class="table-container">
            <h3>📋 Stratégies (<span id="visible-count">{total_strategies}</span> affichées)</h3>
            <table>
                <thead>
                    <tr>
                        <th data-sort="strategy">Stratégie</th><th data-sort="symbol">Symbol</th><th data-sort="status">Statut</th>
                        <th data-sort="capital">Capital</th><th data-sort="trades">Trades</th><th data-sort="pnl">P&L</th>
                        <th data-sort="winrate">Win%</th><th data-sort="pf">PF</th><th data-sort="ruin">Ruine%</th>
                        <th data-sort="ratio">Ret/DD</th><th data-sort="prob">Prob>0</th>
                    </tr>
                </thead>
                <tbody id="table-body">{table_rows}</tbody>
            </table>
        </div>
        
        <footer><p>{config_info}</p></footer>
    </div>
    
    <script>
        const strategiesData = {strategies_json};
        const strategiesDetailed = {strategies_detailed_json};
        Chart.defaults.color = '#a0a0a0';
        
        new Chart(document.getElementById('statusChart'), {{type: 'doughnut', data: {{labels: ['OK', 'WARN', 'RISK'], datasets: [{{data: [{ok_count}, {warning_count}, {high_risk_count}], backgroundColor: ['#00d4aa', '#ffe66d', '#ff6b6b']}}]}}, options: {{responsive: true, maintainAspectRatio: false}}}});
        new Chart(document.getElementById('scatterChart'), {{type: 'scatter', data: {{datasets: [{{data: strategiesData.map(s => ({{x: s.ruin_pct, y: Math.min(s.return_dd_ratio, 10)}})), backgroundColor: strategiesData.map(s => s.status === 'OK' ? '#00d4aa' : (s.status === 'WARNING' ? '#ffe66d' : '#ff6b6b'))}}]}}, options: {{responsive: true, maintainAspectRatio: false, plugins: {{legend: {{display: false}}}}, scales: {{x: {{title: {{display: true, text: 'Ruine%'}}}}, y: {{title: {{display: true, text: 'Return/DD'}}, max: 10}}}}}}}});
        
        const topPnl = strategiesData.sort((a, b) => b.total_pnl - a.total_pnl).slice(0, 10);
        new Chart(document.getElementById('topPnlChart'), {{type: 'bar', data: {{labels: topPnl.map(s => s.strategy_name.substring(0, 20)), datasets: [{{data: topPnl.map(s => s.total_pnl), backgroundColor: '#4ecdc4'}}]}}, options: {{responsive: true, maintainAspectRatio: false, indexAxis: 'y', plugins: {{legend: {{display: false}}}}}}}});
        
        const topRatio = strategiesData.filter(s => s.return_dd_ratio < 100).sort((a, b) => b.return_dd_ratio - a.return_dd_ratio).slice(0, 10);
        new Chart(document.getElementById('topRatioChart'), {{type: 'bar', data: {{labels: topRatio.map(s => s.strategy_name.substring(0, 20)), datasets: [{{data: topRatio.map(s => s.return_dd_ratio), backgroundColor: topRatio.map(s => s.return_dd_ratio >= 2 ? '#00d4aa' : '#ffe66d')}}]}}, options: {{responsive: true, maintainAspectRatio: false, indexAxis: 'y', plugins: {{legend: {{display: false}}}}}}}});
        
        let activeCriteria = {{maxRuin: 10.0, minReturnDD: null, minProbPositive: null}};
        
        function findRecommendedCapital(strategyName) {{
            const strategy = strategiesDetailed[strategyName];
            if (!strategy || !strategy.levels) return {{capital: null, status: 'HIGH_RISK', metrics: {{}}}};
            const levels = strategy.levels.sort((a, b) => a.capital - b.capital);
            for (let level of levels) {{
                const ruinOK = level.ruin_pct <= activeCriteria.maxRuin;
                const returnDDOK = activeCriteria.minReturnDD === null || level.return_dd >= activeCriteria.minReturnDD;
                const probOK = activeCriteria.minProbPositive === null || level.prob_positive >= activeCriteria.minProbPositive;
                if (ruinOK && returnDDOK && probOK) return {{capital: level.capital, status: 'OK', metrics: {{ruin: level.ruin_pct, returnDD: level.return_dd, probPositive: level.prob_positive}}}};
                if (ruinOK) return {{capital: level.capital, status: 'WARNING', metrics: {{ruin: level.ruin_pct, returnDD: level.return_dd, probPositive: level.prob_positive}}}};
            }}
            return {{capital: null, status: 'HIGH_RISK', metrics: {{}}}};
        }}
        
        function updateTableRow(strategyName, result) {{
            const row = document.querySelector(`tr[data-strategy="${{strategyName}}"]`);
            if (!row) return;
            const cells = row.querySelectorAll('td');
            const badge = cells[2].querySelector('.status-badge');
            badge.className = 'status-badge';
            if (result.status === 'OK') {{badge.classList.add('status-ok'); badge.textContent = '✓ OK';}}
            else if (result.status === 'WARNING') {{badge.classList.add('status-warning'); badge.textContent = '⚠ WARNING';}}
            else {{badge.classList.add('status-danger'); badge.textContent = '✗ HIGH RISK';}}
            cells[3].textContent = result.capital ? `$${{result.capital.toLocaleString()}}` : 'N/A';
            if (result.capital && result.metrics.ruin !== undefined) {{
                cells[8].textContent = result.metrics.ruin.toFixed(1) + '%';
                cells[9].textContent = result.metrics.returnDD.toFixed(2);
                cells[10].textContent = result.metrics.probPositive.toFixed(1) + '%';
            }}
            row.classList.add('highlight');
            setTimeout(() => row.classList.remove('highlight'), 500);
        }}
        
        function recalculateAll() {{
            let okCount = 0, warningCount = 0, highRiskCount = 0, capitals = [];
            for (let strategyName in strategiesDetailed) {{
                const result = findRecommendedCapital(strategyName);
                updateTableRow(strategyName, result);
                if (result.status === 'OK') okCount++;
                else if (result.status === 'WARNING') warningCount++;
                else highRiskCount++;
                if (result.capital) capitals.push(result.capital);
            }}
            document.getElementById('live-ok-count').textContent = okCount;
            document.getElementById('live-warning-count').textContent = warningCount;
            document.getElementById('live-highrisk-count').textContent = highRiskCount;
            document.getElementById('live-with-capital-count').textContent = capitals.length;
            if (capitals.length > 0) {{
                const avg = capitals.reduce((a, b) => a + b, 0) / capitals.length;
                const median = capitals.sort((a, b) => a - b)[Math.floor(capitals.length / 2)];
                document.getElementById('live-avg-capital').textContent = '$$' + Math.round(avg).toLocaleString();
                document.getElementById('live-median-capital').textContent = '$$' + median.toLocaleString();
            }}
        }}
        
        document.getElementById('max-ruin').addEventListener('input', (e) => {{activeCriteria.maxRuin = parseFloat(e.target.value); document.getElementById('ruin-value').textContent = activeCriteria.maxRuin.toFixed(1);}});
        document.getElementById('enable-returndd').addEventListener('change', (e) => {{const s = document.getElementById('min-return-dd'); s.disabled = !e.target.checked; activeCriteria.minReturnDD = e.target.checked ? parseFloat(s.value) : null; document.getElementById('returndd-value').textContent = e.target.checked ? activeCriteria.minReturnDD.toFixed(1) : 'Désactivé';}});
        document.getElementById('min-return-dd').addEventListener('input', (e) => {{activeCriteria.minReturnDD = parseFloat(e.target.value); document.getElementById('returndd-value').textContent = activeCriteria.minReturnDD.toFixed(1);}});
        document.getElementById('enable-prob').addEventListener('change', (e) => {{const s = document.getElementById('min-prob-positive'); s.disabled = !e.target.checked; activeCriteria.minProbPositive = e.target.checked ? parseFloat(s.value) : null; document.getElementById('prob-value').textContent = e.target.checked ? activeCriteria.minProbPositive.toFixed(0) + '%' : 'Désactivé';}});
        document.getElementById('min-prob-positive').addEventListener('input', (e) => {{activeCriteria.minProbPositive = parseFloat(e.target.value); document.getElementById('prob-value').textContent = activeCriteria.minProbPositive.toFixed(0) + '%';}});
        
        function resetCriteria() {{activeCriteria = {{maxRuin: 10.0, minReturnDD: null, minProbPositive: null}}; document.getElementById('max-ruin').value = 10; document.getElementById('ruin-value').textContent = '10.0'; document.getElementById('enable-returndd').checked = false; document.getElementById('min-return-dd').disabled = true; document.getElementById('returndd-value').textContent = 'Désactivé'; document.getElementById('enable-prob').checked = false; document.getElementById('min-prob-positive').disabled = true; document.getElementById('prob-value').textContent = 'Désactivé'; recalculateAll();}}
        function setKevinDavey() {{activeCriteria = {{maxRuin: 10.0, minReturnDD: 2.0, minProbPositive: 80.0}}; document.getElementById('max-ruin').value = 10; document.getElementById('ruin-value').textContent = '10.0'; document.getElementById('enable-returndd').checked = true; document.getElementById('min-return-dd').disabled = false; document.getElementById('min-return-dd').value = 2.0; document.getElementById('returndd-value').textContent = '2.0'; document.getElementById('enable-prob').checked = true; document.getElementById('min-prob-positive').disabled = false; document.getElementById('min-prob-positive').value = 80; document.getElementById('prob-value').textContent = '80%'; recalculateAll();}}
        
        function applyDisplayFilters() {{const symbol = document.getElementById('filter-symbol').value; const status = document.getElementById('filter-status').value; const minTrades = parseInt(document.getElementById('filter-min-trades').value) || 0; const rows = document.querySelectorAll('#table-body tr'); let count = 0; rows.forEach(row => {{const match = (!symbol || row.getAttribute('data-symbol') === symbol) && (!status || row.getAttribute('data-status') === status) && (parseInt(row.querySelectorAll('td')[4].textContent.replace(/,/g, '')) >= minTrades); row.style.display = match ? '' : 'none'; if (match) count++;}});document.getElementById('visible-count').textContent = count;}}
        function resetDisplayFilters() {{document.getElementById('filter-symbol').value = ''; document.getElementById('filter-status').value = ''; document.getElementById('filter-min-trades').value = '20'; applyDisplayFilters();}}
        
        document.querySelectorAll('th[data-sort]').forEach(th => {{th.addEventListener('click', () => {{const column = th.getAttribute('data-sort'); const direction = th.classList.contains('sorted-asc') ? 'desc' : 'asc'; document.querySelectorAll('th[data-sort]').forEach(h => h.classList.remove('sorted-asc', 'sorted-desc')); th.classList.add(`sorted-${{direction}}`); const tbody = document.getElementById('table-body'); const rows = Array.from(tbody.querySelectorAll('tr')); const map = {{strategy: 0, symbol: 1, status: 2, capital: 3, trades: 4, pnl: 5, winrate: 6, pf: 7, ruin: 8, ratio: 9, prob: 10}}; rows.sort((a, b) => {{const aVal = a.querySelectorAll('td')[map[column]]?.textContent || ''; const bVal = b.querySelectorAll('td')[map[column]]?.textContent || ''; const aNum = parseFloat(aVal.replace(/[^0-9.-]/g, '')) || 0; const bNum = parseFloat(bVal.replace(/[^0-9.-]/g, '')) || 0; if (column === 'strategy' || column === 'symbol' || column === 'status') return direction === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal); return direction === 'asc' ? aNum - bNum : bNum - aNum;}}); rows.forEach(row => tbody.appendChild(row));}});}});
        
        window.addEventListener('load', () => {{console.log('Loaded:', Object.keys(strategiesDetailed).length, 'strategies'); recalculateAll();}});
    </script>
</body>
</html>
"""
'''

# Écrire le nouveau fichier
new_content = individual_part + summary_template

with open(src_file, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"   ✓ {len(new_content)} caractères écrits")

print("\n" + "=" * 80)
print("✅ RESTAURATION TERMINÉE")
print("=" * 80)
print("\nLancez maintenant:")
print("  cd C:\\TradeData\\V2")
print("  python test_generation_complete.py")
