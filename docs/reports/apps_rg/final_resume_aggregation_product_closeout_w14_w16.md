# Final resume aggregation product closeout W14–W16

**Status:** PARTIAL  
**Evaluated:** 2026-05-19T09:10:10Z

## W14 — IBM bullets RCA

Pin [`ibm_bullets_20260518_224815`](artifacts/apps_rg/runtime_proofs/ibm_bullets/real/ibm_bullets_20260518_224815): REAL_LLM, X2 pass, **X3_REVIEW** (anthropic soft-fail 2.8).

| Cause class | Evidence |
|-------------|----------|
| Null `allowed_fact_packet` in judge packet | [`ibm_bullets_judge_packet.json`](artifacts/apps_rg/runtime_proofs/ibm_bullets/real/ibm_bullets_20260518_224815/ibm_bullets_judge_packet.json) |
| Circular claim ledger (bul_ibm_* self-ref only) | [`claim_ledger.json`](artifacts/apps_rg/runtime_proofs/ibm_bullets/real/ibm_bullets_20260518_224815/claim_ledger.json) |
| Renewal-rate vocabulary advisory | [`x1d_llm_judge_outputs.json`](artifacts/apps_rg/runtime_proofs/ibm_bullets/real/ibm_bullets_20260518_224815/x1d_llm_judge_outputs.json) |

Failed regen [`ibm_bullets_20260518_233826`](artifacts/apps_rg/runtime_proofs/ibm_bullets/real/ibm_bullets_20260518_233826): broad skills ledger pool → wrong `fact_*` scope, lost locked IBM metrics, **X3_BLOCK**.

Full RCA: [`ibm_bullets_blocker_rca_w14.json`](artifacts/apps_rg/runtime_proofs/final_resume_assembly/ibm_bullets_blocker_rca_w14.json)

## W15 — Repair

**Code** ([`ibm_bullets_lane.py`](apps_rg/runtime/sections/ibm_bullets_lane.py)):

- Force canonical base-resume IBM employment when ledger pool lacks `bul_ibm_001..005`.
- Always pass non-null `allowed_fact_packet` (canonical facts) to judges.
- Align claim_ledger `source_fact_ids` to canonical bul_ibm_* + metric ids.

**Regeneration:**

1. `ibm_bullets_20260519_090504` — **BLOCKED** (`PROVIDER_UNAVAILABLE`, qwen preflight).
2. Judge replay on pin L2 with fix → **X3_ALLOW** (gemini/openai/anthropic all model-backed pass); promoted onto pin run dir.

## W16 — Product aggregation / package

| Check | Result |
|-------|--------|
| All 7 lanes REAL_LLM + X3_ALLOW (rollup) | Yes |
| Review lanes | 0 |
| Package X3 | **X3_ALLOW** |
| `cross_section_x2_product_pass` | **false** (WARN: exact_duplicate, same_claim_different_wording) |
| `product_allow_claimed` (receipt) | **false** (WARN policy blocks product ALLOW) |

## Remaining blockers for full product ALLOW

- Cross-section WARN gates (not FAIL): 11 exact-duplicate groups, 12 same-fact wording variants.
- Fresh end-to-end qwen REAL_LLM ibm_bullets regen not re-proven (provider down); judge replay on existing L2 only.

## Non-claims

- Did not claim product ALLOW on receipt (`product_allow_claimed=false` due to cross-section WARN).
- Did not use OFFLINE_CONTRACT_STUB or mock judges for proof path.
- No `agentic_core` edits.
