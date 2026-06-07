"""
tests/unit/windsurf_scripts/test_plan_wave_table_updater.py

Unit tests for tools/plan_lifecycle/_plan_wave_table_updater.py.

Tests are pure-Python: they write temp plan files and assert the on-disk
content after calling update_wave_in_plan.
"""
from __future__ import annotations

import io
import os
import re
import sys
import textwrap
from pathlib import Path
from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))

from tools.plan_lifecycle._plan_wave_table_updater import (  # noqa: E402
    STATUS_DONE,
    STATUS_IN_PROGRESS,
    STATUS_TODO,
    _find_plan_file,
    _update_phase_in_plan,
    update_wave_in_plan,
    update_wave_note_columns,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SLUG = "test-plan-aabbcc"
PLAN_FILENAME = f"{SLUG}.md"


def _make_plan(tmp_path: Path, content: str) -> Path:
    """Write a plan .md file under docs/archive/windsurf/legacy-tree/plans/ inside tmp_path."""
    plans_dir = tmp_path / "docs" / "archive" / "windsurf" / "legacy-tree" / "plans"
    plans_dir.mkdir(parents=True)
    plan_file = plans_dir / PLAN_FILENAME
    plan_file.write_text(textwrap.dedent(content), encoding="utf-8")
    return plan_file


SAMPLE_WAVE_TABLE = """\
# Test Plan

## Wave Structure

| Wave | Focus | Scope | Status |
|------|-------|-------|--------|
| W0 | Baseline | 4 gates | 🔲 TODO |
| W1 | Discovery | Read-only | 🔲 TODO |
| W1.5 | Matrix | 1 artifact | 🔲 TODO |
| W2 | Payload | 2 artifacts | 🔲 TODO |
| W3 | Impl | Tests | 🔲 TODO |
| **W4** | Wiring | Bindings | 🔲 TODO |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W0 | Baseline | 4 CI gates | Must pass | ~2K | 🔲 TODO |
| W1 | Discovery | All source | Touchpoints | ~8K | 🔲 TODO |
"""

SAMPLE_WITH_BLOCKED = """\
# Test Plan

## Wave Structure

| Wave | Focus | Scope | Status |
|------|-------|-------|--------|
| W0 | Baseline | 4 gates | ✅ DONE |
| W1 | Discovery | Read-only | 🔄 IN PROGRESS |
| W2 | Payload | 2 artifacts | ❌ BLOCKED |
| W3 | Impl | Tests | 🔲 TODO |
"""


# ---------------------------------------------------------------------------
# wave_complete tests
# ---------------------------------------------------------------------------


def test_wave_complete_flips_todo_to_done(tmp_path: Path) -> None:
    plan_file = _make_plan(tmp_path, SAMPLE_WAVE_TABLE)
    ok, msg = update_wave_in_plan(tmp_path, SLUG, wave=1, kind="wave_complete")
    assert ok, msg
    content = plan_file.read_text(encoding="utf-8")
    # W1 row should be DONE; W0 and W2+ should stay TODO
    assert "| W1 | Discovery | Read-only | ✅ DONE |" in content
    assert "| W0 | Baseline | 4 gates | 🔲 TODO |" in content
    assert "| W2 | Payload | 2 artifacts | 🔲 TODO |" in content
    # Phase-Level W1 row also updated
    assert "| W1 | Discovery | All source | Touchpoints | ~8K | ✅ DONE |" in content


def test_wave_complete_flips_in_progress_to_done(tmp_path: Path) -> None:
    content = SAMPLE_WAVE_TABLE.replace(
        "| W2 | Payload | 2 artifacts | 🔲 TODO |",
        "| W2 | Payload | 2 artifacts | 🔄 IN PROGRESS |",
    )
    plan_file = _make_plan(tmp_path, content)
    ok, msg = update_wave_in_plan(tmp_path, SLUG, wave=2, kind="wave_complete")
    assert ok, msg
    result = plan_file.read_text(encoding="utf-8")
    assert "| W2 | Payload | 2 artifacts | ✅ DONE |" in result


def test_wave_complete_bold_label(tmp_path: Path) -> None:
    plan_file = _make_plan(tmp_path, SAMPLE_WAVE_TABLE)
    ok, msg = update_wave_in_plan(tmp_path, SLUG, wave=4, kind="wave_complete")
    assert ok, msg
    content = plan_file.read_text(encoding="utf-8")
    assert "✅ DONE" in content
    assert "| **W4** | Wiring | Bindings | ✅ DONE |" in content


def test_wave_complete_fractional_wave(tmp_path: Path) -> None:
    plan_file = _make_plan(tmp_path, SAMPLE_WAVE_TABLE)
    ok, msg = update_wave_in_plan(tmp_path, SLUG, wave=1, kind="wave_complete")
    assert ok, msg
    content = plan_file.read_text(encoding="utf-8")
    # W1.5 has wave integer part 1 — should also be flipped
    assert "| W1.5 | Matrix | 1 artifact | ✅ DONE |" in content


def test_wave_complete_already_done_is_noop(tmp_path: Path) -> None:
    content = SAMPLE_WAVE_TABLE.replace(
        "| W0 | Baseline | 4 gates | 🔲 TODO |",
        "| W0 | Baseline | 4 gates | ✅ DONE |",
    )
    plan_file = _make_plan(tmp_path, content)
    ok, msg = update_wave_in_plan(tmp_path, SLUG, wave=0, kind="wave_complete")
    assert ok
    result = plan_file.read_text(encoding="utf-8")
    # Still DONE, no double-flip
    assert "| W0 | Baseline | 4 gates | ✅ DONE |" in result


# ---------------------------------------------------------------------------
# wave_start tests
# ---------------------------------------------------------------------------


def test_wave_start_flips_todo_to_in_progress(tmp_path: Path) -> None:
    plan_file = _make_plan(tmp_path, SAMPLE_WAVE_TABLE)
    ok, msg = update_wave_in_plan(tmp_path, SLUG, wave=0, kind="wave_start")
    assert ok, msg
    content = plan_file.read_text(encoding="utf-8")
    assert "| W0 | Baseline | 4 gates | 🔄 IN PROGRESS |" in content
    assert "| W1 | Discovery | Read-only | 🔲 TODO |" in content


def test_wave_start_does_not_flip_done(tmp_path: Path) -> None:
    content = SAMPLE_WAVE_TABLE.replace(
        "| W0 | Baseline | 4 gates | 🔲 TODO |",
        "| W0 | Baseline | 4 gates | ✅ DONE |",
    )
    plan_file = _make_plan(tmp_path, content)
    ok, msg = update_wave_in_plan(tmp_path, SLUG, wave=0, kind="wave_start")
    assert ok
    result = plan_file.read_text(encoding="utf-8")
    assert "| W0 | Baseline | 4 gates | ✅ DONE |" in result


# ---------------------------------------------------------------------------
# plan_complete tests
# ---------------------------------------------------------------------------


def test_plan_complete_flips_all_remaining(tmp_path: Path) -> None:
    content = SAMPLE_WAVE_TABLE.replace(
        "| W0 | Baseline | 4 gates | 🔲 TODO |",
        "| W0 | Baseline | 4 gates | ✅ DONE |",
    ).replace(
        "| W1 | Discovery | Read-only | 🔲 TODO |",
        "| W1 | Discovery | Read-only | 🔄 IN PROGRESS |",
    )
    plan_file = _make_plan(tmp_path, content)
    ok, msg = update_wave_in_plan(tmp_path, SLUG, wave=-1, kind="plan_complete")
    assert ok, msg
    result = plan_file.read_text(encoding="utf-8")
    assert "🔲 TODO" not in result
    assert "🔄 IN PROGRESS" not in result


# ---------------------------------------------------------------------------
# phase_complete is a no-op
# ---------------------------------------------------------------------------


def test_phase_complete_is_noop(tmp_path: Path) -> None:
    plan_file = _make_plan(tmp_path, SAMPLE_WAVE_TABLE)
    original = plan_file.read_text(encoding="utf-8")
    ok, msg = update_wave_in_plan(tmp_path, SLUG, wave=1, kind="phase_complete")
    assert ok
    assert plan_file.read_text(encoding="utf-8") == original


# ---------------------------------------------------------------------------
# missing plan file
# ---------------------------------------------------------------------------


def test_missing_plan_file_returns_false(tmp_path: Path) -> None:
    plans_dir = tmp_path / "docs" / "archive" / "windsurf" / "legacy-tree" / "plans"
    plans_dir.mkdir(parents=True)
    ok, msg = update_wave_in_plan(tmp_path, SLUG, wave=1, kind="wave_complete")
    assert not ok
    assert "not found" in msg


# ---------------------------------------------------------------------------
# bypass env var
# ---------------------------------------------------------------------------


def test_bypass_env_var(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    plan_file = _make_plan(tmp_path, SAMPLE_WAVE_TABLE)
    monkeypatch.setenv("WAVE_TABLE_UPDATE_BYPASS", "1")
    ok, msg = update_wave_in_plan(tmp_path, SLUG, wave=1, kind="wave_complete")
    assert ok
    assert "bypassed" in msg
    content = plan_file.read_text(encoding="utf-8")
    assert "🔲 TODO" in content  # unchanged


# ---------------------------------------------------------------------------
# Hardened: wave_start edge cases
# ---------------------------------------------------------------------------


def test_wave_start_does_not_flip_in_progress(tmp_path: Path) -> None:
    """wave_start must not re-flip a row already IN PROGRESS."""
    content = SAMPLE_WAVE_TABLE.replace(
        "| W1 | Discovery | Read-only | 🔲 TODO |",
        "| W1 | Discovery | Read-only | 🔄 IN PROGRESS |",
    )
    plan_file = _make_plan(tmp_path, content)
    ok, msg = update_wave_in_plan(tmp_path, SLUG, wave=1, kind="wave_start")
    assert ok
    result = plan_file.read_text(encoding="utf-8")
    assert "| W1 | Discovery | Read-only | 🔄 IN PROGRESS |" in result


def test_wave_start_updates_phase_level_summary_row(tmp_path: Path) -> None:
    """wave_start must also flip the Phase-Level Summary row."""
    plan_file = _make_plan(tmp_path, SAMPLE_WAVE_TABLE)
    ok, msg = update_wave_in_plan(tmp_path, SLUG, wave=1, kind="wave_start")
    assert ok, msg
    content = plan_file.read_text(encoding="utf-8")
    assert "| W1 | Discovery | All source | Touchpoints | ~8K | 🔄 IN PROGRESS |" in content


# ---------------------------------------------------------------------------
# Hardened: wave_complete edge cases
# ---------------------------------------------------------------------------


def test_wave_complete_does_not_flip_blocked(tmp_path: Path) -> None:
    """wave_complete must NOT flip ❌ BLOCKED rows — blocked means manual intervention needed."""
    plan_file = _make_plan(tmp_path, SAMPLE_WITH_BLOCKED)
    ok, msg = update_wave_in_plan(tmp_path, SLUG, wave=2, kind="wave_complete")
    assert ok
    result = plan_file.read_text(encoding="utf-8")
    assert "| W2 | Payload | 2 artifacts | ❌ BLOCKED |" in result


def test_wave_complete_no_match_wave_number(tmp_path: Path) -> None:
    """wave_complete for a wave number not in the table → ok=True, file unchanged."""
    plan_file = _make_plan(tmp_path, SAMPLE_WAVE_TABLE)
    original = plan_file.read_text(encoding="utf-8")
    ok, msg = update_wave_in_plan(tmp_path, SLUG, wave=99, kind="wave_complete")
    assert ok
    assert plan_file.read_text(encoding="utf-8") == original


def test_wave_complete_does_not_bleed_into_adjacent_waves(tmp_path: Path) -> None:
    """W2 complete must not touch W20, W12, W21 if they existed."""
    content = """\
# Adjacent wave test

## Wave Structure

| Wave | Focus | Scope | Status |
|------|-------|-------|--------|
| W2 | Target | Work | 🔲 TODO |
| W20 | Adjacent | Work | 🔲 TODO |
| W12 | Adjacent | Work | 🔲 TODO |
"""
    plan_file = _make_plan(tmp_path, content)
    ok, msg = update_wave_in_plan(tmp_path, SLUG, wave=2, kind="wave_complete")
    assert ok, msg
    result = plan_file.read_text(encoding="utf-8")
    assert "| W2 | Target | Work | ✅ DONE |" in result
    assert "| W20 | Adjacent | Work | 🔲 TODO |" in result
    assert "| W12 | Adjacent | Work | 🔲 TODO |" in result


# ---------------------------------------------------------------------------
# Hardened: plan_complete edge cases
# ---------------------------------------------------------------------------


def test_plan_complete_preserves_done_rows(tmp_path: Path) -> None:
    """plan_complete must not modify rows already ✅ DONE."""
    plan_file = _make_plan(tmp_path, SAMPLE_WITH_BLOCKED)
    ok, msg = update_wave_in_plan(tmp_path, SLUG, wave=-1, kind="plan_complete")
    assert ok, msg
    result = plan_file.read_text(encoding="utf-8")
    assert "| W0 | Baseline | 4 gates | ✅ DONE |" in result


def test_plan_complete_does_not_flip_blocked(tmp_path: Path) -> None:
    """plan_complete must NOT flip ❌ BLOCKED rows."""
    plan_file = _make_plan(tmp_path, SAMPLE_WITH_BLOCKED)
    ok, msg = update_wave_in_plan(tmp_path, SLUG, wave=-1, kind="plan_complete")
    assert ok, msg
    result = plan_file.read_text(encoding="utf-8")
    assert "| W2 | Payload | 2 artifacts | ❌ BLOCKED |" in result


# ---------------------------------------------------------------------------
# Hardened: non-wave rows are never touched
# ---------------------------------------------------------------------------


def test_non_wave_rows_untouched(tmp_path: Path) -> None:
    """Header, divider, and prose lines must never be modified."""
    content = """\
# My Plan

## Wave Structure

| Wave | Focus | Scope | Status |
|------|-------|-------|--------|
| W0 | Baseline | 4 gates | 🔲 TODO |

Some prose mentioning W1 TODO should not be changed.

> Quoted W2 🔲 TODO block should not be changed either.
"""
    plan_file = _make_plan(tmp_path, content)
    ok, msg = update_wave_in_plan(tmp_path, SLUG, wave=0, kind="wave_complete")
    assert ok, msg
    result = plan_file.read_text(encoding="utf-8")
    assert "| Wave | Focus | Scope | Status |" in result  # header row untouched
    assert "|------|-------|-------|--------|" in result  # divider untouched
    assert "Some prose mentioning W1 TODO should not be changed." in result
    assert "> Quoted W2 🔲 TODO block should not be changed either." in result


# ---------------------------------------------------------------------------
# Hardened: CRLF line endings preserved
# ---------------------------------------------------------------------------


def test_crlf_line_endings_preserved(tmp_path: Path) -> None:
    """File with Windows CRLF line endings must not be converted to LF."""
    crlf_content = SAMPLE_WAVE_TABLE.replace("\n", "\r\n")
    plans_dir = tmp_path / "docs" / "archive" / "windsurf" / "legacy-tree" / "plans"
    plans_dir.mkdir(parents=True)
    plan_file = plans_dir / PLAN_FILENAME
    plan_file.write_bytes(crlf_content.encode("utf-8"))

    ok, msg = update_wave_in_plan(tmp_path, SLUG, wave=0, kind="wave_complete")
    assert ok, msg
    raw = plan_file.read_bytes()
    assert b"\r\n" in raw, "CRLF endings must be preserved after update"
    text = plan_file.read_text(encoding="utf-8")
    assert "✅ DONE" in text


# ---------------------------------------------------------------------------
# Hardened: unknown kind is a no-op
# ---------------------------------------------------------------------------


def test_unknown_kind_is_noop(tmp_path: Path) -> None:
    """Any kind not in the known set returns ok=True without touching the file."""
    plan_file = _make_plan(tmp_path, SAMPLE_WAVE_TABLE)
    original = plan_file.read_text(encoding="utf-8")
    ok, msg = update_wave_in_plan(tmp_path, SLUG, wave=1, kind="mystery_kind")
    assert ok
    assert "no-op" in msg
    assert plan_file.read_text(encoding="utf-8") == original


# ---------------------------------------------------------------------------
# Regression: bare 🔲 (without " TODO") must be recognized (RC-1)
# ---------------------------------------------------------------------------

SAMPLE_BARE_TODO = """\
# Test Plan

## Wave Structure

| Wave | Focus | Scope | Status |
|------|-------|-------|--------|
| W0 | Baseline | 4 gates | ✅ DONE |
| W1 | Fix bug | 3 files | ✅ DONE |
| W2 | Stub files | 5 files | ✅ DONE |
| W3 | Update docs | 2 files | 🔲 |
| W4 | Final verify | tests | 🔲 |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W3 | Update docs | `README.md` | None | ~200 | 🔲 |
| W4 | Final verify | test files | None | ~300 | 🔲 |
"""


def test_bare_todo_wave_complete(tmp_path: Path) -> None:
    """wave_complete must flip bare 🔲 (no ' TODO') to ✅ DONE."""
    plan_file = _make_plan(tmp_path, SAMPLE_BARE_TODO)
    ok, msg = update_wave_in_plan(tmp_path, SLUG, wave=3, kind="wave_complete")
    assert ok, msg
    content = plan_file.read_text(encoding="utf-8")
    assert "| W3 | Update docs | 2 files | ✅ DONE |" in content
    assert "| W3 | Update docs | `README.md` | None | ~200 | ✅ DONE |" in content
    # W4 should still be bare 🔲
    assert "| W4 | Final verify | tests | 🔲 |" in content


def test_bare_todo_wave_start(tmp_path: Path) -> None:
    """wave_start must flip bare 🔲 to 🔄 IN PROGRESS."""
    plan_file = _make_plan(tmp_path, SAMPLE_BARE_TODO)
    ok, msg = update_wave_in_plan(tmp_path, SLUG, wave=3, kind="wave_start")
    assert ok, msg
    content = plan_file.read_text(encoding="utf-8")
    assert "| W3 | Update docs | 2 files | 🔄 IN PROGRESS |" in content
    assert "| W3 | Update docs | `README.md` | None | ~200 | 🔄 IN PROGRESS |" in content


def test_bare_todo_plan_complete(tmp_path: Path) -> None:
    """plan_complete must flip all bare 🔲 rows to ✅ DONE."""
    plan_file = _make_plan(tmp_path, SAMPLE_BARE_TODO)
    ok, msg = update_wave_in_plan(tmp_path, SLUG, wave=-1, kind="plan_complete")
    assert ok, msg
    content = plan_file.read_text(encoding="utf-8")
    assert "🔲" not in content
    assert "| W3 | Update docs | 2 files | ✅ DONE |" in content
    assert "| W4 | Final verify | tests | ✅ DONE |" in content


# ---------------------------------------------------------------------------
# Regression: letter-suffix wave labels like W2R (RC-2)
# ---------------------------------------------------------------------------

SAMPLE_LETTER_SUFFIX = """\
# Test Plan

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status |
|------|-----------|-------|-------------|--------|
| W1 | W1.P1 | First wave | ~300 | ✅ DONE |
| W2 | W2.P1 | Second wave | ~2000 | ✅ DONE |
| W2R | W2R.P1 | Regression repair | ~600 | 🔲 TODO |
| W3 | W3.P1 | Documentation | ~200 | 🔲 TODO |
"""


def test_letter_suffix_wave_complete(tmp_path: Path) -> None:
    """wave_complete with wave=2 must also flip W2R row."""
    plan_file = _make_plan(tmp_path, SAMPLE_LETTER_SUFFIX)
    ok, msg = update_wave_in_plan(tmp_path, SLUG, wave=2, kind="wave_complete")
    assert ok, msg
    content = plan_file.read_text(encoding="utf-8")
    assert "| W2R | W2R.P1 | Regression repair | ~600 | ✅ DONE |" in content
    # W3 should be unaffected
    assert "| W3 | W3.P1 | Documentation | ~200 | 🔲 TODO |" in content


def test_letter_suffix_wave_start(tmp_path: Path) -> None:
    """wave_start with wave=2 must also flip W2R row."""
    plan_file = _make_plan(tmp_path, SAMPLE_LETTER_SUFFIX)
    ok, msg = update_wave_in_plan(tmp_path, SLUG, wave=2, kind="wave_start")
    assert ok, msg
    content = plan_file.read_text(encoding="utf-8")
    assert "| W2R | W2R.P1 | Regression repair | ~600 | 🔄 IN PROGRESS |" in content


def test_letter_suffix_bare_todo_combined(tmp_path: Path) -> None:
    """Both defects combined: W2R with bare 🔲 must be recognized."""
    content = SAMPLE_LETTER_SUFFIX.replace(
        "| W2R | W2R.P1 | Regression repair | ~600 | 🔲 TODO |",
        "| W2R | W2R.P1 | Regression repair | ~600 | 🔲 |",
    )
    plan_file = _make_plan(tmp_path, content)
    ok, msg = update_wave_in_plan(tmp_path, SLUG, wave=2, kind="wave_complete")
    assert ok, msg
    result = plan_file.read_text(encoding="utf-8")
    assert "| W2R | W2R.P1 | Regression repair | ~600 | ✅ DONE |" in result


# ---------------------------------------------------------------------------
# Phase-Level Summary Update Tests (W4.P4)
# ---------------------------------------------------------------------------


def _make_plan_with_phase_table(tmp_path: Path, content: str) -> Path:
    """Create a plan file with both Wave Structure and Phase-Level Summary tables."""
    plans_dir = tmp_path / "docs" / "archive" / "windsurf" / "legacy-tree" / "plans"
    plans_dir.mkdir(parents=True, exist_ok=True)
    plan_file = plans_dir / PLAN_FILENAME
    plan_file.write_text(content, encoding="utf-8")
    return plan_file


def test_phase_only_update_works(tmp_path: Path) -> None:
    """Phase-only update: W1.P1 -> ✅ DONE."""
    content = (
        "---\n"
        "plan_id: test-plan-aabbcc\n"
        "last_updated: 2026-05-12T08:00Z\n"
        "---\n\n"
        "## Wave Structure\n\n"
        "| Wave | Phase IDs | Focus | Status |\n"
        "|------|-----------|-------|--------|\n"
        "| W1 | P1 | Phase 1 work | 🔲 TODO |\n\n"
        "## Phase-Level Summary\n\n"
        "| Phase ID | Title | Scope | Est. Tokens | Status |\n"
        "|----------|-------|-------|-------------|--------|\n"
        "| W1.P1 | Test phase | files.py | ~600 | 🔲 TODO |\n"
    )
    plan_file = _make_plan_with_phase_table(tmp_path, content)
    ok, msg = _update_phase_in_plan(tmp_path, SLUG, phase="W1.P1", kind="phase_complete")
    assert ok, msg
    result = plan_file.read_text(encoding="utf-8")
    # Phase row updated
    assert "| W1.P1 | Test phase | files.py | ~600 | ✅ DONE |" in result
    # Wave Structure untouched
    assert "| W1 | P1 | Phase 1 work | 🔲 TODO |" in result


def test_phase_start_flips_todo_to_in_progress(tmp_path: Path) -> None:
    """Phase start: 🔲 TODO -> 🔄 IN PROGRESS."""
    content = (
        "---\n"
        "plan_id: test-plan-aabbcc\n"
        "last_updated: 2026-05-12T08:00Z\n"
        "---\n\n"
        "## Phase-Level Summary\n\n"
        "| Phase ID | Title | Scope | Est. Tokens | Status |\n"
        "|----------|-------|-------|-------------|--------|\n"
        "| W5.P8 | Diagnostics | gap.py | ~800 | 🔲 TODO |\n"
    )
    plan_file = _make_plan_with_phase_table(tmp_path, content)
    ok, msg = _update_phase_in_plan(tmp_path, SLUG, phase="W5.P8", kind="phase_start")
    assert ok, msg
    result = plan_file.read_text(encoding="utf-8")
    assert "| W5.P8 | Diagnostics | gap.py | ~800 | 🔄 IN PROGRESS |" in result


def test_wave_and_phase_update_same_plan(tmp_path: Path) -> None:
    """Wave + phase update in same plan works."""
    content = (
        "---\n"
        "plan_id: test-plan-aabbcc\n"
        "last_updated: 2026-05-12T08:00Z\n"
        "---\n\n"
        "## Wave Structure\n\n"
        "| Wave | Phase IDs | Focus | Status |\n"
        "|------|-----------|-------|--------|\n"
        "| W3 | P5, P6 | Wave 3 work | 🔲 TODO |\n\n"
        "## Phase-Level Summary\n\n"
        "| Phase ID | Title | Scope | Est. Tokens | Status |\n"
        "|----------|-------|-------|-------------|--------|\n"
        "| W3.P5 | Phase 5 | scope.py | ~400 | 🔲 TODO |\n"
        "| W3.P6 | Phase 6 | more.py | ~500 | 🔲 TODO |\n"
    )
    plan_file = _make_plan_with_phase_table(tmp_path, content)
    
    # Update wave first
    ok, msg = update_wave_in_plan(tmp_path, SLUG, wave=3, kind="wave_complete")
    assert ok, msg
    
    # Update phase
    ok, msg = _update_phase_in_plan(tmp_path, SLUG, phase="W3.P5", kind="phase_complete")
    assert ok, msg
    
    result = plan_file.read_text(encoding="utf-8")
    # Wave updated
    assert "| W3 | P5, P6 | Wave 3 work | ✅ DONE |" in result
    # Phase updated
    assert "| W3.P5 | Phase 5 | scope.py | ~400 | ✅ DONE |" in result
    # Other phase untouched
    assert "| W3.P6 | Phase 6 | more.py | ~500 | 🔲 TODO |" in result


def test_missing_phase_returns_noop_message(tmp_path: Path) -> None:
    """Missing phase is no-op with clear message (following existing updater pattern)."""
    content = (
        "---\n"
        "plan_id: test-plan-aabbcc\n"
        "last_updated: 2026-05-12T08:00Z\n"
        "---\n\n"
        "## Phase-Level Summary\n\n"
        "| Phase ID | Title | Scope | Est. Tokens | Status |\n"
        "|----------|-------|-------|-------------|--------|\n"
        "| W1.P1 | Test | file.py | ~600 | 🔲 TODO |\n"
    )
    _make_plan_with_phase_table(tmp_path, content)
    ok, msg = _update_phase_in_plan(tmp_path, SLUG, phase="W99.P99", kind="phase_complete")
    # Returns True (not an error) with informative message
    assert ok is True
    assert "no matching rows found/changed" in msg
    assert "phase=W99.P99" in msg


def test_phase_update_refreshes_last_updated(tmp_path: Path) -> None:
    """last_updated in frontmatter refreshes when phase status changes."""
    old_timestamp = "2026-05-12T08:00Z"
    content = (
        f"---\n"
        f"plan_id: test-plan-aabbcc\n"
        f"last_updated: {old_timestamp}\n"
        f"---\n\n"
        f"## Phase-Level Summary\n\n"
        f"| Phase ID | Title | Scope | Est. Tokens | Status |\n"
        f"|----------|-------|-------|-------------|--------|\n"
        f"| W10.P12 | Big phase | many.py | ~1000 | 🔲 TODO |\n"
    )
    plan_file = _make_plan_with_phase_table(tmp_path, content)
    ok, msg = _update_phase_in_plan(tmp_path, SLUG, phase="W10.P12", kind="phase_complete")
    assert ok, msg
    result = plan_file.read_text(encoding="utf-8")
    # Old timestamp replaced with new one
    assert old_timestamp not in result
    # New timestamp format present (ISO 8601 UTC)
    assert re.search(r"last_updated:\s*\d{4}-\d{2}-\d{2}T\d{2}:\d{2}Z", result)


def test_unrelated_tables_untouched(tmp_path: Path) -> None:
    """Unrelated markdown tables are untouched during phase update."""
    content = (
        "---\n"
        "plan_id: test-plan-aabbcc\n"
        "last_updated: 2026-05-12T08:00Z\n"
        "---\n\n"
        "## Gap Register\n\n"
        "| ID | Description | Severity | Status |\n"
        "|----|-------------|----------|--------|\n"
        "| GAP-1 | Some gap | High | 🔲 TODO |\n\n"
        "## Phase-Level Summary\n\n"
        "| Phase ID | Title | Scope | Est. Tokens | Status |\n"
        "|----------|-------|-------|-------------|--------|\n"
        "| W1.P1 | Test | file.py | ~600 | 🔲 TODO |\n\n"
        "## Definition of Done\n\n"
        "| ID | Criterion | Status |\n"
        "|----|-----------|--------|\n"
        "| DoD-1 | Test passes | 🔲 TODO |\n"
    )
    plan_file = _make_plan_with_phase_table(tmp_path, content)
    ok, msg = _update_phase_in_plan(tmp_path, SLUG, phase="W1.P1", kind="phase_complete")
    assert ok, msg
    result = plan_file.read_text(encoding="utf-8")
    # Phase row updated
    assert "| W1.P1 | Test | file.py | ~600 | ✅ DONE |" in result
    # Gap Register untouched
    assert "| GAP-1 | Some gap | High | 🔲 TODO |" in result
    # DoD table untouched
    assert "| DoD-1 | Test passes | 🔲 TODO |" in result


def test_phase_complete_from_in_progress(tmp_path: Path) -> None:
    """Phase complete: 🔄 IN PROGRESS -> ✅ DONE."""
    content = (
        "---\n"
        "plan_id: test-plan-aabbcc\n"
        "last_updated: 2026-05-12T08:00Z\n"
        "---\n\n"
        "## Phase-Level Summary\n\n"
        "| Phase ID | Title | Scope | Est. Tokens | Status |\n"
        "|----------|-------|-------|-------------|--------|\n"
        "| W5.P8 | Diagnostics | gap.py | ~800 | 🔄 IN PROGRESS |\n"
    )
    plan_file = _make_plan_with_phase_table(tmp_path, content)
    ok, msg = _update_phase_in_plan(tmp_path, SLUG, phase="W5.P8", kind="phase_complete")
    assert ok, msg
    result = plan_file.read_text(encoding="utf-8")
    assert "| W5.P8 | Diagnostics | gap.py | ~800 | ✅ DONE |" in result


def test_blocked_phase_not_flipped(tmp_path: Path) -> None:
    """❌ BLOCKED phases are not flipped by phase_complete."""
    content = (
        "---\n"
        "plan_id: test-plan-aabbcc\n"
        "last_updated: 2026-05-12T08:00Z\n"
        "---\n\n"
        "## Phase-Level Summary\n\n"
        "| Phase ID | Title | Scope | Est. Tokens | Status |\n"
        "|----------|-------|-------|-------------|--------|\n"
        "| W1.P1 | Test | file.py | ~600 | ❌ BLOCKED |\n"
    )
    plan_file = _make_plan_with_phase_table(tmp_path, content)
    ok, msg = _update_phase_in_plan(tmp_path, SLUG, phase="W1.P1", kind="phase_complete")
    # No rows changed but returns success
    assert ok is True
    assert "no matching rows found/changed" in msg
    result = plan_file.read_text(encoding="utf-8")
    # BLOCKED status preserved
    assert "| W1.P1 | Test | file.py | ~600 | ❌ BLOCKED |" in result


# ===========================================================================
# NEW TESTS — plan-update-enforcement-template-fix-e7a3c1
# ===========================================================================

# ---------------------------------------------------------------------------
# Slug resolution: no trailing 6-hex suffix
# ---------------------------------------------------------------------------

SLUG_NO_HEX = "apps-rg-master-governed-runtime-hardening"


def test_find_plan_file_exact_match(tmp_path: Path) -> None:
    """_find_plan_file resolves exact-match slugs (canonical case)."""
    plans_dir = tmp_path / "docs" / "archive" / "windsurf" / "legacy-tree" / "plans"
    plans_dir.mkdir(parents=True)
    plan_file = plans_dir / f"{SLUG_NO_HEX}.md"
    plan_file.write_text("# plan", encoding="utf-8")
    found = _find_plan_file(tmp_path, SLUG_NO_HEX)
    assert found == plan_file


def test_find_plan_file_no_hex_suffix_exact(tmp_path: Path) -> None:
    """Slug without trailing 6-char hex suffix resolves if file name matches exactly."""
    slug = "my-long-plan-name-without-hex"
    plans_dir = tmp_path / "docs" / "archive" / "windsurf" / "legacy-tree" / "plans"
    plans_dir.mkdir(parents=True)
    (plans_dir / f"{slug}.md").write_text("# plan", encoding="utf-8")
    assert _find_plan_file(tmp_path, slug) is not None


# ---------------------------------------------------------------------------
# Slug resolution: numeric-prefixed filename
# ---------------------------------------------------------------------------


def test_find_plan_file_numeric_prefix_underscore(tmp_path: Path) -> None:
    """01_<slug>.md resolves when slug=<slug> (no numeric prefix)."""
    slug = "apps-rg-master-governed-runtime-hardening"
    plans_dir = tmp_path / "docs" / "archive" / "windsurf" / "legacy-tree" / "plans"
    plans_dir.mkdir(parents=True)
    (plans_dir / f"01_{slug}.md").write_text("# plan", encoding="utf-8")
    found = _find_plan_file(tmp_path, slug)
    assert found is not None
    assert found.name == f"01_{slug}.md"


def test_find_plan_file_numeric_prefix_dash(tmp_path: Path) -> None:
    """02-<slug>.md resolves when slug=<slug>."""
    slug = "some-plan-abc123"
    plans_dir = tmp_path / "docs" / "archive" / "windsurf" / "legacy-tree" / "plans"
    plans_dir.mkdir(parents=True)
    (plans_dir / f"02-{slug}.md").write_text("# plan", encoding="utf-8")
    found = _find_plan_file(tmp_path, slug)
    assert found is not None
    assert found.name == f"02-{slug}.md"


# ---------------------------------------------------------------------------
# Slug resolution: frontmatter plan_id
# ---------------------------------------------------------------------------


def test_find_plan_file_frontmatter_plan_id(tmp_path: Path) -> None:
    """File with plan_id: <slug> in frontmatter resolves even if filename differs."""
    slug = "custom-slug-no-hex"
    plans_dir = tmp_path / "docs" / "archive" / "windsurf" / "legacy-tree" / "plans"
    plans_dir.mkdir(parents=True)
    content = "---\nplan_id: custom-slug-no-hex\n---\n# plan"
    (plans_dir / "01_different-filename.md").write_text(content, encoding="utf-8")
    found = _find_plan_file(tmp_path, slug)
    assert found is not None
    assert found.name == "01_different-filename.md"


def test_find_plan_file_missing_returns_none(tmp_path: Path) -> None:
    """Returns None when no plan file can be resolved for the slug."""
    plans_dir = tmp_path / "docs" / "archive" / "windsurf" / "legacy-tree" / "plans"
    plans_dir.mkdir(parents=True)
    assert _find_plan_file(tmp_path, "no-such-plan-xyz") is None


# ---------------------------------------------------------------------------
# S-series phase row update
# ---------------------------------------------------------------------------

SAMPLE_S_SERIES_PHASES = (
    "---\n"
    "plan_id: test-plan-aabbcc\n"
    "last_updated: 2026-05-01T10:00Z\n"
    "---\n\n"
    "## Phase Progress\n\n"
    "| Phase | Title | Status |\n"
    "|-------|-------|--------|\n"
    "| S0 | Fast Runtime Path Inventory | 🔲 TODO |\n"
    "| S0.5 | Cache Safety Guard | 🔲 TODO |\n"
    "| S1 | Structured Resume Schema | 🔄 IN PROGRESS |\n"
    "| S9 | Closeout | 🔲 TODO |\n"
)


def test_s_series_phase_complete_flips_todo(tmp_path: Path) -> None:
    """S0 phase row flips from 🔲 TODO to ✅ DONE via phase_complete."""
    plan_file = _make_plan_with_phase_table(tmp_path, SAMPLE_S_SERIES_PHASES)
    ok, msg = _update_phase_in_plan(tmp_path, SLUG, phase="S0", kind="phase_complete")
    assert ok, msg
    result = plan_file.read_text(encoding="utf-8")
    assert "| S0 | Fast Runtime Path Inventory | ✅ DONE |" in result
    assert "| S0.5 | Cache Safety Guard | 🔲 TODO |" in result  # unaffected


def test_s_series_decimal_phase_complete(tmp_path: Path) -> None:
    """S0.5 phase row (decimal suffix) flips to ✅ DONE."""
    plan_file = _make_plan_with_phase_table(tmp_path, SAMPLE_S_SERIES_PHASES)
    ok, msg = _update_phase_in_plan(tmp_path, SLUG, phase="S0.5", kind="phase_complete")
    assert ok, msg
    result = plan_file.read_text(encoding="utf-8")
    assert "| S0.5 | Cache Safety Guard | ✅ DONE |" in result


def test_s_series_in_progress_phase_complete(tmp_path: Path) -> None:
    """S1 in 🔄 IN PROGRESS flips to ✅ DONE via phase_complete."""
    plan_file = _make_plan_with_phase_table(tmp_path, SAMPLE_S_SERIES_PHASES)
    ok, msg = _update_phase_in_plan(tmp_path, SLUG, phase="S1", kind="phase_complete")
    assert ok, msg
    result = plan_file.read_text(encoding="utf-8")
    assert "| S1 | Structured Resume Schema | ✅ DONE |" in result


def test_s_series_last_phase(tmp_path: Path) -> None:
    """S9 (high single-digit) resolves and flips correctly."""
    plan_file = _make_plan_with_phase_table(tmp_path, SAMPLE_S_SERIES_PHASES)
    ok, msg = _update_phase_in_plan(tmp_path, SLUG, phase="S9", kind="phase_complete")
    assert ok, msg
    result = plan_file.read_text(encoding="utf-8")
    assert "| S9 | Closeout | ✅ DONE |" in result


# ---------------------------------------------------------------------------
# Note-column: fill empty / dash / em-dash placeholders
# ---------------------------------------------------------------------------

SAMPLE_NOTE_TABLE = (
    "---\nplan_id: test-plan-aabbcc\n---\n\n"
    "## Wave Progress\n\n"
    "| Wave | Focus | Status | Tests Added | Files Changed |\n"
    "|------|-------|--------|-------------|---------------|\n"
    "| W1 | Slug fixes | ✅ DONE | — | — |\n"
    "| W2 | Template | 🔲 TODO | — | — |\n"
    "| W3 | Hook | 🔲 TODO | — | — |\n"
)


def test_note_column_fills_em_dash(tmp_path: Path) -> None:
    """note='+8 tests, 3 files' fills '—' cells in W1 row."""
    plan_file = _make_plan_with_phase_table(tmp_path, SAMPLE_NOTE_TABLE)
    ok, msg = update_wave_note_columns(tmp_path, SLUG, wave=1, note="+8 tests, 3 files")
    assert ok, msg
    result = plan_file.read_text(encoding="utf-8")
    assert "| W1 | Slug fixes | ✅ DONE | 8 | 3 |" in result
    # Other rows untouched
    assert "| W2 | Template | 🔲 TODO | — | — |" in result


def test_note_column_fills_plain_dash(tmp_path: Path) -> None:
    """Cells containing literal '-' (ASCII dash) are treated as placeholder."""
    content = SAMPLE_NOTE_TABLE.replace("| W1 | Slug fixes | ✅ DONE | — | — |",
                                        "| W1 | Slug fixes | ✅ DONE | - | - |")
    plan_file = _make_plan_with_phase_table(tmp_path, content)
    ok, msg = update_wave_note_columns(tmp_path, SLUG, wave=1, note="+5 tests, 2 files")
    assert ok, msg
    result = plan_file.read_text(encoding="utf-8")
    assert "| W1 | Slug fixes | ✅ DONE | 5 | 2 |" in result


def test_note_column_fills_empty_cell(tmp_path: Path) -> None:
    """Empty cells (whitespace only) are treated as placeholder."""
    content = SAMPLE_NOTE_TABLE.replace("| W1 | Slug fixes | ✅ DONE | — | — |",
                                        "| W1 | Slug fixes | ✅ DONE |  |  |")
    plan_file = _make_plan_with_phase_table(tmp_path, content)
    ok, msg = update_wave_note_columns(tmp_path, SLUG, wave=1, note="+3 tests, 1 file")
    assert ok, msg
    result = plan_file.read_text(encoding="utf-8")
    assert "3" in result and "1" in result


# ---------------------------------------------------------------------------
# Note-column: overwrite numeric cells with explicit new value
# ---------------------------------------------------------------------------


def test_note_column_overwrites_existing_numeric(tmp_path: Path) -> None:
    """If cell already has numeric value, a new explicit marker overwrites it."""
    content = SAMPLE_NOTE_TABLE.replace("| W1 | Slug fixes | ✅ DONE | — | — |",
                                        "| W1 | Slug fixes | ✅ DONE | 5 | 3 |")
    plan_file = _make_plan_with_phase_table(tmp_path, content)
    ok, msg = update_wave_note_columns(tmp_path, SLUG, wave=1, note="+12 tests, 4 files")
    assert ok, msg
    result = plan_file.read_text(encoding="utf-8")
    assert "| W1 | Slug fixes | ✅ DONE | 12 | 4 |" in result


# ---------------------------------------------------------------------------
# Note-column: preserve nonnumeric manual text and warn
# ---------------------------------------------------------------------------


def test_note_column_preserves_nonnumeric_manual_text(tmp_path: Path, capsys) -> None:
    """Nonnumeric manual text ('infra only') is preserved; WARN emitted to stderr."""
    content = SAMPLE_NOTE_TABLE.replace("| W1 | Slug fixes | ✅ DONE | — | — |",
                                        "| W1 | Slug fixes | ✅ DONE | infra only | — |")
    plan_file = _make_plan_with_phase_table(tmp_path, content)
    ok, msg = update_wave_note_columns(tmp_path, SLUG, wave=1, note="+8 tests, 3 files")
    assert ok, msg
    result = plan_file.read_text(encoding="utf-8")
    # nonnumeric text preserved
    assert "infra only" in result
    # Files Changed filled (it was —)
    assert "| W1 | Slug fixes | ✅ DONE | infra only | 3 |" in result
    # Warning emitted to stderr
    captured = capsys.readouterr()
    assert "nonnumeric manual text" in captured.err
    assert "infra only" in captured.err


# ---------------------------------------------------------------------------
# Note-column: invalid/prose note does not modify cells
# ---------------------------------------------------------------------------


def test_note_column_invalid_prose_leaves_cells_unchanged(tmp_path: Path) -> None:
    """A note with no parseable +N tests / N files pattern leaves cells unchanged."""
    plan_file = _make_plan_with_phase_table(tmp_path, SAMPLE_NOTE_TABLE)
    original = plan_file.read_text(encoding="utf-8")
    ok, msg = update_wave_note_columns(tmp_path, SLUG, wave=1, note="scope=summary-signal")
    assert ok, msg
    assert "no test/file counts found" in msg
    assert plan_file.read_text(encoding="utf-8") == original


def test_note_column_empty_note_is_noop(tmp_path: Path) -> None:
    """Empty note string → no-op, file unchanged."""
    plan_file = _make_plan_with_phase_table(tmp_path, SAMPLE_NOTE_TABLE)
    original = plan_file.read_text(encoding="utf-8")
    ok, msg = update_wave_note_columns(tmp_path, SLUG, wave=1, note="")
    assert ok, msg
    assert plan_file.read_text(encoding="utf-8") == original


# ---------------------------------------------------------------------------
# Idempotency: same marker run twice
# ---------------------------------------------------------------------------


def test_wave_complete_idempotent(tmp_path: Path) -> None:
    """Running wave_complete twice on the same wave is idempotent."""
    plan_file = _make_plan(tmp_path, SAMPLE_WAVE_TABLE)
    ok1, _ = update_wave_in_plan(tmp_path, SLUG, wave=1, kind="wave_complete")
    content_after_first = plan_file.read_text(encoding="utf-8")
    ok2, _ = update_wave_in_plan(tmp_path, SLUG, wave=1, kind="wave_complete")
    content_after_second = plan_file.read_text(encoding="utf-8")
    assert ok1 and ok2
    # Status cell identical after both runs (only last_updated may differ)
    assert "| W1 | Discovery | Read-only | ✅ DONE |" in content_after_first
    assert "| W1 | Discovery | Read-only | ✅ DONE |" in content_after_second


def test_phase_complete_idempotent(tmp_path: Path) -> None:
    """Running phase_complete twice on the same phase is idempotent."""
    content = (
        "---\nplan_id: test-plan-aabbcc\nlast_updated: 2026-05-01T00:00Z\n---\n\n"
        "## Phase-Level Summary\n\n"
        "| Phase ID | Title | Scope | Est. Tokens | Status |\n"
        "|----------|-------|-------|-------------|--------|\n"
        "| W2.P3 | Some phase | file.py | ~400 | 🔲 TODO |\n"
    )
    plan_file = _make_plan_with_phase_table(tmp_path, content)
    ok1, _ = _update_phase_in_plan(tmp_path, SLUG, phase="W2.P3", kind="phase_complete")
    result1 = plan_file.read_text(encoding="utf-8")
    ok2, _ = _update_phase_in_plan(tmp_path, SLUG, phase="W2.P3", kind="phase_complete")
    result2 = plan_file.read_text(encoding="utf-8")
    assert ok1 and ok2
    assert "| W2.P3 | Some phase | file.py | ~400 | ✅ DONE |" in result1
    assert "| W2.P3 | Some phase | file.py | ~400 | ✅ DONE |" in result2


def test_note_column_idempotent(tmp_path: Path) -> None:
    """Running update_wave_note_columns twice with same note is idempotent."""
    plan_file = _make_plan_with_phase_table(tmp_path, SAMPLE_NOTE_TABLE)
    ok1, _ = update_wave_note_columns(tmp_path, SLUG, wave=1, note="+8 tests, 3 files")
    result1 = plan_file.read_text(encoding="utf-8")
    ok2, _ = update_wave_note_columns(tmp_path, SLUG, wave=1, note="+8 tests, 3 files")
    result2 = plan_file.read_text(encoding="utf-8")
    assert ok1 and ok2
    # Both runs produce the same cell values
    assert "| W1 | Slug fixes | ✅ DONE | 8 | 3 |" in result1
    assert "| W1 | Slug fixes | ✅ DONE | 8 | 3 |" in result2


# ---------------------------------------------------------------------------
# Unresolvable slug: update_wave_note_columns returns False, not raises
# ---------------------------------------------------------------------------


def test_note_columns_missing_plan_returns_false(tmp_path: Path) -> None:
    """update_wave_note_columns returns (False, msg) when plan file not found."""
    plans_dir = tmp_path / "docs" / "archive" / "windsurf" / "legacy-tree" / "plans"
    plans_dir.mkdir(parents=True)
    ok, msg = update_wave_note_columns(tmp_path, SLUG, wave=1, note="+5 tests, 2 files")
    assert ok is False
    assert "not found" in msg


# ---------------------------------------------------------------------------
# Hook: _warn_unresolvable_slugs emits WARN to stderr and logs event
# ---------------------------------------------------------------------------


def test_warn_unresolvable_slug_emits_stderr(tmp_path: Path, capsys) -> None:
    """_warn_unresolvable_slugs writes a WARN line to stderr for unknown slugs."""
    import importlib.util
    import io
    import sys

    REPO_ROOT_LOCAL = Path(__file__).resolve().parents[3]
    hook_path = REPO_ROOT_LOCAL / ".claude" / "governance/scripts" / "_legacy_windsurf" / "post_cursor_agent_wave_lifecycle_capture.py"
    spec = importlib.util.spec_from_file_location("_wlc_warn_test", hook_path)
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]

    # Build a minimal marker dataclass-like object
    from tools.notion._wave_lifecycle_helpers import WaveLifecycleMarker
    marker = WaveLifecycleMarker(kind="wave_complete", slug="no-such-plan-xyz", wave=1)

    # Override REPO_ROOT inside the module to point at tmp_path so no real file is found
    orig = mod.REPO_ROOT
    mod.REPO_ROOT = tmp_path
    plans_dir = tmp_path / "docs" / "archive" / "windsurf" / "legacy-tree" / "plans"
    plans_dir.mkdir(parents=True)
    try:
        mod._warn_unresolvable_slugs([marker])
    finally:
        mod.REPO_ROOT = orig

    captured = capsys.readouterr()
    assert "WARN" in captured.err
    assert "no-such-plan-xyz" in captured.err
    assert "wave_complete" in captured.err
