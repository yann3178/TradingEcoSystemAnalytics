@echo off
REM Configuration Simple: Ruine Seule
REM Ruine ≤10% (pas de contrainte sur Return/DD ni Prob>0)

cd /d "%~dp0"

echo ================================================================================
echo CONFIGURATION: SIMPLE (RUINE SEULE)
echo ================================================================================
echo Criteres: Ruine ≤10%% UNIQUEMENT
echo Pas de contrainte sur Return/DD ni Probabilite positive
echo Recommande pour: Voir toutes les strategies viables au seuil de ruine choisi
echo ================================================================================
echo.

python run_monte_carlo_html_generator.py --max-ruin 10

echo.
pause
