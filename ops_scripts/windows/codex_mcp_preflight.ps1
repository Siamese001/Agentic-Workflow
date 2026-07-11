param(
    [string]$RepoRoot = "C:\Git\Agentic-Workflow-FRESH",
    [string]$UserConfig = "$env:USERPROFILE\.codex\config.toml",
    [switch]$Sync,
    [switch]$EnsureServices,
    [switch]$Json,
    [ValidateRange(5, 600)]
    [int]$DependencyWaitSeconds = 120,
    [ValidateRange(5, 600)]
    [int]$ServiceStartupTimeoutSeconds = 120
)

$ErrorActionPreference = "Stop"
$script:DefinitionPath = Join-Path $PSScriptRoot 'codex_mcp_http_services.psd1'

function Get-UtcTimestamp { return [DateTime]::UtcNow.ToString('o') }

function Invoke-PythonStep {
    param([string]$Label, [string[]]$Arguments)
    $stderrPath = Join-Path ([IO.Path]::GetTempPath()) "codex-mcp-preflight-$PID-$Label.stderr"
    try {
        $lines = & $python @Arguments 2>$stderrPath
        $code = $LASTEXITCODE
        $stdout = $lines -join [Environment]::NewLine
        $stderrContent = if (Test-Path -LiteralPath $stderrPath) { Get-Content -LiteralPath $stderrPath -Raw } else { $null }
        $stderr = if ($null -eq $stderrContent) { '' } else { ([string]$stderrContent).Trim() }
        return [ordered]@{ label = $Label; status = if ($code -eq 0) { 'PASS' } else { 'FAIL' }; exit_code = $code; stdout = ([string]$stdout).Trim(); stderr = $stderr }
    }
    finally {
        Remove-Item -LiteralPath $stderrPath -Force -ErrorAction SilentlyContinue
    }
}

function Test-CodexRouteBlock {
    param([string]$ConfigPath, [hashtable]$Service)
    if (-not (Test-Path -LiteralPath $ConfigPath -PathType Leaf)) {
        return [ordered]@{ path = $ConfigPath; valid = $false; reason = 'missing_config' }
    }
    $content = Get-Content -LiteralPath $ConfigPath -Raw
    $server = [regex]::Escape($Service.ServerId)
    $match = [regex]::Match($content, "(?ms)^\[mcp_servers\.$server\]\s*`r?`n(.*?)(?=^\[|\z)")
    if (-not $match.Success) { return [ordered]@{ path = $ConfigPath; valid = $false; reason = 'missing_server_block' } }
    $block = $match.Groups[1].Value
    $urlMatch = $block -match ('(?m)^url\s*=\s*"' + [regex]::Escape($Service.Url) + '"\s*$')
    $requiredMatch = $block -match '(?m)^required\s*=\s*true\s*$'
    $commandAbsent = $block -notmatch '(?m)^command\s*='
    return [ordered]@{
        path = $ConfigPath
        valid = [bool]($urlMatch -and $requiredMatch -and $commandAbsent)
        url_match = [bool]$urlMatch
        required = [bool]$requiredMatch
        primary_stdio_absent = [bool]$commandAbsent
    }
}

function Test-RootMcpRoute {
    param($RootConfig, [hashtable]$Service)
    $entry = $RootConfig.mcpServers.($Service.ServerId)
    return [ordered]@{
        server_id = $Service.ServerId
        valid = [bool]($entry -and $entry.url -eq $Service.Url -and -not $entry.command)
        url = if ($entry) { $entry.url } else { $null }
        primary_stdio_absent = [bool]($entry -and -not $entry.command)
    }
}

function Get-LogTails {
    param([hashtable]$Service, [string]$Root)
    $tails = [ordered]@{}
    foreach ($key in @('StdoutLogPath', 'StderrLogPath')) {
        $path = Join-Path $Root $Service[$key]
        $tails[$key] = if (Test-Path -LiteralPath $path -PathType Leaf) { (Get-Content -LiteralPath $path -Tail 20) -join [Environment]::NewLine } else { '' }
    }
    return $tails
}

$resolvedRoot = [IO.Path]::GetFullPath($RepoRoot)
$pythonCommand = Get-Command python.exe -ErrorAction SilentlyContinue
if (-not $pythonCommand) { $pythonCommand = Get-Command python -ErrorAction Stop }
$python = $pythonCommand.Source
$definition = Import-PowerShellDataFile -LiteralPath $script:DefinitionPath
$services = @($definition.Services.Values | Sort-Object { $_.Port })
$report = [ordered]@{
    schema_version = 'codex-mcp-preflight/v2'
    generated_at = Get-UtcTimestamp
    repo_root = $resolvedRoot
    status = 'PASS'
    steps = @()
    route_invariants = @()
    service_lifecycle = $null
    probes = @()
    diagnostics = [ordered]@{}
}

Push-Location $resolvedRoot
try {
    $step = Invoke-PythonStep -Label 'repo_config_check' -Arguments @('.codex/governance/scripts/sync_mcp_config.py', '--check', '--json')
    $report.steps += $step
    if ($step.status -ne 'PASS') { throw 'repo MCP config validation failed' }

    if ($Sync -or $EnsureServices) {
        $step = Invoke-PythonStep -Label 'user_config_sync' -Arguments @('.codex/governance/scripts/sync_mcp_config.py', '--sync-user-config', '--user-config', $UserConfig, '--json')
        $report.steps += $step
        if ($step.status -ne 'PASS') { throw 'user config sync failed' }
    }

    $step = Invoke-PythonStep -Label 'user_config_check' -Arguments @('.codex/governance/scripts/sync_mcp_config.py', '--check-user-config', '--user-config', $UserConfig, '--json')
    $report.steps += $step
    if ($step.status -ne 'PASS') { throw 'user config projection drifted' }

    $rootConfig = Get-Content -LiteralPath (Join-Path $resolvedRoot '.mcp.json') -Raw | ConvertFrom-Json
    foreach ($service in $services) {
        $rootRoute = Test-RootMcpRoute -RootConfig $rootConfig -Service $service
        $repoRoute = Test-CodexRouteBlock -ConfigPath (Join-Path $resolvedRoot '.codex/config.toml') -Service $service
        $userRoute = Test-CodexRouteBlock -ConfigPath $UserConfig -Service $service
        $valid = $rootRoute.valid -and $repoRoute.valid -and $userRoute.valid
        $report.route_invariants += [ordered]@{ server_id = $service.ServerId; valid = $valid; root = $rootRoute; repo_codex = $repoRoute; user_codex = $userRoute }
        if (-not $valid) { throw "required HTTP route invariant failed: $($service.ServerId)" }
    }

    if ($EnsureServices) {
        $taskScript = Join-Path $PSScriptRoot 'codex_mcp_service_tasks.ps1'
        $taskLines = & $taskScript -RepoRoot $resolvedRoot -PythonExe $python -Install -EnsureRunning -Json `
            -DependencyWaitSeconds $DependencyWaitSeconds -StartupTimeoutSeconds $ServiceStartupTimeoutSeconds
        $taskCode = $LASTEXITCODE
        $taskRaw = $taskLines -join [Environment]::NewLine
        try { $report.service_lifecycle = $taskRaw | ConvertFrom-Json } catch { throw "service task manager returned invalid JSON: $taskRaw" }
        if ($taskCode -ne 0 -or $report.service_lifecycle.status -ne 'PASS') { throw 'managed HTTP MCP services are not healthy' }

        foreach ($service in $services) {
            $probe = Invoke-PythonStep -Label "probe_$($service.ServerId)" -Arguments @(
                'scripts/governance/probe_mcp_http_server.py', '--url', $service.Url,
                '--tool', $service.HealthTool, '--timeout', '30', '--json'
            )
            try { $payload = $probe.stdout | ConvertFrom-Json } catch { $payload = $null }
            $probeResult = [ordered]@{
                server_id = $service.ServerId
                health_tool = $service.HealthTool
                status = if ($probe.status -eq 'PASS' -and $payload -and $payload.initialize.ok -and $payload.tools_list.ok -and $payload.tool_call.ok) { 'PASS' } else { 'FAIL' }
                initialize = [bool]($payload -and $payload.initialize.ok)
                tools_list = [bool]($payload -and $payload.tools_list.ok)
                health_tool_ok = [bool]($payload -and $payload.tool_call.ok)
                payload = $payload
            }
            $report.probes += $probeResult
            if ($probeResult.status -ne 'PASS') {
                $report.diagnostics[$service.ServerId] = Get-LogTails -Service $service -Root $resolvedRoot
                throw "MCP health-tool probe failed: $($service.ServerId)"
            }
        }
    }
}
catch {
    $report.status = 'FAIL'
    $report.error = $_.Exception.Message
    $report.error_location = $_.InvocationInfo.PositionMessage
    foreach ($service in $services) {
        if (-not $report.diagnostics.Contains($service.ServerId)) {
            $report.diagnostics[$service.ServerId] = Get-LogTails -Service $service -Root $resolvedRoot
        }
    }
}
finally {
    Pop-Location
}

if ($Json) { $report | ConvertTo-Json -Depth 40 }
else {
    foreach ($step in $report.steps) {
        if ($step.stdout) { Write-Host $step.stdout }
        if ($step.stderr) { Write-Warning $step.stderr }
    }
    Write-Host "Codex MCP preflight: $($report.status)"
    if ($report.error) { Write-Error $report.error }
}
if ($report.status -ne 'PASS') { exit 1 }
