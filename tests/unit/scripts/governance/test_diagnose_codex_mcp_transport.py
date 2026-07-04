"""Tests for scripts/governance/diagnose_codex_mcp_transport.py."""

from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "governance"))

import diagnose_codex_mcp_transport as mod  # noqa: E402


def _write_registry(root: Path, *server_ids: str) -> None:
    (root / ".mcp.json").write_text(
        json.dumps({"mcpServers": {server_id: {} for server_id in server_ids}}),
        encoding="utf-8",
    )


def _report(
    routes: dict[str, dict],
    processes: dict[str, dict] | None = None,
    *,
    available: bool = True,
) -> dict:
    return {
        "route_contract_path": "docs/reports/codex/codex_mcp_live_route_contract.json",
        "route_evidence": {
            "available": available,
            "counts": {},
            "servers": routes,
            "reason": "" if available else "no route contract found",
        },
        "processes": {"servers": processes or {}},
    }


def _route(classification: str, **overrides: object) -> dict:
    route = {
        "classification": classification,
        "callable_status": "absent",
        "fallback_message_key": None,
        "selected_codex_route": "raw_mcp_callable",
        "callability_proof": {"status": "absent"},
    }
    route.update(overrides)
    return route


def test_closed_transport_maps_to_server_healthy_transport_closed(tmp_path: Path) -> None:
    _write_registry(tmp_path, "adg_sqlite")
    report = _report(
        {
            "adg_sqlite": _route(
                "EXPOSED_BLOCKED",
                callable_status="closed_transport",
                fallback_message_key="closed_transport",
            )
        },
        {"adg_sqlite": {"classification": "single", "process_count": 1}},
    )

    diagnosis = mod.build_diagnosis(
        "adg_sqlite",
        report=report,
        root=tmp_path,
        adg_transport_checker=lambda **kwargs: {"status": "closed_transport", "open": False},
    )

    assert diagnosis["classification"] == "server_healthy_codex_transport_closed"
    assert diagnosis["shell_reopen_supported"] is False
    assert "Host/TUI MCP reconnect" in diagnosis["recommended_action"]
    assert diagnosis["degraded_fallback_available"] is False


def test_process_only_maps_to_callability_unproven(tmp_path: Path) -> None:
    _write_registry(tmp_path, "memory")
    report = _report(
        {"memory": _route("PROCESS_ONLY")},
        {"memory": {"classification": "single", "process_count": 1}},
    )

    diagnosis = mod.build_diagnosis("memory", report=report, root=tmp_path)

    assert diagnosis["classification"] == "process_only_callability_unproven"
    assert diagnosis["safe_to_cleanup_processes"] is False
    assert "Process presence is not callability proof" in diagnosis["recommended_action"]


def test_duplicate_process_without_attached_pid_requires_pid_proof(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.delenv("CODEX_MCP_ATTACHED_MEMORY_PID", raising=False)
    _write_registry(tmp_path, "memory")
    report = _report(
        {"memory": _route("PROCESS_ONLY")},
        {"memory": {"classification": "duplicate", "process_count": 2}},
    )

    diagnosis = mod.build_diagnosis("memory", report=report, root=tmp_path)

    assert diagnosis["classification"] == "duplicate_cohort"
    assert diagnosis["safe_to_cleanup_processes"] == "requires_attached_pid"
    assert diagnosis["evidence"]["cleanup"]["cleanup_blocker"] == "attached_pid_required"
    assert "Do not kill" in diagnosis["recommended_action"]


def test_callable_route_maps_to_no_recovery_needed(tmp_path: Path) -> None:
    _write_registry(tmp_path, "memory")
    report = _report(
        {"memory": _route("CALLABLE", callable_status="healthy")},
        {"memory": {"classification": "single", "process_count": 1}},
    )

    diagnosis = mod.build_diagnosis("memory", report=report, root=tmp_path)

    assert diagnosis["classification"] == "callable"
    assert diagnosis["codex_restart_required"] is False
    assert diagnosis["recommended_action"] == "No recovery needed; active Codex MCP callability proof is present."


def test_degraded_fallback_remains_degraded_not_callable(tmp_path: Path) -> None:
    _write_registry(tmp_path, "deepwiki")
    report = _report(
        {"deepwiki": _route("DEGRADED_FALLBACK", selected_codex_route="degraded_fallback")},
        {"deepwiki": {"classification": "none", "process_count": 0}},
    )

    diagnosis = mod.build_diagnosis("deepwiki", report=report, root=tmp_path)

    assert diagnosis["classification"] == "degraded_fallback_available"
    assert diagnosis["degraded_fallback_available"] is True
    assert diagnosis["codex_restart_required"] is False
    assert "do not count it as green readiness" in diagnosis["recommended_action"]


def test_missing_route_contract_is_explicit(tmp_path: Path) -> None:
    _write_registry(tmp_path, "adg_sqlite")
    report = _report({}, available=False)

    diagnosis = mod.build_diagnosis(
        "adg_sqlite",
        report=report,
        root=tmp_path,
        adg_transport_checker=lambda **kwargs: {"status": "callability_unproven", "open": False},
    )

    assert diagnosis["classification"] == "no_route_contract"
    assert diagnosis["evidence"]["route_evidence_available"] is False
    assert "No route contract evidence" in diagnosis["recommended_action"]
