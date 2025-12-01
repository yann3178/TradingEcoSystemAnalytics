@echo off
REM Script batch principal - Monte Carlo HTML Generator V3
REM Tous les parametres sont personnalisables

cd /d "%~dp0"

echo ================================================================================
echo GENERATEUR HTML MONTE CARLO V3 - VERSION PARAMETRABLE
echo ================================================================================
echo.

if "%1"=="" (
    REM Aucun argument: defaut simple (ruine seule)
    echo Configuration: Par defaut - Ruine ≤10%% seulement
    echo.
    python run_monte_carlo_html_generator.py
) else if "%2"=="" (
    REM Un argument: run specifique
    echo Configuration: Run %1 - Ruine ≤10%% seulement
    echo.
    python run_monte_carlo_html_generator.py --run %1
) else if "%3"=="" (
    REM Deux arguments: run + max-ruin
    echo Configuration: Run %1 - Ruine ≤%2%%
    echo.
    python run_monte_carlo_html_generator.py --run %1 --max-ruin %2
) else if "%4"=="" (
    REM Trois arguments: run + max-ruin + min-return-dd
    echo Configuration: Run %1 - Ruine ≤%2%% ET Return/DD ≥%3
    echo.
    python run_monte_carlo_html_generator.py --run %1 --max-ruin %2 --min-return-dd %3
) else (
    REM Quatre arguments: tous les criteres
    echo Configuration: Run %1 - Ruine ≤%2%% ET Return/DD ≥%3 ET Prob>0 ≥%4%%
    echo.
    python run_monte_carlo_html_generator.py --run %1 --max-ruin %2 --min-return-dd %3 --min-prob-positive %4
)

echo.
pause
