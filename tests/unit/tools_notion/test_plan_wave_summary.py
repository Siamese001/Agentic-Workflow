from __future__ import annotations

from tools.notion.plan_wave_summary import (
    build_plan_notion_ai_summary,
    build_plan_notion_summary,
    extract_closeout_notes,
    extract_phase_rows,
    extract_wave_rows,
)
from tools.notion.register_ondisk_plans_batch import _extract_summary


PLAN_TEXT = """---
plan_id: apps-rg-c02-bootstrap-gate-correctness-c02f1a
plan_format: v2
---

# apps_rg AIG E2E Durability

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: COMPLETE
LAST_COMPLETED_WAVE: W3
LAST_UPDATED: 2026-06-10

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1, W1.2 | C0.2 evidence bootstrap durability -- dense+sparse provisioner | ~40K | reusable builders | DONE | Fresh worktree provisions dense + sparse |
| W2 | W2.1, W2.2 | bundle_consumed crash durability | ~18K | fix present | DONE | No TypeError on X2 gates |
| W3 | W3.1, W3.2 | single_thought decimal correctness | ~24K | shared validator | DONE | Decimal bullets pass |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Unify dense+sparse bootstrap | DONE |
| W1.2 | Wire bootstrap into seed/readiness | DONE |
| W2.1 | Regression test bundle_consumed | DONE |

## Execution Closeout

CLOSEOUT_WAVE_COMPLETE: plan=apps-rg-c02-bootstrap-gate-correctness-c02f1a wave=1 note="dense+sparse fact_vectors bootstrap complete"
PHASE_COMPLETE: plan=apps-rg-c02-bootstrap-gate-correctness-c02f1a phase=W2.1 note="bundle_consumed regression complete"
CLOSEOUT_WAVE_COMPLETE: plan=apps-rg-c02-bootstrap-gate-correctness-c02f1a wave=3 note="sentence-aware validator migration complete"
PLAN_COMPLETE: plan=apps-rg-c02-bootstrap-gate-correctness-c02f1a note="W1-W3 verification complete"
"""


def test_extracts_wave_phase_and_closeout_notes() -> None:
    waves = extract_wave_rows(PLAN_TEXT)
    phases = extract_phase_rows(PLAN_TEXT)
    notes = extract_closeout_notes(PLAN_TEXT)

    assert [w.wave for w in waves] == ["W1", "W2", "W3"]
    assert waves[0].status == "DONE"
    assert phases[0].phase == "W1.1"
    assert [n.label for n in notes] == ["W1", "W2.1", "W3", "PLAN"]
    assert notes[-1].note == "W1-W3 verification complete"


def test_build_plan_notion_summary_includes_required_dashboard_signals() -> None:
    summary = build_plan_notion_summary(PLAN_TEXT)

    assert "PLAN_STATUS=DONE" in summary
    assert "CURRENT_WAVE=COMPLETE" in summary
    assert "LAST_COMPLETED_WAVE=W3" in summary
    assert "W1 DONE: C0.2 evidence bootstrap durability" in summary
    assert "W2 DONE: bundle_consumed crash durability" in summary
    assert "Phases: W1.1 DONE; W1.2 DONE; W2.1 DONE." in summary
    assert "W1: dense+sparse fact_vectors bootstrap complete" in summary
    assert "PLAN: W1-W3 verification complete" in summary
    assert len(summary) <= 2000


def test_build_plan_notion_ai_summary_is_short_and_statusful() -> None:
    ai_summary = build_plan_notion_ai_summary(PLAN_TEXT)

    assert ai_summary.startswith("DONE:")
    assert "W1, W2, W3 complete" in ai_summary
    assert len(ai_summary) <= 180


def test_batch_registration_uses_wave_aware_summary() -> None:
    summary = _extract_summary(PLAN_TEXT)

    assert "Overall: PLAN_STATUS=DONE" in summary
    assert "Closeout notes:" in summary
    assert "first non-header" not in summary.lower()
