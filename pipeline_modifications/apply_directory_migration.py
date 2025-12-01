"""
Script de Migration Automatique - Architecture Directories V2
==============================================================
Applique automatiquement toutes les modifications de chemins pour unifier
l'architecture HTML sous outputs/html_reports/

Usage:
    python apply_directory_migration.py              # Dry-run (aperçu seulement)
    python apply_directory_migration.py --apply      # Appliquer réellement

Auteur: Trading Analytics Pipeline V2
Date: 2025-11-30
Version: 1.0.1 (Corrected)
"""

import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
import argparse


# =============================================================================
# CONFIGURATION
# =============================================================================

V2_ROOT = Path(__file__).parent.parent
BACKUP_DIR = V2_ROOT / "pipeline_modifications" / "backups"

FILES_TO_MODIFY = [
    V2_ROOT / "config" / "settings.py",
    V2_ROOT / "src" / "analyzers" / "config.py",
    V2_ROOT / "src" / "generators" / "correlation_pages.py",
    V2_ROOT / "run_pipeline.py",
]


# =============================================================================
# MODIFICATIONS À APPLIQUER
# =============================================================================

MODIFICATIONS = {
    "config/settings.py": [
        {
            "description": "Supprimer AI_HTML_REPORTS_DIR obsolète",
            "search": re.compile(
                r'# AI Analysis HTML Reports.*?\n'
                r'AI_ANALYSIS_DIR = OUTPUT_ROOT / "ai_analysis"\n'
                r'AI_HTML_REPORTS_DIR = AI_ANALYSIS_DIR / "html_reports".*?\n'
                r'AI_INDEX_FILE = AI_HTML_REPORTS_DIR / "index\.html"',
                re.MULTILINE | re.DOTALL
            ),
            "replace": """# AI Analysis - CSV seulement
AI_ANALYSIS_DIR = OUTPUT_ROOT / "ai_analysis"
AI_ANALYSIS_CSV = AI_ANALYSIS_DIR / "strategies_ai_analysis.csv"
AI_TRACKING_FILE = AI_ANALYSIS_DIR / "strategy_tracking.json"

# LEGACY: Compatibilité migration (redirige vers html_reports/)
AI_HTML_REPORTS_DIR = HTML_REPORTS_DIR
AI_INDEX_FILE = HTML_INDEX_FILE""",
        },
        {
            "description": "Ajouter nouveaux chemins HTML",
            "search": re.compile(
                r'# Rapports HTML\n'
                r'HTML_REPORTS_DIR = OUTPUT_ROOT / "html_reports"\n'
                r'HTML_INDEX_FILE = HTML_REPORTS_DIR / "index\.html"',
                re.MULTILINE
            ),
            "replace": """# Rapports HTML - Architecture unifiée
HTML_REPORTS_DIR = OUTPUT_ROOT / "html_reports"
HTML_INDEX_FILE = HTML_REPORTS_DIR / "index.html"

# Sous-dossiers HTML
HTML_CORRELATION_DIR = HTML_REPORTS_DIR / "correlation"
HTML_CORRELATION_DASHBOARDS_DIR = HTML_CORRELATION_DIR / "dashboards"
HTML_CORRELATION_PAGES_DIR = HTML_CORRELATION_DIR / "pages"

HTML_MONTECARLO_DIR = HTML_REPORTS_DIR / "montecarlo"
HTML_MONTECARLO_DASHBOARDS_DIR = HTML_MONTECARLO_DIR / "dashboards"
HTML_MONTECARLO_INDIVIDUAL_DIR = HTML_MONTECARLO_DIR / "individual"

# Correlation - CSV seulement
CORRELATION_DIR = OUTPUT_ROOT / "correlation"

# Monte Carlo - CSV seulement
MONTE_CARLO_DIR = OUTPUT_ROOT / "monte_carlo" """,
        },
        {
            "description": "Mettre à jour ensure_directories()",
            "search": re.compile(
                r'def ensure_directories\(\):.*?'
                r'directories = \[(.*?)\]',
                re.MULTILINE | re.DOTALL
            ),
            "replace": lambda m: f"""def ensure_directories():
    \"\"\"Crée tous les répertoires nécessaires s'ils n'existent pas.\"\"\"
    directories = [
{m.group(1).rstrip()},
        
        # HTML Reports structure
        HTML_REPORTS_DIR,
        HTML_CORRELATION_DIR,
        HTML_CORRELATION_DASHBOARDS_DIR,
        HTML_CORRELATION_PAGES_DIR,
        HTML_MONTECARLO_DIR,
        HTML_MONTECARLO_DASHBOARDS_DIR,
        HTML_MONTECARLO_INDIVIDUAL_DIR,
    ]""",
        },
    ],
    
    "src/analyzers/config.py": [
        {
            "description": "Ajouter import HTML_REPORTS_DIR",
            "search": re.compile(
                r'from config\.settings import \((.*?)\)',
                re.MULTILINE | re.DOTALL
            ),
            "replace": lambda m: f"""from config.settings import (
{m.group(1).rstrip()},
    HTML_REPORTS_DIR, AI_ANALYSIS_DIR,
)""",
        },
        {
            "description": "Corriger html_reports_dir",
            "search": re.compile(
                r'html_reports_dir: Path = field\(default_factory=lambda: OUTPUT_ROOT / "ai_analysis" / "html_reports"\)',
                re.MULTILINE
            ),
            "replace": 'html_reports_dir: Path = field(default_factory=lambda: HTML_REPORTS_DIR)',
        },
        {
            "description": "Corriger output_dir",
            "search": re.compile(
                r'output_dir: Path = field\(default_factory=lambda: OUTPUT_ROOT / "ai_analysis"\)',
                re.MULTILINE
            ),
            "replace": 'output_dir: Path = field(default_factory=lambda: AI_ANALYSIS_DIR)',
        },
        {
            "description": "Corriger csv_output",
            "search": re.compile(
                r'csv_output: Path = field\(default_factory=lambda: OUTPUT_ROOT / "ai_analysis" / "strategies_ai_analysis\.csv"\)',
                re.MULTILINE
            ),
            "replace": 'csv_output: Path = field(default_factory=lambda: AI_ANALYSIS_DIR / "strategies_ai_analysis.csv")',
        },
        {
            "description": "Corriger tracking_file",
            "search": re.compile(
                r'tracking_file: Path = field\(default_factory=lambda: OUTPUT_ROOT / "ai_analysis" / "strategy_tracking\.json"\)',
                re.MULTILINE
            ),
            "replace": 'tracking_file: Path = field(default_factory=lambda: AI_ANALYSIS_DIR / "strategy_tracking.json")',
        },
    ],
    
    "src/generators/correlation_pages.py": [
        {
            "description": "Mettre à jour imports",
            "search": re.compile(
                r'from config\.settings import \((.*?)AI_HTML_REPORTS_DIR,(.*?)\)',
                re.MULTILINE | re.DOTALL
            ),
            "replace": lambda m: f"""from config.settings import (
{m.group(1)}HTML_CORRELATION_PAGES_DIR,{m.group(2)})""",
        },
        {
            "description": "Corriger html_reports_dir dans CorrelationPagesConfig",
            "search": re.compile(
                r'html_reports_dir: Path = AI_HTML_REPORTS_DIR',
                re.MULTILINE
            ),
            "replace": 'html_reports_dir: Path = HTML_CORRELATION_PAGES_DIR',
        },
    ],
    
    "run_pipeline.py": [
        {
            "description": "Ajouter imports HTML_CORRELATION_DIR, HTML_MONTECARLO_DIR",
            "search": re.compile(
                r'from config\.settings import \((.*?)\)',
                re.MULTILINE | re.DOTALL
            ),
            "replace": lambda m: f"""from config.settings import (
{m.group(1).rstrip()},
    HTML_CORRELATION_DIR, HTML_MONTECARLO_DIR,
)""",
        },
    ],
}


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def create_backup(file_path: Path) -> Path:
    """Crée un backup timestampé du fichier."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{file_path.stem}_backup_{timestamp}{file_path.suffix}"
    backup_path = BACKUP_DIR / backup_name
    shutil.copy2(file_path, backup_path)
    return backup_path


def apply_modification(
    content: str,
    search_pattern,
    replacement,
    description: str,
    dry_run: bool = True
) -> Tuple[str, bool]:
    """
    Applique une modification au contenu.
    
    Returns:
        Tuple (nouveau_contenu, succès)
    """
    if isinstance(search_pattern, re.Pattern):
        if callable(replacement):
            # Replacement est une fonction lambda
            match = search_pattern.search(content)
            if match:
                new_content = search_pattern.sub(replacement, content)
                return new_content, True
            else:
                return content, False
        else:
            # Replacement est une string
            new_content = search_pattern.sub(replacement, content)
            if new_content != content:
                return new_content, True
            else:
                return content, False
    else:
        # Simple string replacement
        if search_pattern in content:
            new_content = content.replace(search_pattern, replacement)
            return new_content, True
        else:
            return content, False


def process_file(
    file_path: Path,
    modifications: List[Dict],
    dry_run: bool = True
) -> Dict[str, any]:
    """
    Traite un fichier avec toutes ses modifications.
    
    Returns:
        Dict avec résultats détaillés
    """
    result = {
        "file": str(file_path.relative_to(V2_ROOT)),
        "exists": file_path.exists(),
        "backup": None,
        "modifications": [],
        "success": False,
    }
    
    if not file_path.exists():
        result["error"] = "Fichier introuvable"
        return result
    
    # Lire le contenu original
    try:
        original_content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        result["error"] = f"Erreur lecture: {e}"
        return result
    
    current_content = original_content
    applied_count = 0
    
    # Appliquer chaque modification
    for mod in modifications:
        new_content, success = apply_modification(
            current_content,
            mod["search"],
            mod["replace"],
            mod["description"],
            dry_run
        )
        
        mod_result = {
            "description": mod["description"],
            "applied": success,
        }
        
        if success:
            applied_count += 1
            current_content = new_content
        
        result["modifications"].append(mod_result)
    
    # Calculer les stats
    result["success"] = applied_count > 0
    result["applied_count"] = applied_count
    result["total_modifications"] = len(modifications)
    
    if result["success"] and not dry_run:
        # Créer backup
        backup_path = create_backup(file_path)
        result["backup"] = str(backup_path.relative_to(V2_ROOT))
        
        # Écrire le nouveau contenu
        try:
            file_path.write_text(current_content, encoding='utf-8')
        except Exception as e:
            result["error"] = f"Erreur écriture: {e}"
            result["success"] = False
    
    return result


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Migration automatique de l'architecture directories V2"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Appliquer réellement les modifications (défaut: dry-run)"
    )
    args = parser.parse_args()
    
    dry_run = not args.apply
    mode_text = "DRY-RUN (aperçu)" if dry_run else "APPLICATION RÉELLE"
    
    print("=" * 80)
    print(f"  MIGRATION AUTOMATIQUE - ARCHITECTURE DIRECTORIES V2")
    print("=" * 80)
    print(f"\nMode: {mode_text}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nRacine: {V2_ROOT}")
    
    if not dry_run:
        print(f"Backups: {BACKUP_DIR}")
    
    print(f"\nFichiers à traiter: {len(FILES_TO_MODIFY)}")
    print()
    
    # Traiter chaque fichier
    results = []
    for file_path in FILES_TO_MODIFY:
        rel_path = str(file_path.relative_to(V2_ROOT))
        if rel_path in MODIFICATIONS:
            mods = MODIFICATIONS[rel_path]
            result = process_file(file_path, mods, dry_run)
            results.append(result)
    
    # Afficher les résultats
    print("\n" + "=" * 80)
    print("  RÉSULTATS")
    print("=" * 80 + "\n")
    
    total_files = len(results)
    success_files = sum(1 for r in results if r["success"])
    total_mods = sum(r["applied_count"] for r in results)
    
    for result in results:
        status_icon = "✅" if result["success"] else "⚠️"
        print(f"{status_icon} {result['file']}")
        
        if not result["exists"]:
            print(f"   ❌ Fichier introuvable")
            continue
        
        if "error" in result:
            print(f"   ❌ {result['error']}")
            continue
        
        print(f"   📝 {result['applied_count']}/{result['total_modifications']} modifications appliquées")
        
        for mod in result["modifications"]:
            mod_icon = "✓" if mod["applied"] else "✗"
            print(f"      {mod_icon} {mod['description']}")
        
        if result.get("backup") and not dry_run:
            print(f"   💾 Backup: {result['backup']}")
        
        print()
    
    # Résumé final
    print("=" * 80)
    print(f"  RÉSUMÉ")
    print("=" * 80)
    print(f"\n✅ Fichiers traités: {success_files}/{total_files}")
    print(f"📝 Modifications appliquées: {total_mods}")
    
    if dry_run:
        print(f"\n⚠️  MODE DRY-RUN: Aucune modification n'a été appliquée")
        print(f"   Pour appliquer réellement, exécutez:")
        print(f"   python {Path(__file__).name} --apply")
    else:
        print(f"\n✅ Modifications appliquées avec succès!")
        print(f"💾 Backups créés dans: {BACKUP_DIR}")
        print(f"\n📋 Prochaines étapes:")
        print(f"   1. Vérifier les fichiers modifiés")
        print(f"   2. Exécuter: python migrate_html_files.py")
        print(f"   3. Valider: python validate_directory_migration.py")
    
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
