#!/usr/bin/env python3
"""test_repair_notion_plan_statuses.py — Unit tests for repair_notion_plan_statuses.

Focus: wrong-plan guard (_assert_slug_matches) and _extract_status_from_plan.
The main() function requires live Notion; tested via targeted unit mocks.
"""
import pytest

from tools.notion.repair_notion_plan_statuses import (
    _assert_slug_matches,
    _extract_status_from_plan,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _slug_props(slug_text: str) -> dict:
    """Build a minimal Notion page properties dict with a Slug title."""
    return {
        "Slug": {
            "title": [{"plain_text": slug_text, "text": {"content": slug_text}}]
        }
    }


def _no_slug_props() -> dict:
    return {}


# ---------------------------------------------------------------------------
# _assert_slug_matches
# ---------------------------------------------------------------------------

class TestAssertSlugMatches:
    """Tests for the bulk-repair wrong-plan guard (D-2)."""

    def test_match_returns_ok(self):
        ok, msg = _assert_slug_matches(_slug_props("my-plan-abc123"), "my-plan-abc123")
        assert ok is True
        assert msg == "ok"

    def test_mismatch_detected(self):
        ok, msg = _assert_slug_matches(_slug_props("other-plan-xyz"), "my-plan-abc123")
        assert ok is False
        assert "slug_mismatch" in msg
        assert "my-plan-abc123" in msg
        assert "other-plan-xyz" in msg

    def test_no_slug_property_is_permissive(self):
        ok, msg = _assert_slug_matches(_no_slug_props(), "my-plan-abc123")
        assert ok is True
        assert msg == "ok_no_slug"

    def test_empty_slug_in_page_is_permissive(self):
        """Empty title list → no slug → permissive."""
        props = {"Slug": {"title": []}}
        ok, msg = _assert_slug_matches(props, "my-plan-abc123")
        assert ok is True
        assert msg == "ok_no_slug"

    def test_whitespace_only_slug_is_permissive(self):
        props = {"Slug": {"title": [{"plain_text": "   "}]}}
        ok, msg = _assert_slug_matches(props, "my-plan-abc123")
        assert ok is True
        assert msg == "ok_no_slug"

    def test_multi_block_slug_concatenated(self):
        """Slug property can have multiple text blocks — they should be joined."""
        props = {
            "Slug": {
                "title": [
                    {"plain_text": "my-plan"},
                    {"plain_text": "-abc123"},
                ]
            }
        }
        ok, msg = _assert_slug_matches(props, "my-plan-abc123")
        assert ok is True

    def test_text_content_fallback(self):
        """Blocks may use text.content instead of plain_text."""
        props = {
            "Slug": {
                "title": [{"text": {"content": "my-plan-abc123"}}]
            }
        }
        ok, msg = _assert_slug_matches(props, "my-plan-abc123")
        assert ok is True

    def test_mismatch_blocked_write(self):
        """Confirm guard would block a wrong-plan write in a simulated loop."""
        rows_patched = []
        pages = [
            {"id": "page-correct", "properties": _slug_props("correct-slug-aabbcc")},
            {"id": "page-wrong",   "properties": _slug_props("wrong-slug-xxyyzz")},
            {"id": "page-no-slug", "properties": _no_slug_props()},
        ]
        expected_slug = "correct-slug-aabbcc"

        for page in pages:
            props = page.get("properties", {})
            slug_ok, _ = _assert_slug_matches(props, expected_slug)
            if slug_ok:
                rows_patched.append(page["id"])

        assert "page-correct" in rows_patched
        assert "page-wrong" not in rows_patched
        assert "page-no-slug" in rows_patched  # permissive


# ---------------------------------------------------------------------------
# _extract_status_from_plan
# ---------------------------------------------------------------------------

class TestExtractStatusFromPlan:
    """Tests for the markdown status extractor."""

    def test_frontmatter_in_progress(self):
        md = "---\nstatus: In Progress\n---\n# Plan"
        assert _extract_status_from_plan(md) == "In Progress"

    def test_frontmatter_completed(self):
        md = "---\nstatus: Completed\n---\n# Plan"
        assert _extract_status_from_plan(md) == "Completed"

    def test_frontmatter_live_maps_to_in_progress(self):
        md = "---\nstatus: live\n---\n# Plan"
        assert _extract_status_from_plan(md) == "In Progress"

    def test_frontmatter_done_maps_to_completed(self):
        md = "---\nstatus: done\n---\n"
        assert _extract_status_from_plan(md) == "Completed"

    def test_bold_metadata_status(self):
        md = "# Plan\n\n**Status**: In Progress\n"
        assert _extract_status_from_plan(md) == "In Progress"

    def test_bold_metadata_retired(self):
        md = "**Status**: Retired\n"
        assert _extract_status_from_plan(md) == "Retired"

    def test_plain_status_line(self):
        # 5-status SSOT: "Waiting" is coerced → "In Progress" via STALE_EQUIVALENTS.
        md = "Status: Waiting\n"
        assert _extract_status_from_plan(md) == "In Progress"

    def test_superseded_returns_retired(self):
        md = "# Old Plan\n\nSUPERSEDED by new-plan-abc\n"
        assert _extract_status_from_plan(md) == "Retired"

    def test_default_not_started(self):
        md = "# Plan without status\n\nSome content.\n"
        assert _extract_status_from_plan(md) == "Not Started"

    def test_deferred_status(self):
        # 5-status SSOT: "Deferred" is coerced → "In Progress" via STALE_EQUIVALENTS.
        md = "---\nstatus: deferred\n---\n"
        assert _extract_status_from_plan(md) == "In Progress"

    def test_frontmatter_case_insensitive(self):
        md = "---\nstatus: COMPLETED\n---\n"
        assert _extract_status_from_plan(md) == "Completed"
