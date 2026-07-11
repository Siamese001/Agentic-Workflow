param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('adg_sqlite', 'memory')]
    [string]$ServerId,
    [Parameter(Mandatory = $true)]
    [string]$RepoRoot,
    [string]$PythonExe,
    [switch]$Json,
    [ValidateRange(0, 600)]
    [int]$DependencyWaitSeconds = 0,
    [ValidateRange(100, 10000)]
    [int]$RetryIntervalMilliseconds = 1000,
    [switch]$DependencyProbeOnly,
    [string]$DependencyHostOverride,
    [ValidateRange(0, 65535)]
    [int]$DependencyPortOverride = 0
)

$ErrorActionPreference = 'Stop'
$script:DefinitionPath = Join-Path $PSScriptRoot 'codex_mcp_http_services.psd1'

function Get-UtcTimestamp {
    return [DateTime]::UtcNow.ToString('o')
}

function Protect-LogText {
    param([AllowNull()][string]$Text)
    if ($null -eq $Text) { return $null }
    # Keep credential-bearing URLs and named secrets out of receipts and diagnostics.
    $redacted = $Text -replace '(?i)(redis|rediss|https?)://[^\s/"'']+@', '$1://[REDACTED]@'
    $redacted = $redacted -replace '(?i)(password|token|secret|api[_-]?key)\s*[=:]\s*[^\s,;]+', '$1=[REDACTED]'
    return $redacted
}

function Write-JsonAtomic {
    param([string]$Path, [hashtable]$Payload)
    $parent = Split-Path -Parent $Path
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
    $temporary = "$Path.tmp"
    $Payload | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $temporary -Encoding UTF8
    Move-Item -LiteralPath $temporary -Destination $Path -Force
}

function Resolve-RepoPath {
    param([string]$Root, [string]$RelativePath)
    return [IO.Path]::GetFullPath((Join-Path $Root $RelativePath))
}

function Resolve-PythonExecutable {
    param([string]$Requested)
    if ($Requested) {
        if ([IO.Path]::IsPathRooted($Requested)) {
            if (-not (Test-Path -LiteralPath $Requested -PathType Leaf)) {
                throw "Python executable does not exist: $Requested"
            }
            return [IO.Path]::GetFullPath($Requested)
        }
        $resolved = Get-Command $Requested -ErrorAction Stop
        return $resolved.Source
    }
    foreach ($candidate in @('python.exe', 'python')) {
        $resolved = Get-Command $candidate -ErrorAction SilentlyContinue
        if ($resolved) { return $resolved.Source }
    }
    throw 'Unable to resolve Python. Supply -PythonExe.'
}

function Test-TcpDependency {
    param([string]$HostName, [int]$Port, [int]$TimeoutMilliseconds)
    $client = [Net.Sockets.TcpClient]::new()
    try {
        $pending = $client.ConnectAsync($HostName, $Port)
        return $pending.Wait($TimeoutMilliseconds) -and $client.Connected
    }
    catch {
        return $false
    }
    finally {
        $client.Dispose()
    }
}

function Wait-ServiceDependencies {
    param([hashtable]$Service, [int]$TimeoutOverrideSeconds, [int]$PollMilliseconds)
    $receipts = @()
    foreach ($dependency in @($Service.Dependencies)) {
        if ($dependency.Kind -ne 'tcp') {
            throw "Unsupported dependency kind: $($dependency.Kind)"
        }
        $ready = $false
        $attempts = 0
        $started = [DateTime]::UtcNow
        $timeoutSeconds = if ($TimeoutOverrideSeconds -gt 0) { $TimeoutOverrideSeconds } else { [int]$dependency.TimeoutSeconds }
        $policy = [string]$dependency.FailurePolicy
        if ($timeoutSeconds -le 0) { throw "Dependency timeout must be positive: $($dependency.Name)" }
        if ($policy -notin @('block', 'continue_degraded')) { throw "Unsupported dependency failure policy: $policy" }
        while ((([DateTime]::UtcNow - $started).TotalSeconds -lt $timeoutSeconds) -and -not $ready) {
            $attempts++
            $ready = Test-TcpDependency -HostName $dependency.Host -Port $dependency.Port -TimeoutMilliseconds ([Math]::Min($PollMilliseconds, 2000))
            if (-not $ready) { Start-Sleep -Milliseconds $PollMilliseconds }
        }
        $receipts += [ordered]@{
            name = $dependency.Name
            kind = $dependency.Kind
            host = $dependency.Host
            port = $dependency.Port
            timeout_seconds = $timeoutSeconds
            failure_policy = $policy
            ready = $ready
            attempts = $attempts
            outcome = if ($ready) { 'ready' } elseif ($policy -eq 'continue_degraded') { 'continue_degraded' } else { 'blocked' }
        }
    }
    return $receipts
}

function Get-PortListener {
    param([int]$Port)
    $listener = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if (-not $listener) { return $null }
    return [ordered]@{
        address = $listener.LocalAddress
        port = $listener.LocalPort
        pid = $listener.OwningProcess
    }
}

function Quote-ProcessArgument {
    param([string]$Value)
    if ($Value -match '["\r\n]') { throw 'No-window adapter arguments may not contain quotes or line breaks.' }
    return '"' + $Value + '"'
}

$resolvedRoot = [IO.Path]::GetFullPath($RepoRoot)
if (-not (Test-Path -LiteralPath (Join-Path $resolvedRoot '.mcp.json') -PathType Leaf)) {
    throw "RepoRoot is not an Agentic-Workflow checkout: $resolvedRoot"
}
if (-not (Test-Path -LiteralPath $script:DefinitionPath -PathType Leaf)) {
    throw "Service definition is missing: $script:DefinitionPath"
}

$definition = Import-PowerShellDataFile -LiteralPath $script:DefinitionPath
$service = $definition.Services[$ServerId]
if (-not $service) { throw "Unknown managed HTTP MCP service: $ServerId" }
foreach ($dependency in @($service.Dependencies)) {
    if ($DependencyHostOverride) { $dependency.Host = $DependencyHostOverride }
    if ($DependencyPortOverride -gt 0) { $dependency.Port = $DependencyPortOverride }
}
$python = Resolve-PythonExecutable -Requested $PythonExe
$statePath = Resolve-RepoPath -Root $resolvedRoot -RelativePath $service.StatePath
$launcherStatePath = Resolve-RepoPath -Root $resolvedRoot -RelativePath $service.LauncherStatePath
$stdoutPath = Resolve-RepoPath -Root $resolvedRoot -RelativePath $service.StdoutLogPath
$stderrPath = Resolve-RepoPath -Root $resolvedRoot -RelativePath $service.StderrLogPath
$hiddenAdapter = Join-Path $PSScriptRoot 'run_hidden_wait.vbs'
$wscript = Join-Path $env:SystemRoot 'System32\wscript.exe'
if (-not (Test-Path -LiteralPath $hiddenAdapter -PathType Leaf)) { throw "No-window adapter is missing: $hiddenAdapter" }
if (-not (Test-Path -LiteralPath $wscript -PathType Leaf)) { throw "wscript.exe is missing: $wscript" }
New-Item -ItemType Directory -Path (Split-Path -Parent $stdoutPath) -Force | Out-Null

$baseReceipt = @{
    schema_version = 'codex-mcp-http-service-runner/v1'
    server_id = $service.ServerId
    task_name = $service.TaskName
    endpoint = $service.Url
    expected_transport = $service.ExpectedTransport
    repo_root = $resolvedRoot
    python_executable = $python
    runner_pid = $PID
    launched_at = Get-UtcTimestamp
}

try {
    $dependencies = Wait-ServiceDependencies -Service $service -TimeoutOverrideSeconds $DependencyWaitSeconds -PollMilliseconds $RetryIntervalMilliseconds
    $blockedDependencies = @($dependencies | Where-Object { $_.outcome -eq 'blocked' })
    $dependencyStatus = if (@($dependencies | Where-Object { $_.outcome -eq 'continue_degraded' }).Count -gt 0) { 'degraded' } else { 'ready' }
    if ($blockedDependencies.Count -gt 0) {
        $receipt = $baseReceipt.Clone()
        $receipt.status = 'blocked'
        $receipt.dependencies = $dependencies
        $receipt.dependency_status = 'blocked'
        $receipt.exit_code = 78
        $receipt.termination_classification = 'dependency_blocked'
        $receipt.terminated_at = Get-UtcTimestamp
        Write-JsonAtomic -Path $statePath -Payload $receipt
        if ($Json) { $receipt | ConvertTo-Json -Depth 20 }
        exit 78
    }
    if ($DependencyProbeOnly) {
        $receipt = $baseReceipt.Clone()
        $receipt.status = if ($dependencyStatus -eq 'degraded') { 'degraded' } else { 'ok' }
        $receipt.dependencies = $dependencies
        $receipt.dependency_status = $dependencyStatus
        $receipt.terminated_at = Get-UtcTimestamp
        if ($Json) { $receipt | ConvertTo-Json -Depth 20 }
        exit 0
    }

    $listener = Get-PortListener -Port $service.Port
    if ($listener) {
        $receipt = $baseReceipt.Clone()
        $receipt.status = 'blocked'
        $receipt.termination_classification = 'foreign_port_conflict'
        $receipt.listener = $listener
        $receipt.terminated_at = Get-UtcTimestamp
        Write-JsonAtomic -Path $statePath -Payload $receipt
        if ($Json) { $receipt | ConvertTo-Json -Depth 20 }
        exit 73
    }

    $env:AGENTIC_REPO_ROOT = $resolvedRoot
    $env:ADG_REPO_ROOT = $resolvedRoot
    if (-not $env:ADG_REDIS_URL -or $env:ADG_REDIS_URL -match '\$|YOUR_|CHANGEME|PLACEHOLDER') {
        $env:ADG_REDIS_URL = 'redis://localhost:6379/0'
    }
    $env:MEMORY_DB = Resolve-RepoPath -Root $resolvedRoot -RelativePath 'artifacts/memory/knowledge_graph.sqlite'
    $env:PYTHONUNBUFFERED = '1'
    $env:PYTHONPATH = if ($env:PYTHONPATH) { "$resolvedRoot$([IO.Path]::PathSeparator)$env:PYTHONPATH" } else { $resolvedRoot }

    Push-Location $resolvedRoot
    try {
        $preflightLines = & $python -m $service.Module --preflight-only --json 2>&1
        $preflightCode = $LASTEXITCODE
    }
    finally {
        Pop-Location
    }
    $preflightText = Protect-LogText -Text ($preflightLines -join [Environment]::NewLine)
    try { $preflight = $preflightText | ConvertFrom-Json -AsHashtable } catch { $preflight = @{ status = 'invalid'; output = $preflightText } }
    if ($preflightCode -ne 0 -or $preflight.status -notin @('ok', 'degraded')) {
        $receipt = $baseReceipt.Clone()
        $receipt.status = 'blocked'
        $receipt.dependencies = $dependencies
        $receipt.preflight = $preflight
        $receipt.exit_code = $preflightCode
        $receipt.termination_classification = 'preflight_failed'
        $receipt.terminated_at = Get-UtcTimestamp
        Write-JsonAtomic -Path $statePath -Payload $receipt
        if ($Json) { $receipt | ConvertTo-Json -Depth 20 }
        exit 74
    }

    $arguments = @(
        '-m', $service.Module,
        '--host', $service.Host,
        '--port', [string]$service.Port,
        '--path', $service.Path,
        '--state-path', $launcherStatePath,
        '--service-log-path', (Resolve-RepoPath -Root $resolvedRoot -RelativePath $service.ServiceLogPath)
    )
    $hiddenArguments = @('//B', '//NoLogo', $hiddenAdapter, $python) + $arguments
    $argumentText = ($hiddenArguments | ForEach-Object { Quote-ProcessArgument -Value $_ }) -join ' '
    $child = Start-Process -FilePath $wscript -ArgumentList $argumentText -WorkingDirectory $resolvedRoot -PassThru
    $listenerDeadline = [DateTime]::UtcNow.AddSeconds(30)
    do {
        Start-Sleep -Milliseconds 200
        $listener = Get-PortListener -Port $service.Port
        if (-not $listener) { $child.Refresh() }
    } while (-not $listener -and -not $child.HasExited -and [DateTime]::UtcNow -lt $listenerDeadline)
    if (-not $listener) { throw "Managed service did not open port $($service.Port) through the no-window adapter." }
    $running = $baseReceipt.Clone()
    $running.status = 'running'
    $running.adapter_pid = $child.Id
    $running.python_pid = [int]$listener.pid
    $running.no_window_adapter = $hiddenAdapter
    $running.dependencies = $dependencies
    $running.dependency_status = $dependencyStatus
    $running.preflight = $preflight
    $running.stdout_log = $stdoutPath
    $running.stderr_log = $stderrPath
    Write-JsonAtomic -Path $statePath -Payload $running
    if ($Json) { $running | ConvertTo-Json -Depth 20 }

    $child | Wait-Process
    $child.Refresh()
    $exitCode = if ($null -eq $child.ExitCode) { 75 } else { [int]$child.ExitCode }
    # Task Scheduler reliably applies RestartOnFailure to a stable positive action code.
    $finalCode = 70
    $terminated = $running.Clone()
    $terminated.status = 'stopped'
    $terminated.terminated_at = Get-UtcTimestamp
    $terminated.child_exit_code = $exitCode
    $terminated.exit_code = $finalCode
    $terminated.termination_classification = 'unexpected_service_exit'
    Write-JsonAtomic -Path $statePath -Payload $terminated
    exit $finalCode
}
catch [System.Management.Automation.PipelineStoppedException] {
    $interrupted = $baseReceipt.Clone()
    $interrupted.status = 'stopped'
    $interrupted.terminated_at = Get-UtcTimestamp
    $interrupted.exit_code = 130
    $interrupted.termination_classification = 'intentional_interrupt'
    Write-JsonAtomic -Path $statePath -Payload $interrupted
    exit 130
}
catch {
    $failed = $baseReceipt.Clone()
    $failed.status = 'failed'
    $failed.terminated_at = Get-UtcTimestamp
    $failed.exit_code = 76
    $failed.termination_classification = 'runner_failure'
    $failed.error = Protect-LogText -Text $_.Exception.Message
    Write-JsonAtomic -Path $statePath -Payload $failed
    if ($Json) { $failed | ConvertTo-Json -Depth 20 }
    else { Write-Error $failed.error }
    exit 76
}
