[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = (Get-Location).Path
$script:RemovedCount = 0
$script:WouldRemoveCount = 0
$script:WarningCount = 0

if (-not (Test-Path -LiteralPath (Join-Path $ProjectRoot "AGENTS.md"))) {
    Write-Error "Refusing cleanup: AGENTS.md not found at project root '$ProjectRoot'."
    exit 2
}

function Test-InProjectRoot {
    param([Parameter(Mandatory = $true)][string]$Path)

    $fullPath = [System.IO.Path]::GetFullPath($Path)
    $rootPath = [System.IO.Path]::GetFullPath($ProjectRoot).TrimEnd([System.IO.Path]::DirectorySeparatorChar)
    return $fullPath.Equals($rootPath, [System.StringComparison]::OrdinalIgnoreCase) -or
        $fullPath.StartsWith($rootPath + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)
}

function Remove-ProjectItem {
    param([Parameter(Mandatory = $true)][string]$LiteralPath)

    if (-not (Test-Path -LiteralPath $LiteralPath)) {
        return
    }

    if (-not (Test-InProjectRoot -Path $LiteralPath)) {
        Write-Warning "Skipping cleanup target outside project root: $LiteralPath"
        return
    }

    try {
        if ($DryRun) {
            $script:WouldRemoveCount += 1
            return
        }

        if ($PSCmdlet.ShouldProcess($LiteralPath, "Remove transient Codex worktree artifact")) {
            Remove-Item -LiteralPath $LiteralPath -Recurse -Force -ErrorAction Stop
            $script:RemovedCount += 1
        }
    }
    catch {
        $script:WarningCount += 1
        Write-Warning "Could not remove '$LiteralPath': $($_.Exception.Message)"
    }
}

$directTargets = @(
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "artifacts/mcp/playwright",
    ".playwright-mcp"  # deprecated pre-2026-06 Playwright MCP output root
)

foreach ($target in $directTargets) {
    Remove-ProjectItem -LiteralPath (Join-Path $ProjectRoot $target)
}

$scanRoots = @(
    "agentic_core",
    "apps_architect",
    "apps_eval",
    "apps_exec",
    "apps_lic",
    "apps_qna",
    "apps_research",
    "apps_rg",
    "apps_shared",
    "apps_underwriting_ai",
    "config",
    "ops_scripts",
    "scripts",
    "tests",
    "tools"
)

foreach ($scanRoot in $scanRoots) {
    $rootPath = Join-Path $ProjectRoot $scanRoot
    if (-not (Test-Path -LiteralPath $rootPath)) {
        continue
    }

    Get-ChildItem -LiteralPath $rootPath -Recurse -Directory -Filter "__pycache__" -Force -ErrorAction SilentlyContinue |
        ForEach-Object { Remove-ProjectItem -LiteralPath $_.FullName }

    Get-ChildItem -Path (Join-Path $rootPath "*") -Recurse -File -Include "*.pyc", "*.pyo" -Force -ErrorAction SilentlyContinue |
        ForEach-Object { Remove-ProjectItem -LiteralPath $_.FullName }
}

if ($DryRun) {
    Write-Host "Codex cleanup dry run: would_remove=$script:WouldRemoveCount warnings=$script:WarningCount"
} else {
    Write-Host "Codex cleanup complete: removed=$script:RemovedCount warnings=$script:WarningCount"
}
