[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = (Get-Location).Path

if (-not (Test-Path -LiteralPath (Join-Path $ProjectRoot "AGENTS.md"))) {
    Write-Error "Refusing cleanup: AGENTS.md not found at project root '$ProjectRoot'."
    exit 2
}

$TransientCleanup = Join-Path $ProjectRoot "ops_scripts\maintenance\cleanup_codex_worktree.ps1"
$WorktreeCleanup = Join-Path $ProjectRoot ".codex\hooks\prune_merged_chat_worktrees.py"

if (-not (Test-Path -LiteralPath $TransientCleanup)) {
    Write-Error "Transient cleanup script not found: $TransientCleanup"
    exit 2
}
if (-not (Test-Path -LiteralPath $WorktreeCleanup)) {
    Write-Error "Worktree cleanup script not found: $WorktreeCleanup"
    exit 2
}

if ($DryRun) {
    & powershell -NoProfile -ExecutionPolicy Bypass -File $TransientCleanup -DryRun
} else {
    & powershell -NoProfile -ExecutionPolicy Bypass -File $TransientCleanup
}
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

$previousReapDetached = [Environment]::GetEnvironmentVariable("WORKTREE_REAP_DETACHED", "Process")
$previousReapPrefixes = [Environment]::GetEnvironmentVariable("WORKTREE_REAP_BRANCH_PREFIXES", "Process")
$previousPrunePrefixes = [Environment]::GetEnvironmentVariable("WORKTREE_PRUNE_BRANCH_PREFIXES", "Process")

try {
    [Environment]::SetEnvironmentVariable("WORKTREE_REAP_DETACHED", "1", "Process")
    [Environment]::SetEnvironmentVariable("WORKTREE_REAP_BRANCH_PREFIXES", "*", "Process")
    [Environment]::SetEnvironmentVariable("WORKTREE_PRUNE_BRANCH_PREFIXES", "*", "Process")

    if ($DryRun) {
        & python $WorktreeCleanup --dry-run
    } else {
        & python $WorktreeCleanup --delete-merged
    }
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
} finally {
    [Environment]::SetEnvironmentVariable("WORKTREE_REAP_DETACHED", $previousReapDetached, "Process")
    [Environment]::SetEnvironmentVariable("WORKTREE_REAP_BRANCH_PREFIXES", $previousReapPrefixes, "Process")
    [Environment]::SetEnvironmentVariable("WORKTREE_PRUNE_BRANCH_PREFIXES", $previousPrunePrefixes, "Process")
}
