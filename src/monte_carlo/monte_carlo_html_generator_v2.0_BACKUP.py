#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monte Carlo HTML Generator V2
==============================

Génère des rapports HTML pour les simulations Monte Carlo:
- Page de synthèse: all_strategies_montecarlo.html
- Pages individuelles: Individual/{Symbol}_{Strategy}_MC.html

Usage:
    python monte_carlo_html_generator.py                 # Dernier run
    python monte_carlo_html_generator.py --run 20251201_1130   # Run spécifique

Auteur: Yann
Date: 2025-12-01
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import sys
import argparse
import re
import os
import importlib.util

# Configuration des chemins
SCRIPT_DIR = Path(__file__).parent.absolute()
V2_ROOT = SCRIPT_DIR.parent.parent

# Ajouter V2_ROOT au path si nécessaire
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

# Importer les settings
try:
    from config.settings import HTML_MONTECARLO_DIR, OUTPUT_ROOT
except ImportError:
    # Fallback si l'import échoue
    OUTPUT_ROOT = V2_ROOT / "outputs"
    HTML_MONTECARLO_DIR = OUTPUT_ROOT / "html_reports" / "montecarlo"


def find_latest_monte_carlo_run() -> Path:
    """Trouve le répertoire de run Monte Carlo le plus récent."""
    mc_dir = OUTPUT_ROOT / "monte_carlo"
    
    if not mc_dir.exists():
        raise FileNotFoundError(f"Répertoire Monte Carlo introuvable: {mc_dir}")
    
    # Chercher les répertoires au format YYYYMMDD_HHMM
    run_dirs = [d for d in mc_dir.iterdir() if d.is_dir() and re.match(r'\d{8}_\d{4}', d.name)]
    
    if not run_dirs:
        raise FileNotFoundError(f"Aucun run Monte Carlo trouvé dans {mc_dir}")
    
    # Retourner le plus récent
    return max(run_dirs, key=lambda d: d.name)


def extract_symbol_from_strategy_name(strategy_name: str) -> str:
    """
    Extrait le symbole du nom de la stratégie.
    Format attendu: SYMBOL_ResteDuNom
    """
    parts = strategy_name.split('_')
    if len(parts) > 0:
        # Premier élément est généralement le symbole
        symbol = parts[0]
        # Gérer les cas spéciaux comme BTCUSDT, ETHUSDT
        if len(symbol) > 10:
            return "OTHER"
        return symbol
    return "UNKNOWN"


def load_summary_data(summary_file: Path) -> pd.DataFrame:
    """
    Charge le fichier summary CSV.
    """
    # Format européen: séparateur ; et décimal ,
    df = pd.read_csv(
        summary_file,
        sep=';',
        decimal=',',
        encoding='utf-8-sig'
    )
    
    # Extraire le symbole si vide
    if 'symbol' in df.columns and df['symbol'].isna().all():
        df['symbol'] = df['strategy_name'].apply(extract_symbol_from_strategy_name)
    
    return df


def load_individual_strategy_data(csv_file: Path) -> Dict:
    """
    Charge les données détaillées d'une stratégie depuis son CSV.
    """
    # Lire les métadonnées en commentaires
    metadata = {}
    with open(csv_file, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.startswith('#'):
                break
            if ':' in line:
                key, value = line[1:].split(':', 1)
                metadata[key.strip()] = value.strip()
    
    # Lire les données CSV
    df = pd.read_csv(csv_file, comment='#')
    
    return {
        'metadata': metadata,
        'data': df
    }


def generate_individual_html(
    strategy_name: str,
    symbol: str,
    summary_row: Dict,
    detail_data: Dict,
    output_file: Path
):
    """Génère une page HTML individuelle pour une stratégie."""
    
    metadata = detail_data['metadata']
    df = detail_data['data']
    
    # Préparer les données pour les graphiques
    capital_levels = df['Start_Equity'].tolist()
    ruin_probs = (df['Ruin_Pct'] / 100).tolist()  # Convertir en fraction
    return_dd_ratios = df['Return_DD_Ratio'].tolist()
    median_profits = df['Median_Profit'].tolist()
    prob_positives = (df['Prob_Positive_Pct'] / 100).tolist()
    
    # Capital recommandé
    recommended_capital = summary_row.get('recommended_capital', 0)
    if pd.isna(recommended_capital):
        recommended_capital = 0
    
    # Trouver la ligne correspondante au capital recommandé
    if recommended_capital > 0:
        rec_row = df[df['Start_Equity'] == recommended_capital]
        if len(rec_row) > 0:
            rec_row = rec_row.iloc[0].to_dict()
        else:
            rec_row = df.iloc[-1].to_dict()
    else:
        rec_row = df.iloc[-1].to_dict()
    
    # Générer les lignes du tableau
    results_rows = ""
    for _, row in df.iterrows():
        row_class = 'recommended' if row['Start_Equity'] == recommended_capital else ''
        results_rows += f"""
        <tr class="{row_class}">
            <td>${row['Start_Equity']:,.0f}</td>
            <td>{row['Ruin_Pct']:.2f}%</td>
            <td>{row['Median_DD_Pct']:.2f}%</td>
            <td>${row['Median_Profit']:,.0f}</td>
            <td>{row['Median_Return_Pct']:.2f}%</td>
            <td>{min(row['Return_DD_Ratio'], 99.99):.2f}</td>
            <td>{row['Prob_Positive_Pct']:.1f}%</td>
        </tr>
        """
    
    # Déterminer le statut et la recommandation
    status = summary_row.get('status', 'UNKNOWN')
    
    if status == 'OK':
        recommendation_class = ""
        status_class = "ok"
        recommendation_title = f"✅ Capital Recommandé: ${recommended_capital:,.0f}"
        recommendation_text = "Ce niveau de capital satisfait tous les critères Kevin Davey."
        ruin_pct = rec_row['Ruin_Pct']
        ret_dd = rec_row['Return_DD_Ratio']
        prob_pos = rec_row['Prob_Positive_Pct']
        criteria_html = f"""
            <li>Risque de ruine: {ruin_pct:.2f}% ≤ 10%</li>
            <li>Return/DD ratio: {ret_dd:.2f} ≥ 2</li>
            <li>Probabilité positive: {prob_pos:.1f}% ≥ 80%</li>
        """
    elif status == 'WARNING':
        recommendation_class = "warning"
        status_class = "warning"
        recommendation_title = f"⚠️ Capital Suggéré: ${recommended_capital:,.0f}" if recommended_capital > 0 else "⚠️ Critères partiellement satisfaits"
        recommendation_text = "Ce niveau satisfait certains critères mais pas tous."
        
        ruin_pct = rec_row['Ruin_Pct']
        ret_dd = rec_row['Return_DD_Ratio']
        prob_pos = rec_row['Prob_Positive_Pct']
        
        criteria_items = []
        if ruin_pct <= 10:
            criteria_items.append(f'<li>Risque de ruine: {ruin_pct:.2f}% ≤ 10%</li>')
        else:
            criteria_items.append(f'<li class="fail">Risque de ruine: {ruin_pct:.2f}% > 10%</li>')
        
        if ret_dd >= 2:
            criteria_items.append(f'<li>Return/DD ratio: {ret_dd:.2f} ≥ 2</li>')
        else:
            criteria_items.append(f'<li class="fail">Return/DD ratio: {ret_dd:.2f} < 2</li>')
        
        if prob_pos >= 80:
            criteria_items.append(f'<li>Probabilité positive: {prob_pos:.1f}% ≥ 80%</li>')
        else:
            criteria_items.append(f'<li class="fail">Probabilité positive: {prob_pos:.1f}% < 80%</li>')
        
        criteria_html = "\n".join(criteria_items)
    else:
        recommendation_class = "danger"
        status_class = "danger"
        recommendation_title = "❌ Risque Élevé - Aucun Capital Recommandé"
        recommendation_text = "Même avec le capital maximum testé, les critères ne sont pas satisfaits."
        ruin_pct = rec_row['Ruin_Pct']
        ret_dd = rec_row['Return_DD_Ratio']
        prob_pos = rec_row['Prob_Positive_Pct']
        criteria_html = f"""
            <li class="fail">Risque de ruine: {ruin_pct:.2f}% > 10%</li>
            <li class="fail">Return/DD ratio: {ret_dd:.2f} < 2</li>
            <li class="fail">Probabilité positive: {prob_pos:.1f}% < 80%</li>
        """
    
    # Template HTML
    html_content = HTML_INDIVIDUAL_TEMPLATE.format(
        strategy_full_name=f"{symbol}_{strategy_name}",
        generation_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        total_trades=f"{int(summary_row.get('nb_trades', 0)):,}",
        trades_per_year=f"{int(summary_row.get('trades_per_year', 0)):,}",
        total_profit=f"{summary_row.get('total_pnl', 0):,.0f}",
        profit_factor=f"{min(summary_row.get('profit_factor', 0), 99.99):.2f}",
        win_rate=f"{summary_row.get('win_rate', 0):.1f}",
        backtest_years=f"{summary_row.get('years', 0):.1f}",
        nb_simulations=metadata.get('Simulations per level', '1000'),
        nb_capital_levels=len(df),
        simulated_trades=metadata.get('Trades per year', '30'),
        ruin_threshold=metadata.get('Ruin threshold', '40%').replace('%', ''),
        recommendation_class=recommendation_class,
        status_class=status_class,
        recommendation_title=recommendation_title,
        recommendation_text=recommendation_text,
        criteria_html=criteria_html,
        results_rows=results_rows,
        capital_levels_json=json.dumps(capital_levels),
        ruin_probs_json=json.dumps(ruin_probs),
        return_dd_ratios_json=json.dumps([min(r, 20) for r in return_dd_ratios]),
        median_profits_json=json.dumps(median_profits),
        prob_positives_json=json.dumps(prob_positives),
        recommended_capital_json=json.dumps(float(recommended_capital) if recommended_capital > 0 else 0),
    )
    
    # Écrire le fichier
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)


def generate_summary_html(
    summary_df: pd.DataFrame,
    output_file: Path,
    run_info: Dict,
    run_dir: Path
):
    """Génère la page HTML de synthèse avec données embarquées pour recalcul dynamique."""
    
    # Compteurs par statut
    status_counts = summary_df['status'].value_counts().to_dict()
    ok_count = status_counts.get('OK', 0)
    warning_count = status_counts.get('WARNING', 0)
    high_risk_count = status_counts.get('HIGH_RISK', 0)
    
    # Statistiques globales
    total_strategies = len(summary_df)
    total_trades = int(summary_df['nb_trades'].sum())
    total_pnl = summary_df['total_pnl'].sum()
    
    # Extraire les symboles (depuis les noms de stratégies car la colonne symbol peut être vide)
    def get_symbol(row):
        if pd.notna(row['symbol']) and row['symbol'] != '':
            return row['symbol']
        return row['strategy_name'].split('_')[0] if '_' in row['strategy_name'] else 'UNKNOWN'
    
    symbols = sorted(set(summary_df.apply(get_symbol, axis=1)))
    symbol_options = '\n'.join(f'<option value="{s}">{s}</option>' for s in symbols)
    
    # Charger les données complètes de tous les niveaux pour chaque stratégie
    print("   📊 Chargement des données détaillées pour recalcul dynamique...")
    strategies_detailed_data = {}
    
    for _, row in summary_df.iterrows():
        strategy_name = row['strategy_name']
        
        # Le nom du fichier CSV est simplement {strategy_name}_mc.csv
        csv_filename = f"{strategy_name}_mc.csv"
        csv_file = run_dir / csv_filename
        
        if csv_file.exists():
            try:
                df = pd.read_csv(csv_file, comment='#')
                
                # Extraire le symbole du nom de stratégie (premier élément)
                symbol = strategy_name.split('_')[0] if '_' in strategy_name else 'UNKNOWN'
                
                strategies_detailed_data[strategy_name] = {
                    'symbol': symbol,
                    'nb_trades': int(row['nb_trades']),
                    'total_pnl': float(row['total_pnl']),
                    'win_rate': float(row['win_rate']),
                    'profit_factor': float(row['profit_factor']),
                    'levels': [
                        {
                            'capital': float(r['Start_Equity']),
                            'ruin_pct': float(r['Ruin_Pct']),
                            'return_dd': float(r['Return_DD_Ratio']),
                            'prob_positive': float(r['Prob_Positive_Pct']),
                            'median_dd_pct': float(r['Median_DD_Pct']),
                            'median_profit': float(r['Median_Profit'])
                        }
                        for _, r in df.iterrows()
                    ]
                }
            except Exception as e:
                print(f"      ⚠ Erreur pour {strategy_name}: {e}")
        else:
            print(f"      ⚠ Fichier non trouvé: {csv_filename}")
    
    print(f"      ✓ {len(strategies_detailed_data)} stratégies chargées avec données détaillées")
    
    # Générer les lignes du tableau
    table_rows = ""
    for _, row in summary_df.iterrows():
        status_class = {
            'OK': 'status-ok',
            'WARNING': 'status-warning',
            'HIGH_RISK': 'status-danger'
        }.get(row['status'], '')
        
        status_text = {
            'OK': '✓ OK',
            'WARNING': '⚠ Warning',
            'HIGH_RISK': '✗ High Risk'
        }.get(row['status'], row['status'])
        
        capital_str = f"${row['recommended_capital']:,.0f}" if pd.notna(row['recommended_capital']) and row['recommended_capital'] > 0 else "N/A"
        
        # Extraire le symbole si vide (du nom de stratégie)
        if pd.isna(row['symbol']) or row['symbol'] == '':
            symbol = row['strategy_name'].split('_')[0] if '_' in row['strategy_name'] else 'UNKNOWN'
        else:
            symbol = row['symbol']
        
        # Lien vers le rapport individuel
        individual_link = f"Individual/{symbol}_{row['strategy_name']}_MC.html"
        
        table_rows += f"""
        <tr data-strategy="{row['strategy_name']}" data-symbol="{symbol}" data-status="{row['status']}">
            <td><a href="{individual_link}" class="strategy-link">{row['strategy_name']}</a></td>
            <td>{symbol}</td>
            <td><span class="status-badge {status_class}">{status_text}</span></td>
            <td>{capital_str}</td>
            <td>{int(row['nb_trades']):,}</td>
            <td>${row['total_pnl']:,.0f}</td>
            <td>{row['win_rate']:.1f}%</td>
            <td>{min(row['profit_factor'], 99.99):.2f}</td>
            <td>{row['ruin_pct']:.1f}%</td>
            <td>{min(row['return_dd_ratio'], 99.99):.2f}</td>
            <td>{row['prob_positive']:.1f}%</td>
        </tr>
        """
    
    # Préparer les données JSON pour les graphiques ET le recalcul dynamique
    strategies_json_data = []
    for _, row in summary_df.iterrows():
        # Extraire le symbole
        if pd.notna(row['symbol']) and row['symbol'] != '':
            symbol = row['symbol']
        else:
            symbol = row['strategy_name'].split('_')[0] if '_' in row['strategy_name'] else 'UNKNOWN'
        
        strategies_json_data.append({
            'strategy_name': row['strategy_name'],
            'symbol': symbol,
            'status': row['status'],
            'nb_trades': int(row['nb_trades']),
            'total_pnl': round(row['total_pnl'], 2),
            'win_rate': round(row['win_rate'], 1),
            'profit_factor': min(round(row['profit_factor'], 2), 99.99),
            'recommended_capital': float(row['recommended_capital']) if pd.notna(row['recommended_capital']) else 0,
            'ruin_pct': round(row['ruin_pct'], 2),
            'return_dd_ratio': min(round(row['return_dd_ratio'], 2), 99.99),
            'prob_positive': round(row['prob_positive'], 1),
        })
    
    # JSON des données détaillées pour recalcul dynamique
    strategies_detailed_json = json.dumps(strategies_detailed_data)
    
    # Debug: afficher un échantillon
    if strategies_detailed_data:
        first_key = list(strategies_detailed_data.keys())[0]
        print(f"      Debug - Exemple de données pour '{first_key}': {len(strategies_detailed_data[first_key]['levels'])} niveaux")
    else:
        print(f"      ⚠ ATTENTION: Aucune donnée détaillée chargée!")
    
    # Config info
    config_info = f"Run: {run_info['run_name']} | {run_info.get('nb_simulations', 'N/A')} simulations"
    
    # Remplir le template
    html_content = HTML_SUMMARY_TEMPLATE.format(
        generation_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        total_strategies=total_strategies,
        ok_count=ok_count,
        warning_count=warning_count,
        high_risk_count=high_risk_count,
        total_trades=f"{total_trades:,}",
        total_pnl=f"{total_pnl:,.0f}",
        symbol_options=symbol_options,
        table_rows=table_rows,
        strategies_json=json.dumps(strategies_json_data),
        strategies_detailed_json=strategies_detailed_json,
        config_info=config_info,
    )
    
    # Écrire le fichier
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)


def main(run_dir: Optional[Path] = None):
    """
    Point d'entrée principal.
    """
    print("=" * 80)
    print("GÉNÉRATEUR DE RAPPORTS HTML MONTE CARLO V2")
    print("=" * 80)
    print()
    
    # 1. Déterminer le répertoire de run
    if run_dir is None:
        run_dir = find_latest_monte_carlo_run()
    
    print(f"📁 Répertoire de run: {run_dir.name}")
    print()
    
    # 2. Vérifier les fichiers requis
    summary_file = run_dir / "monte_carlo_summary.csv"
    if not summary_file.exists():
        raise FileNotFoundError(f"Fichier summary introuvable: {summary_file}")
    
    # 3. Charger les données summary
    print("📊 Chargement du fichier summary...")
    summary_df = load_summary_data(summary_file)
    print(f"   ✓ {len(summary_df)} stratégies chargées")
    print()
    
    # 4. Créer les répertoires de sortie
    individual_dir = HTML_MONTECARLO_DIR / "Individual"
    individual_dir.mkdir(parents=True, exist_ok=True)
    HTML_MONTECARLO_DIR.mkdir(parents=True, exist_ok=True)
    
    # 5. Générer les pages individuelles
    print("🔨 Génération des pages HTML individuelles...")
    success_count = 0
    error_count = 0
    
    for idx, row in summary_df.iterrows():
        strategy_name = row['strategy_name']
        symbol = row['symbol']
        
        # Trouver le fichier CSV correspondant
        csv_file = run_dir / f"{strategy_name}_mc.csv"
        
        if not csv_file.exists():
            print(f"   ⚠ CSV introuvable: {csv_file.name}")
            error_count += 1
            continue
        
        try:
            # Charger les données détaillées
            detail_data = load_individual_strategy_data(csv_file)
            
            # Générer la page HTML
            output_file = individual_dir / f"{symbol}_{strategy_name}_MC.html"
            generate_individual_html(
                strategy_name=strategy_name,
                symbol=symbol,
                summary_row=row.to_dict(),
                detail_data=detail_data,
                output_file=output_file
            )
            
            success_count += 1
            
            if (idx + 1) % 50 == 0:
                print(f"   Progression: {idx + 1}/{len(summary_df)}")
        
        except Exception as e:
            print(f"   ✗ Erreur pour {strategy_name}: {e}")
            error_count += 1
    
    print(f"   ✓ {success_count} pages individuelles générées")
    if error_count > 0:
        print(f"   ⚠ {error_count} erreurs")
    print()
    
    # 6. Générer la page de synthèse
    print("🔨 Génération de la page de synthèse...")
    summary_html_file = HTML_MONTECARLO_DIR / "all_strategies_montecarlo.html"
    
    run_info = {
        'run_name': run_dir.name,
        'nb_simulations': '1000',  # TODO: extraire des métadonnées
    }
    
    generate_summary_html(
        summary_df=summary_df,
        output_file=summary_html_file,
        run_info=run_info,
        run_dir=run_dir
    )
    
    print(f"   ✓ Page de synthèse générée: {summary_html_file.name}")
    print()
    
    # 7. Résumé final
    print("=" * 80)
    print("✅ GÉNÉRATION TERMINÉE")
    print("=" * 80)
    print(f"📊 Stratégies traitées: {success_count}/{len(summary_df)}")
    print(f"📁 Répertoire de sortie: {HTML_MONTECARLO_DIR}")
    print(f"   • Page de synthèse: all_strategies_montecarlo.html")
    print(f"   • Pages individuelles: Individual/ ({success_count} fichiers)")
    print()


# Import des templates HTML
try:
    from html_templates import INDIVIDUAL_TEMPLATE, SUMMARY_TEMPLATE
except ImportError:
    # Si l'import échoue, charger depuis le fichier
    templates_file = SCRIPT_DIR / "html_templates.py"
    import importlib.util
    spec = importlib.util.spec_from_file_location("html_templates", templates_file)
    html_templates = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(html_templates)
    INDIVIDUAL_TEMPLATE = html_templates.INDIVIDUAL_TEMPLATE
    SUMMARY_TEMPLATE = html_templates.SUMMARY_TEMPLATE

HTML_INDIVIDUAL_TEMPLATE = INDIVIDUAL_TEMPLATE
HTML_SUMMARY_TEMPLATE = SUMMARY_TEMPLATE


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Génère des rapports HTML Monte Carlo")
    parser.add_argument(
        '--run',
        type=str,
        help="Nom du run (ex: 20251201_1130). Par défaut: le plus récent"
    )
    
    args = parser.parse_args()
    
    run_dir = None
    if args.run:
        run_dir = OUTPUT_ROOT / "monte_carlo" / args.run
        if not run_dir.exists():
            print(f"❌ Erreur: Run introuvable: {run_dir}")
            sys.exit(1)
    
    try:
        main(run_dir)
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
