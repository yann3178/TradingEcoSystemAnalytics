#!/usr/bin/env python3
"""
PLAN DE NETTOYAGE - Dashboard Monte Carlo V2.1
==============================================

Ce script analyse les fichiers et propose un plan de nettoyage
pour établir une baseline propre après les modifications.

Exécution: python PLAN_NETTOYAGE.py
"""

from pathlib import Path
from datetime import datetime

V2_ROOT = Path(__file__).parent
MC_DIR = V2_ROOT / "src" / "monte_carlo"

def format_size(size_bytes):
    """Formatte la taille en KB"""
    return f"{size_bytes / 1024:.1f} KB"

def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

print_section("ANALYSE DES FICHIERS - Dashboard Monte Carlo V2.1")

# =============================================================================
# ANALYSE DU RÉPERTOIRE monte_carlo/
# =============================================================================

print("\n📁 Répertoire: src/monte_carlo/")
print("-" * 70)

mc_files = {
    'À CONSERVER (Production)': [
        'config.py',
        'data_loader.py',
        'simulator.py',
        'monte_carlo_html_generator.py',  # Sera remplacé par v2.1
        'html_templates.py',
        '__init__.py',
    ],
    
    'BACKUPS (À conserver pour sécurité)': [
        'config.py.backup',
        'html_templates.py.backup',
    ],
    
    'VERSIONS INTERMÉDIAIRES (Peuvent être supprimées)': [
        'monte_carlo_html_generator_v2.py',
        'monte_carlo_html_generator_v3.py',
        'monte_carlo_html_generator_v2.1.py',  # Après migration
        'html_templates_NEW.py',
        'html_templates_FINAL.py',
    ],
    
    'DOCUMENTATION (À conserver)': [
        'README_HTML_GENERATOR.md',
        'README_V2.md',
        'README_V3.md',
        'README_VERSIONS.md',
    ],
    
    'ANCIENS SCRIPTS (Peuvent être archivés)': [
        'v1_batch_monte_carlo.py',
        'v1_batch_visualizer.py',
    ],
}

# Analyser les fichiers présents
for category, files in mc_files.items():
    print(f"\n{category}:")
    for filename in files:
        filepath = MC_DIR / filename
        if filepath.exists():
            size = format_size(filepath.stat().st_size)
            print(f"   ✅ {filename:45s} ({size})")
        else:
            print(f"   ⚪ {filename:45s} (absent)")

# =============================================================================
# ANALYSE DU RÉPERTOIRE RACINE
# =============================================================================

print("\n\n📁 Répertoire: Racine V2/")
print("-" * 70)

root_files = {
    'SCRIPTS DE MIGRATION (Peuvent être archivés)': [
        'finalize_templates.py',
        'test_config_import.py',
        'create_backups.py',
        'GUIDE_VALIDATION.py',
    ],
    
    'DOCUMENTATION (À conserver)': [
        'MODIFICATIONS_DASHBOARD_MC.md',
        'CHANGELOG.md',
        'README.md',
        'IMPLEMENTATION_RECAP.md',
    ],
    
    'SCRIPTS UTILITAIRES (Selon usage)': [
        'add_mc_banners.py',
        'add_method.py',
        'analyze_non_renamed.py',
        'check_summary_names.py',
        'diagnose_mc_files.py',
        'fix_html_templates_final.py',
        'fix_template_braces.py',
        'migrate_ai_html_names.py',
        'migrate_data.py',
        'migrate_v1_analysis.py',
        'restore_simple_version.py',
        'restore_template_git.py',
        'rollback_migration.py',
        'verify_migration.py',
    ],
}

for category, files in root_files.items():
    print(f"\n{category}:")
    for filename in files:
        filepath = V2_ROOT / filename
        if filepath.exists():
            size = format_size(filepath.stat().st_size)
            print(f"   ✅ {filename:45s} ({size})")
        else:
            print(f"   ⚪ {filename:45s} (absent)")

# =============================================================================
# RECOMMANDATIONS
# =============================================================================

print_section("RECOMMANDATIONS DE NETTOYAGE")

print("""
📌 STRATÉGIE RECOMMANDÉE:

1. MIGRATION DU GÉNÉRATEUR (OBLIGATOIRE)
   ----------------------------------------
   Remplacer le générateur actuel par la version V2.1:
   
   cd C:\\TradeData\\V2\\src\\monte_carlo
   
   # Créer un backup final de l'ancien générateur
   copy monte_carlo_html_generator.py monte_carlo_html_generator_v2.0_BACKUP.py
   
   # Remplacer par la nouvelle version
   copy monte_carlo_html_generator_v2.1.py monte_carlo_html_generator.py
   
   # Vérifier que tout fonctionne
   python monte_carlo_html_generator.py
   

2. ARCHIVAGE DES VERSIONS INTERMÉDIAIRES (RECOMMANDÉ)
   ---------------------------------------------------
   Créer un dossier d'archives pour les versions intermédiaires:
   
   mkdir src\\monte_carlo\\archive
   move src\\monte_carlo\\monte_carlo_html_generator_v2.py archive\\
   move src\\monte_carlo\\monte_carlo_html_generator_v3.py archive\\
   move src\\monte_carlo\\html_templates_NEW.py archive\\
   move src\\monte_carlo\\html_templates_FINAL.py archive\\
   move src\\monte_carlo\\v1_batch_monte_carlo.py archive\\
   move src\\monte_carlo\\v1_batch_visualizer.py archive\\


3. ARCHIVAGE DES SCRIPTS DE MIGRATION (OPTIONNEL)
   ------------------------------------------------
   Créer un dossier pour les scripts de migration:
   
   mkdir migration_v2.1
   move finalize_templates.py migration_v2.1\\
   move test_config_import.py migration_v2.1\\
   move create_backups.py migration_v2.1\\
   move GUIDE_VALIDATION.py migration_v2.1\\
   
   OU les supprimer si vous êtes confiant:
   del finalize_templates.py
   del test_config_import.py
   del create_backups.py
   del GUIDE_VALIDATION.py


4. NETTOYAGE DES SCRIPTS UTILITAIRES (OPTIONNEL)
   -----------------------------------------------
   Analyser les scripts de migration/fix et décider:
   - Garder si encore utilisés
   - Archiver si potentiellement utiles
   - Supprimer si obsolètes
   
   Liste des candidats à l'archivage/suppression:
   • fix_html_templates_final.py
   • fix_template_braces.py
   • restore_simple_version.py
   • restore_template_git.py
   • rollback_migration.py


5. CONSERVATION DES BACKUPS (OBLIGATOIRE)
   ----------------------------------------
   NE PAS SUPPRIMER:
   ✅ config.py.backup
   ✅ html_templates.py.backup
   ✅ monte_carlo_html_generator_v2.0_BACKUP.py (après création)
   
   Ces fichiers permettent de revenir en arrière si besoin.


6. DOCUMENTATION (À CONSERVER)
   ----------------------------
   Garder tous les fichiers de documentation:
   ✅ MODIFICATIONS_DASHBOARD_MC.md
   ✅ CHANGELOG.md
   ✅ README*.md
   ✅ IMPLEMENTATION_RECAP.md

""")

print_section("STRUCTURE CIBLE APRÈS NETTOYAGE")

print("""
src/monte_carlo/
├── config.py                          [Production]
├── config.py.backup                   [Backup]
├── data_loader.py                     [Production]
├── simulator.py                       [Production]
├── monte_carlo_html_generator.py      [Production - V2.1]
├── monte_carlo_html_generator_v2.0_BACKUP.py [Backup]
├── html_templates.py                  [Production]
├── html_templates.py.backup           [Backup]
├── __init__.py                        [Production]
├── README_HTML_GENERATOR.md           [Doc]
├── README_V2.md                       [Doc]
├── README_V3.md                       [Doc]
├── README_VERSIONS.md                 [Doc]
└── archive/                           [Archive]
    ├── monte_carlo_html_generator_v2.py
    ├── monte_carlo_html_generator_v3.py
    ├── monte_carlo_html_generator_v2.1.py
    ├── html_templates_NEW.py
    ├── html_templates_FINAL.py
    ├── v1_batch_monte_carlo.py
    └── v1_batch_visualizer.py

Racine V2/
├── MODIFICATIONS_DASHBOARD_MC.md      [Doc]
├── CHANGELOG.md                       [Doc]
├── README.md                          [Doc]
├── IMPLEMENTATION_RECAP.md            [Doc]
├── run_pipeline.py                    [Production]
├── ... (autres scripts de production)
└── migration_v2.1/                    [Archive - Optionnel]
    ├── finalize_templates.py
    ├── test_config_import.py
    ├── create_backups.py
    └── GUIDE_VALIDATION.py

""")

print_section("COMMANDES DE NETTOYAGE AUTOMATIQUE")

print("""
Voulez-vous que je génère un script PowerShell qui effectue
le nettoyage automatiquement ?

Le script proposera:
1. Migration du générateur vers V2.1
2. Archivage des versions intermédiaires
3. Archivage des scripts de migration
4. Vérification de la présence des backups

Réponse: [Oui / Non]
""")

input("Appuyez sur ENTRÉE pour continuer...")

# =============================================================================
# GÉNÉRATION DU SCRIPT DE NETTOYAGE
# =============================================================================

print("\nGénération du script de nettoyage automatique...")

cleanup_script = """
@echo off
REM Script de nettoyage automatique - Dashboard Monte Carlo V2.1
REM Généré le: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """

echo ========================================================================
echo NETTOYAGE AUTOMATIQUE - Dashboard Monte Carlo V2.1
echo ========================================================================
echo.

cd /d C:\\TradeData\\V2

REM =========================================================================
REM 1. MIGRATION DU GÉNÉRATEUR
REM =========================================================================
echo [1/5] Migration du générateur vers V2.1...

cd src\\monte_carlo

if exist monte_carlo_html_generator.py (
    copy monte_carlo_html_generator.py monte_carlo_html_generator_v2.0_BACKUP.py
    echo    - Backup créé: monte_carlo_html_generator_v2.0_BACKUP.py
)

if exist monte_carlo_html_generator_v2.1.py (
    copy /Y monte_carlo_html_generator_v2.1.py monte_carlo_html_generator.py
    echo    - Générateur mis à jour vers V2.1
) else (
    echo    - ERREUR: monte_carlo_html_generator_v2.1.py introuvable!
    pause
    exit /b 1
)

echo    - OK
echo.

REM =========================================================================
REM 2. ARCHIVAGE DES VERSIONS INTERMÉDIAIRES
REM =========================================================================
echo [2/5] Archivage des versions intermédiaires...

if not exist archive mkdir archive

if exist monte_carlo_html_generator_v2.py (
    move monte_carlo_html_generator_v2.py archive\\
    echo    - Archivé: monte_carlo_html_generator_v2.py
)

if exist monte_carlo_html_generator_v3.py (
    move monte_carlo_html_generator_v3.py archive\\
    echo    - Archivé: monte_carlo_html_generator_v3.py
)

if exist monte_carlo_html_generator_v2.1.py (
    move monte_carlo_html_generator_v2.1.py archive\\
    echo    - Archivé: monte_carlo_html_generator_v2.1.py
)

if exist html_templates_NEW.py (
    move html_templates_NEW.py archive\\
    echo    - Archivé: html_templates_NEW.py
)

if exist html_templates_FINAL.py (
    move html_templates_FINAL.py archive\\
    echo    - Archivé: html_templates_FINAL.py
)

if exist v1_batch_monte_carlo.py (
    move v1_batch_monte_carlo.py archive\\
    echo    - Archivé: v1_batch_monte_carlo.py
)

if exist v1_batch_visualizer.py (
    move v1_batch_visualizer.py archive\\
    echo    - Archivé: v1_batch_visualizer.py
)

echo    - OK
echo.

REM =========================================================================
REM 3. ARCHIVAGE DES SCRIPTS DE MIGRATION (Racine)
REM =========================================================================
echo [3/5] Archivage des scripts de migration...

cd ..\\..

if not exist migration_v2.1 mkdir migration_v2.1

if exist finalize_templates.py (
    move finalize_templates.py migration_v2.1\\
    echo    - Archivé: finalize_templates.py
)

if exist test_config_import.py (
    move test_config_import.py migration_v2.1\\
    echo    - Archivé: test_config_import.py
)

if exist create_backups.py (
    move create_backups.py migration_v2.1\\
    echo    - Archivé: create_backups.py
)

if exist GUIDE_VALIDATION.py (
    move GUIDE_VALIDATION.py migration_v2.1\\
    echo    - Archivé: GUIDE_VALIDATION.py
)

echo    - OK
echo.

REM =========================================================================
REM 4. VÉRIFICATION DES BACKUPS
REM =========================================================================
echo [4/5] Vérification des backups de sécurité...

cd src\\monte_carlo

set BACKUP_OK=1

if not exist config.py.backup (
    echo    - MANQUANT: config.py.backup
    set BACKUP_OK=0
) else (
    echo    - OK: config.py.backup
)

if not exist html_templates.py.backup (
    echo    - MANQUANT: html_templates.py.backup
    set BACKUP_OK=0
) else (
    echo    - OK: html_templates.py.backup
)

if not exist monte_carlo_html_generator_v2.0_BACKUP.py (
    echo    - MANQUANT: monte_carlo_html_generator_v2.0_BACKUP.py
    set BACKUP_OK=0
) else (
    echo    - OK: monte_carlo_html_generator_v2.0_BACKUP.py
)

if %BACKUP_OK%==0 (
    echo.
    echo    - ATTENTION: Certains backups sont manquants!
)

echo.

REM =========================================================================
REM 5. TEST DE GÉNÉRATION
REM =========================================================================
echo [5/5] Test de génération (optionnel)...
echo    Voulez-vous tester la génération maintenant? [O/N]
choice /C ON /N

if errorlevel 2 goto :skip_test

python monte_carlo_html_generator.py

if errorlevel 1 (
    echo    - ERREUR lors de la génération!
    echo    - Consultez les messages d'erreur ci-dessus
    pause
    exit /b 1
) else (
    echo    - Génération réussie!
)

:skip_test

echo.
echo ========================================================================
echo NETTOYAGE TERMINÉ
echo ========================================================================
echo.
echo Structure finale:
echo   src/monte_carlo/
echo     - monte_carlo_html_generator.py (V2.1 - Production)
echo     - html_templates.py (V2.1 - Production)
echo     - config.py (V2.1 - Production)
echo     - archive/ (versions intermédiaires)
echo   
echo   Racine V2/
echo     - migration_v2.1/ (scripts de migration)
echo.
echo Backups de sécurité:
echo   - config.py.backup
echo   - html_templates.py.backup
echo   - monte_carlo_html_generator_v2.0_BACKUP.py
echo.
pause
"""

cleanup_file = V2_ROOT / "NETTOYAGE_AUTO.bat"
cleanup_file.write_text(cleanup_script, encoding='utf-8')

print(f"✅ Script de nettoyage créé: {cleanup_file.name}")
print()
print("Pour exécuter le nettoyage automatique:")
print(f"   {cleanup_file}")
print()
print("OU effectuer le nettoyage manuellement en suivant les recommandations ci-dessus.")
