"""W1.4 — post-agent long-command audit (``post_cursor_agent_long_command_audit agent_response``)."""

from __future__ import annotations

import argparse
import json
import sys
from io import StringIO
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
SCRIPT = REPO_ROOT / ".claude" / "governance/scripts" / "post_cursor_agent_long_command_audit.py"


@pytest.fixture()
def long_cmd_mod(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    import importlib.util

    name = "_post_agent_long_cmd_test"
    spec = importlib.util.spec_from_file_location(name, SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    monkeypatch.setattr(mod, "violations_log", tmp_path / "long_command_violations.jsonl")
    monkeypatch.setattr(mod, "post_agent_audit_log", tmp_path / "long_command_post_agent_audit.jsonl")
    monkeypatch.delenv("LONG_COMMAND_AUDIT_BYPASS", raising=False)
    return mod


def _run_agent_response(mod, stdin_obj: StringIO, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "stdin", stdin_obj)
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
    mod.cmd_agent_response(argparse.Namespace())


class TestPostAgentLongCommandAgentResponse:
    def test_not_applicable_no_run_command_surface(self, long_cmd_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        payload = {"text": "Hello — prose only, no XML invoke."}
        _run_agent_response(long_cmd_mod, StringIO(json.dumps(payload)), monkeypatch)
        log = long_cmd_mod.post_agent_audit_log
        assert log.exists()
        rows = [json.loads(line) for line in log.read_text(encoding="utf-8").strip().splitlines()]
        assert rows[-1]["event"] == "not_applicable"
        assert rows[-1]["reason"] == "no_run_command_surface"

    def test_not_applicable_empty_stdin(self, long_cmd_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        _run_agent_response(long_cmd_mod, StringIO(""), monkeypatch)
        log = long_cmd_mod.post_agent_audit_log
        assert log.exists()
        row = json.loads(log.read_text(encoding="utf-8").strip().splitlines()[-1])
        assert row["event"] == "not_applicable"
        assert row["reason"] == "empty_stdin"

    def test_applicable_allow_clean_short_command(self, long_cmd_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        text = (
            'Ran a quick check.\n<invoke name="run_command">'
            '<parameter name="CommandLine">echo hi</parameter>'
            '<parameter name="Blocking">true</parameter></invoke>\nDone.'
        )
        _run_agent_response(long_cmd_mod, StringIO(json.dumps({"text": text})), monkeypatch)
        log = long_cmd_mod.post_agent_audit_log
        rows = [json.loads(line) for line in log.read_text(encoding="utf-8").strip().splitlines()]
        assert rows[-1]["event"] == "allow"
        assert rows[-1]["reason"] == "long_command_guard_ok"
        assert not long_cmd_mod.violations_log.exists()

    def test_applicable_violation_pytest_no_timeout(self, long_cmd_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        text = (
            '<invoke name="run_command">'
            '<parameter name="CommandLine">pytest tests/ -q</parameter>'
            '<parameter name="Blocking">true</parameter></invoke>'
        )
        _run_agent_response(long_cmd_mod, StringIO(json.dumps({"text": text})), monkeypatch)
        vlog = long_cmd_mod.violations_log
        assert vlog.exists()
        vrow = json.loads(vlog.read_text(encoding="utf-8").strip().splitlines()[-1])
        assert vrow["code"] == "LONG_COMMAND_NO_TIMEOUT"
        assert vrow["command_label"] == "pytest"
        audit = long_cmd_mod.post_agent_audit_log
        arow = json.loads(audit.read_text(encoding="utf-8").strip().splitlines()[-1])
        assert arow["event"] == "violation_advisory"

    def test_bypass_not_applicable(self, long_cmd_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("LONG_COMMAND_AUDIT_BYPASS", "1")
        text = (
            '<invoke name="run_command"><parameter name="CommandLine">pytest x</parameter></invoke>'
        )
        _run_agent_response(long_cmd_mod, StringIO(json.dumps({"text": text})), monkeypatch)
        assert not long_cmd_mod.post_agent_audit_log.exists()


class TestLegacyMainStdin:
    """Legacy path (no subcommand) still records violations under Cursor paths only."""

    def test_legacy_main_writes_violations_to_patched_path(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        import importlib.util

        name = "_long_cmd_legacy_inline"
        spec = importlib.util.spec_from_file_location(name, SCRIPT)
        assert spec and spec.loader
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        vlog = tmp_path / "vio.jsonl"
        monkeypatch.setattr(mod, "violations_log", vlog)
        text = (
            '<invoke name="run_command">'
            '<parameter name="CommandLine">pytest t.py</parameter></invoke>'
        )
        payload = json.dumps({"tool_info": {"response": text}})
        monkeypatch.setattr(sys, "stdin", StringIO(payload))
        monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
        monkeypatch.setattr(sys, "argv", [str(SCRIPT)])
        assert mod.main() == 0
        assert vlog.exists()
        row = json.loads(vlog.read_text(encoding="utf-8").strip().splitlines()[-1])
        assert row["code"] == "LONG_COMMAND_NO_TIMEOUT"


class TestAfterAgentChainOrdering:
    def test_long_command_after_mcp_hygiene_author_gate_first(self) -> None:
        hook = REPO_ROOT / ".cursor" / "hooks" / "after_agent_governance_dispatch.py"
        text = hook.read_text(encoding="utf-8")
        capture_pos = text.index("post_cursor_agent_author_gate_capture.py")
        mcp_pos = text.rindex("post_cursor_agent_mcp_hygiene_audit.py")
        long_pos = text.rindex("post_cursor_agent_long_command_audit.py")
        assert capture_pos < mcp_pos < long_pos
        assert "_SCRIPT_EXTRA_ARGS" in text
        assert '"post_cursor_agent_long_command_audit.py"' in text
