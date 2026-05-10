"""
tests/unit/windsurf_scripts/test_plan_wave_table_updater.py

Unit tests for tools/windsurf/_plan_wave_table_updater.py.

Tests are pure-Python: they write temp plan files and assert the on-disk
content after calling update_wave_in_plan.
"""
from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))

from tools.windsurf._plan_wave_table_updater import (  # noqa: E402
    STATUS_DONE,
    STATUS_IN_PROGRESS,
    STATUS_TODO,
    update_wave_in_plan,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SLUG = "test-plan-aabbcc"
PLAN_FILENAME = f"{SLUG}.md"


def _make_plan(tmp_path: Path, content: str) -> Path:
    """Write a plan .md file under .windsurf/plans/ inside tmp_path."""
    plans_dir = tmp_path / ".windsurf" / "plans"
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
    plans_dir = tmp_path / ".windsurf" / "plans"
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
    plans_dir = tmp_path / ".windsurf" / "plans"
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
