---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\apps-rg-spearman-spine-remediation-f3c9a1.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\apps-rg-spearman-spine-remediation-f3c9a1.md'
source_sha256: 4805ffd3aa73dc20a04474990d4a56586d4b4346eea40baba8afa41cd311d5c1
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-rg-spearman-spine-remediation-f3c9a1
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: true
touches_windsurf_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
last_hardened: 2026-05-14
---

# apps_rg Spearman Spine Remediation

Wire the full Spearman baseline pipeline (6A ingest → 6B evaluate with real judge → 6C RCA → 6D promote → Exit consumes L4 reliability) end-to-end for apps_rg, replacing the IS_STUB judge and offline-only Spearman computation with live, contract-bound evaluation that follows the documented placement rules.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W0
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-05-14

---

## Context (SCQA)

- **Situation** — apps_rg has a fully operational runtime pipeline (U0 → L2 → Exit, verified 2026-05-09 with real Qwen 32B LLM). The L6 shadow evaluation infrastructure (`agentic_core/L6_observability/shadow_eval/`) is complete and OTEL-instrumented: 6A ingest, 6B evaluate (with `CodeOnlyGrader`), 6C RCA, 6D gauntlet/promote/UWG. A `judge_spearman_calibration.py` scaffold runs offline and has produced ρ=0.922 for `executive_positioning`. The holdout fixture has 8 human-labeled rows.

- **Complication** — Seven gaps block a production-valid Spearman spine for apps_rg: (1) `executive_positioning_judge` is IS_STUB — real scores have never been computed; (2) no `lexicon_coverage_judge` exists despite holdout labels for it; (3) Spearman is only computed offline (CI calibration script), never inside the live `run_6b()` path; (4) apps_rg's sealed exhaust is not wired into `build_runtime_exhaust_bundle()` — 6A cannot ingest apps_rg runs; (5) no L4 namespace exists for apps_rg judge baselines (Spearman threshold, calibration history, judge/rubric version); (6) `exit_binding.py` gates never consult an approved `JudgeReliabilitySignal` from L4; (7) the holdout corpus is n=8, far below the minimum for a production Spearman gate.

- **Question** — How do we build a complete, contract-compliant Spearman baseline spine for apps_rg — from real judge scores through 6B calibration through L4 storage through Exit consumption — matching the placement rules?

- **Answer** — Seven sequential waves: implement real judges (W1), wire apps_rg 6B grader (W2), build the 6A exhaust adapter (W3), move Spearman into the live 6B path (W4), define the apps_rg L4 baseline surface (W5), wire Exit to consume L4 reliability (W6), and expand the holdout corpus to ≥30 rows (W7).

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|------------|--------|-----------------|
| W1 | W1.P1–P2 | Real `executive_positioning_judge` + `lexicon_coverage_judge` | ~4K | 🔲 TODO | `IS_STUB=False`; `grade()` returns real float; Spearman gate re-run produces ρ ≥ 0.80 against holdout |
| W2 | W2.P1 | `AppsRgDimensionGrader` wired into 6B `run_6b()` | ~3K | 🔲 TODO | `evaluate_outcome()` with apps_rg grader scores all 7 section-quality dims; UNKNOWN rate < 20% on holdout |
| W3 | W3.P1–P2 | apps_rg 6A exhaust adapter + manifest writer | ~3K | 🔲 TODO | `build_runtime_exhaust_bundle()` accepts apps_rg `ExitResult`; `l6_exhaust_manifest.json` written under `artifacts/apps_rg/runs/<ts>/` |
| W4 | W4.P1 | Live Spearman computation inside `run_6b()` | ~3K | 🔲 TODO | `run_6b()` emits `JudgeReliabilitySignal` with real ρ; CI calibration script verifies offline match |
| W5 | W5.P1–P2 | apps_rg L4 baseline namespace + UWG surface constant | ~3K | 🔲 TODO | L4 schema defined; `target_surface=apps_rg::judge_baseline`; UWG `version_bump` policy declared |
| W6 | W6.P1 | Exit `G_JUDGE_RELIABILITY` gate consuming L4 signal | ~2K | 🔲 TODO | New gate in `_evaluate_c0_evidence_gates()`; below-threshold triggers WARN/HITL escalation |
| W7 | W7.P1 | Holdout corpus expansion to ≥30 rows | ~2K | 🔲 TODO | `apps_rg.jsonl` has ≥30 RELEASE_GATE rows; `lexicon_coverage` pairs populated; Spearman gate passes on fresh run |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.P1 | `executive_positioning_judge` real impl | `apps_rg/engines/judges/executive_positioning_judge.py` | Replace IS_STUB; rubric-grounded lexical/structural scoring; no LLM call required for deterministic dims | ~2K | 🔲 TODO |
| W1.P2 | `lexicon_coverage_judge` new impl | `apps_rg/engines/judges/lexicon_coverage_judge.py`, `apps_rg/engines/judges/__init__.py` | New judge; register in `JUDGE_CALIBRATION_TARGETS`; holdout dim key = `lexicon_coverage` | ~2K | 🔲 TODO |
| W2.P1 | `AppsRgDimensionGrader` | `apps_rg/engines/evaluation/apps_rg_grader.py` (new) | Implements `DimensionGrader` protocol; reads `section_quality_rubrics.yaml`; maps 7 dims to `EvalDimensionScore`; injected into `run_6b()` via `grader=` arg | ~3K | 🔲 TODO |
| W3.P1 | Exhaust adapter | `apps_rg/runtime/bindings/l6_exhaust_adapter.py` (new) | Converts `ExitResult` → `RuntimeExhaustBundle` dict; populates trace_refs, policy_hash, sealed artifact refs, FEC refs, gate receipt refs | ~2K | 🔲 TODO |
| W3.P2 | Manifest writer | `apps_rg/__main__.py` edit | After `exit_finalize_apps_rg()` returns, write `l6_exhaust_manifest.json` to run artifact dir; include adapter output path | ~1K | 🔲 TODO |
| W4.P1 | Live Spearman in 6B | `agentic_core/L6_observability/shadow_eval/calibration.py` edit + `apps_rg/engines/evaluation/apps_rg_grader.py` edit | Extend `build_calibration_record()` caller in `run_6b()` to compute ρ from holdout; emit `JudgeReliabilitySignal`; `kappa_or_agreement_score` = ρ | ~3K | 🔲 TODO |
| W5.P1 | L4 namespace schema | `apps_rg/config/domain_contract/l4_judge_baseline_profile.yaml` (new) | Declares `spearman_threshold`, `calibration_history_max`, `judge_version`, `rubric_version`, `target_surface` | ~1K | 🔲 TODO |
| W5.P2 | UWG surface constant | `apps_rg/runtime/bindings/inert_writeback_types.py` edit | Add `APPS_RG_JUDGE_BASELINE_SURFACE = "apps_rg::judge_baseline"` constant; reference in `L6ShadowHandoff` docstring | ~1K | 🔲 TODO |
| W6.P1 | `G_JUDGE_RELIABILITY` gate | `apps_rg/runtime/bindings/exit_binding.py` edit | New gate in `_evaluate_c0_evidence_gates()`; reads L4 `JudgeReliabilitySignal` if present; WARN when `recommended_use != ALLOW_FOR_EVAL`; HITL escalation when `REQUIRE_HUMAN_REVIEW` | ~2K | 🔲 TODO |
| W7.P1 | Holdout corpus ≥30 rows | `apps_eval/fixtures/holdout/apps_rg.jsonl` edit | Add 22+ rows covering full quality spectrum; include `lexicon_coverage` dim in all rows; tag `RELEASE_GATE`; verify Spearman gate passes at n≥30 | ~2K | 🔲 TODO |

---

## Gap Register (from assessment 2026-05-14)

| ID | Gap | Stage | Severity | Wave |
|----|-----|-------|----------|------|
| G1 | `executive_positioning_judge` IS_STUB — real scores never computed | 6B | HIGH | W1 |
| G2 | No `lexicon_coverage_judge` despite holdout labels | 6B | MEDIUM | W1 |
| G3 | No apps_rg-specific 6B grader; generic `CodeOnlyGrader` scores structural not rubric dims | 6B | HIGH | W2 |
| G4 | No apps_rg exhaust adapter — 6A cannot ingest apps_rg runs | 6A | HIGH | W3 |
| G5 | No exhaust persistence path — `ExitResult` never written for 6A consumption | 6A | HIGH | W3 |
| G6 | Spearman not computed in live `run_6b()` — offline CI only | 6B | HIGH | W4 |
| G7 | No apps_rg L4 namespace for judge baselines | 6D | HIGH | W5 |
| G8 | No UWG `target_surface` constant for apps_rg judge baseline promotion | 6D | HIGH | W5 |
| G9 | `exit_binding.py` does not consume L4 `JudgeReliabilitySignal` | Exit | HIGH | W6 |
| G10 | Holdout n=8 — insufficient for production Spearman gate | 6B | MEDIUM | W7 |
| G11 | No apps_rg-specific RCA hypotheses for rubric dims | 6C | MEDIUM | deferred |
| G12 | No judge drift detection wired for apps_rg | 6C | MEDIUM | deferred |

---

## ADG_HOTSPOT_REPORT

> ADG Provenance: backend=redis_cache+sqlite, snapshot=adg_indexed_05122026_1828.sqlite

| Rank | File | Archetype | Layer | Fan-In | Surfaces | Wave |
|------|------|-----------|-------|--------|----------|------|
| 1 | `apps_rg/runtime/bindings/exit_binding.py` | SAFETY_GATEKEEPER | L3/Exit | medium | Security, State, Execution | W6 |
| 2 | `agentic_core/L6_observability/shadow_eval/calibration.py` | STATE_NODE | L6 | medium | State, Observability | W4 |
| 3 | `agentic_core/L6_observability/shadow_eval/evaluation.py` | ORCHESTRATOR | L6 | medium | Execution, Observability | W2, W4 |
| 4 | `apps_rg/engines/judges/executive_positioning_judge.py` | CENTRAL_DEPENDENCY | app | low | Execution | W1 |
| 5 | `apps_eval/fixtures/holdout/apps_rg.jsonl` | STATE_NODE | data | low | State | W7 |

---

## ADG_GRAPH_LAYER_EVIDENCE

- **MV hotspot centrality**: `exit_binding.py` (SAFETY_GATEKEEPER) intersects Execution + Security + State surfaces — multiplier ×1.75 (L3/Exit layer). Highest-priority edit target for W6.
- **Semantic edge**: `run_6b()` in `shadow_eval/pipeline.py` `flows_to` `build_calibration_record()` in `calibration.py` `flows_to` `CompletedEvalRecord` — W4 must extend this edge to include `JudgeReliabilitySignal` emission.
- **Semantic edge**: `exit_finalize_apps_rg()` `writes_to` `ExitResult` — W3 adapter must `reads_from` this same output.
- **P-view v_p1**: `executive_positioning_judge` has zero callers in runtime path — it is mis-layered stub with no runtime fan-in. W1 resolves by making it a real grader that `apps_rg_grader.py` (W2) calls via `DimensionGrader` protocol.
- **Layer multiplier**: `shadow_eval/calibration.py` at L6 carries ×2.0 multiplier — any change to `build_calibration_record()` signature has highest blast radius; W4 must extend via caller injection, not signature change.

---

## Files In Scope

**New files:**
- `apps_rg/engines/__init__.py` (if absent)
- `apps_rg/engines/judges/executive_positioning_judge.py` (real impl, replace stub)
- `apps_rg/engines/judges/lexicon_coverage_judge.py`
- `apps_rg/engines/judges/__init__.py` (update re-exports)
- `apps_rg/engines/evaluation/__init__.py`
- `apps_rg/engines/evaluation/apps_rg_grader.py`
- `apps_rg/runtime/bindings/l6_exhaust_adapter.py`
- `apps_rg/config/domain_contract/l4_judge_baseline_profile.yaml`
- `tests/_apps_contract/test_apps_rg_spearman_spine.py`

**Edited files:**
- `apps_rg/runtime/bindings/exit_binding.py` (W6 gate)
- `apps_rg/runtime/bindings/inert_writeback_types.py` (W5 surface constant)
- `apps_rg/__main__.py` (W3 manifest write)
- `apps_eval/fixtures/holdout/apps_rg.jsonl` (W7 corpus expansion)
- `ops_scripts/calibration/judge_spearman_calibration.py` (W1 register lexicon_coverage)

**Not in scope (generic core — must not be edited for app-specific reasons):**
- `agentic_core/L6_observability/shadow_eval/evaluation.py` — `run_6b()` uses injected `grader=` arg; no core edit needed
- `agentic_core/L6_observability/shadow_eval/calibration.py` — called via injection; no signature changes

---

## Non-Goals (explicitly out of scope)

- G11 / G12: apps_rg RCA hypothesis mapping and judge drift detection — deferred to a follow-on plan
- Real LLM-based judge scoring (Qwen call per resume section) — `executive_positioning_judge` W1 impl will be deterministic/heuristic; LLM-backed grading is a separate plan
- Notifying downstream consumers (BUS U, runtime L4 write) — W5 declares the schema; actual UWG promotion requires a separate promotion run after Gauntlet pass
- Changing `agentic_core/L6_observability/shadow_eval/pipeline.py` — injection points already exist; no core edit needed

---

## Definition of Done

| ID | Criterion | Verification |
|----|-----------|-------------|
| DoD-1 | `executive_positioning_judge.IS_STUB` is `False`; `grade()` returns a real float in [0,1] for all 8 holdout rows | `python -c "from apps_rg.engines.judges.executive_positioning_judge import IS_STUB, grade; assert not IS_STUB"` exits 0 |
| DoD-2 | Spearman ρ ≥ 0.80 for `executive_positioning` and `lexicon_coverage` at n≥30 holdout | `python ops_scripts/calibration/judge_spearman_calibration.py` emits `meets_threshold=true` for both judges |
| DoD-3 | `AppsRgDimensionGrader` produces non-UNKNOWN scores for ≥5 of 7 rubric dims on a fixture run | `pytest tests/_apps_contract/test_apps_rg_spearman_spine.py -v` passes |
| DoD-4 | `l6_exhaust_manifest.json` present in `artifacts/apps_rg/runs/<ts>/` after a dry-run invocation | `python -m apps_rg --dry-run ...` + assert manifest file exists |
| DoD-5 | `G_JUDGE_RELIABILITY` gate present and emitting PASS/WARN/FAIL verdicts in `ExitDisposition.gate_results` | `pytest tests/_apps_contract/test_apps_rg_spearman_spine.py::test_exit_judge_reliability_gate` passes |
| DoD-6 | All existing `_apps_contract` tests remain green (zero regressions) | `pytest tests/_apps_contract/ -x` exits 0 |
| DoD-7 | `check_judge_spearman_gate.py` exits 0 with ≥30 pairs in holdout | `python ops_scripts/ci/check_judge_spearman_gate.py` exits 0 |

### Verification-vs-Deferral

| Item | In-plan verification | Deferred |
|------|---------------------|---------|
| Real Spearman ρ ≥ 0.80 | DoD-2 with deterministic judge | LLM-backed grading quality |
| apps_rg RCA hypothesis mapping | — | Follow-on plan |
| Actual L4 durable write via UWG | Schema only (W5) | Post-Gauntlet promotion plan |
| Judge drift monitoring | — | Follow-on plan |

---

## Deferred Scope

DEFERRED_SCOPE: apps_rg RCA hypothesis mapping for rubric dims (G11) — deferred to follow-on plan after W2 grader establishes which dims fail most often
DEFERRED_SCOPE: apps_rg judge drift detection wiring to `judge_drift.py` (G12) — deferred; requires baseline ≥30-run history
DEFERRED_SCOPE: LLM-backed `executive_positioning_judge` (Qwen call per section) — deferred; deterministic heuristic sufficient for Spearman gate
DEFERRED_SCOPE: Actual UWG promotion of apps_rg judge baseline to L4 — deferred; W5 declares schema only; promotion requires Gauntlet pass evidence
