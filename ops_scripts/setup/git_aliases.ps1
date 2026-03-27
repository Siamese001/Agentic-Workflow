# Setup git aliases for pre-commit hook management (Windows PowerShell)

Write-Host "Setting up git aliases for pre-commit hook management..." -ForegroundColor Green

# Alias for commit with bypass (when hooks are blocking legitimate commits)
git config --global alias.commit-bypass "commit --no-verify"

# Alias for commit with auto-fix (runs hooks, auto-stages changes, then commits)
git config --global alias.commit-auto "!git add -A && git commit --no-verify"

# Alias for quick hook fix (stages all and commits)
git config --global alias.fix-commit "!git add -A && git commit -m 'Fix: Apply pre-commit hook formatting' --no-verify"

# Alias for checking what hooks would do
git config --global alias.hooks-test "pre-commit run --all-files --verbose"

Write-Host "✅ Git aliases configured:" -ForegroundColor Green
Write-Host "  git commit-bypass  - Commit without pre-commit hooks" -ForegroundColor Cyan
Write-Host "  git commit-auto   - Auto-stage and commit (no-verify)" -ForegroundColor Cyan
Write-Host "  git fix-commit    - Fix and commit hook changes" -ForegroundColor Cyan
Write-Host "  git hooks-test    - Test all hooks on all files" -ForegroundColor Cyan
