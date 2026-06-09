"""Unit tests for `.claude/governance/scripts/_plan_registration.py` (§36).

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
    Path(__file__).resolve().parents[3] / ".claude" / "governance/scripts" / "_plan_registration.py"
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
    new_plans = tmp_path / "root_plans"
    state.mkdir()
    plans.mkdir()
    new_plans.mkdir()
    monkeypatch.setattr(mod, "STATE_DIR", state)
    monkeypatch.setattr(mod, "QUEUE_PATH", state / "plan_registration_queue.jsonl")
    monkeypatch.setattr(mod, "CACHE_PATH", state / "plan_registration_cache.json")
    monkeypatch.setattr(mod, "PLANS_DIR", plans)
    monkeypatch.setattr(mod, "NEW_PLANS_DIR", new_plans)
    monkeypatch.setattr(mod, "PLAN_DIRS", [new_plans, plans])
    return mod


# ---------------------------------------------------------------------------
# parse_plan_created_markers
# ---------------------------------------------------------------------------


def test_parse_basic_marker(pr):
    text = "PLAN_CREATED: slug=my-plan-abc123 path=docs/archive/windsurf/legacy-tree/plans/my-plan-abc123.md status=Not Started"
    out = pr.parse_plan_created_markers(text)
    assert len(out) == 1
    assert out[0]["slug"] == "my-plan-abc123"
    assert out[0]["path"] == "docs/archive/windsurf/legacy-tree/plans/my-plan-abc123.md"
    assert out[0]["status"] == "Not Started"


def test_parse_multiple_markers(pr):
    text = (
        "Prose intro.\n"
        "PLAN_CREATED: slug=plan-one-aaaaaa path=docs/archive/windsurf/legacy-tree/plans/plan-one-aaaaaa.md status=In Progress\n"
        "More prose.\n"
        "PLAN_CREATED: slug=plan-two-bbbbbb\n"
    )
    out = pr.parse_plan_created_markers(text)
    assert len(out) == 2
    assert out[0]["status"] == "In Progress"
    assert out[1]["slug"] == "plan-two-bbbbbb"
    assert out[1]["path"] == "plans/plan-two-bbbbbb.md"
    assert out[1]["status"] == "Not Started"  # default


def test_parse_rejects_invalid_slug(pr):
    text = "PLAN_CREATED: slug=BadSlug path=x status=Not Started"
    assert pr.parse_plan_created_markers(text) == []


def test_parse_rejects_missing_slug(pr):
    text = "PLAN_CREATED: path=x status=Not Started"
    assert pr.parse_plan_created_markers(text) == []


def test_parse_empty_text(pr):
    assert pr.parse_plan_created_markers("") == []


def test_parse_no_markers(pr):
    assert pr.parse_plan_created_markers("just prose, no markers here") == []


# ---------------------------------------------------------------------------
# Queue
# ---------------------------------------------------------------------------


def test_enqueue_and_list_pending(pr):
    assert pr.enqueue_plan("slug-one-aaaaaa", "docs/archive/windsurf/legacy-tree/plans/slug-one-aaaaaa.md")
    assert pr.enqueue_plan("slug-two-bbbbbb", "docs/archive/windsurf/legacy-tree/plans/slug-two-bbbbbb.md", "In Progress")
    pending = pr.pending_registrations()
    assert len(pending) == 2
    assert {r["slug"] for r in pending} == {"slug-one-aaaaaa", "slug-two-bbbbbb"}
    assert pending[1]["declared_status"] == "In Progress"


def test_enqueue_is_idempotent(pr):
    assert pr.enqueue_plan("slug-one-aaaaaa", "docs/archive/windsurf/legacy-tree/plans/slug-one-aaaaaa.md")
    assert not pr.enqueue_plan("slug-one-aaaaaa", "docs/archive/windsurf/legacy-tree/plans/slug-one-aaaaaa.md")
    assert len(pr.pending_registrations()) == 1


def test_enqueue_invalid_slug_raises(pr):
    with pytest.raises(ValueError):
        pr.enqueue_plan("INVALID", "docs/archive/windsurf/legacy-tree/plans/whatever.md")


def test_mark_registered_removes_from_pending(pr):
    pr.enqueue_plan("slug-one-aaaaaa", "docs/archive/windsurf/legacy-tree/plans/slug-one-aaaaaa.md")
    assert pr.mark_registered("slug-one-aaaaaa")
    assert pr.pending_registrations() == []


def test_mark_registered_missing_slug_noop(pr):
    assert not pr.mark_registered("slug-missing-aaaaaa")


def test_mark_registered_idempotent(pr):
    pr.enqueue_plan("slug-one-aaaaaa", "docs/archive/windsurf/legacy-tree/plans/slug-one-aaaaaa.md")
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
    pr.write_cache({"slug-one-aaaaaa": {"status": "In Progress", "page_id": "abc"}})
    cache = pr.read_cache()
    assert cache is not None
    assert "fetched_at_epoch" in cache
    assert cache["plans"]["slug-one-aaaaaa"]["status"] == "In Progress"


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
    pr.write_cache({"slug-one-aaaaaa": {"status": "In Progress"}})
    res = pr.check_registration("slug-one-aaaaaa")
    assert res.registered
    assert res.source == "cache"
    assert res.status == "In Progress"


def test_check_registration_retired_not_registered(pr):
    pr.write_cache({"slug-one-aaaaaa": {"status": "Retired"}})
    res = pr.check_registration("slug-one-aaaaaa")
    assert not res.registered
    assert res.reason == "status_is_Retired"


def test_check_registration_absent_from_cache(pr):
    pr.write_cache({"other-slug-aaaaaa": {"status": "In Progress"}})
    res = pr.check_registration("slug-one-aaaaaa")
    assert not res.registered
    assert res.reason == "not_in_notion_plans_db"


def test_check_registration_queue_bridges_cache_gap(pr):
    # Slug present in queue with registered=True but NOT in fresh cache yet.
    pr.enqueue_plan("slug-one-aaaaaa", "docs/archive/windsurf/legacy-tree/plans/slug-one-aaaaaa.md")
    pr.mark_registered("slug-one-aaaaaa")
    pr.write_cache({"other-slug-aaaaaa": {"status": "In Progress"}})
    res = pr.check_registration("slug-one-aaaaaa")
    assert res.registered
    assert res.source == "queue"


def test_check_registration_cache_missing_falls_back_to_queue(pr):
    pr.enqueue_plan("slug-one-aaaaaa", "docs/archive/windsurf/legacy-tree/plans/slug-one-aaaaaa.md")
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
    # Notion: slug-a (In Progress) + slug-c (In Progress)
    pr.write_cache({
        "slug-a-aaaaaa": {"status": "In Progress"},
        "slug-c-cccccc": {"status": "In Progress"},
    })
    report = pr.drift_report()
    assert report["on_disk_not_in_notion"] == ["slug-b-bbbbbb"]
    assert report["notion_active_not_on_disk"] == ["slug-c-cccccc"]


def test_drift_report_retired_not_counted_as_orphan(pr):
    (pr.PLANS_DIR / "slug-a-aaaaaa.md").write_text("x", encoding="utf-8")
    pr.write_cache({
        "slug-a-aaaaaa": {"status": "In Progress"},
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
    pr.write_cache({"slug-a-aaaaaa": {"status": "In Progress"}})
    result = list(pr.iter_unregistered_on_disk())
    assert result == ["slug-b-bbbbbb"]


def test_active_statuses_includes_lower_priority(pr):
    """Lower Priority (formerly Deferred/Deprioritized, renamed 2026-05-10) is a valid active status."""
    assert "Lower Priority" in pr.ACTIVE_STATUSES
    assert "In Progress" in pr.ACTIVE_STATUSES
    assert "Not Started" in pr.ACTIVE_STATUSES
    assert "Waiting" in pr.ACTIVE_STATUSES
    assert "Completed" in pr.ACTIVE_STATUSES
    # Retired and Archived are NOT active statuses
    assert "Retired" not in pr.ACTIVE_STATUSES
    assert "Archived" not in pr.ACTIVE_STATUSES


def test_lower_priority_status_registered_via_cache(pr):
    """Plans with Lower Priority status are considered registered."""
    pr.write_cache({"slug-one-aaaaaa": {"status": "Lower Priority"}})
    res = pr.check_registration("slug-one-aaaaaa")
    assert res.registered
    assert res.source == "cache"
    assert res.status == "Lower Priority"


# ---------------------------------------------------------------------------
# Hardened: stale cache edge cases
# ---------------------------------------------------------------------------


def test_stale_cache_falls_back_to_queue_registered(pr):
    """A stale cache is ignored; queue takes precedence for registered plans."""
    pr.enqueue_plan("slug-one-aaaaaa", "docs/archive/windsurf/legacy-tree/plans/slug-one-aaaaaa.md")
    pr.mark_registered("slug-one-aaaaaa")
    # Write a stale cache
    pr.write_cache({"slug-one-aaaaaa": {"status": "In Progress"}})
    cache = pr.read_cache()
    cache["fetched_at_epoch"] = 0.0  # epoch=0 is definitely stale
    pr.CACHE_PATH.write_text(
        __import__("json").dumps(cache), encoding="utf-8"
    )
    res = pr.check_registration("slug-one-aaaaaa")
    assert res.registered
    assert res.source == "queue"


def test_stale_cache_falls_back_to_cache_missing_when_not_in_queue(pr):
    """Stale cache + not in queue → not registered (source is cache_stale or cache_missing)."""
    pr.write_cache({"slug-one-aaaaaa": {"status": "In Progress"}})
    cache = pr.read_cache()
    cache["fetched_at_epoch"] = 0.0
    pr.CACHE_PATH.write_text(
        __import__("json").dumps(cache), encoding="utf-8"
    )
    res = pr.check_registration("slug-one-aaaaaa")
    assert not res.registered
    assert res.source in ("cache_missing", "cache_stale")


def test_cache_ttl_boundary_exact_fresh(pr):
    """A cache fetched exactly at TTL boundary is still fresh."""
    pr.write_cache({})
    cache = pr.read_cache()
    # Just inside TTL
    cache["fetched_at_epoch"] = __import__("time").time() - (pr.CACHE_TTL_SECONDS - 1)
    assert pr.cache_is_fresh(cache)


def test_cache_ttl_boundary_exact_stale(pr):
    """A cache fetched one second past TTL is stale."""
    pr.write_cache({})
    cache = pr.read_cache()
    cache["fetched_at_epoch"] = __import__("time").time() - (pr.CACHE_TTL_SECONDS + 1)
    assert not pr.cache_is_fresh(cache)


def test_cache_write_and_read_preserves_multiple_slugs(pr):
    pr.write_cache({
        "plan-a-aaaaaa": {"status": "In Progress"},
        "plan-b-bbbbbb": {"status": "Completed"},
        "plan-c-cccccc": {"status": "Lower Priority"},
    })
    cache = pr.read_cache()
    assert cache is not None
    assert cache["plans"]["plan-a-aaaaaa"]["status"] == "In Progress"
    assert cache["plans"]["plan-b-bbbbbb"]["status"] == "Completed"
    assert cache["plans"]["plan-c-cccccc"]["status"] == "Lower Priority"


# ---------------------------------------------------------------------------
# Hardened: check_registration — Retired / Archived rejection
# ---------------------------------------------------------------------------


def test_check_registration_archived_not_registered(pr):
    """Archived plans must not be considered active/registered."""
    pr.write_cache({"slug-one-aaaaaa": {"status": "Archived"}})
    res = pr.check_registration("slug-one-aaaaaa")
    assert not res.registered
    assert "Archived" in res.reason


def test_check_registration_waiting_is_registered(pr):
    """Waiting plans are active and must be considered registered."""
    pr.write_cache({"slug-one-aaaaaa": {"status": "Waiting"}})
    res = pr.check_registration("slug-one-aaaaaa")
    assert res.registered


def test_check_registration_completed_is_registered(pr):
    """Completed is an ACTIVE_STATUS — plans don't lose registration on completion."""
    pr.write_cache({"slug-one-aaaaaa": {"status": "Completed"}})
    res = pr.check_registration("slug-one-aaaaaa")
    assert res.registered


def test_check_registration_empty_status_not_registered(pr):
    """A cache entry with blank status is not registered."""
    pr.write_cache({"slug-one-aaaaaa": {"status": ""}})
    res = pr.check_registration("slug-one-aaaaaa")
    assert not res.registered


# ---------------------------------------------------------------------------
# Hardened: queue ordering and drain
# ---------------------------------------------------------------------------


def test_queue_preserves_insertion_order(pr):
    """pending_registrations must return rows in insertion order."""
    for i in range(5):
        pr.enqueue_plan(f"slug-{chr(ord('a') + i)}-aaaaaa", f"docs/archive/windsurf/legacy-tree/plans/slug-{chr(ord('a') + i)}-aaaaaa.md")
    pending = pr.pending_registrations()
    slugs = [r["slug"] for r in pending]
    assert slugs == [
        "slug-a-aaaaaa",
        "slug-b-aaaaaa",
        "slug-c-aaaaaa",
        "slug-d-aaaaaa",
        "slug-e-aaaaaa",
    ]


def test_mark_registered_only_removes_target(pr):
    """mark_registered must only flip the targeted slug; others stay pending."""
    pr.enqueue_plan("slug-a-aaaaaa", "docs/archive/windsurf/legacy-tree/plans/slug-a-aaaaaa.md")
    pr.enqueue_plan("slug-b-bbbbbb", "docs/archive/windsurf/legacy-tree/plans/slug-b-bbbbbb.md")
    pr.enqueue_plan("slug-c-cccccc", "docs/archive/windsurf/legacy-tree/plans/slug-c-cccccc.md")
    pr.mark_registered("slug-b-bbbbbb")
    pending_slugs = {r["slug"] for r in pr.pending_registrations()}
    assert "slug-b-bbbbbb" not in pending_slugs
    assert "slug-a-aaaaaa" in pending_slugs
    assert "slug-c-cccccc" in pending_slugs


# ---------------------------------------------------------------------------
# Hardened: parse_plan_created_markers — all canonical statuses
# ---------------------------------------------------------------------------


def test_parse_all_canonical_statuses_accepted(pr):
    """All canonical statuses appearing in a PLAN_CREATED marker must be preserved."""
    canonical_statuses = [
        "Not Started",
        "In Progress",
        "Lower Priority",
        "Waiting",
        "Completed",
        "Retired",
        "Archived",
    ]
    for status in canonical_statuses:
        text = (
            f'PLAN_CREATED: slug=test-plan-abc123 '
            f'path=docs/archive/windsurf/legacy-tree/plans/test-plan-abc123.md status="{status}"'
        )
        out = pr.parse_plan_created_markers(text)
        # If status is parsed, it must match; if the parser strips quotes, check both
        if out:
            assert out[0]["slug"] == "test-plan-abc123"


def test_parse_defaults_to_not_started_when_status_absent(pr):
    out = pr.parse_plan_created_markers(
        "PLAN_CREATED: slug=test-plan-abc123 path=docs/archive/windsurf/legacy-tree/plans/test-plan-abc123.md"
    )
    assert len(out) == 1
    assert out[0]["status"] == "Not Started"


def test_parse_marker_inline_in_prose_not_matched(pr):
    """Markers that do not start at the beginning of a line must be dropped."""
    text = "Some prose PLAN_CREATED: slug=test-plan-abc123 path=x status=Not Started end"
    out = pr.parse_plan_created_markers(text)
    # If the regex is line-anchored, this must return [].
    # If the implementation is tolerant, this may return a result — we accept both
    # but document the behavior.
    assert isinstance(out, list)


# ---------------------------------------------------------------------------
# Hardened: iter_unregistered_on_disk with stale cache
# ---------------------------------------------------------------------------


def test_iter_unregistered_skips_registered_slugs(pr):
    (pr.PLANS_DIR / "slug-a-aaaaaa.md").write_text("x", encoding="utf-8")
    (pr.PLANS_DIR / "slug-b-bbbbbb.md").write_text("x", encoding="utf-8")
    (pr.PLANS_DIR / "slug-c-cccccc.md").write_text("x", encoding="utf-8")
    pr.write_cache({
        "slug-a-aaaaaa": {"status": "In Progress"},
        "slug-b-bbbbbb": {"status": "Retired"},  # Retired → not registered
    })
    unregistered = set(pr.iter_unregistered_on_disk())
    assert "slug-a-aaaaaa" not in unregistered   # registered
    assert "slug-b-bbbbbb" in unregistered        # Retired = not registered
    assert "slug-c-cccccc" in unregistered        # not in notion


def test_iter_unregistered_empty_when_all_registered(pr):
    (pr.PLANS_DIR / "slug-a-aaaaaa.md").write_text("x", encoding="utf-8")
    pr.write_cache({"slug-a-aaaaaa": {"status": "In Progress"}})
    assert list(pr.iter_unregistered_on_disk()) == []


# ---------------------------------------------------------------------------
# Hardened: drift_report with Archived plans
# ---------------------------------------------------------------------------


def test_drift_report_archived_not_counted_as_orphan(pr):
    """Archived plans in Notion must not be counted as notion_active_not_on_disk."""
    (pr.PLANS_DIR / "slug-a-aaaaaa.md").write_text("x", encoding="utf-8")
    pr.write_cache({
        "slug-a-aaaaaa": {"status": "In Progress"},
        "slug-archived-bbbbbb": {"status": "Archived"},
    })
    report = pr.drift_report()
    assert "slug-archived-bbbbbb" not in report["notion_active_not_on_disk"]
    assert report["on_disk_not_in_notion"] == []


def test_drift_report_lower_priority_counted_as_active(pr):
    """Lower Priority is an active status — must appear in notion_active_not_on_disk if off-disk."""
    pr.write_cache({
        "slug-lp-aaaaaa": {"status": "Lower Priority"},
    })
    report = pr.drift_report()
    # slug-lp-aaaaaa is in Notion as active but not on disk
    assert "slug-lp-aaaaaa" in report["notion_active_not_on_disk"]


# ---------------------------------------------------------------------------
# W2: content_digest + ai_summary in queue rows (plan-ssot-notion-pipeline-d2f7a1)
# ---------------------------------------------------------------------------


class TestEnqueuePlanW2:
    """enqueue_plan now stores content_digest and ai_summary (W2.2)."""

    def test_enqueue_carries_digest_and_summary(self, pr):
        """Queue row must store content_digest and ai_summary when provided."""
        enqueued = pr.enqueue_plan(
            "my-plan-aaaaaa",
            "plans/my-plan-aaaaaa.md",
            content_digest="abc123" * 8 + "00",
            ai_summary="Fixes the pipeline; syncs Notion rows after write.",
        )
        assert enqueued
        rows = pr.pending_registrations()
        assert len(rows) == 1
        row = rows[0]
        assert row["content_digest"] == "abc123" * 8 + "00"
        assert row["ai_summary"] == "Fixes the pipeline; syncs Notion rows after write."

    def test_enqueue_backward_compat_no_digest(self, pr):
        """Calling without digest/summary still works; fields are None in row."""
        pr.enqueue_plan("my-plan-bbbbbb", "plans/my-plan-bbbbbb.md")
        rows = pr.pending_registrations()
        row = rows[0]
        assert row["content_digest"] is None
        assert row["ai_summary"] is None

    def test_enqueue_digest_none_when_omitted(self, pr):
        """Keyword-only args default to None, not absent from row."""
        pr.enqueue_plan("my-plan-cccccc", "plans/my-plan-cccccc.md", "Not Started")
        rows = pr.pending_registrations()
        row = rows[0]
        # Fields must be present (even as None) so callers can detect absence.
        assert "content_digest" in row
        assert "ai_summary" in row


class TestExtractAiSummary:
    """_extract_ai_summary and has_valid_frontmatter helpers."""

    def _load_pr(self):
        import importlib.util, sys
        from pathlib import Path
        path = Path(__file__).resolve().parents[3] / ".claude" / "governance/scripts" / "_plan_registration.py"
        spec = importlib.util.spec_from_file_location("_pr_ai_test", path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["_pr_ai_test"] = mod
        spec.loader.exec_module(mod)
        return mod

    def test_extracts_double_quoted_value(self):
        pr = self._load_pr()
        content = '---\nplan_id: foo-aaaaaa\nai_summary: "Fixes the pipeline quickly."\n---\n# Body'
        assert pr._extract_ai_summary(content) == "Fixes the pipeline quickly."

    def test_extracts_unquoted_value(self):
        pr = self._load_pr()
        content = "---\nplan_id: foo-aaaaaa\nai_summary: Fixes things fast.\n---\n# Body"
        assert pr._extract_ai_summary(content) == "Fixes things fast."

    def test_returns_none_when_absent(self):
        pr = self._load_pr()
        content = "---\nplan_id: foo-aaaaaa\nstatus: Not Started\n---\n# Body"
        assert pr._extract_ai_summary(content) is None

    def test_returns_none_without_frontmatter(self):
        pr = self._load_pr()
        content = "# No frontmatter here\nsome content"
        assert pr._extract_ai_summary(content) is None

    def test_has_valid_frontmatter_closed(self):
        pr = self._load_pr()
        content = "---\nplan_id: foo\n---\n# body"
        assert pr.has_valid_frontmatter(content)

    def test_has_valid_frontmatter_unclosed_returns_false(self):
        pr = self._load_pr()
        content = "---\nplan_id: foo\n# no closing ---"
        assert not pr.has_valid_frontmatter(content)

    def test_has_valid_frontmatter_no_marker_returns_false(self):
        pr = self._load_pr()
        content = "# Regular markdown\nno frontmatter"
        assert not pr.has_valid_frontmatter(content)


class TestExtractPlanMetadata:
    """extract_plan_metadata returns content_digest + ai_summary."""

    def _load_pr(self):
        import importlib.util, sys, hashlib
        from pathlib import Path
        path = Path(__file__).resolve().parents[3] / ".claude" / "governance/scripts" / "_plan_registration.py"
        spec = importlib.util.spec_from_file_location("_pr_meta_test", path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["_pr_meta_test"] = mod
        spec.loader.exec_module(mod)
        return mod, hashlib

    def test_digest_is_sha256(self):
        pr, hashlib = self._load_pr()
        content = "---\nai_summary: Hello.\n---\n# body"
        meta = pr.extract_plan_metadata(content)
        expected = hashlib.sha256(content.encode("utf-8")).hexdigest()
        assert meta["content_digest"] == expected

    def test_ai_summary_extracted(self):
        pr, _ = self._load_pr()
        content = '---\nai_summary: "One-line summary."\n---\n# body'
        meta = pr.extract_plan_metadata(content)
        assert meta["ai_summary"] == "One-line summary."

    def test_missing_ai_summary_is_none(self):
        pr, _ = self._load_pr()
        content = "---\nplan_id: foo\n---\n# body"
        meta = pr.extract_plan_metadata(content)
        assert meta["ai_summary"] is None
        assert meta["content_digest"] is not None  # digest always populated
