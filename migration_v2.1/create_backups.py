#!/usr/bin/env python3
"""
Script de backup des fichiers avant modification
"""
from pathlib import Path
from shutil import copy2
from datetime import datetime

V2_ROOT = Path(__file__).parent
MC_DIR = V2_ROOT / "src" / "monte_carlo"

# Fichiers à sauvegarder
files_to_backup = [
    MC_DIR / "monte_carlo_html_generator.py",
    MC_DIR / "html_templates.py",
]

print("=" * 70)
print("CRÉATION DES BACKUPS")
print("=" * 70)
print()

for file_path in files_to_backup:
    if file_path.exists():
        backup_path = file_path.with_suffix(file_path.suffix + '.backup')
        copy2(file_path, backup_path)
        print(f"✅ {file_path.name}")
        print(f"   → {backup_path.name}")
    else:
        print(f"❌ {file_path.name} - INTROUVABLE")

print()
print("✅ Backups créés avec succès !")
