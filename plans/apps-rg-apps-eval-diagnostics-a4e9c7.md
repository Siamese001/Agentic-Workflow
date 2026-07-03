---
plan_id: apps-rg-apps-eval-diagnostics-a4e9c7
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

# Apps RG Apps Eval Diagnostics

Add post-run diagnostic observations for `apps_rg` in `apps_eval` without changing the deterministic scorecard contract.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: IN_PROGRESS
CURRENT_WAVE: W3
LAST_COMPLETED_WAVE: W3
LAST_UPDATED: 2026-07-03

---

## Context (SCQA)

- **Situation** — `apps_eval` already emits deterministic `apps_rg` scorecards, coverage matrices, component scorecards, regression summaries, release gates, and optional L6 handoff artifacts.
- **Complication** — It does not yet emit non-authoritative diagnostics explaining graph sufficiency, retrieval quality, L2 retry causes, X1D judge categories, E4 heal opportunities, L1 planning rigor, or L0/cache posture.
- **Question** — How do we add richer `apps_rg` diagnostic evidence without duplicating current required microsteps or giving `apps_eval` runtime authority?
- **Answer** — Add a separate diagnostic observation schema and artifacts that consume existing post-run receipts, carry source refs/digests, and stay shadow-only.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1, W1.2 | Diagnostic schema, artifact contract, and validation | ~8K | Existing scorecard contract remains stable | DONE | Diagnostic rows validate independently and cannot mutate scorecards |
| W2 | W2.1, W2.2 | `apps_rg` diagnostic collection and emission | ~12K | Existing runtime artifacts contain enough evidence for shadow observations | DONE | `diagnostic_rows.jsonl` and `diagnostic_summary.json` emit after scorecard artifacts |
| W3 | W3.1, W3.2 | Tests, trend integration, and regression proof | ~10K | Trend additions remain informational | IN_PROGRESS | `apps_rg` gates pass; full `apps_eval` suite has unrelated `apps_lic` determinism drift on `main` |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Add diagnostic contracts | DONE |
| W1.2 | Add validation hard stops | DONE |
| W2.1 | Collect `apps_rg` post-run diagnostic observations | DONE |
| W2.2 | Emit diagnostic artifacts without scorecard mutation | DONE |
| W3.1 | Add focused diagnostic tests and fixtures | DONE |
| W3.2 | Run regression and plan closeout gates | IN_PROGRESS |

---

## Out Of Scope

- Changing `ScorecardRow.v1` semantics or stuffing rich diagnostics into scorecard rows.
- Making diagnostics required, release-blocking, or current-run mutating.
- Running an LLM judge from `apps_eval`.
- Adding duplicate graph/retrieval runtime logic instead of consuming existing `apps_rg` receipts.
- Any current-run repair involving missing graph evidence, missing briefing, broader retrieval, route changes, provider substitution, HITL, UWG mutation, or L4 learning.

---

## Wave 1 — Diagnostic Contract

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Authorization**: NOT_REQUIRED — App eval-only contracts, no core/runtime authority.

**Phases**:
- **W1.1** — Add diagnostic contracts | ~4K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** — Add validation hard stops | ~4K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- `DiagnosticObservationV1` and `DiagnosticSummaryV1` are separate from `ScorecardRow`.
- Every diagnostic row requires source artifact refs and digests.
- Duplicate-overlap, release-blocking, current-run-authority, and missing-proof rows are rejected.

---

## Wave 2 — Apps RG Collector And Emission

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W2.1** — Collect post-run observations | ~8K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W2.2** — Emit diagnostic artifacts | ~4K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- Diagnostics are derived only from existing `apps_rg` artifacts and receipts.
- `diagnostic_rows.jsonl` and `diagnostic_summary.json` are emitted after existing scorecard artifacts.
- Existing scorecard, coverage, release gate, and L6 handoff behavior remains unchanged.

---

## Wave 3 — Tests And Regression Proof

WAVE_ID: W3
WAVE_STATUS: IN_PROGRESS
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W3.1** — Add diagnostic tests and fixtures | ~6K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W3.2** — Run regression gates | ~4K tokens | PHASE_STATUS: IN_PROGRESS | PHASE_COMPLETE: NO

**Acceptance**:
- Existing `apps_rg` microstep coverage tests remain stable.
- New tests cover missing source refs, duplicate overlap, unsafe E4 categories, X1D category separation, graph diagnostics, and R1B no-bypass observations.
- Plan and eval regression gates pass.

---

## Execution Details

### W1.1 — Add Diagnostic Contracts
**Scope**: Add diagnostic observation and summary models under `apps_eval` contracts without modifying `ScorecardRow.v1`.

**Commands**:
```bash
python -m pytest apps_eval/tests/test_apps_rg_microstep_scorecards.py -q
```

### W1.2 — Add Validation Hard Stops
**Scope**: Enforce shadow-only authority, source refs/digests, no duplicate overlap, and no release-blocking diagnostic promotion.

**Commands**:
```bash
python -m pytest apps_eval/tests -q
```

### W2.1 — Collect Post-Run Observations
**Scope**: Build an `apps_rg` diagnostic collector that consumes existing artifact indexes, graph receipts, X1D diagnostics, L2 attempt summaries, L1/L0 profiles, and cache evidence when present.

**Commands**:
```bash
python -m pytest apps_eval/tests -q
```

### W2.2 — Emit Diagnostic Artifacts
**Scope**: Emit `diagnostic_rows.jsonl` and `diagnostic_summary.json` after existing scorecard artifacts without changing scorecard verdicts.

**Commands**:
```bash
python -m pytest apps_eval/tests/test_apps_rg_microstep_scorecards.py apps_eval/tests/test_l6_handoff_shape.py -q
```

### W3.1 — Add Diagnostic Tests And Fixtures
**Scope**: Add focused fixtures for graph, briefing, retrieval, L2 retry, X1D, E4, L1, L0, and R1B disabled observations.

**Commands**:
```bash
python -m pytest apps_eval/tests -q
```

### W3.2 — Run Regression Gates
**Scope**: Run eval, e2e, and plan-format verification.

**Commands**:
```bash
python ops_scripts/ci/check_plan_format_compliance.py --strict --paths plans/apps-rg-apps-eval-diagnostics-a4e9c7.md
python ops_scripts/ci/check_plan_wave_summary_top.py
python ops_scripts/ci/check_plan_definition_of_done.py
python -m pytest apps_eval/tests -q
python -m pytest tests/e2e/test_l6_v40_apps_rg_apps_eval.py -q
```

---

## Gap Register

**GAP-1: Some diagnostic families may be sparse until more `apps_rg` receipts exist**
- Missing evidence produces `NOT_OBSERVED` or `WARN`.
- Diagnostics must not trigger current-run retrieval, routing, provider, HITL, UWG, or L4 actions.
- Status: CLOSED for this implementation; sparse evidence is represented as diagnostics, not repair.

**GAP-2: Historical trends need sample history before promotion**
- Diagnostic observations are shadow-only in this plan.
- Any later promotion to release-blocking requires a separate plan.
- Status: CLOSED for this implementation; promotion remains out of scope.

---

## Definition of Done

DoD-1: Diagnostic schema is separate from `ScorecardRow.v1`
- Evidence: tests prove scorecard row shape and current required microstep coverage remain stable.
- Status: DONE

DoD-2: Diagnostic artifacts are emitted post-run only
- Evidence: `diagnostic_rows.jsonl` and `diagnostic_summary.json` are present after eval emission and do not alter scorecard verdicts.
- Status: DONE

DoD-3: Validation hard stops reject unsafe observations
- Evidence: tests reject missing source refs/digests, duplicate overlap, current-run authority, and release-blocking promotion.
- Status: DONE

DoD-4: `apps_rg` diagnostic families are covered
- Evidence: tests cover briefing, graph traversal, retrieval, L2 retry, X1D categories, E4 safety, L1 planning, and L0/cache diagnostics.
- Status: DONE

DoD-5: Regression gates pass
- Evidence: Focused `apps_rg` diagnostics/microstep/dev-suite tests pass and `python -m pytest tests/e2e/test_l6_v40_apps_rg_apps_eval.py -q` passes. `python -m pytest apps_eval/tests -q` has one unrelated `apps_lic` determinism snapshot drift that also fails on `main`.
- Status: IN_PROGRESS

---

## Scope Expansion Authorization

When scope is discovered during execution, emit markers in order:

```
DISCOVERED_SCOPE: plan=apps-rg-apps-eval-diagnostics-a4e9c7 wave=<N> phase=<M> gap="<what>" impact="<severity>"
AUTHORIZATION_DECISION: plan=apps-rg-apps-eval-diagnostics-a4e9c7 decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|author_gate|self> decisive_reason="<why>"
SCOPE_EXPANSION: plan=apps-rg-apps-eval-diagnostics-a4e9c7 reason="<summary>" added="<waves/phases>" authorized="yes"
```

---

## Supersedes

| Predecessor slug | Reason |
|---|---|

_None — net-new plan._

---

## Marker Quick Reference

```
WAVE_START: plan=apps-rg-apps-eval-diagnostics-a4e9c7 wave=<N>
WAVE_COMPLETE: plan=apps-rg-apps-eval-diagnostics-a4e9c7 wave=<N> note="+N tests, N files, scope=<summary>"
PHASE_COMPLETE: plan=apps-rg-apps-eval-diagnostics-a4e9c7 phase=<W1.1>
PLAN_COMPLETE: plan=apps-rg-apps-eval-diagnostics-a4e9c7 note="<final outcome>"
```
