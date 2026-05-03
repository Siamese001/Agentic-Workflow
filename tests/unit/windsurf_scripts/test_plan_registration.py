"""Unit tests for `.windsurf/scripts/_plan_registration.py` (§36).

Covers:
  - parse_plan_created_markers (marker grammar)
  - enqueue_plan / pending_registrations / mark_registered (queue semantics)
  - read_cache / cache_is_fresh / write_cache (cache I/O)
  - check_registration (decision logic across all source states)
  - drift_report (both-directions drift)
  - list_on_disk_plans (filename shape validation)
"""

from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path

import pytest

HELPER_PATH = (
    Path(__file__).resolve().parents[3] / ".windsurf" / "scripts" / "_plan_registration.py"
)


@pytest.fixture()
def pr(tmp_path, monkeypatch):
    """Load the helper module with its state paths redirected to tmp_path."""
    mod_name = "_plan_registration_under_test"
    spec = importlib.util.spec_from_file_location(mod_name, HELPER_PATH)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    # Register before exec — @dataclass introspects sys.modules[cls.__module__].
    sys.modules[mod_name] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception:
        sys.modules.pop(mod_name, None)
        raise

    state = tmp_path / "state"
    plans = tmp_path / "plans"
    state.mkdir()
    plans.mkdir()
    monkeypatch.setattr(mod, "STATE_DIR", state)
    monkeypatch.setattr(mod, "QUEUE_PATH", state / "plan_registration_queue.jsonl")
    monkeypatch.setattr(mod, "CACHE_PATH", state / "plan_registration_cache.json")
    monkeypatch.setattr(mod, "PLANS_DIR", plans)
    return mod


# ---------------------------------------------------------------------------
# parse_plan_created_markers
# ---------------------------------------------------------------------------


def test_parse_basic_marker(pr):
    text = "PLAN_CREATED: slug=my-plan-abc123 path=.windsurf/plans/my-plan-abc123.md status=Draft"
    out = pr.parse_plan_created_markers(text)
    assert len(out) == 1
    assert out[0]["slug"] == "my-plan-abc123"
    assert out[0]["path"] == ".windsurf/plans/my-plan-abc123.md"
    assert out[0]["status"] == "Draft"


def test_parse_multiple_markers(pr):
    text = (
        "Prose intro.\n"
        "PLAN_CREATED: slug=plan-one-aaaaaa path=.windsurf/plans/plan-one-aaaaaa.md status=Live\n"
        "More prose.\n"
        "PLAN_CREATED: slug=plan-two-bbbbbb\n"
    )
    out = pr.parse_plan_created_markers(text)
    assert len(out) == 2
    assert out[0]["status"] == "Live"
    assert out[1]["slug"] == "plan-two-bbbbbb"
    assert out[1]["path"] == ".windsurf/plans/plan-two-bbbbbb.md"
    assert out[1]["status"] == "Draft"  # default


def test_parse_rejects_invalid_slug(pr):
    text = "PLAN_CREATED: slug=BadSlug path=x status=Draft"
    assert pr.parse_plan_created_markers(text) == []


def test_parse_rejects_missing_slug(pr):
    text = "PLAN_CREATED: path=x status=Draft"
    assert pr.parse_plan_created_markers(text) == []


def test_parse_empty_text(pr):
    assert pr.parse_plan_created_markers("") == []


def test_parse_no_markers(pr):
    assert pr.parse_plan_created_markers("just prose, no markers here") == []


# ---------------------------------------------------------------------------
# Queue
# ---------------------------------------------------------------------------


def test_enqueue_and_list_pending(pr):
    assert pr.enqueue_plan("slug-one-aaaaaa", ".windsurf/plans/slug-one-aaaaaa.md")
    assert pr.enqueue_plan("slug-two-bbbbbb", ".windsurf/plans/slug-two-bbbbbb.md", "Live")
    pending = pr.pending_registrations()
    assert len(pending) == 2
    assert {r["slug"] for r in pending} == {"slug-one-aaaaaa", "slug-two-bbbbbb"}
    assert pending[1]["declared_status"] == "Live"


def test_enqueue_is_idempotent(pr):
    assert pr.enqueue_plan("slug-one-aaaaaa", ".windsurf/plans/slug-one-aaaaaa.md")
    assert not pr.enqueue_plan("slug-one-aaaaaa", ".windsurf/plans/slug-one-aaaaaa.md")
    assert len(pr.pending_registrations()) == 1


def test_enqueue_invalid_slug_raises(pr):
    with pytest.raises(ValueError):
        pr.enqueue_plan("INVALID", ".windsurf/plans/whatever.md")


def test_mark_registered_removes_from_pending(pr):
    pr.enqueue_plan("slug-one-aaaaaa", ".windsurf/plans/slug-one-aaaaaa.md")
    assert pr.mark_registered("slug-one-aaaaaa")
    assert pr.pending_registrations() == []


def test_mark_registered_missing_slug_noop(pr):
    assert not pr.mark_registered("slug-missing-aaaaaa")


def test_mark_registered_idempotent(pr):
    pr.enqueue_plan("slug-one-aaaaaa", ".windsurf/plans/slug-one-aaaaaa.md")
    assert pr.mark_registered("slug-one-aaaaaa")
    # Second call returns False because no row was flipped.
    assert not pr.mark_registered("slug-one-aaaaaa")


def test_queue_survives_corrupt_lines(pr):
    pr.QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
    pr.QUEUE_PATH.write_text(
        '{"slug": "slug-ok-aaaaaa", "registered": false}\n'
        "NOT JSON\n"
        '{"slug": "slug-other-bbbbbb", "registered": true, "registered_at": "2026-01-01T00:00:00Z"}\n',
        encoding="utf-8",
    )
    pending = pr.pending_registrations()
    assert [r["slug"] for r in pending] == ["slug-ok-aaaaaa"]


# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------


def test_write_cache_and_read_cache_roundtrip(pr):
    pr.write_cache({"slug-one-aaaaaa": {"status": "Live", "page_id": "abc"}})
    cache = pr.read_cache()
    assert cache is not None
    assert "fetched_at_epoch" in cache
    assert cache["plans"]["slug-one-aaaaaa"]["status"] == "Live"


def test_cache_is_fresh_true_for_recent(pr):
    pr.write_cache({})
    assert pr.cache_is_fresh(pr.read_cache())


def test_cache_is_fresh_false_for_stale(pr):
    pr.write_cache({})
    cache = pr.read_cache()
    cache["fetched_at_epoch"] = time.time() - (pr.CACHE_TTL_SECONDS + 100)
    assert not pr.cache_is_fresh(cache)


def test_cache_is_fresh_false_for_none(pr):
    assert not pr.cache_is_fresh(None)


def test_read_cache_missing_returns_none(pr):
    assert pr.read_cache() is None


def test_read_cache_malformed_returns_none(pr):
    pr.CACHE_PATH.write_text("not json", encoding="utf-8")
    assert pr.read_cache() is None


# ---------------------------------------------------------------------------
# check_registration
# ---------------------------------------------------------------------------


def test_check_registration_registered_via_cache(pr):
    pr.write_cache({"slug-one-aaaaaa": {"status": "Live"}})
    res = pr.check_registration("slug-one-aaaaaa")
    assert res.registered
    assert res.source == "cache"
    assert res.status == "Live"


def test_check_registration_retired_not_registered(pr):
    pr.write_cache({"slug-one-aaaaaa": {"status": "Retired"}})
    res = pr.check_registration("slug-one-aaaaaa")
    assert not res.registered
    assert res.reason == "status_is_Retired"


def test_check_registration_absent_from_cache(pr):
    pr.write_cache({"other-slug-aaaaaa": {"status": "Live"}})
    res = pr.check_registration("slug-one-aaaaaa")
    assert not res.registered
    assert res.reason == "not_in_notion_plans_db"


def test_check_registration_queue_bridges_cache_gap(pr):
    # Slug present in queue with registered=True but NOT in fresh cache yet.
    pr.enqueue_plan("slug-one-aaaaaa", ".windsurf/plans/slug-one-aaaaaa.md")
    pr.mark_registered("slug-one-aaaaaa")
    pr.write_cache({"other-slug-aaaaaa": {"status": "Live"}})
    res = pr.check_registration("slug-one-aaaaaa")
    assert res.registered
    assert res.source == "queue"


def test_check_registration_cache_missing_falls_back_to_queue(pr):
    pr.enqueue_plan("slug-one-aaaaaa", ".windsurf/plans/slug-one-aaaaaa.md")
    pr.mark_registered("slug-one-aaaaaa")
    res = pr.check_registration("slug-one-aaaaaa")
    assert res.registered
    assert res.source == "queue"


def test_check_registration_cache_missing_and_not_in_queue(pr):
    res = pr.check_registration("slug-one-aaaaaa")
    assert not res.registered
    assert res.source == "cache_missing"


def test_check_registration_invalid_slug(pr):
    res = pr.check_registration("NOT_A_SLUG")
    assert not res.registered
    assert res.reason == "invalid_slug"


# ---------------------------------------------------------------------------
# drift_report
# ---------------------------------------------------------------------------


def test_drift_report_both_directions(pr):
    # On-disk: slug-a + slug-b
    (pr.PLANS_DIR / "slug-a-aaaaaa.md").write_text("x", encoding="utf-8")
    (pr.PLANS_DIR / "slug-b-bbbbbb.md").write_text("x", encoding="utf-8")
    # Notion: slug-a (Live) + slug-c (Live)
    pr.write_cache({
        "slug-a-aaaaaa": {"status": "Live"},
        "slug-c-cccccc": {"status": "Live"},
    })
    report = pr.drift_report()
    assert report["on_disk_not_in_notion"] == ["slug-b-bbbbbb"]
    assert report["notion_active_not_on_disk"] == ["slug-c-cccccc"]


def test_drift_report_retired_not_counted_as_orphan(pr):
    (pr.PLANS_DIR / "slug-a-aaaaaa.md").write_text("x", encoding="utf-8")
    pr.write_cache({
        "slug-a-aaaaaa": {"status": "Live"},
        "slug-retired-bbbbbb": {"status": "Retired"},
    })
    report = pr.drift_report()
    assert report["notion_active_not_on_disk"] == []
    assert report["on_disk_not_in_notion"] == []


# ---------------------------------------------------------------------------
# list_on_disk_plans
# ---------------------------------------------------------------------------


def test_list_on_disk_plans_filters_bad_filenames(pr):
    (pr.PLANS_DIR / "plan-one-abc123.md").write_text("x", encoding="utf-8")
    (pr.PLANS_DIR / "not-a-plan.md").write_text("x", encoding="utf-8")  # no hex suffix
    (pr.PLANS_DIR / "plan-two-ABC123.md").write_text("x", encoding="utf-8")  # uppercase hex
    (pr.PLANS_DIR / "README.md").write_text("x", encoding="utf-8")
    slugs = pr.list_on_disk_plans()
    assert slugs == ["plan-one-abc123"]


def test_list_on_disk_plans_missing_dir(pr, tmp_path, monkeypatch):
    monkeypatch.setattr(pr, "PLANS_DIR", tmp_path / "does-not-exist")
    assert pr.list_on_disk_plans() == []


# ---------------------------------------------------------------------------
# iter_unregistered_on_disk
# ---------------------------------------------------------------------------


def test_iter_unregistered_on_disk(pr):
    (pr.PLANS_DIR / "slug-a-aaaaaa.md").write_text("x", encoding="utf-8")
    (pr.PLANS_DIR / "slug-b-bbbbbb.md").write_text("x", encoding="utf-8")
    pr.write_cache({"slug-a-aaaaaa": {"status": "Live"}})
    result = list(pr.iter_unregistered_on_disk())
    assert result == ["slug-b-bbbbbb"]
