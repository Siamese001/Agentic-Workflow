"""Runtime-hardened behavioral tests for ``subprocess_runner_util``."""

from __future__ import annotations

import subprocess
import sys

import pytest

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def subprocess_runner_module():
    return pytest.importorskip("agentic_core.L0_routing.utils.subprocess_runner_util")


class TestInvokeArchGovernorFunction:
    def test_is_callable(self, subprocess_runner_module):
        assert callable(subprocess_runner_module.invoke_arch_governor)


class TestRunJsonCommand:
    def test_success_dict_payload_returned(self, subprocess_runner_module):
        result = subprocess_runner_module._run_json_command(
            [sys.executable, "-c", 'import json; print(json.dumps({"ok": True}))'],
            timeout=10,
        )

        assert result == {"ok": True}

    def test_success_non_dict_json_wrapped(self, subprocess_runner_module):
        result = subprocess_runner_module._run_json_command(
            [sys.executable, "-c", 'print("[1, 2, 3]")'],
            timeout=10,
        )

        assert result == {"success": True, "payload": [1, 2, 3]}

    def test_nonzero_returncode_returns_error_dict(self, subprocess_runner_module):
        result = subprocess_runner_module._run_json_command(
            [sys.executable, "-c", 'import sys; print("err-msg", file=sys.stderr); sys.exit(2)'],
            timeout=10,
        )

        assert result["success"] is False
        assert result["returncode"] == 2

    def test_timeout_returns_error_dict(self, subprocess_runner_module, monkeypatch):
        def _raise_timeout(*args, **kwargs):
            raise subprocess.TimeoutExpired(cmd=["x"], timeout=1)

        monkeypatch.setattr(subprocess_runner_module.subprocess, "run", _raise_timeout)

        result = subprocess_runner_module._run_json_command(["x"], timeout=1)

        assert result["success"] is False
        assert "timed out" in result["error"].lower()

    def test_invalid_json_stdout_returns_error_dict(self, subprocess_runner_module):
        result = subprocess_runner_module._run_json_command(
            [sys.executable, "-c", 'print("not json at all")'],
            timeout=10,
        )

        assert result["success"] is False
        assert "parse" in result["error"].lower() or "failed to parse" in result["error"].lower()
        assert "stdout" in result

    def test_empty_stdout_returns_success_true(self, subprocess_runner_module):
        result = subprocess_runner_module._run_json_command(
            [sys.executable, "-c", "pass"],
            timeout=10,
        )

        assert result == {"success": True}
