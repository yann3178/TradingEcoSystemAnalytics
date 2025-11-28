"""
CSS Styles pour les rapports HTML enrichis
==========================================
"""

KPI_DASHBOARD_CSS = '''
<style>
    /* === KPI DASHBOARD === */
    .kpi-dashboard {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 12px;
        padding: 25px;
        margin: 25px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .kpi-dashboard h2 {
        color: #2c3e50;
        margin-bottom: 20px;
        border-left: 4px solid #3498db;
        padding-left: 15px;
    }
    
    .kpi-dashboard h3 {
        color: #34495e;
        margin: 20px 0 15px 0;
        font-size: 1.1em;
    }
    
    .kpi-header-row {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-bottom: 20px;
    }
    
    .kpi-chip {
        background: white;
        border-radius: 20px;
        padding: 8px 15px;
        display: flex;
        align-items: center;
        gap: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .chip-label { color: #7f8c8d; font-size: 0.85em; }
    .chip-value { font-weight: 600; color: #2c3e50; }
    
    .kpi-main-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 15px;
        margin-bottom: 20px;
    }
    
    .kpi-secondary-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 12px;
        margin-bottom: 20px;
    }
    
    .kpi-card {
        background: white;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    }
    
    .kpi-card.main { padding: 20px; }
    .kpi-card.main .kpi-value { font-size: 1.8em; }
    
    .kpi-title {
        color: #7f8c8d;
        font-size: 0.85em;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .kpi-value {
        font-size: 1.4em;
        font-weight: 700;
        color: #2c3e50;
    }
    
    .kpi-value.positive { color: #27ae60; }
    .kpi-value.negative { color: #e74c3c; }
    .kpi-value.neutral { color: #7f8c8d; }
    .kpi-subtitle { font-size: 0.8em; color: #95a5a6; margin-top: 5px; }
    
    /* === IS/OOS SECTION === */
    .isoos-section {
        background: white;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
    }
    
    .isoos-info {
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
        margin-bottom: 20px;
    }
    
    .isoos-badge {
        padding: 12px 20px;
        border-radius: 8px;
        display: flex;
        flex-direction: column;
        gap: 5px;
    }
    
    .isoos-badge.is {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        color: white;
    }
    
    .isoos-badge.oos {
        background: linear-gradient(135deg, #27ae60 0%, #219a52 100%);
        color: white;
    }
    
    .badge-label { font-size: 0.8em; opacity: 0.9; }
    .badge-value { font-weight: 600; }
    .badge-duration { font-size: 0.85em; opacity: 0.9; }
    
    .isoos-metrics {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 12px;
    }
    
    /* === PERIOD TABLE === */
    .period-section {
        background: white;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
        overflow-x: auto;
    }
    
    .period-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.95em;
    }
    
    .period-table th {
        background: #f8f9fa;
        padding: 12px;
        text-align: left;
        font-weight: 600;
        color: #2c3e50;
        border-bottom: 2px solid #e9ecef;
    }
    
    .period-table td {
        padding: 12px;
        border-bottom: 1px solid #e9ecef;
    }
    
    .period-table tr:hover { background: #f8f9fa; }
    .period-table .positive { color: #27ae60; font-weight: 500; }
    .period-table .negative { color: #e74c3c; font-weight: 500; }
    
    /* === EQUITY CURVE === */
    .equity-section {
        background: white;
        border-radius: 12px;
        padding: 25px;
        margin: 25px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .equity-section h2 {
        color: #2c3e50;
        margin-bottom: 15px;
        border-left: 4px solid #27ae60;
        padding-left: 15px;
    }
    
    .equity-legend {
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
        margin-bottom: 15px;
        padding: 10px;
        background: #f8f9fa;
        border-radius: 8px;
    }
    
    .legend-item {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.9em;
    }
    
    .legend-item .legend-color {
        width: 20px;
        height: 4px;
        border-radius: 2px;
    }
    
    .legend-item.is .legend-color { background: #3498db; }
    .legend-item.oos .legend-color { background: #27ae60; }
    .legend-item.separator { color: #e74c3c; font-weight: 500; }
    
    .chart-container {
        position: relative;
        height: 400px;
        width: 100%;
    }
    
    .equity-source {
        margin-top: 10px;
        text-align: right;
        color: #95a5a6;
    }
    
    .no-data {
        background: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        color: #856404;
    }
    
    /* === RESPONSIVE === */
    @media (max-width: 768px) {
        .kpi-main-grid { grid-template-columns: repeat(2, 1fr); }
        .kpi-secondary-grid { grid-template-columns: repeat(2, 1fr); }
        .chart-container { height: 300px; }
    }
</style>
'''
