param(
    [string]$RepoRoot = 'C:\Git\Agentic-Workflow-FRESH',
    [string]$PythonExe,
    [switch]$Install,
    [switch]$EnsureRunning,
    [switch]$Status,
    [switch]$Uninstall,
    [switch]$Json,
    [ValidateRange(5, 600)]
    [int]$DependencyWaitSeconds = 120,
    [ValidateRange(5, 600)]
    [int]$StartupTimeoutSeconds = 120,
    [ValidateRange(1, 60)]
    [int]$ProbeTimeoutSeconds = 15
)

$ErrorActionPreference = 'Stop'
$script:DefinitionPath = Join-Path $PSScriptRoot 'codex_mcp_http_services.psd1'
$script:RunnerPath = Join-Path $PSScriptRoot 'run_codex_http_mcp_service.ps1'

function Get-UtcTimestamp { return [DateTime]::UtcNow.ToString('o') }

function Resolve-Executable {
    param([string]$Requested, [string[]]$Candidates, [string]$Label)
    if ($Requested) {
        if ([IO.Path]::IsPathRooted($Requested)) {
            if (-not (Test-Path -LiteralPath $Requested -PathType Leaf)) { throw "$Label does not exist: $Requested" }
            return [IO.Path]::GetFullPath($Requested)
        }
        return (Get-Command $Requested -ErrorAction Stop).Source
    }
    foreach ($candidate in $Candidates) {
        $command = Get-Command $candidate -ErrorAction SilentlyContinue
        if ($command) { return $command.Source }
    }
    throw "Unable to resolve $Label."
}

function Resolve-RepoPath {
    param([string]$Root, [string]$RelativePath)
    return [IO.Path]::GetFullPath((Join-Path $Root $RelativePath))
}

function Quote-TaskArgument {
    param([string]$Value)
    return '"' + $Value.Replace('"', '\"') + '"'
}

function Get-ExpectedTaskAction {
    param([hashtable]$Service, [string]$Root, [string]$Pwsh, [string]$Python)
    $arguments = @(
        '-NoLogo', '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass',
        '-File', (Quote-TaskArgument $script:RunnerPath),
        '-ServerId', $Service.ServerId,
        '-RepoRoot', (Quote-TaskArgument $Root),
        '-PythonExe', (Quote-TaskArgument $Python),
        '-DependencyWaitSeconds', [string]$DependencyWaitSeconds
    ) -join ' '
    return [ordered]@{ execute = $Pwsh; arguments = $arguments; working_directory = $Root }
}

function Test-TaskActionMatch {
    param($Task, [hashtable]$Expected)
    if (-not $Task -or @($Task.Actions).Count -ne 1) { return $false }
    $action = @($Task.Actions)[0]
    return (
        [string]::Equals([IO.Path]::GetFullPath($action.Execute), [IO.Path]::GetFullPath($Expected.execute), [StringComparison]::OrdinalIgnoreCase) -and
        [string]::Equals(($action.Arguments -replace '\s+$', ''), $Expected.arguments, [StringComparison]::Ordinal) -and
        [string]::Equals(([string]$action.WorkingDirectory).TrimEnd('\'), $Expected.working_directory.TrimEnd('\'), [StringComparison]::OrdinalIgnoreCase)
    )
}

function Test-TaskSettingsMatch {
    param($Task, [hashtable]$Service)
    if (-not $Task) { return $false }
    $settings = $Task.Settings
    return (
        [bool]$settings.StartWhenAvailable -and
        -not [bool]$settings.DisallowStartIfOnBatteries -and
        -not [bool]$settings.StopIfGoingOnBatteries -and
        [int]$settings.RestartCount -eq [int]$Service.RestartPolicy.Count -and
        [string]$settings.MultipleInstances -match 'IgnoreNew'
    )
}

function Test-TaskTriggersMatch {
    param($Task, [hashtable]$Service)
    if (-not $Task) { return $false }
    $triggers = @($Task.Triggers)
    $hasLogon = [bool]($triggers | Where-Object { $_.CimClass.CimClassName -eq 'MSFT_TaskLogonTrigger' } | Select-Object -First 1)
    $expectedInterval = "PT$([int]$Service.RestartPolicy.WatchdogIntervalMinutes)M"
    $hasWatchdog = [bool]($triggers | Where-Object {
        $_.CimClass.CimClassName -eq 'MSFT_TaskTimeTrigger' -and $_.Repetition.Interval -eq $expectedInterval
    } | Select-Object -First 1)
    return $hasLogon -and $hasWatchdog
}

function Wait-TaskNotRunning {
    param([string]$TaskName, [int]$TimeoutSeconds = 15)
    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    do {
        $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if (-not $task -or [string]$task.State -ne 'Running') { return }
        Start-Sleep -Milliseconds 250
    } while ([DateTime]::UtcNow -lt $deadline)
    throw "Scheduled Task did not stop in time: $TaskName"
}

function Install-ManagedTask {
    param([hashtable]$Service, [string]$Root, [string]$Pwsh, [string]$Python)
    $expected = Get-ExpectedTaskAction -Service $Service -Root $Root -Pwsh $Pwsh -Python $Python
    $existing = Get-ScheduledTask -TaskName $Service.TaskName -ErrorAction SilentlyContinue
    $expectedActionMatch = Test-TaskActionMatch -Task $existing -Expected $expected
    $settingsMatch = Test-TaskSettingsMatch -Task $existing -Service $Service
    $triggersMatch = Test-TaskTriggersMatch -Task $existing -Service $Service
    if ($existing -and $expectedActionMatch -and $settingsMatch -and $triggersMatch -and [bool]$existing.Settings.Enabled) {
        return [ordered]@{ server_id = $Service.ServerId; task_name = $Service.TaskName; action = 'unchanged'; expected_action_match = $true }
    }

    if ($existing) {
        Disable-ScheduledTask -TaskName $Service.TaskName | Out-Null
        Stop-ManagedTaskInstance -Service $Service -Root $Root
    }

    $action = New-ScheduledTaskAction -Execute $expected.execute -Argument $expected.arguments -WorkingDirectory $Root
    $logonTrigger = New-ScheduledTaskTrigger -AtLogOn -User ([Security.Principal.WindowsIdentity]::GetCurrent().Name)
    $watchdogTrigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) `
        -RepetitionInterval (New-TimeSpan -Minutes ([int]$Service.RestartPolicy.WatchdogIntervalMinutes)) `
        -RepetitionDuration (New-TimeSpan -Days ([int]$Service.RestartPolicy.WatchdogDurationDays))
    $principal = New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited
    $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
        -ExecutionTimeLimit ([TimeSpan]::Zero) -RestartCount ([int]$Service.RestartPolicy.Count) `
        -RestartInterval (New-TimeSpan -Minutes ([int]$Service.RestartPolicy.IntervalMinutes)) -MultipleInstances IgnoreNew
    $taskDefinition = New-ScheduledTask -Action $action -Trigger @($logonTrigger, $watchdogTrigger) -Principal $principal -Settings $settings
    Register-ScheduledTask -TaskName $Service.TaskName -InputObject $taskDefinition -Force | Out-Null

    $installed = Get-ScheduledTask -TaskName $Service.TaskName -ErrorAction Stop
    $actionMatches = Test-TaskActionMatch -Task $installed -Expected $expected
    if (-not $actionMatches) { throw "Scheduled Task action validation failed after registration: $($Service.TaskName)" }
    return [ordered]@{
        server_id = $Service.ServerId
        task_name = $Service.TaskName
        action = if ($existing) { 'repaired' } else { 'installed' }
        expected_action_match = $actionMatches
    }
}

function Get-PortListener {
    param([int]$Port)
    $listener = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $listener) { return $null }
    return [ordered]@{ address = $listener.LocalAddress; port = $listener.LocalPort; pid = [int]$listener.OwningProcess }
}

function Read-JsonFile {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    try { return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json -AsHashtable } catch { return $null }
}

function Find-VerifiedManagedListenerPid {
    param([hashtable]$Service, [string]$Root)
    $runnerState = Read-JsonFile -Path (Resolve-RepoPath -Root $Root -RelativePath $Service.StatePath)
    $launcherState = Read-JsonFile -Path (Resolve-RepoPath -Root $Root -RelativePath $Service.LauncherStatePath)
    $listener = Get-PortListener -Port $Service.Port
    if (-not $listener) { return $null }
    $runnerMatches = [bool]($runnerState -and $runnerState.server_id -eq $Service.ServerId -and $runnerState.endpoint -eq $Service.Url -and $runnerState.python_pid -and [int]$runnerState.python_pid -eq [int]$listener.pid)
    $launcherMatches = [bool]($launcherState -and $launcherState.server_id -eq $Service.ServerId -and $launcherState.url -eq $Service.Url -and $launcherState.pid -and [int]$launcherState.pid -eq [int]$listener.pid)
    if ($runnerMatches -or $launcherMatches) {
        $process = Get-CimInstance Win32_Process -Filter "ProcessId=$($listener.pid)" -ErrorAction SilentlyContinue
        $moduleMatch = $process -and $process.CommandLine -match [regex]::Escape($Service.Module)
        $repoMatch = $process -and $process.CommandLine -match [regex]::Escape($Root)
        if ($moduleMatch -and $repoMatch) { return [int]$listener.pid }
    }
    return $null
}

function Stop-ManagedTaskInstance {
    param([hashtable]$Service, [string]$Root)
    $verifiedChildPid = Find-VerifiedManagedListenerPid -Service $Service -Root $Root

    $task = Get-ScheduledTask -TaskName $Service.TaskName -ErrorAction SilentlyContinue
    $wasRunning = [bool]($task -and [string]$task.State -eq 'Running')
    if ($wasRunning) {
        Stop-ScheduledTask -TaskName $Service.TaskName
        Wait-TaskNotRunning -TaskName $Service.TaskName
    }
    if (-not $verifiedChildPid -and $wasRunning) {
        $deadline = [DateTime]::UtcNow.AddSeconds(5)
        do {
            Start-Sleep -Milliseconds 250
            $verifiedChildPid = Find-VerifiedManagedListenerPid -Service $Service -Root $Root
        } while (-not $verifiedChildPid -and [DateTime]::UtcNow -lt $deadline)
    }
    if ($verifiedChildPid -and (Get-Process -Id $verifiedChildPid -ErrorAction SilentlyContinue)) {
        Stop-Process -Id $verifiedChildPid -ErrorAction Stop
        $deadline = [DateTime]::UtcNow.AddSeconds(15)
        do {
            Start-Sleep -Milliseconds 250
            $remaining = Get-PortListener -Port $Service.Port
        } while ($remaining -and [DateTime]::UtcNow -lt $deadline)
        if ($remaining) { throw "Verified managed listener did not stop: $($Service.ServerId) PID $verifiedChildPid" }
    }
}

function Invoke-McpProbe {
    param([hashtable]$Service, [string]$Python, [string]$Tool)
    $stderrPath = Join-Path ([IO.Path]::GetTempPath()) "codex-mcp-probe-$PID-$($Service.ServerId)-$Tool.stderr"
    try {
        $lines = & $Python (Join-Path $resolvedRoot 'scripts/governance/probe_mcp_http_server.py') `
            --url $Service.Url --tool $Tool --timeout $ProbeTimeoutSeconds --json 2>$stderrPath
        $code = $LASTEXITCODE
        $raw = $lines -join [Environment]::NewLine
        try { $payload = $raw | ConvertFrom-Json } catch { $payload = $null }
        $stderrContent = if (Test-Path -LiteralPath $stderrPath) { Get-Content -LiteralPath $stderrPath -Raw } else { $null }
        $stderr = if ($null -eq $stderrContent) { '' } else { ([string]$stderrContent).Trim() }
        if (-not $payload) {
            return [ordered]@{ status = 'fail'; exit_code = $code; initialize = $false; tools_list = $false; tool = $false; error = "invalid probe JSON; $stderr".Trim() }
        }
        return [ordered]@{
            status = $payload.status
            exit_code = $code
            initialize = [bool]$payload.initialize.ok
            tools_list = [bool]$payload.tools_list.ok
            tool = [bool]$payload.tool_call.ok
            tool_name = $Tool
            payload = $payload
        }
    }
    finally {
        Remove-Item -LiteralPath $stderrPath -Force -ErrorAction SilentlyContinue
    }
}

function Find-ServicePid {
    param($IdentityProbe, $HealthProbe)
    foreach ($probe in @($IdentityProbe, $HealthProbe)) {
        if (-not $probe) { continue }
        $serialized = $probe | ConvertTo-Json -Depth 30 -Compress
        $match = [regex]::Match($serialized, '\\?"pid\\?"\s*:\s*(\d+)')
        if ($match.Success) { return [int]$match.Groups[1].Value }
    }
    return $null
}

function Get-ManagedServiceStatus {
    param([hashtable]$Service, [string]$Root, [string]$Pwsh, [string]$Python)
    $expected = Get-ExpectedTaskAction -Service $Service -Root $Root -Pwsh $Pwsh -Python $Python
    $task = Get-ScheduledTask -TaskName $Service.TaskName -ErrorAction SilentlyContinue
    $taskInfo = if ($task) { Get-ScheduledTaskInfo -TaskName $Service.TaskName -ErrorAction SilentlyContinue } else { $null }
    $listener = Get-PortListener -Port $Service.Port
    $runnerState = Read-JsonFile -Path (Resolve-RepoPath -Root $Root -RelativePath $Service.StatePath)
    $launcherState = Read-JsonFile -Path (Resolve-RepoPath -Root $Root -RelativePath $Service.LauncherStatePath)
    $ownership = 'none'
    if ($listener) {
        $runnerProcessAlive = [bool]($runnerState -and $runnerState.runner_pid -and (Get-Process -Id ([int]$runnerState.runner_pid) -ErrorAction SilentlyContinue))
        $runnerOwnsListener = [bool](
            $task -and
            [string]$task.State -eq 'Running' -and
            $runnerProcessAlive -and
            $runnerState -and
            $runnerState.status -eq 'running' -and
            $runnerState.python_pid -and
            [int]$runnerState.python_pid -eq [int]$listener.pid
        )
        $launcherMatches = [bool](
            $launcherState -and
            $launcherState.status -eq 'running' -and
            $launcherState.pid -and
            [int]$launcherState.pid -eq [int]$listener.pid
        )
        $ownership = if ($runnerOwnsListener -and $launcherMatches) { 'managed' } else { 'foreign' }
    }

    $healthProbe = if ($listener) { Invoke-McpProbe -Service $Service -Python $Python -Tool $Service.HealthTool } else { $null }
    $identityProbe = if ($healthProbe -and $healthProbe.status -eq 'ok' -and $Service.IdentityTool) {
        Invoke-McpProbe -Service $Service -Python $Python -Tool $Service.IdentityTool
    } else { $null }
    $protocolHealthy = [bool]($healthProbe -and $healthProbe.initialize -and $healthProbe.tools_list -and $healthProbe.tool)
    $actionMatch = Test-TaskActionMatch -Task $task -Expected $expected
    $overall = if (-not $task) { 'task_missing' } elseif (-not $actionMatch) { 'task_drifted' } elseif ($listener -and $ownership -eq 'foreign') { 'foreign_port_conflict' } elseif ($protocolHealthy) { 'healthy' } elseif ([string]$task.State -eq 'Running') { 'running_unhealthy' } else { 'stopped' }

    return [ordered]@{
        server_id = $Service.ServerId
        task_name = $Service.TaskName
        endpoint = $Service.Url
        task_installed = [bool]$task
        task_enabled = [bool]($task -and $task.Settings.Enabled)
        task_state = if ($task) { [string]$task.State } else { 'Missing' }
        last_run_time = if ($taskInfo -and $taskInfo.LastRunTime) { $taskInfo.LastRunTime.ToString('o') } else { $null }
        last_task_result = if ($taskInfo) { $taskInfo.LastTaskResult } else { $null }
        action_target = if ($task) { @($task.Actions)[0].Execute } else { $null }
        action_arguments = if ($task) { @($task.Actions)[0].Arguments } else { $null }
        expected_action = $expected
        expected_action_match = $actionMatch
        trigger_types = if ($task) { @($task.Triggers | ForEach-Object { $_.CimClass.CimClassName }) } else { @() }
        endpoint_listener = [bool]$listener
        listener_pid = if ($listener) { $listener.pid } else { $null }
        mcp_initialize = [bool]($healthProbe -and $healthProbe.initialize)
        mcp_tools_list = [bool]($healthProbe -and $healthProbe.tools_list)
        health_tool = $Service.HealthTool
        health_tool_status = [bool]($healthProbe -and $healthProbe.tool)
        identity_tool = $Service.IdentityTool
        service_pid = Find-ServicePid -IdentityProbe $identityProbe -HealthProbe $healthProbe
        runner_state_status = if ($runnerState) { $runnerState.status } else { 'absent' }
        ownership_classification = $ownership
        overall_classification = $overall
    }
}

function Ensure-ManagedService {
    param([hashtable]$Service, [string]$Root, [string]$Pwsh, [string]$Python)
    $before = Get-ManagedServiceStatus -Service $Service -Root $Root -Pwsh $Pwsh -Python $Python
    if ($before.overall_classification -eq 'healthy') {
        return [ordered]@{ server_id = $Service.ServerId; action = 'already_healthy'; status = 'PASS'; before = $before; after = $before }
    }
    if ($before.endpoint_listener -and $before.ownership_classification -eq 'foreign') {
        return [ordered]@{ server_id = $Service.ServerId; action = 'blocked'; status = 'FAIL'; reason = 'foreign_port_conflict'; before = $before; after = $before }
    }

    $task = Get-ScheduledTask -TaskName $Service.TaskName -ErrorAction Stop
    $action = if ([string]$task.State -eq 'Running') { 'restarted_unhealthy' } else { 'started' }
    Disable-ScheduledTask -TaskName $Service.TaskName | Out-Null
    try {
        Stop-ManagedTaskInstance -Service $Service -Root $Root
    }
    finally {
        Enable-ScheduledTask -TaskName $Service.TaskName | Out-Null
    }
    Start-ScheduledTask -TaskName $Service.TaskName
    $deadline = [DateTime]::UtcNow.AddSeconds($StartupTimeoutSeconds)
    do {
        Start-Sleep -Seconds 1
        $after = Get-ManagedServiceStatus -Service $Service -Root $Root -Pwsh $Pwsh -Python $Python
        if ($after.overall_classification -eq 'healthy') {
            return [ordered]@{ server_id = $Service.ServerId; action = $action; status = 'PASS'; before = $before; after = $after }
        }
        if ($after.overall_classification -eq 'foreign_port_conflict') {
            return [ordered]@{ server_id = $Service.ServerId; action = 'blocked'; status = 'FAIL'; reason = 'foreign_port_conflict'; before = $before; after = $after }
        }
    } while ([DateTime]::UtcNow -lt $deadline)
    return [ordered]@{ server_id = $Service.ServerId; action = $action; status = 'FAIL'; reason = 'startup_timeout'; before = $before; after = $after }
}

if (-not ($Install -or $EnsureRunning -or $Status -or $Uninstall)) { $Status = $true }
$resolvedRoot = [IO.Path]::GetFullPath($RepoRoot)
if (-not (Test-Path -LiteralPath (Join-Path $resolvedRoot '.mcp.json') -PathType Leaf)) { throw "Invalid RepoRoot: $resolvedRoot" }
if (-not (Test-Path -LiteralPath $script:DefinitionPath -PathType Leaf)) { throw "Missing service definition: $script:DefinitionPath" }
if (-not (Test-Path -LiteralPath $script:RunnerPath -PathType Leaf)) { throw "Missing service runner: $script:RunnerPath" }
$definition = Import-PowerShellDataFile -LiteralPath $script:DefinitionPath
$services = @($definition.Services.Values | Sort-Object { $_.Port })
$python = Resolve-Executable -Requested $PythonExe -Candidates @('python.exe', 'python') -Label 'Python'
$pwsh = Resolve-Executable -Candidates @('pwsh.exe', 'pwsh') -Label 'pwsh.exe'

$report = [ordered]@{
    schema_version = 'codex-mcp-service-tasks/v1'
    generated_at = Get-UtcTimestamp
    repo_root = $resolvedRoot
    operations = @()
    services = @()
    status = 'PASS'
}

try {
    if ($Uninstall) {
        foreach ($service in $services) {
            $task = Get-ScheduledTask -TaskName $service.TaskName -ErrorAction SilentlyContinue
            if ($task) {
                Disable-ScheduledTask -TaskName $service.TaskName | Out-Null
                Stop-ManagedTaskInstance -Service $service -Root $resolvedRoot
                Unregister-ScheduledTask -TaskName $service.TaskName -Confirm:$false
                $report.operations += [ordered]@{ server_id = $service.ServerId; action = 'uninstalled'; status = 'PASS' }
            } else {
                $report.operations += [ordered]@{ server_id = $service.ServerId; action = 'already_absent'; status = 'PASS' }
            }
        }
    } else {
        if ($Install -or $EnsureRunning) {
            foreach ($service in $services) {
                $report.operations += Install-ManagedTask -Service $service -Root $resolvedRoot -Pwsh $pwsh -Python $python
            }
        }
        if ($EnsureRunning) {
            foreach ($service in $services) {
                $result = Ensure-ManagedService -Service $service -Root $resolvedRoot -Pwsh $pwsh -Python $python
                $report.operations += $result
                if ($result.status -ne 'PASS') { $report.status = 'FAIL' }
            }
        }
        if ($Status -or $Install -or $EnsureRunning) {
            foreach ($service in $services) {
                $serviceStatus = Get-ManagedServiceStatus -Service $service -Root $resolvedRoot -Pwsh $pwsh -Python $python
                $report.services += $serviceStatus
                if ($EnsureRunning -and $serviceStatus.overall_classification -ne 'healthy') { $report.status = 'FAIL' }
            }
        }
    }
}
catch {
    $report.status = 'FAIL'
    $report.error = $_.Exception.Message
    $report.error_location = $_.InvocationInfo.PositionMessage
    $report.script_stack = $_.ScriptStackTrace
}

if ($Json) { $report | ConvertTo-Json -Depth 30 }
else {
    Write-Host "MCP service tasks: $($report.status)"
    foreach ($service in $report.services) {
        Write-Host ("{0}: task={1} endpoint={2} ownership={3} overall={4}" -f $service.server_id, $service.task_state, $service.endpoint_listener, $service.ownership_classification, $service.overall_classification)
    }
    if ($report.error) { Write-Error $report.error }
}
if ($report.status -ne 'PASS') { exit 1 }
