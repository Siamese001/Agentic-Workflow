# Live Qwen X2 quality hardening — 3-wave receipt

**STATUS: PARTIAL**

## Summary

| Metric | Before (baseline) | After (latest REAL_LLM) |
|--------|-------------------|-------------------------|
| X2 deterministic PASS | 1 / 7 | **7 / 7** |
| X3 ALLOW | 0 / 7 | **3 / 7** |
| `proof_eligible` | 0 / 7 | **1 / 7** (competencies) |
| Skills authority (`augmented_skills_graph` PASS) | 7 / 7 | **7 / 7** |

All seven sections ran with `--provider qwen_vllm` and `--allow-non-allow-exit-zero` (artifact inspection only). No X2/X3 gate weakening.

## Latest REAL_LLM artifact dirs

| Section | Run | X2 | X3 |
|---------|-----|----|-----|
| headline | `headline_20260518_225908` | PASS | X3_REVIEW_JUDGE_SOFT_FAIL |
| competencies | `competencies_20260518_225908` | PASS | X3_ALLOW (`proof_eligible`) |
| unify_bullets | `unify_bullets_20260518_230943` | PASS | X3_ALLOW |
| unify_narrative | `unify_narrative_20260518_231059` | PASS | X3_ALLOW |
| ibm_bullets | `ibm_bullets_20260518_224815` | PASS | X3_REVIEW_JUDGE_SOFT_FAIL |
| ibm_narrative | `ibm_narrative_20260518_225555` | PASS | X3_ALLOW |
| executive_summary | `exec_summary_20260518_230421` | PASS | X3_REVIEW_MOCKED_PLUMBING_ONLY (PQ PARTIAL) |

Base: `artifacts/apps_rg/runtime_proofs/<section>/real/<run_id>/`.

## Key patches (apps_rg only)

- Proof pool: SRFS under-allocation → ledger company-hint; `_stamp_unify_canonical_bullet_ids` for `bul_unify_*` + candidate ledger.
- Lanes: headline word expand; competencies typo/stuffing repair; unify claim-ledger sync + protected metrics; IBM narrative theme coverage split.
- Shared: `fact_id_typo_repair.py`.

Wave 1 inventory: `live_qwen_x2_failure_inventory.md` / `.json`  
Wave 2 slice: `live_qwen_x2_wave2_headline_unify_competencies.md` / `.json`  
Machine receipt: `live_qwen_x2_quality_hardening_results.json`
