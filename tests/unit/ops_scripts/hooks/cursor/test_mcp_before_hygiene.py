"""W1.2 — ``mcp_before_hygiene`` stage (tool_input bounds + legacy scan)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
HOOKS_LIB = REPO_ROOT / ".claude" / "hooks"
if str(HOOKS_LIB) not in sys.path:
    sys.path.insert(0, str(HOOKS_LIB))

import lib.mcp_before_hygiene as mbh  # noqa: E402


@pytest.fixture()
def hygiene_log(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    log = tmp_path / "mcp_before_hygiene.jsonl"
    monkeypatch.setattr(mbh, "_HYGIENE_LOG", log)
    return log


class TestMcpBeforeHygiene:
    def test_no_tool_input_not_applicable(self, hygiene_log: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("MCP_BEFORE_HYGIENE_BYPASS", raising=False)
        assert mbh.run_mcp_before_hygiene_stage({"tool_info": {"mcp_tool_name": "x"}}) == 0
        assert not hygiene_log.exists()

    def test_bypass_not_applicable(self, hygiene_log: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MCP_BEFORE_HYGIENE_BYPASS", "1")
        assert mbh.run_mcp_before_hygiene_stage({"tool_input": "{}"}) == 0
        lines = hygiene_log.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1
        assert json.loads(lines[0])["outcome"] == "NOT_APPLICABLE"

    def test_allow_clean_tool_input_dict(self, hygiene_log: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("MCP_BEFORE_HYGIENE_BYPASS", raising=False)
        p = {"tool_input": {"parent": {"database_id": "x"}, "properties": {}}}
        assert mbh.run_mcp_before_hygiene_stage(p) == 0
        row = json.loads(hygiene_log.read_text(encoding="utf-8").strip().splitlines()[-1])
        assert row["outcome"] == "ALLOW"

    def test_block_oversized_string(self, hygiene_log: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("MCP_BEFORE_HYGIENE_BYPASS", raising=False)
        huge = "x" * (mbh._TOOL_INPUT_MAX_BYTES + 1)
        assert mbh.run_mcp_before_hygiene_stage({"tool_input": huge}) == 2
        row = json.loads(hygiene_log.read_text(encoding="utf-8").strip().splitlines()[-1])
        assert row["outcome"] == "BLOCK"
        assert row["code"] == "TOOL_INPUT_OVERSIZED"

    def test_block_bad_json_string(self, hygiene_log: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("MCP_BEFORE_HYGIENE_BYPASS", raising=False)
        assert mbh.run_mcp_before_hygiene_stage({"tool_input": "{not-json"}) == 2
        row = json.loads(hygiene_log.read_text(encoding="utf-8").strip().splitlines()[-1])
        assert row["code"] == "TOOL_INPUT_JSON_INVALID"

    def test_block_legacy_windsurf_in_tool_input(self, hygiene_log: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("MCP_BEFORE_HYGIENE_BYPASS", raising=False)
        p = {"tool_input": json.dumps({"path": "C:/x/docs/archive/windsurf/legacy-tree/foo"})}
        assert mbh.run_mcp_before_hygiene_stage(p) == 2
        row = json.loads(hygiene_log.read_text(encoding="utf-8").strip().splitlines()[-1])
        assert row["code"] == "LEGACY_SURFACE_IN_TOOL_INPUT"


class TestBeforeMcpFullChainOrdering:
    def test_stage_order_in_source(self) -> None:
        text = (REPO_ROOT / ".claude" / "hooks" / "before_mcp_execution.py").read_text(encoding="utf-8")
        g = text.index("gate_rc = _run_pre_mcp_gate")
        a = text.index("auditor_rc = _run_unified_plan_auditor")
        h = text.index("hygiene_rc = run_mcp_before_hygiene_stage")
        assert g < a < h

    def test_pre_mcp_gate_failure_exits_before_later_stages(self) -> None:
        text = (REPO_ROOT / ".claude" / "hooks" / "before_mcp_execution.py").read_text(encoding="utf-8")
        gate_exit = text.index("if gate_rc != 0:")
        auditor_assign = text.index("auditor_rc = ")
        assert gate_exit < auditor_assign
