# AG-RGGOV-6 Manual Quarantine Script
# Performs file moves that .codeiumignore blocks Cursor Agent from doing automatically
#
# Run: powershell -ExecutionPolicy Bypass -File tools/quarantine/AG_RGGOV_6_manual_quarantine.ps1

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

Write-Host "=== AG-RGGOV-6 Runtime Authority Quarantine ===" -ForegroundColor Cyan
Write-Host "Repo: $repoRoot" -ForegroundColor Gray
Write-Host ""

# Ensure archive directories exist
$archiveDirs = @(
    "$repoRoot\archives\apps_rg\orchestration_config_20260509",
    "$repoRoot\archives\apps_rg\runtime_traces_20260509"
)

foreach ($dir in $archiveDirs) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "[CREATE] $dir" -ForegroundColor Green
    } else {
        Write-Host "[EXISTS] $dir" -ForegroundColor Gray
    }
}

Write-Host ""

# Define quarantine operations
$moves = @(
    @{
        Source = "$repoRoot\apps_rg\config\agent_spec_config.py"
        Target = "$repoRoot\archives\apps_rg\orchestration_config_20260509\agent_spec_config.py"
        Reason = "172+ OTEL emissions, OrchestrationTopology, AgentSpec, runtime configs"
    },
    @{
        Source = "$repoRoot\apps_rg\utils\sovereign_config_loader_util.py"
        Target = "$repoRoot\archives\apps_rg\runtime_traces_20260509\sovereign_config_loader_util.py"
        Reason = "100+ OTEL emissions, imports AgentSpec/OrchestrationTopology"
    },
    @{
        Source = "$repoRoot\apps_rg\engines\_lifecycle_emits.py"
        Target = "$repoRoot\archives\apps_rg\runtime_traces_20260509\_lifecycle_emits.py"
        Reason = "Centralized emit boilerplate - 75 emissions per engine"
    }
)

# Execute moves
foreach ($move in $moves) {
    if (Test-Path $move.Source) {
        Write-Host "[QUARANTINE] $($move.Source)" -ForegroundColor Yellow
        Write-Host "  → $($move.Target)" -ForegroundColor Gray
        Write-Host "  Reason: $($move.Reason)" -ForegroundColor DarkGray
        
        # Create target directory if needed
        $targetDir = Split-Path -Parent $move.Target
        if (!(Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }
        
        # Move with overwrite protection
        if (Test-Path $move.Target) {
            Write-Host "  [WARN] Target exists - skipping (already quarantined?)" -ForegroundColor Magenta
        } else {
            Move-Item -Path $move.Source -Destination $move.Target -Force
            Write-Host "  [DONE] File quarantined" -ForegroundColor Green
        }
    } else {
        Write-Host "[SKIP] $($move.Source) - not found (already moved?)" -ForegroundColor Gray
    }
    Write-Host ""
}

# Create quarantine receipt in archives/
$receiptPath = "$repoRoot\archives\apps_rg\QUARANTINE_RECEIPT_AG_RGGOV_6.md"
$receiptContent = @"
# AG-RGGOV-6 Quarantine Receipt

**Date:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Decision:** profiles_only (Author-Gate approved)
**Plan:** apps-rg-declarative-ingress-only-spinal-governance-c8b3e1

## Files Quarantined

| File | Destination | Contamination |
|------|-------------|---------------|
| agent_spec_config.py | orchestration_config_20260509/ | 172+ OTEL emissions, OrchestrationTopology, AgentSpec, GateConfig |
| sovereign_config_loader_util.py | runtime_traces_20260509/ | 100+ OTEL emissions, imports from agent_spec_config.py |
| _lifecycle_emits.py | runtime_traces_20260509/ | Centralized emit boilerplate (75 emissions per engine) |

## Declarative Profiles Created (apps_rg/profiles/)

- rg_evidence_profile.yaml — Extraction rules, validation scope, quality thresholds
- rg_prompt_profile.yaml — Style constraints, content constraints
- rg_style_profile.yaml — Voice/tone, power verbs, passive phrase avoidance
- rg_output_schema.json — Bullets per section, word limits, required sections
- rg_capability_profile.yaml — Supported formats, optimization targets
- rg_planning_profile.yaml — Max sections, output structure

## Pending Author-Gate Decisions

- AG-RGGOV-6a: Duplicate threshold behavioral semantics
- AG-RGGOV-6b: Quality score threshold semantics
- AG-RGGOV-6c: Scoring weights runtime binding
- AG-RGGOV-6d: Power verbs enforcement level

## Next Steps

1. Update imports in apps_rg/__main__.py if referencing quarantined modules
2. Resolve AG-RGGOV-6a through AG-RGGOV-6d before finalizing profile schemas
3. Verify no runtime regressions from declarative profile migration

---
Quarantine performed by: AG_RGGOV_6_manual_quarantine.ps1
Metadata: .windsurf/state/AG_RGGOV_6_QUARANTINE_METADATA.json
"@

$receiptContent | Out-File -FilePath $receiptPath -Encoding utf8
Write-Host "[RECEIPT] $receiptPath" -ForegroundColor Cyan

Write-Host ""
Write-Host "=== Quarantine Complete ===" -ForegroundColor Cyan
Write-Host "Review the receipt and update any imports before committing." -ForegroundColor Yellow
