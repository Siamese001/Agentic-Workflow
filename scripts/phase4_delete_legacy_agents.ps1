# Phase 4 Hard Migration - Legacy Agent Deletion Script
# Generated: 2026-01-27
# 
# This script deletes legacy agents that have been fully superseded by Unified agents.
# Run with -WhatIf to preview changes without deleting.

param(
    [switch]$WhatIf,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Phase 4 Hard Migration - Legacy Agent Cleanup" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Group A: Redundant Base/Transitional Files (SAFE TO DELETE)
$groupA = @(
    "agentic_core\L5_safety\unified\CodeDetectorAgent.py",
    "agentic_core\L5_safety\unified\CodeEnforcerAgent.py",
    "agentic_core\L5_safety\unified\ResourceManagerAgent.py",
    "agentic_core\L5_safety\unified\SafetyDetectorAgent.py",
    "agentic_core\L5_safety\unified\SecurityManagerAgent.py",
    "agentic_core\L5_safety\unified\StructuralValidatorAgent.py",
    "agentic_core\L5_safety\unified\StructureEnforcerAgent.py",
    "agentic_core\L5_safety\unified\StructureHealerAgent.py"
)

# Group B: Additional safe deletions (no active imports found)
$groupB = @(
    "agentic_core\L5_safety\guardrails\HallucinationHunterAgent.py",
    "agentic_core\L5_safety\red_teaming\PromptInjectionAgent.py"
)

$repoRoot = Split-Path -Parent $PSScriptRoot
$deletedCount = 0
$skippedCount = 0
$errorCount = 0

Write-Host "Repository Root: $repoRoot" -ForegroundColor Gray
Write-Host ""

# Process Group A
Write-Host "GROUP A: Redundant Base/Transitional Files" -ForegroundColor Yellow
Write-Host "-------------------------------------------" -ForegroundColor Yellow

foreach ($file in $groupA) {
    $fullPath = Join-Path $repoRoot $file
    
    if (Test-Path $fullPath) {
        if ($WhatIf) {
            Write-Host "  [WOULD DELETE] $file" -ForegroundColor DarkYellow
        } else {
            try {
                Remove-Item $fullPath -Force:$Force
                Write-Host "  [DELETED] $file" -ForegroundColor Green
                $deletedCount++
            } catch {
                Write-Host "  [ERROR] $file - $_" -ForegroundColor Red
                $errorCount++
            }
        }
    } else {
        Write-Host "  [SKIPPED] $file (not found)" -ForegroundColor DarkGray
        $skippedCount++
    }
}

Write-Host ""

# Process Group B
Write-Host "GROUP B: Additional Safe Deletions (No Active Imports)" -ForegroundColor Yellow
Write-Host "-------------------------------------------------------" -ForegroundColor Yellow

foreach ($file in $groupB) {
    $fullPath = Join-Path $repoRoot $file
    
    if (Test-Path $fullPath) {
        if ($WhatIf) {
            Write-Host "  [WOULD DELETE] $file" -ForegroundColor DarkYellow
        } else {
            try {
                Remove-Item $fullPath -Force:$Force
                Write-Host "  [DELETED] $file" -ForegroundColor Green
                $deletedCount++
            } catch {
                Write-Host "  [ERROR] $file - $_" -ForegroundColor Red
                $errorCount++
            }
        }
    } else {
        Write-Host "  [SKIPPED] $file (not found)" -ForegroundColor DarkGray
        $skippedCount++
    }
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

if ($WhatIf) {
    Write-Host "  Mode: DRY RUN (no files deleted)" -ForegroundColor Yellow
    Write-Host "  Files that would be deleted: $($groupA.Count + $groupB.Count - $skippedCount)" -ForegroundColor Yellow
} else {
    Write-Host "  Deleted: $deletedCount" -ForegroundColor Green
}

Write-Host "  Skipped: $skippedCount" -ForegroundColor Gray
Write-Host "  Errors: $errorCount" -ForegroundColor $(if ($errorCount -gt 0) { "Red" } else { "Gray" })
Write-Host ""

if ($WhatIf) {
    Write-Host "Run without -WhatIf to execute deletions." -ForegroundColor Cyan
}
