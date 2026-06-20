"""Tests for the unified post-turn governance dispatch Stop hook.

W1 (claude-enforcement-runtime-truth-hardening). The hook is a live Stop hook under
.claude/hooks/. It imports lib.claude_hook_common (so .claude/hooks must be on sys.path).

The central regression these tests pin: the live Claude ``Stop`` payload carries NO
inline ``response`` — only a ``transcript_path``. The previous implementation guarded on
``payload.get("response")`` and therefore silently no-opped the ENTIRE governance chain
on every real Stop event. These tests prove (a) transcript recovery now works, (b) the
chain actually runs on a real Stop payload, and (c) when no response is recoverable the
hook emits a *visible* fail-open receipt instead of a silent no-op.

The real governance sub-scripts are stubbed (monkeypatched) so the unit test is fast and
free of side effects; we assert on which scripts the dispatcher *attempted*, via the
per-Stop dispatch receipt.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from io import StringIO
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
HOOKS_DIR = REPO_ROOT / ".claude" / "hooks"
HOOK = HOOKS_DIR / "after_agent_governance_dispatch.py"


@pytest.fixture()
def hook(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.syspath_prepend(str(HOOKS_DIR))
    name = "_after_agent_governance_dispatch_test"
    spec = importlib.util.spec_from_file_location(name, HOOK)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    # Redirect the receipt to a temp file so we never touch the real artifacts dir.
    monkeypatch.setattr(mod, "_DISPATCH_RECEIPT", tmp_path / "post_turn_dispatch_receipts.jsonl")
    # Stub the whole subprocess chain — default every member to "ok", record calls.
    calls: list[str] = []

    def _fake_run_script(name: str, raw: str, env: dict) -> str:
        calls.append(name)
        return mod._TEST_STATUS.get(name, "ok")  # type: ignore[attr-defined]

    def _fake_dispatch(raw: str) -> str:
        calls.append("post_agent_dispatch.py")
        return mod._TEST_STATUS.get("post_agent_dispatch.py", "ok")  # type: ignore[attr-defined]

    def _fake_cleanup() -> str:
        calls.append("worktree_cleanup")
        return mod._TEST_CLEANUP_STATUS  # type: ignore[attr-defined]

    mod._TEST_STATUS = {}  # type: ignore[attr-defined]
    mod._TEST_CLEANUP_STATUS = "ok"  # type: ignore[attr-defined]
    mod._TEST_CALLS = calls  # type: ignore[attr-defined]
    monkeypatch.setattr(mod, "_run_script", _fake_run_script)
    monkeypatch.setattr(mod, "_run_dispatch", _fake_dispatch)
    monkeypatch.setattr(mod, "_run_worktree_cleanup", _fake_cleanup)
    return mod


def _run(mod, payload, monkeypatch: pytest.MonkeyPatch) -> int:
    raw = payload if isinstance(payload, str) else json.dumps(payload)
    monkeypatch.setattr(sys, "stdin", StringIO(raw))
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
    return mod.main()


def _receipts(mod) -> list[dict]:
    path = mod._DISPATCH_RECEIPT
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_transcript(tmp_path: Path, *assistant_texts: str) -> Path:
    """Write a realistic Claude transcript JSONL; each text becomes one assistant turn."""
    lines = [json.dumps({"type": "user", "message": {"role": "user", "content": "do the thing"}})]
    for text in assistant_texts:
        lines.append(
            json.dumps(
                {
                    "type": "assistant",
                    "message": {
                        "role": "assistant",
                        "content": [
                            {"type": "text", "text": text},
                            {"type": "tool_use", "name": "Read", "input": {}},
                        ],
                    },
                }
            )
        )
    path = tmp_path / "transcript.jsonl"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


# --------------------------------------------------------------------------- #
# The no-op regression — real Stop payload (transcript_path, no inline response)
# --------------------------------------------------------------------------- #

class TestRealStopPayload:
    def test_real_stop_payload_runs_chain(self, hook, monkeypatch, tmp_path) -> None:
        transcript = _write_transcript(tmp_path, "first turn", "STATUS: PASS final turn")
        payload = {
            "session_id": "s1",
            "transcript_path": str(transcript),
            "hook_event_name": "Stop",
            "stop_hook_active": False,
        }
        rc = _run(hook, payload, monkeypatch)
        assert rc == 0
        # The chain actually ran (the bug was: it never did on real Stop payloads).
        assert hook._TEST_CALLS, "governance chain did not run on a real Stop payload"
        assert "post_agent_adg_audit.py" in hook._TEST_CALLS
        assert "post_agent_dispatch.py" in hook._TEST_CALLS
        rows = _receipts(hook)
        assert len(rows) == 1
        assert rows[0]["response_present"] is True
        assert rows[0]["dispatch_result"] == "dispatched"
        assert hook._TEST_CALLS[-1] == "worktree_cleanup"

    def test_old_guard_would_have_no_opped(self, hook, monkeypatch, tmp_path) -> None:
        # Documents the bug: the real Stop payload has NO "response" key, which the old
        # `payload.get("response")` guard treated as empty -> silent no-op.
        transcript = _write_transcript(tmp_path, "final text")
        payload = {"session_id": "s1", "transcript_path": str(transcript)}
        assert payload.get("response") is None  # the old guard's input
        # But the new resolver recovers it from the transcript.
        assert hook.resolve_response_text(payload) == "final text"


# --------------------------------------------------------------------------- #
# Transcript recovery unit behavior
# --------------------------------------------------------------------------- #

class TestTranscriptRecovery:
    def test_recovers_last_assistant_message(self, hook, tmp_path) -> None:
        transcript = _write_transcript(tmp_path, "early", "middle", "the last one")
        assert hook.recover_response_from_transcript(str(transcript)) == "the last one"

    def test_skips_malformed_lines(self, hook, tmp_path) -> None:
        path = tmp_path / "t.jsonl"
        path.write_text(
            "not json at all\n"
            + json.dumps({"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": "good"}]}})
            + "\n{ broken\n",
            encoding="utf-8",
        )
        assert hook.recover_response_from_transcript(str(path)) == "good"

    def test_missing_file_returns_empty(self, hook, tmp_path) -> None:
        assert hook.recover_response_from_transcript(str(tmp_path / "nope.jsonl")) == ""

    def test_empty_path_returns_empty(self, hook) -> None:
        assert hook.recover_response_from_transcript("") == ""

    def test_string_content_form(self, hook, tmp_path) -> None:
        path = tmp_path / "t.jsonl"
        path.write_text(
            json.dumps({"type": "assistant", "message": {"role": "assistant", "content": "plain string body"}}) + "\n",
            encoding="utf-8",
        )
        assert hook.recover_response_from_transcript(str(path)) == "plain string body"


# --------------------------------------------------------------------------- #
# Resolver precedence + degraded payloads
# --------------------------------------------------------------------------- #

class TestResolveResponse:
    def test_inline_response_beats_transcript(self, hook, tmp_path) -> None:
        transcript = _write_transcript(tmp_path, "from transcript")
        payload = {"response": "inline wins", "transcript_path": str(transcript)}
        assert hook.resolve_response_text(payload) == "inline wins"

    def test_inline_response_runs_chain(self, hook, monkeypatch) -> None:
        rc = _run(hook, {"session_id": "s2", "response": "STATUS: PASS inline"}, monkeypatch)
        assert rc == 0
        assert hook._TEST_CALLS
        assert _receipts(hook)[0]["response_present"] is True


class TestDegradedPayloads:
    def test_empty_payload_writes_unavailable_receipt_no_chain(self, hook, monkeypatch) -> None:
        rc = _run(hook, "", monkeypatch)
        assert rc == 0
        assert hook._TEST_CALLS == ["worktree_cleanup"]  # chain must NOT run; cleanup still does
        rows = _receipts(hook)
        assert len(rows) == 1
        assert rows[0]["response_present"] is False
        assert rows[0]["dispatch_result"] == "response_unavailable"

    def test_malformed_json_payload_no_crash(self, hook, monkeypatch) -> None:
        rc = _run(hook, "this is not json {", monkeypatch)
        assert rc == 0
        assert hook._TEST_CALLS == ["worktree_cleanup"]
        assert _receipts(hook)[0]["dispatch_result"] == "response_unavailable"

    def test_transcript_path_missing_file_is_unavailable(self, hook, monkeypatch, tmp_path) -> None:
        rc = _run(hook, {"session_id": "s3", "transcript_path": str(tmp_path / "absent.jsonl")}, monkeypatch)
        assert rc == 0
        assert hook._TEST_CALLS == ["worktree_cleanup"]
        assert _receipts(hook)[0]["dispatch_result"] == "response_unavailable"


# --------------------------------------------------------------------------- #
# Receipt accounting for chain sub-script outcomes
# --------------------------------------------------------------------------- #

class TestReceiptAccounting:
    def test_records_missing_timeout_error(self, hook, monkeypatch) -> None:
        hook._TEST_STATUS = {
            "post_agent_long_command_audit.py": "missing",
            "post_agent_runtime_rca_audit.py": "timeout",
            "post_agent_dispatch.py": "error",
        }
        rc = _run(hook, {"session_id": "s4", "response": "STATUS: PARTIAL body"}, monkeypatch)
        assert rc == 0
        row = _receipts(hook)[0]
        assert "post_agent_long_command_audit.py" in row["scripts_missing"]
        assert "post_agent_runtime_rca_audit.py" in row["scripts_timed_out"]
        assert "post_agent_dispatch.py" in row["scripts_failed_open"]
        # A missing script is not "attempted"; a timeout/error is.
        assert "post_agent_long_command_audit.py" not in row["scripts_attempted"]
        assert "post_agent_runtime_rca_audit.py" in row["scripts_attempted"]


# --------------------------------------------------------------------------- #
# Chain membership + wiring guards
# --------------------------------------------------------------------------- #

class TestChainMembershipAndWiring:
    def test_ag_chain_unchanged(self, hook) -> None:
        # Guards against accidental silent removal of a governance audit from the chain.
        assert hook._AG_CHAIN == (
            "post_agent_mcp_hygiene_audit.py",
            "post_agent_long_command_audit.py",
            "post_agent_adg_burndown_inline_audit.py",
            "post_agent_work_classification_audit.py",
            "post_agent_runtime_rca_audit.py",
            "post_agent_recommendation_gate_audit.py",
        )

    def test_hook_registered_in_settings_stop(self) -> None:
        settings = json.loads((REPO_ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
        cmds = [h["command"] for group in settings["hooks"]["Stop"] for h in group["hooks"]]
        assert any("after_agent_governance_dispatch.py" in c for c in cmds), cmds
