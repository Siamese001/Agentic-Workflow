# Final resume aggregation product closeout — W11–W13

**STATUS: PARTIAL**

Headline is now **X3_ALLOW** on the product-proof rollup pin. **ibm_bullets** remains **X3_REVIEW_JUDGE_SOFT_FAIL** (anthropic_claude soft-fail). Cross-section WARN gates still block `product_allow_claimed`.

## W11 — Blocker RCA

| Lane | Pinned run | X3 | Primary blocker | RCA class |
|------|------------|-----|-----------------|-----------|
| headline (prior pin) | `headline_20260518_225908` | X3_REVIEW_JUDGE_SOFT_FAIL | anthropic_claude score 3.2 | judge_soft_fail, unsupported_claim |
| headline (rollup pin) | `headline_20260518_233603` | **X3_ALLOW** | — | Existing ALLOW run; claim_ledger uses `fact_engineering_*` ids |
| ibm_bullets | `ibm_bullets_20260518_224815` | X3_REVIEW_JUDGE_SOFT_FAIL | anthropic_claude score 2.8 | judge_soft_fail, proof_pool_mismatch (null allowed_fact_packet) |

Artifacts:
- [headline_blocker_rca.json](../../artifacts/apps_rg/runtime_proofs/final_resume_assembly/headline_blocker_rca.json)
- [ibm_bullets_blocker_rca.json](../../artifacts/apps_rg/runtime_proofs/final_resume_assembly/ibm_bullets_blocker_rca.json)

**ibm_bullets root cause:** Judge packet had `allowed_fact_packet: null` while using base-resume proof pool; Anthropic flagged circular ledger / unverifiable metrics. **Code fix:** `build_ibm_bullets_allowed_fact_packet()` passed into `run_ibm_bullets_judges` ([ibm_bullets_lane.py](../../apps_rg/runtime/sections/ibm_bullets_lane.py)).

**W12 regen attempts:** New REAL_LLM runs did not beat pinned scores (`headline_20260518_233957` REVIEW; `ibm_bullets_20260518_233826` X3_BLOCK). Rollup kept best product-proof pins.

## W12 — Regeneration

| Run | REAL_LLM | X3 | Rollup selected |
|-----|----------|-----|-----------------|
| `headline_20260518_233957` | yes | X3_REVIEW_JUDGE_SOFT_FAIL | no |
| `headline_20260518_233603` | yes | **X3_ALLOW** | **yes** |
| `ibm_bullets_20260518_233826` | yes | X3_BLOCK | no |
| `ibm_bullets_20260518_224815` | yes | X3_REVIEW_JUDGE_SOFT_FAIL | **yes** |

[regenerated_lane_matrix_w11_w13.json](../../artifacts/apps_rg/runtime_proofs/final_resume_assembly/regenerated_lane_matrix_w11_w13.json)

## W13 — Product aggregation proof

| Check | Result |
|-------|--------|
| Rollup `--product-proof` | headline ALLOW; 6/7 lanes ALLOW |
| Review lanes | **ibm_bullets only** (no mock/plumbing) |
| Structural X2 | PASS |
| Cross-section product | **FAIL** (WARN: duplicates, wording, x3_review_present) |
| Package X3 | `X3_REVIEW_SECTION_JUDGE_STATUS`, `deterministic_blocked=false` |
| `product_allow_claimed` | **false** |

## Residual blockers for PASS

1. **ibm_bullets:** All three model-backed judges must pass (anthropic currently soft-fails on factual_support).
2. **Cross-section:** Clear WARN on `x2_cross_section_exact_duplicate` / `x3_review_present` or document explicit product policy exception (WARN ≠ PASS).

## Non-claims

- Product ALLOW not claimed.
- No OFFLINE_CONTRACT_STUB in rollup pin.
- No mock judges in rollup pin.
- JD/briefing not proof.
