"""
Script de Réorganisation HTML - Architecture Directories V2
============================================================
Réorganise les fichiers HTML déjà partiellement migrés dans html_reports/
pour créer la structure finale conforme.

Situation actuelle détectée :
- Correlation pages: déjà dans html_reports/ (245 fichiers *_correlation.html)
- Correlation dashboards: dans correlation/ (6 fichiers)
- Monte Carlo: déjà dans html_reports/MonteCarlo/ (249 fichiers)

Cible :
- html_reports/correlation/dashboards/
- html_reports/correlation/pages/
- html_reports/montecarlo/dashboards/
- html_reports/montecarlo/individual/

Usage:
    python reorganize_html_structure.py              # Dry-run (aperçu)
    python reorganize_html_structure.py --apply      # Appliquer

Auteur: Trading Analytics Pipeline V2
Date: 2025-11-30
Version: 1.0.0
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime
import argparse


# =============================================================================
# CONFIGURATION
# =============================================================================

V2_ROOT = Path(__file__).parent.parent
OUTPUTS_DIR = V2_ROOT / "outputs"
HTML_REPORTS_DIR = OUTPUTS_DIR / "html_reports"

# Sources
CORRELATION_DIR = OUTPUTS_DIR / "correlation"
CORRELATION_PAGES_FULL = OUTPUTS_DIR / "correlation_pages_full"
MONTECARLO_OLD_DIR = HTML_REPORTS_DIR / "MonteCarlo"
MONTE_CARLO_SOURCE = OUTPUTS_DIR / "monte_carlo"

# Destinations
HTML_CORRELATION_DIR = HTML_REPORTS_DIR / "correlation"
HTML_CORRELATION_DASHBOARDS = HTML_CORRELATION_DIR / "dashboards"
HTML_CORRELATION_PAGES = HTML_CORRELATION_DIR / "pages"

HTML_MONTECARLO_DIR = HTML_REPORTS_DIR / "montecarlo"
HTML_MONTECARLO_DASHBOARDS = HTML_MONTECARLO_DIR / "dashboards"
HTML_MONTECARLO_INDIVIDUAL = HTML_MONTECARLO_DIR / "individual"


# =============================================================================
# DÉTECTION DE TYPE
# =============================================================================

def is_dashboard_file(filename: str) -> bool:
    """
    Détermine si un fichier HTML est un dashboard (vs page individuelle).
    
    Critères:
    - Nom contient "dashboard" ou "index"
    - Nom contient un timestamp _YYYYMMDD_HHMM
    """
    lower = filename.lower()
    
    # Pattern dashboard
    if "dashboard" in lower or "index" in lower:
        return True
    
    # Pattern timestamp (ex: correlation_dashboard_20251130_2145.html)
    timestamp_pattern = re.compile(r'_\d{8}_\d{4}\.html$')
    if timestamp_pattern.search(filename):
        return True
    
    return False


def is_correlation_page(filename: str) -> bool:
    """
    Détermine si un fichier est une page de corrélation individuelle.
    
    Critères:
    - Nom se termine par _correlation.html ou _SYMBOL_correlation.html
    """
    lower = filename.lower()
    return "_correlation.html" in lower and not is_dashboard_file(filename)


# =============================================================================
# PHASE 1: RÉORGANISER CORRELATION
# =============================================================================

def reorganize_correlation_html(dry_run: bool = True) -> dict:
    """
    Réorganise les fichiers correlation déjà dans html_reports/
    et migre les dashboards depuis correlation/
    """
    stats = {
        "pages_moved": 0,
        "dashboards_from_correlation": 0,
        "dashboards_from_html_reports": 0,
        "errors": [],
    }
    
    print("─" * 80)
    print("  PHASE 1: Réorganisation Correlation HTML")
    print("─" * 80)
    
    # Créer structure
    if not dry_run:
        HTML_CORRELATION_DASHBOARDS.mkdir(parents=True, exist_ok=True)
        HTML_CORRELATION_PAGES.mkdir(parents=True, exist_ok=True)
    
    # 1. Déplacer les pages individuelles de html_reports/ → correlation/pages/
    print(f"\n📄 Déplacement pages individuelles:")
    print(f"   Source: {HTML_REPORTS_DIR}")
    print(f"   Destination: {HTML_CORRELATION_PAGES}")
    
    if HTML_REPORTS_DIR.exists():
        for file in HTML_REPORTS_DIR.glob("*_correlation.html"):
            if is_correlation_page(file.name):
                dest = HTML_CORRELATION_PAGES / file.name
                
                if not dest.exists() or not dry_run:
                    try:
                        if not dry_run:
                            shutil.move(str(file), str(dest))
                        stats["pages_moved"] += 1
                        print(f"   ✓ {file.name}")
                    except Exception as e:
                        stats["errors"].append(f"Page {file.name}: {e}")
                        print(f"   ✗ {file.name}: {e}")
    
    # 2. Migrer les dashboards de correlation/ → correlation/dashboards/
    print(f"\n📊 Migration dashboards depuis correlation/:")
    print(f"   Source: {CORRELATION_DIR}")
    print(f"   Destination: {HTML_CORRELATION_DASHBOARDS}")
    
    if CORRELATION_DIR.exists():
        for file in CORRELATION_DIR.glob("*.html"):
            if is_dashboard_file(file.name):
                dest = HTML_CORRELATION_DASHBOARDS / file.name
                
                if not dest.exists() or not dry_run:
                    try:
                        if not dry_run:
                            shutil.copy2(str(file), str(dest))  # Copy pour garder backup
                        stats["dashboards_from_correlation"] += 1
                        print(f"   ✓ {file.name}")
                    except Exception as e:
                        stats["errors"].append(f"Dashboard {file.name}: {e}")
                        print(f"   ✗ {file.name}: {e}")
    
    # 3. Déplacer dashboards qui seraient dans html_reports/
    print(f"\n📊 Vérification dashboards dans html_reports/:")
    if HTML_REPORTS_DIR.exists():
        dashboards_found = 0
        for file in HTML_REPORTS_DIR.glob("*.html"):
            if is_dashboard_file(file.name) and "correlation" in file.name.lower():
                dest = HTML_CORRELATION_DASHBOARDS / file.name
                
                if not dest.exists() or not dry_run:
                    try:
                        if not dry_run:
                            shutil.move(str(file), str(dest))
                        stats["dashboards_from_html_reports"] += 1
                        dashboards_found += 1
                        print(f"   ✓ {file.name}")
                    except Exception as e:
                        stats["errors"].append(f"Dashboard {file.name}: {e}")
                        print(f"   ✗ {file.name}: {e}")
        
        if dashboards_found == 0:
            print(f"   (Aucun dashboard trouvé)")
    
    return stats


# =============================================================================
# PHASE 2: RÉORGANISER MONTE CARLO
# =============================================================================

def reorganize_montecarlo_html(dry_run: bool = True) -> dict:
    """
    Renomme MonteCarlo/ → montecarlo/ et organise en dashboards/individual/
    """
    stats = {
        "individual_moved": 0,
        "dashboards_moved": 0,
        "folder_renamed": False,
        "errors": [],
    }
    
    print("\n" + "─" * 80)
    print("  PHASE 2: Réorganisation Monte Carlo HTML")
    print("─" * 80)
    
    # Créer structure
    if not dry_run:
        HTML_MONTECARLO_DASHBOARDS.mkdir(parents=True, exist_ok=True)
        HTML_MONTECARLO_INDIVIDUAL.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📁 Réorganisation: MonteCarlo/ → montecarlo/")
    
    if MONTECARLO_OLD_DIR.exists():
        print(f"   Source: {MONTECARLO_OLD_DIR}")
        print(f"   Destination dashboards: {HTML_MONTECARLO_DASHBOARDS}")
        print(f"   Destination individual: {HTML_MONTECARLO_INDIVIDUAL}")
        
        # 1. Dashboards à la racine de MonteCarlo/
        print(f"\n   📊 Dashboards (racine):")
        for file in MONTECARLO_OLD_DIR.glob("*.html"):
            # Tous les HTML à la racine sont des dashboards
            dest = HTML_MONTECARLO_DASHBOARDS / file.name
            
            if not dest.exists() or not dry_run:
                try:
                    if not dry_run:
                        shutil.copy2(str(file), str(dest))
                    stats["dashboards_moved"] += 1
                    print(f"      ✓ {file.name}")
                except Exception as e:
                    stats["errors"].append(f"Dashboard {file.name}: {e}")
                    print(f"      ✗ {file.name}: {e}")
        
        # 2. Pages individuelles dans MonteCarlo/Individual/
        individual_dir = MONTECARLO_OLD_DIR / "Individual"
        if individual_dir.exists():
            print(f"\n   📄 Pages individuelles (Individual/):")
            for file in individual_dir.glob("*.html"):
                dest = HTML_MONTECARLO_INDIVIDUAL / file.name
                
                if not dest.exists() or not dry_run:
                    try:
                        if not dry_run:
                            shutil.copy2(str(file), str(dest))
                        stats["individual_moved"] += 1
                        if stats["individual_moved"] <= 5:  # Afficher les 5 premiers
                            print(f"      ✓ {file.name}")
                        elif stats["individual_moved"] == 6:
                            print(f"      ... (+ {len(list(individual_dir.glob('*.html'))) - 5} autres fichiers)")
                    except Exception as e:
                        stats["errors"].append(f"Individual {file.name}: {e}")
                        if stats["individual_moved"] <= 5:
                            print(f"      ✗ {file.name}: {e}")
        
        # 3. Supprimer l'ancien dossier MonteCarlo/
        if not dry_run and stats["individual_moved"] + stats["dashboards_moved"] > 0:
            try:
                shutil.rmtree(MONTECARLO_OLD_DIR)
                stats["folder_renamed"] = True
                print(f"\n   ✓ Ancien dossier MonteCarlo/ supprimé")
            except Exception as e:
                stats["errors"].append(f"Suppression MonteCarlo/: {e}")
                print(f"\n   ✗ Erreur suppression: {e}")
    else:
        print(f"   ⚠️ Dossier MonteCarlo/ introuvable (déjà renommé ?)")
        
        # Vérifier si montecarlo/ existe déjà
        if HTML_MONTECARLO_DIR.exists():
            print(f"   ✓ Dossier montecarlo/ existe déjà")
            stats["folder_renamed"] = True
    
    return stats


# =============================================================================
# PHASE 3: NETTOYAGE
# =============================================================================

def cleanup_duplicates(dry_run: bool = True) -> dict:
    """
    Nettoie les doublons et dossiers obsolètes
    """
    stats = {
        "correlation_pages_full_removed": False,
        "empty_dirs_removed": 0,
        "errors": [],
    }
    
    print("\n" + "─" * 80)
    print("  PHASE 3: Nettoyage des doublons")
    print("─" * 80)
    
    # Supprimer correlation_pages_full/ (doublon)
    if CORRELATION_PAGES_FULL.exists():
        print(f"\n🗑️  Suppression: {CORRELATION_PAGES_FULL}")
        print(f"   (Doublon des pages déjà dans html_reports/correlation/pages/)")
        
        if not dry_run:
            try:
                shutil.rmtree(CORRELATION_PAGES_FULL)
                stats["correlation_pages_full_removed"] = True
                print(f"   ✓ Supprimé")
            except Exception as e:
                stats["errors"].append(f"Suppression correlation_pages_full: {e}")
                print(f"   ✗ Erreur: {e}")
        else:
            print(f"   (Dry-run: non supprimé)")
    
    # Nettoyer dossier correlation/ vide
    if CORRELATION_DIR.exists():
        try:
            remaining = list(CORRELATION_DIR.glob("*"))
            if len(remaining) == 0:
                print(f"\n🗑️  Suppression dossier vide: {CORRELATION_DIR}")
                if not dry_run:
                    CORRELATION_DIR.rmdir()
                    stats["empty_dirs_removed"] += 1
                    print(f"   ✓ Supprimé")
        except Exception as e:
            stats["errors"].append(f"Nettoyage correlation/: {e}")
    
    return stats


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Réorganisation de l'architecture HTML V2"
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
    print(f"  RÉORGANISATION HTML - ARCHITECTURE DIRECTORIES V2")
    print("=" * 80)
    print(f"\nMode: {mode_text}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nRacine: {V2_ROOT}")
    print(f"Outputs: {OUTPUTS_DIR}")
    
    # Phase 1: Correlation
    stats_correlation = reorganize_correlation_html(dry_run)
    
    # Phase 2: Monte Carlo
    stats_montecarlo = reorganize_montecarlo_html(dry_run)
    
    # Phase 3: Nettoyage
    stats_cleanup = cleanup_duplicates(dry_run)
    
    # Résumé final
    print("\n" + "=" * 80)
    print("  RÉSUMÉ FINAL")
    print("=" * 80)
    
    print("\n📊 Correlation:")
    print(f"   Pages déplacées: {stats_correlation['pages_moved']}")
    print(f"   Dashboards migrés (correlation/): {stats_correlation['dashboards_from_correlation']}")
    print(f"   Dashboards migrés (html_reports/): {stats_correlation['dashboards_from_html_reports']}")
    
    print("\n📊 Monte Carlo:")
    print(f"   Pages individuelles: {stats_montecarlo['individual_moved']}")
    print(f"   Dashboards: {stats_montecarlo['dashboards_moved']}")
    print(f"   Dossier renommé: {'✓' if stats_montecarlo['folder_renamed'] else '✗'}")
    
    print("\n🗑️  Nettoyage:")
    print(f"   correlation_pages_full/ supprimé: {'✓' if stats_cleanup['correlation_pages_full_removed'] else '✗'}")
    print(f"   Dossiers vides supprimés: {stats_cleanup['empty_dirs_removed']}")
    
    # Erreurs
    all_errors = (
        stats_correlation['errors'] +
        stats_montecarlo['errors'] +
        stats_cleanup['errors']
    )
    
    if all_errors:
        print("\n❌ Erreurs rencontrées:")
        for error in all_errors:
            print(f"   • {error}")
    
    # Instructions finales
    if dry_run:
        print("\n" + "─" * 80)
        print("⚠️  MODE DRY-RUN: Aucune modification appliquée")
        print("\nPour appliquer réellement:")
        print(f"   python {Path(__file__).name} --apply")
    else:
        print("\n" + "─" * 80)
        print("✅ Réorganisation terminée!")
        print("\n📋 Prochaines étapes:")
        print("   1. Vérifier la nouvelle structure:")
        print("      • html_reports/correlation/dashboards/")
        print("      • html_reports/correlation/pages/")
        print("      • html_reports/montecarlo/dashboards/")
        print("      • html_reports/montecarlo/individual/")
        print("   2. Valider: python validate_directory_migration.py")
        print("   3. Tester: python run_pipeline.py --step enrich --dry-run")
    
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
