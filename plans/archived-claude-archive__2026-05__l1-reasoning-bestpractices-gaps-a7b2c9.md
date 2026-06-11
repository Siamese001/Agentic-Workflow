---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\l1-reasoning-bestpractices-gaps-a7b2c9.md'
original_relative_path: '_archive\\2026-05\\l1-reasoning-bestpractices-gaps-a7b2c9.md'
source_sha256: 9cf64552dc8298651f9bbbfe9dc574323eb9df5e303828c42b5b60017eeb5deb
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# L1 Reasoning & Plan Generation — Best-Practice Gap Analysis + Rectification Plan

- **Plan ID**: `l1-reasoning-bestpractices-gaps-a7b2c9`
- **Scope target**: `docs/reference/_notes/agentic_process_mapping_v34.md` §2 "L1 Reasoning + Plan Generation" AND `agentic_core/L1_cognition/`
- **Status**: Draft — no code changes
- **Tier**: T3 (cross-layer: doc + contracts + L1 engines + L5 policy)
- **ADG snapshot basis**: most recent `artifacts/adg/adg_indexed_*.sqlite` (gap audit uses ADG later at execution time)
- **Author-Gate**: none yet; execution will require Author-Gate for any contract schema change
- **Token estimator**: not run (doc/planning work only). Token estimates below are UNRESOLVED-ESTIMATE and must be validated by `tools/utils/planning/token_estimator.py` before any execution wave starts.

---

## 1. Best-Practice Survey (Anthropic / OpenAI / Google)

### 1.1 Anthropic — *Building Effective Agents* + *Claude's Constitution*

| BP-A# | Practice | Citation |
|---|---|---|
| **BP-A1** | **Evaluator-optimizer loop** — one LLM generates, another critiques, iterate until acceptable | Building Effective Agents §Evaluator-optimizer |
| **BP-A2** | **Workflow vs agent distinction** — prefer predictable workflows; reserve open-loop agent behavior for open-ended problems | ibid §Agents |
| **BP-A3** | **Stopping conditions** — max iterations, budget cap, explicit human checkpoint at blockers | ibid §Agents |
| **BP-A4** | **Ground-truth feedback each step** — tool results, code execution output, environmental signal | ibid §Agents |
| **BP-A5** | **Clarify in ambiguity** — ask the user instead of guessing when intent is unclear | Claude's Constitution |
| **BP-A6** | **Abstain / decline** as first-class option when unsafe or under-specified | Claude's Constitution |
| **BP-A7** | **Lowest viable autonomy** — don't escalate from a single turn to a multi-step agent loop without cause | Building Effective Agents §When to use agents |

### 1.2 OpenAI — *Reasoning Best Practices* + *GPT-5 prompting guide*

| BP-O# | Practice | Citation |
|---|---|---|
| **BP-O1** | **Planner / Doer split** — reasoning model as planner, cheaper GPT model as doer | Reasoning Best Practices §Multistep agentic planning |
| **BP-O2** | **Keep prompts simple & direct** — reasoning models hurt by "think step by step" prompts | §How to prompt reasoning models |
| **BP-O3** | **Delimiters (markdown / XML tags) for input sections** | §How to prompt |
| **BP-O4** | **Zero-shot first, few-shot only if examples clearly align** | §How to prompt |
| **BP-O5** | **Explicit constraints + explicit end-goal parameters** in the prompt | §How to prompt |
| **BP-O6** | **Developer message ≠ system message** — role separation since o1-2024-12-17 | §How to prompt |
| **BP-O7** | **Reasoning effort calibration** — plan extensively before tool calls, reflect extensively after | GPT-5 prompting guide |

### 1.3 Google — *ADK Planners & Thinking* + *ADK Multi-agent patterns*

| BP-G# | Practice | Citation |
|---|---|---|
| **BP-G1** | **Two canonical planner modes**: `BuiltInPlanner` (extended thinking / internal CoT) and `PlanReActPlanner` (structured Plan/Reason/Act tags) | Planners & Thinking Tutorial 12 |
| **BP-G2** | **Match planner to task complexity** — don't plan simple queries | §6 Best Practices |
| **BP-G3** | **`include_thoughts` toggle** — show thoughts in debug/educational, hide in production | §Best Practices |
| **BP-G4** | **Pair planner with clear instruction** (Plan → Explain → Execute → Review → Adjust) | §Best Practices |
| **BP-G5** | **Measure planner overhead** vs no-planner baseline; accept overhead only if quality lifts | §Best Practices |
| **BP-G6** | **Graceful fallback on planning failure** — best-effort answer + explain limitations, don't abandon | §Best Practices |
| **BP-G7** | **Replanning** on new evidence is a first-class branch of the Plan-ReAct loop | §Replanning Example |
| **BP-G8** | **Sequential / output-key state handoff** — later agents read earlier agents' structured outputs from shared session state, not from free text | Multi-agent patterns |

---

## 2. Current v33 §2 Coverage

What §2 (lines 71–137) already covers:

| v33 element | Maps to |
|---|---|
| I1 goal + success condition | BP-O5 (end-goal), BP-A2 (task framing) |
| I2 constraints + rules | BP-O5 (explicit constraints) |
| I3 details + work class | BP-G2 (match planner to complexity — partial) |
| M1 task schemas + routes | BP-O3 (delimiters/schemas — partial) |
| M2 safety / policy / escalation | BP-A6, BP-A3 (human checkpoint) |
| M3 examples + approved patterns | BP-O4 (few-shot when useful) |
| T1 interpret the request | BP-A5 (clarify) — partial |
| T2 draft the plan | BP-A1, BP-G1 (plan drafting) |
| T3 validate / simplify / clarify | BP-A1 (evaluator) — partial, single-pass |
| Output contract: proposed_route, query_spec, task_spec, route_risk, confidence, grounding_required, assumptions, gaps | BP-O1 (planner/doer handoff), BP-G8 (structured handoff) |
| Invariant: no retrieval / no routing / no execution / no mutation | BP-A2 (workflow discipline), BP-O1 (planner role purity) |
| "Abstain within L1 only" | BP-A6 |
| "Lowest viable agency" | BP-A7 |

---

## 3. Doctrinal Gaps — v33 §2 vs Best Practices

Each row: **GAP-D#** — missing doctrine, the best-practice it violates or under-specifies, and the fix class (D = doctrine edit only).

| GAP-D# | Missing element in v33 §2 | BP violated | Fix class |
|---|---|---|---|
| **GAP-D1** | No explicit **planner/doer split** language — §2 does not name that L1 may run a reasoning-class model distinct from L2's doer model, nor call out `reasoning_effort` calibration. | BP-O1, BP-O7 | D |
| **GAP-D2** | **Evaluator-optimizer loop** is absent — T3 is a single validate pass, not a critic→refiner→re-validate loop with an iteration bound. | BP-A1 | D |
| **GAP-D3** | No **planner-mode selection rubric** — §2 does not distinguish "extended thinking / internal CoT" vs "structured Plan-ReAct tags" vs "direct / no planner", even though the repo already has `ReasoningMode = {CHAIN_OF_THOUGHT, REACT, DIRECT, DECOMPOSED}`. | BP-G1, BP-G2 | D |
| **GAP-D4** | No **stopping conditions / iteration budget** inside the T1–T3 loop. Max refinement passes, wall-clock budget, token budget, and "abandon-to-abstain" threshold are not stated. | BP-A3, BP-G5 | D |
| **GAP-D5** | No **plan-skip criterion** — §2 assumes L1 always produces a plan. No rule like "if intent frame is trivial + unambiguous + cache-eligible, skip planner and hand a direct-route slip to L0". | BP-G2 | D |
| **GAP-D6** | No **`include_thoughts` / thought-redaction policy** — what is private L1 scratchpad vs what appears in the plan contract that crosses L1→L0? | BP-G3 | D |
| **GAP-D7** | **Clarify vs abstain vs refine** is collapsed into one T3 bullet ("clarify or abstain if needed"). No explicit clarify-to-user branch distinct from abstain-to-R5. | BP-A5, BP-A6 | D |
| **GAP-D8** | No **fact-grading protocol** for the `declared assumptions / unresolved gaps` output — should align with constitutional §20 (DIRECTLY OBSERVED / DERIVED / UNRESOLVED). | BP-A4 | D |
| **GAP-D9** | Explicit **reflection / self-critique** step is not named — T3 checks validity but does not invoke a separate critic persona/model. | BP-A1, BP-O7 | D |
| **GAP-D10** | No **few-shot selection policy** — M3 loads "examples + approved patterns" but no rule of zero-shot-first-then-few-shot-if-mismatch. | BP-O4 | D |
| **GAP-D11** | No **schema / delimiter contract** for plan handoff — output fields are named but no JSON/XML schema or delimiter convention specified. | BP-O3 | D |
| **GAP-D12** | **Planning-failure fallback** is not distinguished from abstain — no explicit "best-effort safe default with explained limitations → R5" variant. | BP-G6 | D |
| **GAP-D13** | **Replan trigger from [5] EXIT EVAL** is missing — §2 is one-shot. No contract for re-entering L1 when evidence from L2/C0 invalidates a plan assumption. | BP-G7 | D |
| **GAP-D14** | **Confidence calibration rubric** is not defined — §2 lists `confidence` and `grounding_required` but no rubric for how L1 picks the score/threshold, nor how that threshold gates `ESCALATE_TO_HITL`. | BP-O1, BP-A3 | D |
| **GAP-D15** | No **developer-vs-system-message** separation for the L1 prompt envelope — how L5 policy prepends vs user goal vs examples is unspecified. | BP-O6 | D |
| **GAP-D16** | **Ground-truth feedback loop** is not named inside §2 — BP-A4 says the plan must anticipate what ground-truth signal each step will produce; §2 has `grounding_required` but no per-step expected-evidence declaration. | BP-A4 | D |
| **GAP-D17** | No **planner overhead measurement hook** — no observability contract saying "L1 must emit planner-on vs planner-off timing/cost so we can verify the planner earns its overhead". | BP-G5 | D |

---

## 4. Repo Gaps — `agentic_core/L1_cognition/` vs v33 Contract

Each row: **GAP-R#** — code-side divergence, evidence path, fix class (S = schema/contract, E = engine, O = observability, T = tests, M = migration).

| GAP-R# | Finding | Evidence | Fix class |
|---|---|---|---|
| **GAP-R1** | `L1PlanContract` has 7 fields; v33 §2 output contract lists **8 semantic items** (`proposed_route`, `query_spec`, `task_spec`, `route_risk`, `confidence`, `grounding_required`, `declared_assumptions`, `unresolved_gaps`). Missing as typed fields: `proposed_route`, `query_spec`, `task_spec`, `route_risk`, `declared_assumptions`, `unresolved_gaps`. | `agentic_core/L1_cognition/types/plan_contract_types.py:71–77` | S |
| **GAP-R2** | `ReasoningPlan` (engine) and `L1PlanContract` (types) are **two unbridged artifacts** — `L1PlanContract.steps` is a generic `tuple`, not typed `PlanStep`. No adapter documented from `ReasoningPlan → L1PlanContract`. | `reasoning_plan.py` vs `plan_contract_types.py` | S / E |
| **GAP-R3** | No distinct **evaluator-optimizer module** in `L1_cognition/reasoning/`. `reasoning_evaluation.py` exists (29 KB) but its relationship to the T3 validate step is not documented and it is not wired into `plan_creator.create_reasoning_plan()`. | `reasoning_evaluation.py`, `plan_creator.py:1–15` | E |
| **GAP-R4** | `abstain_planner` exists (re-export shim) but **no `clarify_planner` / clarification-request primitive**. `AbstainDecision` has `ACTION_CONTINUE` / `ACTION_EMIT_R5` only — no `ACTION_REQUEST_CLARIFICATION` action. | `abstain_planner.py`, `runtime/contracts/abstain_contract.py` | S / E |
| **GAP-R5** | **No `replan` primitive** — no handler for exit-gate feedback re-entering L1. `plan_creator.py` docstring is one-shot (goal → decompose → checkpoints → evidence → bind → persist). | `plan_creator.py:1–15` | E |
| **GAP-R6** | `budget_enforcer.py` is 977 bytes — **likely insufficient** for per-plan iteration budget / wall-clock / token-cap enforcement called for by GAP-D4. | `agentic_core/L1_cognition/enforcement/budget_enforcer.py` | E |
| **GAP-R7** | `ReasoningMode` enum has 4 values (`CHAIN_OF_THOUGHT`, `REACT`, `DIRECT`, `DECOMPOSED`) but **no selection rubric** in code or doc mapping those values to work-class / complexity / budget (GAP-D3). | `plan_contract_types.py:45–51` | E / D |
| **GAP-R8** | No typed **`ExpectedGroundTruth` per plan step** — plan steps are free-form dicts; BP-A4 requires each step to declare the evidence signal it expects to produce. | `reasoning_plan.py` + `plan_contract_types.py` | S |
| **GAP-R9** | No **observability emitter** for planner-on vs planner-off overhead comparison (GAP-D17). `meta_observability.py` exists but no `planner_overhead_metric` primitive surfaced in the chokepoint. | `enforcement/reasoning_chokepoint.py` (18 KB) | O |
| **GAP-R10** | No **developer-message vs system-message** separation in `prompt_template_manager.py` — L5 policy, user goal, M3 examples are combined into a single prompt envelope without role separation (GAP-D15). | `prompt_template_manager.py` | E |
| **GAP-R11** | No **confidence-score rubric** in code — `L1PlanContract.confidence_score ∈ [0.0, 1.0]` is validated but nothing binds it to a rubric or to `reasoning_chokepoint`'s HITL gate threshold. | `plan_contract_types.py:113–116`, `enforcement/reasoning_chokepoint.py` | E / D |
| **GAP-R12** | No **plan-failure graceful-fallback path** — `plan_creator` either succeeds or raises `ReasoningPlanError`. No `emit_best_effort_plan_with_limitations()` helper feeding R5 (GAP-D12). | `plan_creator.py`, `reasoning_plan.py` | E |
| **GAP-R13** | No **thought-redaction layer** — the plan contract does not separate `private_scratchpad` (L1-only) from `published_rationale` (crosses to L0) (GAP-D6). | `plan_contract_types.py` | S |
| **GAP-R14** | Test coverage for the plan-contract validation path likely under-exercises all 8 doctrinal fields once added (assumption — must be verified with ADG fan-in on `L1PlanContract` at execution time). | (to verify) | T |
| **GAP-R15** | The ubiquitous lifecycle_trace emitter block at file-top in `reasoning_plan.py`, `plan_creator.py`, `react_engine.py` is **boilerplate**; contains no L1-specific planner-overhead or evaluator-iteration emitters. This is a latent observability gap (GAP-D17 / GAP-R9). | `reasoning_plan.py:20–80`, `react_engine.py:87–166` | O |

---

## 5. Rectification Plan — Waves, Phases, Success Criteria

### 5.1 Wave Summary

| Wave | Phase IDs | Focus | Est. Tokens (UNRESOLVED-ESTIMATE) | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| **W1 — Doctrine lift** | P1.1, P1.2, P1.3 | Rewrite `docs/reference/_notes/agentic_process_mapping_v34.md` §2 to close GAP-D1..GAP-D17; add companion ADR for the revised L1 output contract. | 🟡 ~12k | Single doc + one ADR; no code. | **Done 2026-04-23** | §2 explicitly covers all 17 BP rows; ADR-043 created + registered in Notion ADR Registry; no §3–6 edits required yet. |
| **W2 — Contract expansion** | P2.1, P2.2, P2.3 | Expand `L1PlanContract` from 7 → 14 typed v2 fields + `ReasoningMode` selection rubric + `ExpectedGroundTruth` per step + thought-redaction canary. Build `L1PlanContractV2` alongside v1 with `from_v1`/`to_v1` shims. CI schema gate added. | 🟡 ~18k | Back-compat shim for 90-day window; CI schema check added. | **Done 2026-04-23** | v2 types land; `L1PlanContractV2` validates all 14 fields; 31 new v2 tests + 32 legacy v1 tests all pass; CI gate `check_l1_plan_contract_fields.py` exits 0. |
| **W3 — Evaluator-optimizer + clarify/replan** | P3.1, P3.2, P3.3 | Add `evaluator_optimizer.run_evaluator_optimizer_loop` (pure primitive, budget-bounded draft↔critique). Add `plan_clarify` + `ClarifyDecision` + `ACTION_REQUEST_CLARIFICATION` to abstain_contract (SSOT) with L1 `clarify_planner` shim. Add `replan_contract` with `ReplanRequest`, `validate_replan_request`, `advance_replan_depth`, `MAX_REPLAN_DEPTH=3`. | 🟡 ~20k | No new MCP dependency; pure L1 module wiring. | **Done 2026-04-23** | Loop primitive covers ACCEPT/REFINE_EXHAUSTED/BUDGET_EXHAUSTED/ESCALATE with injected clock; clarify decision distinct from abstain; replan depth capped + advance helper; 99/99 new tests pass + 34/34 legacy abstain tests still pass. |
| **W4 — Budget, overhead, redaction, dev-message** | P4.1, P4.2, P4.3 | Replace `budget_enforcer.py` stub with real iteration/time/token caps. Add `planner_overhead_metric` emitter in `reasoning_chokepoint`. Split dev-msg vs sys-msg in `prompt_template_manager`. Implement thought-redaction at L1→L0 boundary. | 🟡 ~16k | OTel metrics route through existing `meta_observability`. | Todo | All 4 primitives live; baseline A/B (planner-on vs planner-off) captured in OTel; dev/sys split documented. |
| **W5 — Test + SVP review** | P5.1, P5.2, P5.3 | Raise unit + contract coverage on revised `L1PlanContract` to ≥90%. Add golden tests for clarify/abstain/replan branches. SVP Engineering review + Author-Gate calibration report. | 🟡 ~14k | `pytest_mcp` healthy; coverage gate enabled. | Todo | ≥90% on `L1_cognition/types/plan_contract_types.py` + `reasoning_chokepoint.py` + `plan_creator.py`; SVP row in Notion; calibration report clean. |

### 5.2 Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens (UNRESOLVED-ESTIMATE) | Status |
|---|---|---|---|---|---|
| **P1.1** | Doctrine edit §2 — add BP-O1/O2/O3/O6, BP-G1/G2/G3/G5, BP-A1/A3/A4 | `docs/reference/_notes/agentic_process_mapping_v34.md` (§2 only) | Must not silently widen §3–6; keep ASCII-art intact | 🟢 ~5k | Todo |
| **P1.2** | Clarify / abstain / refine / replan branch diagram | same file, §2 | Risk of diagram drift with §3 route-switch box | 🟡 ~4k | Todo |
| **P1.3** | ADR for revised L1 output contract (9 fields + thought redaction) | `docs/architecture/adr/ADR-<next>.md` + Notion ADR Registry row | ADR numbering + auto-routing to Notion | 🟢 ~3k | Todo |
| **P2.1** | Typed-field expansion on `L1PlanContract` (+ `PlanStep.expected_ground_truth`) | `agentic_core/L1_cognition/types/plan_contract_types.py`, `reasoning_plan.py` | Frozen dataclass migration; Author-Gate required (schema change) | 🟡 ~7k | Todo |
| **P2.2** | `ReasoningPlan → L1PlanContract` adapter + back-compat shim | `plan_creator.py`, `types/plan_contract_types.py` | Existing L0 consumers assume 7 fields | 🟡 ~5k | Todo |
| **P2.3** | CI schema gate (`check_l1_plan_contract_fields.py`) | `ops_scripts/ci/` | Gate must fail-closed on regression | 🟢 ~6k | Todo |
| **P3.1** | Wire `reasoning_evaluation` into `plan_creator` as critic-refiner loop with bounded iterations | `plan_creator.py`, `reasoning_evaluation.py`, `enforcement/budget_enforcer.py` | Risk of infinite refine loop if budget not wired first | 🟡 ~8k | Todo |
| **P3.2** | Add `clarify_planner.py` + `ACTION_REQUEST_CLARIFICATION` | new `agentic_core/L1_cognition/reasoning/clarify_planner.py`, `runtime/contracts/abstain_contract.py` | Must not collide with runtime HITL (ADR-023) | 🟡 ~6k | Todo |
| **P3.3** | `replan_primitive` re-entry contract from [5] EXIT EVAL | `agentic_core/L3_orchestration/exit_control/` ↔ `L1_cognition/reasoning/plan_creator.py` | Cross-layer; tight gravity check | 🟡 ~6k | Todo |
| **P4.1** | Real `budget_enforcer` (iteration, wall-clock, tokens) | `enforcement/budget_enforcer.py` | Default caps must be configurable | 🟢 ~4k | Todo |
| **P4.2** | `planner_overhead_metric` emitter | `enforcement/reasoning_chokepoint.py`, `reasoning/meta_observability.py` | OTel semantic attr naming | 🟢 ~4k | Todo |
| **P4.3** | Dev-msg vs sys-msg split + thought redaction at L1→L0 | `prompt_template_manager.py`, `types/plan_contract_types.py` | L5 policy ordering must be preserved | 🟡 ~8k | Todo |
| **P5.1** | Unit + contract tests for revised `L1PlanContract` + adapter | `tests/unit/agentic_core/L1_cognition/` | Coverage ≥90% on target files | 🟡 ~6k | Todo |
| **P5.2** | Golden tests for clarify / abstain / replan / graceful-fallback branches | `tests/integration/L1_cognition/` | Fixtures for exit-gate feedback | 🟡 ~5k | Todo |
| **P5.3** | SVP Engineering review row + Author-Gate calibration report | Notion SVP Engineering Reviews + `docs/reports/author-gate/` | Author-Gate cadence scheduled | 🟢 ~3k | Todo |

### 5.3 Gap Register (machine-checkable closure map)

| Gap ID | Closed by Phase |
|---|---|
| GAP-D1 | P1.1 |
| GAP-D2 | P1.1, P3.1 |
| GAP-D3 | P1.1, P2.1 |
| GAP-D4 | P1.1, P4.1 |
| GAP-D5 | P1.1 |
| GAP-D6 | P1.1, P4.3 |
| GAP-D7 | P1.2, P3.2 |
| GAP-D8 | P1.1, P2.1 |
| GAP-D9 | P1.1, P3.1 |
| GAP-D10 | P1.1 |
| GAP-D11 | P1.3, P2.1 |
| GAP-D12 | P1.1, P3.1 |
| GAP-D13 | P1.2, P3.3 |
| GAP-D14 | P1.1, P4.2 |
| GAP-D15 | P1.1, P4.3 |
| GAP-D16 | P1.1, P2.1 |
| GAP-D17 | P4.2 |
| GAP-R1 | P2.1 |
| GAP-R2 | P2.2 |
| GAP-R3 | P3.1 |
| GAP-R4 | P3.2 |
| GAP-R5 | P3.3 |
| GAP-R6 | P4.1 |
| GAP-R7 | P1.1, P2.1 |
| GAP-R8 | P2.1 |
| GAP-R9 | P4.2 |
| GAP-R10 | P4.3 |
| GAP-R11 | P2.1, P4.2 |
| GAP-R12 | P3.1 |
| GAP-R13 | P4.3 |
| GAP-R14 | P5.1 |
| GAP-R15 | P4.2 |

---

## 6. Execution Entry Criteria (must be satisfied before W1 starts)

1. Author-Gate packet resolved for "Contract schema change on `L1PlanContract`" (blocks W2).
2. Token estimator run on W1–W5 phases; estimates moved from UNRESOLVED-ESTIMATE → concrete values.
3. ADG snapshot regenerated to capture any L1 fan-in changes at W1 baseline.
4. SVP Engineering reviewer named for W5 sign-off.
5. MCP green light (`adg_sqlite` + `redis`) for any T2/T3 execution wave.

---

## 7. Non-Goals

- No edits to §3 (routing), §4 (execution), §5 (exit eval), §6 (universal write gate), §7 (policy plane) in this plan.
- No new MCP server; no new runtime dependency; no LLM-model swap.
- No ADR-023 runtime HITL changes — this plan is scoped to **author-gate / developer-loop L1 planning semantics**, not runtime exit control.

---

## 8. Open Questions (flag at W1 Author-Gate)

- **OQ1**: Should `published_rationale` (redacted thought stream) be mandatory or opt-in per work class?
- **OQ2**: Default iteration budget for evaluator-optimizer — 1, 2, or 3 refinement passes?
- **OQ3**: Should `ACTION_REQUEST_CLARIFICATION` return to ingress [1] or surface at [5] EXIT EVAL?
- **OQ4**: Confidence-score rubric anchored on what? Prior success rate, L5 risk class, or fixed per-route table?
