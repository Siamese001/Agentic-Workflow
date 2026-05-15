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

## Wave structure (draft)

| Wave | Focus | Exit criteria (draft) |
|------|--------|------------------------|
| **W1** | Requirements + contracts | ADR or plan-linked retrieval contract: sparse lane IDs, merge policy, caps, failure modes |
| **W2** | Index + ingest path | Deterministic fixture + ingest/tooling for sparse collection(s) or Chroma hybrid config |
| **W3** | Binding merge | `c0_retrieve_apps_rg` (or app-owned helper) merges dense + sparse with stable ordering; tests prove no duplicate explosion |
| **W4** | FEC / receipts | Citation or lineage hooks for sparse hits; optional `dense_search_refs` sibling for sparse; freshness/contradiction rules scoped |
| **W5** | Gates + CI | Readiness or sibling gate for sparse lane; contract tests; optional seed step mirroring dense pattern |

## Open questions (to resolve in W1)

- Chroma native hybrid vs separate collection vs external BM25 store.
- Query text per section for sparse vs dense (same vs specialized).
- Metadata filter parity across lanes.

## Evidence discipline

Each wave closes with: exact commands, test/gate names, artifact paths, and honest PASS / PARTIAL / FAIL.

## References

- Closed dense plan: `.cursor/plans/apps-rg-fact-vectors-c0-notion-d4e8c2.md`
- C0 binding (read-only for design): `apps_rg/runtime/bindings/c0_binding.py`
- Section / metadata profiles: `apps_rg/config/domain_contract/`
