#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de restauration Git pour html_templates.py
"""
import subprocess
from pathlib import Path

def run_git_command(cmd, cwd):
    """Execute une commande git."""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        shell=True
    )
    return result.returncode, result.stdout, result.stderr

def main():
    repo_dir = Path("C:/TradeData/V2")
    file_path = "src/monte_carlo/html_templates.py"
    
    print("=" * 80)
    print("RESTAURATION GIT - html_templates.py")
    print("=" * 80)
    
    # Vérifier le statut actuel
    print("\n📊 Statut Git actuel...")
    rc, out, err = run_git_command(f"git status {file_path}", repo_dir)
    print(out)
    
    # Voir les derniers commits
    print("\n📜 Derniers commits affectant ce fichier:")
    rc, out, err = run_git_command(f"git log --oneline -5 -- {file_path}", repo_dir)
    print(out)
    
    # Demander confirmation
    print("\n" + "=" * 80)
    print("ATTENTION: Cette opération va restaurer le fichier à la dernière version Git")
    print("=" * 80)
    choice = input("\nContinuer? (oui/non): ").strip().lower()
    
    if choice != "oui":
        print("\n❌ Restauration annulée")
        return
    
    # Restaurer
    print("\n🔄 Restauration en cours...")
    rc, out, err = run_git_command(f"git checkout HEAD -- {file_path}", repo_dir)
    
    if rc == 0:
        print("✅ Fichier restauré avec succès!")
        print(f"\n📁 {file_path} est maintenant à la version Git")
    else:
        print(f"❌ Erreur lors de la restauration:")
        print(err)
    
    print("\n" + "=" * 80)
    print("Vous pouvez maintenant relancer la génération HTML")
    print("=" * 80)

if __name__ == "__main__":
    main()
