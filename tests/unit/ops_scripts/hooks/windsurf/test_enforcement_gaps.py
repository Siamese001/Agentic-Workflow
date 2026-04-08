"""
TARGETED tests for the 5 enforcement gaps identified by the user.

Gap 1: Subprocess timeout not enforced
  - pre_write_gate must block subprocess.run/Popen/call/check_output/check_call
    that lack timeout= in the new_string being written.
  - Must NOT block when timeout= is present.
  - Must block all five subprocess variants.
  - Multi-line calls with timeout= on a later line: allowed.

Gap 2: Structured reasoning mandate not injected for T2/T3
  - pre_prompt_classifier must emit the SR mandate to stderr for T2/T3 prompts
    when infrastructure is healthy.
  - Mandate must contain the key action words Cascade needs:
    mcp8_create_task, SR_INTAKE, SR_PLAN, SR_APPROVAL.
  - T0/T1 must NOT emit the mandate.
  - Mandate must reference the retired Sequential Thinking MCP so Cascade
    knows NOT to use it.

Gap 3: Redis health not checked before T2/T3 work
  - pre_prompt_classifier must exit 2 (BLOCK) when Redis is down for T2/T3.
  - Must NOT block T0/T1 when Redis is down.
  - Must NOT block T2/T3 when Redis is up (even if ADG is also healthy).
  - Block message must mention Redis so Cascade knows why it was blocked.

Gap 4: show_output: false made classifier output invisible to Cascade
  - hooks.json must have show_output: true for pre_user_prompt so Cascade
    can read the SR mandate and tier tag.

Gap 5: check_adg_health_stale renamed → broke test import
  - The function check_adg_health_red must exist and be importable.
  - check_adg_health_stale must NOT exist (was the old broken name).
  - check_adg_health_red must return True when probe reports non-ok status.
  - check_adg_health_red must return False when probe reports ok status.
  - check_adg_health_red must fail-open (return False) when probe errors.
"""

import json
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[5]))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_probe_result(servers: list) -> MagicMock:
    """Build a mock subprocess.run result returning {"servers": [...]} JSON."""
    mock = MagicMock()
    mock.returncode = 0
    mock.stdout = json.dumps({"servers": servers})
    return mock


def _run_classifier_healthy(prompt: str):
    """Run main() with healthy ADG + Redis, return (exit_code, captured)."""
    from ops_scripts.hooks.windsurf.pre_prompt_classifier import main
    payload = {"tool_info": {"user_prompt": prompt}}
    with patch("sys.stdin", StringIO(json.dumps(payload))):
        with patch(
            "ops_scripts.hooks.windsurf.pre_prompt_classifier.check_adg_health_red",
            return_value=False,
        ):
            with patch(
                "ops_scripts.hooks.windsurf.pre_prompt_classifier.check_redis_down",
                return_value=False,
            ):
                import io
                stderr_capture = io.StringIO()
                with patch("sys.stderr", stderr_capture):
                    rc = main()
                return rc, stderr_capture.getvalue()


# ---------------------------------------------------------------------------
# Gap 1: Subprocess timeout enforcement in pre_write_gate
# ---------------------------------------------------------------------------

class TestGap1SubprocessTimeoutEnforcement:
    """
    Gap: subprocess calls without timeout= were not blocked by pre_write_gate.
    Fix: _SUBPROCESS_CALL_RE + _TIMEOUT_RE scan in scan_antipatterns().
    """

    def setup_method(self):
        from ops_scripts.hooks.windsurf.pre_write_gate import scan_antipatterns
        self.scan = scan_antipatterns

    # All 5 subprocess variants must be blocked without timeout=
    def test_subprocess_run_no_timeout_blocked(self):
        v = self.scan("subprocess.run(['git', 'status'])\n")
        assert any("timeout=" in x for x in v), \
            "subprocess.run without timeout= must be blocked (constitutional §14)"

    def test_subprocess_popen_no_timeout_blocked(self):
        v = self.scan("proc = subprocess.Popen(['cmd'], stdout=subprocess.PIPE)\n")
        assert any("timeout=" in x for x in v), \
            "subprocess.Popen without timeout= must be blocked"

    def test_subprocess_call_no_timeout_blocked(self):
        v = self.scan("subprocess.call(['pip', 'install', 'x'])\n")
        assert any("timeout=" in x for x in v), \
            "subprocess.call without timeout= must be blocked"

    def test_subprocess_check_output_no_timeout_blocked(self):
        v = self.scan("out = subprocess.check_output(['git', 'log'])\n")
        assert any("timeout=" in x for x in v), \
            "subprocess.check_output without timeout= must be blocked"

    def test_subprocess_check_call_no_timeout_blocked(self):
        v = self.scan("subprocess.check_call(['make', 'test'])\n")
        assert any("timeout=" in x for x in v), \
            "subprocess.check_call without timeout= must be blocked"

    # All 5 variants allowed when timeout= present
    def test_subprocess_run_with_timeout_allowed(self):
        v = self.scan("subprocess.run(['git', 'status'], timeout=30)\n")
        assert not any("missing timeout=" in x for x in v)

    def test_subprocess_popen_with_timeout_allowed(self):
        v = self.scan("subprocess.Popen(['cmd'], timeout=10)\n")
        assert not any("missing timeout=" in x for x in v)

    def test_subprocess_call_with_timeout_allowed(self):
        v = self.scan("subprocess.call(['pip'], timeout=15)\n")
        assert not any("missing timeout=" in x for x in v)

    def test_subprocess_check_output_with_timeout_allowed(self):
        v = self.scan("subprocess.check_output(['git'], timeout=20)\n")
        assert not any("missing timeout=" in x for x in v)

    def test_subprocess_check_call_with_timeout_allowed(self):
        v = self.scan("subprocess.check_call(['make'], timeout=30)\n")
        assert not any("missing timeout=" in x for x in v)

    # Multiline call — timeout on a later line must be found
    def test_multiline_subprocess_run_timeout_on_later_line_allowed(self):
        code = (
            "result = subprocess.run(\n"
            "    ['git', 'status'],\n"
            "    capture_output=True,\n"
            "    timeout=30,\n"
            ")\n"
        )
        v = self.scan(code)
        assert not any("missing timeout=" in x for x in v)

    # Two calls both missing timeout= → both violations reported
    def test_two_calls_both_missing_both_violations_reported(self):
        code = "subprocess.run(['a'])\nsubprocess.Popen(['b'])\n"
        v = self.scan(code)
        assert sum(1 for x in v if "missing timeout=" in x) == 2, \
            "Both subprocess calls without timeout= must each be reported"

    # One with, one without → only one violation
    def test_one_with_one_without_only_one_violation(self):
        code = "subprocess.run(['a'], timeout=5)\nsubprocess.Popen(['b'])\n"
        v = self.scan(code)
        assert sum(1 for x in v if "missing timeout=" in x) == 1

    # main() integration — ensures the gate fires end-to-end
    def test_main_blocks_subprocess_without_timeout_via_payload(self):
        from ops_scripts.hooks.windsurf.pre_write_gate import main
        payload = {
            "tool_info": {
                "file_path": "ops_scripts/some_script.py",
                "edits": [
                    {"old_string": "", "new_string": "subprocess.run(['git', 'log'])\n"},
                ],
            },
        }
        with patch("sys.stdin", StringIO(json.dumps(payload))):
            with patch("sys.argv", ["pre_write_gate.py"]):
                result = main()
        assert result == 2, "main() must block subprocess.run without timeout="

    def test_main_allows_subprocess_with_timeout_via_payload(self):
        from ops_scripts.hooks.windsurf.pre_write_gate import main
        payload = {
            "tool_info": {
                "file_path": "ops_scripts/some_script.py",
                "edits": [
                    {"old_string": "", "new_string": "subprocess.run(['git', 'log'], timeout=30)\n"},
                ],
            },
        }
        with patch("sys.stdin", StringIO(json.dumps(payload))):
            with patch("sys.argv", ["pre_write_gate.py"]):
                result = main()
        assert result == 0, "main() must allow subprocess.run with timeout="


# ---------------------------------------------------------------------------
# Gap 2: Structured reasoning mandate injected for T2/T3
# ---------------------------------------------------------------------------

class TestGap2StructuredReasoningMandateInjection:
    """
    Gap: pre_prompt_classifier never injected the SR mandate, so Cascade
    continued using the retired Sequential Thinking MCP pattern.
    Fix: _SR_MANDATE printed to stderr for T2/T3 when infra is healthy.
    """

    def test_t3_mandate_contains_mcp8_create_task(self):
        _, stderr = _run_classifier_healthy("refactor the authentication architecture")
        assert "mcp8_create_task" in stderr, \
            "SR mandate must instruct Cascade to call mcp8_create_task for T3"

    def test_t3_mandate_contains_sr_intake(self):
        _, stderr = _run_classifier_healthy("restructure the layer boundaries")
        assert "SR_INTAKE" in stderr, \
            "SR mandate must contain SR_INTAKE block instruction"

    def test_t3_mandate_contains_sr_plan(self):
        # Use a reliable T3 prompt — keyword "architecture" or "refactor"
        _, stderr = _run_classifier_healthy("refactor the architecture to restructure modules")
        assert "SR_PLAN" in stderr, \
            "SR mandate must contain SR_PLAN block instruction"

    def test_t3_mandate_contains_sr_approval(self):
        _, stderr = _run_classifier_healthy("consolidate the duplicate registries")
        assert "SR_APPROVAL" in stderr, \
            "SR mandate must contain SR_APPROVAL gate instruction"

    def test_t3_mandate_mentions_retired_sequential_thinking(self):
        _, stderr = _run_classifier_healthy("refactor the governance model")
        assert (
            "Sequential Thinking" in stderr
            or "RETIRED" in stderr
            or "sequential" in stderr.lower()
        ), "SR mandate must reference that Sequential Thinking MCP is retired"

    def test_t3_mandate_mentions_task_manager(self):
        _, stderr = _run_classifier_healthy("architectural redesign of L0 routing")
        assert (
            "Task Manager" in stderr
            or "mcp8" in stderr
            or "task_manager" in stderr.lower()
        ), "SR mandate must reference Task Manager MCP as replacement"

    def test_t2_mandate_injected(self):
        _, stderr = _run_classifier_healthy("fix and update the hook implementation")
        assert "mcp8_create_task" in stderr, \
            "SR mandate must also be injected for T2 prompts"

    def test_t0_mandate_not_injected(self):
        _, stderr = _run_classifier_healthy("explain how the pre_run_gate works")
        assert "mcp8_create_task" not in stderr, \
            "SR mandate must NOT be injected for T0 (question) prompts"

    def test_t1_mandate_not_injected(self):
        _, stderr = _run_classifier_healthy("fix the typo in the docstring")
        assert "mcp8_create_task" not in stderr, \
            "SR mandate must NOT be injected for T1 (trivial) prompts"

    def test_mandate_not_injected_when_adg_red(self):
        from ops_scripts.hooks.windsurf.pre_prompt_classifier import main
        import io
        payload = {"tool_info": {"user_prompt": "refactor the entire architecture"}}
        with patch("sys.stdin", StringIO(json.dumps(payload))):
            with patch(
                "ops_scripts.hooks.windsurf.pre_prompt_classifier.check_adg_health_red",
                return_value=True,
            ):
                with patch(
                    "ops_scripts.hooks.windsurf.pre_prompt_classifier.check_redis_down",
                    return_value=False,
                ):
                    stderr_cap = io.StringIO()
                    with patch("sys.stderr", stderr_cap):
                        main()
        assert "mcp8_create_task" not in stderr_cap.getvalue(), \
            "SR mandate must NOT be injected when ADG is red (blocked before reaching that code)"

    def test_mandate_not_injected_when_redis_down(self):
        from ops_scripts.hooks.windsurf.pre_prompt_classifier import main
        import io
        payload = {"tool_info": {"user_prompt": "refactor the entire architecture"}}
        with patch("sys.stdin", StringIO(json.dumps(payload))):
            with patch(
                "ops_scripts.hooks.windsurf.pre_prompt_classifier.check_adg_health_red",
                return_value=False,
            ):
                with patch(
                    "ops_scripts.hooks.windsurf.pre_prompt_classifier.check_redis_down",
                    return_value=True,
                ):
                    stderr_cap = io.StringIO()
                    with patch("sys.stderr", stderr_cap):
                        main()
        assert "mcp8_create_task" not in stderr_cap.getvalue(), \
            "SR mandate must NOT be injected when Redis is down (blocked before reaching that code)"


# ---------------------------------------------------------------------------
# Gap 3: Redis health not checked before T2/T3 work
# ---------------------------------------------------------------------------

class TestGap3RedisHealthCheck:
    """
    Gap: pre_prompt_classifier only checked ADG health, not Redis.
    A session with Redis down could allow T2/T3 work to proceed without
    the MCP infrastructure needed for structured reasoning.
    Fix: check_redis_down() function + block T2/T3 when Redis unreachable.
    """

    def setup_method(self):
        from ops_scripts.hooks.windsurf.pre_prompt_classifier import (
            check_redis_down,
            main,
        )
        self.check_redis_down = check_redis_down
        self.main = main

    def _run(self, prompt: str, adg_red: bool = False, redis_down: bool = False) -> tuple:
        import io
        payload = {"tool_info": {"user_prompt": prompt}}
        with patch("sys.stdin", StringIO(json.dumps(payload))):
            with patch(
                "ops_scripts.hooks.windsurf.pre_prompt_classifier.check_adg_health_red",
                return_value=adg_red,
            ):
                with patch(
                    "ops_scripts.hooks.windsurf.pre_prompt_classifier.check_redis_down",
                    return_value=redis_down,
                ):
                    stderr_cap = io.StringIO()
                    with patch("sys.stderr", stderr_cap):
                        rc = self.main()
        return rc, stderr_cap.getvalue()

    # check_redis_down unit tests
    def test_check_redis_down_exists_and_importable(self):
        assert callable(self.check_redis_down), \
            "check_redis_down must be importable from pre_prompt_classifier"

    def test_check_redis_down_returns_true_on_connection_refused(self):
        import socket
        with patch("socket.create_connection", side_effect=ConnectionRefusedError):
            assert self.check_redis_down() is True, \
                "check_redis_down must return True when Redis port is refused"

    def test_check_redis_down_returns_false_on_success(self):
        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        import socket
        with patch("socket.create_connection", return_value=mock_conn):
            assert self.check_redis_down() is False, \
                "check_redis_down must return False when Redis is reachable"

    def test_check_redis_down_fails_open_on_oserror(self):
        import socket
        with patch("socket.create_connection", side_effect=OSError("Network unreachable")):
            assert self.check_redis_down() is False, \
                "check_redis_down must fail-open (return False) on unexpected OSError"

    # Integration: T2/T3 blocked when Redis down
    def test_t3_blocked_when_redis_down(self):
        rc, _ = self._run("refactor the authentication layer", redis_down=True)
        assert rc == 2, "T3 prompt must be BLOCKED when Redis is down"

    def test_t2_blocked_when_redis_down(self):
        rc, _ = self._run("fix and update the test file", redis_down=True)
        assert rc == 2, "T2 prompt must be BLOCKED when Redis is down"

    # Integration: T0/T1 NOT blocked when Redis down
    def test_t0_not_blocked_when_redis_down(self):
        rc, _ = self._run("explain how the hook works", redis_down=True)
        assert rc == 0, "T0 prompt must NOT be blocked even when Redis is down"

    def test_t1_not_blocked_when_redis_down(self):
        rc, _ = self._run("fix the typo in the docstring", redis_down=True)
        assert rc == 0, "T1 prompt must NOT be blocked even when Redis is down"

    # Integration: T2/T3 allowed when both healthy
    def test_t3_allowed_when_redis_up(self):
        rc, _ = self._run("refactor the auth layer", adg_red=False, redis_down=False)
        assert rc == 0, "T3 prompt must be allowed when Redis is up and ADG is healthy"

    # Block message mentions Redis
    def test_redis_block_message_mentions_redis(self):
        _, stderr = self._run("refactor the entire architecture", redis_down=True)
        assert "redis" in stderr.lower() or "Redis" in stderr, \
            "Block message must mention Redis so Cascade knows why it was blocked"

    # Both red: still blocks
    def test_both_adg_red_and_redis_down_still_blocks(self):
        rc, _ = self._run("restructure the layer hierarchy", adg_red=True, redis_down=True)
        assert rc == 2, "Must block when both ADG is red AND Redis is down"


# ---------------------------------------------------------------------------
# Gap 4: show_output: false made classifier output invisible to Cascade
# ---------------------------------------------------------------------------

class TestGap4ShowOutputInHooksJson:
    """
    Gap: hooks.json had show_output: false for pre_user_prompt, meaning
    Cascade never saw the SR mandate or tier tag emitted to stderr.
    Fix: show_output must be true so Cascade receives the classifier output.
    """

    def setup_method(self):
        self.hooks_path = Path(__file__).resolve().parents[5] / ".windsurf" / "hooks.json"

    def test_hooks_json_exists(self):
        assert self.hooks_path.exists(), "hooks.json must exist at .windsurf/hooks.json"

    def test_pre_user_prompt_hook_configured(self):
        data = json.loads(self.hooks_path.read_text(encoding="utf-8"))
        hooks = data.get("hooks", data)
        assert "pre_user_prompt" in hooks, \
            "hooks.json must contain pre_user_prompt hook configuration"

    def test_pre_user_prompt_show_output_is_true(self):
        data = json.loads(self.hooks_path.read_text(encoding="utf-8"))
        hooks = data.get("hooks", data)
        pre_user_prompt = hooks["pre_user_prompt"]
        entries = pre_user_prompt if isinstance(pre_user_prompt, list) else [pre_user_prompt]
        classifier_entries = [
            e for e in entries
            if "pre_prompt_classifier" in e.get("command", "")
        ]
        assert classifier_entries, \
            "No pre_user_prompt hook entry references pre_prompt_classifier"
        for entry in classifier_entries:
            assert entry.get("show_output") is True, (
                f"pre_user_prompt hook for pre_prompt_classifier must have "
                f"show_output: true (found: {entry.get('show_output')!r}). "
                "Without this, Cascade cannot see the SR mandate or tier tag."
            )

    def test_pre_user_prompt_command_is_pre_prompt_classifier(self):
        data = json.loads(self.hooks_path.read_text(encoding="utf-8"))
        hooks = data.get("hooks", data)
        entries = hooks.get("pre_user_prompt", [])
        if not isinstance(entries, list):
            entries = [entries]
        commands = [e.get("command", "") for e in entries]
        assert any("pre_prompt_classifier" in c for c in commands), \
            "pre_user_prompt hook must invoke pre_prompt_classifier.py"

    def test_hooks_json_is_valid_json(self):
        text = self.hooks_path.read_text(encoding="utf-8")
        data = json.loads(text)  # raises if invalid
        assert isinstance(data, dict), "hooks.json must be a JSON object"


# ---------------------------------------------------------------------------
# Gap 5: check_adg_health_stale renamed to check_adg_health_red
# ---------------------------------------------------------------------------

class TestGap5AdgHealthFunctionRename:
    """
    Gap: test suite imported check_adg_health_stale which no longer existed
    after the function was renamed to check_adg_health_red.
    Fix: ensure check_adg_health_red exists, check_adg_health_stale does not.
    """

    def _run_health_check(self, servers_response: list) -> bool:
        """Helper: run check_adg_health_red with a mocked probe that returns servers_response."""
        from ops_scripts.hooks.windsurf.pre_prompt_classifier import check_adg_health_red
        mock_result = _make_probe_result(servers_response)
        with patch(
            "ops_scripts.hooks.windsurf.pre_prompt_classifier.subprocess.run",
            return_value=mock_result,
        ):
            # Also mock probe_script.exists() to return True so the function doesn't bail early
            with patch("pathlib.Path.exists", return_value=True):
                return check_adg_health_red(Path("."))

    def test_check_adg_health_red_importable(self):
        from ops_scripts.hooks.windsurf.pre_prompt_classifier import check_adg_health_red
        assert callable(check_adg_health_red), \
            "check_adg_health_red must be importable and callable"

    def test_check_adg_health_stale_does_not_exist(self):
        import ops_scripts.hooks.windsurf.pre_prompt_classifier as mod
        assert not hasattr(mod, "check_adg_health_stale"), (
            "check_adg_health_stale must not exist — it was the old broken name. "
            "Use check_adg_health_red."
        )

    def test_check_adg_health_red_returns_true_when_probe_reports_non_ok(self):
        result = self._run_health_check([{"name": "adg_sqlite", "status": "error"}])
        assert result is True, \
            "check_adg_health_red must return True when probe reports status != 'ok'"

    def test_check_adg_health_red_returns_false_when_probe_reports_ok(self):
        result = self._run_health_check([{"name": "adg_sqlite", "status": "ok"}])
        assert result is False, \
            "check_adg_health_red must return False when probe reports status == 'ok'"

    def test_check_adg_health_red_fails_open_when_probe_errors(self):
        from ops_scripts.hooks.windsurf.pre_prompt_classifier import check_adg_health_red
        with patch(
            "ops_scripts.hooks.windsurf.pre_prompt_classifier.subprocess.run",
            side_effect=FileNotFoundError("probe not found"),
        ):
            with patch("pathlib.Path.exists", return_value=True):
                result = check_adg_health_red(Path("."))
        assert result is False, \
            "check_adg_health_red must fail-open (return False) when probe script errors"

    def test_check_adg_health_red_fails_open_on_malformed_json(self):
        from ops_scripts.hooks.windsurf.pre_prompt_classifier import check_adg_health_red
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "{not valid json}"
        with patch(
            "ops_scripts.hooks.windsurf.pre_prompt_classifier.subprocess.run",
            return_value=mock_result,
        ):
            with patch("pathlib.Path.exists", return_value=True):
                result = check_adg_health_red(Path("."))
        assert result is False, \
            "check_adg_health_red must fail-open when probe returns malformed JSON"

    def test_check_adg_health_red_fails_open_on_nonzero_exit(self):
        from ops_scripts.hooks.windsurf.pre_prompt_classifier import check_adg_health_red
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        with patch(
            "ops_scripts.hooks.windsurf.pre_prompt_classifier.subprocess.run",
            return_value=mock_result,
        ):
            with patch("pathlib.Path.exists", return_value=True):
                result = check_adg_health_red(Path("."))
        assert result is False, \
            "check_adg_health_red must fail-open when probe exits with non-zero code"

    def test_check_adg_health_red_fails_open_when_probe_script_missing(self):
        from ops_scripts.hooks.windsurf.pre_prompt_classifier import check_adg_health_red
        # probe_script.exists() returns False → should bail out and return False
        with patch("pathlib.Path.exists", return_value=False):
            result = check_adg_health_red(Path("/nonexistent"))
        assert result is False, \
            "check_adg_health_red must fail-open when probe script file does not exist"

    def test_check_adg_health_red_returns_true_when_adg_sqlite_absent_from_results(self):
        # Probe returned results but adg_sqlite not among them → red (absent = unhealthy)
        result = self._run_health_check([{"name": "other_server", "status": "ok"}])
        assert result is True, \
            "check_adg_health_red must return True (red) when adg_sqlite not in probe results"
