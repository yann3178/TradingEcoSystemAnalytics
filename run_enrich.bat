@echo off
echo ============================================================
echo  Trading Strategy Pipeline V2 - Enrichissement
echo ============================================================
echo.

cd /d "%~dp0"

REM Vérifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou pas dans le PATH
    pause
    exit /b 1
)

REM Exécuter l'enrichissement
python run_enrich.py %*

echo.
pause
