#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Sets up automatic command logging to latest_mission_log.txt
.DESCRIPTION
    Adds a prompt function to your PowerShell profile that automatically
    logs all command output to latest_mission_log.txt after each command execution.
#>

$ProfileContent = @'
# Auto-logging function for Agentic-Workflow
$global:LastCommand = ""
$global:LogFile = "C:\Git\Agentic-Workflow\latest_mission_log.txt"

function prompt {
    $lastCmd = Get-History -Count 1
    if ($lastCmd -and $lastCmd.CommandLine -ne $global:LastCommand) {
        $global:LastCommand = $lastCmd.CommandLine
        
        # Build log entry
        $logEntry = @"
================================================================================
MISSION LOG - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
================================================================================
COMMAND: $($lastCmd.CommandLine)
DIRECTORY: $(Get-Location)
EXIT CODE: $LASTEXITCODE
================================================================================

"@
        
        # Overwrite log file
        try {
            Set-Content -Path $global:LogFile -Value $logEntry -Encoding UTF8 -ErrorAction SilentlyContinue
        } catch {
            # Silently fail if can't write
        }
    }
    
    # Return normal prompt
    "PS $($executionContext.SessionState.Path.CurrentLocation)$('>' * ($nestedPromptLevel + 1)) "
}

Write-Host "Auto-logging enabled -> latest_mission_log.txt" -ForegroundColor Green
'@

# Check if profile exists
if (!(Test-Path $PROFILE)) {
    New-Item -Path $PROFILE -ItemType File -Force | Out-Null
    Write-Host "Created PowerShell profile at: $PROFILE" -ForegroundColor Yellow
}

# Backup existing profile
$BackupPath = "$PROFILE.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
Copy-Item -Path $PROFILE -Destination $BackupPath -ErrorAction SilentlyContinue
Write-Host "Backed up existing profile to: $BackupPath" -ForegroundColor Cyan

# Append to profile
Add-Content -Path $PROFILE -Value "`n# === AUTO-LOGGING FOR AGENTIC-WORKFLOW ===`n$ProfileContent`n"

Write-Host "`n✓ Auto-logging setup complete!" -ForegroundColor Green
Write-Host "  Restart your terminal or run: . `$PROFILE" -ForegroundColor Yellow
Write-Host "  All commands will now log to: C:\Git\Agentic-Workflow\latest_mission_log.txt`n" -ForegroundColor Cyan
