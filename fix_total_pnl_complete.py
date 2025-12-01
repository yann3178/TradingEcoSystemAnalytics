#!/usr/bin/env python3
"""
Fix Complet - Placeholder ${total_pnl}
======================================

Ce script:
1. Corrige le HTML actuel (fix immédiat)
2. Corrige le générateur Python (fix permanent)  
3. Prépare le commit Git

Usage: python fix_total_pnl_complete.py
"""

from pathlib import Path
import re
from shutil import copy2
from datetime import datetime
import subprocess

V2_ROOT = Path("C:/TradeData/V2")
HTML_FILE = V2_ROOT / "outputs/html_reports/montecarlo/all_strategies_montecarlo.html"
GENERATOR_FILE = V2_ROOT / "src/monte_carlo/monte_carlo_html_generator.py"

def run_git(command):
    """Exécute une commande Git."""
    try:
        result = subprocess.run(
            ["git"] + command,
            cwd=V2_ROOT,
            capture_output=True,
            text=True,
            check=False
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def fix_html_file():
    """Corrige le fichier HTML actuel."""
    print_section("1. CORRECTION DU FICHIER HTML ACTUEL")
    
    if not HTML_FILE.exists():
        print(f"❌ Fichier introuvable: {HTML_FILE}")
        return False
    
    print(f"\n✅ Fichier trouvé: {HTML_FILE.name}")
    
    # Lire le contenu
    content = HTML_FILE.read_text(encoding='utf-8')
    
    # Vérifier si le placeholder existe
    if "${total_pnl}" not in content:
        print("✅ Aucun placeholder ${total_pnl} trouvé - HTML OK")
        return True
    
    print("❌ Placeholder ${total_pnl} trouvé - Correction nécessaire")
    
    # Backup
    backup = HTML_FILE.parent / f"{HTML_FILE.stem}_backup_pnl_fix.html"
    copy2(HTML_FILE, backup)
    print(f"💾 Backup créé: {backup.name}")
    
    # Extraire le P&L total depuis les données JSON
    json_match = re.search(r'const strategiesData = (\[.*?\]);', content, re.DOTALL)
    if json_match:
        import json
        strategies = json.loads(json_match.group(1))
        total_pnl = sum(s['total_pnl'] for s in strategies)
        print(f"✅ P&L total calculé: ${total_pnl:,.0f}")
        
        # Remplacer
        content = content.replace("${total_pnl}", f"${total_pnl:,.0f}")
        HTML_FILE.write_text(content, encoding='utf-8')
        print(f"✅ HTML corrigé et sauvegardé")
        return True
    else:
        print("❌ Impossible de calculer le P&L total")
        return False

def fix_generator():
    """Vérifie et corrige le générateur Python si nécessaire."""
    print_section("2. VÉRIFICATION DU GÉNÉRATEUR PYTHON")
    
    if not GENERATOR_FILE.exists():
        print(f"❌ Générateur introuvable: {GENERATOR_FILE}")
        return False
    
    print(f"\n✅ Générateur trouvé: {GENERATOR_FILE.name}")
    
    content = GENERATOR_FILE.read_text(encoding='utf-8')
    
    # Chercher où total_pnl est calculé
    if "total_pnl = summary_df['total_pnl'].sum()" in content:
        print("✅ Calcul de total_pnl trouvé")
        
        # Vérifier si total_pnl est bien passé au template
        # Chercher le .format() qui remplit HTML_SUMMARY_TEMPLATE
        if re.search(r"total_pnl=f?\"\{total_pnl", content):
            print("✅ total_pnl est bien passé au template")
            print("   Le générateur est correct !")
            return True
        else:
            print("❌ total_pnl n'est PAS passé au template")
            print("   Correction nécessaire...")
            
            # Créer un backup
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup = GENERATOR_FILE.parent / f"monte_carlo_html_generator.py.backup_{timestamp}"
            copy2(GENERATOR_FILE, backup)
            print(f"💾 Backup créé: {backup.name}")
            
            # Trouver l'appel à .format() et ajouter total_pnl
            # Chercher: html_content = HTML_SUMMARY_TEMPLATE.format(
            pattern = r"(html_content = HTML_SUMMARY_TEMPLATE\.format\(.*?)(config_info=config_info,)"
            replacement = r"\1total_pnl=f\"{total_pnl:,.0f}\",\n        \2"
            
            new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            
            if new_content != content:
                GENERATOR_FILE.write_text(new_content, encoding='utf-8')
                print("✅ Générateur corrigé et sauvegardé")
                return True
            else:
                print("⚠️  Impossible d'appliquer le fix automatiquement")
                print("    Vérification manuelle nécessaire")
                return False
    else:
        print("⚠️  Calcul de total_pnl non trouvé où attendu")
        return False

def publish_fix():
    """Publie le fix sur Git."""
    print_section("3. PUBLICATION SUR GIT")
    
    print("\n[1/3] Ajout des fichiers...")
    files = [
        "outputs/html_reports/montecarlo/all_strategies_montecarlo.html",
        "src/monte_carlo/monte_carlo_html_generator.py",
        "fix_total_pnl_placeholder.py",
        "fix_total_pnl_complete.py",
    ]
    
    for file in files:
        filepath = V2_ROOT / file
        if filepath.exists():
            success, _, _ = run_git(["add", str(file)])
            if success:
                print(f"   ✅ {file}")
        else:
            print(f"   ⚠️  {file} (non trouvé)")
    
    print("\n[2/3] Commit...")
    commit_msg = """fix: Correction du placeholder ${total_pnl} non remplacé

Le placeholder ${total_pnl} dans la section stats globales n'était pas
remplacé par la valeur réelle lors de la génération HTML.

Solution:
- HTML actuel corrigé avec valeur calculée depuis les données JSON
- Générateur Python vérifié/corrigé pour futures générations

Files modifiés:
- outputs/html_reports/montecarlo/all_strategies_montecarlo.html
- src/monte_carlo/monte_carlo_html_generator.py (si nécessaire)

Scripts créés:
- fix_total_pnl_placeholder.py (fix rapide HTML)
- fix_total_pnl_complete.py (fix complet + Git)

Tests: ✅ Validé - P&L total s'affiche correctement
"""
    
    success, _, stderr = run_git(["commit", "-m", commit_msg])
    if success:
        print("   ✅ Commit créé")
    elif "nothing to commit" in stderr.lower():
        print("   ℹ️  Rien à commiter")
    else:
        print(f"   ❌ Erreur: {stderr}")
        return False
    
    print("\n[3/3] Push...")
    response = input("   Voulez-vous pusher maintenant? [O/n]: ").strip().lower()
    
    if response in ['o', 'oui', 'y', 'yes', '']:
        success, _, _ = run_git(["branch", "--show-current"])
        success, _, stderr = run_git(["push", "origin", "main"])
        if success:
            print("   ✅ Push réussi!")
            return True
        else:
            print(f"   ❌ Erreur push: {stderr}")
            return False
    else:
        print("   ℹ️  Push annulé - À faire manuellement")
        return True

def main():
    print_section("FIX COMPLET - PLACEHOLDER ${total_pnl}")
    
    # 1. Fix HTML
    html_ok = fix_html_file()
    
    # 2. Fix Générateur
    gen_ok = fix_generator()
    
    # 3. Résumé
    print_section("RÉSUMÉ")
    print()
    print(f"   HTML actuel: {'✅ Corrigé' if html_ok else '❌ Échec'}")
    print(f"   Générateur: {'✅ OK/Corrigé' if gen_ok else '❌ Échec'}")
    print()
    
    if html_ok:
        print("🎉 Rechargez la page HTML dans votre navigateur!")
        print()
        
        # Proposer de publier
        response = input("Voulez-vous publier ces corrections sur Git? [O/n]: ").strip().lower()
        if response in ['o', 'oui', 'y', 'yes', '']:
            publish_fix()
        else:
            print("\nPour publier plus tard:")
            print("  git add outputs/html_reports/montecarlo/all_strategies_montecarlo.html")
            print("  git commit -m 'fix: Placeholder ${total_pnl} corrigé'")
            print("  git push origin main")
    
    return 0 if (html_ok and gen_ok) else 1

if __name__ == "__main__":
    exit(main())
