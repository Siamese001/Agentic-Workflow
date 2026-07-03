"""Tests for MCP tool exposure auditing."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import pytest

_AUDIT_PATH = Path(__file__).resolve().parents[3] / ".codex" / "governance" / "scripts" / "mcp_tool_exposure_audit.py"

_spec = importlib.util.spec_from_file_location("_mcp_tool_exposure_audit_under_test", _AUDIT_PATH)
assert _spec is not None and _spec.loader is not None
audit_mod = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = audit_mod
_spec.loader.exec_module(audit_mod)


def _write_config(tmp_path: Path, server_ids: list[str] | None = None) -> Path:
    ids = server_ids or list(audit_mod.MAJOR_MCP_TOOLS)
    servers: dict[str, dict[str, Any]] = {}
    for server_id in ids:
        if server_id == "GitKraken":
            servers[server_id] = {"command": "gk", "args": ["mcp"]}
        elif server_id in {"adg_sqlite", "memory", "vector_db"}:
            servers[server_id] = {"command": "python", "args": ["-u", "-m", f"tools.mcp.{server_id}"]}
        elif server_id in {"context7", "notion", "playwright"}:
            servers[server_id] = {"command": "cmd", "args": ["/c", "npx", "-y", server_id]}
        else:
            servers[server_id] = {"url": f"https://example.invalid/{server_id}"}
    config_path = tmp_path / ".mcp.json"
    config_path.write_text(json.dumps({"mcpServers": servers}), encoding="utf-8")
    return config_path


def _native_lister(server_id: str, _config: dict[str, Any]) -> tuple[bool, set[str], str]:
    assert server_id == "GitKraken"
    return True, set(audit_mod.MAJOR_MCP_TOOLS["GitKraken"]), "native list-tools ok"


def _adg_open() -> tuple[bool, str, str]:
    return True, "open", "active-session ADG MCP transport open"


def _adg_closed() -> tuple[bool, str, str]:
    return False, "callability_unproven", "active-session ADG MCP transport callability_unproven"


def test_tool_search_snapshot_missing_gitkraken_is_red(tmp_path: Path):
    config_path = _write_config(tmp_path)
    observed = {"adg_health", "adg_nodes_by_file", "browser_navigate", "API_query_data_source"}

    results = audit_mod.audit(
        config_path=config_path,
        observed_host_tools=observed,
        heartbeat_report={"ok": True, "alive": ["adg_sqlite", "memory", "vector_db"], "dead": []},
        native_tool_lister=_native_lister,
        adg_transport_checker=_adg_open,
    )

    gitkraken = next(item for item in results if item.server_id == "GitKraken")
    assert gitkraken.status == "RED"
    assert gitkraken.host_exposed is False
    assert "not exposed in Codex tool_search snapshot" in gitkraken.reasons
    assert gitkraken.rca["root_cause"].startswith("The GitKraken CLI can list MCP tools")
    assert gitkraken.rca["fix_or_next"].startswith("next:")


def test_tool_search_snapshot_with_major_tools_is_green(tmp_path: Path):
    config_path = _write_config(tmp_path)
    observed = {tool for tools in audit_mod.MAJOR_MCP_TOOLS.values() for tool in tools[:1]}
    observed.update(audit_mod.MAJOR_MCP_TOOLS["GitKraken"])

    results = audit_mod.audit(
        config_path=config_path,
        observed_host_tools=observed,
        heartbeat_report={"ok": True, "alive": ["adg_sqlite", "memory", "vector_db"], "dead": []},
        native_tool_lister=_native_lister,
        adg_transport_checker=_adg_open,
    )

    by_server = {item.server_id: item for item in results}
    assert set(by_server) == {"GitKraken", "adg_sqlite", "memory"}
    assert by_server["GitKraken"].status == "GREEN"
    assert by_server["memory"].status == "GREEN"


def test_python_mcp_dead_is_red_without_host_snapshot(tmp_path: Path):
    config_path = _write_config(tmp_path)

    results = audit_mod.audit(
        config_path=config_path,
        heartbeat_report={"ok": False, "alive": ["adg_sqlite"], "dead": ["memory", "vector_db"]},
        native_tool_lister=_native_lister,
        adg_transport_checker=_adg_open,
    )

    by_server = {item.server_id: item for item in results}
    assert by_server["memory"].status == "RED"
    assert by_server["memory"].native_ok is False
    assert "python MCP process dead" in by_server["memory"].reasons
    assert by_server["memory"].rca["root_cause"].startswith("The Memory Python MCP process is not alive")
    assert by_server["memory"].rca["fix_or_next"].startswith("next:")


def test_missing_major_server_declaration_is_red(tmp_path: Path):
    config_path = _write_config(tmp_path, server_ids=["adg_sqlite"])

    results = audit_mod.audit(
        config_path=config_path,
        heartbeat_report={"ok": True, "alive": ["adg_sqlite"], "dead": []},
        native_tool_lister=_native_lister,
        adg_transport_checker=_adg_open,
    )

    gitkraken = next(item for item in results if item.server_id == "GitKraken")
    assert gitkraken.status == "RED"
    assert gitkraken.declared is False
    assert "not declared in .mcp.json" in gitkraken.reasons


def test_adg_active_transport_closed_is_red_with_host_snapshot_and_heartbeat(tmp_path: Path):
    config_path = _write_config(tmp_path)
    observed = {tool for tools in audit_mod.MAJOR_MCP_TOOLS.values() for tool in tools}

    results = audit_mod.audit(
        config_path=config_path,
        observed_host_tools=observed,
        heartbeat_report={"ok": True, "alive": ["adg_sqlite", "memory", "vector_db"], "dead": []},
        native_tool_lister=_native_lister,
        adg_transport_checker=_adg_closed,
    )

    adg = next(item for item in results if item.server_id == "adg_sqlite")
    assert adg.status == "RED"
    assert adg.native_ok is True
    assert adg.active_transport_ok is False
    assert adg.active_transport_status == "callability_unproven"
    assert "active-session ADG MCP transport callability_unproven" in adg.reasons
    assert "independent initialize/tools-list probes" in adg.rca["root_cause"]
    assert "supervisor open=true" in adg.rca["recurrence_guard"]


def test_native_lister_reports_missing_env_var_before_subprocess(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    config_path = tmp_path / ".mcp.json"
    config_path.write_text(
        json.dumps(
            {
                "mcpServers": {
                    "GitKraken": {
                        "command": "${GITKRAKEN_GK_PATH}",
                        "args": ["mcp"],
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.delenv("GITKRAKEN_GK_PATH", raising=False)

    ok, tools, reason = audit_mod._config_command_tools("GitKraken", json.loads(config_path.read_text()))

    assert ok is False
    assert tools == set()
    assert reason == "missing env var(s): GITKRAKEN_GK_PATH"


def test_load_tool_search_snapshot_extracts_nested_tool_names(tmp_path: Path):
    snapshot = tmp_path / "tool-search.json"
    snapshot.write_text(
        json.dumps(
            {
                "tools": [
                    {"namespace": "mcp__adg_sqlite", "name": "adg_health"},
                    "mcp__playwright.browser_navigate",
                    {"tool_name": "pull_request_create"},
                ]
            }
        ),
        encoding="utf-8",
    )

    names = audit_mod.load_tool_search_snapshot(snapshot)

    assert "adg_health" in names
    assert "browser_navigate" in names
    assert "pull_request_create" in names


def test_cli_advisory_returns_zero_on_red_results(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    config_path = _write_config(tmp_path, server_ids=["adg_sqlite"])
    monkeypatch.setattr(
        audit_mod,
        "audit",
        lambda **_kwargs: [
            audit_mod.ExposureResult(
                server_id="GitKraken",
                status="RED",
                declared=False,
                host_exposed=None,
                native_ok=None,
                expected_tools=["git_status"],
                reasons=["not declared in .mcp.json"],
            )
        ],
    )

    rc = audit_mod.main(["--config", str(config_path), "--advisory", "--json"])

    assert rc == 0
