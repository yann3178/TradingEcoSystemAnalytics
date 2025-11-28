"""
Générateur de Rapports HTML
============================
Génération des rapports individuels et du dashboard pour les analyses IA.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


# =============================================================================
# UTILITAIRES HTML
# =============================================================================

def html_escape(text: str) -> str:
    """Échappe les caractères HTML."""
    if not text:
        return ""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def format_text_for_html(text: str) -> str:
    """
    Convertit le texte formaté (markdown-like) en HTML.
    
    Supporte:
        - **bold** -> <strong>
        - \\n -> line breaks
        - • bullet points -> <ul>/<li>
        - 1. numbered lists -> <ol>/<li>
    """
    if not text or text in ("N/A", "None"):
        return text or ""
    
    # Escape HTML d'abord
    text = html_escape(text)
    
    # Convertir **bold**
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    
    # Traiter les lignes
    lines = text.split('\\n')
    html_lines = []
    in_ul = False
    in_ol = False
    
    for line in lines:
        stripped = line.strip()
        
        # Bullet point
        if stripped.startswith('•'):
            if not in_ul:
                if in_ol:
                    html_lines.append('</ol>')
                    in_ol = False
                html_lines.append('<ul class="analysis-list">')
                in_ul = True
            content = stripped[1:].strip()
            html_lines.append(f'<li>{content}</li>')
        
        # Numbered list
        elif re.match(r'^\d+\.', stripped):
            if not in_ol:
                if in_ul:
                    html_lines.append('</ul>')
                    in_ul = False
                html_lines.append('<ol class="analysis-list">')
                in_ol = True
            content = re.sub(r'^\d+\.\s*', '', stripped)
            html_lines.append(f'<li>{content}</li>')
        
        # Normal text
        else:
            if in_ul:
                html_lines.append('</ul>')
                in_ul = False
            if in_ol:
                html_lines.append('</ol>')
                in_ol = False
            
            if stripped:
                html_lines.append(f'<p>{stripped}</p>')
    
    # Fermer les listes ouvertes
    if in_ul:
        html_lines.append('</ul>')
    if in_ol:
        html_lines.append('</ol>')
    
    return ''.join(html_lines)


def get_score_class(score) -> str:
    """Retourne la classe CSS selon le score."""
    try:
        score = float(score)
        if score >= 7:
            return "score-high"
        elif score >= 4:
            return "score-medium"
        else:
            return "score-low"
    except (ValueError, TypeError):
        return ""


def get_type_color(strategy_type: str) -> str:
    """Retourne la couleur selon le type de stratégie."""
    colors = {
        'BREAKOUT': '#3498db',
        'MEAN_REVERSION': '#9b59b6',
        'TREND_FOLLOWING': '#27ae60',
        'PATTERN': '#e67e22',
        'VOLATILITY': '#e74c3c',
        'SEASONAL': '#f39c12',
        'MOMENTUM': '#1abc9c',
        'OTHER': '#95a5a6',
    }
    return colors.get(strategy_type.upper(), '#7f8c8d')


# =============================================================================
# GÉNÉRATEUR DE RAPPORTS
# =============================================================================

class HTMLReportGenerator:
    """Génère les rapports HTML pour les analyses de stratégies."""
    
    # CSS commun pour tous les rapports
    COMMON_CSS = """
    <style>
        :root {
            --primary: #3498db;
            --success: #27ae60;
            --warning: #f39c12;
            --danger: #e74c3c;
            --dark: #2c3e50;
            --light: #ecf0f1;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .back-link {
            display: inline-block;
            margin-bottom: 20px;
            color: var(--primary);
            text-decoration: none;
            font-weight: 500;
        }
        
        .back-link:hover {
            text-decoration: underline;
        }
        
        h1 {
            color: var(--dark);
            border-bottom: 3px solid var(--primary);
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        
        h2 {
            color: #34495e;
            margin-top: 30px;
            margin-bottom: 15px;
            border-left: 4px solid var(--primary);
            padding-left: 15px;
        }
        
        .header-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .info-box {
            background: var(--light);
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid var(--primary);
        }
        
        .info-box strong {
            display: block;
            color: var(--dark);
            margin-bottom: 5px;
            font-size: 0.9em;
        }
        
        .badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 15px;
            color: white;
            font-size: 0.85em;
            font-weight: 500;
        }
        
        .badge-yes {
            background: var(--success);
        }
        
        .badge-no {
            background: #95a5a6;
        }
        
        .score {
            font-size: 1.5em;
            font-weight: bold;
        }
        
        .score-high {
            color: var(--success);
        }
        
        .score-medium {
            color: var(--warning);
        }
        
        .score-low {
            color: var(--danger);
        }
        
        .section {
            margin: 25px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        
        .analysis-list {
            margin: 10px 0 10px 20px;
        }
        
        .analysis-list li {
            margin: 8px 0;
        }
        
        .code-block {
            background: #282c34;
            color: #abb2bf;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.5;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        
        .patterns-list {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin: 10px 0;
        }
        
        .pattern-tag {
            background: var(--light);
            padding: 5px 10px;
            border-radius: 4px;
            font-family: monospace;
            font-size: 0.9em;
        }
        
        .links-section {
            margin-top: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 8px;
            color: white;
        }
        
        .links-section a {
            color: white;
            text-decoration: underline;
        }
        
        @media (max-width: 768px) {
            .header-grid {
                grid-template-columns: 1fr;
            }
            
            body {
                padding: 10px;
            }
            
            .container {
                padding: 15px;
            }
        }
    </style>
    """
    
    def __init__(self, output_dir: Path):
        """
        Initialise le générateur.
        
        Args:
            output_dir: Répertoire de sortie pour les HTML
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_strategy_report(
        self,
        analysis: Dict,
        strategy_code: str,
        mc_report_path: Optional[str] = None,
        correlation_path: Optional[str] = None,
    ) -> Path:
        """
        Génère le rapport HTML pour une stratégie.
        
        Args:
            analysis: Résultat de l'analyse IA
            strategy_code: Code source de la stratégie
            mc_report_path: Chemin vers le rapport Monte Carlo (optionnel)
            correlation_path: Chemin vers le dashboard corrélation (optionnel)
            
        Returns:
            Path du fichier HTML généré
        """
        name = analysis.get("strategy_name", "Unknown")
        stype = analysis.get("strategy_type", "OTHER")
        subtype = analysis.get("strategy_subtype", "")
        
        # Scores
        quality_score = analysis.get("quality_score", "N/A")
        complexity_score = analysis.get("complexity_score", "N/A")
        
        # Formatage des sections
        summary_html = format_text_for_html(analysis.get("summary", ""))
        entry_html = format_text_for_html(analysis.get("entry_conditions", ""))
        exit_html = format_text_for_html(analysis.get("exit_conditions", ""))
        quality_analysis_html = format_text_for_html(analysis.get("quality_analysis", ""))
        pattern_details_html = format_text_for_html(analysis.get("pattern_details", ""))
        
        # Patterns list
        patterns = analysis.get("function_patterns", [])
        if isinstance(patterns, str):
            patterns = [p.strip() for p in patterns.split(";") if p.strip()]
        
        patterns_html = '<div class="patterns-list">'
        for p in patterns:
            patterns_html += f'<span class="pattern-tag">{html_escape(p)}</span>'
        patterns_html += '</div>' if patterns else '<p>Aucun pattern identifié</p>'
        
        # Liens vers autres rapports
        links_html = ""
        if mc_report_path or correlation_path:
            links_html = '<div class="links-section"><h3>📊 Rapports Liés</h3><ul>'
            if mc_report_path:
                links_html += f'<li><a href="{mc_report_path}">📈 Simulation Monte Carlo</a></li>'
            if correlation_path:
                links_html += f'<li><a href="{correlation_path}">🔗 Analyse de Corrélation</a></li>'
            links_html += '</ul></div>'
        
        # Construire le HTML
        type_color = get_type_color(stype)
        quality_class = get_score_class(quality_score)
        complexity_class = get_score_class(complexity_score)
        
        exit_on_close = analysis.get("exit_on_close", "NO")
        eoc_class = "badge-yes" if exit_on_close.upper() == "YES" else "badge-no"
        
        time_exit = analysis.get("time_exit_condition", "NO")
        te_class = "badge-yes" if time_exit.upper() == "YES" else "badge-no"
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html_escape(name)} - Strategy Analysis</title>
    {self.COMMON_CSS}
</head>
<body>
    <div class="container">
        <a href="index.html" class="back-link">← Retour à la liste</a>
        
        <h1>📊 {html_escape(name)}</h1>
        
        <div class="header-grid">
            <div class="info-box">
                <strong>Type</strong>
                <span class="badge" style="background-color: {type_color}">{stype}</span>
            </div>
            <div class="info-box">
                <strong>Sous-type</strong>
                <span>{html_escape(subtype)}</span>
            </div>
            <div class="info-box">
                <strong>Score Qualité</strong>
                <span class="score {quality_class}">{quality_score}/10</span>
            </div>
            <div class="info-box">
                <strong>Score Complexité</strong>
                <span class="score {complexity_class}">{complexity_score}/10</span>
            </div>
        </div>
        
        <div class="section">
            <h2>📝 Résumé</h2>
            {summary_html}
        </div>
        
        <div class="section">
            <h2>🎯 Conditions d'Entrée</h2>
            {entry_html}
        </div>
        
        <div class="section">
            <h2>🚪 Conditions de Sortie</h2>
            {exit_html}
        </div>
        
        <div class="header-grid">
            <div class="info-box">
                <strong>Stop Loss</strong>
                {format_text_for_html(analysis.get('stop_loss_level', 'None'))}
            </div>
            <div class="info-box">
                <strong>Take Profit</strong>
                {format_text_for_html(analysis.get('take_profit_level', 'None'))}
            </div>
            <div class="info-box">
                <strong>Exit On Close</strong>
                <span class="badge {eoc_class}">{exit_on_close}</span>
            </div>
            <div class="info-box">
                <strong>Time Exit</strong>
                <span class="badge {te_class}">{time_exit}</span>
            </div>
        </div>
        
        <div class="section">
            <h2>🔧 Patterns & Fonctions</h2>
            {patterns_html}
            <p><strong>Nombre de patterns:</strong> {analysis.get('number_of_patterns', 'N/A')}</p>
        </div>
        
        {"<div class='section'><h2>🔍 Détails des Patterns</h2>" + pattern_details_html + "</div>" if pattern_details_html and pattern_details_html not in ('N/A', 'None', '') else ""}
        
        <div class="section">
            <h2>⭐ Analyse Qualité</h2>
            {quality_analysis_html}
        </div>
        
        {links_html}
        
        <h2>💻 Code Source</h2>
        <div class="code-block"><pre>{html_escape(strategy_code)}</pre></div>
        
        <p style="margin-top: 20px; color: #7f8c8d; font-size: 0.9em;">
            Généré le {datetime.now().strftime('%Y-%m-%d %H:%M')} | 
            Hash: {analysis.get('code_hash', 'N/A')[:12]}...
        </p>
    </div>
</body>
</html>"""
        
        # Sauvegarder
        filename = f"{name.replace(' ', '_').replace('/', '_')}.html"
        output_path = self.output_dir / filename
        output_path.write_text(html, encoding='utf-8')
        
        return output_path
    
    def generate_dashboard(
        self,
        results: List[Dict],
        output_filename: str = "index.html",
    ) -> Path:
        """
        Génère le dashboard principal listant toutes les stratégies.
        
        Args:
            results: Liste des résultats d'analyse
            output_filename: Nom du fichier de sortie
            
        Returns:
            Path du fichier HTML généré
        """
        # Trier par qualité décroissante
        sorted_results = sorted(
            results,
            key=lambda x: float(x.get('quality_score', 0)) if x.get('quality_score', 'N/A') != 'N/A' else 0,
            reverse=True
        )
        
        # Statistiques
        total = len(results)
        
        quality_scores = [
            float(r.get('quality_score', 0)) 
            for r in results 
            if r.get('quality_score', 'N/A') != 'N/A'
        ]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        # Distribution par type
        type_counts = {}
        for r in results:
            t = r.get('strategy_type', 'OTHER')
            type_counts[t] = type_counts.get(t, 0) + 1
        
        # Générer les cards
        cards_html = ""
        for r in sorted_results:
            name = r.get('strategy_name', 'Unknown')
            stype = r.get('strategy_type', 'OTHER')
            subtype = r.get('strategy_subtype', '')
            summary = r.get('summary', '')
            quality = r.get('quality_score', 'N/A')
            complexity = r.get('complexity_score', 'N/A')
            
            # Nettoyer le résumé
            summary_clean = re.sub(r'\\n+', ' ', summary)
            summary_clean = re.sub(r'\*\*([^*]+)\*\*', r'\1', summary_clean)
            summary_clean = re.sub(r'\s+', ' ', summary_clean).strip()
            if len(summary_clean) > 150:
                summary_clean = summary_clean[:147] + '...'
            
            html_file = f"{name.replace(' ', '_').replace('/', '_')}.html"
            type_color = get_type_color(stype)
            quality_class = get_score_class(quality)
            
            cards_html += f"""
            <div class="strategy-card" data-type="{stype.lower()}" data-quality="{quality}">
                <h3><a href="{html_file}">{html_escape(name)}</a></h3>
                <div class="card-badges">
                    <span class="badge" style="background-color: {type_color}">{stype}</span>
                    <span class="badge badge-subtype">{html_escape(subtype[:40])}</span>
                </div>
                <p class="card-summary">{html_escape(summary_clean)}</p>
                <div class="card-scores">
                    <span>Qualité: <strong class="{quality_class}">{quality}/10</strong></span>
                    <span>Complexité: <strong>{complexity}/10</strong></span>
                </div>
            </div>
            """
        
        # Générer la distribution par type
        type_dist_html = ""
        max_count = max(type_counts.values()) if type_counts else 1
        for t, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            pct = (count / max_count) * 100
            color = get_type_color(t)
            type_dist_html += f"""
            <div class="type-row">
                <span class="type-name">{t}</span>
                <div class="type-bar-container">
                    <div class="type-bar" style="width: {pct}%; background-color: {color}"></div>
                </div>
                <span class="type-count">{count}</span>
            </div>
            """
        
        # Type filter buttons
        type_buttons = '<button class="active" data-type="all">Tous ({total})</button>'
        for t, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            type_buttons += f'<button data-type="{t.lower()}">{t} ({count})</button>'
        
        html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Strategy Analysis Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{ max-width: 1400px; margin: 0 auto; }}
        
        .header {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }}
        
        h1 {{
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        
        .subtitle {{
            color: #7f8c8d;
            margin-bottom: 20px;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        
        .stat-box {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        
        .stat-box strong {{
            display: block;
            font-size: 2em;
            margin-bottom: 5px;
        }}
        
        .filters {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }}
        
        .search-box {{
            width: 100%;
            padding: 12px;
            font-size: 1em;
            border: 2px solid #ddd;
            border-radius: 5px;
            margin-bottom: 15px;
        }}
        
        .type-filter {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}
        
        .type-filter button {{
            padding: 8px 16px;
            border: 2px solid #667eea;
            background: white;
            color: #667eea;
            border-radius: 20px;
            cursor: pointer;
            font-weight: 500;
        }}
        
        .type-filter button:hover,
        .type-filter button.active {{
            background: #667eea;
            color: white;
        }}
        
        .content-wrapper {{
            display: grid;
            grid-template-columns: 280px 1fr;
            gap: 30px;
        }}
        
        .sidebar {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            height: fit-content;
            position: sticky;
            top: 20px;
        }}
        
        .sidebar h2 {{
            font-size: 1.2em;
            margin-bottom: 15px;
            color: #2c3e50;
        }}
        
        .type-row {{
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }}
        
        .type-name {{
            width: 100px;
            font-size: 0.85em;
        }}
        
        .type-bar-container {{
            flex: 1;
            height: 20px;
            background: #ecf0f1;
            border-radius: 10px;
            overflow: hidden;
            margin: 0 10px;
        }}
        
        .type-bar {{
            height: 100%;
        }}
        
        .type-count {{
            width: 30px;
            text-align: right;
            font-weight: bold;
        }}
        
        .strategies-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 20px;
        }}
        
        .strategy-card {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }}
        
        .strategy-card:hover {{
            transform: translateY(-5px);
        }}
        
        .strategy-card h3 {{
            margin-bottom: 10px;
        }}
        
        .strategy-card h3 a {{
            color: #2c3e50;
            text-decoration: none;
        }}
        
        .strategy-card h3 a:hover {{
            color: #667eea;
        }}
        
        .card-badges {{
            margin-bottom: 10px;
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.8em;
            color: white;
            margin-right: 5px;
        }}
        
        .badge-subtype {{
            background: #95a5a6;
        }}
        
        .card-summary {{
            color: #555;
            font-size: 0.9em;
            margin-bottom: 10px;
            min-height: 40px;
        }}
        
        .card-scores {{
            display: flex;
            justify-content: space-between;
            padding-top: 10px;
            border-top: 1px solid #eee;
            font-size: 0.9em;
        }}
        
        .score-high {{ color: #27ae60; }}
        .score-medium {{ color: #f39c12; }}
        .score-low {{ color: #e74c3c; }}
        
        @media (max-width: 1000px) {{
            .content-wrapper {{
                grid-template-columns: 1fr;
            }}
            .sidebar {{
                position: relative;
                top: 0;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI Strategy Analysis Dashboard</h1>
            <p class="subtitle">Analyse automatisée des stratégies de trading</p>
            
            <div class="stats">
                <div class="stat-box">
                    <strong>{total}</strong>
                    <span>Stratégies</span>
                </div>
                <div class="stat-box">
                    <strong>{avg_quality:.1f}/10</strong>
                    <span>Qualité Moyenne</span>
                </div>
                <div class="stat-box">
                    <strong>{len(type_counts)}</strong>
                    <span>Types</span>
                </div>
            </div>
        </div>
        
        <div class="filters">
            <input type="text" id="searchBox" class="search-box" placeholder="🔍 Rechercher une stratégie...">
            <div class="type-filter" id="typeFilter">
                {type_buttons}
            </div>
        </div>
        
        <div class="content-wrapper">
            <div class="sidebar">
                <h2>📊 Distribution par Type</h2>
                {type_dist_html}
            </div>
            
            <div class="strategies-grid" id="strategiesGrid">
                {cards_html}
            </div>
        </div>
    </div>
    
    <script>
        const searchBox = document.getElementById('searchBox');
        const typeFilter = document.getElementById('typeFilter');
        const grid = document.getElementById('strategiesGrid');
        let currentType = 'all';
        
        searchBox.addEventListener('input', filterCards);
        
        typeFilter.querySelectorAll('button').forEach(btn => {{
            btn.addEventListener('click', () => {{
                typeFilter.querySelectorAll('button').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentType = btn.dataset.type;
                filterCards();
            }});
        }});
        
        function filterCards() {{
            const search = searchBox.value.toLowerCase();
            const cards = grid.querySelectorAll('.strategy-card');
            
            cards.forEach(card => {{
                const text = card.textContent.toLowerCase();
                const type = card.dataset.type;
                
                const matchSearch = text.includes(search);
                const matchType = currentType === 'all' || type === currentType;
                
                card.style.display = matchSearch && matchType ? 'block' : 'none';
            }});
        }}
    </script>
</body>
</html>"""
        
        output_path = self.output_dir / output_filename
        output_path.write_text(html, encoding='utf-8')
        
        return output_path


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def generate_all_reports(
    results: List[Dict],
    strategy_codes: Dict[str, str],
    output_dir: Path,
) -> Dict[str, Path]:
    """
    Génère tous les rapports HTML.
    
    Args:
        results: Liste des résultats d'analyse
        strategy_codes: Dict {strategy_name: code_source}
        output_dir: Répertoire de sortie
        
    Returns:
        Dict des chemins générés
    """
    generator = HTMLReportGenerator(output_dir)
    generated = {}
    
    for result in results:
        name = result.get("strategy_name", "Unknown")
        code = strategy_codes.get(name, "// Code non disponible")
        
        try:
            path = generator.generate_strategy_report(result, code)
            generated[name] = path
        except Exception as e:
            print(f"❌ Erreur génération HTML pour {name}: {e}")
    
    # Dashboard
    dashboard_path = generator.generate_dashboard(results)
    generated["_dashboard"] = dashboard_path
    
    return generated


if __name__ == "__main__":
    # Test
    test_analysis = {
        "strategy_name": "Test Strategy",
        "strategy_type": "BREAKOUT",
        "strategy_subtype": "Channel Breakout",
        "summary": "This is a **test** strategy\\n• Point 1\\n• Point 2",
        "entry_conditions": "**LONG:**\\n• Buy when price breaks above channel",
        "exit_conditions": "**Stops:**\\n• Fixed stop at 50 points",
        "stop_loss_level": "SetStopLoss(**50**) = 50 in **currency**",
        "take_profit_level": "None",
        "exit_on_close": "YES",
        "time_exit_condition": "NO",
        "time_exit_details": "None",
        "function_patterns": ["ATR(10)", "HighestHigh(20)"],
        "pattern_details": "None",
        "number_of_patterns": "2",
        "complexity_score": "5",
        "quality_score": "7",
        "quality_analysis": "**STRENGTHS:**\\n• Clear entry logic\\n\\n**WEAKNESSES:**\\n• No profit target",
        "code_hash": "abc123def456",
    }
    
    test_code = """// Test Strategy
Input: Period(20);
Buy next bar at Highest(H, Period) stop;
SetStopLoss(50);
SetExitOnClose;
"""
    
    from pathlib import Path
    output = Path(r"C:\TradeData\V2\outputs\test_html")
    output.mkdir(parents=True, exist_ok=True)
    
    gen = HTMLReportGenerator(output)
    report_path = gen.generate_strategy_report(test_analysis, test_code)
    print(f"✅ Rapport généré: {report_path}")
    
    # Dashboard avec plusieurs résultats
    results = [test_analysis]
    dash_path = gen.generate_dashboard(results)
    print(f"✅ Dashboard généré: {dash_path}")
