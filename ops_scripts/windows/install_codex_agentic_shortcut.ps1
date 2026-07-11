param(
    [string]$RepoRoot = 'C:\Git\Agentic-Workflow-FRESH',
    [string]$SourceShortcut,
    [string]$CodexLaunchTarget,
    [string]$DestinationDirectory = ([Environment]::GetFolderPath('Desktop')),
    [switch]$Remove,
    [switch]$SkipTaskRepair,
    [switch]$Json
)

$ErrorActionPreference = 'Stop'
$shortcutName = 'Codex — Agentic Workflow'

function Find-CodexShortcut {
    $roots = @(
        (Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs'),
        (Join-Path $env:ProgramData 'Microsoft\Windows\Start Menu\Programs'),
        [Environment]::GetFolderPath('Desktop'),
        [Environment]::GetFolderPath('CommonDesktopDirectory')
    ) | Where-Object { $_ -and (Test-Path -LiteralPath $_ -PathType Container) }
    foreach ($root in $roots) {
        $match = Get-ChildItem -LiteralPath $root -Filter '*.lnk' -File -Recurse -ErrorAction SilentlyContinue |
            Where-Object { $_.BaseName -match '(?i)^codex' -and $_.BaseName -ne $shortcutName } |
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
        if ($applicationId) {
            return [ordered]@{
                target = "shell:AppsFolder\$($package.PackageFamilyName)!$applicationId"
                install_location = $package.InstallLocation
            }
        }
    }
    catch { return $null }
    return $null
}

function Quote-ShortcutArgument {
    param([string]$Value)
    if ($Value -match '["\r\n]') { throw 'Shortcut arguments may not contain quotes or line breaks.' }
    return '"' + $Value + '"'
}

$resolvedRoot = [IO.Path]::GetFullPath($RepoRoot)
$shortcutPath = Join-Path $DestinationDirectory "$shortcutName.lnk"
$report = [ordered]@{
    schema_version = 'codex-agentic-shortcut/v1'
    repo_root = $resolvedRoot
    shortcut_path = $shortcutPath
    status = 'FAIL'
}

try {
    if ($Remove) {
        if (Test-Path -LiteralPath $shortcutPath -PathType Leaf) { Remove-Item -LiteralPath $shortcutPath -Force; $report.action = 'removed' }
        else { $report.action = 'already_absent' }
        $report.status = 'PASS'
    } else {
        if (-not $SkipTaskRepair) {
            $taskScript = Join-Path $PSScriptRoot 'codex_mcp_service_tasks.ps1'
            $taskLines = & $taskScript -RepoRoot $resolvedRoot -Install -Json
            $taskCode = $LASTEXITCODE
            $taskRaw = $taskLines -join [Environment]::NewLine
            try { $report.task_repair = $taskRaw | ConvertFrom-Json } catch { throw "Task repair returned invalid JSON: $taskRaw" }
            if ($taskCode -ne 0 -or $report.task_repair.status -ne 'PASS') { throw 'Scheduled Task install or repair failed.' }
        }

        $source = if ($SourceShortcut) { $SourceShortcut } else { Find-CodexShortcut }
        $packageTarget = if (-not $source -and -not $CodexLaunchTarget) { Find-CodexPackageTarget } else { $null }
        $target = if ($source) { $source } elseif ($CodexLaunchTarget) { $CodexLaunchTarget } elseif ($packageTarget) { $packageTarget.target } else { $null }
        $isPackageTarget = $target -and $target.StartsWith('shell:AppsFolder\', [StringComparison]::OrdinalIgnoreCase)
        if (-not $target -or (-not $isPackageTarget -and -not (Test-Path -LiteralPath $target -PathType Leaf))) {
            throw 'No official Codex shortcut or launch target was found. Supply -SourceShortcut or -CodexLaunchTarget.'
        }
        $pwsh = (Get-Command pwsh.exe -ErrorAction Stop).Source
        $wscript = Join-Path $env:SystemRoot 'System32\wscript.exe'
        $adapter = Join-Path $PSScriptRoot 'run_hidden_wait.vbs'
        if (-not (Test-Path -LiteralPath $wscript -PathType Leaf)) { throw "wscript.exe is missing: $wscript" }
        if (-not (Test-Path -LiteralPath $adapter -PathType Leaf)) { throw "No-window adapter is missing: $adapter" }
        $launcher = Join-Path $PSScriptRoot 'launch_codex_agentic.ps1'
        $arguments = @('//B', '//NoLogo', (Quote-ShortcutArgument $adapter), (Quote-ShortcutArgument $pwsh), '-NoLogo', '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass', '-File', (Quote-ShortcutArgument $launcher), '-RepoRoot', (Quote-ShortcutArgument $resolvedRoot))
        if ($source) { $arguments += @('-CodexShortcut', (Quote-ShortcutArgument ([IO.Path]::GetFullPath($source)))) }
        else { $arguments += @('-CodexLaunchTarget', (Quote-ShortcutArgument $(if ($isPackageTarget) { $target } else { [IO.Path]::GetFullPath($target) }))) }

        New-Item -ItemType Directory -Path $DestinationDirectory -Force | Out-Null
        $shell = New-Object -ComObject WScript.Shell
        $shortcut = $shell.CreateShortcut($shortcutPath)
        $shortcut.TargetPath = $wscript
        $shortcut.Arguments = $arguments -join ' '
        $shortcut.WorkingDirectory = $resolvedRoot
        $shortcut.Description = 'Launch Codex after Agentic Workflow HTTP MCP services are healthy.'
        if ($source -and [IO.Path]::GetExtension($source) -eq '.lnk') {
            $official = $shell.CreateShortcut($source)
            if ($official.IconLocation) { $shortcut.IconLocation = $official.IconLocation }
            elseif ($official.TargetPath) { $shortcut.IconLocation = $official.TargetPath }
        } elseif ($CodexLaunchTarget) {
            $shortcut.IconLocation = [IO.Path]::GetFullPath($CodexLaunchTarget)
        } elseif ($packageTarget) {
            $runningCodex = Get-Process -Name 'Codex' -ErrorAction SilentlyContinue | Where-Object { $_.Path -and $_.Path.StartsWith($packageTarget.install_location, [StringComparison]::OrdinalIgnoreCase) } | Select-Object -First 1
            if ($runningCodex) { $shortcut.IconLocation = $runningCodex.Path }
        }
        $shortcut.Save()
        $report.status = 'PASS'
        $report.action = if (Test-Path -LiteralPath $shortcutPath) { 'installed_or_repaired' } else { 'failed' }
        $report.source_target = if ($isPackageTarget) { $target } else { [IO.Path]::GetFullPath($target) }
    }
}
catch {
    $report.status = 'FAIL'
    $report.error = $_.Exception.Message
}

if ($Json) { $report | ConvertTo-Json -Depth 20 }
else {
    Write-Host "Codex Agentic shortcut: $($report.status) ($shortcutPath)"
    if ($report.error) { Write-Error $report.error }
}
if ($report.status -ne 'PASS') { exit 1 }
