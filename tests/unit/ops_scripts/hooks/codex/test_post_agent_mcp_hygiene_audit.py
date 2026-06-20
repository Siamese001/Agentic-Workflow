"""W1.3 — post-agent MCP hygiene (``post_agent_mcp_hygiene_audit agent_response``)."""

from __future__ import annotations

import argparse
import json
import sys
from io import StringIO
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
SCRIPT = REPO_ROOT / ".codex" / "governance/scripts" / "post_agent_mcp_hygiene_audit.py"


@pytest.fixture()
def hygiene_mod(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    import importlib.util

    name = "_post_agent_mcp_hygiene_test"
    spec = importlib.util.spec_from_file_location(name, SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    fake_logs = {
        "preflight": tmp_path / "preflight.jsonl",
        "orphan_reap": tmp_path / "orphan_reap.jsonl",
        "serialization": tmp_path / "serialization.jsonl",
        "post_agent": tmp_path / "post_agent.jsonl",
    }
    monkeypatch.setattr(mod, "LOG_PATHS", fake_logs)
    monkeypatch.delenv("MCP_HYGIENE_BYPASS", raising=False)
    monkeypatch.delenv("MCP_POST_AGENT_HYGIENE_BYPASS", raising=False)
    return mod


def _run_agent_response(mod, stdin_obj: StringIO, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "stdin", stdin_obj)
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
    mod.cmd_agent_response(argparse.Namespace())


class TestPostAgentMcpHygieneAgentResponse:
    def test_not_applicable_no_mcp_surface(self, hygiene_mod, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        payload = {"text": "Hello — no tools here."}
        _run_agent_response(hygiene_mod, StringIO(json.dumps(payload)), monkeypatch)
        log = hygiene_mod.LOG_PATHS["post_agent"]
        assert log.exists()
        rows = [json.loads(line) for line in log.read_text(encoding="utf-8").strip().splitlines()]
        assert rows[-1]["event"] == "not_applicable"

    def test_applicable_allow_clean(self, hygiene_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        payload = {"text": '<invoke name="mcp1_adg_health">adg probe only</invoke>'}
        _run_agent_response(hygiene_mod, StringIO(json.dumps(payload)), monkeypatch)
        log = hygiene_mod.LOG_PATHS["post_agent"]
        rows = [json.loads(line) for line in log.read_text(encoding="utf-8").strip().splitlines()]
        assert rows[-1]["event"] == "allow"

    def test_applicable_violation_serialization_dup(self, hygiene_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        payload = {
            "text": (
                '<invoke name="mcp1_x">notion_ aa notion_ bb mcp surface</invoke>'
            )
        }
        _run_agent_response(hygiene_mod, StringIO(json.dumps(payload)), monkeypatch)
        ser = hygiene_mod.LOG_PATHS["serialization"]
        assert ser.exists()
        row = json.loads(ser.read_text(encoding="utf-8").strip().splitlines()[-1])
        assert row["event"] == "serialization_violation"
        assert "notion" in row["violations"]

    def test_bypass_not_applicable(self, hygiene_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MCP_POST_AGENT_HYGIENE_BYPASS", "1")
        _run_agent_response(hygiene_mod, StringIO(json.dumps({"text": "mcp0_y"})), monkeypatch)
        assert not hygiene_mod.LOG_PATHS["post_agent"].exists()


class TestRunAllDoesNotReap:
    def test_run_all_does_not_call_orphan_reap(self, hygiene_mod, monkeypatch: pytest.MonkeyPatch) -> None:
        calls: list[str] = []

        def fake_orphan(args: argparse.Namespace) -> int:
            calls.append("orphan")
            return 0

        monkeypatch.setattr(hygiene_mod, "cmd_orphan_reap", fake_orphan)
        hygiene_mod._cmd_run_all(argparse.Namespace())
        assert calls == []


class TestAfterAgentChainWiring:
    def test_mcp_hygiene_before_long_command_with_agent_response_argv(self) -> None:
        text = (REPO_ROOT / ".codex" / "hooks" / "after_agent_governance_dispatch.py").read_text(encoding="utf-8")
        assert "post_agent_mcp_hygiene_audit.py" in text
        assert "post_agent_long_command_audit.py" in text
        assert "agent_response" in text
        mcp_pos = text.rindex("post_agent_mcp_hygiene_audit.py")
        long_pos = text.rindex("post_agent_long_command_audit.py")
        burndown_pos = text.rindex("post_agent_adg_burndown_inline_audit.py")
        assert mcp_pos < long_pos < burndown_pos

    def test_author_gate_scripts_retired_from_direct_chain(self) -> None:
        text = (REPO_ROOT / ".codex" / "hooks" / "after_agent_governance_dispatch.py").read_text(encoding="utf-8")
        assert "post_agent_author_gate_capture.py" not in text
        assert "post_agent_ag_queue_seed_capture.py" not in text
