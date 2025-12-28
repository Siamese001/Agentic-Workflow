#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Removes auto-logging from PowerShell profile
.DESCRIPTION
    Removes the AUTO-LOGGING FOR AGENTIC-WORKFLOW section from your PowerShell profile
#>

Write-Host "Removing auto-logging from PowerShell profile..." -ForegroundColor Yellow

if (!(Test-Path $PROFILE)) {
    Write-Host "No PowerShell profile found. Nothing to remove." -ForegroundColor Green
    exit 0
}

# Read profile content
$content = Get-Content $PROFILE -Raw

# Check if auto-logging exists
if ($content -notmatch "AUTO-LOGGING FOR AGENTIC-WORKFLOW") {
    Write-Host "Auto-logging not found in profile. Nothing to remove." -ForegroundColor Green
    exit 0
}

# Backup existing profile
$BackupPath = "$PROFILE.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
Copy-Item -Path $PROFILE -Destination $BackupPath
Write-Host "Backed up profile to: $BackupPath" -ForegroundColor Cyan

# Remove the auto-logging section
$pattern = '(?s)\n# === AUTO-LOGGING FOR AGENTIC-WORKFLOW ===.*?(?=\n#|$)'
$newContent = $content -replace $pattern, ''

# Also remove any standalone auto-logging blocks
$newContent = $newContent -replace '(?s)# Auto-logging function for Agentic-Workflow.*?Write-Host "Auto-logging enabled.*?\n', ''

# Write cleaned content
Set-Content -Path $PROFILE -Value $newContent.TrimEnd()

Write-Host "`n✓ Auto-logging removed from PowerShell profile!" -ForegroundColor Green
Write-Host "  Restart your terminal or run: . `$PROFILE" -ForegroundColor Yellow
Write-Host "  Mission logs will no longer be created automatically.`n" -ForegroundColor Cyan
