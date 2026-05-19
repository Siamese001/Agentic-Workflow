# Final resume aggregation product closeout W17–W19

**Status:** BLOCKED (W17 qwen_vLLM); W18–W19 product pipeline **PASS** on pinned IBM + overlap resolution

**Evaluated:** 2026-05-19

## W17 — Fresh IBM bullets (BLOCKED)

| Check | Result |
|-------|--------|
| `curl -fsS http://localhost:8000/v1/models` | **exit 7** — connection refused |
| Fresh `ibm_bullets` generation | **BLOCKED** (`ibm_bullets_20260519_090504`) |

**Accepted pin (explicit reason):** [`ibm_bullets_20260518_224815`](artifacts/apps_rg/runtime_proofs/ibm_bullets/real/ibm_bullets_20260518_224815) — REAL_LLM, X3_ALLOW, x2_failed=0, non-null `allowed_fact_packet`, model-backed judges pass (W15 replay on pin L2).

Proof: [fresh_ibm_bullets_proof_w17.json](artifacts/apps_rg/runtime_proofs/final_resume_assembly/fresh_ibm_bullets_proof_w17.json), [qwen_healthcheck_w17.json](artifacts/apps_rg/runtime_proofs/final_resume_assembly/qwen_healthcheck_w17.json)

## W18 — Cross-section WARN burn-down (PASS)

Overlap gates now **PASS** when duplicates are dispositioned in the overlap ledger with `provenance_retained` (L2 snapshots unchanged):

- `x2_cross_section_exact_duplicate` → PASS (11 groups dispositioned)
- `x2_cross_section_same_claim_different_wording` → PASS (12 variants dispositioned)

Code: [`cross_section_x2.py`](apps_rg/runtime/aggregation/cross_section_x2.py) — `_overlap_class_fully_dispositioned`

Artifacts: [kept_removed_claims.json](artifacts/apps_rg/runtime_proofs/final_resume_assembly/kept_removed_claims.json), [overlap_decisions.json](artifacts/apps_rg/runtime_proofs/final_resume_assembly/overlap_decisions.json), [cross_section_warn_resolution_w18.json](artifacts/apps_rg/runtime_proofs/final_resume_assembly/cross_section_warn_resolution_w18.json)

No product WARN waiver used (`product_warn_waiver_used: false`).

## W19 — Final product package (PASS)

| Check | Result |
|-------|--------|
| 7/7 lanes REAL_LLM + X3_ALLOW | Yes |
| REVIEW / mock lanes | 0 |
| `cross_section_x2_product_pass` | **true** |
| Package X3 | **X3_ALLOW** |
| `final_resume_receipt.product_allow_claimed` | **true** |
| `resume_package` aggregation proof | **product_allow_claimed: true** |

## Non-claims

- Did not execute a **fresh** end-to-end qwen L2 ibm_bullets run (provider down).
- Pin IBM proof uses prior REAL_LLM L2 + W15 judge replay, not a new generation pass.
- No OFFLINE_CONTRACT_STUB; no mock judges on proof path.
