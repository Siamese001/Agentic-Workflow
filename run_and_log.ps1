#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Executes a command and logs output to latest_mission_log.txt
.DESCRIPTION
    Wrapper script that runs any command and automatically appends
    the full terminal output to latest_mission_log.txt in the root directory.
    Overwrites the file each run for fresh data.
.PARAMETER Command
    The command to execute
.EXAMPLE
    .\run_and_log.ps1 "python canon_validator_agentic_v2.py"
#>

param(
    [Parameter(Mandatory=$true, Position=0, ValueFromRemainingArguments=$true)]
    [string[]]$Command
)

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$LogFile = Join-Path $RootDir "latest_mission_log.txt"
$CommandString = $Command -join ' '

# Header with timestamp
$Header = @"
================================================================================
MISSION LOG - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
================================================================================
COMMAND: $CommandString
DIRECTORY: $(Get-Location)
================================================================================

"@

# Execute command and capture all output
try {
    $Output = & cmd /c $CommandString 2>&1 | Out-String
    $ExitCode = $LASTEXITCODE
    
    # Build log content
    $LogContent = $Header + $Output + "`n`n"
    $LogContent += "================================================================================`n"
    $LogContent += "EXIT CODE: $ExitCode`n"
    $LogContent += "================================================================================`n"
    
    # Overwrite log file
    Set-Content -Path $LogFile -Value $LogContent -Encoding UTF8
    
    # Display output to console
    Write-Host $Output
    
    # Exit with same code as command
    exit $ExitCode
    
} catch {
    $ErrorContent = $Header + "ERROR: $_`n"
    Set-Content -Path $LogFile -Value $ErrorContent -Encoding UTF8
    Write-Error $_
    exit 1
}
