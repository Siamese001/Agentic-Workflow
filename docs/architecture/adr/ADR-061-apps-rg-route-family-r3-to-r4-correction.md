# ADR-061: apps_rg Route Family Correction — R3_grounded_read → R4_SINGLE_ACTION

**Status:** Accepted  
**Date:** 2026-05-04  
**Plan:** `apps-rg-canonical-wireup-c8a4f2` W3 P5  
**Author-Gate decision:** W2 Option B (score 0.88, dominance fired, gap 0.26 vs Option A)

---

## Context

`apps_rg/spine_manifest.yaml` historically declared `type: R3_grounded_read` as its route shape. The `R3_grounded_read` shape requires corpus retrieval (C0 vector lookup) as a first-class step in the pipeline contract.

A pre-W3 audit of the live `apps_rg` codebase found **zero** C0 corpus retrieval calls:

- The Job Description is loaded from a local JSON file (`--jd` CLI arg).
- The company brief is loaded from a local JSON file (`--manual-brief` CLI arg).
- The master résumé is loaded from `apps_shared/data/master_resume.json`.
- No call to any vector store, ChromaDB, `c0_retrieval` module, or `L0_routing.c0_retrieval` exists in the pipeline path.

All three inputs are **preloaded deterministic context** — they arrive before the pipeline runs and do not require retrieval.

The `R3_grounded_read` declaration was therefore a contract fiction: the manifest claimed a capability that was never exercised.

---

## Decision

**Correct the route family to `R4_SINGLE_ACTION`.**

The `R4_SINGLE_ACTION` shape describes exactly what `apps_rg` does:
- Receives a deterministic request (target company + JD + master résumé).
- Loads all context from disk (preloaded inputs — no retrieval).
- Runs a deterministic HOP pipeline producing a single artifact (résumé draft).
- No `CommitRequest`, no `StateDiffCandidate`, no durable per-request state write.
- Output is a local artifact consumed by the requesting user.

The change is captured in:
- `apps_rg/spine_manifest.yaml` — `claimed_routes[0].type` changed from `R3_grounded_read` to `R4_SINGLE_ACTION`.
- `apps_rg/config/apps_rg_static_dag.yaml` — `route_family: R4_SINGLE_ACTION` declared.
- `apps_rg/config/l0_policy.yaml` — `default_capability: apps_rg.resume_generation_v1`.
- `apps_rg/integrations/preloaded_input_context_manifest.py` — new manifest records `c0_bypass_reason: GROUNDING_NOT_REQUIRED` and the three preloaded input file hashes.

---

## Consequences

### Positive
- **Contract truth**: the manifest now reflects what the code actually does.
- **C0 bypass receipt**: `apps_rg` now explicitly emits a `C0BypassReceipt(reason=GROUNDING_NOT_REQUIRED)` at the L0 gate, consistent with `apps_shared` bypass conventions.
- **Governance test coverage**: 19 new tests in `tests/governance/test_apps_rg_*.py` enforce the corrected contract and prevent silent regression to a retrieval posture.
- **Scanner accuracy**: `tools/analysis/apps_spine_coverage.py` will now correctly classify `apps_rg` in the R4 bucket, not the R3 bucket.

### Neutral
- The existing `anthropic_rag_entrypoint.py` module (renamed to `rg_pa_compiler.py` via compat wrapper in W3 P6) is preserved without modification. Its function — building an Anthropic Messages API payload from a `PromptEnvelope` — is a **prompt-assembly** step, not a retrieval step. The "RAG" in its historical name referred to Retrieval-Augmented Generation as a style, not to an actual retrieval call.

### Negative / risks
- **Scanner tooling**: any tooling that had hardcoded `apps_rg` in an R3 list must be updated. The spine coverage scanner reads `spine_manifest.yaml` dynamically, so it self-corrects. Custom scripts that hard-mapped the route family must update their own state.
- **Historical notes**: ADRs or runbooks predating this decision that mention `R3_grounded_read` for `apps_rg` are now stale. They should be updated on their next revision cycle; they do not need immediate correction.

---

## Alternatives Considered

### Keep R3_grounded_read with a note
Rejected. A manifest that claims a contract the code does not fulfill is a governance lie. No amount of prose can make a fiction true.

### Promote to R3R4_managed_workflow
Rejected. `apps_rg` has no `CommitRequest`, no `StateDiffCandidate`, and no per-request durable state write. The managed-workflow shape is reserved for apps that write structured state changes through UWG after L2 execution. `apps_rg` writes local output artifacts only — these are classified as local artifact persistence, not L4 durable state (same classification as `apps_research`, `apps_exec`, `apps_lic`, `apps_rfp`).

### Add C0 corpus retrieval to justify R3
Rejected. apps_rg's résumé generation quality does not require a retrieval corpus. Adding retrieval to justify a historical mislabeling would be engineering theater with real latency cost.

---

## References

- `apps_rg/spine_manifest.yaml` — corrected route claim
- `apps_rg/config/apps_rg_static_dag.yaml` — static DAG with `route_family: R4_SINGLE_ACTION`
- `apps_rg/integrations/preloaded_input_context_manifest.py` — context manifest (c0_bypass)
- `tests/governance/test_apps_rg_c0_bypass_manifest.py` — test 1 (`test_apps_rg_c0_bypass_declared_in_static_dag`)
- `tests/governance/test_apps_rg_static_dag.py` — test 2 (`test_apps_rg_static_dag_declares_r4_single_action`)
- `docs/reference/APP_OVERLAY_VS_CORE_ONLY_RUNTIME.md` — Route-Shape Taxonomy
- Plan: `.windsurf/plans/apps-rg-canonical-wireup-c8a4f2.md` W3 P5 + W4 P9
