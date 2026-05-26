#!/usr/bin/env python3
"""Tests for consolidated wave summary at top (PLAN-WAVE-TOP)."""

from __future__ import annotations

from ops_scripts.ci.plan_wave_summary_top import (
    WaveSummarySeverity,
    validate_consolidated_wave_summary_at_top,
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
        violations = validate_consolidated_wave_summary_at_top(content, ".cursor/plans/x.md")
        fails = [v for v in violations if v.severity == WaveSummarySeverity.FAIL]
        assert fails == []

    def test_missing_status_tables_fails(self):
        content = _minimal_plan(with_status_tables=False)
        violations = validate_consolidated_wave_summary_at_top(content, ".cursor/plans/x.md")
        assert any(v.rule_id == "WS-TOP-1" for v in violations)

    def test_wave_detail_before_tables_fails(self):
        content = _minimal_plan(wave_before_tables=True)
        violations = validate_consolidated_wave_summary_at_top(content, ".cursor/plans/x.md")
        assert any(v.rule_id in {"WS-TOP-2", "WS-TOP-4", "WS-TOP-5", "WS-TOP-6"} for v in violations)

    def test_dod_exempt_skips(self):
        content = """---
dod_exempt: true
---

## Wave 1 — Only

WAVE_ID: W1
"""
        violations = validate_consolidated_wave_summary_at_top(content, ".cursor/plans/x.md")
        assert violations == []

    def test_archive_path_skips(self):
        content = _minimal_plan(with_status_tables=False)
        violations = validate_consolidated_wave_summary_at_top(
            content,
            ".cursor/plans/_archive/2026-05/x.md",
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
        violations = validate_consolidated_wave_summary_at_top(content, ".cursor/plans/x.md")
        fails = [v for v in violations if v.severity == WaveSummarySeverity.FAIL]
        warns = [v for v in violations if v.severity == WaveSummarySeverity.WARN]
        assert fails == []
        assert any(v.rule_id == "WS-TOP-7" for v in warns)
