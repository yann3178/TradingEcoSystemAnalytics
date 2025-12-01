@echo off
REM Configuration Kevin Davey Classique Complete
REM Ruine ≤10% ET Return/DD ≥2 ET Prob>0 ≥80%

cd /d "%~dp0"

echo ================================================================================
echo CONFIGURATION: KEVIN DAVEY CLASSIQUE
echo ================================================================================
echo Criteres: Ruine ≤10%% ET Return/DD ≥2.0 ET Probabilite positive ≥80%%
echo ================================================================================
echo.

python run_monte_carlo_html_generator.py --max-ruin 10 --min-return-dd 2.0 --min-prob-positive 80

echo.
pause
