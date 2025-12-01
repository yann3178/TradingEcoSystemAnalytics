@echo off
REM Configuration Agressive
REM Ruine ≤20% ET Return/DD ≥1.5 ET Prob>0 ≥70%

cd /d "%~dp0"

echo ================================================================================
echo CONFIGURATION: AGRESSIVE
echo ================================================================================
echo Criteres: Ruine ≤20%% ET Return/DD ≥1.5 ET Probabilite positive ≥70%%
echo Recommande pour: Maximiser le nombre de strategies, accepter plus de risque
echo ================================================================================
echo.

python run_monte_carlo_html_generator.py --max-ruin 20 --min-return-dd 1.5 --min-prob-positive 70

echo.
pause
