#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Restaure la version simple qui fonctionnait du HTML generator
(SANS la mise à jour des graphiques qui a tout cassé)
"""
import shutil
from pathlib import Path

# Backup d'abord
src_dir = Path("C:/TradeData/V2/src/monte_carlo")
backup_dir = Path("C:/TradeData/V2/backups")
backup_dir.mkdir(exist_ok=True)

print("=" * 80)
print("RESTAURATION VERSION SIMPLE (sans graphiques dynamiques)")
print("=" * 80)
print()

# Sauvegarder la version actuelle
print("📦 Sauvegarde de la version actuelle...")
shutil.copy2(
    src_dir / "html_templates.py",
    backup_dir / "html_templates.py.broken"
)
shutil.copy2(
    src_dir / "monte_carlo_html_generator.py",
    backup_dir / "monte_carlo_html_generator.py.broken"
)
print("   ✓ Sauvegardé dans backups/")

# Le monte_carlo_html_generator.py est OK, on garde juste les corrections
print("\n📝 monte_carlo_html_generator.py est déjà correct")

# Pour html_templates.py, on va juste retirer la partie updateCharts
print("\n🔧 Correction de html_templates.py...")
print("   Suppression de la fonction updateCharts() et de l'initialisation charts")

template_file = src_dir / "html_templates.py"
with open(template_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Trouver et supprimer la section problématique
# On va chercher "let charts =" jusqu'à "function initCharts()"
# et la remplacer par du code simple sans les graphiques

# La stratégie : on garde tout AVANT "let charts" et tout APRÈS "window.addEventListener('load'"
# et on met notre JavaScript simple au milieu

before_marker = "        // Data"
after_marker = "        // Initialisation au chargement"

if before_marker in content and after_marker in content:
    before_part = content.split(before_marker)[0]
    after_part = content.split(after_marker)[1]
    
    # Notre JavaScript simple (sans graphiques dynamiques)
    simple_js = """        // Data
        const strategiesData = {strategies_json};
        const strategiesDetailed = {strategies_detailed_json};
        
        // Chart.js defaults
        Chart.defaults.color = '#a0a0a0';
        Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.1)';
        
        // Status Pie Chart (statique)
        new Chart(document.getElementById('statusChart'), {{
            type: 'doughnut',
            data: {{
                labels: ['✓ OK', '⚠ WARNING', '✗ HIGH RISK'],
                datasets: [{{
                    data: [{ok_count}, {warning_count}, {high_risk_count}],
                    backgroundColor: ['#00d4aa', '#ffe66d', '#ff6b6b']
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ position: 'bottom' }} }}
            }}
        }});
        
        // Scatter Chart (statique)
        new Chart(document.getElementById('scatterChart'), {{
            type: 'scatter',
            data: {{
                datasets: [{{
                    label: 'Stratégies',
                    data: strategiesData.map(s => ({{
                        x: s.ruin_pct,
                        y: s.return_dd_ratio > 100 ? 100 : s.return_dd_ratio,
                        strategy: s.strategy_name,
                        status: s.status
                    }})),
                    backgroundColor: strategiesData.map(s => 
                        s.status === 'OK' ? '#00d4aa' : (s.status === 'WARNING' ? '#ffe66d' : '#ff6b6b')
                    )
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return context.raw.strategy + ' (' + context.raw.status + ')';
                            }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{ title: {{ display: true, text: 'Risque de Ruine (%)' }} }},
                    y: {{ title: {{ display: true, text: 'Return/DD Ratio' }}, max: 10 }}
                }}
            }}
        }});
        
        // Top P&L Chart (statique)
        const topPnl = strategiesData.sort((a, b) => b.total_pnl - a.total_pnl).slice(0, 10);
        new Chart(document.getElementById('topPnlChart'), {{
            type: 'bar',
            data: {{
                labels: topPnl.map(s => s.symbol + '_' + s.strategy_name.substring(0, 15)),
                datasets: [{{
                    label: 'P&L Total',
                    data: topPnl.map(s => s.total_pnl),
                    backgroundColor: '#4ecdc4'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {{ legend: {{ display: false }} }}
            }}
        }});
        
        // Top Return/DD Chart (statique)
        const topRatio = strategiesData
            .filter(s => s.return_dd_ratio < 100)
            .sort((a, b) => b.return_dd_ratio - a.return_dd_ratio)
            .slice(0, 10);
        new Chart(document.getElementById('topRatioChart'), {{
            type: 'bar',
            data: {{
                labels: topRatio.map(s => s.symbol + '_' + s.strategy_name.substring(0, 15)),
                datasets: [{{
                    label: 'Return/DD',
                    data: topRatio.map(s => s.return_dd_ratio),
                    backgroundColor: topRatio.map(s => s.return_dd_ratio >= 2 ? '#00d4aa' : '#ffe66d')
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {{ legend: {{ display: false }} }}
            }}
        }});
        
        // RECALCUL DYNAMIQUE
        
        let activeCriteria = {{
            maxRuin: 10.0,
            minReturnDD: null,
            minProbPositive: null
        }};
        
        function findRecommendedCapital(strategyName) {{
            const strategy = strategiesDetailed[strategyName];
            if (!strategy || !strategy.levels) {{
                console.warn(`Strategy '${{strategyName}}' not found or has no levels`);
                return {{ capital: null, status: 'HIGH_RISK', metrics: {{}} }};
            }}
            
            const levels = strategy.levels.sort((a, b) => a.capital - b.capital);
            
            for (let level of levels) {{
                const ruinOK = level.ruin_pct <= activeCriteria.maxRuin;
                const returnDDOK = activeCriteria.minReturnDD === null || level.return_dd >= activeCriteria.minReturnDD;
                const probOK = activeCriteria.minProbPositive === null || level.prob_positive >= activeCriteria.minProbPositive;
                
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
                
                if (ruinOK && (!returnDDOK || !probOK)) {{
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
            
            return {{ capital: null, status: 'HIGH_RISK', metrics: {{}} }};
        }}
        
        function updateTableRow(strategyName, result) {{
            const row = document.querySelector(`tr[data-strategy="${{strategyName}}"]`);
            if (!row) return;
            
            const cells = row.querySelectorAll('td');
            
            const statusBadge = cells[2].querySelector('.status-badge');
            statusBadge.className = 'status-badge';
            if (result.status === 'OK') {{
                statusBadge.classList.add('status-ok');
                statusBadge.textContent = '✓ OK';
            }} else if (result.status === 'WARNING') {{
                statusBadge.classList.add('status-warning');
                statusBadge.textContent = '⚠ WARNING';
            }} else {{
                statusBadge.classList.add('status-danger');
                statusBadge.textContent = '✗ HIGH RISK';
            }}
            
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
            console.log('Recalculating with criteria:', activeCriteria);
            
            let okCount = 0;
            let warningCount = 0;
            let highRiskCount = 0;
            let withCapitalCount = 0;
            let capitals = [];
            
            for (let strategyName in strategiesDetailed) {{
                const result = findRecommendedCapital(strategyName);
                updateTableRow(strategyName, result);
                
                if (result.status === 'OK') okCount++;
                else if (result.status === 'WARNING') warningCount++;
                else highRiskCount++;
                
                if (result.capital) {{
                    withCapitalCount++;
                    capitals.push(result.capital);
                }}
            }}
            
            document.getElementById('live-ok-count').textContent = okCount;
            document.getElementById('live-warning-count').textContent = warningCount;
            document.getElementById('live-highrisk-count').textContent = highRiskCount;
            document.getElementById('live-with-capital-count').textContent = withCapitalCount;
            
            if (capitals.length > 0) {{
                const avgCapital = capitals.reduce((a, b) => a + b, 0) / capitals.length;
                const medianCapital = capitals.sort((a, b) => a - b)[Math.floor(capitals.length / 2)];
                
                document.getElementById('live-avg-capital').textContent = '$$' + Math.round(avgCapital).toLocaleString();
                document.getElementById('live-median-capital').textContent = '$$' + medianCapital.toLocaleString();
            }}
            
            console.log('Recalculation complete:', {{ okCount, warningCount, highRiskCount, withCapitalCount }});
        }}
        
        document.getElementById('max-ruin').addEventListener('input', (e) => {{
            activeCriteria.maxRuin = parseFloat(e.target.value);
            document.getElementById('ruin-value').textContent = activeCriteria.maxRuin.toFixed(1);
        }});
        
        document.getElementById('enable-returndd').addEventListener('change', (e) => {{
            const slider = document.getElementById('min-return-dd');
            slider.disabled = !e.target.checked;
            if (e.target.checked) {{
                activeCriteria.minReturnDD = parseFloat(slider.value);
                document.getElementById('returndd-value').textContent = activeCriteria.minReturnDD.toFixed(1);
            }} else {{
                activeCriteria.minReturnDD = null;
                document.getElementById('returndd-value').textContent = 'Désactivé';
            }}
        }});
        
        document.getElementById('min-return-dd').addEventListener('input', (e) => {{
            activeCriteria.minReturnDD = parseFloat(e.target.value);
            document.getElementById('returndd-value').textContent = activeCriteria.minReturnDD.toFixed(1);
        }});
        
        document.getElementById('enable-prob').addEventListener('change', (e) => {{
            const slider = document.getElementById('min-prob-positive');
            slider.disabled = !e.target.checked;
            if (e.target.checked) {{
                activeCriteria.minProbPositive = parseFloat(slider.value);
                document.getElementById('prob-value').textContent = activeCriteria.minProbPositive.toFixed(0) + '%';
            }} else {{
                activeCriteria.minProbPositive = null;
                document.getElementById('prob-value').textContent = 'Désactivé';
            }}
        }});
        
        document.getElementById('min-prob-positive').addEventListener('input', (e) => {{
            activeCriteria.minProbPositive = parseFloat(e.target.value);
            document.getElementById('prob-value').textContent = activeCriteria.minProbPositive.toFixed(0) + '%';
        }});
        
        function resetCriteria() {{
            activeCriteria = {{ maxRuin: 10.0, minReturnDD: null, minProbPositive: null }};
            document.getElementById('max-ruin').value = 10;
            document.getElementById('ruin-value').textContent = '10.0';
            document.getElementById('enable-returndd').checked = false;
            document.getElementById('min-return-dd').disabled = true;
            document.getElementById('returndd-value').textContent = 'Désactivé';
            document.getElementById('enable-prob').checked = false;
            document.getElementById('min-prob-positive').disabled = true;
            document.getElementById('prob-value').textContent = 'Désactivé';
            recalculateAll();
        }}
        
        function setKevinDavey() {{
            activeCriteria = {{ maxRuin: 10.0, minReturnDD: 2.0, minProbPositive: 80.0 }};
            document.getElementById('max-ruin').value = 10;
            document.getElementById('ruin-value').textContent = '10.0';
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
        
        function applyDisplayFilters() {{
            const symbol = document.getElementById('filter-symbol').value;
            const status = document.getElementById('filter-status').value;
            const minTrades = parseInt(document.getElementById('filter-min-trades').value) || 0;
            
            const rows = document.querySelectorAll('#table-body tr');
            let visibleCount = 0;
            
            rows.forEach(row => {{
                const rowSymbol = row.getAttribute('data-symbol');
                const rowStatus = row.getAttribute('data-status');
                const rowTrades = parseInt(row.querySelectorAll('td')[4].textContent.replace(/,/g, ''));
                
                const symbolMatch = !symbol || rowSymbol === symbol;
                const statusMatch = !status || rowStatus === status;
                const tradesMatch = rowTrades >= minTrades;
                
                if (symbolMatch && statusMatch && tradesMatch) {{
                    row.style.display = '';
                    visibleCount++;
                }} else {{
                    row.style.display = 'none';
                }}
            }});
            
            document.getElementById('visible-count').textContent = visibleCount;
        }}
        
        function resetDisplayFilters() {{
            document.getElementById('filter-symbol').value = '';
            document.getElementById('filter-status').value = '';
            document.getElementById('filter-min-trades').value = '20';
            applyDisplayFilters();
        }}
        
        document.querySelectorAll('th[data-sort]').forEach(th => {{
            th.addEventListener('click', () => {{
                const column = th.getAttribute('data-sort');
                const currentOrder = th.classList.contains('sorted-asc') ? 'desc' : 'asc';
                
                document.querySelectorAll('th[data-sort]').forEach(h => {{
                    h.classList.remove('sorted-asc', 'sorted-desc');
                }});
                th.classList.add(`sorted-${{currentOrder}}`);
                
                sortTable(column, currentOrder);
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
        
        // Initialisation au chargement"""
    
    fixed_content = before_part + simple_js + after_part
    
    with open(template_file, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print("   ✓ Fichier corrigé!")
else:
    print("   ⚠️  Impossible de trouver les marqueurs - le fichier a peut-être été trop modifié")
    print("   Essayez de restaurer depuis une sauvegarde")

print("\n" + "=" * 80)
print("✅ RESTAURATION TERMINÉE")
print("=" * 80)
print("\nMaintenant lancez:")
print("  cd C:\\TradeData\\V2")
print("  python test_generation_complete.py")
print("\nOu directement:")
print("  cd C:\\TradeData\\V2\\src\\monte_carlo")
print("  python monte_carlo_html_generator.py")
