"""Tests for post_adg_mcp_callable_proof PostToolUse capture."""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.adg.mcp import supervisor  # noqa: E402

_SCRIPT_PATH = REPO_ROOT / ".codex" / "governance" / "scripts" / "post_adg_mcp_callable_proof.py"
_spec = importlib.util.spec_from_file_location("post_adg_mcp_callable_proof", _SCRIPT_PATH)
assert _spec and _spec.loader
cap = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cap)


def test_records_process_identity_proof(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(cap, "_REPO_ROOT", tmp_path)
    payload = {
        "session_id": "session-123",
        "tool_name": "mcp__adg_sqlite.adg_process_identity",
        "tool_response": {"status": "ok", "process": {"pid": os.getpid()}},
    }

    path = cap.maybe_record_proof(payload)

    assert path == tmp_path / supervisor.DEFAULT_CALLABLE_PROOF_RELATIVE_PATH
    proof = json.loads(path.read_text(encoding="utf-8"))
    assert proof["status"] == "healthy"
    assert proof["tool"] == "adg_process_identity"
    assert proof["pid"] == os.getpid()
    assert proof["session_id"] == "session-123"


def test_reads_session_id_from_tool_info(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(cap, "_REPO_ROOT", tmp_path)
    payload = {
        "tool_name": "mcp__adg_sqlite.adg_process_identity",
        "tool_info": {"sessionId": "tool-info-session"},
        "tool_response": {"status": "ok", "process": {"pid": os.getpid()}},
    }

    path = cap.maybe_record_proof(payload)

    assert path is not None
    proof = json.loads(path.read_text(encoding="utf-8"))
    assert proof["session_id"] == "tool-info-session"


def test_skips_transport_closed_response(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(cap, "_REPO_ROOT", tmp_path)
    payload = {
        "session_id": "session-123",
        "tool_name": "mcp__adg_sqlite.adg_process_identity",
        "tool_response": "Tool call error: Transport closed",
    }

    path = cap.maybe_record_proof(payload)

    assert path is None
    assert not (tmp_path / supervisor.DEFAULT_CALLABLE_PROOF_RELATIVE_PATH).exists()


def test_adg_health_can_use_single_authoritative_heartbeat_pid(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(cap, "_REPO_ROOT", tmp_path)
    monkeypatch.setattr(cap, "_pid_from_heartbeat", lambda: os.getpid())
    payload = {
        "session_id": "session-123",
        "tool_name": "mcp__adg_sqlite__adg_health",
        "tool_response": {"status": "ok"},
    }

    path = cap.maybe_record_proof(payload)

    assert path is not None
    proof = json.loads(path.read_text(encoding="utf-8"))
    assert proof["tool"] == "adg_health"
    assert proof["pid"] == os.getpid()


def test_ignores_non_proof_adg_tool(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(cap, "_REPO_ROOT", tmp_path)
    payload = {
        "session_id": "session-123",
        "tool_name": "mcp__adg_sqlite.adg_edge_fanout",
        "tool_response": {"status": "ok", "process": {"pid": os.getpid()}},
    }

    assert cap.maybe_record_proof(payload) is None
