@echo off
REM Script de nettoyage automatique - Dashboard Monte Carlo V2.1
REM Date: 2025-12-01

echo ========================================================================
echo NETTOYAGE AUTOMATIQUE - Dashboard Monte Carlo V2.1
echo ========================================================================
echo.

cd /d C:\TradeData\V2

REM =========================================================================
REM 1. MIGRATION DU GÉNÉRATEUR
REM =========================================================================
echo [1/5] Migration du generateur vers V2.1...

cd src\monte_carlo

if exist monte_carlo_html_generator.py (
    copy monte_carlo_html_generator.py monte_carlo_html_generator_v2.0_BACKUP.py
    echo    - Backup cree: monte_carlo_html_generator_v2.0_BACKUP.py
)

if exist monte_carlo_html_generator_v2.1.py (
    copy /Y monte_carlo_html_generator_v2.1.py monte_carlo_html_generator.py
    echo    - Generateur mis a jour vers V2.1
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
echo [2/5] Archivage des versions intermediaires...

if not exist archive mkdir archive

if exist monte_carlo_html_generator_v2.py (
    move monte_carlo_html_generator_v2.py archive\
    echo    - Archive: monte_carlo_html_generator_v2.py
)

if exist monte_carlo_html_generator_v3.py (
    move monte_carlo_html_generator_v3.py archive\
    echo    - Archive: monte_carlo_html_generator_v3.py
)

if exist monte_carlo_html_generator_v2.1.py (
    move monte_carlo_html_generator_v2.1.py archive\
    echo    - Archive: monte_carlo_html_generator_v2.1.py
)

if exist html_templates_NEW.py (
    move html_templates_NEW.py archive\
    echo    - Archive: html_templates_NEW.py
)

if exist html_templates_FINAL.py (
    move html_templates_FINAL.py archive\
    echo    - Archive: html_templates_FINAL.py
)

if exist v1_batch_monte_carlo.py (
    move v1_batch_monte_carlo.py archive\
    echo    - Archive: v1_batch_monte_carlo.py
)

if exist v1_batch_visualizer.py (
    move v1_batch_visualizer.py archive\
    echo    - Archive: v1_batch_visualizer.py
)

echo    - OK
echo.

REM =========================================================================
REM 3. ARCHIVAGE DES SCRIPTS DE MIGRATION (Racine)
REM =========================================================================
echo [3/5] Archivage des scripts de migration...

cd ..\..

if not exist migration_v2.1 mkdir migration_v2.1

if exist finalize_templates.py (
    move finalize_templates.py migration_v2.1\
    echo    - Archive: finalize_templates.py
)

if exist test_config_import.py (
    move test_config_import.py migration_v2.1\
    echo    - Archive: test_config_import.py
)

if exist create_backups.py (
    move create_backups.py migration_v2.1\
    echo    - Archive: create_backups.py
)

if exist GUIDE_VALIDATION.py (
    move GUIDE_VALIDATION.py migration_v2.1\
    echo    - Archive: GUIDE_VALIDATION.py
)

if exist PLAN_NETTOYAGE.py (
    move PLAN_NETTOYAGE.py migration_v2.1\
    echo    - Archive: PLAN_NETTOYAGE.py
)

echo    - OK
echo.

REM =========================================================================
REM 4. VÉRIFICATION DES BACKUPS
REM =========================================================================
echo [4/5] Verification des backups de securite...

cd src\monte_carlo

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
echo [5/5] Test de generation (optionnel)...
echo    Voulez-vous tester la generation maintenant? [O/N]
choice /C ON /N

if errorlevel 2 goto :skip_test

python monte_carlo_html_generator.py

if errorlevel 1 (
    echo    - ERREUR lors de la generation!
    echo    - Consultez les messages d'erreur ci-dessus
    pause
    exit /b 1
) else (
    echo    - Generation reussie!
)

:skip_test

echo.
echo ========================================================================
echo NETTOYAGE TERMINE
echo ========================================================================
echo.
echo Structure finale:
echo   src/monte_carlo/
echo     - monte_carlo_html_generator.py (V2.1 - Production)
echo     - html_templates.py (V2.1 - Production)
echo     - config.py (V2.1 - Production)
echo     - archive/ (versions intermediaires)
echo.
echo   Racine V2/
echo     - migration_v2.1/ (scripts de migration)
echo.
echo Backups de securite:
echo   - config.py.backup
echo   - html_templates.py.backup
echo   - monte_carlo_html_generator_v2.0_BACKUP.py
echo.
pause
