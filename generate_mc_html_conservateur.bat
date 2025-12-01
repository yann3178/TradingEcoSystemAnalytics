@echo off
REM Configuration Conservatrice
REM Ruine ≤5% ET Return/DD ≥2.5 ET Prob>0 ≥85%

cd /d "%~dp0"

echo ================================================================================
echo CONFIGURATION: CONSERVATRICE
echo ================================================================================
echo Criteres: Ruine ≤5%% ET Return/DD ≥2.5 ET Probabilite positive ≥85%%
echo Recommande pour: Capital important, risque minimal
echo ================================================================================
echo.

python run_monte_carlo_html_generator.py --max-ruin 5 --min-return-dd 2.5 --min-prob-positive 85

echo.
pause
