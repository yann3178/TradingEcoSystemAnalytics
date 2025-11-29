"""
Générateur de pages de corrélation individuelles.

Utilise les résultats de CorrelationAnalyzer pour créer
une page HTML par stratégie avec :
- Profil de corrélation (scores LT/CT, moyennes, max)
- Top N stratégies les plus corrélées
- Top N stratégies les moins corrélées (opportunités de diversification)
- Distribution des corrélations
- Alertes et recommandations

Architecture:
    CorrelationAnalyzer (calculs) -> CorrelationPagesGenerator (HTML)
"""

from pathlib import Path
from typing import Dict, Any, List
import json
import numpy as np
from datetime import datetime


class CorrelationPagesGenerator:
    """
    Génère des pages HTML individuelles pour chaque stratégie.
    
    Utilisation:
        analyzer = CorrelationAnalyzer(data)
        analyzer.run()
        
        generator = CorrelationPagesGenerator(analyzer)
        stats = generator.generate_all(output_dir)
    """
    
    def __init__(self, analyzer):
        """
        Initialise le générateur.
        
        Args:
            analyzer: Instance de CorrelationAnalyzer (doit avoir exécuté run())
        """
        if analyzer.scores is None:
            raise ValueError("L'analyzer doit avoir exécuté run() avant la génération")
        
        self.analyzer = analyzer
        self.template_path = Path(__file__).parent.parent / 'templates' / 'correlation_page.html'
    
    def generate_all(
        self,
        output_dir: Path,
        top_n: int = 15,
        verbose: bool = True
    ) -> Dict[str, int]:
        """
        Génère toutes les pages individuelles.
        
        Args:
            output_dir: Répertoire de sortie pour les pages HTML
            top_n: Nombre de stratégies dans les listes top/bottom
            verbose: Afficher la progression
            
        Returns:
            Dict avec statistiques : {'generated': int, 'errors': int, 'total': int}
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if verbose:
            print("\n" + "=" * 70)
            print("📄 GÉNÉRATION DES PAGES DE CORRÉLATION INDIVIDUELLES")
            print("=" * 70)
        
        strategies = self.analyzer.scores['Strategy'].tolist()
        
        if verbose:
            print(f"\n📊 {len(strategies)} pages à générer...")
        
        generated = 0
        errors = 0
        
        for i, strategy in enumerate(strategies):
            if verbose and (i + 1) % 50 == 0:
                print(f"   → {i + 1}/{len(strategies)} pages générées...")
            
            try:
                # Calculer le profil de corrélation
                profile = self._calculate_profile(strategy, top_n)
                
                # Générer la page HTML
                html_path = output_dir / f"{self._sanitize_filename(strategy)}_correlation.html"
                self._generate_html(profile, html_path)
                
                generated += 1
                
            except Exception as e:
                if verbose:
                    print(f"   ⚠️  Erreur pour {strategy}: {e}")
                errors += 1
        
        if verbose:
            print(f"\n✅ {generated} pages générées avec succès")
            if errors > 0:
                print(f"⚠️  {errors} erreurs rencontrées")
            print(f"📁 Emplacement: {output_dir}")
        
        return {
            'generated': generated,
            'errors': errors,
            'total': len(strategies)
        }
    
    def _calculate_profile(self, strategy: str, top_n: int) -> Dict[str, Any]:
        """
        Calcule le profil de corrélation détaillé d'une stratégie.
        
        Args:
            strategy: Nom de la stratégie (format: StrategyName_Symbol)
            top_n: Nombre de stratégies dans les tops
            
        Returns:
            Dict avec toutes les données nécessaires au template
        """
        # Récupérer les données de base depuis self.analyzer.scores
        strategy_row = self.analyzer.scores[
            self.analyzer.scores['Strategy'] == strategy
        ].iloc[0]
        
        # Extraire nom et symbole (compatible avec différents formats de CSV)
        if 'Strategy_Name' in strategy_row and 'Symbol' in strategy_row:
            strategy_name = strategy_row['Strategy_Name']
            symbol = strategy_row['Symbol']
        else:
            # Fallback: parser le Strategy ID
            parts = strategy.rsplit('_', 1)
            if len(parts) == 2:
                strategy_name, symbol = parts
            else:
                strategy_name, symbol = strategy, 'Unknown'
        
        # Récupérer les corrélations LT et CT pour cette stratégie
        lt_corrs = self.analyzer.corr_matrix_lt.loc[strategy].drop(strategy, errors='ignore').dropna()
        ct_corrs = self.analyzer.corr_matrix_ct.loc[strategy].drop(strategy, errors='ignore').dropna()
        
        # Fusionner toutes les stratégies corrélées (LT + CT)
        all_strats = set(lt_corrs.index) | set(ct_corrs.index)
        correlations_detail = []
        
        for s in all_strats:
            c_lt = lt_corrs.get(s, np.nan)
            c_ct = ct_corrs.get(s, np.nan)
            
            # Calculer le delta (évolution CT - LT)
            delta = c_ct - c_lt if not (np.isnan(c_lt) or np.isnan(c_ct)) else np.nan
            
            # Max absolu pour tri
            max_abs = max(
                abs(c_lt) if not np.isnan(c_lt) else 0,
                abs(c_ct) if not np.isnan(c_ct) else 0
            )
            
            # Extraire symbole de la stratégie corrélée
            # Essayer de récupérer depuis le DataFrame d'abord
            try:
                s_row = self.analyzer.scores[self.analyzer.scores['Strategy'] == s].iloc[0]
                s_symbol = s_row.get('Symbol', 'Unknown')
            except:
                # Fallback: parser
                s_parts = s.rsplit('_', 1)
                s_symbol = s_parts[1] if len(s_parts) == 2 else 'Unknown'
            
            correlations_detail.append({
                'strategy': s,
                'symbol': s_symbol,
                'corr_lt': round(float(c_lt), 3) if not np.isnan(c_lt) else None,
                'corr_ct': round(float(c_ct), 3) if not np.isnan(c_ct) else None,
                'delta': round(float(delta), 3) if not np.isnan(delta) else None,
                'max_abs': max_abs
            })
        
        # Trier par corrélation max absolue (décroissant)
        correlations_detail.sort(key=lambda x: x['max_abs'], reverse=True)
        
        # Top corrélées (les plus fortes corrélations)
        most_correlated = correlations_detail[:top_n]
        
        # Moins corrélées (opportunités de diversification)
        least_correlated = sorted(
            [c for c in correlations_detail if c['max_abs'] > 0],
            key=lambda x: x['max_abs']
        )[:top_n]
        
        # Distribution par bucket
        all_corrs = list(lt_corrs) + list(ct_corrs)
        all_corrs = [c for c in all_corrs if not np.isnan(c)]
        distribution = {
            'very_negative': sum(1 for c in all_corrs if c <= -0.7),
            'negative': sum(1 for c in all_corrs if -0.7 < c <= -0.3),
            'neutral': sum(1 for c in all_corrs if -0.3 < c < 0.3),
            'positive': sum(1 for c in all_corrs if 0.3 <= c < 0.7),
            'very_positive': sum(1 for c in all_corrs if c >= 0.7)
        }
        
        # Générer les alertes
        alerts = self._generate_alerts(strategy_row, most_correlated)
        
        # Gérer les noms de colonnes variables (Delta_Corr vs Delta_Avg, etc.)
        delta_avg = strategy_row.get('Delta_Corr', strategy_row.get('Delta_Avg', 0))
        max_corr_lt_with = strategy_row.get('Max_Corr_LT_With', 'N/A')
        max_corr_ct_with = strategy_row.get('Max_Corr_CT_With', 'N/A')
        
        # Générer Status_Emoji si absent
        status = strategy_row['Status']
        status_emoji = self._get_status_emoji(status)
        
        return {
            'strategy_id': strategy,
            'strategy_name': strategy_name,
            'symbol': symbol,
            
            'score_davey': strategy_row['Score_Davey'],
            'status': status,
            'status_emoji': status_emoji,
            
            'n_corr_lt': int(strategy_row['N_Corr_LT']),
            'n_corr_ct': int(strategy_row['N_Corr_CT']),
            'avg_corr_lt': strategy_row['Avg_Corr_LT'],
            'avg_corr_ct': strategy_row['Avg_Corr_CT'],
            'delta_avg': delta_avg,
            'max_corr_lt': strategy_row['Max_Corr_LT'],
            'max_corr_lt_with': max_corr_lt_with,
            'max_corr_ct': strategy_row['Max_Corr_CT'],
            'max_corr_ct_with': max_corr_ct_with,
            
            'most_correlated': most_correlated,
            'least_correlated': least_correlated,
            'distribution': distribution,
            'alerts': alerts,
            
            'config': {
                'threshold': self.analyzer.correlation_threshold,
                'start_year': self.analyzer.start_year_longterm,
                'recent_months': self.analyzer.recent_months
            }
        }
    
    @staticmethod
    def _get_status_emoji(status: str) -> str:
        """Retourne l'emoji correspondant au status."""
        emoji_map = {
            'Diversifiant': '🟢',
            'Modéré': '🟡',
            'Corrélé': '🟠',
            'Très corrélé': '🔴'
        }
        return emoji_map.get(status, '⚪')
    
    def _generate_alerts(
        self,
        strategy_row,
        most_correlated: List[Dict]
    ) -> List[Dict[str, str]]:
        """
        Génère les alertes pour une stratégie.
        
        Args:
            strategy_row: Ligne du DataFrame scores pour cette stratégie
            most_correlated: Liste des stratégies les plus corrélées
            
        Returns:
            Liste d'alertes avec type et message
        """
        alerts = []
        
        # Corrélation critique
        critical_pairs = [
            c for c in most_correlated
            if (c['corr_lt'] and abs(c['corr_lt']) >= self.analyzer.correlation_threshold) or
               (c['corr_ct'] and abs(c['corr_ct']) >= self.analyzer.correlation_threshold)
        ]
        
        if critical_pairs:
            alerts.append({
                'type': 'warning',
                'message': f"Corrélation critique (≥{self.analyzer.correlation_threshold}) "
                          f"avec {len(critical_pairs)} stratégie(s)"
            })
        
        # Score élevé (redondance)
        if strategy_row['Score_Davey'] >= 10:
            alerts.append({
                'type': 'danger',
                'message': f"Score Davey élevé ({strategy_row['Score_Davey']:.1f}): "
                          f"forte redondance détectée. Candidat à l'élimination."
            })
        
        # Excellente diversification
        elif strategy_row['Score_Davey'] < 2:
            alerts.append({
                'type': 'success',
                'message': "Excellente diversification. Cette stratégie est peu corrélée "
                          "avec le portefeuille."
            })
        
        # Delta important (changement de corrélation)
        delta_avg = strategy_row.get('Delta_Corr', strategy_row.get('Delta_Avg', 0))
        if abs(delta_avg) > 0.2:
            direction = "augmentation" if delta_avg > 0 else "diminution"
            alerts.append({
                'type': 'info',
                'message': f"Forte {direction} de la corrélation moyenne récemment "
                          f"(Δ = {delta_avg:+.3f})"
            })
        
        return alerts
    
    def _generate_html(self, profile: Dict[str, Any], output_path: Path):
        """
        Génère la page HTML depuis le template ou inline.
        
        Args:
            profile: Profil de corrélation de la stratégie
            output_path: Chemin du fichier HTML de sortie
        """
        if self.template_path.exists():
            # Utiliser le template externe
            template = self.template_path.read_text(encoding='utf-8')
            html = self._render_template(template, profile)
        else:
            # Fallback sur template inline
            html = self._generate_inline_html(profile)
        
        output_path.write_text(html, encoding='utf-8')
    
    def _render_template(self, template: str, profile: Dict[str, Any]) -> str:
        """
        Rend le template avec les données du profil.
        
        Args:
            template: Contenu du template HTML
            profile: Données du profil
            
        Returns:
            HTML complet
        """
        # Préparer les données JSON pour JavaScript
        data = {
            'most_correlated': json.dumps(profile['most_correlated'], ensure_ascii=False),
            'least_correlated': json.dumps(profile['least_correlated'], ensure_ascii=False),
            'alerts': json.dumps(profile['alerts'], ensure_ascii=False),
            'distribution': json.dumps(profile['distribution']),
            'timestamp': datetime.now().strftime('%d/%m/%Y à %H:%M')
        }
        
        # Ajouter les données du profil
        data.update(profile)
        
        # Classe CSS du status
        data['status_class'] = profile['status'].lower().replace(' ', '-').replace('é', 'e')
        
        # Formatter les nombres
        data['delta_avg_fmt'] = f"{'+'if profile['delta_avg']>=0 else ''}{profile['delta_avg']:.3f}"
        
        # Remplacer les placeholders
        html = template
        for key, value in data.items():
            placeholder = f"{{{{{key}}}}}"
            html = html.replace(placeholder, str(value))
        
        return html
    
    def _generate_inline_html(self, profile: Dict[str, Any]) -> str:
        """
        Génère le HTML inline (fallback si pas de template).
        
        Args:
            profile: Profil de corrélation
            
        Returns:
            HTML complet
        """
        p = profile  # Raccourci
        
        # Classe CSS du status
        status_class = p['status'].lower().replace(' ', '-').replace('é', 'e')
        
        # Préparer les données JSON
        most_json = json.dumps(p['most_correlated'], ensure_ascii=False)
        least_json = json.dumps(p['least_correlated'], ensure_ascii=False)
        alerts_json = json.dumps(p['alerts'], ensure_ascii=False)
        dist_json = json.dumps(p['distribution'])
        
        return f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{p['strategy_id']} - Analyse de Corrélation</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #0d1117;
            color: #c9d1d9;
            line-height: 1.6;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: #161b22;
            border-radius: 8px;
            padding: 30px;
            border: 1px solid #30363d;
        }}
        .nav {{ margin-bottom: 20px; }}
        .nav a {{
            display: inline-block;
            padding: 8px 16px;
            background: #21262d;
            color: #58a6ff;
            text-decoration: none;
            border-radius: 6px;
            margin-right: 8px;
        }}
        .nav a:hover {{ background: #30363d; }}
        h1 {{ color: #c9d1d9; font-size: 1.8em; margin-bottom: 8px; }}
        .subtitle {{ color: #8b949e; margin-bottom: 20px; }}
        .score-badge {{
            display: inline-flex;
            align-items: center;
            gap: 10px;
            padding: 12px 20px;
            border-radius: 8px;
            font-size: 1.2em;
            font-weight: bold;
            margin: 15px 0;
        }}
        .score-badge.diversifiant {{ background: rgba(46, 160, 67, 0.2); color: #3fb950; }}
        .score-badge.modere {{ background: rgba(187, 128, 9, 0.2); color: #d29922; }}
        .score-badge.correle {{ background: rgba(219, 109, 40, 0.2); color: #f0883e; }}
        .score-badge.tres-correle {{ background: rgba(248, 81, 73, 0.2); color: #f85149; }}
        h2 {{
            color: #58a6ff;
            font-size: 1.3em;
            margin: 24px 0 12px;
            padding-left: 12px;
            border-left: 3px solid #58a6ff;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 12px;
            margin: 16px 0;
        }}
        .stat-card {{
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 16px;
            text-align: center;
        }}
        .stat-value {{ font-size: 1.6em; font-weight: bold; color: #58a6ff; }}
        .stat-label {{ font-size: 0.85em; color: #8b949e; margin-top: 4px; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 12px 0;
            font-size: 0.9em;
        }}
        th, td {{
            padding: 10px 12px;
            text-align: left;
            border-bottom: 1px solid #21262d;
        }}
        th {{
            background: #0d1117;
            color: #8b949e;
            font-weight: 600;
        }}
        tr:hover {{ background: #0d1117; }}
        .corr-high {{ color: #f85149; font-weight: bold; }}
        .corr-medium {{ color: #d29922; }}
        .corr-low {{ color: #3fb950; }}
        .delta-positive {{ color: #f85149; }}
        .delta-positive::before {{ content: '↗ '; }}
        .delta-negative {{ color: #3fb950; }}
        .delta-negative::before {{ content: '↘ '; }}
        .alert {{
            padding: 12px 16px;
            border-radius: 6px;
            margin: 10px 0;
            border-left: 3px solid;
        }}
        .alert.success {{ background: rgba(46, 160, 67, 0.1); border-color: #3fb950; color: #3fb950; }}
        .alert.warning {{ background: rgba(187, 128, 9, 0.1); border-color: #d29922; color: #d29922; }}
        .alert.danger {{ background: rgba(248, 81, 73, 0.1); border-color: #f85149; color: #f85149; }}
        .alert.info {{ background: rgba(88, 166, 255, 0.1); border-color: #58a6ff; color: #58a6ff; }}
        .dist-bar {{
            display: flex;
            height: 24px;
            border-radius: 4px;
            overflow: hidden;
            margin: 12px 0;
        }}
        .dist-segment {{
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 0.75em;
            font-weight: bold;
        }}
        .dist-very-neg {{ background: #58a6ff; }}
        .dist-neg {{ background: #79c0ff; }}
        .dist-neutral {{ background: #6e7681; }}
        .dist-pos {{ background: #d29922; }}
        .dist-very-pos {{ background: #f85149; }}
        @media (max-width: 768px) {{
            .stats-grid {{ grid-template-columns: repeat(2, 1fr); }}
            h1 {{ font-size: 1.4em; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <nav class="nav">
            <a href="{p['strategy_name']}.html">← Rapport Stratégie</a>
            <a href="index.html">📊 Dashboard</a>
        </nav>
        
        <h1>📊 {p['strategy_id']}</h1>
        <p class="subtitle">Analyse de Corrélation • Symbole: {p['symbol']}</p>
        
        <div class="score-badge {status_class}">
            <span>{p['status_emoji']} {p['status']}</span>
            <span>Score: {p['score_davey']}</span>
        </div>
        
        <div id="alerts"></div>
        
        <h2>📈 Profil de Corrélation</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{p['n_corr_lt']}</div>
                <div class="stat-label">Corrélées (LT)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{p['n_corr_ct']}</div>
                <div class="stat-label">Corrélées (CT)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{p['avg_corr_lt']:.3f}</div>
                <div class="stat-label">Moy. LT</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{p['avg_corr_ct']:.3f}</div>
                <div class="stat-label">Moy. CT</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{'+'if p['delta_avg']>=0 else''}{p['delta_avg']:.3f}</div>
                <div class="stat-label">Delta (CT-LT)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{p['max_corr_lt']:.3f}</div>
                <div class="stat-label">Max LT</div>
            </div>
        </div>
        
        <h2>📊 Distribution des Corrélations</h2>
        <div id="distContainer"></div>
        
        <h2>🔝 Top {len(p['most_correlated'])} Stratégies les Plus Corrélées</h2>
        <table id="mostTable">
            <thead><tr><th>Stratégie</th><th>Symbole</th><th>Corr. LT</th><th>Corr. CT</th><th>Delta</th></tr></thead>
            <tbody></tbody>
        </table>
        
        <h2>🔻 Top {len(p['least_correlated'])} Stratégies les Moins Corrélées</h2>
        <table id="leastTable">
            <thead><tr><th>Stratégie</th><th>Symbole</th><th>Corr. LT</th><th>Corr. CT</th><th>Diversification</th></tr></thead>
            <tbody></tbody>
        </table>
        
        <div style="margin-top:30px;padding-top:15px;border-top:1px solid #30363d;text-align:center;color:#6e7681;font-size:0.85em;">
            Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')} • Méthode Kevin Davey
        </div>
    </div>
    
    <script>
        const mostData = {most_json};
        const leastData = {least_json};
        const alerts = {alerts_json};
        const dist = {dist_json};
        
        // Alertes
        const alertsCont = document.getElementById('alerts');
        alerts.forEach(a => {{
            const icons = {{'success': '✅', 'warning': '⚠️', 'danger': '🚨', 'info': '💡'}};
            alertsCont.innerHTML += `<div class="alert ${{a.type}}"><span>${{icons[a.type] || '📌'}} ${{a.message}}</span></div>`;
        }});
        
        // Distribution
        const total = Object.values(dist).reduce((a,b) => a+b, 0);
        if (total > 0) {{
            const pcts = {{
                vn: (dist.very_negative/total*100).toFixed(1),
                n: (dist.negative/total*100).toFixed(1),
                neu: (dist.neutral/total*100).toFixed(1),
                p: (dist.positive/total*100).toFixed(1),
                vp: (dist.very_positive/total*100).toFixed(1)
            }};
            document.getElementById('distContainer').innerHTML = `
                <div class="dist-bar">
                    <div class="dist-segment dist-very-neg" style="width:${{pcts.vn}}%">${{dist.very_negative}}</div>
                    <div class="dist-segment dist-neg" style="width:${{pcts.n}}%">${{dist.negative}}</div>
                    <div class="dist-segment dist-neutral" style="width:${{pcts.neu}}%">${{dist.neutral}}</div>
                    <div class="dist-segment dist-pos" style="width:${{pcts.p}}%">${{dist.positive}}</div>
                    <div class="dist-segment dist-very-pos" style="width:${{pcts.vp}}%">${{dist.very_positive}}</div>
                </div>
                <div style="font-size:0.85em;color:#8b949e;margin-top:8px;">
                    🔵 r≤-0.7 (${{dist.very_negative}}) • 🔷 -0.7<r≤-0.3 (${{dist.negative}}) • ⚪ -0.3<r<0.3 (${{dist.neutral}}) • 🟠 0.3≤r<0.7 (${{dist.positive}}) • 🔴 r≥0.7 (${{dist.very_positive}})
                </div>
            `;
        }}
        
        // Tables
        function getCorrClass(v) {{
            if (!v) return '';
            const a = Math.abs(v);
            return a >= 0.7 ? 'corr-high' : a >= 0.5 ? 'corr-medium' : 'corr-low';
        }}
        
        function fmtCorr(v) {{ return v !== null ? v.toFixed(3) : '-'; }}
        
        function fmtDelta(v) {{
            if (!v) return '-';
            const cls = v > 0.05 ? 'delta-positive' : v < -0.05 ? 'delta-negative' : '';
            return `<span class="${{cls}}">${{v>=0?'+':''}}${{v.toFixed(3)}}</span>`;
        }}
        
        const mostTb = document.querySelector('#mostTable tbody');
        mostData.forEach(r => {{
            mostTb.innerHTML += `<tr>
                <td>${{r.strategy}}</td>
                <td>${{r.symbol}}</td>
                <td class="${{getCorrClass(r.corr_lt)}}">${{fmtCorr(r.corr_lt)}}</td>
                <td class="${{getCorrClass(r.corr_ct)}}">${{fmtCorr(r.corr_ct)}}</td>
                <td>${{fmtDelta(r.delta)}}</td>
            </tr>`;
        }});
        
        const leastTb = document.querySelector('#leastTable tbody');
        leastData.forEach(r => {{
            const stars = r.max_abs < 0.2 ? '⭐⭐⭐' : r.max_abs < 0.4 ? '⭐⭐' : '⭐';
            leastTb.innerHTML += `<tr>
                <td>${{r.strategy}}</td>
                <td>${{r.symbol}}</td>
                <td class="${{getCorrClass(r.corr_lt)}}">${{fmtCorr(r.corr_lt)}}</td>
                <td class="${{getCorrClass(r.corr_ct)}}">${{fmtCorr(r.corr_ct)}}</td>
                <td>${{stars}}</td>
            </tr>`;
        }});
    </script>
</body>
</html>'''
    
    @staticmethod
    def _sanitize_filename(name: str) -> str:
        """
        Sécurise un nom de fichier.
        
        Args:
            name: Nom à sécuriser
            
        Returns:
            Nom sécurisé
        """
        import re
        return re.sub(r'[<>:"/\\|?*]', '_', name)
