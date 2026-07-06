"""Tests for scripts/governance/audit_codex_mcp_transports.py."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "governance"))

import audit_codex_mcp_transports as mod  # noqa: E402
import cleanup_duplicate_mcp_cohorts as cleanup  # noqa: E402
import mcp_callability_epoch as epoch  # noqa: E402


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

    assert mod.classify_route(route, process_state, "closed_transport") == "legacy_stdio_closed"


def test_process_only_when_server_runs_but_no_callable_surface() -> None:
    route = _route("memory", "host_mcp_required", "no_substitute")
    process_state = {"process_count": 1, "classification": "single"}

    assert mod.classify_route(route, process_state) == "PROCESS_ONLY"


def test_duplicate_process_only_is_not_callable() -> None:
    route = _route("memory", "host_mcp_required", "no_substitute")
    process_state = {"process_count": 3, "classification": "duplicate"}

    assert mod.classify_route(route, process_state) == "PROCESS_ONLY"


def test_healthy_callable_status_overrides_process_evidence() -> None:
    route = _route("memory", "host_mcp_required", "no_substitute")
    process_state = {"process_count": 3, "classification": "duplicate"}

    assert mod.classify_route(route, process_state, "healthy") == "CALLABLE"


def test_contract_healthy_proof_is_not_trusted_by_default(monkeypatch) -> None:
    monkeypatch.delenv("CODEX_MCP_CALLABLE_MEMORY", raising=False)
    contract = {
        "routes": [
            {
                "server_id": "memory",
                "selected_codex_route": "raw_mcp_callable",
                "callable_status": "healthy",
                "proof": {
                    "tool": "mcp__memory.mem_get_stats",
                    "evidence": '{"total_entities": 1}',
                },
            }
        ]
    }

    evidence = mod.build_route_evidence(contract, {})

    assert evidence["servers"]["memory"]["classification"] == "HOST_MCP_REQUIRED"
    assert evidence["servers"]["memory"]["callable_status"] == "absent"


def test_contract_healthy_proof_can_be_explicitly_trusted(monkeypatch) -> None:
    monkeypatch.delenv("CODEX_MCP_CALLABLE_MEMORY", raising=False)
    contract = {
        "routes": [
            {
                "server_id": "memory",
                "selected_codex_route": "raw_mcp_callable",
                "callable_status": "healthy",
                "proof": {
                    "tool": "mcp__memory.mem_get_stats",
                    "evidence": '{"total_entities": 1}',
                },
            }
        ]
    }

    evidence = mod.build_route_evidence(contract, {}, trust_contract_callable_proof=True)

    assert evidence["servers"]["memory"]["classification"] == "CALLABLE"
    assert evidence["servers"]["memory"]["callable_status"] == "healthy"


def test_current_epoch_file_proof_makes_route_callable(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    monkeypatch.delenv("CODEX_MCP_CALLABLE_MEMORY", raising=False)
    epoch.write_restart_epoch(repo_root=tmp_path, session_id="s1", epoch_id="epoch-1")
    epoch.write_callability_proof(
        server_id="memory",
        tool="memory_health",
        evidence='{"status":"ok"}',
        repo_root=tmp_path,
    )
    contract = {"routes": [_route("memory", "raw_mcp_callable", "")]}

    evidence = mod.build_route_evidence(contract, {})

    assert evidence["servers"]["memory"]["classification"] == "CALLABLE"
    assert evidence["servers"]["memory"]["callable_status"] == "healthy"
    assert evidence["servers"]["memory"]["callability_proof"]["epoch_id"] == "epoch-1"


def test_stale_epoch_file_proof_does_not_make_route_callable(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    monkeypatch.delenv("CODEX_MCP_CALLABLE_MEMORY", raising=False)
    epoch.write_restart_epoch(repo_root=tmp_path, session_id="s1", epoch_id="epoch-1")
    epoch.write_callability_proof(
        server_id="memory",
        tool="memory_health",
        evidence='{"status":"ok"}',
        repo_root=tmp_path,
    )
    epoch.epoch_path(tmp_path).write_text(
        '{"schema_version":"codex-mcp-session-epoch/v1","epoch_id":"epoch-2"}',
        encoding="utf-8",
    )
    contract = {"routes": [_route("memory", "raw_mcp_callable", "")]}

    evidence = mod.build_route_evidence(contract, {})

    assert evidence["servers"]["memory"]["classification"] == "HOST_MCP_REQUIRED"
    assert evidence["servers"]["memory"]["callable_status"] == "absent"
    assert evidence["servers"]["memory"]["callability_proof"]["status"] == "stale_epoch"


def test_raw_mcp_callable_requires_process_presence() -> None:
    route = _route("adg_sqlite", "raw_mcp_callable", "")

    assert mod.classify_route(route, {"process_count": 1, "classification": "single"}) == "PROCESS_ONLY"
    assert mod.classify_route(route, {"process_count": 0, "classification": "none"}) == "HOST_MCP_REQUIRED"


def test_adg_launcher_marker_matches_current_mcp_command() -> None:
    markers = mod.PROCESS_MARKERS["adg_sqlite"]["markers"]
    normalized = "python -u -m tools.mcp.launch_adg_sqlite_mcp"

    assert any(marker.lower().replace("\\", "/") in normalized for marker in markers)


def test_adg_http_launcher_marker_matches_current_mcp_command() -> None:
    markers = mod.PROCESS_MARKERS["adg_sqlite"]["markers"]
    normalized = "python -m tools.mcp.launch_adg_sqlite_http_mcp"

    assert any(marker.lower().replace("\\", "/") in normalized for marker in markers)


def test_gitkraken_marker_registered_for_process_hygiene() -> None:
    config = mod.PROCESS_MARKERS["GitKraken"]
    normalized = "c:/users/amita/appdata/local/gitkrakencli/gk.exe mcp --readonly"

    assert config["expected"] == "single-process-stdio-server"
    assert any(marker.lower().replace("\\", "/") in normalized for marker in config["markers"])


def test_plugin_substitute_classification_without_process_requirement() -> None:
    route = _route("notion", "plugin_substitute", "plugin_substitute")
    process_state = {"process_count": 0, "classification": "none"}

    assert mod.classify_route(route, process_state) == "PLUGIN_SUBSTITUTE"


def test_degraded_fallback_when_not_process_visible() -> None:
    route = _route("GitKraken", "degraded_fallback")
    process_state = {"process_count": 0, "classification": "none"}

    assert mod.classify_route(route, process_state) == "DEGRADED_FALLBACK"


def test_gitkraken_host_required_route_stays_blocked_without_callable_status() -> None:
    contract = {"routes": [_route("GitKraken", "host_mcp_required", "no_substitute")]}
    process_state = {"GitKraken": {"process_count": 0, "classification": "none"}}

    evidence = mod.build_route_evidence(contract, process_state)

    assert evidence["servers"]["GitKraken"]["classification"] == "HOST_MCP_REQUIRED"


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
            _route("GitKraken", "host_mcp_required", "no_substitute"),
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
        "legacy_stdio_closed": 1,
        "PLUGIN_SUBSTITUTE": 1,
        "PROCESS_ONLY": 1,
        "HOST_MCP_REQUIRED": 1,
    }
    assert evidence["servers"]["adg_sqlite"]["classification"] == "legacy_stdio_closed"
    assert evidence["servers"]["memory"]["classification"] == "PROCESS_ONLY"
    assert evidence["servers"]["GitKraken"]["classification"] == "HOST_MCP_REQUIRED"
    assert evidence["servers"]["notion"]["fallback_message_key"] == "plugin_substitute"


def test_legacy_codex_route_shape_is_normalized() -> None:
    contract = {
        "routes": [
            {"server_id": "GitKraken", "codex_route": "host_mcp_required", "status": "blocked_degraded"},
            {"server_id": "memory", "codex_route": "host_mcp_required", "status": "blocked"},
            {"server_id": "adg_sqlite", "codex_route": "raw_mcp", "status": "transport_green_payload_blocked"},
        ]
    }

    evidence = mod.build_route_evidence(contract, {})

    assert evidence["counts"] == {
        "legacy_stdio_closed": 1,
        "HOST_MCP_REQUIRED": 2,
    }
    assert evidence["servers"]["GitKraken"]["classification"] == "HOST_MCP_REQUIRED"
    assert evidence["servers"]["memory"]["classification"] == "HOST_MCP_REQUIRED"
    assert evidence["servers"]["adg_sqlite"]["classification"] == "legacy_stdio_closed"


def test_http_route_running_without_matching_codex_proof_is_unproven(tmp_path: Path) -> None:
    contract = {"routes": [_route("memory", "raw_mcp_callable", "")]}
    evidence = mod.build_route_evidence(
        contract,
        {"memory": {"process_count": 1, "classification": "single"}},
        registry_servers={"memory": {"url": "http://127.0.0.1:8766/mcp"}},
        http_service_states={
            "memory": {
                "available": True,
                "status": "running",
                "url": "http://127.0.0.1:8766/mcp",
                "url_matches_config": True,
            }
        },
        root=tmp_path,
    )

    state = evidence["servers"]["memory"]
    assert state["classification"] == "codex_http_route_unproven"
    assert state["route_kind"] == "http"
    assert state["configured_url"] == "http://127.0.0.1:8766/mcp"


def test_http_route_service_down_is_separate_from_codex_unproven(tmp_path: Path) -> None:
    contract = {"routes": [_route("memory", "raw_mcp_callable", "")]}
    evidence = mod.build_route_evidence(
        contract,
        {},
        registry_servers={"memory": {"url": "http://127.0.0.1:8766/mcp"}},
        http_service_states={"memory": {"available": False, "status": "absent"}},
        root=tmp_path,
    )

    assert evidence["servers"]["memory"]["classification"] == "http_service_down"


def test_external_http_route_without_local_state_is_unproven_not_down(tmp_path: Path) -> None:
    contract = {"routes": [_route("deepwiki", "raw_mcp_callable", "")]}
    evidence = mod.build_route_evidence(
        contract,
        {},
        registry_servers={"deepwiki": {"url": "https://mcp.deepwiki.com/mcp"}},
        http_service_states={"deepwiki": {"available": False, "status": "absent"}},
        root=tmp_path,
    )

    assert evidence["servers"]["deepwiki"]["classification"] == "codex_http_route_unproven"


def test_http_protocol_unhealthy_is_not_codex_callable(tmp_path: Path) -> None:
    contract = {"routes": [_route("memory", "raw_mcp_callable", "")]}
    evidence = mod.build_route_evidence(
        contract,
        {"memory": {"process_count": 1, "classification": "single"}},
        registry_servers={"memory": {"url": "http://127.0.0.1:8766/mcp"}},
        http_service_states={
            "memory": {
                "available": True,
                "status": "running",
                "url_matches_config": True,
                "protocol_status": "fail",
            }
        },
        root=tmp_path,
    )

    assert evidence["servers"]["memory"]["classification"] == "http_protocol_unhealthy"


def test_http_route_requires_current_endpoint_matched_codex_proof(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.delenv("CODEX_MCP_CALLABLE_MEMORY", raising=False)
    epoch.write_restart_epoch(repo_root=tmp_path, session_id="s1", epoch_id="epoch-1")
    epoch.write_callability_proof(
        server_id="memory",
        tool="memory_health",
        evidence='{"status":"ok"}',
        repo_root=tmp_path,
        route_kind="http",
        endpoint="http://127.0.0.1:8766/mcp",
    )
    contract = {"routes": [_route("memory", "raw_mcp_callable", "")]}

    evidence = mod.build_route_evidence(
        contract,
        {"memory": {"process_count": 1, "classification": "single"}},
        registry_servers={"memory": {"url": "http://127.0.0.1:8766/mcp"}},
        http_service_states={
            "memory": {
                "available": True,
                "status": "running",
                "url_matches_config": True,
            }
        },
        root=tmp_path,
    )

    assert evidence["servers"]["memory"]["classification"] == "codex_http_route_callable"
    assert evidence["servers"]["memory"]["http_callability_acceptance"]["accepted"] is True


def test_adg_http_route_rejects_non_proof_tool(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.delenv("CODEX_MCP_CALLABLE_ADG_SQLITE", raising=False)
    epoch.write_restart_epoch(repo_root=tmp_path, session_id="s1", epoch_id="epoch-1")
    epoch.write_callability_proof(
        server_id="adg_sqlite",
        tool="adg_edge_fanout",
        evidence='{"status":"ok"}',
        repo_root=tmp_path,
        route_kind="http",
        endpoint="http://127.0.0.1:8765/mcp",
    )
    contract = {"routes": [_route("adg_sqlite", "raw_mcp_callable", "")]}

    evidence = mod.build_route_evidence(
        contract,
        {"adg_sqlite": {"process_count": 1, "classification": "single"}},
        registry_servers={"adg_sqlite": {"url": "http://127.0.0.1:8765/mcp"}},
        http_service_states={
            "adg_sqlite": {
                "available": True,
                "status": "running",
                "url_matches_config": True,
            }
        },
        root=tmp_path,
    )

    assert evidence["servers"]["adg_sqlite"]["classification"] == "codex_http_route_unproven"
    assert "adg_proof_tool_not_allowed" in evidence["servers"]["adg_sqlite"]["http_callability_acceptance"]["reasons"]


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


def test_cleanup_python_mcp_marker_requires_direct_argv_match() -> None:
    diagnostic = cleanup.ProcessRecord(
        11,
        1,
        "pwsh.exe",
        (
            "pwsh.exe",
            "-Command",
            "python -c \"print('tools.mcp.launch_adg_sqlite_mcp')\"",
        ),
        101.0,
    )
    real_launcher = cleanup.ProcessRecord(
        12,
        1,
        "python.exe",
        ("python", "-u", "-m", "tools.mcp.launch_adg_sqlite_mcp"),
        102.0,
    )

    assert cleanup._server_id(diagnostic) is None
    assert cleanup._server_id(real_launcher) == "adg_sqlite"


def test_codex_duplicate_cleanup_blocks_without_attached_pid() -> None:
    records = [
        cleanup.ProcessRecord(1, 0, "codex.exe", ("codex.exe",), 100.0),
        cleanup.ProcessRecord(11, 1, "python.exe", ("python", "-u", "tools/memory/adg_memory_server.py"), 101.0),
        cleanup.ProcessRecord(12, 1, "python.exe", ("python", "-u", "tools/memory/adg_memory_server.py"), 102.0),
    ]

    selection = cleanup.select_codex_guarded_targets(records)

    assert selection["status"] == "blocked"
    assert selection["target_pids"] == []
    assert selection["blocked"] == [
        {
            "server_id": "memory",
            "reason": "attached_pid_required",
            "candidate_pids": [11, 12],
        }
    ]


def test_codex_duplicate_cleanup_selects_only_unattached_pids() -> None:
    records = [
        cleanup.ProcessRecord(1, 0, "codex.exe", ("codex.exe",), 100.0),
        cleanup.ProcessRecord(11, 1, "python.exe", ("python", "-u", "tools/memory/adg_memory_server.py"), 101.0),
        cleanup.ProcessRecord(12, 1, "python.exe", ("python", "-u", "tools/memory/adg_memory_server.py"), 102.0),
    ]

    selection = cleanup.select_codex_guarded_targets(records, {"memory": 11})

    assert selection["status"] == "ready"
    assert selection["target_pids"] == [12]
    assert selection["blocked"] == []


def test_codex_duplicate_cleanup_rejects_unknown_attached_pid() -> None:
    records = [
        cleanup.ProcessRecord(1, 0, "codex.exe", ("codex.exe",), 100.0),
        cleanup.ProcessRecord(11, 1, "python.exe", ("python", "-u", "tools/memory/adg_memory_server.py"), 101.0),
        cleanup.ProcessRecord(12, 1, "python.exe", ("python", "-u", "tools/memory/adg_memory_server.py"), 102.0),
    ]

    selection = cleanup.select_codex_guarded_targets(records, {"memory": 99})

    assert selection["status"] == "blocked"
    assert selection["target_pids"] == []
    assert selection["blocked"][0]["reason"] == "attached_pid_not_in_duplicate_group"


def test_codex_cleanup_does_not_block_single_npx_launch_tree() -> None:
    records = [
        cleanup.ProcessRecord(1, 0, "codex.exe", ("codex.exe",), 100.0),
        cleanup.ProcessRecord(10, 1, "cmd.exe", ("cmd.exe", "/c", "npx", "-y", "@upstash/context7-mcp"), 101.0),
        cleanup.ProcessRecord(11, 10, "node.exe", ("node.exe", "npx-cli.js", "-y", "@upstash/context7-mcp"), 102.0),
        cleanup.ProcessRecord(12, 11, "cmd.exe", ("cmd.exe", "/d", "/s", "/c", "context7-mcp"), 103.0),
        cleanup.ProcessRecord(13, 12, "node.exe", ("node.exe", "node_modules/@upstash/context7-mcp/dist/index.js"), 104.0),
    ]

    selection = cleanup.select_codex_guarded_targets(records)

    assert selection["status"] == "no_codex_duplicates"
    assert selection["duplicate_server_ids"] == []
    assert selection["blocked"] == []
    assert selection["target_pids"] == []


def test_codex_cleanup_duplicate_npx_launch_tree_targets_unattached_tree() -> None:
    records = [
        cleanup.ProcessRecord(1, 0, "codex.exe", ("codex.exe",), 100.0),
        cleanup.ProcessRecord(10, 1, "cmd.exe", ("cmd.exe", "/c", "npx", "-y", "@upstash/context7-mcp"), 101.0),
        cleanup.ProcessRecord(11, 10, "node.exe", ("node.exe", "npx-cli.js", "-y", "@upstash/context7-mcp"), 102.0),
        cleanup.ProcessRecord(20, 1, "cmd.exe", ("cmd.exe", "/c", "npx", "-y", "@upstash/context7-mcp"), 201.0),
        cleanup.ProcessRecord(21, 20, "node.exe", ("node.exe", "npx-cli.js", "-y", "@upstash/context7-mcp"), 202.0),
    ]

    blocked = cleanup.select_codex_guarded_targets(records)
    selection = cleanup.select_codex_guarded_targets(records, {"context7": 21})

    assert blocked["status"] == "blocked"
    assert blocked["blocked"] == [
        {
            "server_id": "context7",
            "reason": "attached_pid_required",
            "candidate_pids": [10, 20],
        }
    ]
    assert selection["status"] == "ready"
    assert selection["blocked"] == []
    assert selection["target_pids"] == [10, 11]


def test_cleanup_apply_refuses_blocked_codex_duplicates(monkeypatch) -> None:
    records = [
        cleanup.ProcessRecord(1, 0, "codex.exe", ("codex.exe",), 100.0),
        cleanup.ProcessRecord(11, 1, "python.exe", ("python", "-u", "tools/memory/adg_memory_server.py"), 101.0),
        cleanup.ProcessRecord(12, 1, "python.exe", ("python", "-u", "tools/memory/adg_memory_server.py"), 102.0),
    ]
    monkeypatch.setattr(cleanup, "_snapshot_processes", lambda: records)
    monkeypatch.setattr(cleanup, "_attached_pids_from_env", lambda: {})
    monkeypatch.setattr(
        cleanup,
        "_terminate_targets",
        lambda target_pids: (_ for _ in ()).throw(AssertionError("termination should be blocked")),
    )

    assert cleanup.main(["--apply", "--json"]) == 2


def test_cleanup_apply_with_attached_pid_targets_only_unattached(monkeypatch) -> None:
    records = [
        cleanup.ProcessRecord(1, 0, "codex.exe", ("codex.exe",), 100.0),
        cleanup.ProcessRecord(11, 1, "python.exe", ("python", "-u", "tools/memory/adg_memory_server.py"), 101.0),
        cleanup.ProcessRecord(12, 1, "python.exe", ("python", "-u", "tools/memory/adg_memory_server.py"), 102.0),
    ]
    terminated: list[list[int]] = []
    monkeypatch.setattr(cleanup, "_snapshot_processes", lambda: records)
    monkeypatch.setattr(cleanup, "_attached_pids_from_env", lambda: {})
    monkeypatch.setattr(
        cleanup,
        "_terminate_targets",
        lambda target_pids: terminated.append(target_pids) or {"remaining_target_pids": []},
    )

    assert cleanup.main(["--apply", "--codex-attached-pid", "memory=11", "--json"]) == 0
    assert terminated == [[12]]
