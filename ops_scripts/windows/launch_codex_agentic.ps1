param(
    [string]$RepoRoot = 'C:\Git\Agentic-Workflow-FRESH',
    [string]$CodexShortcut,
    [string]$CodexLaunchTarget,
    [switch]$NoLaunch,
    [switch]$Json
)

$ErrorActionPreference = 'Stop'

function Get-UtcTimestamp { return [DateTime]::UtcNow.ToString('o') }

function Write-JsonAtomic {
    param([string]$Path, [hashtable]$Payload)
    New-Item -ItemType Directory -Path (Split-Path -Parent $Path) -Force | Out-Null
    $temporary = "$Path.tmp"
    $Payload | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $temporary -Encoding UTF8
    Move-Item -LiteralPath $temporary -Destination $Path -Force
}

function Find-CodexShortcut {
    $roots = @(
        (Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs'),
        (Join-Path $env:ProgramData 'Microsoft\Windows\Start Menu\Programs'),
        [Environment]::GetFolderPath('Desktop'),
        [Environment]::GetFolderPath('CommonDesktopDirectory')
    ) | Where-Object { $_ -and (Test-Path -LiteralPath $_ -PathType Container) }
    foreach ($root in $roots) {
        $match = Get-ChildItem -LiteralPath $root -Filter '*.lnk' -File -Recurse -ErrorAction SilentlyContinue |
            Where-Object { $_.BaseName -match '(?i)^codex' -and $_.BaseName -notmatch '(?i)agentic workflow' } |
            Select-Object -First 1
        if ($match) { return $match.FullName }
    }
    return $null
}

function Find-CodexPackageTarget {
    $package = Get-AppxPackage -Name 'OpenAI.Codex' -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $package) { return $null }
    try {
        $manifest = Get-AppxPackageManifest $package
        $applicationId = @($manifest.Package.Applications.Application)[0].Id
        if ($applicationId) { return "shell:AppsFolder\$($package.PackageFamilyName)!$applicationId" }
    }
    catch { return $null }
    return $null
}

$resolvedRoot = [IO.Path]::GetFullPath($RepoRoot)
$receiptPath = Join-Path $resolvedRoot 'artifacts/mcp/codex_agentic_prelaunch.json'
$receipt = [ordered]@{
    schema_version = 'codex-agentic-prelaunch/v1'
    generated_at = Get-UtcTimestamp
    repo_root = $resolvedRoot
    no_launch = [bool]$NoLaunch
    status = 'FAIL'
}

try {
    $preflightScript = Join-Path $PSScriptRoot 'codex_mcp_preflight.ps1'
    $preflightLines = & $preflightScript -RepoRoot $resolvedRoot -Sync -EnsureServices -Json
    $preflightCode = $LASTEXITCODE
    $preflightRaw = $preflightLines -join [Environment]::NewLine
    try { $receipt.preflight = $preflightRaw | ConvertFrom-Json } catch { throw "MCP preflight returned invalid JSON: $preflightRaw" }
    if ($preflightCode -ne 0 -or $receipt.preflight.status -ne 'PASS') { throw 'MCP preflight failed; Codex was not launched.' }

    if ($NoLaunch) {
        $receipt.status = 'PASS'
        $receipt.launch_classification = 'no_launch_requested'
    } else {
        $target = if ($CodexShortcut) { $CodexShortcut } elseif ($CodexLaunchTarget) { $CodexLaunchTarget } elseif ($env:CODEX_DESKTOP_LAUNCH_TARGET) { $env:CODEX_DESKTOP_LAUNCH_TARGET } else { Find-CodexShortcut }
        if (-not $target) { $target = Find-CodexPackageTarget }
        $isPackageTarget = $target -and $target.StartsWith('shell:AppsFolder\', [StringComparison]::OrdinalIgnoreCase)
        if (-not $target -or (-not $isPackageTarget -and -not (Test-Path -LiteralPath $target -PathType Leaf))) {
            throw 'MCP preflight passed, but no Codex Desktop shortcut or launch target was found. Supply -CodexShortcut or -CodexLaunchTarget.'
        }
        $receipt.codex_target = if ($isPackageTarget) { $target } else { [IO.Path]::GetFullPath($target) }
        $existing = Get-Process -Name 'Codex' -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($existing) {
            $receipt.status = 'PASS'
            $receipt.launch_classification = 'existing_instance'
            $receipt.codex_pid = $existing.Id
        } else {
            $process = if ($isPackageTarget) { Start-Process -FilePath 'explorer.exe' -ArgumentList $target -PassThru } else { Start-Process -FilePath $target -PassThru }
            $receipt.status = 'PASS'
            $receipt.launch_classification = 'launched'
            if ($process) { $receipt.codex_pid = $process.Id }
        }
    }
}
catch {
    $receipt.status = 'FAIL'
    $receipt.error = $_.Exception.Message
}

Write-JsonAtomic -Path $receiptPath -Payload $receipt
if ($Json) { $receipt | ConvertTo-Json -Depth 30 }
else {
    Write-Host "Codex Agentic prelaunch: $($receipt.status)"
    if ($receipt.error) { Write-Error $receipt.error }
}
if ($receipt.status -ne 'PASS') { exit 1 }
