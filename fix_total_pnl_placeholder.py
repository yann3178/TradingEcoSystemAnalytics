#!/usr/bin/env python3
"""
Fix du placeholder ${total_pnl} non remplacé
============================================

Ce script corrige le bug où ${total_pnl} n'est pas remplacé
dans le fichier HTML généré.
"""

from pathlib import Path
import re
from shutil import copy2

HTML_FILE = Path("C:/TradeData/V2/outputs/html_reports/montecarlo/all_strategies_montecarlo.html")

print("=" * 70)
print("FIX DU PLACEHOLDER ${total_pnl}")
print("=" * 70)
print()

# 1. Vérifier que le fichier existe
if not HTML_FILE.exists():
    print(f"❌ Fichier introuvable: {HTML_FILE}")
    exit(1)

print(f"✅ Fichier trouvé: {HTML_FILE.name}")

# 2. Lire le contenu
print("📝 Lecture du fichier...")
content = HTML_FILE.read_text(encoding='utf-8')

# 3. Chercher le placeholder
if "${total_pnl}" in content:
    print("❌ PROBLÈME TROUVÉ: Placeholder ${total_pnl} non remplacé!")
    print()
    
    # Trouver le contexte
    idx = content.find("${total_pnl}")
    start = max(0, idx - 150)
    end = min(len(content), idx + 150)
    print("Contexte:")
    print("-" * 70)
    print(content[start:end])
    print("-" * 70)
    print()
    
    # 4. Créer un backup
    print("💾 Création d'un backup...")
    backup = HTML_FILE.parent / f"{HTML_FILE.stem}_backup_pnl_fix.html"
    copy2(HTML_FILE, backup)
    print(f"✅ Backup: {backup.name}")
    print()
    
    # 5. Calculer le P&L total depuis le tableau
    print("🔍 Calcul du P&L total depuis le tableau HTML...")
    
    # Extraire toutes les lignes du tableau
    table_rows = re.findall(r'<td>\$([0-9,.-]+)</td>', content)
    
    # Les P&L sont dans la 6ème colonne (index 5)
    # Pattern: strategy | symbol | status | capital | trades | PNL | ...
    # On doit extraire tous les P&L (qui sont en position spécifique)
    
    # Méthode alternative: chercher toutes les valeurs de P&L dans le JavaScript
    js_match = re.search(r"'total_pnl':\s*([-\d.]+)", content)
    if js_match:
        total_pnl = float(js_match.group(1))
        print(f"   ✓ P&L total trouvé dans les données JS: ${total_pnl:,.0f}")
    else:
        # Fallback: extraire du tableau
        # Chercher les données JSON strateg ies
        json_match = re.search(r'const strategiesData = (\[.*?\]);', content, re.DOTALL)
        if json_match:
            import json
            strategies = json.loads(json_match.group(1))
            total_pnl = sum(s['total_pnl'] for s in strategies)
            print(f"   ✓ P&L total calculé depuis JSON: ${total_pnl:,.0f}")
        else:
            print("   ⚠️ Impossible de calculer automatiquement, utilisation d'une valeur par défaut")
            total_pnl = 0
    
    # 6. Remplacer le placeholder
    print(f"\n🔧 Remplacement de ${{total_pnl}} par ${total_pnl:,.0f}...")
    content = content.replace("${total_pnl}", f"${total_pnl:,.0f}")
    
    # 7. Sauvegarder
    print("💾 Sauvegarde du fichier corrigé...")
    HTML_FILE.write_text(content, encoding='utf-8')
    print(f"✅ Fichier sauvegardé: {HTML_FILE.name}")
    print()
    
    print("=" * 70)
    print("✅ CORRECTION TERMINÉE")
    print("=" * 70)
    print()
    print(f"P&L Total affiché: ${total_pnl:,.0f}")
    print(f"Backup disponible: {backup.name}")
    print()
    print("🧪 Rechargez la page dans votre navigateur pour voir le changement!")
    
else:
    print("✅ Aucun placeholder ${total_pnl} trouvé - Le fichier est OK")
    print()
