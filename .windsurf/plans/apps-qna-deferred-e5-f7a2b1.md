---
plan_id: apps-qna-deferred-e5-f7a2b1
plan_type: deferred_scope
parent_plan: apps-qna-spine-deferred-e9c5b3
---

# apps_qna — E5 Deferred Scope

Deferred scope items from the completed `apps-qna-spine-deferred-e9c5b3` plan (D1–D4, 108 tests).
These items were explicitly deferred during implementation and require future work to move from
stub/heuristic/optional to production-grade implementations.

**Parent Plan**: `.windsurf/plans/apps-qna-spine-deferred-e9c5b3.md` (Completed)
**Created**: 2026-05-05

---

## Wave Structure

| Wave | Focus | Est. Tokens | Status |
|------|-------|-------------|--------|
| E1 | Real C0 vector-store retrieval (replace stub fetcher) | ~35K | 🔲 TODO |
| E2 | Production LLM judges (replace deterministic heuristics) | ~40K | 🔲 TODO |
| E3 | Live provider SDK dispatch (replace stub model execution) | ~30K | 🔲 TODO |
| E4 | Exit-eval hook adoption + __main__.py integration | ~20K | 🔲 TODO |
| E5 | SSOT enforcement gate + config drift CI | ~15K | 🔲 TODO |

---

## Deferred Items

### E1: Real C0 Vector-Store Retrieval (~35K)

**E1.1: Replace stub fetcher in c0_adapter.py**
- Current: `_call_canonical_c0()` uses `_stub_fetch` returning an empty `CandidateEvidencePool`
  and `_stub_adjacency` returning `()`. No vector store is queried.
- File: `apps_qna/c0_adapter.py` lines 96–100
- Needed: Wire a real BGE-M3 / embedding-backed vector store for interview card retrieval.
  The `_stub_fetch` signature is `(plan, route) -> CandidateEvidencePool` — replace with a
  real fetcher calling `apps_qna/integrations/spine_adapter.py` or a dedicated retrieval store.
- Impact: Changes `evidence_sufficiency` from `template_only` → `grounded` for real slugs;
  unlocks real `FinalEvidenceContract.grounded=True` paths throughout the eval pipeline.
- Dependencies: A vector store populated with interview card embeddings (BGE-M3 via spine_adapter).

**E1.2: Populate interview card vector store**
- Current: No store exists; `spine_adapter.py` wraps BGE-M3 but has no indexed corpus.
- Needed: Index the canonical card corpus (22 cards × N interview archetypes) into a
  retrievable store (ChromaDB or equivalent) keyed by `interview_slug`.
- Impact: Prerequisite for E1.1.

### E2: Production LLM Judges (~40K)

**E2.1: context_recall_judge.py — replace heuristic with LLM call**
- Current: `IS_STUB = False, IS_CALIBRATED = True` but scoring is deterministic heuristic:
  `min(len(retrieved ∩ required) / max(len(required), 1), 1.0)` with length-adequacy fallback.
  File: `apps_qna/engines/judges/context_recall_judge.py`
- Needed: Replace heuristic with an LLM judge call (e.g. GPT-4 / Claude) that evaluates
  whether retrieved context contains the necessary evidence to answer the question.
  Should use `QnaProviderContext` from `apps_qna/integrations/provider_adapter.py`.
- Impact: Real quality scores; enables calibrated holdout evaluation.

**E2.2: context_precision_judge.py — replace heuristic with LLM call**
- Current: Deterministic overlap-score heuristic between retrieved and required sources.
  File: `apps_qna/engines/judges/context_precision_judge.py`
- Needed: LLM judge evaluating precision — are the retrieved sources relevant and not noisy?

**E2.3: answer_relevancy_judge.py — replace heuristic with LLM call**
- Current: Keyword-overlap heuristic between card answer text and query.
  File: `apps_qna/engines/judges/answer_relevancy_judge.py`
- Needed: LLM judge evaluating whether the answer is responsive to the question posed.

**E2.4: Judge calibration against holdout corpus**
- Current: Judges are deterministic; no calibration baseline exists.
- Needed: Run E2.1–E2.3 judges against the holdout partition
  (`EvalSetPolicy`, `apps_qna/config/eval_set_policy.py`) and establish a Spearman
  rank-correlation baseline against human judgments.
- Impact: Enables automated quality regression detection in CI.

### E3: Live Provider SDK Dispatch (~30K)

**E3.1: Wire QnaProviderContext to a real model call**
- Current: `apps_qna/integrations/provider_adapter.py` exposes `QnaProviderContext` with
  `model_id`, `max_tokens`, `temperature`, `has_model()` — but no actual model call is made.
  `build_provider_context()` acquires the canonical clock but has no dispatch path.
- Needed: Add `dispatch(prompt: str) -> str` to `QnaProviderContext` that calls the model
  identified by `model_id` via the canonical `agentic_core` provider SDK when `has_model()`
  is True. Must be fail-open — if model unavailable, return `""`.
- Impact: Enables the `R4_SINGLE_ACTION` live-interview route to make a real model call.

**E3.2: Wire PA adapter dispatch to provider**
- Current: `apps_qna/card_context/pa_adapter.py` runs PA.0–PA.7 pipeline checks but
  `dispatchable=True` does NOT trigger a model call — it just validates the context.
- Needed: When `dispatchable=True`, call `QnaProviderContext.dispatch()` with the
  assembled card context as the prompt. Return model output as `PAAdapterResult.model_output`.
- Impact: First real model-in-the-loop path for apps_qna.

### E4: Exit-Eval Hook Adoption + __main__.py Integration (~20K)

**E4.1: Wire maybe_invoke_exit_eval in __main__.py**
- Current: `apps_qna/config/cert_route_registry.yaml` has `invoke_exit_eval: true` but
  `apps_qna/__main__.py` does NOT call `maybe_invoke_exit_eval` from
  `apps_shared/cert/exit_eval_hook.py`. The flag is set but never checked at runtime.
  File: `apps_qna/__main__.py`
- Needed: Import and call `maybe_invoke_exit_eval(run_context, route_registry)` in the
  main run path, after the exit packet is emitted, to trigger the AppSpecificEvaluator.
- Pattern: `apps_rfp/__main__.py` already adopts this hook.
- Impact: Exit eval scores surface in `AppSpecificEvalResult`; enables HITL escalation.

**E4.2: emit_uwg_pack_record adoption in __main__.py**
- Current: `emit_uwg_pack_record()` from `apps_qna/exit_wiring.py` exists and is tested
  but is NOT called anywhere in the live run path — only reachable from tests.
- Needed: Call `emit_uwg_pack_record(manifest=..., exit_packet=..., enabled=cfg.uwg_enabled)`
  in `__main__.py` after the sealed manifest is built, gated by a config flag.
- Impact: Enables optional durable L4 state writes for interview packs.

### E5: SSOT Enforcement Gate + Config Drift CI (~15K)

**E5.1: Promote config_inventory scan to a CI gate**
- Current: `apps_qna/config/config_inventory.py` `scan_config_inventory()` runs as a
  library function with test coverage but is NOT wired into CI.
- Needed: Create `ops_scripts/ci/check_apps_qna_config_drift.py` that runs
  `scan_config_inventory()` and fails when `drift_violations` is non-empty or when
  any `policy_hash`-bearing config has a missing `version` or `status` field.
- Impact: Prevents silent policy_hash / version drift between domain_contract YAMLs.

**E5.2: Spine alignment gate**
- Current: `apps_qna/config/spine_alignment.py` `check_spine_alignment()` runs as a
  library function with test coverage but is NOT wired into CI.
- Needed: Add `check_spine_alignment()` call to the apps-spine-coverage CI scanner
  (`tools/analysis/apps_spine_coverage.py`) so unknown route types cause a gate failure.
- Impact: Prevents apps_qna from silently drifting to an unregistered route pattern.

**E5.3: Holdout partition lock after corpus freeze**
- Current: `EvalSetPolicy` (D3.2) assigns partitions deterministically by SHA-256 hash
  but the `salt` is mutable and not locked — changing it reassigns all slugs.
- Needed: Freeze the salt in `apps_qna/config/domain_contract/eval_rubrics.yaml` under
  a `holdout_salt` field and make `DEFAULT_EVAL_SET_POLICY` read it at import time.
  Add a CI check that alerts when `holdout_salt` changes (corpus-reassignment risk).
- Impact: Prevents accidental holdout contamination when the eval corpus grows.

---

## Success Criteria

- [ ] C0 adapter calls real vector store (evidence_sufficiency = "grounded" for indexed slugs)
- [ ] All three RAG judges backed by LLM calls (not deterministic heuristics)
- [ ] Judge Spearman-rank calibration baseline established on holdout corpus
- [ ] QnaProviderContext.dispatch() makes real model calls when model_id configured
- [ ] PA adapter dispatchable path triggers model execution
- [ ] maybe_invoke_exit_eval called in __main__.py run path
- [ ] emit_uwg_pack_record called in __main__.py (gated by config flag)
- [ ] config_inventory drift scan wired into CI (ops_scripts/ci/check_apps_qna_config_drift.py)
- [ ] spine_alignment check wired into apps-spine-coverage CI scanner
- [ ] holdout_salt frozen in eval_rubrics.yaml with change-detection gate

---

## Implementation Notes

- **E1 prerequisite**: Vector store population (E1.2) must complete before E1.1.
- **E2 prerequisite**: Real model credentials / provider SDK in CI environment.
- **E3 prerequisite**: E2 judges must exist before provider dispatch adds value.
- **E4 can be done independently** — no dependency on E1/E2/E3.
- **E5 can be done independently** — purely CI/gate wiring.

Suggested sequencing: E4 → E5 → E1 → E2 → E3 (ascending cost/risk).

---

PLAN_CREATED: slug=apps-qna-deferred-e5-f7a2b1 path=.windsurf/plans/apps-qna-deferred-e5-f7a2b1.md waves=5 phases=12 tokens=140K
