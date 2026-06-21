<#
.SYNOPSIS
Repairs local Codex MCP startup config for Agentic-Workflow.

.DESCRIPTION
This script patches the project-local .codex/config.toml and the user-level
%USERPROFILE%\.codex\config.toml so GitKraken and memory MCP failures do not
brick Codex session startup.

It does not commit machine-specific config. It writes local runtime config only.

.EXAMPLE
powershell -ExecutionPolicy Bypass -File .\scripts\codex\repair_codex_mcp_handshake.ps1 -RepoRoot C:\Git\agentic-workflow-fresh
#>

[CmdletBinding()]
param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,
    [string]$RedisUrl = "redis://localhost:6379/0",
    [switch]$SkipUserConfig
)

$ErrorActionPreference = "Stop"

function ConvertTo-TomlPath {
    param([Parameter(Mandatory = $true)][string]$Path)
    return ($Path -replace "\\", "/")
}

function Backup-FileIfExists {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (Test-Path $Path) {
        $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
        Copy-Item -Path $Path -Destination "$Path.bak_$stamp" -Force
    }
}

if (-not (Test-Path $RepoRoot)) {
    throw "Repo path not found: $RepoRoot"
}

$RepoRoot = (Resolve-Path $RepoRoot).Path
Set-Location $RepoRoot

$memoryServer = Join-Path $RepoRoot "tools\memory\adg_memory_server.py"
if (-not (Test-Path $memoryServer)) {
    throw "Memory MCP entrypoint not found: $memoryServer"
}

$gkCommand = Get-Command gk -ErrorAction SilentlyContinue
if (-not $gkCommand) {
    throw "GitKraken CLI 'gk' not found on PATH. Install/auth GitKraken CLI, then run: gk auth login"
}
$GitKrakenPath = $gkCommand.Source

$venvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    $PythonPath = $venvPython
} else {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCommand) {
        throw "Python not found. Create repo .venv or install Python before running this repair."
    }
    $PythonPath = $pythonCommand.Source
}

$RepoToml = ConvertTo-TomlPath $RepoRoot
$GitKrakenToml = ConvertTo-TomlPath $GitKrakenPath
$PythonToml = ConvertTo-TomlPath $PythonPath

# Current process env for this shell.
$env:AGENTIC_REPO_ROOT = $RepoRoot
$env:GITKRAKEN_GK_PATH = $GitKrakenPath
$env:ADG_REDIS_URL = $RedisUrl
$env:PYTHONPATH = $RepoRoot

# Persist required env vars for future Codex launches.
[Environment]::SetEnvironmentVariable("AGENTIC_REPO_ROOT", $RepoRoot, "User")
[Environment]::SetEnvironmentVariable("GITKRAKEN_GK_PATH", $GitKrakenPath, "User")
[Environment]::SetEnvironmentVariable("ADG_REDIS_URL", $RedisUrl, "User")

New-Item -ItemType Directory -Force (Join-Path $RepoRoot "artifacts\memory") | Out-Null
New-Item -ItemType Directory -Force (Join-Path $RepoRoot ".codex") | Out-Null

$ProjectConfig = Join-Path $RepoRoot ".codex\config.toml"
Backup-FileIfExists $ProjectConfig

$ProjectToml = @"
# Project-local Codex MCP overrides for this checkout.
# GitKraken and memory are optional so one bad handshake cannot brick Codex startup.

[mcp_servers.GitKraken]
command = "$GitKrakenToml"
args = ["mcp"]
cwd = "$RepoToml"
required = false
startup_timeout_sec = 30

[mcp_servers.memory]
command = "$PythonToml"
args = ["-u", "$RepoToml/tools/memory/adg_memory_server.py"]
cwd = "$RepoToml"
required = false
startup_timeout_sec = 30

[mcp_servers.memory.env]
ADG_REDIS_URL = "$RedisUrl"
MEMORY_DB = "$RepoToml/artifacts/memory/knowledge_graph.sqlite"
PYTHONPATH = "$RepoToml"
PYTHONUNBUFFERED = "1"
"@

Set-Content -Path $ProjectConfig -Value $ProjectToml -Encoding UTF8

if (-not $SkipUserConfig) {
    $UserCodexDir = Join-Path $env:USERPROFILE ".codex"
    $UserConfig = Join-Path $UserCodexDir "config.toml"
    New-Item -ItemType Directory -Force $UserCodexDir | Out-Null
    Backup-FileIfExists $UserConfig

    if (Test-Path $UserConfig) {
        $Existing = Get-Content -Path $UserConfig -Raw
    } else {
        $Existing = ""
    }

    # Remove stale GitKraken/gitkraken/memory MCP tables and their nested tables
    # so duplicate TOML tables cannot poison Codex startup.
    $Pattern = '(?ms)^\[mcp_servers\.(?:GitKraken|gitkraken|memory)(?:\.[^\]]+)?\]\r?\n.*?(?=^\[|\z)'
    $Existing = [regex]::Replace($Existing, $Pattern, '')

    $Patch = @"

[mcp_servers.GitKraken]
command = "$GitKrakenToml"
args = ["mcp"]
cwd = "$RepoToml"
required = false
startup_timeout_sec = 30

[mcp_servers.memory]
command = "$PythonToml"
args = ["-u", "$RepoToml/tools/memory/adg_memory_server.py"]
cwd = "$RepoToml"
required = false
startup_timeout_sec = 30

[mcp_servers.memory.env]
ADG_REDIS_URL = "$RedisUrl"
MEMORY_DB = "$RepoToml/artifacts/memory/knowledge_graph.sqlite"
PYTHONPATH = "$RepoToml"
PYTHONUNBUFFERED = "1"
"@

    $NewUserConfig = ($Existing.TrimEnd() + "`r`n" + $Patch.TrimStart())
    Set-Content -Path $UserConfig -Value $NewUserConfig -Encoding UTF8
}

try {
    & $GitKrakenPath --version | Out-Host
} catch {
    Write-Warning "gk --version failed. If Codex still reports GitKraken startup failure, run: gk auth login"
}

& $PythonPath -c "import pathlib, sys; print('python ok', sys.executable); print('repo exists', pathlib.Path(r'$RepoRoot').exists())"

Write-Host ""
Write-Host "Patched project config: $ProjectConfig"
if (-not $SkipUserConfig) {
    Write-Host "Patched user Codex config: $UserConfig"
}
Write-Host ""
Write-Host "Next: fully quit/restart Codex. Do not only open a new chat inside the same broken session."
