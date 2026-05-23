---
plan_id: apps-qna-deferred-e1e3e5-3d3708
plan_type: deferred_scope
parent_plan: apps-qna-deferred-e5-f7a2b1
---

# apps_qna — E1/E3/E5 Deferred Scope

Deferred scope items from parent plan `apps-qna-deferred-e5-f7a2b1`. Wave E4 is complete;
these remaining waves require infrastructure or external dependencies before implementation.

**Parent Plan**: `.windsurf/plans/apps-qna-deferred-e5-f7a2b1.md` (E4 Complete, E1/E3/E5 Deferred)
**Created**: 2026-05-05

---

## Wave Structure

| Wave | Focus | Est. Tokens | Status | Blocker |
|------|-------|-------------|--------|---------|
| E1 | Real C0 vector-store retrieval (replace stub fetcher) | ~35K | 🔲 TODO | Vector store populated with BGE-M3 embeddings |
| E3 | Live provider SDK dispatch (replace stub model execution) | ~30K | 🔲 TODO | E1 complete (C0 retrieval sources needed) |
| E5 | SSOT enforcement gate + config drift CI | ~15K | 🔲 TODO | None — can be done independently |

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
- **Blocker**: A vector store populated with interview card embeddings (BGE-M3 via spine_adapter).

**E1.2: Populate interview card vector store**
- Current: No store exists; `spine_adapter.py` wraps BGE-M3 but has no indexed corpus.
- Needed: Index the canonical card corpus (22 cards × N interview archetypes) into a
  retrievable store (ChromaDB or equivalent) keyed by `interview_slug`.
- **Blocker**: This is a prerequisite for E1.1. Requires:
  - BGE-M3 embedding model available
  - ChromaDB or similar vector store instance
  - ETL pipeline to index cards

### E3: Live Provider SDK Dispatch (~30K)

**E3.1: Wire QnaProviderContext to a real model call**
- Current: `apps_qna/integrations/provider_adapter.py` exposes `QnaProviderContext` with
  `model_id`, `max_tokens`, `temperature`, `has_model()` — but no actual model call is made.
  `build_provider_context()` acquires the canonical clock but has no dispatch path.
- Needed: Add `dispatch(prompt: str) -> str` to `QnaProviderContext` that calls the model
  identified by `model_id` via the canonical `agentic_core` provider SDK when `has_model()`
  is True. Must be fail-open — if model unavailable, return `""`.
- Impact: Enables the `R4_SINGLE_ACTION` live-interview route to make a real model call.
- **Blocker**: E2 judges should exist before provider dispatch adds value; also requires
  real model credentials in CI/production environment.

**E3.2: Wire PA adapter dispatch to provider**
- Current: `apps_qna/card_context/pa_adapter.py` runs PA.0–PA.7 pipeline checks but
  `dispatchable=True` does NOT trigger a model call — it just validates the context.
- Needed: When `dispatchable=True`, call `QnaProviderContext.dispatch()` with the
  assembled card context as the prompt. Return model output as `PAAdapterResult.model_output`.
- Impact: First real model-in-the-loop path for apps_qna.
- **Blocker**: E3.1 must be complete first.

### E5: SSOT Enforcement Gate + Config Drift CI (~15K)

**E5.1: Promote config_inventory scan to a CI gate**
- Current: `apps_qna/config/config_inventory.py` `scan_config_inventory()` runs as a
  library function with test coverage but is NOT wired into CI.
- Needed: Create `ops_scripts/ci/check_apps_qna_config_drift.py` that runs
  `scan_config_inventory()` and fails when `drift_violations` is non-empty or when
  any `policy_hash`-bearing config has a missing `version` or `status` field.
- Impact: Prevents silent policy_hash / version drift between domain_contract YAMLs.
- **Blocker**: None — can be done independently.

**E5.2: Spine alignment gate**
- Current: `apps_qna/config/spine_alignment.py` `check_spine_alignment()` runs as a
  library function with test coverage but is NOT wired into CI.
- Needed: Add `check_spine_alignment()` call to the apps-spine-coverage CI scanner
  (`tools/analysis/apps_spine_coverage.py`) so unknown route types cause a gate failure.
- Impact: Prevents apps_qna from silently drifting to an unregistered route pattern.
- **Blocker**: None — can be done independently.

**E5.3: Holdout partition lock after corpus freeze**
- Current: `EvalSetPolicy` assigns partitions deterministically by SHA-256 hash
  but the `salt` is mutable and not locked — changing it reassigns all slugs.
- Needed: Freeze the salt in `apps_qna/config/domain_contract/eval_rubrics.yaml` under
  a `holdout_salt` field and make `DEFAULT_EVAL_SET_POLICY` read it at import time.
  Add a CI check that alerts when `holdout_salt` changes (corpus-reassignment risk).
- Impact: Prevents accidental holdout contamination when the eval corpus grows.
- **Blocker**: None — can be done independently.

---

## Implementation Notes

- **E1 prerequisite**: Vector store population (E1.2) must complete before E1.1.
  Requires BGE-M3 model and ChromaDB or similar vector store.
- **E3 prerequisite**: E2 judges should exist before provider dispatch adds value,
  but E3 can technically be stubbed with deterministic responses for wiring validation.
- **E5 can be done independently** — purely CI/gate wiring with no external dependencies.

Suggested sequencing when unblocked: E5 → E1 → E3 (E5 has no blockers, then E1, then E3).

---

## Success Criteria

- [ ] C0 adapter calls real vector store (evidence_sufficiency = "grounded" for indexed slugs)
- [ ] QnaProviderContext.dispatch() makes real model calls when model_id configured
- [ ] PA adapter dispatchable path triggers model execution
- [ ] config_inventory drift scan wired into CI (ops_scripts/ci/check_apps_qna_config_drift.py)
- [ ] spine_alignment check wired into apps-spine-coverage CI scanner
- [ ] holdout_salt frozen in eval_rubrics.yaml with change-detection gate

---

PLAN_CREATED: slug=apps-qna-deferred-e1e3e5-3d3708 path=.windsurf/plans/apps-qna-deferred-e1e3e5-3d3708.md waves=3 phases=7 tokens=80K
