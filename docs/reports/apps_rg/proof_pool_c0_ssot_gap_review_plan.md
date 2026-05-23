# apps_rg proof pool / C0 SSOT — gap review (for human review)

**Plan SSOT:** [.cursor/plans/apps-rg-proof-pool-c0-ssot-a7f3e2.md](../../.cursor/plans/apps-rg-proof-pool-c0-ssot-a7f3e2.md)  
**Audit JSON:** [proof_pool_c0_ssot_gap_audit.json](../../artifacts/apps_rg/plans/proof_pool_c0_ssot_gap_audit.json)  
**Generated:** 2026-05-23  
**Track B completion (modular W23 sweep):** incorporated in [proof_pool_c0_ssot_gap_audit.json](../../artifacts/apps_rg/plans/proof_pool_c0_ssot_gap_audit.json) → `rca_remediation_completion`

---

## Executive summary

Legacy proof-pool **authority** (SRFS-as-proof, broad skills ledger, base-resume fallback) is **retired**. W1 digest chain is populated on fresh modular runs (RCA-9 fix). **Track B (2026-05-23)** closed P0 RCA-1/2/4 on live evidence under `artifacts/apps_rg/plans/w23_lane_sweep/modular_lanes/`; **RCA-3** lifted competencies to `x2_all_pass`. **`all_lanes_proof_ok` remains false** — narratives, headline X2, and judge/X3 layers still block release.

**Executive summary (prior RCA):** modular sweep shows `x2_all_pass` + `lane_proof_ok` + `X3_REVIEW_JUDGE_SOFT_FAIL` — same synthesis-quality gap as Brown & Brown runs; **not** fixed by unify/IBM modular fixes.

---

## Track B — RCA remediation completion (2026-05-23)

| RCA | Fix | Proven |
|-----|-----|--------|
| **RCA-1** | `repair_unify_bullet_surface_id()` (`bul_unify_.003` → `bul_unify_003`) | [unify_bullets_20260523_125754](artifacts/apps_rg/plans/w23_lane_sweep/modular_lanes/unify_bullets/real/unify_bullets_20260523_125754) — `product_quality_status: PASS` |
| **RCA-2** | Modular sweep env + upstream-first order | [companion ACCEPTED_FINALIZED](artifacts/apps_rg/plans/w23_lane_sweep/modular_lanes/unify_narrative/real/unify_narrative_20260523_125925/companion_unify_bullets_context.json) |
| **RCA-3** | Competencies expand **after** final dedupe | competencies `x2_all_pass` (X3 still BLOCK) |
| **RCA-4** | `inject_ibm_locked_metric_anchors()` + scrub | [ibm_bullets_20260523_131013](artifacts/apps_rg/plans/w23_lane_sweep/modular_lanes/ibm_bullets/real/ibm_bullets_20260523_131013) — product PASS |

**Modular lane summary (audit):**

| Lane | x2_all_pass | lane_proof_ok | x3 |
|------|-------------|---------------|-----|
| executive_summary | true | true | X3_REVIEW_JUDGE_SOFT_FAIL |
| headline | false | false | X3_BLOCK |
| competencies | true | true | X3_BLOCK |
| unify_bullets | true | true | X3_REVIEW_JUDGE_SOFT_FAIL |
| unify_narrative | false | false | X3_BLOCK |
| ibm_bullets | true | true | X3_BLOCK |
| ibm_narrative | false | false | X3_BLOCK |

**STATUS:** PARTIAL — P0 fixes proven; `release_eligible_proof_claimed: false`.

---

## Executive summary (historical pre–Track B)

Legacy proof-pool **authority** (SRFS-as-proof, broad skills ledger, base-resume fallback) is **retired**. The remaining problem is **split SSOT**: the C0 evidence room FEC often advertises **more (or different) fact IDs** than the resolver pool that PA, L2, and X2 enforce.

**6 of 6** comparable latest real runs show `allowlist_mismatch=true`. **unify_narrative** is the worst case: pool and FEC share **zero** IDs.

---

## Cross-lane audit table

| Lane | Pool count | FEC count | FEC-only examples | Pool-only examples |
|------|------------|-----------|-------------------|-------------------|
| executive_summary | 7 | 9 | fact_solutions_002, fact_revenue_ops_001 | — |
| headline | 3 | 7 | fact_consulting_001, fact_engineering_platform_002, … | — |
| competencies | 17 | 18 | fact_solutions_002 | — |
| unify_narrative | 7 | 2 | fact_revenue_ops_001, fact_solutions_002 | bul_unify_001…006, unify_narrative_base_001 |
| ibm_bullets | 6 | 7 | fact_solutions_002 | — |
| ibm_narrative | 3 | 5 | fact_revenue_ops_001, fact_solutions_002 | — |
| unify_bullets | — | — | (incomplete proof dir) | — |

---

## Additional gaps (beyond allowlist)

1. **Dual C0.2 hybrid** — reorder at resolver + hybrid in evidence room.  
2. **Receipt schizophrenia** — `c0_fec_bridge_receipt` vs `c0_evidence_room_receipt.bridge_doc` disagree on canonical C0 flags.  
3. **C0.3 claim semantics** — graph BOUND vs `canonical_c0_3_claimed=false`.  
4. **Spine index** — `section_runtime_proof_bundle` missing FEC in chain.  
5. **ibm_bullets** — X2 active proof pool gate **FAIL** on latest run.  
6. **Governance** — retired `x2_exec_summary_sentence_count_2_3` still in `lane_registry`.  
7. **Section parity** — `native_c03` enrich only on competencies.  
8. **Ops** — Chroma `fact_vectors` vs `process_docs` readiness split.

---

## Recommended fix order

1. **W0** — Author-Gate: pool-wins vs FEC-widens-pool.  
2. **W1** — Implement allowlist sync + unify_narrative ID policy + ibm_bullets X2.  
3. **W2** — Receipt/spine alignment.  
4. **W3** — Seven-lane live proof + unify_bullets full dir.  
5. **W4** — Registry + vocabulary cleanup.

---

## Commands to reproduce audit

```bash
python ops_scripts/apps_rg/proof_pool_c0_ssot_gap_audit.py
```
