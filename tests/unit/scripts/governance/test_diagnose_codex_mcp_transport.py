"""Tests for scripts/governance/diagnose_codex_mcp_transport.py."""

from __future__ import annotations

from datetime import UTC, datetime
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "governance"))

import diagnose_codex_mcp_transport as mod  # noqa: E402
import record_codex_mcp_recovery_receipt as receipt_mod  # noqa: E402


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


def test_closed_transport_maps_to_legacy_stdio_closed(tmp_path: Path) -> None:
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

    assert diagnosis["classification"] == "legacy_stdio_closed"
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


def test_all_required_aggregate_summary_counts_core_route_classes(tmp_path: Path) -> None:
    _write_registry(tmp_path, "memory", "GitKraken", "adg_sqlite", "vector_db")
    report = _report(
        {
            "memory": _route("CALLABLE", callable_status="healthy"),
            "GitKraken": _route("PROCESS_ONLY"),
            "adg_sqlite": _route(
                "EXPOSED_BLOCKED",
                callable_status="closed_transport",
                fallback_message_key="closed_transport",
            ),
            "vector_db": _route("PROCESS_ONLY"),
        },
        {
            "memory": {"classification": "single", "process_count": 1},
            "GitKraken": {"classification": "single", "process_count": 1},
            "adg_sqlite": {"classification": "single", "process_count": 1},
            "vector_db": {"classification": "duplicate", "process_count": 2},
        },
    )

    aggregate = mod.build_aggregate_diagnosis(
        list(mod.REQUIRED_CORE_SERVERS),
        mode="all_required",
        report=report,
        root=tmp_path,
        summary=True,
        adg_transport_checker=lambda **kwargs: {"status": "closed_transport", "open": False},
    )

    assert aggregate["schema_version"] == mod.AGGREGATE_SCHEMA_VERSION
    assert aggregate["counts"]["required_route_count"] == 4
    assert aggregate["counts"]["callable_count"] == 1
    assert aggregate["counts"]["blocked_count"] == 3
    assert aggregate["counts"]["process_only_count"] == 1
    assert aggregate["counts"]["duplicate_cohort_count"] == 1
    assert aggregate["counts"]["stale_proof_count"] == 0
    assert aggregate["servers"]["adg_sqlite"]["classification"] == "legacy_stdio_closed"
    assert aggregate["servers"]["GitKraken"]["classification"] == "process_only_callability_unproven"
    assert aggregate["servers"]["vector_db"]["classification"] == "duplicate_cohort"
    assert "recommended_action" in aggregate["servers"]["memory"]


def test_stale_historical_route_proof_is_separate_from_process_only(tmp_path: Path) -> None:
    _write_registry(tmp_path, "memory")
    report = _report(
        {"memory": _route("PROCESS_ONLY", callability_proof={"status": "stale_epoch"})},
        {"memory": {"classification": "single", "process_count": 1}},
    )

    aggregate = mod.build_aggregate_diagnosis(
        ["memory"],
        mode="all_required",
        report=report,
        root=tmp_path,
        summary=True,
    )

    assert aggregate["servers"]["memory"]["classification"] == "stale_callability_proof"
    assert aggregate["counts"]["stale_proof_count"] == 1
    assert aggregate["counts"]["process_only_count"] == 0


def test_http_unproven_route_keeps_reload_and_tool_proof_action(tmp_path: Path) -> None:
    _write_registry(tmp_path, "memory")
    report = _report(
        {
            "memory": _route(
                "codex_http_route_unproven",
                route_kind="http",
                configured_url="http://127.0.0.1:8766/mcp",
            )
        },
        {"memory": {"classification": "single", "process_count": 1}},
    )

    diagnosis = mod.build_diagnosis("memory", report=report, root=tmp_path)

    assert diagnosis["classification"] == "codex_http_route_unproven"
    assert diagnosis["codex_restart_required"] is True
    assert "fresh active-session tool-call proof" in diagnosis["recommended_action"]


def test_http_service_down_is_not_treated_as_stdio_closed(tmp_path: Path) -> None:
    _write_registry(tmp_path, "memory")
    report = _report(
        {"memory": _route("http_service_down", route_kind="http")},
        {"memory": {"classification": "none", "process_count": 0}},
    )

    diagnosis = mod.build_diagnosis("memory", report=report, root=tmp_path)

    assert diagnosis["classification"] == "http_service_down"
    assert diagnosis["codex_restart_required"] is False
    assert "Start or restart" in diagnosis["recommended_action"]


def test_http_callable_route_counts_as_callable(tmp_path: Path) -> None:
    _write_registry(tmp_path, "memory")
    report = _report(
        {
            "memory": _route(
                "codex_http_route_callable",
                callable_status="healthy",
                callability_proof={"status": "healthy"},
            )
        },
        {"memory": {"classification": "single", "process_count": 1}},
    )

    diagnosis = mod.build_diagnosis("memory", report=report, root=tmp_path)

    assert diagnosis["classification"] == "codex_http_route_callable"
    assert diagnosis["codex_restart_required"] is False
    assert "No recovery needed" in diagnosis["recommended_action"]


def _diagnosis(
    classification: str,
    *,
    epoch_id: str | None = None,
    proof_status: str = "absent",
) -> dict:
    return {
        "classification": classification,
        "evidence": {
            "callability_epoch": {
                "epoch_id": epoch_id,
                "status": proof_status,
            },
            "route_state": {
                "callability_proof": {
                    "status": proof_status,
                }
            },
        },
    }


def test_recovery_receipt_passes_only_with_fresh_active_tool_proof(tmp_path: Path) -> None:
    receipt = receipt_mod.build_recovery_receipt(
        server_id="memory",
        before_diagnosis=_diagnosis("server_healthy_codex_transport_closed", epoch_id="before", proof_status="absent"),
        after_diagnosis=_diagnosis("callable", epoch_id="after", proof_status="healthy"),
        operator_action="host_tui_reconnect",
        codex_restart_used=False,
        host_tui_reconnect_used=True,
        generated_at=datetime(2026, 7, 5, 12, 0, tzinfo=UTC),
    )
    path = receipt_mod.write_recovery_receipt(receipt, tmp_path)

    assert receipt["schema_version"] == receipt_mod.SCHEMA_VERSION
    assert receipt["before_epoch_id"] == "before"
    assert receipt["after_epoch_id"] == "after"
    assert receipt["after_proof_status"] == "healthy"
    assert receipt["active_tool_proof_required"] is True
    assert receipt["unsafe_process_kill_used"] is False
    assert receipt["script_performed_recovery"] is False
    assert receipt["recovery_status"] == "PASS"
    assert json.loads(path.read_text(encoding="utf-8"))["validation"]["status"] == "PASS"


def test_recovery_receipt_rejects_process_only_after_state() -> None:
    receipt = receipt_mod.build_recovery_receipt(
        server_id="memory",
        before_diagnosis=_diagnosis("server_healthy_codex_transport_closed", epoch_id="before", proof_status="absent"),
        after_diagnosis=_diagnosis("process_only_callability_unproven", epoch_id="after", proof_status="absent"),
        operator_action="host_tui_reconnect",
        codex_restart_used=False,
        host_tui_reconnect_used=True,
        generated_at=datetime(2026, 7, 5, 12, 0, tzinfo=UTC),
    )

    assert receipt["recovery_status"] == "FAIL_CLOSED"
    assert receipt["validation"]["reason"] == "process_only_proof_rejected"
    assert receipt["after_proof_status"] == "absent"


def test_recovery_receipt_passes_http_callable_after_state() -> None:
    receipt = receipt_mod.build_recovery_receipt(
        server_id="memory",
        before_diagnosis=_diagnosis("codex_http_route_unproven", epoch_id="before", proof_status="absent"),
        after_diagnosis=_diagnosis("codex_http_route_callable", epoch_id="after", proof_status="healthy"),
        operator_action="codex_mcp_client_reload",
        codex_restart_used=True,
        host_tui_reconnect_used=False,
        generated_at=datetime(2026, 7, 5, 12, 0, tzinfo=UTC),
    )

    assert receipt["recovery_status"] == "PASS"
    assert receipt["after_classification"] == "codex_http_route_callable"
    assert receipt["validation"]["reason"] == "fresh_active_tool_proof_present"


def test_recovery_receipt_rejects_callable_without_fresh_proof() -> None:
    receipt = receipt_mod.build_recovery_receipt(
        server_id="adg_sqlite",
        before_diagnosis=_diagnosis("server_healthy_codex_transport_closed", epoch_id="before", proof_status="stale_epoch"),
        after_diagnosis=_diagnosis("callable", epoch_id="after", proof_status="stale_epoch"),
        operator_action="codex_restart",
        codex_restart_used=True,
        host_tui_reconnect_used=False,
        generated_at=datetime(2026, 7, 5, 12, 0, tzinfo=UTC),
    )

    assert receipt["recovery_status"] == "FAIL_CLOSED"
    assert receipt["validation"]["reason"] == "active_tool_proof_missing"
    assert receipt["before_proof_status"] == "stale_epoch"
