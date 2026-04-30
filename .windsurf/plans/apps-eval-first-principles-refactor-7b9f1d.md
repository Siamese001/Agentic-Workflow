# Apps_Eval First-Principles Refactor — Phase 0 & 1 Only

Status: **Phase 0 + W1 done; W2+ gated on three-bucket completion**
Last updated: 2026-04-29
Created: 2026-04-29
Owner: Cascade
Plan slug: `apps-eval-first-principles-refactor-7b9f1d`
Predecessor concepts:
- `requirements/contracts/REQ-CROSS-APP-AGENTSPEC-001.contract.yaml`
- `requirements/contracts/REQ-CROSS-APP-EVAL-RUBRIC-001.contract.yaml`
- `.windsurf/plans/three-bucket-gap-remediation-069806.md` (gating dependency)

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
