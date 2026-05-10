"""
Unit tests for tools/notion/backfill_historical_plan_statuses.py.

Regression coverage for RCA NOTION_PLANS_STATUS_RCA_2026-05-10 Cause A:
the function previously defaulted to "Not Started" when no on-disk ground
truth was present, causing a bulk overwrite of 89+ rows. The fix returns
None for missing ground truth so callers skip the row.

Plan: notion-plans-status-rca-followups-b8e3f2 (W1.P1)
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = REPO_ROOT / "tools" / "notion" / "backfill_historical_plan_statuses.py"


def _load_module():
    """Import backfill_historical_plan_statuses without running CLI."""
    spec = importlib.util.spec_from_file_location(
        "backfill_historical_plan_statuses", MODULE_PATH
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("backfill_historical_plan_statuses", mod)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mod():
    return _load_module()


# -------------------------------------------------------------------
# RCA REGRESSION: no ground truth -> None (must NOT default to Not Started)
# -------------------------------------------------------------------


def test_no_status_metadata_returns_none(mod):
    """RCA Cause A: bare title-only plan must NOT infer Not Started."""
    md = "# My Plan\n\nThis plan has no status metadata anywhere.\n"
    assert mod._extract_status_from_plan(md) is None


def test_empty_string_returns_none(mod):
    assert mod._extract_status_from_plan("") is None


def test_only_body_text_returns_none(mod):
    md = "Some prose. Some more prose.\n\nWith waves and phases mentioned.\n"
    assert mod._extract_status_from_plan(md) is None


# -------------------------------------------------------------------
# Positive cases: each detection branch returns the right canonical
# -------------------------------------------------------------------


@pytest.mark.parametrize(
    ("frontmatter_value", "expected"),
    [
        ("Not Started", "Not Started"),
        ("In Progress", "In Progress"),
        ("Completed", "Completed"),
        ("Retired", "Retired"),
        ("Archived", "Archived"),
        ("Deferred", "Deferred"),
        ("Waiting", "Waiting"),
        # Legacy mappings
        ("Live", "In Progress"),
        ("Draft", "Not Started"),
        ("Done", "Completed"),
        ("Superseded", "Retired"),
        ("Deprioritized", "Deferred"),
        # Quoted variants
        ('"Completed"', "Completed"),
        ("'Retired'", "Retired"),
    ],
)
def test_frontmatter_status_detection(mod, frontmatter_value, expected):
    md = f"---\nstatus: {frontmatter_value}\ntitle: Foo\n---\n\n# Body\n"
    assert mod._extract_status_from_plan(md) == expected


def test_bold_status_metadata(mod):
    md = "# Plan\n\n**Status**: In Progress\n\nMore content.\n"
    assert mod._extract_status_from_plan(md) == "In Progress"


def test_plain_status_line(mod):
    md = "# Plan\n\nStatus: Completed\n\nDetails follow.\n"
    assert mod._extract_status_from_plan(md) == "Completed"


def test_superseded_marker(mod):
    md = "# Plan\n\nThis was SUPERSEDED by foo-abc123.\n"
    assert mod._extract_status_from_plan(md) == "Retired"


# -------------------------------------------------------------------
# Frontmatter takes precedence over later branches
# -------------------------------------------------------------------


def test_frontmatter_wins_over_bold(mod):
    md = "---\nstatus: Completed\n---\n\n**Status**: Not Started\n"
    assert mod._extract_status_from_plan(md) == "Completed"


def test_superseded_only_when_no_explicit_status(mod):
    """Explicit status beats SUPERSEDED token in body."""
    md = "---\nstatus: In Progress\n---\n\n# Plan\n\nNotes about SUPERSEDED items.\n"
    assert mod._extract_status_from_plan(md) == "In Progress"


# -------------------------------------------------------------------
# Drift-detection integration: rows with no ground truth must be skipped
# -------------------------------------------------------------------


def test_main_skips_rows_without_disk_status(mod, tmp_path, monkeypatch, capsys):
    """End-to-end: ensure main()'s drift loop does not include None-status rows."""
    plans_dir = tmp_path / "plans"
    plans_dir.mkdir()
    # Plan A: has frontmatter status -> drift candidate
    (plans_dir / "plan-a-aaaaaa.md").write_text(
        "---\nstatus: Completed\n---\n# A\n", encoding="utf-8"
    )
    # Plan B: NO status metadata -> must be skipped, not patched
    (plans_dir / "plan-b-bbbbbb.md").write_text("# B\n\nNo metadata.\n", encoding="utf-8")

    monkeypatch.setattr(mod, "PLANS_DIR", plans_dir)
    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)

    fake_pages = [
        {
            "id": "page-a",
            "properties": {
                "Slug": {"title": [{"plain_text": "plan-a-aaaaaa"}]},
                "Status": {"select": {"name": "Not Started"}},
                "Plan File Path": {"rich_text": []},
            },
        },
        {
            "id": "page-b",
            "properties": {
                "Slug": {"title": [{"plain_text": "plan-b-bbbbbb"}]},
                "Status": {"select": {"name": "Completed"}},
                "Plan File Path": {"rich_text": []},
            },
        },
    ]

    monkeypatch.setattr(mod, "_query_all_plans", lambda: fake_pages)
    monkeypatch.setattr(sys, "argv", ["backfill_historical_plan_statuses.py", "--dry-run"])

    rc = mod.main()
    assert rc == 0
    out = capsys.readouterr().out
    # plan-a drift detected (Not Started -> Completed)
    assert "plan-a-aaaaaa" in out
    # plan-b MUST NOT appear in drift output (no on-disk ground truth)
    assert "plan-b-bbbbbb" not in out or "SKIP" in out or "skipped" in out.lower()
    # Exactly one drift item (plan-a only)
    assert "1 drift items found" in out
