"""Behavioral tests for strict direct and deferred MCP proof capture."""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.adg.mcp import supervisor  # noqa: E402

SCRIPT_PATH = REPO_ROOT / ".codex" / "governance" / "scripts" / "post_adg_mcp_callable_proof.py"
SPEC = importlib.util.spec_from_file_location("post_adg_mcp_callable_proof", SCRIPT_PATH)
assert SPEC and SPEC.loader
cap = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = cap
SPEC.loader.exec_module(cap)
import mcp_callability_epoch as epoch  # noqa: E402


def _configure(tmp_path: Path) -> None:
    (tmp_path / ".mcp.json").write_text(
        json.dumps(
            {
                "mcpServers": {
                    "adg_sqlite": {"url": "http://127.0.0.1:8765/mcp"},
                    "memory": {"url": "http://127.0.0.1:8766/mcp"},
                }
            }
        ),
        encoding="utf-8",
    )


def _write_http_state(tmp_path: Path, server: str, endpoint: str, pid: int) -> None:
    filename = "adg_sqlite_http_launcher.json" if server == "adg_sqlite" else "memory_http_launcher.json"
    path = tmp_path / "artifacts" / "mcp_heartbeat" / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"status": "running", "url": endpoint, "pid": pid}), encoding="utf-8")


def _deferred(
    *,
    now: datetime,
    server: str = "adg_sqlite",
    tool: str = "adg_health",
    endpoint: str = "http://127.0.0.1:8765/mcp",
    result: dict | None = None,
) -> dict:
    receipt = {
        "schema": "codex-deferred-mcp-result/v1",
        "server_id": server,
        "tool_name": tool,
        "endpoint": endpoint,
        "completed_at": now.isoformat(),
        "result": result or {"isError": False, "structuredContent": {"status": "ok"}},
    }
    return {
        "session_id": "session-123",
        "tool_name": "functions.exec",
        "tool_input": {
            "source": (
                f"const result = await tools.mcp__{server}__{tool}({{}}); "
                'text(JSON.stringify({schema:"codex-deferred-mcp-result/v1",'
                f'server_id:"{server}",tool_name:"{tool}",endpoint:"{endpoint}",'
                "completed_at:new Date().toISOString(),result}));"
            )
        },
        "tool_response": {
            "status": "completed",
            "output": [{"type": "input_text", "text": json.dumps(receipt)}],
        },
    }


def test_sanitized_real_fixture_has_distinguishing_schema() -> None:
    fixture = json.loads(
        (
            REPO_ROOT / "tests" / "fixtures" / "codex_post_tool_use" / "functions_exec_deferred_adg.json"
        ).read_text(encoding="utf-8")
    )

    assert fixture["tool_name"] == "functions.exec"
    assert "await tools.mcp__adg_sqlite__adg_health" in fixture["tool_input"]["source"]
    output = json.loads(fixture["tool_response"]["output"][0]["text"])
    assert output["schema"] == "codex-deferred-mcp-result/v1"
    assert output["result"]["isError"] is False


def test_records_direct_process_identity_proof(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(cap, "_REPO_ROOT", tmp_path)
    _configure(tmp_path)
    now = datetime.now(UTC)
    epoch.write_restart_epoch(repo_root=tmp_path, session_id="session-123", epoch_id="epoch-1", now=now)
    _write_http_state(tmp_path, "adg_sqlite", "http://127.0.0.1:8765/mcp", os.getpid())
    payload = {
        "session_id": "session-123",
        "tool_name": "mcp__adg_sqlite__adg_process_identity",
        "tool_response": {"isError": False, "structuredContent": {"status": "ok", "pid": os.getpid()}},
    }

    path = cap.maybe_record_proof(payload, now=now)

    assert path == tmp_path / supervisor.DEFAULT_CALLABLE_PROOF_RELATIVE_PATH
    status = epoch.proof_status("adg_sqlite", repo_root=tmp_path, now=now)
    assert status["status"] == "healthy"
    assert status["endpoint"] == "http://127.0.0.1:8765/mcp"


def test_records_genuine_deferred_memory_health(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(cap, "_REPO_ROOT", tmp_path)
    _configure(tmp_path)
    now = datetime.now(UTC)
    epoch.write_restart_epoch(
        repo_root=tmp_path, session_id="session-123", epoch_id="epoch-1", now=now - timedelta(seconds=1)
    )
    payload = _deferred(
        now=now,
        server="memory",
        tool="mem_health_check",
        endpoint="http://127.0.0.1:8766/mcp",
    )

    path = cap.maybe_record_proof(payload, now=now)

    assert path == tmp_path / epoch.DEFAULT_LEDGER_RELATIVE_PATH
    status = epoch.proof_status("memory", repo_root=tmp_path, now=now)
    assert status["status"] == "healthy"
    assert status["tool"] == "mem_health_check"
    assert status["route_kind"] == "http"
    assert status["endpoint"] == "http://127.0.0.1:8766/mcp"


def test_rejects_shell_output_and_fabricated_mcp_text(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(cap, "_REPO_ROOT", tmp_path)
    _configure(tmp_path)
    payload = {
        "tool_name": "functions.exec_command",
        "tool_input": {"cmd": "Write-Output mcp__adg_sqlite__adg_health"},
        "tool_response": {"stdout": '{"status":"ok"}', "exit_code": 0},
    }

    decision = cap.classify_event(payload)

    assert not decision.accepted
    assert decision.reason == "outer_tool_not_mcp"


def test_rejects_direct_http_probe(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(cap, "_REPO_ROOT", tmp_path)
    _configure(tmp_path)
    payload = {
        "tool_name": "functions.exec",
        "tool_input": {"source": 'await tools.exec_command({cmd:"python probe_mcp_http_server.py"})'},
        "tool_response": {"output": [{"text": '{"status":"ok"}'}]},
    }

    assert cap.classify_event(payload).reason == "deferred_source_call_count"


def test_rejects_missing_response_and_transport_failure(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(cap, "_REPO_ROOT", tmp_path)
    _configure(tmp_path)
    missing = {"tool_name": "mcp__memory__mem_health_check"}
    failed = {
        "tool_name": "mcp__memory__mem_health_check",
        "tool_response": {"isError": True, "structuredContent": {"status": "error"}},
    }

    assert cap.classify_event(missing).reason == "structured_success_missing"
    assert cap.classify_event(failed).reason == "structured_success_missing"


def test_rejects_direct_success_from_non_http_process(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(cap, "_REPO_ROOT", tmp_path)
    _configure(tmp_path)
    _write_http_state(tmp_path, "memory", "http://127.0.0.1:8766/mcp", os.getpid() + 1)
    payload = {
        "tool_name": "mcp__memory__mem_process_identity",
        "tool_response": {"isError": False, "structuredContent": {"status": "ok", "pid": os.getpid()}},
    }

    assert cap.classify_event(payload).reason == "direct_http_process_mismatch"


def test_rejects_endpoint_mismatch_unconfigured_tool_and_stale_receipt(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(cap, "_REPO_ROOT", tmp_path)
    _configure(tmp_path)
    now = datetime.now(UTC)
    epoch.write_restart_epoch(
        repo_root=tmp_path, session_id="session-123", epoch_id="epoch-1", now=now - timedelta(seconds=2)
    )

    assert (
        cap.classify_event(_deferred(now=now, endpoint="http://127.0.0.1:9999/mcp"), now=now).reason
        == "endpoint_mismatch"
    )
    assert (
        cap.classify_event(_deferred(now=now, tool="adg_node"), now=now).reason == "tool_not_proof_authorized"
    )
    assert (
        cap.classify_event(_deferred(now=now - timedelta(minutes=10)), now=now).reason
        == "stale_deferred_receipt"
    )


def test_rejects_receipt_identity_mismatch(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(cap, "_REPO_ROOT", tmp_path)
    _configure(tmp_path)
    now = datetime.now(UTC)
    payload = _deferred(now=now)
    receipt = json.loads(payload["tool_response"]["output"][0]["text"])
    receipt["tool_name"] = "adg_runtime_info"
    payload["tool_response"]["output"][0]["text"] = json.dumps(receipt)

    assert cap.classify_event(payload, now=now).reason == "deferred_identity_mismatch"


def test_does_not_record_without_current_epoch(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(cap, "_REPO_ROOT", tmp_path)
    _configure(tmp_path)
    payload = {
        "tool_name": "mcp__memory__mem_health_check",
        "tool_response": {"isError": False, "structuredContent": {"status": "ok"}},
    }

    assert cap.maybe_record_proof(payload) is None
    assert not (tmp_path / epoch.DEFAULT_LEDGER_RELATIVE_PATH).exists()
