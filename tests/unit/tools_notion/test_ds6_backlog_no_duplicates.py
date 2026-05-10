"""
DS-6 unit tests for ops_scripts/ci/check_notion_backlog_no_duplicates.py.

Covers:
  - find_duplicate_titles: no dups, single dup group, multiple groups
  - _title extraction from Phase Title / Title / Name / id fallback
  - main(): bypass env var, token-absent skip, no-dups pass, dups fail,
    fail-closed vs advisory mode
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = REPO_ROOT / "ops_scripts" / "ci" / "check_notion_backlog_no_duplicates.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_notion_backlog_no_duplicates", MODULE_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("check_notion_backlog_no_duplicates", mod)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mod():
    return _load()


# ---------------------------------------------------------------------------
# _title helper
# ---------------------------------------------------------------------------


def _make_row(page_id: str, prop_name: str, prop_type: str, text: str) -> dict:
    if prop_type == "title":
        prop = {"type": "title", "title": [{"plain_text": text}]}
    else:
        prop = {"type": "rich_text", "rich_text": [{"plain_text": text}]}
    return {"id": page_id, "properties": {prop_name: prop}}


def test_title_phase_title(mod):
    row = _make_row("abcd1234", "Phase Title", "title", "My Phase")
    assert mod._title(row) == "My Phase"


def test_title_fallback_to_title(mod):
    row = _make_row("abcd1234", "Title", "title", "My Title")
    assert mod._title(row) == "My Title"


def test_title_fallback_to_name(mod):
    row = _make_row("abcd1234", "Name", "rich_text", "My Name")
    assert mod._title(row) == "My Name"


def test_title_id_fallback(mod):
    row = {"id": "deadbeef-0000", "properties": {}}
    result = mod._title(row)
    assert result.startswith("deadbeef")


# ---------------------------------------------------------------------------
# find_duplicate_titles
# ---------------------------------------------------------------------------


def test_no_duplicates_returns_empty(mod):
    rows = [
        _make_row("id1", "Title", "title", "Alpha"),
        _make_row("id2", "Title", "title", "Beta"),
        _make_row("id3", "Title", "title", "Gamma"),
    ]
    assert mod.find_duplicate_titles(rows) == {}


def test_single_dup_group(mod):
    rows = [
        _make_row("id1", "Title", "title", "Alpha"),
        _make_row("id2", "Title", "title", "Alpha"),
        _make_row("id3", "Title", "title", "Beta"),
    ]
    dups = mod.find_duplicate_titles(rows)
    assert "Alpha" in dups
    assert set(dups["Alpha"]) == {"id1", "id2"}
    assert "Beta" not in dups


def test_multiple_dup_groups(mod):
    rows = [
        _make_row("id1", "Title", "title", "X"),
        _make_row("id2", "Title", "title", "X"),
        _make_row("id3", "Title", "title", "Y"),
        _make_row("id4", "Title", "title", "Y"),
        _make_row("id5", "Title", "title", "Z"),
    ]
    dups = mod.find_duplicate_titles(rows)
    assert set(dups.keys()) == {"X", "Y"}
    assert len(dups["X"]) == 2
    assert len(dups["Y"]) == 2


def test_triple_dup_group(mod):
    rows = [_make_row(f"id{i}", "Title", "title", "Same") for i in range(3)]
    dups = mod.find_duplicate_titles(rows)
    assert len(dups["Same"]) == 3


# ---------------------------------------------------------------------------
# main() — offline / bypass paths
# ---------------------------------------------------------------------------


def test_main_skip_when_no_token(mod, monkeypatch):
    monkeypatch.delenv("NOTION_TOKEN", raising=False)
    monkeypatch.delenv("NOTION_API_KEY", raising=False)
    monkeypatch.delenv("BACKLOG_DUP_BYPASS", raising=False)
    rc = mod.main()
    assert rc == 0


def test_main_bypass(mod, monkeypatch, tmp_path):
    monkeypatch.setenv("BACKLOG_DUP_BYPASS", "1")
    monkeypatch.setattr(mod, "VIOLATIONS_LOG", tmp_path / "v.jsonl")
    rc = mod.main()
    assert rc == 0


def test_main_no_dups(mod, monkeypatch):
    monkeypatch.setenv("NOTION_TOKEN", "fake-token")
    monkeypatch.delenv("BACKLOG_DUP_BYPASS", raising=False)
    rows = [
        _make_row("id1", "Title", "title", "Alpha"),
        _make_row("id2", "Title", "title", "Beta"),
    ]
    monkeypatch.setattr(mod, "_query_all", lambda token: rows)
    rc = mod.main()
    assert rc == 0


def test_main_dups_advisory(mod, monkeypatch, tmp_path):
    monkeypatch.setenv("NOTION_TOKEN", "fake-token")
    monkeypatch.delenv("BACKLOG_DUP_BYPASS", raising=False)
    monkeypatch.delenv("BACKLOG_DUP_FAIL_CLOSED", raising=False)
    monkeypatch.setattr(mod, "VIOLATIONS_LOG", tmp_path / "v.jsonl")
    rows = [
        _make_row("id1", "Title", "title", "Dupe"),
        _make_row("id2", "Title", "title", "Dupe"),
    ]
    monkeypatch.setattr(mod, "_query_all", lambda token: rows)
    rc = mod.main()
    assert rc == 0  # advisory — exits 0


def test_main_dups_fail_closed(mod, monkeypatch, tmp_path):
    monkeypatch.setenv("NOTION_TOKEN", "fake-token")
    monkeypatch.setenv("BACKLOG_DUP_FAIL_CLOSED", "1")
    monkeypatch.delenv("BACKLOG_DUP_BYPASS", raising=False)
    monkeypatch.setattr(mod, "VIOLATIONS_LOG", tmp_path / "v.jsonl")
    rows = [
        _make_row("id1", "Title", "title", "Dupe"),
        _make_row("id2", "Title", "title", "Dupe"),
    ]
    monkeypatch.setattr(mod, "_query_all", lambda token: rows)
    rc = mod.main()
    assert rc == 1
