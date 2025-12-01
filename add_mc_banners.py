#!/usr/bin/env python3
"""
Script pour ajouter les bandeaux Monte Carlo à toutes les pages AI
"""

import re
import csv
from pathlib import Path
from typing import Dict, Optional

# Chemins
AI_REPORTS_DIR = Path(r"C:\TradeData\V2\outputs\ai_analysis\html_reports")
MC_INDIVIDUAL_DIR = Path(r"C:\TradeData\V2\outputs\monte_carlo\Individual")

def extract_strategy_info(html_content: str) -> tuple[Optional[str], Optional[str]]:
    """Extraire le nom de la stratégie et le symbole du HTML"""
    
    # Chercher dans les KPI chips pour trouver le symbole
    symbol_match = re.search(r'<span class="chip-label">Symbol</span>\s*<span class="chip-value">([^<]+)</span>', html_content)
    symbol = symbol_match.group(1).strip() if symbol_match else None
    
    return symbol

def read_mc_data(mc_csv_path: Path) -> Optional[Dict[str, str]]:
    """Lire les données Monte Carlo depuis le CSV"""
    
    if not mc_csv_path.exists():
        return None
    
    try:
        with open(mc_csv_path, 'r', encoding='utf-8-sig') as f:
            # Lire l'entête pour trouver le capital recommandé
            lines = f.readlines()
            recommended_capital = None
            
            for line in lines:
                if line.startswith('# Recommended Capital:'):
                    recommended_capital = line.split(':')[1].strip()
                    break
            
            if not recommended_capital:
                return None
            
            # Chercher la ligne avec ce capital dans les données
            # On passe les lignes de commentaires
            data_started = False
            for line in lines:
                if line.startswith('Start_Equity'):
                    data_started = True
                    continue
                
                if data_started and not line.startswith('#'):
                    parts = line.strip().split(';')
                    if parts and parts[0] == recommended_capital:
                        # parts[0] = Start_Equity
                        # parts[1] = Ruin_Pct
                        # parts[6] = Prob_Positive_Pct
                        return {
                            'capital': f"${int(float(recommended_capital)):,}",
                            'ruin_risk': parts[1].replace(',', '.'),
                            'win_prob': parts[6].replace(',', '.')
                        }
        
        return None
        
    except Exception as e:
        print(f"Erreur lecture {mc_csv_path}: {e}")
        return None

def create_mc_banner_html(strategy_name: str, symbol: str, mc_data: Dict[str, str], mc_html_link: str) -> str:
    """Créer le HTML du bandeau Monte Carlo"""
    
    return f'''
        <!-- Bandeau Monte Carlo -->
        <div class="mc-banner">
            <h2>🎲 Simulation Monte Carlo</h2>
            <div class="mc-stats-grid">
                <div class="mc-stat">
                    <div class="mc-stat-icon">💰</div>
                    <div class="mc-stat-content">
                        <div class="mc-stat-label">Capital Min Recommandé</div>
                        <div class="mc-stat-value">{mc_data['capital']}</div>
                    </div>
                </div>
                <div class="mc-stat">
                    <div class="mc-stat-icon">⚠️</div>
                    <div class="mc-stat-content">
                        <div class="mc-stat-label">Risque de Ruine Année 1</div>
                        <div class="mc-stat-value risk">{mc_data['ruin_risk']}%</div>
                    </div>
                </div>
                <div class="mc-stat">
                    <div class="mc-stat-icon">✅</div>
                    <div class="mc-stat-content">
                        <div class="mc-stat-label">Probabilité Gain Année 1</div>
                        <div class="mc-stat-value success">{mc_data['win_prob']}%</div>
                    </div>
                </div>
            </div>
            <a href="{mc_html_link}" class="mc-link">📊 Voir le rapport Monte Carlo complet →</a>
        </div>
        
'''

def create_mc_banner_css() -> str:
    """Créer le CSS pour le bandeau Monte Carlo"""
    
    return '''
        /* ============ BANDEAU MONTE CARLO ============ */
        .mc-banner {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            padding: 30px;
            margin: 40px 0;
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
            color: white;
        }
        
        .mc-banner h2 {
            margin: 0 0 25px 0;
            font-size: 1.8em;
            color: white;
            text-align: center;
        }
        
        .mc-stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }
        
        .mc-stat {
            background: rgba(255, 255, 255, 0.15);
            border-radius: 12px;
            padding: 20px;
            display: flex;
            align-items: center;
            gap: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .mc-stat-icon {
            font-size: 2.5em;
            flex-shrink: 0;
        }
        
        .mc-stat-content {
            flex: 1;
        }
        
        .mc-stat-label {
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 5px;
        }
        
        .mc-stat-value {
            font-size: 1.8em;
            font-weight: 700;
            color: white;
        }
        
        .mc-stat-value.risk {
            color: #ffeb3b;
        }
        
        .mc-stat-value.success {
            color: #4caf50;
        }
        
        .mc-link {
            display: block;
            text-align: center;
            background: white;
            color: #667eea;
            padding: 15px 30px;
            border-radius: 10px;
            text-decoration: none;
            font-weight: 600;
            font-size: 1.1em;
            transition: all 0.3s ease;
        }
        
        .mc-link:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            color: #764ba2;
        }
        
        @media (max-width: 768px) {
            .mc-stats-grid {
                grid-template-columns: 1fr;
            }
            
            .mc-stat {
                flex-direction: column;
                text-align: center;
            }
        }
'''

def process_html_file(html_path: Path) -> bool:
    """Traiter un fichier HTML pour ajouter le bandeau Monte Carlo"""
    
    try:
        # Lire le contenu HTML
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier si le bandeau n'existe pas déjà
        if '<!-- Bandeau Monte Carlo -->' in content:
            print(f"  ⏭️  Bandeau déjà présent, skip...")
            return True
        
        # Extraire le nom de la stratégie depuis le nom de fichier
        strategy_name = html_path.stem  # Enlève .html
        
        # Extraire le symbole
        symbol = extract_strategy_info(content)
        
        if not symbol:
            print(f"  ⚠️  Symbole non trouvé")
            return False
        
        # Chercher le fichier CSV Monte Carlo
        mc_csv_name = f"{symbol}_{strategy_name}_MC.csv"
        mc_csv_path = MC_INDIVIDUAL_DIR / mc_csv_name
        mc_html_name = f"{symbol}_{strategy_name}_MC.html"
        
        # Lire les données MC
        mc_data = read_mc_data(mc_csv_path)
        
        if not mc_data:
            print(f"  ⚠️  Données MC non trouvées ({mc_csv_name})")
            return False
        
        # Créer le lien relatif vers la page MC
        mc_html_link = f"../../../monte_carlo/Individual/{mc_html_name}"
        
        # Créer le bandeau
        banner_html = create_mc_banner_html(strategy_name, symbol, mc_data, mc_html_link)
        
        # Ajouter le CSS s'il n'existe pas
        if '/* ============ BANDEAU MONTE CARLO ============ */' not in content:
            css_to_add = create_mc_banner_css()
            content = content.replace('</style>', css_to_add + '    </style>')
        
        # Trouver où insérer le bandeau (après </div> qui ferme la section AI et avant <h2>💻 Code Source</h2>)
        # Pattern: </p></div> suivi d'espaces/lignes vides puis <h2>💻 Code Source</h2>
        pattern = r'(</p>\s*</div>\s*)(<h2>💻 Code Source</h2>)'
        
        if re.search(pattern, content):
            content = re.sub(pattern, r'\1' + banner_html + r'\2', content)
        else:
            print(f"  ⚠️  Pattern d'insertion non trouvé")
            return False
        
        # Sauvegarder le fichier modifié
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  ✅ Bandeau ajouté (Capital: {mc_data['capital']}, Risque: {mc_data['ruin_risk']}%)")
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        return False

def main():
    """Fonction principale"""
    
    print("🎲 Ajout des bandeaux Monte Carlo aux pages AI\n")
    print(f"📁 Répertoire: {AI_REPORTS_DIR}")
    print(f"📁 Monte Carlo: {MC_INDIVIDUAL_DIR}\n")
    
    # Lister tous les fichiers HTML sauf index.html
    html_files = [f for f in AI_REPORTS_DIR.glob("*.html") 
                  if f.name != "index.html" and not f.name.endswith(".bak")]
    
    print(f"📊 {len(html_files)} pages à traiter\n")
    
    success_count = 0
    skip_count = 0
    error_count = 0
    
    for i, html_path in enumerate(html_files, 1):
        print(f"[{i}/{len(html_files)}] {html_path.name}")
        
        result = process_html_file(html_path)
        
        if result is True:
            success_count += 1
        elif result is None:
            skip_count += 1
        else:
            error_count += 1
    
    print(f"\n{'='*60}")
    print(f"✅ Succès: {success_count}")
    print(f"⏭️  Déjà présents: {skip_count}")
    print(f"❌ Erreurs: {error_count}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
