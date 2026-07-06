param(
    [string]$RepoRoot = "C:\Git\Agentic-Workflow-FRESH",
    [string]$UserConfig = "$env:USERPROFILE\.codex\config.toml",
    [switch]$Sync
)

$ErrorActionPreference = "Stop"
Push-Location $RepoRoot
try {
    python .codex\governance\scripts\sync_mcp_config.py --check
    if ($LASTEXITCODE -ne 0) { throw "repo MCP config validation failed" }

    if ($Sync) {
        python .codex\governance\scripts\sync_mcp_config.py --sync-user-config --user-config $UserConfig
        if ($LASTEXITCODE -ne 0) { throw "user config sync failed" }
    }

    python .codex\governance\scripts\sync_mcp_config.py --check-user-config --user-config $UserConfig --json
    if ($LASTEXITCODE -ne 0) { throw "user config projection drifted" }
}
finally {
    Pop-Location
}
