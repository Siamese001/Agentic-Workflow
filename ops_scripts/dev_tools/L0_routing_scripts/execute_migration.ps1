# Archive Migration Execution Script
# Run from project root: .\scripts\execute_migration.ps1

$ErrorActionPreference = "Stop"

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Archive Migration Execution Script" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

# Create migration branch
Write-Host "`n[1/8] Creating migration branch..." -ForegroundColor Yellow
git checkout -b refactor/migrate-runtime-schemas-shared-2026 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Branch may already exist, continuing..." -ForegroundColor Gray
}

# Create target directories
Write-Host "`n[2/8] Creating target directories..." -ForegroundColor Yellow
$dirs = @(
    "agentic_core/runtime/shared_runtime",
    "agentic_core/L3_orchestration/interfaces",
    "agentic_core/prompt_governance",
    "agentic_core/schemas/models/archive_models",
    "agentic_core/schemas/models/interfaces",
    "agentic_core/schemas/models/data_assets",
    "agentic_core/L5_safety/guardrails",
    "agentic_core/L2_execution/mcp",
    "agentic_core/config"
)

foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  Created: $dir" -ForegroundColor Green
    }
}

# Phase 1: Priority Migrations
Write-Host "`n[3/8] Migrating priority files..." -ForegroundColor Yellow

$migrations = @{
    # Runtime shared
    "archives/runtime/core/reflection_engine.py" = "agentic_core/runtime/shared_runtime/reflection_engine.py"
    "archives/runtime/core/quality/signal_enhancer.py" = "agentic_core/runtime/shared_runtime/signal_enhancer.py"

    # Orchestration
    "archives/runtime/core/dynamic_dag_manager.py" = "agentic_core/L3_orchestration/dynamic_dag_manager.py"
    "archives/schemas/core_interfaces/orchestrator.py" = "agentic_core/L3_orchestration/interfaces/orchestrator.py"

    # Prompt governance
    "archives/runtime/core/prompt_assembler.py" = "agentic_core/prompt_governance/prompt_assembler.py"

    # Schema models
    "archives/runtime/core/cognitive_contracts.py" = "agentic_core/schemas/models/cognitive_contracts.py"
    "archives/runtime/core/shared_models.py" = "agentic_core/schemas/models/runtime_models.py"

    # Safety
    "archives/runtime/core/security/input_validator.py" = "agentic_core/L5_safety/guardrails/input_validator.py"
    "archives/runtime/core/security/secure_config.py" = "agentic_core/L5_safety/guardrails/secure_config.py"
    "archives/runtime/core/security/secure_error.py" = "agentic_core/L5_safety/guardrails/secure_error.py"
    "archives/runtime/core/security/secure_checkpoint.py" = "agentic_core/L5_safety/guardrails/secure_checkpoint.py"
    "archives/runtime/core/security/secure_logger.py" = "agentic_core/L5_safety/guardrails/secure_logger.py"

    # MCP
    "archives/shared/mcp/client.py" = "agentic_core/L2_execution/mcp/archive_client.py"
    "archives/shared/mcp/factory.py" = "agentic_core/L2_execution/mcp/archive_factory.py"
    "archives/shared/mcp/exceptions.py" = "agentic_core/L2_execution/mcp/archive_exceptions.py"
    "archives/shared/mcp/providers.py" = "agentic_core/L2_execution/mcp/archive_providers.py"
    "archives/runtime/shared/mcp_tools.py" = "agentic_core/L2_execution/mcp/mcp_tools.py"

    # Config
    "archives/shared/configuration/config.py" = "agentic_core/config/archive_config.py"
    "archives/shared/configuration/reasoning_config.py" = "agentic_core/config/reasoning_config.py"
}

$migrated = 0
foreach ($src in $migrations.Keys) {
    $dst = $migrations[$src]
    if (Test-Path $src) {
        git mv $src $dst 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  Migrated: $($src.Split('/')[-1])" -ForegroundColor Green
            $migrated++
        } else {
            # Try copy if git mv fails
            Copy-Item $src $dst -Force
            Write-Host "  Copied: $($src.Split('/')[-1])" -ForegroundColor Yellow
            $migrated++
        }
    } else {
        Write-Host "  Skipped (not found): $src" -ForegroundColor Gray
    }
}
Write-Host "  Total migrated: $migrated files" -ForegroundColor Cyan

# Phase 2: Schema migrations
Write-Host "`n[4/8] Migrating schema files..." -ForegroundColor Yellow

$schemaFiles = @(
    "archives/schemas/core_models/budget_profile.py",
    "archives/schemas/core_models/context_profile.py",
    "archives/schemas/core_models/llm_profile.py",
    "archives/schemas/core_models/safety_profile.py",
    "archives/schemas/core_models/l4_types.py",
    "archives/schemas/core_models/simulation_models.py",
    "archives/schemas/core_models/meta_metacognition_models.py",
    "archives/schemas/core_models/golden_state_models.py"
)

foreach ($file in $schemaFiles) {
    if (Test-Path $file) {
        $dest = "agentic_core/schemas/models/archive_models/" + (Split-Path $file -Leaf)
        Copy-Item $file $dest -Force
        Write-Host "  Migrated: $(Split-Path $file -Leaf)" -ForegroundColor Green
    }
}

# Phase 3: Interface migrations
Write-Host "`n[5/8] Migrating interface files..." -ForegroundColor Yellow

$interfaceFiles = @(
    "archives/schemas/core_interfaces/action_plane.py",
    "archives/schemas/core_interfaces/cognitive_plane.py"
)

foreach ($file in $interfaceFiles) {
    if (Test-Path $file) {
        $dest = "agentic_core/schemas/models/interfaces/" + (Split-Path $file -Leaf)
        Copy-Item $file $dest -Force
        Write-Host "  Migrated: $(Split-Path $file -Leaf)" -ForegroundColor Green
    }
}

# Phase 4: Data assets
Write-Host "`n[6/8] Migrating data assets..." -ForegroundColor Yellow

$jsonFiles = Get-ChildItem -Path "archives/schemas/data_assets" -Filter "*.json" -ErrorAction SilentlyContinue
foreach ($file in $jsonFiles) {
    $dest = "agentic_core/schemas/models/data_assets/" + $file.Name
    Copy-Item $file.FullName $dest -Force
    Write-Host "  Migrated: $($file.Name)" -ForegroundColor Green
}

# Phase 5: Delete obsolete files
Write-Host "`n[7/8] Marking obsolete files..." -ForegroundColor Yellow

$deleteFiles = @(
    "archives/runtime/__init__.py",
    "archives/shared/core/__init__.py",
    "archives/shared/errors/__init__.py",
    "archives/shared/internal/__init__.py",
    "archives/runtime/core/subatomic_hop.py",
    "archives/shared/caching/semantic_cache.py"
)

foreach ($file in $deleteFiles) {
    if (Test-Path $file) {
        Write-Host "  Marked for deletion: $file" -ForegroundColor Red
        # Don't actually delete - just mark
    }
}

# Phase 6: Create __init__.py files
Write-Host "`n[8/8] Creating __init__.py files..." -ForegroundColor Yellow

$initDirs = @(
    "agentic_core/schemas/models/archive_models",
    "agentic_core/schemas/models/interfaces",
    "agentic_core/schemas/models/data_assets",
    "agentic_core/L3_orchestration/interfaces"
)

foreach ($dir in $initDirs) {
    $initFile = Join-Path $dir "__init__.py"
    if (-not (Test-Path $initFile)) {
        '"""Archive migration package."""' | Out-File -FilePath $initFile -Encoding utf8
        Write-Host "  Created: $initFile" -ForegroundColor Green
    }
}

Write-Host "`n" + "=" * 60 -ForegroundColor Cyan
Write-Host "Migration Complete!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan

Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Review migrated files for import path updates"
Write-Host "2. Run: python -m pytest tests/ -v"
Write-Host "3. Run: python -m mypy agentic_core/"
Write-Host "4. Commit changes: git add -A && git commit -m 'feat: migrate archive code to agentic_core'"
