#!/usr/bin/env python3
"""
Script de finalisation des templates HTML
Copie l'INDIVIDUAL_TEMPLATE de l'original et ajoute le nouveau SUMMARY_TEMPLATE
"""

from pathlib import Path

MC_DIR = Path(__file__).parent / "src" / "monte_carlo"
original_file = MC_DIR / "html_templates.py"
new_file = MC_DIR / "html_templates_NEW.py"
final_file = MC_DIR / "html_templates_FINAL.py"
backup_file = MC_DIR / "html_templates.py.backup"

print("=" * 70)
print("FINALISATION DES TEMPLATES HTML")
print("=" * 70)
print()

# 1. Lire l'original pour extraire l'INDIVIDUAL_TEMPLATE
print("1. Lecture de l'INDIVIDUAL_TEMPLATE original...")
original_content = original_file.read_text(encoding='utf-8')

# Extraire l'INDIVIDUAL_TEMPLATE (tout ce qui est avant SUMMARY_TEMPLATE)
individual_start = original_content.find('INDIVIDUAL_TEMPLATE = """')
summary_start = original_content.find('SUMMARY_TEMPLATE = """')

if individual_start == -1 or summary_start == -1:
    print("   ❌ Impossible de trouver les templates dans l'original")
    exit(1)

# Extraire INDIVIDUAL_TEMPLATE complet
individual_template_section = original_content[individual_start:summary_start].strip()
print(f"   ✅ INDIVIDUAL_TEMPLATE extrait ({len(individual_template_section)} caractères)")

# 2. Lire le nouveau SUMMARY_TEMPLATE
print("\n2. Lecture du nouveau SUMMARY_TEMPLATE...")
new_content = new_file.read_text(encoding='utf-8')

# Extraire le nouveau SUMMARY_TEMPLATE
new_summary_start = new_content.find('SUMMARY_TEMPLATE = """')
if new_summary_start == -1:
    print("   ❌ Impossible de trouver SUMMARY_TEMPLATE dans le nouveau fichier")
    exit(1)

new_summary_section = new_content[new_summary_start:].strip()
print(f"   ✅ Nouveau SUMMARY_TEMPLATE extrait ({len(new_summary_section)} caractères)")

# 3. Créer le fichier final
print("\n3. Création du fichier final...")

header = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Templates HTML pour les rapports Monte Carlo V2.1
Nouveau SUMMARY_TEMPLATE avec dashboard interactif
"""

'''

final_content = header + individual_template_section + "\n\n" + new_summary_section

final_file.write_text(final_content, encoding='utf-8')
print(f"   ✅ Fichier final créé : {final_file.name}")
print(f"   Taille : {len(final_content) / 1024:.1f} KB")

# 4. Créer le backup si pas déjà fait
if not backup_file.exists():
    print("\n4. Création du backup...")
    from shutil import copy2
    copy2(original_file, backup_file)
    print(f"   ✅ Backup créé : {backup_file.name}")
else:
    print(f"\n4. Backup déjà existant : {backup_file.name}")

print("\n" + "=" * 70)
print("✅ FINALISATION TERMINÉE")
print("=" * 70)
print()
print("Prochaines étapes:")
print("  1. Vérifier le fichier html_templates_FINAL.py")
print("  2. Si OK, le renommer en html_templates.py")
print("  3. Tester la génération")
print()
