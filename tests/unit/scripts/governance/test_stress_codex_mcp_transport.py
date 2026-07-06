"""Tests for scripts/governance/stress_codex_mcp_transport.py."""

from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "governance"))

import stress_codex_mcp_transport as mod  # noqa: E402


def _write_state(root: Path, server_id: str, pid: int = 123) -> None:
    path = root / "artifacts" / "mcp_heartbeat" / f"{server_id}_http_launcher.json"
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": "codex-http-mcp-launcher-state/v1",
                "server_id": server_id,
                "status": "running",
                "url": "http://127.0.0.1:8766/mcp",
                "pid": pid,
            }
        ),
        encoding="utf-8",
    )


async def _ok_stress(**kwargs):
    count = kwargs["count"]
    return {
        "status": "ok",
        "count": count,
        "passed": count,
        "failed": 0,
        "transport_closed_count": 0,
        "stdout_protocol_corruption_count": 0,
        "errors": [],
    }


async def _failed_stress(**kwargs):
    return {
        "status": "fail",
        "count": kwargs["count"],
        "passed": 0,
        "failed": kwargs["count"],
        "transport_closed_count": 1,
        "errors": [{"index": 0, "error": "Transport closed"}],
    }


def test_build_report_passes_direct_http_stress(monkeypatch, tmp_path: Path) -> None:
    _write_state(tmp_path, "memory")
    monkeypatch.setattr(mod, "_stress_http_calls", _ok_stress)

    report = mod.build_report(
        server_id="memory",
        url="http://127.0.0.1:8766/mcp",
        tool="memory_health",
        count=5,
        timeout_s=1,
        root=tmp_path,
    )

    assert report["status"] == "ok"
    assert report["direct_http"]["passed"] == 5
    assert report["service_pid_stable"] is True
    assert report["restarts_observed"] == 0


def test_build_report_requires_active_endpoint_matched_proof(monkeypatch, tmp_path: Path) -> None:
    _write_state(tmp_path, "memory")
    monkeypatch.setattr(mod, "_stress_http_calls", _ok_stress)
    mod.mcp_callability_epoch.write_restart_epoch(repo_root=tmp_path, session_id="s1", epoch_id="epoch-1")
    mod.mcp_callability_epoch.write_callability_proof(
        server_id="memory",
        tool="memory_health",
        evidence='{"status":"ok"}',
        repo_root=tmp_path,
        route_kind="http",
        endpoint="http://127.0.0.1:8766/mcp",
    )

    report = mod.build_report(
        server_id="memory",
        url="http://127.0.0.1:8766/mcp",
        tool="memory_health",
        count=5,
        timeout_s=1,
        require_active_proof=True,
        root=tmp_path,
    )

    assert report["status"] == "ok"
    assert report["active_session_proof"]["status"] == "ok"


def test_build_report_fails_when_active_proof_endpoint_is_wrong(monkeypatch, tmp_path: Path) -> None:
    _write_state(tmp_path, "memory")
    monkeypatch.setattr(mod, "_stress_http_calls", _ok_stress)
    mod.mcp_callability_epoch.write_restart_epoch(repo_root=tmp_path, session_id="s1", epoch_id="epoch-1")
    mod.mcp_callability_epoch.write_callability_proof(
        server_id="memory",
        tool="memory_health",
        evidence='{"status":"ok"}',
        repo_root=tmp_path,
        route_kind="http",
        endpoint="http://127.0.0.1:9999/mcp",
    )

    report = mod.build_report(
        server_id="memory",
        url="http://127.0.0.1:8766/mcp",
        tool="memory_health",
        count=5,
        timeout_s=1,
        require_active_proof=True,
        root=tmp_path,
    )

    assert report["status"] == "fail"
    assert report["active_session_proof"]["http_callability_acceptance"]["accepted"] is False


def test_write_report_creates_parent_directory(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(mod, "_stress_http_calls", _failed_stress)
    report = mod.build_report(
        server_id="memory",
        url="http://127.0.0.1:8766/mcp",
        tool="memory_health",
        count=3,
        timeout_s=1,
        root=tmp_path,
    )
    path = mod.write_report(report, tmp_path / "reports" / "stress.json")

    assert path.exists()
    assert json.loads(path.read_text(encoding="utf-8"))["status"] == "fail"
