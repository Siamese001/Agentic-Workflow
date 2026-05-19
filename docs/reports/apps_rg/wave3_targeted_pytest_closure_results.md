# Wave 3 targeted pytest closure results

**STATUS: PARTIAL**

## Outcome

The aborted broad `-k` filter is **replaced** by **14 explicit test files** (~260 tests, ~15m total). **Wave 3 unify contract coverage is green** after aligning three pipeline tests with claim-ledger sync behavior.

| Batch | Passed | Failed |
|-------|--------|--------|
| Tier A (authority + repairs + proof pool + exec unit) | 90 | 1 |
| Tier B unify (runtime + pipeline) | 33 | 0 |
| Tier B IBM (runtime + pipeline) | 29 | 4 |
| Tier C (ibm narrative + exec runtime slice) | 108 | 0 |
| **Total** | **260** | **5** |

## Failures (documented, not live-Qwen regressions)

1. `test_this_summary_and_candidate_fail_meta_gate` — exec summary meta-filler unit expectation (pre-existing drift).
2. Four IBM **mock** pipeline/slice tests — X3 disposition, X2 gate count 32 vs 31, `$15M` mock text, prompt `allowed_fact_ids` shape (ledger vs `bul_ibm_*`).

Live Qwen receipt unchanged: **7/7 X2 PASS**, **3/7 X3 ALLOW**, **1/7 proof_eligible**.

## Contract test updates (Wave 3 align only)

`tests/_apps_contract/test_unify_bullets_section_pipeline.py` — reflects `_sync_unify_claim_ledger_to_bullets` (no runtime/gate weakening).

Machine receipt: `wave3_targeted_pytest_closure_results.json`
