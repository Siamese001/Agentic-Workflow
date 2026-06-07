"""Unit tests: Cursor beforeMCPExecution chain (pre_mcp_gate ordering + plan auditor)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
HOOKS_LIB = REPO_ROOT / ".cursor" / "hooks"
if str(HOOKS_LIB) not in sys.path:
    sys.path.insert(0, str(HOOKS_LIB))

from lib import cursor_hook_common  # noqa: E402

AUDITOR_PATH = REPO_ROOT / ".claude" / "governance/scripts" / "unified_plan_creation_auditor.py"


def _load_auditor():
    import importlib.util

    name = "unified_plan_creation_auditor_cursor_test"
    spec = importlib.util.spec_from_file_location(
        name,
        AUDITOR_PATH,
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


upa = _load_auditor()


def _valid_plans_post_properties() -> dict:
    return {
        "Slug": {"title": [{"text": {"content": "my-plan-a1b2c3"}}]},
        "Status": {"select": {"name": "Not Started"}},
        "Summary": {"rich_text": [{"text": {"content": "Summary text"}}]},
        "AI Summary ": {"rich_text": [{"text": {"content": "Bullet ok"}}]},
        "Exists On Disk": {"checkbox": True},
    }


class TestCursorHookCommonMcpParsing:
    def test_parse_tool_input_dict(self) -> None:
        p = {"tool_input": {"parent": {"database_id": "x"}}}
        assert cursor_hook_common.parse_mcp_tool_input(p) == {"parent": {"database_id": "x"}}

    def test_parse_tool_input_json_string(self) -> None:
        inner = {"a": 1}
        p = {"tool_input": json.dumps(inner)}
        assert cursor_hook_common.parse_mcp_tool_input(p) == inner

    def test_parse_tool_input_missing_is_none(self) -> None:
        assert cursor_hook_common.parse_mcp_tool_input({}) is None

    def test_normalize_infers_server_from_command_key(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        mcp = {"mcpServers": {"notion": {"command": "npx"}}}
        root = tmp_path / "proj"
        (root / ".cursor").mkdir(parents=True)
        (root / ".cursor" / "mcp.json").write_text(json.dumps(mcp), encoding="utf-8")
        monkeypatch.setattr(cursor_hook_common, "_REPO_ROOT_FOR_MCP", root)
        cursor_hook_common.mcp_config_server_keys.cache_clear()
        payload = {"command": "notion", "tool_name": "API-post-page", "tool_input": "{}"}
        norm = cursor_hook_common.normalize_mcp_payload(payload)
        assert norm["tool_info"]["mcp_server_name"] == "notion"
        cursor_hook_common.mcp_config_server_keys.cache_clear()

    def test_resolve_server_from_command_key(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        mcp = {"mcpServers": {"notion": {"command": "npx"}}}
        root = tmp_path / "proj"
        (root / ".cursor").mkdir(parents=True)
        (root / ".cursor" / "mcp.json").write_text(json.dumps(mcp), encoding="utf-8")
        monkeypatch.setattr(cursor_hook_common, "_REPO_ROOT_FOR_MCP", root)

        cursor_hook_common.mcp_config_server_keys.cache_clear()

        payload = {"command": "notion", "tool_name": "API-post-page"}
        norm = cursor_hook_common.normalize_mcp_payload(payload)
        assert cursor_hook_common.resolve_mcp_server_name(payload, norm) == "notion"

        cursor_hook_common.mcp_config_server_keys.cache_clear()


class TestRunMcpPlanAuditorStage:
    def test_non_notion_not_applicable(self) -> None:
        p = {"tool_info": {"mcp_server_name": "memory", "mcp_tool_name": "search_nodes"}}
        assert upa.run_mcp_plan_auditor_stage(p) == 0

    def test_notion_non_post_page_not_applicable(self) -> None:
        p = {
            "tool_info": {"mcp_server_name": "notion", "mcp_tool_name": "API-query-data-source"},
            "tool_input": "{}",
        }
        assert upa.run_mcp_plan_auditor_stage(p) == 0

    def test_notion_post_wrong_database_not_applicable(self) -> None:
        p = {
            "tool_info": {"mcp_server_name": "notion", "mcp_tool_name": "API-post-page"},
            "tool_input": json.dumps(
                {
                    "parent": {"database_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"},
                    "properties": _valid_plans_post_properties(),
                }
            ),
        }
        assert upa.run_mcp_plan_auditor_stage(p) == 0

    def test_notion_post_plans_invalid_status_blocks(self) -> None:
        props = _valid_plans_post_properties()
        props["Status"] = {"select": {"name": "In Progress"}}
        p = {
            "tool_info": {"mcp_server_name": "notion", "mcp_tool_name": "mcp7_API-post-page"},
            "tool_input": json.dumps(
                {
                    "parent": {"data_source_id": upa.PLANS_DATA_SOURCE_ID},
                    "properties": props,
                }
            ),
        }
        assert upa.run_mcp_plan_auditor_stage(p) == 2

    def test_notion_post_plans_valid_allows(self) -> None:
        p = {
            "tool_info": {"mcp_server_name": "notion", "mcp_tool_name": "API-post-page"},
            "tool_input": json.dumps(
                {
                    "parent": {"data_source_id": upa.PLANS_DATA_SOURCE_ID},
                    "properties": _valid_plans_post_properties(),
                }
            ),
        }
        assert upa.run_mcp_plan_auditor_stage(p) == 0

    def test_malformed_tool_input_blocks(self) -> None:
        p = {
            "tool_info": {"mcp_server_name": "notion", "mcp_tool_name": "API-post-page"},
            "tool_input": "{not-json",
        }
        assert upa.run_mcp_plan_auditor_stage(p) == 2


class TestBeforeMcpHookScriptOrdering:
    def test_gate_invoked_before_auditor_in_source(self) -> None:
        path = REPO_ROOT / ".cursor" / "hooks" / "before_mcp_execution.py"
        text = path.read_text(encoding="utf-8")
        gate_call = text.index("gate_rc = _run_pre_mcp_gate")
        auditor_call = text.index("auditor_rc = _run_unified_plan_auditor")
        assert gate_call < auditor_call
