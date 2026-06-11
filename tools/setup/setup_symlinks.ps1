# setup_symlinks.ps1 — Windows contributor symlink setup for MCP config mirrors.
#
# Creates symlinks so deprecated global editor mirrors read the repo SSOT:
#   ~/.codeium/windsurf/mcp_config.json  ->  <repo>/.mcp.json
#
# Idempotent; safe to re-run. The -IncludeAgentsMd flag is retained for
# compatibility, but root AGENTS.md is already the SSOT and is not replaced.
#
# Requires: Windows Developer Mode enabled OR an elevated (Admin) shell.
# Usage:
#   pwsh -File tools/setup/setup_symlinks.ps1
#   pwsh -File tools/setup/setup_symlinks.ps1 -IncludeAgentsMd
#   pwsh -File tools/setup/setup_symlinks.ps1 -DryRun
#
[CmdletBinding()]
param(
    [switch]$IncludeAgentsMd,
    [switch]$DryRun,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

function Write-Step([string]$msg) {
    Write-Host "[setup_symlinks] $msg"
}

function Test-SymlinkCapability {
    # Fast check: try creating a temp symlink; if it throws, we need Dev Mode or Admin.
    $probeTarget = Join-Path $env:TEMP ("symlink_probe_target_" + [guid]::NewGuid().ToString("N"))
    $probeLink   = Join-Path $env:TEMP ("symlink_probe_link_"   + [guid]::NewGuid().ToString("N"))
    try {
        New-Item -ItemType File -Path $probeTarget -Force | Out-Null
        New-Item -ItemType SymbolicLink -Path $probeLink -Target $probeTarget -ErrorAction Stop | Out-Null
        Remove-Item $probeLink -Force -ErrorAction SilentlyContinue
        Remove-Item $probeTarget -Force -ErrorAction SilentlyContinue
        return $true
    } catch {
        Remove-Item $probeLink -Force -ErrorAction SilentlyContinue
        Remove-Item $probeTarget -Force -ErrorAction SilentlyContinue
        return $false
    }
}

function New-FileSymlink {
    param(
        [Parameter(Mandatory=$true)][string]$LinkPath,
        [Parameter(Mandatory=$true)][string]$TargetPath
    )
    if (-not (Test-Path $TargetPath)) {
        throw "Target does not exist: $TargetPath"
    }
    $targetReal = (Resolve-Path $TargetPath).Path

    # Ensure parent dir
    $parent = Split-Path -Parent $LinkPath
    if (-not (Test-Path $parent)) {
        if ($DryRun) {
            Write-Step "DRY-RUN: would mkdir $parent"
        } else {
            New-Item -ItemType Directory -Path $parent -Force | Out-Null
        }
    }

    if (Test-Path $LinkPath) {
        $existing = Get-Item $LinkPath -Force
        if ($existing.LinkType -eq "SymbolicLink") {
            $currentTarget = $existing.Target
            # Target can be relative or absolute; compare by realpath
            try {
                $currentReal = (Resolve-Path (Join-Path $parent $currentTarget[0]) -ErrorAction Stop).Path
            } catch {
                $currentReal = $currentTarget[0]
            }
            if ($currentReal -ieq $targetReal) {
                Write-Step "OK: $LinkPath already symlinks to $targetReal"
                return
            }
            Write-Step "Replacing stale symlink at $LinkPath (was -> $currentTarget)"
            if (-not $DryRun) { Remove-Item $LinkPath -Force }
        } else {
            # Regular file/dir exists; back it up.
            $backup = "$LinkPath.pre-symlink-backup"
            Write-Step "Backing up existing file: $LinkPath -> $backup"
            if (-not $DryRun) {
                if (Test-Path $backup) {
                    if (-not $Force) {
                        throw "Backup already exists: $backup (pass -Force to overwrite)"
                    }
                    Remove-Item $backup -Force
                }
                Move-Item $LinkPath $backup -Force
            }
        }
    }

    if ($DryRun) {
        Write-Step "DRY-RUN: would symlink $LinkPath -> $targetReal"
    } else {
        New-Item -ItemType SymbolicLink -Path $LinkPath -Target $targetReal | Out-Null
        Write-Step "Created: $LinkPath -> $targetReal"
    }
}

# --- Resolve repo root (this script lives at <repo>/tools/setup/) ---
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot  = Resolve-Path (Join-Path $scriptDir "..\..") | Select-Object -ExpandProperty Path

# --- Capability check ---
if (-not (Test-SymlinkCapability)) {
    Write-Host ""
    Write-Host "ERROR: cannot create symlinks. Enable one of:" -ForegroundColor Red
    Write-Host "  1. Windows Settings -> Privacy & security -> For developers -> Developer Mode ON" -ForegroundColor Yellow
    Write-Host "  2. Re-run this script from an elevated (Administrator) PowerShell" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Without symlinks, the post-write hook will continue to copy the file on save" -ForegroundColor Yellow
    Write-Host "and the CI gate will block PRs on drift — you just lose the zero-drift guarantee" -ForegroundColor Yellow
    Write-Host "on your local machine." -ForegroundColor Yellow
    exit 1
}

# --- Paths ---
$repoMcp     = Join-Path $repoRoot ".mcp.json"
$globalMcp   = Join-Path $env:USERPROFILE ".codeium\windsurf\mcp_config.json"

Write-Step "Repo root: $repoRoot"
Write-Step "Mode: $(if ($DryRun) { 'DRY-RUN' } else { 'APPLY' })"

# --- MCP config symlink ---
Write-Step "--- MCP config ---"
New-FileSymlink -LinkPath $globalMcp -TargetPath $repoMcp

# --- AGENTS.md symlink (opt-in) ---
if ($IncludeAgentsMd) {
    Write-Step "--- AGENTS.md ---"
    Write-Step "SKIP: root AGENTS.md is already the SSOT; no legacy symlink is created"
}

Write-Step "Done."
