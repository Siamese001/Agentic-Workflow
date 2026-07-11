param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('adg_sqlite', 'memory')]
    [string]$ServerId,
    [Parameter(Mandatory = $true)]
    [string]$RepoRoot,
    [string]$PythonExe,
    [switch]$Json,
    [ValidateRange(1, 600)]
    [int]$DependencyWaitSeconds = 120,
    [ValidateRange(100, 10000)]
    [int]$RetryIntervalMilliseconds = 1000
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
    param([hashtable]$Service, [int]$TimeoutSeconds, [int]$PollMilliseconds)
    $started = [DateTime]::UtcNow
    $receipts = @()
    foreach ($dependency in @($Service.Dependencies)) {
        if ($dependency.Kind -ne 'tcp') {
            throw "Unsupported dependency kind: $($dependency.Kind)"
        }
        $ready = $false
        $attempts = 0
        while ((([DateTime]::UtcNow - $started).TotalSeconds -lt $TimeoutSeconds) -and -not $ready) {
            $attempts++
            $ready = Test-TcpDependency -HostName $dependency.Host -Port $dependency.Port -TimeoutMilliseconds ([Math]::Min($PollMilliseconds, 2000))
            if (-not $ready) { Start-Sleep -Milliseconds $PollMilliseconds }
        }
        $receipts += [ordered]@{
            name = $dependency.Name
            kind = $dependency.Kind
            host = $dependency.Host
            port = $dependency.Port
            required = [bool]$dependency.Required
            ready = $ready
            attempts = $attempts
        }
        if ($dependency.Required -and -not $ready) {
            throw "Required dependency '$($dependency.Name)' was not ready within $TimeoutSeconds seconds."
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
    if ($Value -notmatch '[\s"]') { return $Value }
    return '"' + $Value.Replace('"', '\"') + '"'
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
$python = Resolve-PythonExecutable -Requested $PythonExe
$statePath = Resolve-RepoPath -Root $resolvedRoot -RelativePath $service.StatePath
$launcherStatePath = Resolve-RepoPath -Root $resolvedRoot -RelativePath $service.LauncherStatePath
$stdoutPath = Resolve-RepoPath -Root $resolvedRoot -RelativePath $service.StdoutLogPath
$stderrPath = Resolve-RepoPath -Root $resolvedRoot -RelativePath $service.StderrLogPath
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

    $dependencies = Wait-ServiceDependencies -Service $service -TimeoutSeconds $DependencyWaitSeconds -PollMilliseconds $RetryIntervalMilliseconds
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
    $argumentText = ($arguments | ForEach-Object { Quote-ProcessArgument -Value $_ }) -join ' '
    $child = Start-Process -FilePath $python -ArgumentList $argumentText -WorkingDirectory $resolvedRoot `
        -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath -PassThru
    $running = $baseReceipt.Clone()
    $running.status = 'running'
    $running.python_pid = $child.Id
    $running.dependencies = $dependencies
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
