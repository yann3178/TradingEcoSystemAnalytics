#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'enrichissement des pages HTML - Liens croisés Monte Carlo ↔ AI Analysis
==================================================================================

Ce script ajoute des liens de navigation entre:
1. Page synthèse Monte Carlo → Index principal
2. Pages individuelles Monte Carlo → Index principal
3. Pages individuelles Monte Carlo → Pages AI correspondantes
4. Pages AI → Pages Monte Carlo correspondantes (mise à jour)

Usage: python enrich_montecarlo_html_pages_with_ai_pages_link.py
"""

import re
from pathlib import Path
from typing import Optional, List, Tuple

# =============================================================================
# CONFIGURATION
# =============================================================================

V2_ROOT = Path("C:/TradeData/V2")
HTML_ROOT = V2_ROOT / "outputs" / "html_reports"

MC_SUMMARY = HTML_ROOT / "montecarlo" / "all_strategies_montecarlo.html"
MC_INDIVIDUAL_DIR = HTML_ROOT / "montecarlo" / "Individual"
AI_DIR = HTML_ROOT
INDEX_FILE = HTML_ROOT / "index.html"

# CSS pour les boutons de navigation
BUTTON_CSS = """
/* Navigation Buttons - Ajouté par enrich_montecarlo_html_pages_with_ai_pages_link.py */
.nav-button {
    display: inline-block;
    padding: 10px 20px;
    margin: 10px 5px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    text-decoration: none;
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.95em;
    transition: all 0.3s ease;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
}

.nav-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(102, 126, 234, 0.4);
    text-decoration: none;
}

.nav-button.secondary {
    background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
}

.nav-button.secondary:hover {
    box-shadow: 0 6px 12px rgba(78, 205, 196, 0.4);
}

.nav-buttons-container {
    margin: 20px 0;
    padding: 15px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 10px;
    text-align: center;
}
"""

MARKER_START = "<!-- NAVIGATION_LINKS_START -->"
MARKER_END = "<!-- NAVIGATION_LINKS_END -->"

# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def extract_strategy_name_from_mc(mc_filename: str) -> Optional[str]:
    """
    Extrait le nom de stratégie depuis un fichier Monte Carlo.
    
    Exemple:
        RB_RB_SOM_UA_2311_G_4_MC.html → SOM_UA_2311_G_4
    """
    # Enlever .html
    name = mc_filename.replace('.html', '')
    
    # Enlever le suffixe _MC
    if name.endswith('_MC'):
        name = name[:-3]
    
    # Enlever le préfixe RB_RB_ (symbole)
    # Pattern: SYMBOL_SYMBOL_STRATEGY
    parts = name.split('_')
    if len(parts) >= 3 and parts[0] == parts[1]:
        # Enlever les 2 premiers éléments (symbole dupliqué)
        strategy_name = '_'.join(parts[2:])
        return strategy_name
    
    # Si pas de pattern reconnu, retourner tel quel
    return name


def find_ai_page_for_strategy(strategy_name: str) -> Optional[Path]:
    """
    Trouve la page AI correspondante à une stratégie.
    
    Args:
        strategy_name: Nom de la stratégie (ex: SOM_UA_2311_G_4)
    
    Returns:
        Path vers la page AI si trouvée, None sinon
    """
    # Chercher directement le fichier
    ai_file = AI_DIR / f"{strategy_name}.html"
    
    if ai_file.exists():
        return ai_file
    
    # Si pas trouvé, chercher avec des variations
    # Parfois il peut y avoir des différences mineures dans le nommage
    for file in AI_DIR.glob("*.html"):
        if file.name.lower() == f"{strategy_name.lower()}.html":
            return file
    
    return None


def find_mc_page_for_strategy(strategy_name: str) -> Optional[Path]:
    """
    Trouve la page Monte Carlo correspondante à une stratégie.
    
    Args:
        strategy_name: Nom de la stratégie depuis AI (ex: SOM_UA_2311_G_4)
    
    Returns:
        Path vers la page MC si trouvée, None sinon
    """
    # Chercher les fichiers qui contiennent le nom de la stratégie
    pattern = f"*{strategy_name}_MC.html"
    
    for file in MC_INDIVIDUAL_DIR.glob(pattern):
        return file
    
    # Recherche plus large si pas trouvé
    for file in MC_INDIVIDUAL_DIR.glob("*.html"):
        extracted = extract_strategy_name_from_mc(file.name)
        if extracted and extracted.lower() == strategy_name.lower():
            return file
    
    return None


def remove_existing_markers(content: str) -> str:
    """Enlève les markers existants pour éviter les doublons."""
    pattern = f"{re.escape(MARKER_START)}.*?{re.escape(MARKER_END)}"
    return re.sub(pattern, "", content, flags=re.DOTALL)


def inject_after_header(content: str, injection: str) -> str:
    """
    Injecte du contenu après le header (après </header> ou au début du body).
    """
    # Chercher </header>
    header_match = re.search(r'</header>', content, re.IGNORECASE)
    if header_match:
        pos = header_match.end()
        return content[:pos] + "\n" + injection + "\n" + content[pos:]
    
    # Sinon, chercher <body> ou le début du container
    body_match = re.search(r'<body[^>]*>', content, re.IGNORECASE)
    if body_match:
        pos = body_match.end()
        return content[:pos] + "\n" + injection + "\n" + content[pos:]
    
    # En dernier recours, chercher <div class="container">
    container_match = re.search(r'<div class="container">', content, re.IGNORECASE)
    if container_match:
        pos = container_match.end()
        return content[:pos] + "\n" + injection + "\n" + content[pos:]
    
    # Si rien trouvé, retourner tel quel
    return content


def inject_in_style(content: str, css: str) -> str:
    """
    Injecte du CSS dans la balise <style> existante.
    """
    # Chercher la fin de la dernière balise </style>
    style_matches = list(re.finditer(r'</style>', content, re.IGNORECASE))
    
    if style_matches:
        # Injecter avant la dernière balise </style>
        last_match = style_matches[-1]
        pos = last_match.start()
        return content[:pos] + "\n" + css + "\n" + content[pos:]
    
    # Si pas de </style>, chercher </head> et créer une balise style
    head_match = re.search(r'</head>', content, re.IGNORECASE)
    if head_match:
        pos = head_match.start()
        style_block = f"\n<style>{css}</style>\n"
        return content[:pos] + style_block + content[pos:]
    
    return content

# =============================================================================
# ENRICHISSEMENT DES PAGES
# =============================================================================

def enrich_mc_summary_page():
    """
    Enrichit la page de synthèse Monte Carlo avec un bouton vers l'index.
    """
    print("\n[1/4] Enrichissement de la page de synthèse Monte Carlo...")
    
    if not MC_SUMMARY.exists():
        print(f"   ❌ Fichier introuvable: {MC_SUMMARY}")
        return False
    
    content = MC_SUMMARY.read_text(encoding='utf-8')
    
    # Enlever les markers existants
    content = remove_existing_markers(content)
    
    # Injecter le CSS
    content = inject_in_style(content, BUTTON_CSS)
    
    # Créer le bouton
    button_html = f"""
{MARKER_START}
<div class="nav-buttons-container">
    <a href="../index.html" class="nav-button">
        🏠 Retour au Dashboard Principal
    </a>
</div>
{MARKER_END}
"""
    
    # Injecter après le header
    content = inject_after_header(content, button_html)
    
    # Sauvegarder
    MC_SUMMARY.write_text(content, encoding='utf-8')
    print(f"   ✅ Page enrichie: {MC_SUMMARY.name}")
    
    return True


def enrich_mc_individual_pages():
    """
    Enrichit chaque page individuelle Monte Carlo avec:
    - Bouton vers index principal
    - Lien vers page AI correspondante
    """
    print("\n[2/4] Enrichissement des pages individuelles Monte Carlo...")
    
    if not MC_INDIVIDUAL_DIR.exists():
        print(f"   ❌ Répertoire introuvable: {MC_INDIVIDUAL_DIR}")
        return 0
    
    mc_files = list(MC_INDIVIDUAL_DIR.glob("*.html"))
    enriched = 0
    linked_to_ai = 0
    
    for mc_file in mc_files:
        content = mc_file.read_text(encoding='utf-8')
        
        # Enlever les markers existants
        content = remove_existing_markers(content)
        
        # Injecter le CSS
        content = inject_in_style(content, BUTTON_CSS)
        
        # Extraire le nom de stratégie
        strategy_name = extract_strategy_name_from_mc(mc_file.name)
        
        # Chercher la page AI correspondante
        ai_page = find_ai_page_for_strategy(strategy_name) if strategy_name else None
        
        # Créer les boutons
        buttons = []
        buttons.append('<a href="../../index.html" class="nav-button">🏠 Dashboard Principal</a>')
        
        if ai_page:
            # Lien relatif vers la page AI
            rel_path = f"../../{ai_page.name}"
            buttons.append(f'<a href="{rel_path}" class="nav-button secondary">📊 Analyse AI</a>')
            linked_to_ai += 1
        
        button_html = f"""
{MARKER_START}
<div class="nav-buttons-container">
    {' '.join(buttons)}
</div>
{MARKER_END}
"""
        
        # Injecter après le lien de retour existant
        # Chercher le lien "← Retour au tableau de bord"
        back_link_match = re.search(
            r'<a[^>]*class="back-link"[^>]*>.*?</a>',
            content,
            re.IGNORECASE | re.DOTALL
        )
        
        if back_link_match:
            pos = back_link_match.end()
            content = content[:pos] + "\n" + button_html + "\n" + content[pos:]
        else:
            # Sinon injecter après le header
            content = inject_after_header(content, button_html)
        
        # Sauvegarder
        mc_file.write_text(content, encoding='utf-8')
        enriched += 1
    
    print(f"   ✅ {enriched} pages enrichies")
    print(f"   ✅ {linked_to_ai} pages liées à AI Analysis")
    
    return enriched


def enrich_ai_pages():
    """
    Met à jour les pages AI avec les liens corrects vers Monte Carlo.
    """
    print("\n[3/4] Mise à jour des pages AI Analysis...")
    
    # Lister toutes les pages AI (exclure index.html et dossiers)
    ai_files = [
        f for f in AI_DIR.glob("*.html")
        if f.is_file() and f.name != "index.html" and f.name != "all_strategies_montecarlo.html"
    ]
    
    updated = 0
    linked_to_mc = 0
    
    for ai_file in ai_files:
        content = ai_file.read_text(encoding='utf-8')
        
        # Enlever les markers existants
        content = remove_existing_markers(content)
        
        # Injecter le CSS si pas déjà présent
        if "nav-button" not in content:
            content = inject_in_style(content, BUTTON_CSS)
        
        # Extraire le nom de stratégie (c'est le nom du fichier sans .html)
        strategy_name = ai_file.stem
        
        # Chercher la page Monte Carlo correspondante
        mc_page = find_mc_page_for_strategy(strategy_name)
        
        # Chercher le lien Monte Carlo existant et le mettre à jour
        # Pattern: href="montecarlo/..." ou href="MonteCarlo/..."
        mc_link_pattern = r'href="[Mm]onte[Cc]arlo/[^"]*"'
        
        if mc_page:
            # Construire le nouveau lien relatif
            new_link = f'href="montecarlo/Individual/{mc_page.name}"'
            
            # Remplacer le lien existant
            if re.search(mc_link_pattern, content):
                content = re.sub(mc_link_pattern, new_link, content)
                linked_to_mc += 1
            else:
                # Si pas de lien existant, en créer un
                button_html = f"""
{MARKER_START}
<div class="nav-buttons-container">
    <a href="index.html" class="nav-button">🏠 Dashboard Principal</a>
    <a href="montecarlo/Individual/{mc_page.name}" class="nav-button secondary">🎲 Monte Carlo</a>
</div>
{MARKER_END}
"""
                content = inject_after_header(content, button_html)
                linked_to_mc += 1
        
        # Sauvegarder
        ai_file.write_text(content, encoding='utf-8')
        updated += 1
    
    print(f"   ✅ {updated} pages mises à jour")
    print(f"   ✅ {linked_to_mc} pages liées à Monte Carlo")
    
    return updated


def generate_report():
    """
    Génère un rapport de l'enrichissement.
    """
    print("\n[4/4] Génération du rapport...")
    
    report_lines = []
    report_lines.append("=" * 70)
    report_lines.append("RAPPORT D'ENRICHISSEMENT - Liens croisés Monte Carlo ↔ AI")
    report_lines.append("=" * 70)
    report_lines.append("")
    
    # Compter les fichiers
    mc_individual_count = len(list(MC_INDIVIDUAL_DIR.glob("*.html"))) if MC_INDIVIDUAL_DIR.exists() else 0
    ai_count = len([
        f for f in AI_DIR.glob("*.html")
        if f.is_file() and f.name != "index.html" and f.name != "all_strategies_montecarlo.html"
    ])
    
    report_lines.append("📊 STATISTIQUES:")
    report_lines.append(f"   • Page synthèse Monte Carlo: 1")
    report_lines.append(f"   • Pages individuelles Monte Carlo: {mc_individual_count}")
    report_lines.append(f"   • Pages AI Analysis: {ai_count}")
    report_lines.append("")
    
    report_lines.append("🔗 LIENS AJOUTÉS:")
    report_lines.append("   ✅ Page synthèse MC → Index principal")
    report_lines.append("   ✅ Pages individuelles MC → Index principal")
    report_lines.append("   ✅ Pages individuelles MC → Pages AI (si disponibles)")
    report_lines.append("   ✅ Pages AI → Pages MC individuelles (mis à jour)")
    report_lines.append("")
    
    report_lines.append("📁 EMPLACEMENTS:")
    report_lines.append(f"   • Index: {INDEX_FILE.relative_to(V2_ROOT)}")
    report_lines.append(f"   • MC Synthèse: {MC_SUMMARY.relative_to(V2_ROOT)}")
    report_lines.append(f"   • MC Individuelles: {MC_INDIVIDUAL_DIR.relative_to(V2_ROOT)}")
    report_lines.append(f"   • AI Pages: {AI_DIR.relative_to(V2_ROOT)}")
    report_lines.append("")
    
    report_lines.append("🎨 STYLE:")
    report_lines.append("   • Boutons dégradés avec hover effects")
    report_lines.append("   • Responsive design")
    report_lines.append("   • Intégration harmonieuse avec le design existant")
    report_lines.append("")
    
    report_lines.append("=" * 70)
    report_lines.append("✅ ENRICHISSEMENT TERMINÉ")
    report_lines.append("=" * 70)
    
    report = "\n".join(report_lines)
    
    # Sauvegarder le rapport
    report_file = V2_ROOT / "RAPPORT_ENRICHISSEMENT_LIENS.txt"
    report_file.write_text(report, encoding='utf-8')
    
    print(report)
    print(f"\n📄 Rapport sauvegardé: {report_file.name}")

# =============================================================================
# MAIN
# =============================================================================

def main():
    """Point d'entrée principal du script."""
    
    print("=" * 70)
    print("ENRICHISSEMENT DES PAGES HTML - Liens croisés Monte Carlo ↔ AI")
    print("=" * 70)
    
    # Vérifier les répertoires
    if not HTML_ROOT.exists():
        print(f"\n❌ ERREUR: Répertoire HTML introuvable: {HTML_ROOT}")
        return 1
    
    # 1. Enrichir la page de synthèse Monte Carlo
    enrich_mc_summary_page()
    
    # 2. Enrichir les pages individuelles Monte Carlo
    enrich_mc_individual_pages()
    
    # 3. Mettre à jour les pages AI
    enrich_ai_pages()
    
    # 4. Générer le rapport
    generate_report()
    
    return 0


if __name__ == "__main__":
    exit(main())
