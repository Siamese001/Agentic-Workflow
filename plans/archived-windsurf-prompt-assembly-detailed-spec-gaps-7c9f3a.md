---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\prompt-assembly-detailed-spec-gaps-7c9f3a.md'
original_relative_path: 'prompt-assembly-detailed-spec-gaps-7c9f3a.md'
source_sha256: 857b5f36042e303cd081da0399e4f11f7f64ec6f754818a5a42ddd5b7f3b1640
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-04-25'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Prompt Assembly Detailed Spec — Gap Closure

Source spec: `docs/reference/03_L0_Routing/Prompt Assembly/Prompt_Assembly_detailed.md`

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|------------:|-------------|--------|------------------|
| W1 | W1.1–W1.6 | New PA-stage contracts (PA.0/PA.5/PA.7 + events + C0 classifier + pipeline) | ~12000 | Existing CompiledPromptArtifact + PromptBOM are SSOT | Todo | All 6 modules + `__init__.py` import clean |
| W2 | W2.1–W2.6 | Unit tests per module (≥3 tests each, including negative paths) | ~8000 | Existing test fixtures available | Todo | All tests pass via pytest |
| W3 | W3.1 | Top-level orchestrator wiring + integration test | ~3000 | New modules pure-functional | Todo | End-to-end pipeline test passes |
| W4 | W4.1 | Commit + push to origin/main | ~500 | Working tree clean | Todo | Push succeeds |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|------------:|--------|
| W1.1 | PA.0 Boundary Check | `prompt_governance/prompt_assembly/pa0_boundary.py` | Spec checks 0.1–0.7 deterministic | 1500 | Todo |
| W1.2 | PA.5 Budget contracts | `prompt_governance/prompt_assembly/pa5_budget.py` | 4 budget classes + BudgetReport + trim order | 2500 | Todo |
| W1.3 | PA.7 Dispatch states | `prompt_governance/prompt_assembly/pa7_dispatch_states.py` | 8 BLOCKED_* codes | 1000 | Todo |
| W1.4 | PA.3 C0 classifier | `prompt_governance/prompt_assembly/pa3_c0_classifier.py` | PASS/STRIP/QUARANTINE/REJECT per chunk | 2000 | Todo |
| W1.5 | Observability events | `prompt_governance/prompt_assembly/observability_events.py` | 8 named events with payload contracts | 2000 | Todo |
| W1.6 | Pipeline orchestrator | `prompt_governance/prompt_assembly/pipeline.py` | Tie PA.0 → PA.7 stages | 3000 | Todo |
| W2.1 | tests pa0 | `tests/unit/.../test_pa0_boundary.py` | All 7 checks + PASS/FAIL | 1500 | Todo |
| W2.2 | tests pa5 | `tests/unit/.../test_pa5_budget.py` | Trim order determinism, overflow | 1500 | Todo |
| W2.3 | tests pa7 | `tests/unit/.../test_pa7_dispatch_states.py` | All 8 reason codes | 800 | Todo |
| W2.4 | tests c0 classifier | `tests/unit/.../test_pa3_c0_classifier.py` | 4 dispositions + injection patterns | 1500 | Todo |
| W2.5 | tests events | `tests/unit/.../test_observability_events.py` | All 8 events + payload validation | 1200 | Todo |
| W2.6 | tests pipeline | `tests/unit/.../test_pa_pipeline.py` | End-to-end + block paths | 1500 | Todo |
| W3.1 | Integration | (above pipeline test acts as integration) | — | 0 | Todo |
| W4.1 | Commit & push | git | — | 500 | Todo |

## ADG_HOTSPOT_REPORT

This is **purely additive** — new files in `agentic_core/prompt_governance/prompt_assembly/` (new sub-package). Zero modifications to existing CENTRAL_DEPENDENCY / ORCHESTRATOR / STATE_NODE / SAFETY_GATEKEEPER hotspots. Risk classification: ARCHITECTURE_ADDITIVE (no fan-in delta on existing nodes).

## ADG_GRAPH_LAYER_EVIDENCE

Refactoring waves require this section. This is greenfield ADDITIVE, so the section reads as:
- `mv_graph_reverse_dependency_hotspots`: N/A (new files have no fan-in yet)
- `mv_graph_chokepoint_bridges`: N/A (no new chokepoints introduced; new files import existing PromptBOM/CompiledPromptArtifact only)
- `mv_dependency_cone_risk`: low (sub-package isolated under prompt_governance/L_PG)
- Semantic edges used: `imports` only (no `flows_to`, `writes_to`, `emits_side_effect` — pure data contracts + pure functions)
- P-views: not applicable for additive contracts

## Gap Register

| Spec Section | Existing | Gap | Plan |
|--------------|----------|-----|------|
| PA.0 Boundary Check | implicit checks scattered | No formal `BoundaryCheckResult` w/ reason codes | W1.1 |
| PA.5 BudgetReport | informal `_compute_token_budget` | No `BudgetReport` dataclass + 4 trim classes | W1.2 |
| PA.7 OUTPUT STATES | none | No `DispatchDisposition` enum (8 codes) | W1.3 |
| PA.3 C0 classifier | `_classify_c0_content` returns (str, bool) | Lacks PASS/STRIP/QUARANTINE/REJECT + per-chunk record | W1.4 |
| Observability Events | none | No `PromptAssemblyStarted` etc. (8 events) | W1.5 |
| Pipeline orchestrator | `assemble_from_bom` does parts | No top-level PA.0..PA.7 sequencer | W1.6 |

Status: Active.
