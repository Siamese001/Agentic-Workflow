"""Tests for check_notion_classification_gate in pre_mcp_gate.py.

Advisory gate that logs sub-threshold Notion DB writes to a JSONL file.
Always exits 0 — never blocks writes.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
SCRIPTS_DIR = REPO_ROOT / ".claude" / "governance" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import pre_mcp_gate as gate  # noqa: E402

# Canonical DB IDs under test.
_PLANS_DB = "ac53d31b-3068-4039-9ebe-856c12caab32"
_BACKLOG_DB = "fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7"
_OTHER_DB = "aaaabbbb-cccc-dddd-eeee-ffffffffffff"


def _post_page_payload(db_id: str, props: dict | None = None) -> dict:
    """Build a normalized pre_mcp_gate payload for an API-post-page call."""
    return {
        "tool_name": "mcp__notion__API-post-page",
        "tool_info": {
            "mcp_server_name": "notion",
            "mcp_tool_name": "mcp__notion__API-post-page",
        },
        "tool_input": {
            "parent": {"database_id": db_id},
            "properties": props or {"Name": {"title": [{"text": {"content": "test"}}]}},
        },
    }


@pytest.fixture(autouse=True)
def _clear_bypass(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("NOTION_CLASSIFICATION_GATE_BYPASS", raising=False)


@pytest.fixture()
def violations_log(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    log = tmp_path / "notion_classification_violations.jsonl"
    monkeypatch.setattr(gate, "_NOTION_CLASSIFICATION_VIOLATIONS", log)
    return log


class TestNotionClassificationGate:
    def test_non_post_page_tool_exits_0_no_log(self, violations_log: Path) -> None:
        rc = gate.check_notion_classification_gate("mcp__notion__API-patch-page", _post_page_payload(_PLANS_DB))
        assert rc == 0
        assert not violations_log.exists()

    def test_bypass_exits_0_no_log(
        self, violations_log: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("NOTION_CLASSIFICATION_GATE_BYPASS", "1")
        rc = gate.check_notion_classification_gate("mcp__notion__API-post-page", _post_page_payload(_PLANS_DB))
        assert rc == 0
        assert not violations_log.exists()

    def test_unknown_db_exits_0_no_log(self, violations_log: Path) -> None:
        rc = gate.check_notion_classification_gate(
            "mcp__notion__API-post-page", _post_page_payload(_OTHER_DB)
        )
        assert rc == 0
        assert not violations_log.exists()

    def test_plans_db_exits_0_logs_advisory(self, violations_log: Path) -> None:
        rc = gate.check_notion_classification_gate(
            "mcp__notion__API-post-page",
            _post_page_payload(_PLANS_DB, props={"Name": {"title": []}, "Status": {"select": {"name": "Not Started"}}}),
        )
        assert rc == 0
        assert violations_log.exists()
        row = json.loads(violations_log.read_text(encoding="utf-8").strip())
        assert row["kind"] == "notion_classification_advisory"
        assert row["target_db"] == "Plans"
        assert row["database_id"] == _PLANS_DB.lower()
        assert row["advisory"] is True
        assert "PLAN_MULTI_WAVE" in row["threshold_msg"]
        assert "Status" in row["property_keys_present"]

    def test_backlog_db_exits_0_logs_advisory(self, violations_log: Path) -> None:
        rc = gate.check_notion_classification_gate(
            "mcp__notion__API-post-page",
            _post_page_payload(_BACKLOG_DB, props={"Name": {"title": []}}),
        )
        assert rc == 0
        assert violations_log.exists()
        row = json.loads(violations_log.read_text(encoding="utf-8").strip())
        assert row["target_db"] == "BacklogItems"
        assert "BUG_SYSTEMIC" in row["threshold_msg"]
        assert "spawn_task" in row["threshold_msg"]

    def test_plans_db_id_without_hyphens_matches(self, violations_log: Path) -> None:
        bare_id = _PLANS_DB.replace("-", "")
        payload = {
            "tool_name": "mcp__notion__API-post-page",
            "tool_info": {"mcp_server_name": "notion", "mcp_tool_name": "mcp__notion__API-post-page"},
            "tool_input": {"parent": {"database_id": bare_id}, "properties": {}},
        }
        rc = gate.check_notion_classification_gate("mcp__notion__API-post-page", payload)
        assert rc == 0
        assert violations_log.exists()
        row = json.loads(violations_log.read_text(encoding="utf-8").strip())
        assert row["target_db"] == "Plans"

    def test_missing_tool_input_exits_0_no_log(self, violations_log: Path) -> None:
        payload = {
            "tool_name": "mcp__notion__API-post-page",
            "tool_info": {"mcp_server_name": "notion"},
        }
        rc = gate.check_notion_classification_gate("mcp__notion__API-post-page", payload)
        assert rc == 0
        assert not violations_log.exists()

    def test_tool_input_string_json_parses_and_logs(self, violations_log: Path) -> None:
        payload = {
            "tool_name": "mcp__notion__API-post-page",
            "tool_info": {"mcp_server_name": "notion"},
            "tool_input": json.dumps({"parent": {"database_id": _PLANS_DB}, "properties": {}}),
        }
        rc = gate.check_notion_classification_gate("mcp__notion__API-post-page", payload)
        assert rc == 0
        assert violations_log.exists()

    def test_tool_input_invalid_json_exits_0_no_log(self, violations_log: Path) -> None:
        payload = {
            "tool_name": "mcp__notion__API-post-page",
            "tool_input": "not-json!",
        }
        rc = gate.check_notion_classification_gate("mcp__notion__API-post-page", payload)
        assert rc == 0
        assert not violations_log.exists()

    def test_missing_parent_database_id_exits_0_no_log(self, violations_log: Path) -> None:
        payload = {
            "tool_name": "mcp__notion__API-post-page",
            "tool_input": {"parent": {}, "properties": {}},
        }
        rc = gate.check_notion_classification_gate("mcp__notion__API-post-page", payload)
        assert rc == 0
        assert not violations_log.exists()

    def test_advisory_stderr_message_contains_db_name(
        self, violations_log: Path, capsys: pytest.CaptureFixture
    ) -> None:
        gate.check_notion_classification_gate(
            "mcp__notion__API-post-page", _post_page_payload(_BACKLOG_DB)
        )
        captured = capsys.readouterr()
        assert "NOTION-CLASSIFICATION-ADVISORY" in captured.err
        assert "BacklogItems" in captured.err

    def test_multiple_writes_append_rows(self, violations_log: Path) -> None:
        for _ in range(3):
            gate.check_notion_classification_gate(
                "mcp__notion__API-post-page", _post_page_payload(_PLANS_DB)
            )
        rows = [json.loads(line) for line in violations_log.read_text(encoding="utf-8").strip().splitlines()]
        assert len(rows) == 3
        assert all(r["target_db"] == "Plans" for r in rows)
