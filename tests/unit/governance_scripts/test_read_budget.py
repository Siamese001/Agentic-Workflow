"""Unit tests for `.codex/governance/scripts/_legacy_windsurf/_post_handlers/read_budget.py`.

Coverage:
- Counts native read_file invocations
- Counts MCP read_text_file / read_file / read_multiple_files (any prefix)
- Counts read_notebook and read_url_content
- Under-cap responses do NOT log a violation
- Over-cap responses DO log a violation with correct counts
- Bypass env var causes a row to be logged with bypass=true even under-cap
- Empty / non-string input is fail-soft
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
# Canonical path — _post_handlers/ lives in governance/scripts/, not _legacy_windsurf/
HANDLERS_DIR = REPO_ROOT / ".codex" / "governance" / "scripts"
sys.path.insert(0, str(HANDLERS_DIR))

# Import the handler module directly.
from _post_handlers import read_budget  # noqa: E402
from _post_handlers import ParsedResponse  # noqa: E402


# ---------------------------------------------------------------------------
# Pure counting (no I/O)
# ---------------------------------------------------------------------------


def test_count_native_read_file() -> None:
    text = '<invoke name="read_file"><param>foo</param></invoke>' * 3
    counts = read_budget._count_invocations(text)
    assert counts["read_file"] == 3
    assert sum(counts.values()) == 3


def test_count_mcp_read_text_file_any_prefix() -> None:
    text = (
        '<invoke name="mcp4_read_text_file">'
        '<invoke name="mcp7_read_text_file">'
        '<invoke name="mcp12_read_text_file">'
    )
    counts = read_budget._count_invocations(text)
    assert counts["mcp_read_text_file"] == 3


def test_count_mcp_read_multiple_files() -> None:
    text = '<invoke name="mcp4_read_multiple_files">' * 2
    counts = read_budget._count_invocations(text)
    assert counts["mcp_read_multiple_files"] == 2


def test_count_read_notebook_and_url() -> None:
    text = '<invoke name="read_notebook"><invoke name="read_url_content">'
    counts = read_budget._count_invocations(text)
    assert counts["read_notebook"] == 1
    assert counts["read_url_content"] == 1


def test_count_mixed_total() -> None:
    text = (
        '<invoke name="read_file">'
        '<invoke name="read_file">'
        '<invoke name="mcp4_read_text_file">'
        '<invoke name="mcp4_read_multiple_files">'
        '<invoke name="read_notebook">'
    )
    counts = read_budget._count_invocations(text)
    assert sum(counts.values()) == 5


def test_count_zero_when_no_invocations() -> None:
    text = "Just prose with no tool calls."
    counts = read_budget._count_invocations(text)
    assert sum(counts.values()) == 0


# ---------------------------------------------------------------------------
# run() integration with the violations log
# ---------------------------------------------------------------------------


def _make_parsed(text: str) -> ParsedResponse:
    return ParsedResponse(raw=text, response_text=text)


def test_under_cap_does_not_log(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("READ_BUDGET_BYPASS", raising=False)
    text = '<invoke name="read_file">' * 5  # under cap of 10
    read_budget.run(_make_parsed(text), tmp_path)
    log = tmp_path / "artifacts" / "governance" / "read_budget_violations.jsonl"
    assert not log.exists()


def test_over_cap_logs_violation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("READ_BUDGET_BYPASS", raising=False)
    text = '<invoke name="read_file">' * 12  # over cap
    read_budget.run(_make_parsed(text), tmp_path)
    log = tmp_path / "artifacts" / "governance" / "read_budget_violations.jsonl"
    assert log.exists()
    rows = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 1
    row = rows[0]
    assert row["total"] == 12
    assert row["over_cap"] is True
    assert row["bypass"] is False
    assert row["counts"]["read_file"] == 12
    assert row["via"] == "dispatcher"


def test_bypass_logs_even_under_cap(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("READ_BUDGET_BYPASS", "1")
    text = '<invoke name="read_file">'  # 1 read, under cap
    read_budget.run(_make_parsed(text), tmp_path)
    log = tmp_path / "artifacts" / "governance" / "read_budget_violations.jsonl"
    assert log.exists()
    rows = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
    assert rows[0]["bypass"] is True
    assert rows[0]["over_cap"] is False


def test_empty_text_is_noop(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("READ_BUDGET_BYPASS", raising=False)
    read_budget.run(_make_parsed(""), tmp_path)
    log = tmp_path / "artifacts" / "governance" / "read_budget_violations.jsonl"
    assert not log.exists()


def test_mixed_tools_aggregate_to_total(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("READ_BUDGET_BYPASS", raising=False)
    text = (
        '<invoke name="read_file">' * 4
        + '<invoke name="mcp4_read_text_file">' * 4
        + '<invoke name="mcp4_read_multiple_files">' * 3
    )
    read_budget.run(_make_parsed(text), tmp_path)
    log = tmp_path / "artifacts" / "governance" / "read_budget_violations.jsonl"
    rows = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
    assert rows[0]["total"] == 11
    assert rows[0]["counts"]["read_file"] == 4
    assert rows[0]["counts"]["mcp_read_text_file"] == 4
    assert rows[0]["counts"]["mcp_read_multiple_files"] == 3
