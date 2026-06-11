"""Tests for scripts/governance/audit_codex_mcp_transports.py."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "governance"))

import audit_codex_mcp_transports as mod  # noqa: E402
import cleanup_duplicate_mcp_cohorts as cleanup  # noqa: E402


def _route(server_id: str, selected: str, fallback_key: str = "raw_mcp_unavailable") -> dict:
    return {
        "server_id": server_id,
        "selected_codex_route": selected,
        "fallback_message_key": fallback_key,
        "route_owner": "test owner",
        "w2_decision": "test decision",
    }


def test_closed_transport_overrides_process_presence() -> None:
    route = _route("adg_sqlite", "host_mcp_required", "closed_transport")
    process_state = {"process_count": 1, "classification": "single"}

    assert mod.classify_route(route, process_state, "closed_transport") == "EXPOSED_BLOCKED"


def test_process_only_when_server_runs_but_no_callable_surface() -> None:
    route = _route("memory", "host_mcp_required", "no_substitute")
    process_state = {"process_count": 1, "classification": "single"}

    assert mod.classify_route(route, process_state) == "PROCESS_ONLY"


def test_adg_launcher_marker_matches_current_mcp_command() -> None:
    markers = mod.PROCESS_MARKERS["adg_sqlite"]["markers"]
    normalized = "python -u -m tools.mcp.launch_adg_sqlite_mcp"

    assert any(marker.lower().replace("\\", "/") in normalized for marker in markers)


def test_plugin_substitute_classification_without_process_requirement() -> None:
    route = _route("notion", "plugin_substitute", "plugin_substitute")
    process_state = {"process_count": 0, "classification": "none"}

    assert mod.classify_route(route, process_state) == "PLUGIN_SUBSTITUTE"


def test_degraded_fallback_when_not_process_visible() -> None:
    route = _route("GitKraken", "degraded_fallback")
    process_state = {"process_count": 0, "classification": "none"}

    assert mod.classify_route(route, process_state) == "DEGRADED_FALLBACK"


def test_substitute_callable_classification() -> None:
    route = _route("playwright", "substitute_callable", "plugin_substitute")
    process_state = {"process_count": 0, "classification": "none"}

    assert mod.classify_route(route, process_state) == "SUBSTITUTE_CALLABLE"


def test_build_route_evidence_counts_and_fields(monkeypatch) -> None:
    contract = {
        "plan_id": "codex-claude-mcp-access-parity-c6d4e2",
        "wave": "W2",
        "routes": [
            _route("adg_sqlite", "host_mcp_required", "closed_transport"),
            _route("memory", "host_mcp_required", "no_substitute"),
            _route("notion", "plugin_substitute", "plugin_substitute"),
            _route("GitKraken", "degraded_fallback"),
        ],
    }
    process_servers = {
        "adg_sqlite": {"process_count": 1, "classification": "single"},
        "memory": {"process_count": 1, "classification": "single"},
        "notion": {"process_count": 3, "classification": "single_launch_tree"},
        "GitKraken": {"process_count": 0, "classification": "none"},
    }
    monkeypatch.setenv("CODEX_MCP_CALLABLE_ADG_SQLITE", "closed_transport")

    evidence = mod.build_route_evidence(contract, process_servers)

    assert evidence["available"] is True
    assert evidence["counts"] == {
        "DEGRADED_FALLBACK": 1,
        "EXPOSED_BLOCKED": 1,
        "PLUGIN_SUBSTITUTE": 1,
        "PROCESS_ONLY": 1,
    }
    assert evidence["servers"]["adg_sqlite"]["classification"] == "EXPOSED_BLOCKED"
    assert evidence["servers"]["memory"]["classification"] == "PROCESS_ONLY"
    assert evidence["servers"]["notion"]["fallback_message_key"] == "plugin_substitute"


def test_build_route_evidence_without_contract_is_explicit() -> None:
    evidence = mod.build_route_evidence(None, {})

    assert evidence == {
        "available": False,
        "reason": "no route contract found",
        "servers": {},
    }


def test_cleanup_selects_older_claude_mcp_cohort_only() -> None:
    records = [
        cleanup.ProcessRecord(10, 1, "claude.exe", ("claude.exe", "--resume", "old"), 100.0),
        cleanup.ProcessRecord(20, 1, "claude.exe", ("claude.exe", "--resume", "new"), 200.0),
        cleanup.ProcessRecord(11, 10, "python.exe", ("python", "-u", "-m", "tools.mcp.launch_adg_sqlite_mcp"), 101.0),
        cleanup.ProcessRecord(12, 10, "python.exe", ("python", "-u", "tools/memory/adg_memory_server.py"), 102.0),
        cleanup.ProcessRecord(21, 20, "python.exe", ("python", "-u", "-m", "tools.mcp.launch_adg_sqlite_mcp"), 201.0),
        cleanup.ProcessRecord(22, 20, "python.exe", ("python", "-u", "tools/memory/adg_memory_server.py"), 202.0),
        cleanup.ProcessRecord(99, 1, "python.exe", ("python", "-u", "tools/memory/adg_memory_server.py"), 300.0),
    ]

    selection = cleanup.select_duplicate_targets(records)

    assert selection["keep_parent_pid"] == 20
    assert selection["duplicate_parent_pids"] == [10]
    assert selection["target_pids"] == [11, 12]


def test_cleanup_does_not_select_through_nested_claude_parent() -> None:
    records = [
        cleanup.ProcessRecord(1, 0, "claude.exe", ("claude.exe", "wrapper"), 300.0),
        cleanup.ProcessRecord(10, 1, "claude.exe", ("claude.exe", "--resume", "agent"), 100.0),
        cleanup.ProcessRecord(11, 10, "python.exe", ("python", "-u", "-m", "tools.mcp.launch_adg_sqlite_mcp"), 101.0),
    ]

    selection = cleanup.select_duplicate_targets(records)

    assert selection["keep_parent_pid"] == 10
    assert selection["duplicate_parent_pids"] == []
    assert selection["target_pids"] == []
