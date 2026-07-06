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
import mcp_callability_epoch as epoch  # noqa: E402


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


def test_skips_error_payload_without_inline_response(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(cap, "_REPO_ROOT", tmp_path)
    epoch.write_restart_epoch(repo_root=tmp_path, session_id="session-123", epoch_id="epoch-1")
    payload = {
        "session_id": "session-123",
        "tool_name": "mcp__memory.memory_health",
        "error": "Transport closed",
    }

    path = cap.maybe_record_proof(payload)

    assert path is None
    assert epoch.proof_status("memory", repo_root=tmp_path)["status"] == "absent"


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


def test_adg_health_completion_without_inline_response_records_supervisor_proof(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(cap, "_REPO_ROOT", tmp_path)
    monkeypatch.setattr(cap, "_pid_from_heartbeat", lambda: os.getpid())
    payload = {
        "session_id": "session-123",
        "tool_name": "mcp__adg_sqlite.adg_health",
    }

    path = cap.maybe_record_proof(payload)

    assert path == tmp_path / supervisor.DEFAULT_CALLABLE_PROOF_RELATIVE_PATH
    proof = json.loads(path.read_text(encoding="utf-8"))
    assert proof["tool"] == "adg_health"
    assert proof["pid"] == os.getpid()
    assert "PostToolUse completed" in proof["evidence"]


def test_ignores_non_proof_adg_tool(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(cap, "_REPO_ROOT", tmp_path)
    payload = {
        "session_id": "session-123",
        "tool_name": "mcp__adg_sqlite.adg_edge_fanout",
        "tool_response": {"status": "ok", "process": {"pid": os.getpid()}},
    }

    assert cap.maybe_record_proof(payload) is None


def test_records_memory_health_in_current_epoch_ledger(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(cap, "_REPO_ROOT", tmp_path)
    (tmp_path / ".mcp.json").write_text(
        json.dumps({"mcpServers": {"memory": {"url": "http://127.0.0.1:8766/mcp"}}}),
        encoding="utf-8",
    )
    epoch.write_restart_epoch(repo_root=tmp_path, session_id="session-123", epoch_id="epoch-1")
    payload = {
        "session_id": "session-123",
        "tool_name": "mcp__memory.memory_health",
        "tool_response": {"status": "ok", "process": {"pid": os.getpid()}},
    }

    path = cap.maybe_record_proof(payload)

    assert path == tmp_path / epoch.DEFAULT_LEDGER_RELATIVE_PATH
    status = epoch.proof_status("memory", repo_root=tmp_path)
    assert status["status"] == "healthy"
    assert status["tool"] == "memory_health"
    assert status["pid"] == os.getpid()
    assert status["route_kind"] == "http"
    assert status["endpoint"] == "http://127.0.0.1:8766/mcp"


def test_records_vector_health_without_pid_in_current_epoch_ledger(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(cap, "_REPO_ROOT", tmp_path)
    epoch.write_restart_epoch(repo_root=tmp_path, session_id="session-123", epoch_id="epoch-1")
    payload = {
        "session_id": "session-123",
        "tool_name": "mcp__vector_db.health_snapshot",
        "tool_response": {"semantic_ready": True},
    }

    path = cap.maybe_record_proof(payload)

    assert path == tmp_path / epoch.DEFAULT_LEDGER_RELATIVE_PATH
    status = epoch.proof_status("vector_db", repo_root=tmp_path)
    assert status["status"] == "healthy"
    assert status["tool"] == "health_snapshot"


def test_records_memory_completion_without_inline_response_in_current_epoch_ledger(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(cap, "_REPO_ROOT", tmp_path)
    epoch.write_restart_epoch(repo_root=tmp_path, session_id="session-123", epoch_id="epoch-1")
    payload = {
        "session_id": "session-123",
        "tool_name": "mcp__memory.memory_health",
    }

    path = cap.maybe_record_proof(payload)

    assert path == tmp_path / epoch.DEFAULT_LEDGER_RELATIVE_PATH
    status = epoch.proof_status("memory", repo_root=tmp_path)
    assert status["status"] == "healthy"
    assert status["tool"] == "memory_health"


def test_reads_identity_from_nested_tool_object(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(cap, "_REPO_ROOT", tmp_path)
    epoch.write_restart_epoch(repo_root=tmp_path, session_id="session-123", epoch_id="epoch-1")
    payload = {
        "session_id": "session-123",
        "tool": {"server": "vector_db", "name": "health_snapshot"},
        "tool_response": {"semantic_ready": True},
    }

    path = cap.maybe_record_proof(payload)

    assert path == tmp_path / epoch.DEFAULT_LEDGER_RELATIVE_PATH
    status = epoch.proof_status("vector_db", repo_root=tmp_path)
    assert status["status"] == "healthy"
    assert status["tool"] == "health_snapshot"


def test_reads_identity_from_top_level_tool_string(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(cap, "_REPO_ROOT", tmp_path)
    epoch.write_restart_epoch(repo_root=tmp_path, session_id="session-123", epoch_id="epoch-1")
    payload = {
        "session_id": "session-123",
        "tool": "mcp__GitKraken.git_status",
    }

    path = cap.maybe_record_proof(payload)

    assert path == tmp_path / epoch.DEFAULT_LEDGER_RELATIVE_PATH
    status = epoch.proof_status("GitKraken", repo_root=tmp_path)
    assert status["status"] == "healthy"
    assert status["tool"] == "git_status"


def test_does_not_record_generic_route_proof_without_session_epoch(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(cap, "_REPO_ROOT", tmp_path)
    payload = {
        "session_id": "session-123",
        "tool_name": "mcp__memory.memory_health",
        "tool_response": {"status": "ok"},
    }

    assert cap.maybe_record_proof(payload) is None
    assert not (tmp_path / epoch.DEFAULT_LEDGER_RELATIVE_PATH).exists()
