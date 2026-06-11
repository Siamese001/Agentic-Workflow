---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\apps-rg-c0-sparse-exact-core-boundary-gap-plan.md'
original_relative_path: '_archive\\2026-05\\apps-rg-c0-sparse-exact-core-boundary-gap-plan.md'
source_sha256: 1c7bde85804f9264c4ffe0921b1c2306337c3613715dad655fce7c83a5fe2c5b
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_rg C0 Phase 2 — sparse/exact: core boundary gap plan

**Slug:** `apps-rg-c0-sparse-exact-core-boundary-gap-plan`  
**Status:** Closed — W1–W4 implemented per Decision B (W5/W6 optional follow-ups)  
**Analysis artifact:** `artifacts/apps_rg/c0_embedding_gap/apps_rg_c0_sparse_exact_core_boundary_gap_analysis.md`  
**Phase 2 parent:** `.cursor/plans/apps-rg-c0-sparse-exact-phase2-d2f8a1.md` (Status: **Completed**)

## Decision (locked for implementation)

**B — Narrow generic `agentic_core` sparse/exact seam required, then apps_rg config enables it.**

Rationale summary:

- AG-4 `FinalEvidenceContract` / `EvidenceItem` already support `sparse_search_refs`, `bm25_score`, and `retrieval_method` (`agentic_core/runtime/contracts/final_evidence_contract.py`).
- Generic BM25 sidecar + hybrid fusion exist (`bm25_store.py`, `hybrid_search_engine.py`) but are **not** wired into `c0_retrieve_apps_rg`.
- apps_rg **bypasses** L0 `c0_retrieval` dispatcher today; dense Chroma lives in `apps_rg/runtime/bindings/c0_binding.py` — Phase 2 must **not** grow a permanent private BM25 engine under `apps_rg`; it should call **generic** core capabilities with app-owned profiles.

## Immutable constraints (carry-forward)

- C0 remains **evidence-only**; no direct L4 writes.
- No **apps_rg domain literals** in new `agentic_core` code (IBM/Unify/competencies/JD prose).
- Do not claim PASS for sparse readiness without command output + targeted tests (per Phase 2 plan).
- Prefer **operator** sparse index (FTS/BM25 sidecar or Chroma hybrid) with deterministic merge — choose in W1 design.

## Wave plan (smallest safe scope)

### W1 — Generic seam design (no code or ADR-only)

- Finalize sparse lane IDs, receipt string format for `sparse_search_refs`, merge policy (RRF vs interleaved), per-section caps, dedupe keys (`chunk_digest` / `source_document_id`).
- Resolve open question from Phase 2 plan: Chroma hybrid vs SQLite FTS sidecar vs separate sparse collection — document **one** default for apps_rg first consumer.
- Document mapping between **L0 C0 dispatcher** `FinalEvidenceContract` (`c0_retrieval/final_contract.py`) and **AG-4** FEC to avoid accidental dual implementation (single direction: new work targets AG-4 path used by apps_rg).

**Exit:** Design section appended to analysis artifact or new ADR under `docs/architecture/adr/` when implementation authorized.

### W2 — Generic core sparse/exact interface

- Implement neutral entrypoint: given `(index_handle, query_text, metadata_filter, top_k)` return ranked hits + scores suitable for AG-4 `EvidenceItem` population (`retrieval_method` includes `sparse`, `bm25_score` set).
- Unit tests in `tests/unit/agentic_core/...` — **no** `apps_rg` strings.

**Exit:** Green unit tests; migration receipt if touching `agentic_core` beyond greenfield module.

### W3 — Generic merge / dedupe utility

- Deterministic merge of dense + sparse candidate lists; stable tie-break; optional stratum tags compatible with FEC `evidence_strata`.
- Property tests for ordering stability and dedupe.

**Exit:** Green tests; documented complexity bounds (max items).

### W4 — apps_rg profile enablement

- Extend `section_retrieval_profile.yaml` (and related SSOT) for sparse lane toggles, query templates, caps — **all domain intent stays here**.
- Update `c0_binding.py` to invoke **only** generic core APIs; populate real `sparse_search_refs` when lane executes; retain `NOT_APPLICABLE` sentinel **only** when profile disables sparse or index absent (with explicit `not_applicable_reason` at contract level if required by gates).

**Exit:** Local/runtime proof with seeded sparse index (no mock-as-PASS).

### W5 — Tests, gates, proofs

- Extend `tests/_apps_contract/test_c0_fact_vectors_chroma_runtime.py` or add sibling: when sparse fixture present, assert sparse ref **not** equal to `C0_SPARSE_LANE_NA_REF`.
- Add section-level assertions for Unify/IBM/competencies anchors via sparse+dense merge.
- Run: `pytest tests/_apps_contract/test_c0_fact_vectors_chroma_runtime.py -q`, new sparse tests, `python ops_scripts/ci/run_contract_gates.py` (or minimal subset per gate ownership).

**Exit:** Command log in wave completion note; honest PASS/PARTIAL.

### W6 — No core leakage scan

- `git status --short -- agentic_core`
- `rg -n "ibm|unify|competencies|SMOKE_C0" agentic_core` (tune allowlist for existing shims)
- CI / pre-commit governance as applicable.

**Exit:** Zero unexpected hits; receipt if shims touched.

## Acceptance gates checklist

| Gate | Method |
|------|--------|
| No apps_rg literals added to agentic_core (new code) | `rg` + human review |
| Core generic tests pass if core touched | `pytest tests/unit/agentic_core/...` (scoped) |
| apps_rg IBM/Unify/competency sparse behavior | `tests/_apps_contract/...` with fixture |
| Sparse lane never claims PASS if unavailable | Profile + binding: EMPTY/NA/WARN per exit profile; tests for missing index |
| Dense Phase 1 tests still pass | `pytest tests/_apps_contract/test_c0_fact_vectors_chroma_runtime.py -q` |
| agentic_core working tree reviewed | `git status --short -- agentic_core` |

## References (read-only)

- `apps_rg/runtime/bindings/c0_binding.py`
- `apps_rg/config/domain_contract/section_retrieval_profile.yaml`
- `apps_rg/config/domain_contract/metadata_filter_profile.yaml`
- `apps_rg/config/domain_contract/fact_vectors_schema.yaml`
- `agentic_core/runtime/contracts/final_evidence_contract.py`
- `agentic_core/L0_routing/c0_retrieval/dispatcher.py`
- `agentic_core/L3_orchestration/reasoning/engines/hybrid_search_engine.py`
- `agentic_core/L4_state/utils/memory/bm25_store.py`
