# Executive summary C0.3 binding — hot path & receipt glossary

**Plans:** [c03-exec-summary-gaps-v2-a8f2e1](../../.cursor/plans/c03-exec-summary-gaps-v2-a8f2e1.md) (W0 vocabulary) · archived [c03-skills-graph-exec-summary-f9a2c4](../../.cursor/plans/_archive/2026-05/c03-skills-graph-exec-summary-f9a2c4.md) (W0–W5 implementation) · **DG-1:** A (pool-wins)

**Terminology SSOT (code):** `apps_rg/runtime/section_spine_terminology.py` (`C03_RECEIPT_FIELD_GLOSSARY`, `GRAPH_EXPANSION_MODE_*`)

**Baseline proof run:** [exec_summary_20260526_211453](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_211453)

---

## Layman (what C0.3 means here)

The resume system picks a **small set of proven facts** from a skills-and-facts graph (not from the job description text). The graph also suggests **extra neighbors** for targeting and structure, but only facts in the **allowed pool** may appear as claims in the paragraph. Job description and briefing **steer ranking and wording**; they are **not** proof.

---

## Two binding layers (do not conflate)

| Layer | Artifact | What it is | Claim proof? |
|-------|----------|------------|--------------|
| **Section graph context** | `c03_graphrag_bound.json` | Incident-edge walk on static `master_skills_arsenal_ledger.json` | Only facts also in `allowed_fact_ids` |
| **Native C0.3 contract** | `native_c03_final_evidence.json` | Route/ACL-bound `AppsRgC03FinalEvidenceContract` | Same 7 facts when pool-wins; `binding_classification=FULL_C0_3_GRAPHRAG_BINDING` **label** does not mean spine GraphRAG ran |

| Flag | Expected on section CLI | Meaning |
|------|-------------------------|---------|
| `binding_classification` | `SECTION_GRAPH_CONTEXT_BINDING_NOT_PRODUCT_C0_3` (bound doc) or `FULL_C0_3_GRAPHRAG_BINDING` (native contract) | See table above |
| `canonical_c0_3_claimed` | `false` | No spine canonical C0.3 traverse |
| `core_c03_graph_rag_used` | `false` | No `agentic_core` GraphRAG |
| `is_full_c0_3_graphrag` | `false` on `c03_graphrag_bound.json` | Incident-edge binding only |

---

## Graph expansion honesty (W0)

| Term | Implementation today | Common misread |
|------|----------------------|----------------|
| **`graph_expansion_mode=incident_edge_v1`** | Enumerate `graph_edges` whose source/target touches a selected proof fact node | “GraphRAG retrieved context” |
| **`graph_hop_paths_count`** | Count of `ref:graph:edge:*` refs (incident edges), capped at 64 | “2-hop BFS path count” |
| **`graph_hop_bounds: 2`** (native contract) | ACL **policy maximum** depth | Proof that 2-hop traverse ran |

**Competencies contrast:** competencies lane materializes `graph_hop_path` per skill (stricter). Executive summary W4 (plan) may align hop paths or rename the count field.

---

## End-to-end flow

```mermaid
flowchart LR
  A[augmented_skills_graph] --> B[SRFS 7 facts]
  B --> C[track_weighted_expansion]
  C --> D[c03_graphrag_bound incident_edge]
  D --> E[filter_c03 pool-wins]
  E --> F[graph_targeting_capsule non-proof]
  F --> G[native_c03_final_evidence]
  G --> H[PA + L2]
  H --> I[text_claim_coverage]
```

1. `resolve_section_proof_pool(executive_summary)` — SRFS arsenal → `allowed_fact_ids` (7 on Brown baseline)
2. `build_track_weighted_expansion` + `build_section_c03_graphrag_bound(attach_sqlite=True)`
3. `filter_c03_evidence_to_allowed_pool` — strip claimable FEC items outside pool; stamp `c03_context_fact_ids` / `c03_filtered_out_fact_ids`
4. `build_graph_targeting_capsule` — non-proof PA theming (max 8 skills × 120 chars)
5. `enrich_proof_pool_with_native_c03` — `native_c03_final_evidence.json`; `canonical_c0_3_claimed=false`
6. Pre-L2 `assert_pre_l2_allowlist_coherence` — block provider if claimable ⊄ pool
7. PA: `GRAPH_TARGETING_CAPSULE` + proof facts only from `allowed_fact_ids`
8. Composition: brushstrokes B1–B4 + `graph_skill_refs`

---

## Artifacts (per run dir)

| File | Role |
|------|------|
| `c03_graphrag_bound.json` | Section binding + FEC-shaped snapshot (`fec_shape_only`) |
| `native_c03_final_evidence.json` | Native contract when route/ACL emit |
| `graph_targeting_capsule.json` | JD/GTM skills; `claim_support_allowed: false` |
| `graph_selection_rationale.json` | Track weights, JD boosts; `jd_used_as_proof: false` |
| `section_metric_receipt.json` | `allowed_fact_ids`, filtered/context fact lists, authority digests |
| `c0_graph_lane_receipt.json` | Skill→fact edges for dominant claims |
| `selected_fact_plan.json` / `real_l2_generation_result.json` | Composition + `graph_skill_refs` |
| `text_claim_coverage.json` | Sentence → `source_fact_ids` |
| `allowlist_coherence_receipt.json` | Pool-wins filter receipt (when emitted) |

**Legacy filename:** `c03_graphrag_bound.json` remains for compatibility. Preferred name in terminology SSOT: `section_graph_binding.json`.

---

## Receipt field glossary

Copied from `C03_RECEIPT_FIELD_GLOSSARY` in code (update both when adding fields).

| Field | Plain English |
|-------|----------------|
| `allowed_fact_ids` | Sole claim authority for L2/X2/judges |
| `c03_context_fact_ids` | Graph neighbors kept for context; not claimable |
| `c03_filtered_out_fact_ids` | Neighbors removed from claim pool (pool-wins DG-1=A) |
| `promoted_fact_ids` | Empty under DG-1=A |
| `graph_targeting_skill_ids` | Skills in targeting capsule + expansion metadata |
| `proof_pool_type` | Label `augmented_skills_graph`; not an authority switch |
| `evidence_authority.authority` | `augmented_skills_graph` for product proof |
| `selection_method` | e.g. `augmented_skills_graph_c03_graphrag+hybrid_informed_order_v1` |
| `support_target_met` | `graph_lane_v1`: PASS/SUPPORTED + non-empty allowed pool + evidence items (aligned across c03 bound, c0_metrics, section receipt) |
| `support_target_derivation` | `graph_lane_v1` when using section graph proof pool |
| `graph_digest` | Full graph JSON SHA-256 (`graph_payload_digest` SSOT); matches `evidence_authority.graph_digest` |
| `graph_digest_scope` | On `graph_selection_rationale.json`: `full_graph_payload` |
| `c03_promotion_candidates.json` | Read-only scored list for `c03_filtered_out_fact_ids` (track weight, JD overlap, edge distance); `promotion_eligible=false`, `reason=pool_wins_dg1_a` |
| `graph_hop_paths_by_fact_id` | Track→pillar→skill→fact hop steps per allowed fact (W4); on `c03_graphrag_bound` + `c0_graph_lane_receipt.json` |
| `graph_incident_edge_refs_count` | Incident-edge ref cardinality when no track hop paths materialized |
| `graph_expansion_mode` | `TRACK_WEIGHTED_MULTI_HOP` when hop paths present; else `incident_edge_v1` |
| `allowlist_mismatch` | `false` when FEC claimable ⊆ pool |

---

## Brown baseline (`exec_summary_20260526_211453`)

| Item | Value |
|------|--------|
| `allowed_fact_ids` | 7 (platform, governance, quant, exec, certs) |
| `c03_filtered_out_fact_ids` | 11 (GTM, revenue, partnerships, …) |
| `c03_graphrag_bound_status` | BOUND |
| `graph_expansion_mode` (on bound doc after W0) | `incident_edge_v1` |
| X2 | All PASS |
| X3 | BLOCK (judges: gemini_pro decisive, anthropic_claude soft) |
| Prose vs pool | `fact_certs_001` in pool, not in `text_claim_coverage` (W1) |

---

## Operator guide pointer

Full CLI, regen, and run-summary templates: [executive_summary_operator_guide.md](../../apps_rg/executive_summary_operator_guide.md) § C0.3 skills graph.

---

## Competencies contrast

Competencies uses graph-skills proof pool (P2-W1A) with `graph_hop_path` on skills. Executive summary uses graph-only binding + pool-wins allowlist (no promotion unless DG-1=B).
