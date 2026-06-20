---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\apps-research-deferred-scope-2-f3a9c1.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\apps-research-deferred-scope-2-f3a9c1.md'
source_sha256: c71b29c7275fdcb0248270bde7d7166fdac304f02678fad092befa14c6c3271c
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan: apps-research-deferred-scope-2-f3a9c1

**Status**: Completed  
**Parent**: `apps-research-deferred-scope-b7e3d2` (Completed 2026-05-04)  
**Created**: 2026-05-04  
**Completed**: 2026-05-04  

---

## Goal

Implement the remaining deferred scope items carried forward from
`apps-research-deferred-scope-b7e3d2` that were explicitly out-of-scope
or blocked during that plan's execution. These items represent the
remaining gaps between the current `apps_research` implementation and
full production readiness.

---

## Deferred Scope Items Carried Forward

### DS-A: `apps_rg` + `apps_lic` structured C0 fan-out (FEC v1.1)

**Source**: `apps-research-deferred-scope-b7e3d2` Out Of Scope  
**Priority**: P1 (AUDIT BLOCKER #4 partial — these two apps remain)

`apps_rg` and `apps_lic` have FEC producers at `schema_version == "1.0"`.
Neither app has a `query_decomposer`-equivalent structured retrieval plan
driving the C0 bundle. The `AEH1` gate currently warns on both.

**Acceptance criteria**:
- `apps_rg/cert/fec_producer.py` emits `schema_version == "1.1"` with
  a structured `retrieval_plan` block.
- `apps_lic/cert/fec_producer.py` emits `schema_version == "1.1"` with
  a structured `retrieval_plan` block.
- `AEH1` gate reports 0 ERRORs for both apps.
- Contract tests (`test_apps_rg_fec_producer.py`,
  `test_apps_lic_fec_producer.py`) updated to assert v1.1 shape.

---

### DS-B: UWG / L4 durable write path for research briefs

**Source**: `apps-research-deferred-scope-b7e3d2` DS-3 (landed stub only)  
**Priority**: P1 (§29 ROUTER_DECISION compliance gap)

`GovernedResearchRun.run_governed_e2e()` returns briefs to the caller
without committing provenance through the `DurableWriteGateway` (UWG).
Brief provenance is therefore not auditable at the L4 level and the
execution path has no `ROUTER_DECISION:` emit.

**Acceptance criteria**:
- `GovernedResearchRun.run_governed_e2e()` commits a provenance record
  through UWG before returning the brief.
- UWG commit decision emits `ROUTER_DECISION:` + `emit_ledger_event` per §29.
- `agentic_core/L4_state/` has a `research_brief_record` schema (or
  equivalent existing schema reused).
- Contract test covers the UWG commit path with a mocked gateway.

---

### DS-C: Real Spearman calibration for `citation_quality` judge

**Source**: `apps-research-deferred-scope-b7e3d2` DS-1 (holdout infra
landed in W4; real Spearman deferred pending human-label data)  
**Priority**: P2 (blocked on human-annotation dependency)

`citation_quality_judge.py` is `IS_CALIBRATED=True` via deterministic
heuristics but `judge_agreement_tracker.py` still reports
`holdout_comparison: null` because no human-labeled holdout corpus
exists yet. Closing this item requires:

**Acceptance criteria**:
- A human-labeled holdout fixture with ≥ 50 pairs at
  `data/judge_calibration/citation_quality_holdout.jsonl`.
- `judge_agreement_tracker.py` computes Spearman ρ against the holdout
  and reports a non-null `holdout_comparison` for the `citation_quality`
  dim.
- Spearman ρ ≥ 0.70 (initial bar; raise to 0.80 once corpus grows
  to ≥ 100 pairs).
- `test_w4_citation_quality_judge.py` assertion for non-null
  `holdout_comparison` passes.

**Blocked by**: Manual annotation of ≥ 50 brief/citation pairs
(external dependency — cannot be automated).

---

### DS-D: `coverage_depth` briefing rubric dim — real grader

**Source**: `apps-research-deferred-scope-b7e3d2` DS-1 residual  
**Priority**: P2

The `coverage_depth` dim in
`apps_research/config/domain_contract/eval_rubrics.yaml` currently
has no grader wired (falls through to `GRADER_UNKNOWN_SENTINEL`).
A deterministic heuristic grader (similar to `citation_quality_judge`)
measuring family coverage ratio should be straightforward.

**Acceptance criteria**:
- `apps_research/engines/judges/coverage_depth_judge.py` created with
  `IS_STUB=False`, `IS_CALIBRATED=True`, deterministic heuristic scoring.
- Wired into `grader_roster.yaml`.
- `eval_rubrics.yaml` `coverage_depth` dim updated to `grader_type:
  llm_as_judge` (heuristic).
- Contract test covering scoring behavior for shallow vs deep briefs.

---

### DS-E: `apps_exec` + `apps_rfp` + `apps_qna` exit-hook adoption

**Source**: `apps-eval-harness-deferred-e4a1b7` Out Of Scope  
**Priority**: P2

`apps_exec` and `apps_research` FEC producers are registered but their
`__main__.py` entry points do not yet call `maybe_invoke_exit_eval`.
`apps_rfp` adopted the hook but has no cert-route-registry opt-in.
`apps_qna` has the flag but the graded-output projection is incomplete.

**Acceptance criteria**:
- `apps_exec/__main__.py` imports and calls `maybe_invoke_exit_eval`.
- `apps_research/__main__.py` (if it exists / when created) calls
  `maybe_invoke_exit_eval`.
- `apps_rfp/config/cert_route_registry.yaml` has `invoke_exit_eval: true`.
- `NO_CERT_EXIT_INVOCATION` gate green for all 8 apps.
- Regression guard: existing tests in `test_w2p3_exit_eval_hook.py` pass.

---

### DS-F: FORENSIC + COMPETITIVE_SCAN engine integration tests (non-mocked)

**Source**: `apps-research-deferred-scope-b7e3d2` W5 residual  
**Priority**: P3

W5 added mocked engine integration tests for the two new profiles.
Non-mocked end-to-end smoke tests (similar to the existing
`TestFECv11E2E` pattern) require a live or semi-live research run,
which is expensive and outside the contract-test tier. This item tracks
promoting the new profiles to the same coverage level as DOSSIER.

**Acceptance criteria**:
- `TestFECv11E2E` class extended with one FORENSIC and one
  COMPETITIVE_SCAN test using the same stub-findings pattern as the
  DOSSIER test.
- Both new profiles produce a `_c0_bundle` with correct
  `source_portfolio_summary.total_final_sources` meeting their thresholds.
- `_depth_profile` key in the brief matches the requested profile.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status |
|------|-----------|-------|-------------|-------------|--------|
| W1 | A1, A2 | DS-A: `apps_rg` + `apps_lic` FEC v1.1 + structured retrieval plan | ~20K | AEH1 gate infra in place | ✅ DONE (already satisfied — schema_version=1.1 + source_ladder present) |
| W2 | B1, B2 | DS-B: UWG durable write path for research briefs | ~18K | DurableWriteGateway API stable | ✅ DONE (research_brief_uwg_writer.py fully implemented) |
| W3 | C1, D1 | DS-C + DS-D: holdout corpus + coverage_depth judge (P2; blocked on annotation) | ~15K | Human-labeled holdout available | ✅ DONE (DS-D done; DS-C ❌ BLOCKED on human annotation) |
| W4 | E1 | DS-E: exit-hook adoption for `apps_exec`, `apps_rfp`, `apps_qna` | ~10K | cert_route_registry pattern established | ✅ DONE (already satisfied — all 3 __main__.py call maybe_invoke_exit_eval) |
| W5 | F1 | DS-F: FORENSIC + COMPETITIVE_SCAN non-mocked E2E tests | ~8K | W5 of parent complete | ✅ DONE (28 new tests, all passing) |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| A1 | `apps_rg` FEC v1.1 + retrieval plan | `apps_rg/cert/fec_producer.py`, test | No query_decomposer equivalent; must design lightweight analog | ~10K | ✅ DONE |
| A2 | `apps_lic` FEC v1.1 + retrieval plan | `apps_lic/cert/fec_producer.py`, test | Multi-hop complexity; retrieval plan shape TBD | ~10K | ✅ DONE |
| B1 | UWG commit path for research briefs | `governed_research_run.py`, `DurableWriteGateway` | ROUTER_DECISION emit required; L4 schema design | ~10K | ✅ DONE |
| B2 | `L4_state` research_brief_record schema | `agentic_core/L4_state/` | agentic_core contract freeze risk | ~8K | ✅ DONE |
| C1 | Human-labeled holdout + Spearman calibration | `data/judge_calibration/`, `judge_agreement_tracker.py` | Requires human annotation (external dependency) | ~8K | ❌ BLOCKED (external dependency) |
| D1 | `coverage_depth` heuristic judge | `apps_research/engines/judges/coverage_depth_judge.py`, rubric/roster | Scoring heuristic design | ~7K | ✅ DONE |
| E1 | Exit-hook adoption for 3 apps | `apps_exec/__main__.py`, `apps_rfp/config/`, `apps_qna/` | Per-app dim-score projection variability | ~10K | ✅ DONE |
| F1 | FORENSIC + COMPETITIVE_SCAN E2E tests | `test_apps_research_spine_alignment.py` | Stub-findings shape must meet new profile thresholds | ~8K | ✅ DONE |

---

## Prerequisites

- `apps-research-deferred-scope-b7e3d2` **Completed** ✅
- `apps-eval-harness-deferred-e4a1b7` **Completed** ✅
- Human-labeled holdout data for DS-C (external dependency — blocks W3/C1)
- ADG MCP green before W2 (cross-layer changes)

---

## Out Of Scope

- `apps_underwriting_ai` C0 binding (already on separate plan per prior session)
- Production log mining with PII redaction
- SSOT consolidation of legacy policy/threshold YAMLs
- Holdout vs dev eval-set separation (eval-harness W5.P1)
- Real LLM-as-judge calls for any dim (all heuristic/deterministic in scope here)
