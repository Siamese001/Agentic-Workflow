# refresh-windsurf-docs.ps1
# Idempotent script to download Windsurf documentation into docs/cursor/.
# Run from the repo root: .\.cursor\scripts\_legacy_windsurf\refresh-windsurf-docs.ps1

$ErrorActionPreference = "Stop"

$outDir = Join-Path $PSScriptRoot "..\.." "docs\windsurf"
$outDir = [System.IO.Path]::GetFullPath($outDir)

# 1. Create output directory if missing
if (-not (Test-Path $outDir)) {
    New-Item -ItemType Directory -Path $outDir | Out-Null
    Write-Host "Created directory: $outDir"
}

# Map of filename -> URL
$downloads = [ordered]@{
    "llms-full.txt"                   = "https://docs.windsurf.com/llms-full.txt"
    "context-awareness-overview.md"   = "https://docs.windsurf.com/context-awareness/overview"
    "advanced-configuration.md"       = "https://docs.windsurf.com/windsurf/advanced"
    "memories-rules.md"               = "https://docs.windsurf.com/windsurf/cascade/memories"
    "agents-md.md"                    = "https://docs.windsurf.com/windsurf/cascade/agents-md"
    "skills.md"                       = "https://docs.windsurf.com/windsurf/cascade/skills"
    "workflows.md"                    = "https://docs.windsurf.com/windsurf/cascade/workflows"
    "hooks.md"                        = "https://docs.windsurf.com/windsurf/cascade/hooks"
    "mcp.md"                          = "https://docs.windsurf.com/windsurf/cascade/mcp"
    "web-search.md"                   = "https://docs.windsurf.com/windsurf/cascade/web-search"
    "prompt-engineering.md"           = "https://docs.windsurf.com/best-practices/prompt-engineering"
    "changelog.md"                    = "https://windsurf.com/changelog"
}

# 2-3. Download each file
foreach ($entry in $downloads.GetEnumerator()) {
    $dest = Join-Path $outDir $entry.Key
    Write-Host "Fetching $($entry.Key) from $($entry.Value) ..."
    try {
        Invoke-WebRequest -Uri $entry.Value -OutFile $dest -UseBasicParsing
        Write-Host "  -> saved to $dest"
    } catch {
        Write-Error "Failed to download $($entry.Key) from $($entry.Value): $_"
        exit 1
    }
}

# 4. Write fetch timestamp
$timestampFile = Join-Path $outDir "FETCHED_AT.txt"
$timestamp = (Get-Date -Format "yyyy-MM-dd HH:mm:ss") + " +0000"
Set-Content -Path $timestampFile -Value $timestamp -Encoding UTF8
Write-Host "Timestamp written to ${timestampFile}: $timestamp"

Write-Host "`nDone. All Windsurf docs refreshed in: $outDir"
