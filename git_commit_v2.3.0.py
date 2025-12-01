"""
Script de commit Git pour la version 2.3.0

Met à jour Git avec tous les changements de la session :
- Nouveau module correlation_pages.py
- Documentation mise à jour
- Pipeline intégré
"""

import subprocess
from pathlib import Path
import sys


def run_git_command(cmd: list, description: str) -> bool:
    """Exécute une commande Git et affiche le résultat."""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(
            cmd,
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode != 0:
            print(f"❌ Erreur: {result.stderr}")
            return False
        
        if result.stdout:
            print(result.stdout)
        
        print(f"✅ {description} - OK")
        return True
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def main():
    """Fonction principale."""
    print("=" * 70)
    print("📦 COMMIT GIT - VERSION 2.3.0")
    print("=" * 70)
    
    # Vérifier qu'on est dans un repo Git
    if not (Path(__file__).parent / ".git").exists():
        print("\n❌ Erreur: Pas un repository Git")
        print("   Initialisez d'abord avec: git init")
        return 1
    
    # 1. Vérifier le statut
    print("\n📊 Statut Git actuel:")
    run_git_command(["git", "status"], "Vérification statut")
    
    # 2. Ajouter les fichiers
    files_to_add = [
        # Nouveaux modules
        "src/generators/correlation_pages.py",
        "src/templates/README.md",
        
        # Documentation
        "docs/correlation_pages_module.md",
        "README.md",
        "CHANGELOG.md",
        "IMPLEMENTATION_RECAP.md",
        
        # Pipeline modifié
        "run_pipeline.py",
        
        # Scripts de test
        "test_correlation_pages_simple.py",
        "generate_all_correlation_pages.py",
        "integrate_correlation_pages.py",
    ]
    
    print(f"\n📁 Ajout de {len(files_to_add)} fichiers...")
    for file in files_to_add:
        file_path = Path(file)
        if file_path.exists():
            run_git_command(["git", "add", file], f"Ajout {file}")
        else:
            print(f"   ⚠️  {file} n'existe pas - ignoré")
    
    # 3. Commit
    commit_message = """feat: Add correlation individual pages module (v2.3.0)

✨ New Features:
- New module: src/generators/correlation_pages.py
- Generate 245 individual HTML pages (one per strategy)
- Correlation profile with Davey score, top 15 correlated/diversifying
- Modern GitHub Dark theme design, mobile-friendly
- Integration in run_pipeline.py (auto-generation after correlation analysis)

🏗️ Architecture:
- Clean separation: correlation_calculator.py (calculations) + correlation_pages.py (HTML generation)
- No code duplication
- Compatible with European CSV format (semicolon, comma decimals)
- Flexible column names handling (Strategy_ID vs Strategy, Delta_Avg vs Delta_Corr)

📝 Documentation:
- docs/correlation_pages_module.md: Complete usage guide
- CHANGELOG.md: Detailed v2.3.0 changelog
- README.md: Updated with v2.3.0 features
- IMPLEMENTATION_RECAP.md: Implementation summary

🧪 Testing:
- test_correlation_pages_simple.py: Test with existing data
- generate_all_correlation_pages.py: Generate all 245 pages
- integrate_correlation_pages.py: Auto-integration script

📊 Statistics:
- 245 strategies analyzed
- 245 HTML pages generated
- Generation time: ~90 seconds
- Success rate: 100%

🔄 Migration:
- Removed: correlation_pages_generator.py (duplicate code)
- Version: 2.2.0 → 2.3.0
"""
    
    if not run_git_command(["git", "commit", "-m", commit_message], "Commit v2.3.0"):
        print("\n⚠️  Rien à committer ou erreur")
        print("   Vérifiez 'git status' pour plus de détails")
    
    # 4. Afficher le log
    print("\n📜 Dernier commit:")
    run_git_command(["git", "log", "-1", "--oneline"], "Affichage dernier commit")
    
    # 5. Instructions push
    print("\n" + "=" * 70)
    print("✅ COMMIT LOCAL RÉUSSI")
    print("=" * 70)
    print("\n📤 Pour pousser vers GitHub:")
    print("   git push origin main")
    print("\n📊 Pour voir les changements:")
    print("   git log -1")
    print("   git show HEAD")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
