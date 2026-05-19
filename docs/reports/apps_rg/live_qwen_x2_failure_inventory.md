# Live Qwen X2 failure inventory (Wave 1)

**Source:** `apps_rg_live_section_proof_results.json` + artifact bundle inspection.

## Summary

| Class | Sections affected |
|-------|-----------------|
| Deterministic X2 format | headline, unify_bullets, ibm_bullets, ibm_narrative |
| Deterministic X2 support | competencies, unify_bullets, ibm_narrative |
| Dependency (upstream bullets) | unify_narrative |
| Judge-only | executive_summary (X2 PASS) |

## Root-cause highlights

### Headline
- **Gate:** `x2_headline_word_count_10_to_13` (observed 9 words).
- **Cause:** Model under-filled word budget; LLM retry did not recover.
- **Fix:** Deterministic one-token expand in `headline_lane` (segments 2–4 only).

### Competencies
- **Gates:** structured term / canonical / primary fact.
- **Cause:** Typo `fact_g_overnance_003` not in allow-list.
- **Fix:** `repair_fact_id_against_allowlist` fingerprint repair + PA exact-ID instruction.

### Unify narrative
- **Gates:** one sentence, source supported, unify scope.
- **Cause:** `companion_unify_bullets_status` ≠ `ACCEPTED_FINALIZED`; empty `narrative_sentence`.
- **Fix:** Unblock by fixing unify bullets + proof pool (≥6 base-resume `bul_unify_*` facts).

### Unify bullets
- **Gates:** protected metrics, claim_ledger coverage, metrics preserved.
- **Cause:** Ledger company-hint returned only **2** `fact_*` rows; model used `bul_unify_*` ids with `fact_*` ledger roots.
- **Fix:** Reject hint slices `<6` facts → base resume fallback; sync claim_ledger; protected-bullet repair.

## Machine-readable matrix

`live_qwen_x2_failure_inventory.json`
