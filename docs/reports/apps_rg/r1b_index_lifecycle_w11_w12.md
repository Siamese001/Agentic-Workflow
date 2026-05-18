# R1B derived index and lifecycle (W11–W12)

## Summary

UWG-admitted R1B durable bundles under `durable/uwg_admitted/` are projected into a **derived read-only** lookup surface at `derived_index/`. Whole-run preflight consults the derived index first (intent vectors only), loads parent record and parent-bound chunks from durable truth on hit, and preserves R1A → R1B → generation order with Exit review on hits.

## Durable truth vs derived index

| Layer | Role | Path |
|-------|------|------|
| UWG-admitted durable projection | Production truth | `durable/uwg_admitted/intents/`, `chunks/<parent>/` |
| Derived index | Read surface only | `derived_index/intent_vectors/`, `by_digest/` |
| Fixture mirror | Test/proof only | `R1BSemanticCacheStore` intents/chunks |
| C0 `fact_vectors` | Excluded from R1B | not used |

## Indexed vs excluded

**Indexed:** `record_id`, `normalized_intent_digest`, `request_intent_vector`, `cache_grain`, `cache_admissible`, profile hashes, `durable_bundle_ref`.

**Excluded:** child chunk vectors, chunk IDs as lookup keys, C0 fact_vectors, fixture mirror as production truth.

## Lifecycle proof

1. Post-Exit eligible run → promotion candidate  
2. Exit-sourced `CommitRequest` → UWG admit  
3. Durable bundle + governance sidecar  
4. `project_durable_to_derived_index()` (also called from `promote_and_project_r1b_cache`)  
5. Future whole-run lookup via `lookup_r1b_via_derived_index` / `execute_whole_run_r1b_preflight`  
6. Hit → terminal packet with `exit_review_required`; miss/reject → generation fallthrough  

## Artifacts

- `artifacts/apps_rg/r1b_semantic_cache/w11_w12_fixtures/` — projection, refresh, lifecycle, separation proofs  
- Manifest: `docs/reports/apps_rg/r1b_index_lifecycle_w11_w12_manifest.json`

## Non-claims

- File-backed fixtures are not durable production truth.  
- Core `UWGCommitReceipt` parity is **not** solved (W10b gap carried forward).  
- Chroma/vector DB is not wired as production index; derived index is file-backed projection.  
- No section-level loose R1B lookup.
