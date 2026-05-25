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
        ("Deferred", "Lower Priority"),
        ("Waiting", "Waiting"),
        # Legacy mappings
        ("Live", "In Progress"),
        ("Draft", "Not Started"),
        ("Done", "Completed"),
        ("Superseded", "Retired"),
        ("Deprioritized", "Lower Priority"),
        ("Active", "In Progress"),
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


# -------------------------------------------------------------------
# DS-7: CI mode — no-ground-truth rows excluded from drift count
# -------------------------------------------------------------------


def test_ci_mode_no_ground_truth_not_counted_as_drift(
    mod, tmp_path, monkeypatch, capsys
):
    """DS-7: plan with on-disk file but no frontmatter status must NOT inflate
    CI drift count. It should appear in the no_ground_truth_skipped counter,
    NOT in drift_items, so --ci does NOT exit 2 when only such rows exist."""
    plan_no_status = tmp_path / "plan-c-cccccc.md"
    plan_no_status.write_text("# Plan C\n\nNo status field here.\n", encoding="utf-8")

    fake_pages = [
        {
            "id": "page-c",
            "properties": {
                "Slug": {"title": [{"plain_text": "plan-c-cccccc"}]},
                "Status": {"select": {"name": "In Progress"}},
                "Plan File Path": {
                    "rich_text": [{"plain_text": str(plan_no_status)}]
                },
            },
        },
    ]

    monkeypatch.setattr(mod, "_query_all_plans", lambda: fake_pages)
    monkeypatch.setattr(sys, "argv", ["backfill_historical_plan_statuses.py", "--ci"])

    rc = mod.main()
    out = capsys.readouterr().out
    # No true drift — exit 0
    assert rc == 0, f"Expected exit 0 (no drift), got {rc}. Output:\n{out}"
    # The row appears in the no-ground-truth counter, not drift
    assert "0 drift items" in out or "No drift" in out
    assert "ground-truth" in out.lower() or "no_ground_truth" in out.lower() or "ground truth" in out.lower()


def test_ci_mode_exits_2_only_for_true_drift(mod, tmp_path, monkeypatch, capsys):
    """DS-7: --ci must still exit 2 when there is genuine drift (on-disk has
    an explicit status that differs from Notion)."""
    plan_with_status = tmp_path / "plan-d-dddddd.md"
    plan_with_status.write_text(
        "---\nstatus: Completed\n---\n# Plan D\n", encoding="utf-8"
    )

    fake_pages = [
        {
            "id": "page-d",
            "properties": {
                "Slug": {"title": [{"plain_text": "plan-d-dddddd"}]},
                "Status": {"select": {"name": "Not Started"}},
                "Plan File Path": {
                    "rich_text": [{"plain_text": str(plan_with_status)}]
                },
            },
        },
    ]

    monkeypatch.setattr(mod, "_query_all_plans", lambda: fake_pages)
    monkeypatch.setattr(sys, "argv", ["backfill_historical_plan_statuses.py", "--ci"])

    rc = mod.main()
    assert rc == 2, f"Expected exit 2 (true drift detected), got {rc}"
