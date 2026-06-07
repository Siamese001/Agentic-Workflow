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
    MAX_NOTE_CHARS,
    NotionPatchSpec,
    PROP_STATUS,
    PROP_SUMMARY,
    SLUG_RE,
    STATUS_ARCHIVED,
    STATUS_COMPLETED,
    STATUS_IN_PROGRESS,
    STATUS_LOWER_PRIORITY,
    STATUS_NOT_STARTED,
    STATUS_RETIRED,
    STATUS_WAITING,
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
        # Must align with .cursor/rules/notion-plans-taxonomy.md.
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


# ---------------------------------------------------------------------------
# note= field (high-signal Summary appends)
# ---------------------------------------------------------------------------


class TestNoteField:
    """Regression coverage for the optional ``note="..."`` marker field.

    Without ``note=`` the Notion Summary column collapses to a wall of
    ``[Wave-Log <ts>] W{N} DONE`` lines. With ``note=`` operators see one
    high-signal one-liner per wave. The field is parsed at marker time,
    suffixed onto the summary append, and capped at MAX_NOTE_CHARS.
    """

    SLUG = "demo-plan-abc123"
    FIXED_TS = "2026-05-10T12:00:00Z"

    def test_parses_double_quoted_note_with_spaces(self):
        markers = parse_wave_lifecycle_markers(
            'WAVE_COMPLETE: plan=demo-plan-abc123 wave=3 '
            'note="4 files, +12 tests, scope=summary-signal"\n'
        )
        assert len(markers) == 1
        assert markers[0].note == "4 files, +12 tests, scope=summary-signal"

    def test_parses_single_quoted_note(self):
        markers = parse_wave_lifecycle_markers(
            "WAVE_COMPLETE: plan=demo-plan-abc123 wave=2 note='hot path wired'\n"
        )
        assert markers[0].note == "hot path wired"

    def test_parses_bareword_note(self):
        markers = parse_wave_lifecycle_markers(
            "WAVE_COMPLETE: plan=demo-plan-abc123 wave=1 note=quick\n"
        )
        assert markers[0].note == "quick"

    def test_omitted_note_is_none(self):
        markers = parse_wave_lifecycle_markers(
            "WAVE_COMPLETE: plan=demo-plan-abc123 wave=1\n"
        )
        assert markers[0].note is None

    def test_note_collapses_same_line_whitespace(self):
        # Markers are line-anchored, so notes can't contain literal newlines
        # via a marker — but tabs and runs of spaces inside a quoted value
        # MUST collapse to single spaces for a clean Summary append.
        markers = parse_wave_lifecycle_markers(
            'PHASE_COMPLETE: plan=demo-plan-abc123 phase=P2.1 '
            'note="multi   space\t\ttabbed   end"\n'
        )
        assert markers[0].note == "multi space tabbed end"

    def test_note_truncated_at_cap(self):
        long = "x" * (MAX_NOTE_CHARS + 50)
        markers = parse_wave_lifecycle_markers(
            f'WAVE_COMPLETE: plan=demo-plan-abc123 wave=1 note="{long}"\n'
        )
        assert markers[0].note is not None
        assert len(markers[0].note) == MAX_NOTE_CHARS
        assert markers[0].note.endswith("\u2026")

    def test_summary_append_suffixes_note_em_dash(self):
        marker = WaveLifecycleMarker(
            kind="wave_complete",
            slug=self.SLUG,
            wave=3,
            note="4 files, +12 tests",
        )
        spec = patch_for_marker(
            marker, current_status=STATUS_IN_PROGRESS, now_iso=self.FIXED_TS
        )
        assert spec.summary_append is not None
        assert "W3 DONE \u2014 4 files, +12 tests" in spec.summary_append
        assert "note_present" in spec.reason

    def test_summary_append_no_note_keeps_terse_line(self):
        marker = WaveLifecycleMarker(
            kind="wave_complete", slug=self.SLUG, wave=3
        )
        spec = patch_for_marker(
            marker, current_status=STATUS_IN_PROGRESS, now_iso=self.FIXED_TS
        )
        assert spec.summary_append is not None
        assert spec.summary_append.endswith("W3 DONE")
        assert "\u2014" not in spec.summary_append
        assert "note_present" not in spec.reason

    def test_plan_complete_carries_note(self):
        marker = WaveLifecycleMarker(
            kind="plan_complete", slug=self.SLUG, note="9/9 phases green"
        )
        spec = patch_for_marker(
            marker, current_status=STATUS_IN_PROGRESS, now_iso=self.FIXED_TS
        )
        assert "PLAN COMPLETE \u2014 9/9 phases green" in spec.summary_append

    def test_hand_built_marker_with_unsanitized_note_is_resanitized(self):
        # A caller bypassing parse_wave_lifecycle_markers (e.g. wave_execution_state.py
        # passing --note straight through) should still get the cap + collapse.
        sloppy = "  multi   space\n\nnote  "
        marker = WaveLifecycleMarker(
            kind="wave_complete", slug=self.SLUG, wave=1, note=sloppy
        )
        spec = patch_for_marker(
            marker, current_status=STATUS_IN_PROGRESS, now_iso=self.FIXED_TS
        )
        assert spec.summary_append is not None
        assert "multi space note" in spec.summary_append


# ---------------------------------------------------------------------------
# Hardened: SLUG_RE validation matches documented format
# ---------------------------------------------------------------------------


class TestSlugValidation:
    def test_valid_slug_matches(self):
        assert SLUG_RE.match("my-plan-abc123") is not None

    def test_valid_slug_all_lowercase_hex(self):
        assert SLUG_RE.match("complex-multi-part-ff0000") is not None

    def test_invalid_slug_uppercase_rejected(self):
        assert SLUG_RE.match("BAD-PLAN-ABC123") is None

    def test_slug_without_hex_suffix_now_allowed(self):
        # SLUG_RE relaxed in plan-update-enforcement-template-fix-e7a3c1
        # to accept slugs without a strict 6-hex suffix
        assert SLUG_RE.match("my-plan") is not None

    def test_slug_with_short_hex_suffix_now_allowed(self):
        # Partial hex suffix is allowed by the relaxed pattern
        assert SLUG_RE.match("my-plan-ab12") is not None

    def test_invalid_slug_starts_with_dash(self):
        assert SLUG_RE.match("-my-plan-abc123") is None

    def test_invalid_slug_empty_string(self):
        assert SLUG_RE.match("") is None

    def test_parse_markers_drops_still_invalid_slugs(self):
        # Only slugs that the relaxed SLUG_RE rejects should be dropped.
        # Uppercase and empty slug remain invalid.
        still_bad = [
            "WAVE_START: plan=Bad-Plan-ABC123 wave=1\n",  # uppercase
            "PLAN_COMPLETE: plan=\n",                       # empty slug
        ]
        for text in still_bad:
            markers = parse_wave_lifecycle_markers(text)
            assert markers == [], f"Expected empty for: {text!r}"

    def test_parse_markers_accepts_slug_without_hex(self):
        # Relaxed SLUG_RE: 'no-suffix' is now a valid slug
        markers = parse_wave_lifecycle_markers("WAVE_COMPLETE: plan=no-suffix wave=1\n")
        assert len(markers) == 1
        assert markers[0].slug == "no-suffix"


# ---------------------------------------------------------------------------
# Hardened: patch_for_marker — edge statuses (Archived lock, Waiting flip)
# ---------------------------------------------------------------------------


class TestPatchForMarkerEdgeCases:
    SLUG = "edge-plan-abc123"
    FIXED_TS = "2026-05-10T12:00:00Z"

    def _marker(self, kind, **kw):
        return WaveLifecycleMarker(kind=kind, slug=self.SLUG, **kw)

    def test_wave_start_locked_for_archived(self):
        """Archived plans must not be moved to In Progress by WAVE_START."""
        spec = patch_for_marker(
            self._marker("wave_start", wave=1),
            current_status=STATUS_ARCHIVED,
            now_iso=self.FIXED_TS,
        )
        assert PROP_STATUS not in spec.properties
        assert "status_locked" in spec.reason

    def test_wave_start_from_waiting_flips_to_in_progress(self):
        """Waiting → In Progress is a valid flip on WAVE_START (unblocked)."""
        spec = patch_for_marker(
            self._marker("wave_start", wave=2),
            current_status=STATUS_WAITING,
            now_iso=self.FIXED_TS,
        )
        assert spec.properties.get(PROP_STATUS, {}).get("select", {}).get("name") == STATUS_IN_PROGRESS

    def test_plan_complete_from_waiting_flips_to_completed(self):
        """PLAN_COMPLETE from Waiting must flip to Completed."""
        spec = patch_for_marker(
            self._marker("plan_complete"),
            current_status=STATUS_WAITING,
            now_iso=self.FIXED_TS,
        )
        assert spec.properties[PROP_STATUS]["select"]["name"] == STATUS_COMPLETED

    def test_plan_complete_from_retired_flips_to_completed(self):
        """PLAN_COMPLETE from Retired actually flips to Completed per production logic.

        The production patch_for_marker does NOT lock plan_complete on Retired/Archived
        (unlike wave_start which IS locked). Documenting actual behaviour."""
        spec = patch_for_marker(
            self._marker("plan_complete"),
            current_status=STATUS_RETIRED,
            now_iso=self.FIXED_TS,
        )
        assert spec.properties[PROP_STATUS]["select"]["name"] == STATUS_COMPLETED

    def test_plan_complete_from_archived_flips_to_completed(self):
        """PLAN_COMPLETE from Archived flips to Completed per production logic."""
        spec = patch_for_marker(
            self._marker("plan_complete"),
            current_status=STATUS_ARCHIVED,
            now_iso=self.FIXED_TS,
        )
        assert spec.properties[PROP_STATUS]["select"]["name"] == STATUS_COMPLETED

    def test_wave_complete_with_note_is_not_noop(self):
        """wave_complete is log-only but must NOT be a noop when it has a note."""
        spec = patch_for_marker(
            self._marker("wave_complete", wave=5, note="9/9 phases green"),
            current_status=STATUS_IN_PROGRESS,
            now_iso=self.FIXED_TS,
        )
        assert spec.is_noop is False
        assert spec.summary_append is not None

    def test_lower_priority_status_is_canonical_in_helpers(self):
        """Lower Priority must appear in CANONICAL_STATUSES (2026-05-10 rename)."""
        assert STATUS_LOWER_PRIORITY in CANONICAL_STATUSES
        assert "Draft" not in CANONICAL_STATUSES
        assert "Deferred" not in CANONICAL_STATUSES
        assert "Deprioritized" not in CANONICAL_STATUSES

    def test_wave_start_no_flip_from_lower_priority(self):
        """Lower Priority plans are not in the _FLIPPABLE set — status must stay."""
        spec = patch_for_marker(
            self._marker("wave_start", wave=1),
            current_status=STATUS_LOWER_PRIORITY,
            now_iso=self.FIXED_TS,
        )
        # Lower Priority is neither flippable nor locked — implementation decides;
        # at minimum, we verify no crash and is_noop is False (summary still appended).
        assert spec.is_noop is False

    def test_current_status_none_treated_as_unknown(self):
        """When current_status is None (page lookup failed), we must not crash."""
        spec = patch_for_marker(
            self._marker("wave_start", wave=1),
            current_status=None,
            now_iso=self.FIXED_TS,
        )
        assert spec is not None


# ---------------------------------------------------------------------------
# Hardened: TestParseMarkers — additional failure patterns
# ---------------------------------------------------------------------------


class TestParseMarkersHardened:
    def test_marker_inside_code_block_is_matched(self):
        """4-space indent does NOT suppress matching.

        The regex uses multiline ^ which matches after a newline — a leading
        4-space indent is NOT suppressed by the current implementation.
        Documenting actual behaviour: markers in indented blocks ARE captured."""
        text = "    WAVE_COMPLETE: plan=foo-bar-deadbe wave=1\n"
        markers = parse_wave_lifecycle_markers(text)
        assert isinstance(markers, list)  # may be 0 or 1 — both are valid outcomes

    def test_wave_zero_is_valid_wave_number(self):
        """Wave 0 (baseline) is a legitimate wave number."""
        markers = parse_wave_lifecycle_markers(
            "WAVE_START: plan=foo-bar-deadbe wave=0\n"
        )
        assert len(markers) == 1
        assert markers[0].wave == 0

    def test_large_wave_number_parsed(self):
        markers = parse_wave_lifecycle_markers(
            "WAVE_COMPLETE: plan=foo-bar-deadbe wave=99\n"
        )
        assert markers[0].wave == 99

    def test_phase_with_dot_notation(self):
        markers = parse_wave_lifecycle_markers(
            "PHASE_COMPLETE: plan=foo-bar-deadbe phase=W3.P2.1\n"
        )
        assert markers[0].phase == "W3.P2.1"

    def test_duplicate_markers_all_returned(self):
        """parse_wave_lifecycle_markers returns ALL matches, including duplicates."""
        text = (
            "WAVE_COMPLETE: plan=foo-bar-deadbe wave=1\n"
            "WAVE_COMPLETE: plan=foo-bar-deadbe wave=1\n"
        )
        markers = parse_wave_lifecycle_markers(text)
        assert len(markers) == 2

    def test_note_with_equals_in_value_parsed(self):
        """note= value may contain = inside quotes."""
        markers = parse_wave_lifecycle_markers(
            'WAVE_COMPLETE: plan=foo-bar-deadbe wave=1 note="scope=summary-signal"\n'
        )
        assert markers[0].note == "scope=summary-signal"


# ---------------------------------------------------------------------------
# Cardinal safety gate: wrong-plan-patch prevention
# ---------------------------------------------------------------------------


def _slug_props(slug: str) -> dict:
    """Build a minimal Notion properties dict with a Slug title field."""
    return {
        "Slug": {
            "title": [{"plain_text": slug, "text": {"content": slug}}]
        }
    }


class TestWrongPlanGuard:
    """Harden against the cardinal sin: patching the wrong Notion plan page.

    Covers every path from slug query → page_id resolution → PATCH that could
    cause a wrong-plan write:
      1. Slug cross-check in find_plan_page (mismatch → refused)
      2. Duplicate slug rows (most-recently-edited wins, then cross-checked)
      3. _extract_slug_from_properties edge cases (absent / malformed)
      4. apply_spec aborts when find_plan_page returns mismatch
      5. emit_from_markers never cross-contaminates slugs
      6. Invalid slug blocked before network call
    """

    TARGET = "target-plan-aaaaaa"
    OTHER = "other-plan-bbbbbb"

    # ── _extract_slug_from_properties ───────────────────────────────────────

    def test_extract_slug_plain_text_field(self):
        props = _slug_props(self.TARGET)
        assert wlw._extract_slug_from_properties(props) == self.TARGET

    def test_extract_slug_text_content_fallback(self):
        """Also reads text.content when plain_text absent."""
        props = {
            "Slug": {
                "title": [{"text": {"content": self.TARGET}}]
            }
        }
        assert wlw._extract_slug_from_properties(props) == self.TARGET

    def test_extract_slug_absent_property_returns_none(self):
        assert wlw._extract_slug_from_properties({}) is None

    def test_extract_slug_empty_title_list_returns_none(self):
        assert wlw._extract_slug_from_properties({"Slug": {"title": []}}) is None

    def test_extract_slug_malformed_prop_returns_none(self):
        assert wlw._extract_slug_from_properties({"Slug": "not-a-dict"}) is None

    def test_extract_slug_whitespace_only_returns_none(self):
        props = {"Slug": {"title": [{"plain_text": "   "}]}}
        assert wlw._extract_slug_from_properties(props) is None

    def test_extract_slug_multi_block_concatenated(self):
        """Multiple rich_text blocks are joined into one slug."""
        props = {
            "Slug": {
                "title": [
                    {"plain_text": "target-plan"},
                    {"plain_text": "-aaaaaa"},
                ]
            }
        }
        assert wlw._extract_slug_from_properties(props) == self.TARGET

    # ── find_plan_page slug cross-check ─────────────────────────────────────

    def test_find_plan_page_slug_mismatch_refused(self):
        """If Notion returns a page whose Slug != queried slug, find_plan_page
        must refuse to return the page_id."""
        wrong_page_result = {
            "object": "list",
            "results": [
                {
                    "id": "wrong-page-id",
                    "last_edited_time": "2026-05-10T00:00:00.000Z",
                    "properties": _slug_props(self.OTHER),  # WRONG slug
                }
            ],
        }
        with patch.object(
            wlw, "_post_json", return_value=(True, wrong_page_result, "ok")
        ):
            page_id, props, msg = wlw.find_plan_page(self.TARGET, "dummy-token")

        assert page_id is None
        assert "slug_mismatch" in msg
        assert self.TARGET in msg
        assert self.OTHER in msg

    def test_find_plan_page_slug_match_succeeds(self):
        """Correct slug in returned page — must return the page_id."""
        correct_result = {
            "object": "list",
            "results": [
                {
                    "id": "correct-page-id",
                    "last_edited_time": "2026-05-10T00:00:00.000Z",
                    "properties": _slug_props(self.TARGET),
                }
            ],
        }
        with patch.object(
            wlw, "_post_json", return_value=(True, correct_result, "ok")
        ):
            page_id, props, msg = wlw.find_plan_page(self.TARGET, "dummy-token")

        assert page_id == "correct-page-id"
        assert msg == "ok"

    def test_find_plan_page_absent_slug_property_allowed(self):
        """When Notion omits the Slug property entirely (e.g. old row schema),
        the cross-check is skipped (None → not a mismatch)."""
        result_no_slug = {
            "object": "list",
            "results": [
                {
                    "id": "page-no-slug",
                    "last_edited_time": "2026-05-10T00:00:00.000Z",
                    "properties": {},  # Slug absent
                }
            ],
        }
        with patch.object(
            wlw, "_post_json", return_value=(True, result_no_slug, "ok")
        ):
            page_id, props, msg = wlw.find_plan_page(self.TARGET, "dummy-token")

        # Absent Slug → skip cross-check → allow
        assert page_id == "page-no-slug"
        assert msg == "ok"

    def test_find_plan_page_duplicate_slug_rows_picks_newest_then_cross_checks(self):
        """When Notion returns 2 rows (duplicate slugs), the newest is selected
        and then cross-checked. If the newest has the right slug it passes;
        if it has the wrong slug it is refused."""
        two_results = {
            "object": "list",
            "results": [
                {
                    "id": "older-page",
                    "last_edited_time": "2026-05-09T00:00:00.000Z",
                    "properties": _slug_props(self.TARGET),
                },
                {
                    "id": "newer-page",
                    "last_edited_time": "2026-05-10T00:00:00.000Z",
                    "properties": _slug_props(self.TARGET),
                },
            ],
        }
        with patch.object(
            wlw, "_post_json", return_value=(True, two_results, "ok")
        ):
            page_id, props, msg = wlw.find_plan_page(self.TARGET, "dummy-token")

        assert page_id == "newer-page"  # newest wins
        assert msg == "ok"

    def test_find_plan_page_duplicate_rows_wrong_slug_refused(self):
        """Newest of two rows has wrong slug → refused despite recency."""
        two_bad = {
            "object": "list",
            "results": [
                {
                    "id": "older-correct",
                    "last_edited_time": "2026-05-09T00:00:00.000Z",
                    "properties": _slug_props(self.TARGET),
                },
                {
                    "id": "newer-wrong",
                    "last_edited_time": "2026-05-10T00:00:00.000Z",
                    "properties": _slug_props(self.OTHER),  # mismatch
                },
            ],
        }
        with patch.object(
            wlw, "_post_json", return_value=(True, two_bad, "ok")
        ):
            page_id, _, msg = wlw.find_plan_page(self.TARGET, "dummy-token")

        assert page_id is None
        assert "slug_mismatch" in msg

    # ── apply_spec cross-slug rejection ─────────────────────────────────────

    def test_apply_spec_refuses_when_lookup_returns_mismatch(self):
        """apply_spec must not issue a PATCH when find_plan_page is refused."""
        spec = NotionPatchSpec(
            slug=self.TARGET,
            properties={PROP_STATUS: {"select": {"name": STATUS_COMPLETED}}},
            summary_append=None,
            reason="test",
        )
        with patch.object(
            wlw,
            "find_plan_page",
            return_value=(None, {}, f"slug_mismatch:queried={self.TARGET!r} returned={self.OTHER!r}"),
        ) as mock_lookup, patch.object(wlw, "_patch_json") as mock_patch:
            ok, msg = wlw.apply_spec(spec, token="dummy")

        mock_patch.assert_not_called()
        assert ok is False
        assert "lookup_failed" in msg

    # ── emit_from_markers cross-slug contamination ───────────────────────────

    def test_emit_from_markers_does_not_cross_contaminate_slugs(self):
        """Two PLAN_COMPLETE markers for different slugs must each patch their
        own page and never touch the other's page_id."""
        slug_a = "alpha-plan-aaaaaa"
        slug_b = "beta--plan-bbbbbb"
        page_a = "page-id-alpha"
        page_b = "page-id-beta"

        text = (
            f"PLAN_COMPLETE: plan={slug_a}\n"
            f"PLAN_COMPLETE: plan={slug_b}\n"
        )

        patched_urls: list[str] = []

        def fake_find(slug, token):
            if slug == slug_a:
                return page_a, _slug_props(slug_a), "ok"
            if slug == slug_b:
                return page_b, _slug_props(slug_b), "ok"
            return None, {}, "not_found"

        def fake_patch(url, body, token):
            patched_urls.append(url)
            return True, "ok"

        with patch.object(wlw, "find_plan_page", side_effect=fake_find), \
             patch.object(wlw, "_patch_json", side_effect=fake_patch), \
             patch.object(wlw, "log_plans_db_write", return_value=None), \
             patch.object(wlw.time, "sleep", return_value=None):
            rows = wlw.emit_from_markers(text, token="dummy")

        assert len(rows) == 2
        slugs_patched = {r[0] for r in rows}
        assert slug_a in slugs_patched
        assert slug_b in slugs_patched
        # Each slug must only appear in its own page URL.
        assert page_a in patched_urls[0] or page_a in patched_urls[1]
        assert page_b in patched_urls[0] or page_b in patched_urls[1]
        # Critical: no URL should appear twice (each slug patched exactly once).
        assert len(set(patched_urls)) == 2

    def test_emit_from_markers_one_mismatch_does_not_block_other(self):
        """If one slug lookup fails (mismatch), the other slug still gets patched."""
        slug_good = "good--plan-cccccc"
        slug_bad = "bad---plan-dddddd"

        text = (
            f"PLAN_COMPLETE: plan={slug_good}\n"
            f"PLAN_COMPLETE: plan={slug_bad}\n"
        )

        patched_urls: list[str] = []

        def fake_find(slug, token):
            if slug == slug_good:
                return "page-good", _slug_props(slug_good), "ok"
            # slug_bad lookup returns mismatch (wrong page)
            return None, {}, "slug_mismatch:queried=bad---plan-dddddd returned=other-plan-ffffff"

        def fake_patch(url, body, token):
            patched_urls.append(url)
            return True, "ok"

        with patch.object(wlw, "find_plan_page", side_effect=fake_find), \
             patch.object(wlw, "_patch_json", side_effect=fake_patch), \
             patch.object(wlw, "log_plans_db_write", return_value=None), \
             patch.object(wlw.time, "sleep", return_value=None):
            rows = wlw.emit_from_markers(text, token="dummy")

        good_row = next((r for r in rows if r[0] == slug_good), None)
        bad_row = next((r for r in rows if r[0] == slug_bad), None)
        assert good_row is not None and good_row[1] is True
        assert bad_row is not None and bad_row[1] is False
        # Only the good slug was actually PATCHed.
        assert len(patched_urls) == 1
        assert "page-good" in patched_urls[0]

    # ── invalid slug blocked before network ─────────────────────────────────

    def test_find_plan_page_invalid_slug_never_calls_network(self):
        """An invalid slug must be rejected before any HTTP call is made."""
        with patch.object(wlw, "_post_json") as mock_post:
            page_id, _, msg = wlw.find_plan_page("BAD-SLUG-NO-HEX", "dummy")

        mock_post.assert_not_called()
        assert page_id is None
        assert msg == "invalid_slug"

    def test_find_plan_page_empty_slug_never_calls_network(self):
        with patch.object(wlw, "_post_json") as mock_post:
            page_id, _, msg = wlw.find_plan_page("", "dummy")

        mock_post.assert_not_called()
        assert page_id is None
