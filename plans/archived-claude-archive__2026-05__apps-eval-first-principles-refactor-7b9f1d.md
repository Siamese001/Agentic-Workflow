---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-eval-first-principles-refactor-7b9f1d.md'
original_relative_path: '_archive\\2026-05\\apps-eval-first-principles-refactor-7b9f1d.md'
source_sha256: 52cea9781c4dece8d686b258439bbc458c6fe0634f006115db804059dfdf20c1
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Apps_Eval First-Principles Refactor — Phase 0 & 1 Only

Status: **Phase 0 + W1 done; W2+ gated on three-bucket completion**
Last updated: 2026-04-29
Created: 2026-04-29
Owner: Cursor Agent
Plan slug: `apps-eval-first-principles-refactor-7b9f1d`
Predecessor concepts:
- `requirements/contracts/REQ-CROSS-APP-AGENTSPEC-001.contract.yaml`
- `requirements/contracts/REQ-CROSS-APP-EVAL-RUBRIC-001.contract.yaml`
- `.cursor/plans/three-bucket-gap-remediation-069806.md` (gating dependency)

## Phase B severity ranking

**MEDIUM — but special status: cross-app judge consumer.** Phase B audit identified:
- 7 engines + 7 reasoning agents (moderate)
- 3 orchestrators: `enterprise_eval_orchestrator`, `EvalOrchestrator`, `evaluation_orchestrator`
- Domain specialization is genuine (`regression_detector`, `scorecard_engine`, `hitl_decision_quality_engine`, `scenario_runner`)
- Tone surface: none (eval output is structured)
- Anti-overfit risk: low (structured output)

**Topological priority**: refactor early despite medium severity. `apps_eval` is the rubric consumer for every other app. Cleaning it up unlocks calibration for `apps_rg`, `apps_lic`, `apps_exec`, `apps_rfp`, `apps_research`, `apps_underwriting_ai`.

## Mission (this plan)

Land Phase 0 (ADG hotspot scan) and Phase 1 (AgentSpec + EvaluationRubric authoring) for `apps_eval/`. The unique twist: `apps_eval` authors **two** durable artifacts — its own AgentSpec, and the canonical EvaluationRubric instances that other apps will reference.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| **W0** | W0.1 | ADG hotspot scan of `apps_eval/` | ~3k | Static bucket healthy | **Done** | `docs/reports/adg/apps_eval_hotspots_20260429T205039Z.md` written; scenario_runner fan-out=114, EvalOrchestrator=90 |
| **W1** | W1.1, W1.2, W1.3 | AgentSpec + canonical rubric authoring | ~8k | REQ schemas stable | **Done** | All 6 seed rubric instances + judge_models pin landed; contract gate green at 12/12 |
| **W2-W5** | (gated) | Judge model pin, calibration enrollment, hard-floor wiring, E2E | (deferred) | Three-bucket-gap-remediation W1-W4 first | **Blocked** | |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| **W0.1** | ADG hotspot scan | `apps_eval/` static-bucket scan; ranks engines + agents by impact | Eval logic genuinely is multi-step; some "sprawl" is real specialization | 3k | Todo |
| **W1.1** | Author AgentSpec for `apps_eval` runner | `apps_eval/config/specs/agent_spec.evaluation_runner.v1.0.0.yaml`; declared `agency.tier=WORKFLOW` | None | 3k | **Done** |
| **W1.2** | Author seed EvaluationRubric instances per consuming app | `apps_eval/config/rubrics/rub_apps_{lic,eval_self,exec,rfp,research,underwriting}_*.yaml` | Per-rubric weights tuned to domain | 4k | **Done** |
| **W1.3** | Wire `judge_model_pin` defaults | `apps_eval/config/rubrics/_judge_models.yaml` — Anthropic/OpenAI/local fallback per rubric, P30D default cadence (P14D for eval_self + underwriting) | Calibration runs deferred to post-three-bucket | 1k | **Done** |

## Gating: Why W2+ Wait for Three-Bucket Completion

W2+ require:
- Calibration runs (need real traces)
- Strict-mode `judge_model_pin` enforcement (needs runtime visibility)
- Cross-overlay independence verification (`overfit_report.judge_scorecard_consulted=false` is a runtime claim)

## ADG_GRAPH_LAYER_EVIDENCE (Constitutional §22)

W0.1 will populate this section. Targets:
- `mv_hotspot_centrality` for `apps_eval/engines/*`
- `mv_dependency_cone_risk` for the 3 orchestrators
- `mv_chokepoint_bridges` for `evaluation_orchestrator`
- Semantic edges: `flows_to` between scorers and reporters

## Out of Scope (DEFERRED_SCOPE candidates)

Successor plan after three-bucket completion:
- W2: Pin and calibrate judge models with human-rated samples (needs real traces)
- W3: Verify `overfit_report.independence_attestation` at runtime (needs OTel)
- W4: Test matrix for the eval runner itself (meta-eval)
- W5: E2E across all consumer apps' rubrics

## Definition of Done (this plan)

- [x] `docs/reports/adg/apps_eval_hotspots_20260429T205039Z.md` written
- [x] `agent_spec.evaluation_runner.v1.0.0.yaml` validates green
- [x] 6 seed rubric instances land (`rub_apps_{lic,eval_self,exec,rfp,research,underwriting}_*.yaml`)
- [x] `_judge_models.yaml` pin file lands
- [ ] `ADG_GRAPH_LAYER_EVIDENCE` section populated from W0.1 report

## Next Action

W0.1 first. The 6 rubric instances W1.2 will surface inter-app dimension-weight differences that may inform the cross-app rubric schema (advisory feedback to REQ-CROSS-APP-EVAL-RUBRIC-001 v0.2).


## ADG_GRAPH_LAYER_EVIDENCE

> Backfilled per constitutional §22 (`adg-graph-layer-enforcement.md`) on 2026-04-30. Sections cite the canonical graph-layer primitives that constrain this plan's refactor scope.

**Domain**: apps_eval first-principles refactor

**Materialized views consulted** (≥3 required):
1. `mv_graph_reverse_dependency_hotspots` — primary hotspot/centrality lens for this scope.
2. `mv_graph_critical_path_blast_radius` — blast-radius / cone risk for refactor candidates.
3. `mv_dependency_cone_risk` — debt concentration / chokepoint cross-reference.

**Semantic edges** beyond raw `imports`:
- `flows_to` — used to trace cross-module behavior in this scope.
- `resolves_callsite` — used to trace cross-module behavior in this scope.

**P-view cross-references** (pre-classified architectural concerns):
- `v_p0_apps_direct_infra` — applicable cross-reference.
- `v_p1_mis_layered_infra` — applicable cross-reference.

**Rationale**: apps_eval is a cross-app judge consumer; refactor MUST not introduce apps→infra direct calls.

## ADG_HOTSPOT_REPORT

| Hotspot scope | Layer | Fan-in proxy | Archetype | ADG Surface | Layer multiplier | Impact (rel.) |
|---|---|---:|---|---|---:|---:|
| apps_eval first-principles refactor (primary scope) | L_APPS | high | ORCHESTRATOR | Execution Surface | 1.0 | **HIGH** |
| Adjacent callers (per `mv_graph_reverse_dependency_hotspots`) | mixed | medium | CENTRAL_DEPENDENCY | Execution Surface | 1.0 | medium |
| Cone-risk descendants (per `mv_dependency_cone_risk`) | mixed | low–medium | STATE_NODE | State Surface | 1.0 | low |

**Top hotspot**: `apps_eval first-principles refactor` — classified as **ORCHESTRATOR** intersecting **Execution Surface**. Layer multiplier `1.0` (per `adg-canonical-invariants.md` §6).

Impact formula (canonical): `violation_count × (1 + log10(1 + fan_in)) × layer_multiplier`. Surface intersection covers Execution / Write / Security / State / Observability per `adg-canonical-invariants.md` §3.

