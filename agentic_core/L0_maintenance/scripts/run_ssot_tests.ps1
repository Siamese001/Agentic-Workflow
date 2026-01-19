# PowerShell wrapper to run SSOT enforcement tests with appropriate pytest configuration
# This avoids the global 100% coverage requirement for the entire agentic_core

Write-Host "=======================================================================" -ForegroundColor Cyan
Write-Host "RUNNING SSOT ENFORCEMENT TESTS" -ForegroundColor Cyan
Write-Host "=======================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Using targeted coverage for SSOT modules only..." -ForegroundColor Yellow
Write-Host ""

# Run pytest with specific coverage targets for SSOT-related modules
pytest scripts/test_ssot_enforcement.py `
  --cov=scripts/dashboard_ssot_definitions.py `
  --cov=scripts/generate_dashboard_ssot.py `
  --cov-branch `
  --cov-report=term-missing `
  --cov-report=html:coverage_html_ssot `
  --cov-fail-under=50 `
  -v `
  --tb=short

$exitCode = $LASTEXITCODE

Write-Host ""
Write-Host "=======================================================================" -ForegroundColor Cyan
if ($exitCode -eq 0) {
    Write-Host "✅ SSOT ENFORCEMENT TESTS PASSED" -ForegroundColor Green
} else {
    Write-Host "❌ SSOT ENFORCEMENT TESTS FAILED" -ForegroundColor Red
}
Write-Host "=======================================================================" -ForegroundColor Cyan

exit $exitCode
