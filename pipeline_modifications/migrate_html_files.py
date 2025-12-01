"""
Script de Migration Physique des Fichiers HTML
===============================================
Déplace les fichiers HTML depuis leur emplacement actuel vers la nouvelle
architecture unifiée outputs/html_reports/

Usage:
    python migrate_html_files.py              # Dry-run (aperçu seulement)
    python migrate_html_files.py --apply      # Déplacer réellement

Auteur: Trading Analytics Pipeline V2
Date: 2025-11-30
Version: 1.0.0
"""

import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
import argparse


# =============================================================================
# CONFIGURATION
# =============================================================================

V2_ROOT = Path(__file__).parent.parent
OUTPUTS_DIR = V2_ROOT / "outputs"

# Chemins source (anciens)
SOURCE_PATHS = {
    "ai_analysis": OUTPUTS_DIR / "ai_analysis" / "html_reports",
    "correlation": OUTPUTS_DIR / "correlation",
    "correlation_pages_full": OUTPUTS_DIR / "correlation_pages_full",
    "monte_carlo": OUTPUTS_DIR / "monte_carlo",
}

# Chemins destination (nouveaux)
DEST_PATHS = {
    "html_reports": OUTPUTS_DIR / "html_reports",
    "correlation_dashboards": OUTPUTS_DIR / "html_reports" / "correlation" / "dashboards",
    "correlation_pages": OUTPUTS_DIR / "html_reports" / "correlation" / "pages",
    "montecarlo_dashboards": OUTPUTS_DIR / "html_reports" / "montecarlo" / "dashboards",
    "montecarlo_individual": OUTPUTS_DIR / "html_reports" / "montecarlo" / "individual",
}


# =============================================================================
# FONCTIONS DE MIGRATION
# =============================================================================

def is_dashboard_file(filepath: Path) -> bool:
    """Détermine si un fichier HTML est un dashboard ou une page individuelle."""
    name = filepath.name.lower()
    # Les dashboards contiennent généralement "dashboard", "index", ou ont un timestamp
    if "dashboard" in name or "index" in name:
        return True
    # Pattern: correlation_20241130_1430.html
    if re.match(r'.*_\d{8}_\d{4}\.html$', name):
        return True
    return False


def migrate_ai_analysis_html(dry_run: bool = True) -> Dict[str, any]:
    """
    Migre les HTML de ai_analysis/html_reports/ vers html_reports/
    
    Returns:
        Dict avec statistiques de migration
    """
    result = {
        "source": "ai_analysis/html_reports",
        "destination": "html_reports",
        "files_found": 0,
        "files_moved": 0,
        "files_skipped": 0,
        "errors": []
    }
    
    source = SOURCE_PATHS["ai_analysis"]
    dest = DEST_PATHS["html_reports"]
    
    if not source.exists():
        result["errors"].append(f"Source inexistante: {source}")
        return result
    
    # Créer destination
    if not dry_run:
        dest.mkdir(parents=True, exist_ok=True)
    
    # Lister tous les HTML
    html_files = list(source.glob("*.html"))
    result["files_found"] = len(html_files)
    
    for html_file in html_files:
        dest_file = dest / html_file.name
        
        # Vérifier si déjà existant
        if dest_file.exists():
            result["files_skipped"] += 1
            continue
        
        # Déplacer
        if not dry_run:
            try:
                shutil.move(str(html_file), str(dest_file))
                result["files_moved"] += 1
            except Exception as e:
                result["errors"].append(f"{html_file.name}: {e}")
        else:
            result["files_moved"] += 1  # Simulation
    
    return result


def migrate_correlation_html(dry_run: bool = True) -> Dict[str, any]:
    """
    Migre les HTML de correlation vers html_reports/correlation/
    Sépare dashboards et pages individuelles.
    
    Returns:
        Dict avec statistiques de migration
    """
    result = {
        "source": "correlation + correlation_pages_full",
        "destination": "html_reports/correlation",
        "dashboards_found": 0,
        "dashboards_moved": 0,
        "pages_found": 0,
        "pages_moved": 0,
        "errors": []
    }
    
    dest_dashboards = DEST_PATHS["correlation_dashboards"]
    dest_pages = DEST_PATHS["correlation_pages"]
    
    if not dry_run:
        dest_dashboards.mkdir(parents=True, exist_ok=True)
        dest_pages.mkdir(parents=True, exist_ok=True)
    
    # Parcourir tous les emplacements sources
    for source_key in ["correlation", "correlation_pages_full"]:
        source = SOURCE_PATHS[source_key]
        
        if not source.exists():
            continue
        
        html_files = list(source.glob("*.html"))
        
        for html_file in html_files:
            # Déterminer si dashboard ou page
            is_dashboard = is_dashboard_file(html_file)
            
            if is_dashboard:
                result["dashboards_found"] += 1
                dest_file = dest_dashboards / html_file.name
            else:
                result["pages_found"] += 1
                dest_file = dest_pages / html_file.name
            
            # Vérifier si déjà existant
            if dest_file.exists():
                continue
            
            # Déplacer
            if not dry_run:
                try:
                    shutil.move(str(html_file), str(dest_file))
                    if is_dashboard:
                        result["dashboards_moved"] += 1
                    else:
                        result["pages_moved"] += 1
                except Exception as e:
                    result["errors"].append(f"{html_file.name}: {e}")
            else:
                if is_dashboard:
                    result["dashboards_moved"] += 1
                else:
                    result["pages_moved"] += 1
    
    return result


def migrate_montecarlo_html(dry_run: bool = True) -> Dict[str, any]:
    """
    Migre les HTML de monte_carlo vers html_reports/montecarlo/
    
    Returns:
        Dict avec statistiques de migration
    """
    result = {
        "source": "monte_carlo",
        "destination": "html_reports/montecarlo",
        "dashboards_found": 0,
        "dashboards_moved": 0,
        "individual_found": 0,
        "individual_moved": 0,
        "errors": []
    }
    
    source = SOURCE_PATHS["monte_carlo"]
    dest_dashboards = DEST_PATHS["montecarlo_dashboards"]
    dest_individual = DEST_PATHS["montecarlo_individual"]
    
    if not source.exists():
        result["errors"].append(f"Source inexistante: {source}")
        return result
    
    if not dry_run:
        dest_dashboards.mkdir(parents=True, exist_ok=True)
        dest_individual.mkdir(parents=True, exist_ok=True)
    
    # Parcourir tous les HTML
    for html_file in source.rglob("*.html"):
        # Déterminer si dashboard ou page individuelle
        is_dashboard = is_dashboard_file(html_file)
        
        if is_dashboard:
            result["dashboards_found"] += 1
            dest_file = dest_dashboards / html_file.name
        else:
            result["individual_found"] += 1
            dest_file = dest_individual / html_file.name
        
        # Vérifier si déjà existant
        if dest_file.exists():
            continue
        
        # Déplacer
        if not dry_run:
            try:
                shutil.move(str(html_file), str(dest_file))
                if is_dashboard:
                    result["dashboards_moved"] += 1
                else:
                    result["individual_moved"] += 1
            except Exception as e:
                result["errors"].append(f"{html_file.name}: {e}")
        else:
            if is_dashboard:
                result["dashboards_moved"] += 1
            else:
                result["individual_moved"] += 1
    
    return result


def cleanup_empty_directories(dry_run: bool = True) -> List[str]:
    """
    Nettoie les répertoires vides après migration.
    
    Returns:
        Liste des répertoires supprimés
    """
    cleaned = []
    
    for key, path in SOURCE_PATHS.items():
        if path.exists() and path.is_dir():
            # Vérifier si vide (sauf sous-dossiers backup)
            items = list(path.glob("*"))
            items = [i for i in items if not i.name.startswith("backup")]
            
            if len(items) == 0:
                if not dry_run:
                    # Ne supprimer que le dossier html_reports dans ai_analysis
                    if key == "ai_analysis":
                        shutil.rmtree(path)
                        cleaned.append(str(path.relative_to(V2_ROOT)))
                else:
                    cleaned.append(str(path.relative_to(V2_ROOT)))
    
    return cleaned


# =============================================================================
# MAIN
# =============================================================================

import re

def main():
    parser = argparse.ArgumentParser(
        description="Migration physique des fichiers HTML vers nouvelle architecture"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Appliquer réellement la migration (défaut: dry-run)"
    )
    args = parser.parse_args()
    
    dry_run = not args.apply
    mode_text = "DRY-RUN (aperçu)" if dry_run else "MIGRATION RÉELLE"
    
    print("=" * 80)
    print(f"  MIGRATION PHYSIQUE DES FICHIERS HTML")
    print("=" * 80)
    print(f"\nMode: {mode_text}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nRacine: {V2_ROOT}")
    print()
    
    # Phase 1: Migration AI Analysis
    print("\n" + "─" * 80)
    print("  PHASE 1: Migration AI Analysis HTML")
    print("─" * 80 + "\n")
    
    result_ai = migrate_ai_analysis_html(dry_run)
    print(f"📁 Source: {result_ai['source']}")
    print(f"📁 Destination: {result_ai['destination']}")
    print(f"📄 Fichiers trouvés: {result_ai['files_found']}")
    print(f"✅ Fichiers déplacés: {result_ai['files_moved']}")
    if result_ai['files_skipped'] > 0:
        print(f"⏭️  Fichiers ignorés (déjà présents): {result_ai['files_skipped']}")
    if result_ai['errors']:
        print(f"❌ Erreurs: {len(result_ai['errors'])}")
        for err in result_ai['errors'][:5]:
            print(f"   • {err}")
    
    # Phase 2: Migration Correlation
    print("\n" + "─" * 80)
    print("  PHASE 2: Migration Correlation HTML")
    print("─" * 80 + "\n")
    
    result_corr = migrate_correlation_html(dry_run)
    print(f"📁 Source: {result_corr['source']}")
    print(f"📁 Destination: {result_corr['destination']}")
    print(f"\n📊 Dashboards:")
    print(f"   Trouvés: {result_corr['dashboards_found']}")
    print(f"   Déplacés: {result_corr['dashboards_moved']}")
    print(f"\n📄 Pages individuelles:")
    print(f"   Trouvées: {result_corr['pages_found']}")
    print(f"   Déplacées: {result_corr['pages_moved']}")
    if result_corr['errors']:
        print(f"\n❌ Erreurs: {len(result_corr['errors'])}")
        for err in result_corr['errors'][:5]:
            print(f"   • {err}")
    
    # Phase 3: Migration Monte Carlo
    print("\n" + "─" * 80)
    print("  PHASE 3: Migration Monte Carlo HTML")
    print("─" * 80 + "\n")
    
    result_mc = migrate_montecarlo_html(dry_run)
    print(f"📁 Source: {result_mc['source']}")
    print(f"📁 Destination: {result_mc['destination']}")
    print(f"\n📊 Dashboards:")
    print(f"   Trouvés: {result_mc['dashboards_found']}")
    print(f"   Déplacés: {result_mc['dashboards_moved']}")
    print(f"\n📄 Pages individuelles:")
    print(f"   Trouvées: {result_mc['individual_found']}")
    print(f"   Déplacées: {result_mc['individual_moved']}")
    if result_mc['errors']:
        print(f"\n❌ Erreurs: {len(result_mc['errors'])}")
        for err in result_mc['errors'][:5]:
            print(f"   • {err}")
    
    # Phase 4: Nettoyage
    print("\n" + "─" * 80)
    print("  PHASE 4: Nettoyage des répertoires vides")
    print("─" * 80 + "\n")
    
    cleaned = cleanup_empty_directories(dry_run)
    if cleaned:
        print(f"🗑️  Répertoires nettoyés: {len(cleaned)}")
        for c in cleaned:
            print(f"   • {c}")
    else:
        print("✓ Aucun répertoire vide à nettoyer")
    
    # Résumé final
    total_moved = (
        result_ai['files_moved'] +
        result_corr['dashboards_moved'] + result_corr['pages_moved'] +
        result_mc['dashboards_moved'] + result_mc['individual_moved']
    )
    
    total_errors = (
        len(result_ai['errors']) +
        len(result_corr['errors']) +
        len(result_mc['errors'])
    )
    
    print("\n" + "=" * 80)
    print(f"  RÉSUMÉ FINAL")
    print("=" * 80)
    print(f"\n✅ Total fichiers déplacés: {total_moved}")
    print(f"🗑️  Répertoires nettoyés: {len(cleaned)}")
    
    if total_errors > 0:
        print(f"❌ Erreurs rencontrées: {total_errors}")
    
    if dry_run:
        print(f"\n⚠️  MODE DRY-RUN: Aucun fichier n'a été déplacé")
        print(f"   Pour appliquer réellement, exécutez:")
        print(f"   python {Path(__file__).name} --apply")
    else:
        print(f"\n✅ Migration terminée avec succès!")
        print(f"\n📋 Structure créée:")
        print(f"   outputs/html_reports/")
        print(f"   ├── *.html (stratégies AI Analysis)")
        print(f"   ├── correlation/")
        print(f"   │   ├── dashboards/")
        print(f"   │   └── pages/")
        print(f"   └── montecarlo/")
        print(f"       ├── dashboards/")
        print(f"       └── individual/")
        print(f"\n📋 Prochaine étape:")
        print(f"   python validate_directory_migration.py")
    
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
