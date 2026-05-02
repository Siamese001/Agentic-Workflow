# Audit Backlog Closeout — Read-Only Investigations

**Date:** 2026-05-02
**Plan reference:** `.windsurf/plans/agentic-core-eval-control-audit-backlog-closeout-e7f2a8.md`
**Prior reports closed:**
- `docs/reports/agentic_core_eval_control_audit/2026-05-02.md` (parent)
- `docs/reports/agentic_core_eval_control_audit/2026-05-02-per-module-followup.md` (per-module)
- `docs/reports/agentic_core_eval_control_audit/2026-05-02-gap-closure.md` (operational verdict)
- `.windsurf/plans/agentic-core-eval-implementation-d4e9c2.md` (implemented F-2/F-3/F-4/F-5/P-1/P-2/P-4)

**Scope:** the 6 read-only audit items the implementation plan flagged as out-of-scope (discovery only): P-3, P-5, P-6, P-8, F-1, F-6.

**Constraints honored:** No code changes. No patches. No refactors. Single-file Markdown deliverable.

**ADG provenance:** backend=`sqlite+fs`, snapshot=`artifacts/adg/adg_indexed_04292026_0654.sqlite`.

---

## P-3 · `g22_output_quality.py` upstream scorer (closed)

**Question:** Who writes `groundedness` / `faithfulness` / `citation_support` / `completeness` / `task_fit` into `ctx.output` before G22 reads them?

**Method:** grep across `agentic_core/` for the five field names; rank by match count to surface canonical producers.

**Finding:** the canonical runtime producer is `agentic_core/utils/workflow_engines/groundedness.py` (82 matches — the dominant hit). Module docstring (lines 1-8): *"Measures whether the generated answer is supported by retrieved context. Uses token-overlap heuristic (F1 over unigrams) as a deterministic zero-dependency approximation. An LLM-judge variant is available via the optional judge callable injected at construction time."*

**Implication:** the seam the parent audit recommended (Qwen-bound upstream scorer) **already exists** as an injected callable parameter. The default behavior is the deterministic F1 heuristic, NOT a Qwen judge. To make the audit's recommendation operational, callers that construct the groundedness scorer must inject a judge callable (e.g. wrap `evaluation/judges/qwen_judge_provider.py::QwenJudgeProvider.judge` or `L5_safety/eval_spine/judge_backends/qwen_vllm.py::QwenVllmBackend`). No new code is required to make the seam available.

**Secondary producers worth a future pass:**

- `agentic_core/L6_observability/utils/evaluation/shadow_eval_grader.py` (33 matches) — shadow-only, correctly Ensemble Only per parent audit.
- `agentic_core/L4_state/reasoning/meta_learning_feedback.py` (23 matches) — offline meta-learning, out of scope for runtime gates.
- `agentic_core/evaluation/judges/llm_judge.py` (23 matches) — RAG-eval harness, hardcoded Gemini binding.
- `agentic_core/L4_state/utils/memory/retrieval_eval_registry.py` (21 matches) — retrieval-eval registry.
- `agentic_core/L3_orchestration/exit_eval/factory.py` (15 matches) — Exit-side factory.
- `agentic_core/L3_orchestration/reasoning/engines/l4e_retrieval_integration.py` (16 matches) — L4E retrieval integration.

**Status:** **CLOSED.** Producer identified. Seam already exists. No code change required to enable the audit recommendation; recommendation now reads as "wire a Qwen callable into `groundedness.py`'s injected judge parameter at construction time".

**Severity revision:** parent gap was tagged `medium`. Revised to `low` — the producer is identified and the integration seam is already in place; only call-site wiring remains.

---

## P-5 · L1 semantic judges abstain → HITL wiring (closed with mixed findings)

**Question:** Do `retrieval_grader.py`, `retrieval_reflexion.py`, `plan_creator.py`, `plan_self_repair.py` route their abstain output to G06 HITL, or do they swallow it?

**Method:** grep each file for `abstain` / `UNKNOWN` / `HITL` / `escalate` / `G06`.

| Module | abstain wiring present | HITL routing | Verdict |
|---|---|---|---|
| `retrieval_grader.py` | **no matches** for any of the four terms | none | **GAP**: grader emits a relevance verdict but does not signal abstain at all; downstream cannot route what it does not see |
| `retrieval_reflexion.py` | yes — `OUTCOME_ABSTAINED` (L6 semconv constant) emitted on (a) two consecutive all-irrelevant passes, (b) `ReflectionNextAction.ABSTAIN` from grader, (c) retriever exception | **partial**: outcome attribute is published to L6 telemetry; no direct route into G06 visible in this module — terminal abstain, not escalation | acceptable for a reflection-loop but does not enforce HITL |
| `plan_creator.py` | yes — `_emit_escalates_to_human("p1", "plan_creator", "L1")` lifecycle event emitted | **partial**: `_emit_escalates_to_human` is a contract event (telemetry-shape), not a direct G06 invocation. Whether G06 picks it up depends on the L6 → G06 wiring (not inspected here) | seam exists, terminal-vs-route question deferred |
| `plan_self_repair.py` | yes — `ClarifyOrAbstainMarker.FALLBACK` set on unrepairable plans (cap at 2 iterations) | **none**: marker is terminal; no escalation event. Module docstring (line 12) explicitly says "**deterministic** — no LLM calls, no retrieval, no tool use" | abstain is final-state, not escalation |

**Implication:** the parent audit gap is real. `retrieval_grader.py` does not even emit an abstain signal. `plan_self_repair.py` and `retrieval_reflexion.py` produce terminal abstain states without HITL routing. `plan_creator.py` emits a `_emit_escalates_to_human` lifecycle event, which is the strongest of the four — but whether that event triggers G06 depends on L6 wiring outside this module.

**Recommendation:** keep the gap open. The actionable next step is **NOT** in any of the four modules — it is in the L6 telemetry → G06 routing layer, which decides whether `_emit_escalates_to_human` events become G06 ledger entries. That is a separate audit pass.

**Status:** **CLOSED with confirmed gap.** Per-module wiring documented; root cause is in the L6 → G06 routing layer, not in the four L1 modules. Severity remains `medium`.

---

## P-6 · `mixture_of_experts.py` and `ensemble_router.py` — agent-swarm risk (closed)

**Question:** Do these L0 modules implement an agent-swarm pattern (forbidden), or deterministic gating across pre-defined provider adapters (allowed)?

**Method:** read first 120 lines of each.

**`mixture_of_experts.py`:**

- `ExpertSpecialization.matches_query(query)` (lines 44-49): pure string matching. `match_ratio = keyword_matches / len(self.keywords) if self.keywords else 0.0; return match_ratio * self.capability_score`
- `BaseExpert` (lines 81-117): abstract base for routing experts with `predict(query, context) -> ExpertPrediction`. Each expert is a routing decision-maker, not a generative agent.
- `MoEDecision` (lines 66-78): the output is a `selected_expert` + `selected_agent` pair with confidence scores — a routing decision, not a generated artifact.

**Verdict:** deterministic gating. The MoE name refers to the architecture pattern (gating network choosing among specialized routing experts via keyword + capability score), NOT agent-swarm candidate generation. Audit row #8 classification `None` is correct.

**`ensemble_router.py`:**

- `RoutingPrediction` (lines 33-41): one prediction = `(agent_name, confidence, uncertainty, ...)` — a routing pick, not generated content.
- `EnsembleFeatures` (lines 44-83): statistical aggregation features — `mean_confidence`, `std_confidence`, `max_confidence`, `agent_agreement_score`, `top_agent_consensus`, `agent_diversity`, `mean_uncertainty`, `std_uncertainty`, `uncertainty_correlation`, `model_weights`, `model_reliability`. All deterministic statistics.
- `EnsembleDecision` (lines 86-97): final pick + meta-learner confidence — a single routing decision.
- `BaseRoutingModel` (lines 100-118): routing model protocol with `predict()` returning a `RoutingPrediction`. Not a generative agent.

**Verdict:** deterministic ensemble of routing models with meta-learner. The "ensemble" refers to combining base routing models (each deterministic) via statistical features and a meta-learner — classic MAB / ensemble-learning pattern, not candidate-generator swarm. Audit row #8 classification `None` is correct.

**Status:** **CLOSED.** No agent-swarm pattern detected in either file. Both correctly classified `None` in the parent audit. No follow-up action.

---

## P-8 · `_history_summarizer_llm.py` role classification (closed)

**Question:** Is this module a generative compression assistant (None) or a judging surface (Judge)?

**Method:** read full file (96 lines, complete).

**Findings:**

- Module docstring (lines 1-22): "*Pluggable backend for the EQ-8 compressor. When `USE_LLM_SUMMARIZER=1` is set, the compressor's call site may replace an evicted block of messages with an LLM-generated summary instead of discarding them outright. Feature-flag gated and default-off. The rule-based EQ-8 compressor remains the deterministic authority. Any failure in the LLM path falls back to rule-based compression silently — the contract is 'summarization is a best-effort optimization, never a correctness hinge'.*"
- `Summarizer` Protocol (line 40): `summarize(messages: list[dict]) -> str` — emits a summary string, not a verdict.
- `NullSummarizer` (line 48): deterministic placeholder that returns `f"[summary placeholder — {n} message(s) elided]"`.
- `summarize_or_fallback` (line 58): safe-entry helper that catches any exception and returns a fallback string.
- The actual file does **not** invoke any LLM. It is a Protocol + Null impl + safe-call helper. LLM-backed implementations would live elsewhere (not in this file).

**Verdict:** generative compression assistance, NOT judging. Audit row #52 (parent) classified `L2_execution/enforcement/*` 43-module group as `None`, with this specific file noted in §6 gaps as needing role confirmation. **Confirmed `None`.** This module produces narrative summaries (when an LLM is wired) — it does not produce a score, verdict, or disposition. The boundary rule "judges recommend, never commit" applies trivially here because no judging happens.

**Status:** **CLOSED.** Audit classification `None` confirmed correct. No follow-up action.

---

## F-1 · `config/judges/trace_rubric.yaml` content inspection (closed with audit clarification)

**Question:** Does the trace-grader rubric YAML declare LLM-backed dimensions, as the parent audit row #103 implied?

**Method:** read full file (150 lines).

**Findings:**

- Schema reference: `agentic_core.evaluation.judges.trace_rubric_schema_v1`.
- Five dimensions declared: `tool_selection`, `handoff_fired_when_required`, `instruction_adherence`, `safety_policy_adherence`, `trajectory_shape`.
- **NONE of the five dimensions carry a `scoring_method: llm_pointwise` field** (the field that signals LLM judging in the sibling `rubrics.json`).
- All five dimensions correspond to entries in `_DEFAULT_SCORERS` in `agentic_core/L5_safety/eval_spine/trace_grader.py` (lines 223-229) — `_score_tool_selection`, `_score_handoff`, `_score_instruction_adherence`, `_score_safety_policy`, `_score_trajectory_shape` — all deterministic Python functions.
- The YAML declares `unknown_budget` per dimension (0.10 to 0.25) and an aggregate `unknown_budget: 0.30` at file scope. The Unknown-budget mechanism EXISTS, but is currently only triggered by deterministic scorer abstain paths (e.g. when `tool_selection` has no `expected_tools` set), not by LLM abstention.

**Implication:** the parent audit row #103 stated "ADR-036 declares LLM-backed dimensions but defaults to Unknown unless `register_dim_scorer(dim, callable)` is invoked at init". This claim is **partially incorrect**: the YAML declares NO LLM-backed dimensions today. The seam (`register_dim_scorer`) exists and would let an operator register a Qwen scorer for any of the five dims, OR for a NEW dim added to the YAML. But there is no LLM dim sitting unregistered today — the gap is that the rubric YAML has not yet adopted any of the 10 new LLM rubrics added to `evaluation/judges/rubrics.json` in plan `d4e9c2`.

**Audit correction:** parent gap row P-4 should be reframed. The actionable items are:

1. Decide which of the 10 new `rubrics.json` LLM rubrics belong in `trace_rubric.yaml` (the runtime trace grader is per-trajectory; some `rubrics.json` rubrics are per-output and don't fit).
2. Add those dims to `trace_rubric.yaml` with `scoring_method: llm_pointwise` (or equivalent flag).
3. Wire `QwenVllmBackend` (just authored in plan `d4e9c2`) via `register_dim_scorer` for each new LLM dim.

**Status:** **CLOSED.** YAML inspected; trace_rubric is currently 100% deterministic. The audit's framing is corrected: the gap is "rubric YAML does not yet declare LLM dims", not "LLM dims declared but unscorered". This refines but does not invalidate the parent recommendation. Severity remains `medium`.

---

## F-6 · Two large L5/reasoning files deeper-read (closed)

**Question:** Are `ArchitectureGovernorAgent.py` (75KB) and `FileClassificationAgent.py` (256KB) correctly classified `None` (deterministic) per the per-module follow-up audit?

**Method:** read first 60 lines of each.

**`ArchitectureGovernorAgent.py` (1551 lines total):**

- Imports `from agentic_core.L2_execution.utils import write_gateway as _wg` — uses UWG for any state writes, boundary-compliant.
- 30+ lifecycle-trace-contract emitter calls at module load: `_emit_dispatches_healing_run`, `_emit_routes_through`, `_emit_checks_agent_registry`, `_emit_validates_agent_capability`, `_emit_dispatches_execution_plan`, `_emit_agent_executes_agent`, `_emit_routes_to_agent`, `_emit_verifies_policy`. These are P0-level governance emitters — confirmation that this is a SovereignBaseAgent-style governance agent.
- No imports from any LLM provider, no judge module imports, no rubric imports. The 1551-line body is structural governance — layer-gravity invariants, boundary checks, hierarchy validation.

**Verdict:** structural / governance. `None` classification is correct.

**`FileClassificationAgent.py` (5684 lines total):**

- Module-level comment line 1: `# guardian: allow-silent_swallower` — flagged anti-pattern but exempted with guardian comment.
- Same UWG / lifecycle-trace-contract emitter pattern as ArchitectureGovernorAgent.
- 256KB file size in a rule-based classification agent is consistent with very large rule tables / classification matrices, not with a judge — judges are typically small (a few hundred lines for the protocol + parser + adapter).
- No judge / LLM provider imports visible in the head.

**Verdict:** rule-based classification agent. `None` classification is correct. The 256KB likely represents an extensive built-in rule table.

**Optional follow-up (not blocking):** the `# guardian: allow-silent_swallower` comment at module top of `FileClassificationAgent.py` is anomalous (no specific justification visible in the first 60 lines). A focused anti-pattern audit could review whether the swallower exemption is well-scoped. Out of scope for this read-only pass.

**Status:** **CLOSED.** Both classifications confirmed correct. One optional follow-up (anti-pattern review of the FileClassificationAgent silent swallower comment) noted but not actioned.

---

## Summary Table

| gap_id | original severity | finding | revised severity | actionable next step | status |
|---|---|---|---|---|---|
| P-3 | medium | Producer is `utils/workflow_engines/groundedness.py`; F1-heuristic default with optional judge callable seam | low | Wire Qwen callable into the groundedness scorer's injected judge parameter at call site | closed |
| P-5 | medium | `retrieval_grader.py` lacks abstain entirely; `retrieval_reflexion.py` and `plan_self_repair.py` produce terminal abstain without HITL routing; `plan_creator.py` emits `_emit_escalates_to_human` event but G06 wiring not verified here | medium | Audit the L6 → G06 routing layer to confirm escalation events become ledger entries | closed (gap confirmed) |
| P-6 | low | Both modules are deterministic gating, not agent-swarm | low | none | closed |
| P-8 | low | Pure Protocol + Null impl + safe-call helper; no LLM call inside this file | low | none | closed |
| F-1 | medium | trace_rubric.yaml declares 0 LLM-pointwise dimensions today; all 5 dims are deterministic; the seam to register LLM scorers exists but is not used | medium | Decide which of the 10 new `rubrics.json` LLM rubrics to add to `trace_rubric.yaml` and wire `QwenVllmBackend` for each | closed (audit reframed) |
| F-6 | low | Both large L5 files are structural / rule-based; classifications correct | low | optional anti-pattern audit on `FileClassificationAgent.py`'s silent-swallower exemption | closed |

---

## Final Determination

**`AUDIT_BACKLOG_OPERATIONALLY_CLEARED`** — read-only investigations complete. Of the 6 items:

- 3 closed with no follow-up action needed (P-6, P-8, F-6).
- 2 closed with refined understanding that revises the audit framing rather than introducing new code work (P-3 severity dropped to `low`, F-1 audit framing corrected).
- 1 closed with confirmed gap that requires a separate audit pass on a different layer (P-5 → L6 → G06 routing verification).

No code changes proposed. No new plan rows opened beyond this closeout. The original three-report audit chain (parent + per-module + gap-closure) plus the `d4e9c2` implementation plan plus this closeout collectively cover the full audit lifecycle for the agentic_core eval/control review.

---

**End of backlog closeout.** Zero code changes. Zero patches. Zero refactors. Single Markdown deliverable under `docs/reports/agentic_core_eval_control_audit/`.
