# Script PowerShell pour appliquer le patch AI Analysis
# Version: 2.2.0
# Date: 2025-11-28

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host "PATCH PIPELINE: Ajout AI Analysis V2.2.0" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host ""

# Vérifier qu'on est dans le bon répertoire
if (-not (Test-Path "run_pipeline.py")) {
    Write-Host "❌ Erreur: run_pipeline.py introuvable" -ForegroundColor Red
    Write-Host "   Exécutez ce script depuis C:\TradeData\V2" -ForegroundColor Red
    exit 1
}

# Exécuter le patch Python
Write-Host "🚀 Exécution du patch..." -ForegroundColor Green
Write-Host ""

python patch_pipeline_add_ai.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ PATCH TERMINÉ!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Tests recommandés:" -ForegroundColor Yellow
    Write-Host "  python run_pipeline.py --dry-run" -ForegroundColor Cyan
    Write-Host "  python run_pipeline.py --run-ai-analysis --dry-run" -ForegroundColor Cyan
    Write-Host "  python run_pipeline.py --step ai-analysis --ai-max 5 --dry-run" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "❌ Erreur lors du patch" -ForegroundColor Red
    exit 1
}
