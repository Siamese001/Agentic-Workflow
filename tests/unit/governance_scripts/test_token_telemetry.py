"""Unit tests for `.claude/governance/scripts/_legacy_windsurf/_post_handlers/token_telemetry.py`."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
HANDLERS_DIR = REPO_ROOT / ".claude" / "governance" / "scripts"
sys.path.insert(0, str(HANDLERS_DIR))

from _post_handlers import token_telemetry  # noqa: E402
from _post_handlers import ParsedResponse  # noqa: E402


def _make_parsed(text: str) -> ParsedResponse:
    return ParsedResponse(raw=text, response_text=text)


def test_approx_tokens_zero_for_empty() -> None:
    assert token_telemetry._approx_tokens("") == 0


def test_approx_tokens_bytes_div_4() -> None:
    assert token_telemetry._approx_tokens("a" * 100) == 25


def test_count_tool_calls_extracts_names() -> None:
    text = (
        '<invoke name="read_file">'
        '<invoke name="read_file">'
        '<invoke name="grep_search">'
        '<invoke name="mcp4_read_text_file">'
    )
    counts = token_telemetry._count_tool_calls(text)
    assert counts["read_file"] == 2
    assert counts["grep_search"] == 1
    assert counts["mcp4_read_text_file"] == 1


def test_count_tool_calls_empty() -> None:
    assert token_telemetry._count_tool_calls("just prose") == {}


def test_count_markers_only_present() -> None:
    text = "DECISION_CAPTURED: foo\nNEXT_STEP: bar\nNEXT_STEP: baz\n"
    out = token_telemetry._count_markers(text)
    assert out == {"DECISION_CAPTURED": 1, "NEXT_STEP": 2}


def test_run_writes_row(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TOKEN_TELEMETRY_DISABLED", raising=False)
    text = (
        '<invoke name="read_file"><invoke name="grep_search">'
        "DECISION_CAPTURED: foo bar baz"
    )
    token_telemetry.run(_make_parsed(text), tmp_path)
    log = tmp_path / "artifacts" / "governance" / "turn_budget.jsonl"
    assert log.exists()
    rows = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 1
    row = rows[0]
    assert row["tool_call_total"] == 2
    assert row["tool_call_counts"] == {"read_file": 1, "grep_search": 1}
    assert row["marker_counts"] == {"DECISION_CAPTURED": 1}
    assert row["response_bytes"] == len(text)
    assert row["approx_response_tokens"] == len(text) // 4
    assert row["via"] == "dispatcher"


def test_run_disabled_via_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TOKEN_TELEMETRY_DISABLED", "1")
    token_telemetry.run(_make_parsed("anything"), tmp_path)
    log = tmp_path / "artifacts" / "governance" / "turn_budget.jsonl"
    assert not log.exists()


def test_run_empty_payload_noop(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TOKEN_TELEMETRY_DISABLED", raising=False)
    token_telemetry.run(_make_parsed(""), tmp_path)
    log = tmp_path / "artifacts" / "governance" / "turn_budget.jsonl"
    assert not log.exists()


def test_run_appends_multiple_rows(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TOKEN_TELEMETRY_DISABLED", raising=False)
    token_telemetry.run(_make_parsed('<invoke name="read_file">'), tmp_path)
    token_telemetry.run(_make_parsed('<invoke name="grep_search">'), tmp_path)
    log = tmp_path / "artifacts" / "governance" / "turn_budget.jsonl"
    rows = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 2
    assert rows[0]["tool_call_counts"] == {"read_file": 1}
    assert rows[1]["tool_call_counts"] == {"grep_search": 1}
