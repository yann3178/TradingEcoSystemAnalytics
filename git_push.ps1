# Git Push Script - Trading EcoSystem Analytics V2
# Execute in PowerShell from C:\TradeData\V2\

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "GIT PUSH - Trading EcoSystem Analytics V2" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Navigate to V2 directory
Set-Location "C:\TradeData\V2"

# Show current status
Write-Host "📊 Git Status:" -ForegroundColor Yellow
git status --short

Write-Host ""
Write-Host "📁 Files to be committed:" -ForegroundColor Yellow

# Stage all changes
git add -A

# Show what will be committed
git status --short

Write-Host ""
Write-Host "📝 Committing changes..." -ForegroundColor Green

# Commit with message
$commitMessage = @"
v2.1.0: Complete V1→V2 migration (281 strategies)

## Added
- Migration V1→V2 complete: 281 strategies migrated from mc_ai_analysis
- 281 HTML reports generated with dashboard index.html
- Script run_enrich_ai_reports.py for AI Analysis enrichment
- AI Analysis paths in config/settings.py

## Modified
- config/settings.py: Added AI_ANALYSIS_DIR, AI_HTML_REPORTS_DIR
- docs/PROJECT_STATUS.md: Updated with current state
- docs/NEXT_SESSION_PROMPT.md: Updated continuation instructions
- CHANGELOG.md: Added v2.1.0 release notes
- README.md: Updated with current statistics

## Statistics
- Strategies migrated: 281
- HTML files generated: 281
- V2 types standardized: 8
- Equity curves available: 241
"@

git commit -m $commitMessage

Write-Host ""
Write-Host "🚀 Pushing to GitHub..." -ForegroundColor Green

# Push to origin main
git push origin main

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "✅ Done! Check: https://github.com/yann3178/TradingEcoSystemAnalytics" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan
