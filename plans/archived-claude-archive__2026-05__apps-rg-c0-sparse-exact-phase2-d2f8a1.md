---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-rg-c0-sparse-exact-phase2-d2f8a1.md'
original_relative_path: '_archive\\2026-05\\apps-rg-c0-sparse-exact-phase2-d2f8a1.md'
source_sha256: 81298d61174eae2808cdcd52d206bf4d9bac527b95a16bd43b6c825c0bd5291c
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_rg C0 Phase 2 — sparse / exact retrieval hardening

**Slug:** `apps-rg-c0-sparse-exact-phase2-d2f8a1`  
**Status:** Completed  
**Notion Plans page ID:** `36127693-f55c-81c0-b56f-d455590ee9be`  
**Supersedes / relates:** Dense `fact_vectors` C0 lane is **closed** under `apps-rg-fact-vectors-c0-notion-d4e8c2` — this plan is **only** Phase 2 expansion.

## Immutable constraints

- Do **not** edit `agentic_core` unless explicitly authorized for generic spine work.
- Keep app-specific retrieval policy, profiles, manifests, and tests in `apps_*` (primarily `apps_rg`).
- Do not weaken existing dense-lane gates or readiness semantics; Phase 2 **adds** lanes or policies alongside dense, with explicit merge rules.
- Do not claim PASS for Phase 2 without command output, targeted tests, and (where applicable) persisted-store proof.

## Objective

Extend C0 evidence retrieval beyond the **dense BGE-M3 `fact_vectors`** lane with a controlled **sparse / exact-match** surface (e.g. BM25 or keyword/exact index), define **dense + sparse merge** (ordering, dedupe, caps), surface **sparse refs** in FEC or companion maps where the contract allows, and strengthen **receipts / metrics** for retrieval quality — without conflating this work with the closed dense readiness plan.

## Non-goals (explicit)

- Re-litigating dense ingest, `SEED-RG-FV`, or CHECK-RG-FACT-VECTORS behavior (see closed plan on disk).
- Replacing Chroma dense with sparse-only unless ADR-level decision.
- Broad `agentic_core` FEC schema changes without governance receipt.

## Wave structure

| Wave | Focus | Status / exit |
|------|--------|----------------|
| **W1** | Requirements + contracts | **Done** — Decision B + gap plan (`apps-rg-c0-sparse-exact-core-boundary-gap-plan.md`); generic seam contract locked. |
| **W2** | Index + ingest path | **Done** — `get_sparse_index` / `sparse_sidecar_exists` profile-driven; BM25 sidecar resolution; core unit tests. |
| **W3** | Binding merge | **Done** — `c0_binding` optional sparse lane + RRF merge; 5-tuple bounded retrieval; `sparse_search_refs` populated when enabled. |
| **W4** | FEC / receipts | **Done** — sparse receipts on lane; `section_retrieval_profile.yaml` per-section toggles; contract tests (`test_c0_sparse_exact_apps_rg_wiring`, `test_w4_bounded_section_retrieval`). |
| **W5** | Gates + CI | **Future** — optional fail-closed sparse readiness gate / extended `test_c0_fact_vectors_chroma_runtime` when sparse fixture is standard in CI. |

### Completion record (disk SSOT)

- **Completed:** 2026-05-15
- **Notion Plans page:** `36127693-f55c-81c0-b56f-d455590ee9be`
- **Delivered modules (representative):** `agentic_core/knowledge/retrieval/c0_sparse_exact_seam.py`; `bm25_store.py` sparse index helpers; `apps_rg/runtime/bindings/c0_binding.py`; `apps_rg/config/domain_contract/section_retrieval_profile.yaml`; unit + `_apps_contract` tests as listed in wave table.

## Follow-ups (optional / W5)

- CI fail-closed sparse readiness or extended chroma-runtime assertions when sparse sidecar is a standard fixture.
- Broader metadata-filter parity across lanes if new sections enable sparse.

## Evidence discipline

Each wave closes with: exact commands, test/gate names, artifact paths, and honest PASS / PARTIAL / FAIL.

## References

- Closed dense plan: `.cursor/plans/apps-rg-fact-vectors-c0-notion-d4e8c2.md`
- C0 binding (read-only for design): `apps_rg/runtime/bindings/c0_binding.py`
- Section / metadata profiles: `apps_rg/config/domain_contract/`
