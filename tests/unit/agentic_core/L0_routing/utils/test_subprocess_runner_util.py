"""Behavioral tests for agentic_core/L0_routing/utils/subprocess_runner_util.py."""

from __future__ import annotations

import json
import subprocess
import sys
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L0_routing.utils.subprocess_runner_util import _run_json_command


class TestInvokeArchGovernorFunction:
    def test_is_callable(self):
        """invoke_arch_governor is importable and callable."""
        from agentic_core.L0_routing.utils.subprocess_runner_util import invoke_arch_governor

        assert callable(invoke_arch_governor)


@pytest.mark.unit
class TestRunJsonCommand:
    """Tests for _run_json_command — the unified subprocess helper from L0 hardening phase."""

    def test_success_dict_payload_returned(self):
        """Returns the parsed dict when subprocess exits 0 with valid JSON."""
        result = _run_json_command(
            [sys.executable, "-c", 'import json, sys; print(json.dumps({"ok": True}))'],
            timeout=10,
        )
        assert result == {"ok": True}

    def test_success_non_dict_json_wrapped(self):
        """When subprocess emits a JSON list, wraps in {'success': True, 'payload': ...}."""
        result = _run_json_command(
            [sys.executable, "-c", 'print("[1, 2, 3]")'],
            timeout=10,
        )
        assert result == {"success": True, "payload": [1, 2, 3]}

    def test_nonzero_returncode_returns_error_dict(self):
        """Returns {'success': False, 'error': ..., 'returncode': N} on nonzero exit."""
        result = _run_json_command(
            [sys.executable, "-c", 'import sys; print("err-msg", file=sys.stderr); sys.exit(2)'],
            timeout=10,
        )
        assert result["success"] is False
        assert "returncode" in result
        assert result["returncode"] == 2

    def test_timeout_returns_error_dict(self):
        """Returns {'success': False, 'error': '...timed out...'} on SubprocessTimeoutExpired."""
        completed = MagicMock()
        completed.returncode = 0
        completed.stdout = ""
        completed.stderr = ""

        with patch(
            "agentic_core.L0_routing.utils.subprocess_runner_util.subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd=["x"], timeout=1),
        ):
            result = _run_json_command(["x"], timeout=1)

        assert result["success"] is False
        assert "timed out" in result["error"]

    def test_invalid_json_stdout_returns_error_dict(self):
        """Returns {'success': False, 'error': '...parse...', 'stdout': ...} on invalid JSON."""
        result = _run_json_command(
            [sys.executable, "-c", 'print("not json at all")'],
            timeout=10,
        )
        assert result["success"] is False
        assert "parse" in result["error"].lower() or "Failed to parse" in result["error"]
        assert "stdout" in result

    def test_empty_stdout_returns_success_true(self):
        """Returns {'success': True} when subprocess exits 0 with no stdout."""
        result = _run_json_command(
            [sys.executable, "-c", "pass"],
            timeout=10,
        )
        assert result == {"success": True}
