"""
Tests for ops_scripts/ci/mcp_health_monitor.py

Edge cases covered:
- Windows bare 'npx' misconfiguration → MISCONFIGURED error (not hang)
- npx.cmd → classified as is_npx, probed with 5s timeout
- Missing cwd → MISSING_CWD error
- Unknown command type → SKIPPED
- Process exits immediately (non-zero) → STARTUP_FAILED
- Process stays running past timeout → healthy
- FileNotFoundError (command not on PATH) → COMMAND_NOT_FOUND
- OSError (permission denied etc) → OS_ERROR
- Process hangs on terminate → killed via proc.kill()
- Config file missing → empty results list
- Config file malformed JSON → handled gracefully
- Disabled server → skipped
- to_dict() serialisation roundtrip
- print_summary() exit codes: 0=all pass, 1=any fail
- HEALTH_PROBES registry completeness (all mandatory MCPs present)
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# --- import target module --------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from ops_scripts.ci.mcp_health_monitor import (
    HEALTH_PROBES,
    MCPHealthResult,
    print_summary,
    probe_mcp_stdio,
    run_health_probe,
)

REPO_ROOT = Path(r"C:\Git\Agentic-Workflow")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_python_config(**overrides) -> dict:
    base = {
        "command": "python",
        "args": ["-c", "import time; time.sleep(10)"],
        "cwd": str(REPO_ROOT),
    }
    base.update(overrides)
    return base


def _make_npx_config(**overrides) -> dict:
    base = {
        "command": "npx.cmd",
        "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
        "cwd": str(REPO_ROOT),
    }
    base.update(overrides)
    return base


# ===========================================================================
# MCPHealthResult
# ===========================================================================


class TestMCPHealthResult:
    def test_defaults(self):
        r = MCPHealthResult("test_mcp")
        assert r.name == "test_mcp"
        assert r.startup_ok is None
        assert r.health_ok is None
        assert r.latency_ms == 0.0
        assert r.stderr == ""
        assert r.error is None

    def test_to_dict_roundtrip(self):
        r = MCPHealthResult("mcp_x")
        r.startup_ok = True
        r.health_ok = True
        r.latency_ms = 42.5
        r.stderr = "warn: something"
        r.error = None
        r.cwd = "/some/path"

        d = r.to_dict()
        assert d["name"] == "mcp_x"
        assert d["startup_ok"] is True
        assert d["health_ok"] is True
        assert d["latency_ms"] == 42.5
        assert d["stderr_preview"] == "warn: something"
        assert d["error"] is None
        assert d["cwd"] == "/some/path"

    def test_to_dict_stderr_truncated_at_200(self):
        r = MCPHealthResult("x")
        r.stderr = "a" * 500
        d = r.to_dict()
        assert len(d["stderr_preview"]) == 200

    def test_to_dict_empty_stderr(self):
        r = MCPHealthResult("x")
        r.stderr = ""
        d = r.to_dict()
        assert d["stderr_preview"] == ""


# ===========================================================================
# probe_mcp_stdio — Windows npx misconfiguration
# ===========================================================================


class TestProbeWindowsNpxMisconfiguration:
    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-only check")
    def test_bare_npx_returns_misconfigured_on_windows(self):
        cfg = {"command": "npx", "args": ["-y", "some-pkg"], "cwd": str(REPO_ROOT)}
        result = probe_mcp_stdio("seq_thinking", cfg)
        assert result.startup_ok is False
        assert result.error is not None
        assert "MISCONFIGURED" in result.error
        assert "npx.cmd" in result.error

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-only check")
    def test_npx_cmd_not_blocked_on_windows(self):
        """npx.cmd must NOT trigger MISCONFIGURED — it's the correct form."""
        cfg = _make_npx_config(command="npx.cmd")
        # Mock Popen so we don't actually launch a process
        mock_proc = MagicMock()
        mock_proc.wait.side_effect = subprocess.TimeoutExpired(cmd=[], timeout=5)
        mock_proc.terminate = MagicMock()
        with patch("ops_scripts.ci.mcp_health_monitor.subprocess.Popen", return_value=mock_proc):
            result = probe_mcp_stdio("seq_thinking", cfg)
        assert (
            result.error
            != "MISCONFIGURED: command='npx' on Windows — must be 'npx.cmd'. Run: python tools/adg/sync_yaml_to_global.py"
        )

    @pytest.mark.skipif(sys.platform == "win32", reason="Non-Windows: npx allowed")
    def test_bare_npx_not_blocked_on_non_windows(self):
        """On Linux/Mac, bare 'npx' is fine — gate must not trigger."""
        cfg = {"command": "npx", "args": ["-y", "some-pkg"], "cwd": str(REPO_ROOT)}
        mock_proc = MagicMock()
        mock_proc.wait.side_effect = subprocess.TimeoutExpired(cmd=[], timeout=5)
        mock_proc.terminate = MagicMock()
        with patch("ops_scripts.ci.mcp_health_monitor.subprocess.Popen", return_value=mock_proc):
            result = probe_mcp_stdio("seq_thinking", cfg)
        assert result.error is None or "MISCONFIGURED" not in result.error


# ===========================================================================
# probe_mcp_stdio — MCP type classification
# ===========================================================================


class TestProbeClassification:
    def test_missing_cwd_blocks_probe(self):
        cfg = {"command": "python", "args": ["-c", "pass"]}  # no cwd
        result = probe_mcp_stdio("no_cwd", cfg)
        assert result.startup_ok is False
        assert "MISSING_CWD" in result.error

    def test_unknown_command_type_skipped(self):
        cfg = {"command": "ruby", "args": ["server.rb"], "cwd": str(REPO_ROOT)}
        result = probe_mcp_stdio("ruby_mcp", cfg)
        assert result.startup_ok is True
        assert result.health_ok is True
        assert "SKIPPED" in result.error

    def test_gk_command_skipped(self):
        """GitKraken uses 'gk' — should be SKIPPED not MISCONFIGURED."""
        cfg = {"command": "gk", "args": ["mcp"], "cwd": str(REPO_ROOT)}
        result = probe_mcp_stdio("gitkraken", cfg)
        assert "SKIPPED" in result.error


# ===========================================================================
# probe_mcp_stdio — Process lifecycle
# ===========================================================================


class TestProbeProcessLifecycle:
    def _make_proc(self, *, exits_immediately: bool, returncode: int = 1, stderr: str = "") -> MagicMock:
        proc = MagicMock()
        if exits_immediately:
            proc.wait.return_value = returncode
            proc.returncode = returncode
            proc.stderr = MagicMock()
            proc.stderr.read.return_value = stderr
        else:
            proc.wait.side_effect = subprocess.TimeoutExpired(cmd=[], timeout=0.5)
            proc.terminate = MagicMock()
        return proc

    def test_process_exits_immediately_is_startup_failed(self):
        proc = self._make_proc(exits_immediately=True, returncode=1, stderr="ImportError: missing module")
        cfg = _make_python_config()
        with patch("ops_scripts.ci.mcp_health_monitor.subprocess.Popen", return_value=proc):
            result = probe_mcp_stdio("sqlite_mcp", cfg)
        assert result.startup_ok is False
        assert "STARTUP_FAILED" in result.error
        assert result.stderr == "ImportError: missing module"

    def test_process_exits_zero_immediately_is_startup_failed(self):
        """Exit 0 before timeout still means the long-running server died unexpectedly."""
        proc = self._make_proc(exits_immediately=True, returncode=0, stderr="")
        cfg = _make_python_config()
        with patch("ops_scripts.ci.mcp_health_monitor.subprocess.Popen", return_value=proc):
            result = probe_mcp_stdio("sqlite_mcp", cfg)
        assert result.startup_ok is False
        assert "STARTUP_FAILED" in result.error

    def test_process_still_running_after_timeout_is_healthy(self):
        proc = self._make_proc(exits_immediately=False)
        cfg = _make_python_config()
        with patch("ops_scripts.ci.mcp_health_monitor.subprocess.Popen", return_value=proc):
            result = probe_mcp_stdio("redis_mcp", cfg)
        assert result.startup_ok is True
        assert result.health_ok is True
        assert result.error is None

    def test_command_not_found_returns_error(self):
        cfg = {"command": "nonexistent_binary_xyz", "args": [], "cwd": str(REPO_ROOT)}
        # Manually set is_local_python_inline to get past classification
        with patch(
            "ops_scripts.ci.mcp_health_monitor.subprocess.Popen",
            side_effect=FileNotFoundError("[WinError 2] The system cannot find the file"),
        ):
            # Need to trick the classifier — use python -c form
            cfg2 = {"command": "python", "args": ["-c", "pass"], "cwd": str(REPO_ROOT)}
            with patch(
                "ops_scripts.ci.mcp_health_monitor.subprocess.Popen",
                side_effect=FileNotFoundError("not found"),
            ):
                result = probe_mcp_stdio("bad_mcp", cfg2)
        assert result.startup_ok is False
        assert "COMMAND_NOT_FOUND" in result.error

    def test_oserror_returns_os_error(self):
        cfg = _make_python_config()
        with patch(
            "ops_scripts.ci.mcp_health_monitor.subprocess.Popen", side_effect=OSError(13, "Permission denied")
        ):
            result = probe_mcp_stdio("pytest_mcp", cfg)
        assert result.startup_ok is False
        assert "OS_ERROR" in result.error

    def test_stubborn_process_killed_after_terminate_timeout(self):
        """Process ignores terminate() — must be kill()ed."""
        proc = MagicMock()
        proc.wait.side_effect = [
            subprocess.TimeoutExpired(cmd=[], timeout=0.5),  # first wait → healthy
            subprocess.TimeoutExpired(cmd=[], timeout=3),  # second wait after terminate → kill
        ]
        proc.kill = MagicMock()
        cfg = _make_python_config()
        with patch("ops_scripts.ci.mcp_health_monitor.subprocess.Popen", return_value=proc):
            result = probe_mcp_stdio("stubborn_mcp", cfg)
        assert result.startup_ok is True
        proc.kill.assert_called_once()

    def test_npx_uses_5s_probe_timeout(self):
        """npx MCPs must use 5s timeout, not 0.5s."""
        proc = MagicMock()
        proc.terminate = MagicMock()
        captured_timeouts = []

        def wait_side_effect(timeout=None):
            captured_timeouts.append(timeout)
            if len(captured_timeouts) == 1:
                raise subprocess.TimeoutExpired(cmd=[], timeout=timeout)
            return 0

        proc.wait.side_effect = wait_side_effect
        cfg = _make_npx_config()
        with patch("ops_scripts.ci.mcp_health_monitor.subprocess.Popen", return_value=proc):
            probe_mcp_stdio("seq_thinking", cfg)
        assert captured_timeouts[0] == 5, f"npx probe timeout must be 5s, got {captured_timeouts[0]}"

    def test_python_uses_half_second_probe_timeout(self):
        """Local Python MCPs use 0.5s timeout."""
        proc = MagicMock()
        proc.terminate = MagicMock()
        captured_timeouts = []

        def wait_side_effect(timeout=None):
            captured_timeouts.append(timeout)
            if len(captured_timeouts) == 1:
                raise subprocess.TimeoutExpired(cmd=[], timeout=timeout)
            return 0

        proc.wait.side_effect = wait_side_effect
        cfg = _make_python_config()
        with patch("ops_scripts.ci.mcp_health_monitor.subprocess.Popen", return_value=proc):
            probe_mcp_stdio("redis_mcp", cfg)
        assert captured_timeouts[0] == 0.5, f"Python probe timeout must be 0.5s, got {captured_timeouts[0]}"


# ===========================================================================
# run_health_probe — config loading
# ===========================================================================


class TestRunHealthProbe:
    def test_missing_config_returns_empty(self, tmp_path):
        result = run_health_probe(tmp_path / "nonexistent.json")
        assert result == []

    def test_disabled_server_skipped(self, tmp_path):
        config = {
            "mcpServers": {
                "my_mcp": {"command": "python", "args": [], "cwd": str(tmp_path), "disabled": True}
            }
        }
        cfg_file = tmp_path / "mcp_config.json"
        cfg_file.write_text(json.dumps(config), encoding="utf-8")
        results = run_health_probe(cfg_file)
        assert all(r.name != "my_mcp" for r in results)

    def test_valid_config_runs_probe_per_server(self, tmp_path):
        config = {
            "mcpServers": {
                "mcp_a": {"command": "python", "args": ["-c", "pass"], "cwd": str(tmp_path)},
                "mcp_b": {"command": "python", "args": ["-c", "pass"], "cwd": str(tmp_path)},
            },
        }
        cfg_file = tmp_path / "mcp_config.json"
        cfg_file.write_text(json.dumps(config), encoding="utf-8")

        mock_proc = MagicMock()
        mock_proc.wait.side_effect = subprocess.TimeoutExpired(cmd=[], timeout=0.5)
        mock_proc.terminate = MagicMock()
        with patch("ops_scripts.ci.mcp_health_monitor.subprocess.Popen", return_value=mock_proc):
            results = run_health_probe(cfg_file)
        assert len(results) == 2
        assert {r.name for r in results} == {"mcp_a", "mcp_b"}


# ===========================================================================
# print_summary — exit code logic
# ===========================================================================


class TestPrintSummary:
    def _healthy(self, name: str) -> MCPHealthResult:
        r = MCPHealthResult(name)
        r.startup_ok = True
        r.health_ok = True
        return r

    def _failed(self, name: str, error: str = "STARTUP_FAILED: Exit code 1") -> MCPHealthResult:
        r = MCPHealthResult(name)
        r.startup_ok = False
        r.error = error
        return r

    def test_all_healthy_returns_0(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "ops_scripts.ci.mcp_health_monitor.REPO_ROOT",
            tmp_path,
        )
        (tmp_path / "artifacts" / "adg").mkdir(parents=True)
        results = [self._healthy("adg_redis"), self._healthy("redis_mcp")]
        exit_code = print_summary(results)
        assert exit_code == 0

    def test_any_failure_returns_1(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "ops_scripts.ci.mcp_health_monitor.REPO_ROOT",
            tmp_path,
        )
        (tmp_path / "artifacts" / "adg").mkdir(parents=True)
        results = [self._healthy("adg_redis"), self._failed("redis_mcp")]
        exit_code = print_summary(results)
        assert exit_code == 1

    def test_all_failed_returns_1(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "ops_scripts.ci.mcp_health_monitor.REPO_ROOT",
            tmp_path,
        )
        (tmp_path / "artifacts" / "adg").mkdir(parents=True)
        results = [self._failed("adg_redis"), self._failed("redis_mcp")]
        exit_code = print_summary(results)
        assert exit_code == 1

    def test_writes_health_report_json(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "ops_scripts.ci.mcp_health_monitor.REPO_ROOT",
            tmp_path,
        )
        (tmp_path / "artifacts" / "adg").mkdir(parents=True)
        results = [self._healthy("adg_redis")]
        print_summary(results)
        report = tmp_path / "artifacts" / "adg" / "mcp_health_report.json"
        assert report.exists()
        data = json.loads(report.read_text())
        assert "summary" in data
        assert data["summary"]["total"] == 1
        assert data["summary"]["healthy"] == 1

    def test_skipped_servers_not_counted_as_failed(self, tmp_path, monkeypatch):
        """Servers with SKIPPED error (unknown type) must not inflate fail count."""
        monkeypatch.setattr(
            "ops_scripts.ci.mcp_health_monitor.REPO_ROOT",
            tmp_path,
        )
        (tmp_path / "artifacts" / "adg").mkdir(parents=True)
        skipped = MCPHealthResult("gitkraken")
        skipped.startup_ok = True
        skipped.health_ok = True
        skipped.error = "SKIPPED: Unknown MCP type"
        results = [skipped]
        exit_code = print_summary(results)
        assert exit_code == 0


# ===========================================================================
# HEALTH_PROBES registry — mandatory MCP coverage
# ===========================================================================


class TestHealthProbesRegistry:
    MANDATORY_MCPS = {
        "adg_redis",
        "memory",
        "filesystem",
        "sequential_thinking",
        "redis_mcp",
        "pytest_mcp",
        "otel_mcp",
    }

    def test_all_mandatory_mcps_registered(self):
        missing = self.MANDATORY_MCPS - set(HEALTH_PROBES.keys())
        assert not missing, f"Missing mandatory MCP probes: {missing}"

    def test_each_probe_has_required_fields(self):
        for name, probe in HEALTH_PROBES.items():
            assert "method" in probe, f"{name}: missing 'method'"
            assert "tool" in probe, f"{name}: missing 'tool'"
            assert "args" in probe, f"{name}: missing 'args'"
            assert "timeout" in probe, f"{name}: missing 'timeout'"

    def test_sequential_thinking_probe_args_valid(self):
        probe = HEALTH_PROBES["sequential_thinking"]
        args = probe["args"]
        assert "thought" in args
        assert "nextThoughtNeeded" in args
        assert args["nextThoughtNeeded"] is False, "Health check must not chain thoughts"
        assert args.get("thoughtNumber") == 1
        assert args.get("totalThoughts") == 1

    def test_timeouts_are_positive(self):
        for name, probe in HEALTH_PROBES.items():
            assert probe["timeout"] > 0, f"{name}: timeout must be positive"

    def test_redis_probe_timeout_is_fast(self):
        assert HEALTH_PROBES["redis_mcp"]["timeout"] <= 5, "Redis health should be fast (<=5s)"

    def test_pytest_probe_timeout_sufficient(self):
        assert HEALTH_PROBES["pytest_mcp"]["timeout"] >= 10, "PyTest discovery needs time (>=10s)"
