# Executive summary C0.3 binding hot path

**Plan:** `c03-skills-graph-exec-summary-f9a2c4` · **DG-1:** A (pool-wins)

## Flow

1. `resolve_section_proof_pool(executive_summary)` — SRFS arsenal → `allowed_fact_ids`
2. `build_track_weighted_expansion` + `build_section_c03_graphrag_bound(attach_sqlite=True)`
3. `filter_c03_evidence_to_allowed_pool` — strip claimable FEC items outside pool
4. `build_graph_targeting_capsule` — non-proof PA theming (max 8 skills × 120 chars)
5. `enrich_proof_pool_with_native_c03` — receipt parity; `canonical_c0_3_claimed=false`
6. Pre-L2 `assert_pre_l2_allowlist_coherence` — block provider if claimable ⊄ pool
7. PA: `GRAPH_TARGETING_CAPSULE` + proof facts only from `allowed_fact_ids`

## Artifacts

- `c03_graphrag_bound.json`
- `graph_targeting_capsule.json`
- `allowlist_coherence_receipt.json`
- `native_c03_final_evidence.json` (when route/ACL emit)

## Competencies contrast

Competencies uses graph-skills proof pool wave P2-W1A; executive_summary uses graph-only binding + pool-wins allowlist (no promotion unless DG-1=B).
