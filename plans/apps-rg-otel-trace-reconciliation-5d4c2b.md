---
plan_id: apps-rg-otel-trace-reconciliation-5d4c2b
plan_format: v2
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
supersedes: []
---

# apps_rg OTel Trace Reconciliation Consumer

Add a post-run trace reconciliation artifact so apps_rg OTel snapshots are consumed by apps_eval and L6 without becoming current-run control input.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: W3
LAST_COMPLETED_WAVE: W3
LAST_UPDATED: 2026-06-28

---

## Context (SCQA)

- **Situation** - apps_rg can emit local receipts and optional OTel spans, but full end-to-end learning currently consumes local artifacts rather than the OTel backend.
- **Complication** - Without a deterministic post-run consumer, OTel remains emit-only and does not help apps_eval/L6 explain missing spans, fallback timing, or trace gaps.
- **Question** - How should OTel be consumed without letting a laggy external backend alter X1-X3, UWG, or product disposition?
- **Answer** - Emit a bounded `trace_reconciliation.json/jsonl` after receipts are sealed, have apps_eval grade it as observability evidence, and include its refs in L6 handoff/learning.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1, W1.2 | Reconciliation artifact | ~9K | Local receipts remain proof authority | DONE | Builder writes deterministic JSON/JSONL and handles missing OTel as WARN |
| W2 | W2.1, W2.2 | L6 and apps_eval consumption | ~10K | Existing L6/apps_eval contracts can carry optional refs | DONE | L6 package/handoff/learning and apps_eval scorecards consume refs |
| W3 | W3.1, W3.2 | Verification and receipts | ~6K | Focused tests are enough for the vertical slice | DONE | Targeted pytest and plan checks pass |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Define trace reconciliation schema and builder | DONE |
| W1.2 | Emit reconciliation JSON/JSONL from L6 v40 runner | DONE |
| W2.1 | Surface reconciliation refs in L6 handoff and learning | DONE |
| W2.2 | Add apps_eval optional microstep consumption | DONE |
| W3.1 | Add focused unit tests | DONE |
| W3.2 | Run targeted verification and close receipts | DONE |

---

## Out Of Scope

- Querying the Docker OTel backend directly from apps_rg runtime.
- Allowing OTel to change X1-X3, UWG, exit code, or product artifacts.
- Runtime ADG ingest beyond producing a bounded artifact suitable for later ingest.
- Full apps_rg live E2E generation.

---

## Wave 1 - Reconciliation Artifact

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: A

**Authorization**: USER_APPROVED - user approved the design on 2026-06-28.

**Phases**:
- **W1.1** - Define trace reconciliation schema and pure builder | ~5K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** - Emit reconciliation JSON/JSONL from L6 v40 runner | ~4K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- Missing OTel produces `TRACE_UNAVAILABLE`, not a run failure.
- Local provider attempt receipts remain authoritative.
- Reconciliation rows include future-run-only observability findings.

---

## Wave 2 - Downstream Consumption

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: B

**Phases**:
- **W2.1** - Surface reconciliation refs in L6 package, handoff, and learning | ~5K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W2.2** - Add apps_eval optional microstep consumption | ~5K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- L6 handoff and learning records include `trace_reconciliation_ref`.
- apps_eval can score `TRACE_RECONCILED`, `TRACE_PARTIAL`, `TRACE_MISMATCH`, and `TRACE_UNAVAILABLE`.
- Optional rows avoid breaking older fixtures that have no reconciliation artifact.

---

## Wave 3 - Verification

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: C

**Phases**:
- **W3.1** - Add focused unit tests | ~3K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W3.2** - Run targeted verification and close receipts | ~3K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- Focused reconciliation, L6 runner, and apps_eval microstep tests pass.
- Plan format checks pass.
- Final writeback records ADG degraded fallback provenance.

---

## Definition of Done

- `trace_reconciliation.json` and `trace_reconciliation_rows.jsonl` are emitted post-run.
- L6 v40 package, L6 handoff, and L6 learning records reference the reconciliation artifact.
- apps_eval has an optional scorecard row that consumes reconciliation verdicts.
- Missing OTel does not fail current-run product behavior.
- Targeted tests pass and unrelated dirty worktree changes are untouched.

---

## Evidence

- ADG Provenance: backend=sqlite DEGRADED_FALLBACK, snapshot=adg_indexed_06272026_2302.sqlite, reason=adg_sqlite MCP transport closed.
- Verification: `python -m pytest tests/unit/apps_rg/runtime/observability/test_trace_reconciliation.py tests/apps_rg/test_l6_v40_shadow_eval_runner.py apps_eval/tests/test_apps_rg_microstep_scorecards.py apps_eval/tests/test_l6_handoff_shape.py tests/e2e/test_l6_v40_apps_rg_apps_eval.py tests/unit/apps_rg/test_l6_microstep_observability.py -q` -> 12 passed.
- Hygiene: `python -m ruff check --select F401,E402,I <changed python files>` -> all checks passed.
- Plan check: `python ops_scripts/ci/check_plan_format_compliance.py --advisory --paths plans/apps-rg-otel-trace-reconciliation-5d4c2b.md` -> 0 fail/error/warn.
