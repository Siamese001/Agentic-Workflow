"""Unit tests for tools/notion/_wave_lifecycle_helpers.py + wave_lifecycle_writer.py.

Plan: notion-wave-lifecycle-autosync-f4a2b8 (W1.P1.2 / W1.P4.2 — partial).

Covers:
  - parse_wave_lifecycle_markers (4 marker kinds + slug validation + kv parsing)
  - patch_for_marker decision matrix (5 transition cases per kind)
  - coalesce_specs (merging multiple markers per slug)
  - rich_text helpers in writer (block split, trim, append)
  - apply_spec dry-run / bypass / no-token / noop paths

Network is fully mocked. No NOTION_TOKEN required.
"""
from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from tools.notion._wave_lifecycle_helpers import (
    CANONICAL_STATUSES,
    NotionPatchSpec,
    PROP_STATUS,
    PROP_SUMMARY,
    STATUS_COMPLETED,
    STATUS_IN_PROGRESS,
    STATUS_NOT_STARTED,
    STATUS_RETIRED,
    WAVE_LOG_PREFIX,
    WaveLifecycleMarker,
    coalesce_specs,
    parse_wave_lifecycle_markers,
    patch_for_marker,
)
from tools.notion import wave_lifecycle_writer as wlw


# ---------------------------------------------------------------------------
# Marker parsing
# ---------------------------------------------------------------------------


class TestParseMarkers:
    def test_parses_wave_start(self):
        markers = parse_wave_lifecycle_markers(
            "WAVE_START: plan=test-plan-abc123 wave=1\n"
        )
        assert len(markers) == 1
        assert markers[0].kind == "wave_start"
        assert markers[0].slug == "test-plan-abc123"
        assert markers[0].wave == 1

    def test_parses_wave_complete(self):
        markers = parse_wave_lifecycle_markers(
            "WAVE_COMPLETE: plan=foo-bar-deadbe wave=3\n"
        )
        assert markers[0].kind == "wave_complete"
        assert markers[0].slug == "foo-bar-deadbe"
        assert markers[0].wave == 3

    def test_parses_phase_complete(self):
        markers = parse_wave_lifecycle_markers(
            "PHASE_COMPLETE: plan=foo-bar-deadbe phase=P2.1\n"
        )
        assert markers[0].kind == "phase_complete"
        assert markers[0].phase == "P2.1"

    def test_parses_plan_complete(self):
        markers = parse_wave_lifecycle_markers("PLAN_COMPLETE: plan=foo-bar-deadbe\n")
        assert markers[0].kind == "plan_complete"

    def test_drops_invalid_slug(self):
        markers = parse_wave_lifecycle_markers("WAVE_START: plan=BAD_UPPER wave=1\n")
        assert markers == []

    def test_drops_marker_without_plan(self):
        markers = parse_wave_lifecycle_markers("WAVE_START: wave=1\n")
        assert markers == []

    def test_only_matches_at_line_start(self):
        # "Quoted: WAVE_COMPLETE: plan=foo-bar-deadbe wave=1" inside prose must NOT match.
        text = "Some prose mentioning WAVE_COMPLETE: plan=foo-bar-deadbe wave=1 inline."
        markers = parse_wave_lifecycle_markers(text)
        assert markers == []

    def test_handles_multiple_markers_in_order(self):
        text = (
            "WAVE_COMPLETE: plan=p1-aaaaaa wave=1\n"
            "WAVE_COMPLETE: plan=p1-aaaaaa wave=2\n"
            "PLAN_COMPLETE: plan=p1-aaaaaa\n"
        )
        markers = parse_wave_lifecycle_markers(text)
        assert len(markers) == 3
        kinds = [m.kind for m in markers]
        assert "plan_complete" in kinds
        assert kinds.count("wave_complete") == 2

    def test_handles_empty_input(self):
        assert parse_wave_lifecycle_markers("") == []
        assert parse_wave_lifecycle_markers("   \n\n") == []

    def test_invalid_wave_number_yields_none(self):
        markers = parse_wave_lifecycle_markers(
            "WAVE_START: plan=test-plan-abc123 wave=notanint\n"
        )
        assert markers[0].wave is None


# ---------------------------------------------------------------------------
# patch_for_marker — decision matrix
# ---------------------------------------------------------------------------


class TestPatchForMarker:
    SLUG = "demo-plan-abc123"
    FIXED_TS = "2026-05-10T12:00:00Z"

    def _marker(self, kind, **kw):
        return WaveLifecycleMarker(kind=kind, slug=self.SLUG, **kw)

    def test_wave_start_flips_not_started_to_in_progress(self):
        spec = patch_for_marker(
            self._marker("wave_start", wave=1),
            current_status=STATUS_NOT_STARTED,
            now_iso=self.FIXED_TS,
        )
        assert spec.properties[PROP_STATUS]["select"]["name"] == STATUS_IN_PROGRESS
        assert spec.summary_append.startswith(WAVE_LOG_PREFIX)
        assert "W1 START" in spec.summary_append
        assert "status_flip" in spec.reason

    def test_wave_start_no_flip_when_already_in_progress(self):
        spec = patch_for_marker(
            self._marker("wave_start", wave=2),
            current_status=STATUS_IN_PROGRESS,
            now_iso=self.FIXED_TS,
        )
        assert PROP_STATUS not in spec.properties
        assert spec.summary_append is not None
        assert "already_in_progress" in spec.reason

    def test_wave_start_locked_for_retired(self):
        spec = patch_for_marker(
            self._marker("wave_start", wave=1),
            current_status=STATUS_RETIRED,
            now_iso=self.FIXED_TS,
        )
        assert PROP_STATUS not in spec.properties
        assert "status_locked" in spec.reason

    def test_wave_complete_log_only(self):
        spec = patch_for_marker(
            self._marker("wave_complete", wave=3),
            current_status=STATUS_IN_PROGRESS,
            now_iso=self.FIXED_TS,
        )
        assert spec.properties == {}
        assert "W3 DONE" in spec.summary_append

    def test_phase_complete_log_only(self):
        spec = patch_for_marker(
            self._marker("phase_complete", phase="P2.1"),
            current_status=STATUS_IN_PROGRESS,
            now_iso=self.FIXED_TS,
        )
        assert spec.properties == {}
        assert "Phase P2.1 DONE" in spec.summary_append

    def test_plan_complete_flips_to_completed(self):
        spec = patch_for_marker(
            self._marker("plan_complete"),
            current_status=STATUS_IN_PROGRESS,
            now_iso=self.FIXED_TS,
        )
        assert spec.properties[PROP_STATUS]["select"]["name"] == STATUS_COMPLETED
        assert "PLAN COMPLETE" in spec.summary_append

    def test_plan_complete_idempotent_on_already_completed(self):
        spec = patch_for_marker(
            self._marker("plan_complete"),
            current_status=STATUS_COMPLETED,
            now_iso=self.FIXED_TS,
        )
        assert PROP_STATUS not in spec.properties
        assert "already_completed" in spec.reason

    def test_unknown_kind_is_noop(self):
        marker = WaveLifecycleMarker(kind="bogus", slug=self.SLUG)
        spec = patch_for_marker(marker, current_status=None, now_iso=self.FIXED_TS)
        assert spec.is_noop is True


# ---------------------------------------------------------------------------
# coalesce_specs
# ---------------------------------------------------------------------------


class TestCoalesce:
    def test_merges_two_markers_for_same_slug(self):
        s1 = NotionPatchSpec(
            slug="x-aaaaaa",
            summary_append="line1",
            reason="r1",
        )
        s2 = NotionPatchSpec(
            slug="x-aaaaaa",
            properties={PROP_STATUS: {"select": {"name": STATUS_COMPLETED}}},
            summary_append="line2",
            reason="r2",
        )
        merged = coalesce_specs([s1, s2])
        assert "x-aaaaaa" in merged
        m = merged["x-aaaaaa"]
        assert m.properties[PROP_STATUS]["select"]["name"] == STATUS_COMPLETED
        assert "line1" in m.summary_append and "line2" in m.summary_append
        assert "r1" in m.reason and "r2" in m.reason

    def test_drops_noop_specs(self):
        noop = NotionPatchSpec(slug="x-aaaaaa", reason="noop")
        merged = coalesce_specs([noop])
        assert merged == {}

    def test_keeps_distinct_slugs_separate(self):
        s1 = NotionPatchSpec(slug="a-aaaaaa", summary_append="a")
        s2 = NotionPatchSpec(slug="b-bbbbbb", summary_append="b")
        merged = coalesce_specs([s1, s2])
        assert set(merged.keys()) == {"a-aaaaaa", "b-bbbbbb"}

    def test_status_last_writer_wins(self):
        s1 = NotionPatchSpec(
            slug="a-aaaaaa",
            properties={PROP_STATUS: {"select": {"name": STATUS_IN_PROGRESS}}},
        )
        s2 = NotionPatchSpec(
            slug="a-aaaaaa",
            properties={PROP_STATUS: {"select": {"name": STATUS_COMPLETED}}},
        )
        merged = coalesce_specs([s1, s2])
        assert merged["a-aaaaaa"].properties[PROP_STATUS]["select"]["name"] == STATUS_COMPLETED


# ---------------------------------------------------------------------------
# Writer: rich_text helpers
# ---------------------------------------------------------------------------


class TestRichTextHelpers:
    def test_rich_text_plain_concatenates_blocks(self):
        prop = {
            "rich_text": [
                {"plain_text": "hello "},
                {"plain_text": "world"},
            ]
        }
        assert wlw._rich_text_plain(prop) == "hello world"

    def test_rich_text_plain_handles_missing(self):
        assert wlw._rich_text_plain({}) == ""
        assert wlw._rich_text_plain(None) == ""  # type: ignore[arg-type]

    def test_rich_text_blocks_splits_long_content(self):
        long = "x" * 2500
        blocks = wlw._rich_text_blocks(long)
        assert len(blocks) == 2
        assert blocks[0]["text"]["content"] == "x" * wlw.RICH_TEXT_BLOCK_MAX

    def test_build_summary_property_appends_with_newline(self):
        result = wlw._build_summary_property("existing", "new line")
        blocks = result[PROP_SUMMARY]["rich_text"]
        joined = "".join(b["text"]["content"] for b in blocks)
        assert joined == "existing\nnew line"

    def test_build_summary_property_empty_existing(self):
        result = wlw._build_summary_property("", "first")
        blocks = result[PROP_SUMMARY]["rich_text"]
        joined = "".join(b["text"]["content"] for b in blocks)
        assert joined == "first"


# ---------------------------------------------------------------------------
# Writer: apply_spec — dry-run / bypass / no-token / noop
# ---------------------------------------------------------------------------


class TestApplySpec:
    def test_noop_spec_returns_ok(self):
        spec = NotionPatchSpec(slug="x-aaaaaa", reason="empty")
        ok, msg = wlw.apply_spec(spec, dry_run=False, token="dummy")
        assert ok is True
        assert msg == "noop"

    def test_dry_run_does_not_call_network(self):
        spec = NotionPatchSpec(
            slug="x-aaaaaa",
            properties={PROP_STATUS: {"select": {"name": STATUS_COMPLETED}}},
            summary_append="dry",
        )
        with patch.object(wlw, "_post_json") as mock_post, patch.object(
            wlw, "_patch_json"
        ) as mock_patch:
            ok, msg = wlw.apply_spec(spec, dry_run=True)
        assert ok is True
        assert msg == "dry_run"
        mock_post.assert_not_called()
        mock_patch.assert_not_called()

    def test_bypass_env_short_circuits(self, monkeypatch):
        monkeypatch.setenv("WAVE_LIFECYCLE_NOTION_BYPASS", "1")
        monkeypatch.setenv("NOTION_TOKEN", "dummy")
        spec = NotionPatchSpec(
            slug="x-aaaaaa",
            properties={PROP_STATUS: {"select": {"name": STATUS_COMPLETED}}},
        )
        with patch.object(wlw, "_post_json") as mock_post, patch.object(
            wlw, "_patch_json"
        ) as mock_patch:
            ok, msg = wlw.apply_spec(spec)
        assert ok is True
        assert msg == "bypass"
        mock_post.assert_not_called()
        mock_patch.assert_not_called()

    def test_no_token_fails_soft(self, monkeypatch):
        monkeypatch.delenv("NOTION_TOKEN", raising=False)
        monkeypatch.delenv("NOTION_API_KEY", raising=False)
        monkeypatch.delenv("WAVE_LIFECYCLE_NOTION_BYPASS", raising=False)
        spec = NotionPatchSpec(
            slug="x-aaaaaa",
            properties={PROP_STATUS: {"select": {"name": STATUS_COMPLETED}}},
        )
        ok, msg = wlw.apply_spec(spec)
        assert ok is False
        assert msg == "no_notion_token"

    def test_lookup_failure_fails_soft(self, monkeypatch):
        monkeypatch.delenv("WAVE_LIFECYCLE_NOTION_BYPASS", raising=False)
        spec = NotionPatchSpec(
            slug="x-aaaaaa",
            properties={PROP_STATUS: {"select": {"name": STATUS_COMPLETED}}},
        )
        with patch.object(wlw, "find_plan_page", return_value=(None, {}, "not_found")):
            ok, msg = wlw.apply_spec(spec, token="dummy")
        assert ok is False
        assert "lookup_failed" in msg

    def test_successful_patch_includes_summary_merge(self, monkeypatch):
        monkeypatch.delenv("WAVE_LIFECYCLE_NOTION_BYPASS", raising=False)
        existing_props = {
            PROP_SUMMARY: {"rich_text": [{"plain_text": "prior"}]},
        }
        spec = NotionPatchSpec(
            slug="x-aaaaaa",
            properties={PROP_STATUS: {"select": {"name": STATUS_COMPLETED}}},
            summary_append="new",
        )
        captured = {}

        def fake_patch(url, body, token):
            captured["url"] = url
            captured["body"] = body
            return True, "ok"

        with patch.object(
            wlw, "find_plan_page", return_value=("page-123", existing_props, "ok")
        ), patch.object(wlw, "_patch_json", side_effect=fake_patch):
            ok, msg = wlw.apply_spec(spec, token="dummy")
        assert ok is True
        assert msg == "ok"
        sent_props = captured["body"]["properties"]
        assert PROP_STATUS in sent_props
        assert PROP_SUMMARY in sent_props
        joined = "".join(b["text"]["content"] for b in sent_props[PROP_SUMMARY]["rich_text"])
        assert "prior" in joined and "new" in joined


# ---------------------------------------------------------------------------
# Status taxonomy alignment
# ---------------------------------------------------------------------------


class TestStatusTaxonomy:
    def test_canonical_includes_all_documented(self):
        # Must align with .windsurf/rules/notion-plans-taxonomy.md.
        assert "Not Started" in CANONICAL_STATUSES
        assert "In Progress" in CANONICAL_STATUSES
        assert "Completed" in CANONICAL_STATUSES
        assert "Retired" in CANONICAL_STATUSES
        assert "Archived" in CANONICAL_STATUSES
        # The stale "Draft" / "Live" forms must NOT be canonical.
        assert "Draft" not in CANONICAL_STATUSES
        assert "Live" not in CANONICAL_STATUSES

    def test_patch_status_rejects_non_canonical(self):
        ok, msg = wlw.patch_status("x-aaaaaa", "Draft")
        assert ok is False
        assert "invalid_status" in msg
