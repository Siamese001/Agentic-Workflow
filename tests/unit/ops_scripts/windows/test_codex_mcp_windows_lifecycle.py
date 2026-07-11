"""Contract tests for the repo-owned Windows HTTP MCP lifecycle."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
WINDOWS = REPO_ROOT / "ops_scripts" / "windows"
SERVICE_DATA = WINDOWS / "codex_mcp_http_services.psd1"
RUNNER = WINDOWS / "run_codex_http_mcp_service.ps1"
TASKS = WINDOWS / "codex_mcp_service_tasks.ps1"
PREFLIGHT = WINDOWS / "codex_mcp_preflight.ps1"
LAUNCHER = WINDOWS / "launch_codex_agentic.ps1"
SHORTCUT = WINDOWS / "install_codex_agentic_shortcut.ps1"
HIDDEN_ADAPTER = WINDOWS / "run_hidden_wait.vbs"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_service_definition_has_exact_managed_routes() -> None:
    text = _read(SERVICE_DATA)

    assert set(re.findall(r"(?m)^\s{8}(adg_sqlite|memory)\s*=\s*@\{", text)) == {
        "adg_sqlite",
        "memory",
    }
    for expected in (
        "AgenticWorkflow-ADG-HTTP-MCP",
        "tools.mcp.launch_adg_sqlite_http_mcp",
        "http://127.0.0.1:8765/mcp",
        "adg_health",
        "AgenticWorkflow-Memory-HTTP-MCP",
        "tools.mcp.launch_memory_http_mcp",
        "http://127.0.0.1:8766/mcp",
        "memory_health",
    ):
        assert expected in text


def test_all_windows_lifecycle_scripts_consume_shared_definition() -> None:
    for path in (RUNNER, TASKS, PREFLIGHT):
        assert "codex_mcp_http_services.psd1" in _read(path)


def test_runner_is_foreground_fail_closed_and_redacts_credentials() -> None:
    text = _read(RUNNER)

    assert "Start-Process" in text and "Wait-Process" in text
    assert "unexpected_service_exit" in text
    assert "credential" in text.lower() and "REDACTED" in text
    assert "ADG_REDIS_URL" in text and "redis://localhost:6379/0" in text
    assert "foreign_port_conflict" in text
    assert "run_hidden_wait.vbs" in text
    assert "wscript.exe" in text
    assert "adapter_pid" in text


def test_task_manager_repairs_drift_and_has_required_ensure_branches() -> None:
    text = _read(TASKS)

    assert "run_codex_http_mcp_service.ps1" in text
    assert "Register-ScheduledTask" in text and "-Force" in text
    assert "expected_action_match" in text
    assert "already_healthy" in text
    assert "Start-ScheduledTask" in text
    assert "foreign_port_conflict" in text
    assert "RestartCount" in text and "RestartInterval" in text
    assert "WatchdogIntervalMinutes" in _read(SERVICE_DATA)
    assert "New-ScheduledTaskTrigger -Once" in text
    assert "MultipleInstances IgnoreNew" in text
    for field in (
        "working_directory",
        "logon_type",
        "run_level",
        "enabled",
        "logon_trigger_user",
        "watchdog_interval",
        "watchdog_duration",
        "restart_interval",
        "restart_count",
        "disallow_start_on_battery",
        "stop_on_battery",
        "execution_limit",
        "multiple_instances",
    ):
        assert field in text
    assert "task_fingerprint_match" in text


def test_complete_task_fingerprint_drift_is_detected_behaviorally() -> None:
    command = rf"""
. '{TASKS}' -FunctionsOnly
$service=@{{RestartPolicy=@{{Count=255;IntervalMinutes=1;WatchdogIntervalMinutes=1;WatchdogDurationDays=3650}}}}
$expected=@{{execute='C:\Windows\System32\wscript.exe';arguments='expected';working_directory='{REPO_ROOT}'}}
$settings=[pscustomobject]@{{Enabled=$false;StartWhenAvailable=$false;DisallowStartIfOnBatteries=$true;StopIfGoingOnBatteries=$true;ExecutionTimeLimit='PT1H';RestartCount=1;RestartInterval='PT2M';MultipleInstances='Parallel'}}
$principal=[pscustomobject]@{{UserId='not-the-managed-user';LogonType='Password';RunLevel='Highest'}}
$logon=[pscustomobject]@{{CimClass=[pscustomobject]@{{CimClassName='MSFT_TaskLogonTrigger'}};UserId='wrong-user'}}
$watchdog=[pscustomobject]@{{CimClass=[pscustomobject]@{{CimClassName='MSFT_TaskTimeTrigger'}};Repetition=[pscustomobject]@{{Interval='PT2M';Duration='P1D';StopAtDurationEnd=$false}}}}
$task=[pscustomobject]@{{Actions=@([pscustomobject]@{{Execute='C:\Windows\System32\cmd.exe';Arguments='wrong';WorkingDirectory='C:\'}});Settings=$settings;Principal=$principal;Triggers=@($logon,$watchdog)}}
@(Get-TaskDriftFields -Task $task -Expected $expected -Service $service) | ConvertTo-Json
"""
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", command],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    drift = set(json.loads(result.stdout))
    assert {
        "action",
        "arguments",
        "working_directory",
        "user",
        "logon_type",
        "run_level",
        "enabled",
        "logon_trigger_user",
        "watchdog_interval",
        "watchdog_duration",
        "restart_interval",
        "restart_count",
        "disallow_start_on_battery",
        "stop_on_battery",
        "execution_limit",
        "multiple_instances",
    } <= drift


def test_preflight_preserves_sync_and_requires_health_tools() -> None:
    text = _read(PREFLIGHT)

    assert "[switch]$Sync" in text
    assert "[switch]$EnsureServices" in text
    assert "--sync-user-config" in text
    assert "probe_mcp_http_server.py" in text
    assert "HealthTool" in text


def test_launcher_no_launch_and_shortcut_avoid_versioned_codex_path() -> None:
    launcher = _read(LAUNCHER)
    shortcut = _read(SHORTCUT)

    assert "[switch]$NoLaunch" in launcher
    assert "codex_mcp_preflight.ps1" in launcher
    assert "Start-Process" in launcher
    assert "Codex — Agentic Workflow" in shortcut
    assert "launch_codex_agentic.ps1" in shortcut
    assert "run_hidden_wait.vbs" in shortcut
    assert "$shortcut.TargetPath = $wscript" in shortcut
    assert "SuppressErrorDialog" in launcher
    assert "WScript.Shell" in launcher
    assert not re.search(r"Codex[^\r\n]*app-\d", launcher + shortcut, re.IGNORECASE)


def test_repo_routes_remain_required_streamable_http() -> None:
    mcp = json.loads((REPO_ROOT / ".mcp.json").read_text(encoding="utf-8"))
    config = (REPO_ROOT / ".codex" / "config.toml").read_text(encoding="utf-8")

    assert mcp["mcpServers"]["adg_sqlite"] == {"url": "http://127.0.0.1:8765/mcp"}
    assert mcp["mcpServers"]["memory"] == {"url": "http://127.0.0.1:8766/mcp"}
    for server_id, url in (
        ("adg_sqlite", "http://127.0.0.1:8765/mcp"),
        ("memory", "http://127.0.0.1:8766/mcp"),
    ):
        block = re.search(rf"(?ms)^\[mcp_servers\.{server_id}\]\s*$\n(.*?)(?=^\[|\Z)", config)
        assert block is not None
        assert f'url = "{url}"' in block.group(1)
        assert "required = true" in block.group(1)
        assert "command =" not in block.group(1)


def test_new_powershell_files_parse() -> None:
    paths = [SERVICE_DATA, RUNNER, TASKS, PREFLIGHT, LAUNCHER, SHORTCUT]
    quoted = ",".join(f"'{path}'" for path in paths)
    command = (
        "$errors=@(); "
        f"@({quoted}) | ForEach-Object {{ "
        "[System.Management.Automation.Language.Parser]::ParseFile($_,[ref]$null,[ref]$errors) | Out-Null }; "
        "if($errors.Count){$errors | ForEach-Object {$_.ToString()}; exit 1}"
    )
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", command],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_hidden_adapter_propagates_exact_exit_code() -> None:
    pwsh = subprocess.run(
        ["powershell", "-NoProfile", "-Command", "(Get-Command pwsh.exe).Source"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=True,
    ).stdout.strip()
    result = subprocess.run(
        ["wscript.exe", "//B", "//NoLogo", str(HIDDEN_ADAPTER), pwsh, "-NoProfile", "-Command", "exit 37"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 37
    assert result.stdout == ""
    assert result.stderr == ""


def _dependency_probe(server_id: str, tmp_path: Path) -> subprocess.CompletedProcess[str]:
    (tmp_path / ".mcp.json").write_text('{"mcpServers":{}}', encoding="utf-8")
    return subprocess.run(
        [
            "pwsh.exe",
            "-NoLogo",
            "-NoProfile",
            "-NonInteractive",
            "-File",
            str(RUNNER),
            "-ServerId",
            server_id,
            "-RepoRoot",
            str(tmp_path),
            "-DependencyProbeOnly",
            "-DependencyHostOverride",
            "127.0.0.1",
            "-DependencyPortOverride",
            "1",
            "-DependencyWaitSeconds",
            "1",
            "-RetryIntervalMilliseconds",
            "100",
            "-Json",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


def test_adg_continues_degraded_when_redis_is_unreachable(tmp_path: Path) -> None:
    result = _dependency_probe("adg_sqlite", tmp_path)
    payload = json.loads(result.stdout)

    assert result.returncode == 0
    assert payload["status"] == "degraded"
    assert payload["dependency_status"] == "degraded"
    assert payload["dependencies"]["failure_policy"] == "continue_degraded"
    assert payload["dependencies"]["ready"] is False


def test_memory_blocks_when_redis_is_unreachable(tmp_path: Path) -> None:
    result = _dependency_probe("memory", tmp_path)
    payload = json.loads(result.stdout)

    assert result.returncode != 0
    assert result.returncode == 78
    assert payload["status"] == "blocked"
    assert payload["dependency_status"] == "blocked"
    assert payload["termination_classification"] == "dependency_blocked"
    assert payload["dependencies"]["failure_policy"] == "block"
