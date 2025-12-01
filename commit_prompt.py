"""
Commit final: ajout du prompt pour la prochaine session
"""

import subprocess
from pathlib import Path
import sys


def main():
    """Commit le fichier NEXT_SESSION_PROMPT.md"""
    print("=" * 70)
    print("📦 COMMIT FINAL - Prompt Prochaine Session")
    print("=" * 70)
    
    v2_root = Path(__file__).parent
    
    # Add
    print("\n📁 Ajout du fichier...")
    subprocess.run(
        ["git", "add", "docs/NEXT_SESSION_PROMPT.md"],
        cwd=v2_root,
        check=True
    )
    
    # Commit
    print("💾 Commit...")
    subprocess.run(
        ["git", "commit", "-m", 
         "docs: Add next session prompt for v2.4.0 development\n\n"
         "- Complete context and objectives\n"
         "- Detailed tasks with Git workflow\n"
         "- Critical constraints (large files handling)\n"
         "- Validation checklist"],
        cwd=v2_root,
        check=True
    )
    
    # Push
    print("📤 Push vers GitHub...")
    subprocess.run(
        ["git", "push", "origin", "main"],
        cwd=v2_root,
        check=True
    )
    
    print("\n✅ Commit réussi!")
    print("\n📄 Fichier ajouté: docs/NEXT_SESSION_PROMPT.md")
    print("🌐 Disponible sur GitHub")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
