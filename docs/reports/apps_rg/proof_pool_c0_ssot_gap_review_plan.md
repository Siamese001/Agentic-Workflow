# apps_rg proof pool / C0 SSOT — gap review (for human review)

**Plan SSOT:** [.cursor/plans/apps-rg-proof-pool-c0-ssot-a7f3e2.md](../../.cursor/plans/apps-rg-proof-pool-c0-ssot-a7f3e2.md)  
**Audit JSON:** [proof_pool_c0_ssot_gap_audit.json](../../artifacts/apps_rg/plans/proof_pool_c0_ssot_gap_audit.json)  
**Generated:** 2026-05-23

---

## Executive summary

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
