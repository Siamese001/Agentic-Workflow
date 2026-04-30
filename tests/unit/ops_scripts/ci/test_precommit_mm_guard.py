"""Unit tests for ``ops_scripts/ci/precommit_mm_guard.py`` (W4 P4.1).

Plan: ``.windsurf/plans/adg-three-bucket-unified-c4f8e2.md`` (W4 P4.1).

The guard parses ``git status --porcelain`` and exits non-zero when any file
is staged AND has unstaged modifications (the "MM dual-state" trap that
causes silent commit rollback under pre-commit's stash/restore flow).
"""

from __future__ import annotations

# Inventory mode: tests verify CLI behavior, do not consume ADG views.
__adg_consumer_mode__ = "inventory"

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci.precommit_mm_guard import (  # noqa: E402
    INDEX_STAGED_CODES,
    WORKTREE_DIRTY_CODES,
    find_dual_state,
    format_violation_message,
    main,
    parse_porcelain,
)


# ---------------------------------------------------------------------------
# parse_porcelain
# ---------------------------------------------------------------------------


def test_parse_porcelain_empty() -> None:
    assert parse_porcelain("") == []


def test_parse_porcelain_clean_modified() -> None:
    """Pure index-modified (`M ` worktree clean) parses fine."""
    rows = parse_porcelain("M  agentic_core/x.py\n")
    assert rows == [("M", " ", "agentic_core/x.py")]


def test_parse_porcelain_pure_unstaged() -> None:
    """Pure worktree-modified (` M`) parses fine."""
    rows = parse_porcelain(" M agentic_core/x.py\n")
    assert rows == [(" ", "M", "agentic_core/x.py")]


def test_parse_porcelain_dual_mm() -> None:
    """MM dual-state parses both columns."""
    rows = parse_porcelain("MM agentic_core/x.py\n")
    assert rows == [("M", "M", "agentic_core/x.py")]


def test_parse_porcelain_skips_untracked() -> None:
    """Untracked (??) files are skipped — they cannot trigger the trap."""
    rows = parse_porcelain("?? new_file.py\n")
    assert rows == []


def test_parse_porcelain_skips_ignored() -> None:
    """Ignored (!!) files are skipped."""
    rows = parse_porcelain("!! .venv/lib/site-packages/x.py\n")
    assert rows == []


def test_parse_porcelain_handles_rename() -> None:
    """`R  old -> new` reports the destination path."""
    rows = parse_porcelain("R  old/path.py -> new/path.py\n")
    assert rows == [("R", " ", "new/path.py")]


def test_parse_porcelain_multiple_lines() -> None:
    text = (
        "M  agentic_core/a.py\n"
        " M agentic_core/b.py\n"
        "MM agentic_core/c.py\n"
        "?? agentic_core/d.py\n"
        "AM agentic_core/e.py\n"
    )
    rows = parse_porcelain(text)
    assert rows == [
        ("M", " ", "agentic_core/a.py"),
        (" ", "M", "agentic_core/b.py"),
        ("M", "M", "agentic_core/c.py"),
        ("A", "M", "agentic_core/e.py"),
    ]


# ---------------------------------------------------------------------------
# find_dual_state
# ---------------------------------------------------------------------------


def test_find_dual_state_mm() -> None:
    rows = [("M", "M", "x.py")]
    assert find_dual_state(rows) == [("M", "M", "x.py")]


def test_find_dual_state_am() -> None:
    """Added+modified — staged add with later worktree modifications."""
    rows = [("A", "M", "new.py")]
    assert find_dual_state(rows) == [("A", "M", "new.py")]


def test_find_dual_state_md() -> None:
    """Modified+deleted — staged modify, then worktree deletion."""
    rows = [("M", "D", "deleted.py")]
    assert find_dual_state(rows) == [("M", "D", "deleted.py")]


def test_find_dual_state_clean_staged_only() -> None:
    """`M ` (staged only, clean worktree) is NOT a violation."""
    rows = [("M", " ", "x.py")]
    assert find_dual_state(rows) == []


def test_find_dual_state_clean_unstaged_only() -> None:
    """` M` (worktree only, nothing staged) is NOT a violation."""
    rows = [(" ", "M", "x.py")]
    assert find_dual_state(rows) == []


def test_find_dual_state_multiple_mixed() -> None:
    rows = [
        ("M", " ", "clean_staged.py"),
        (" ", "M", "clean_unstaged.py"),
        ("M", "M", "dual_a.py"),
        ("A", "M", "dual_b.py"),
        ("M", "D", "dual_c.py"),
    ]
    found = find_dual_state(rows)
    assert {p for (_, _, p) in found} == {
        "dual_a.py",
        "dual_b.py",
        "dual_c.py",
    }


def test_find_dual_state_empty_input() -> None:
    assert find_dual_state([]) == []


# ---------------------------------------------------------------------------
# Status-code constants (regression guard against future weakening)
# ---------------------------------------------------------------------------


def test_index_codes_cover_canonical_staged_states() -> None:
    """The constant must cover M, A, D, R, C per git status --porcelain spec."""
    assert {"M", "A", "D", "R", "C"} <= INDEX_STAGED_CODES


def test_worktree_codes_include_modified_and_deleted() -> None:
    assert {"M", "D"} <= WORKTREE_DIRTY_CODES


# ---------------------------------------------------------------------------
# format_violation_message
# ---------------------------------------------------------------------------


def test_violation_message_lists_paths() -> None:
    msg = format_violation_message([("M", "M", "agentic_core/x.py")])
    assert "agentic_core/x.py" in msg
    assert "MM" in msg
    assert "git add" in msg
    assert "git stash" in msg
    assert "PRECOMMIT_MM_GUARD_BYPASS=1" in msg
    assert "Everything up-to-date" in msg  # explains the user-visible symptom


# ---------------------------------------------------------------------------
# main() CLI integration
# ---------------------------------------------------------------------------


def test_main_clean_status_returns_zero() -> None:
    rc = main(["--status-text", "M  agentic_core/x.py"])
    assert rc == 0


def test_main_dual_state_returns_one(capsys) -> None:
    rc = main(["--status-text", "MM agentic_core/x.py"])
    assert rc == 1
    captured = capsys.readouterr()
    assert "COMMIT BLOCKED" in captured.err
    assert "agentic_core/x.py" in captured.err


def test_main_empty_status_returns_zero() -> None:
    """No staged changes means pre-commit isn't doing anything dangerous."""
    rc = main(["--status-text", ""])
    assert rc == 0


def test_main_bypass_env_returns_zero(monkeypatch, capsys) -> None:
    monkeypatch.setenv("PRECOMMIT_MM_GUARD_BYPASS", "1")
    rc = main(["--status-text", "MM agentic_core/x.py"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "BYPASS active" in captured.err


def test_main_multiple_violations_listed(capsys) -> None:
    text = "MM file_a.py\nAM file_b.py\nMD file_c.py\n"
    rc = main(["--status-text", text])
    assert rc == 1
    captured = capsys.readouterr()
    for path in ("file_a.py", "file_b.py", "file_c.py"):
        assert path in captured.err


def test_main_pure_staged_passes() -> None:
    """A normal `git add file && git commit` flow must not be blocked."""
    text = "M  agentic_core/x.py\nA  new_file.py\n"
    assert main(["--status-text", text]) == 0
