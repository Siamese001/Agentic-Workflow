#!/usr/bin/env python3
"""Tests for consolidated wave summary at top (PLAN-WAVE-TOP)."""

from __future__ import annotations

from ops_scripts.ci.plan_wave_summary_top import (
    WaveSummarySeverity,
    is_plan_format_v2,
    validate_consolidated_wave_summary_at_top,
    validate_plan_format,
)


def _minimal_plan(*, with_status_tables: bool = True, wave_before_tables: bool = False) -> str:
    markers = """FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W1
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-01-01
"""
    wave_detail = """## Wave 1 — First

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
"""
    tables = """
## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1 | Scope | ~10K | — | TODO | Done when green |

"""
    body = f"""---
plan_id: test-plan-abc123
---

# Test

{markers}
"""
    if wave_before_tables and with_status_tables:
        return body + wave_detail + tables
    if with_status_tables:
        return body + tables + wave_detail
    return body + wave_detail


class TestWaveSummaryAtTop:
    def test_valid_plan_passes(self):
        content = _minimal_plan()
        violations = validate_consolidated_wave_summary_at_top(content, ".codex/plans/x.md")
        fails = [v for v in violations if v.severity == WaveSummarySeverity.FAIL]
        assert fails == []

    def test_missing_status_tables_fails(self):
        content = _minimal_plan(with_status_tables=False)
        violations = validate_consolidated_wave_summary_at_top(content, ".codex/plans/x.md")
        assert any(v.rule_id == "WS-TOP-1" for v in violations)

    def test_wave_detail_before_tables_fails(self):
        content = _minimal_plan(wave_before_tables=True)
        violations = validate_consolidated_wave_summary_at_top(content, ".codex/plans/x.md")
        assert any(v.rule_id in {"WS-TOP-2", "WS-TOP-4", "WS-TOP-5", "WS-TOP-6"} for v in violations)

    def test_dod_exempt_skips(self):
        content = """---
dod_exempt: true
---

## Wave 1 — Only

WAVE_ID: W1
"""
        violations = validate_consolidated_wave_summary_at_top(content, ".codex/plans/x.md")
        assert violations == []

    def test_archive_path_skips(self):
        content = _minimal_plan(with_status_tables=False)
        violations = validate_consolidated_wave_summary_at_top(
            content,
            ".codex/plans/_archive/2026-05/x.md",
        )
        assert violations == []

    def test_short_columns_warn_not_fail(self):
        content = """---
plan_id: test-plan-abc123
---

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W1
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-01-01

## Status Tables

### Wave Progress

| Wave | Focus | Status |
|------|-------|--------|
| W1 | Work | TODO |

## Wave 1 — First

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
"""
        violations = validate_consolidated_wave_summary_at_top(content, ".codex/plans/x.md")
        fails = [v for v in violations if v.severity == WaveSummarySeverity.FAIL]
        warns = [v for v in violations if v.severity == WaveSummarySeverity.WARN]
        assert fails == []
        assert any(v.rule_id == "WS-TOP-7" for v in warns)


_V2_WAVE_COLS = (
    "| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |\n"
    "|------|-----------|-------|-------------|-------------|--------|------------------|\n"
    "| W1 | W1.1 | Scope1 | ~10K | — | TODO | done |\n"
    "| W2 | W2.1 | Scope2 | ~10K | — | TODO | done |\n"
)
_V2_SHORT_COLS = "| Wave | Focus | Status |\n|------|-------|--------|\n| W1 | Scope1 | TODO |\n| W2 | S2 | TODO |\n"
_V2_PHASE = (
    "\n### Phase Progress\n\n| Phase | Title | Status |\n|-------|-------|--------|\n"
    "| W1.1 | First | TODO |\n| W2.1 | Second | TODO |\n"
)
_V2_DETAIL = "## Wave 1 — First\n\nWAVE_ID: W1\n\n## Wave 2 — Second\n\nWAVE_ID: W2\n"


def _v2_plan(*, with_phase: bool = True, short_cols: bool = False, wave_detail: str | None = None, v2: bool = True) -> str:
    fm = "plan_format: v2\n" if v2 else ""
    cols = _V2_SHORT_COLS if short_cols else _V2_WAVE_COLS
    phase = _V2_PHASE if with_phase else ""
    detail = wave_detail if wave_detail is not None else _V2_DETAIL
    return (
        f"---\nplan_id: test-plan-abc123\n{fm}---\n\n# Test\n\n## Context (SCQA)\n- s\n\n"
        "## Status Tables\n\n### Wave Progress\n\n" + cols + phase + "\n" + detail
    )


def _fail_ids(content: str) -> set[str]:
    return {v.rule_id for v in validate_plan_format(content, ".codex/plans/x.md") if v.severity == WaveSummarySeverity.FAIL}


class TestPlanFormatV2:
    def test_v2_marker_detected(self):
        assert is_plan_format_v2("---\nplan_format: v2\n---\n")
        assert is_plan_format_v2("body\nPLAN_FORMAT: v2\nmore")
        assert not is_plan_format_v2("---\nplan_id: x\n---\n")

    def test_compliant_v2_plan_passes(self):
        assert _fail_ids(_v2_plan()) == set()

    def test_missing_phase_table_fails(self):
        assert "WS-PHASE-1" in _fail_ids(_v2_plan(with_phase=False))

    def test_short_columns_fail_for_v2(self):
        assert "WS-TOP-7" in _fail_ids(_v2_plan(short_cols=True))

    def test_out_of_order_wave_headings_fail(self):
        detail = "## Wave 2 — Second\n\nWAVE_ID: W2\n\n## Wave 1 — First\n\nWAVE_ID: W1\n"
        assert "WS-ORDER-1" in _fail_ids(_v2_plan(wave_detail=detail))

    def test_dependency_on_higher_wave_fails(self):
        detail = (
            "## Wave 1 — First\n\nWAVE_ID: W1\nThis wave depends on W2 finishing.\n\n"
            "## Wave 2 — Second\n\nWAVE_ID: W2\n"
        )
        assert "WS-ORDER-2" in _fail_ids(_v2_plan(wave_detail=detail))

    def test_before_inversion_fails(self):
        detail = (
            "## Wave 1 — First\n\nWAVE_ID: W1\nNote: W3 before W1 is required.\n\n"
            "## Wave 2 — Second\n\nWAVE_ID: W2\n\n## Wave 3 — Third\n\nWAVE_ID: W3\n"
        )
        assert "WS-ORDER-3" in _fail_ids(_v2_plan(wave_detail=detail))

    def test_legacy_plan_grandfathered_no_new_fails(self):
        # No plan_format: v2 marker → out-of-order + missing phase must NOT produce the v2-only FAILs.
        detail = "## Wave 2 — Second\n\nWAVE_ID: W2\n\n## Wave 1 — First\n\nWAVE_ID: W1\n"
        ids = _fail_ids(_v2_plan(with_phase=False, wave_detail=detail, v2=False))
        assert "WS-PHASE-1" not in ids
        assert "WS-ORDER-1" not in ids
        assert "WS-TOP-7" not in ids  # short/legacy columns stay WARN, not FAIL
