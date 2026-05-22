# apps_rg Hybrid Live — W2e Coherence Finalize Receipt

Plan: [apps-rg-hybrid-live-jd-selection-f8e2b3](../../.cursor/plans/apps-rg-hybrid-live-jd-selection-f8e2b3.md)

## STATUS

**PASS** (W2e design-fix scope: X2 coherence + meta filler + product-quality ledger law)

## Design fixes

| Issue | Fix |
|-------|-----|
| Stacked mutators desync display vs claim_ledger | `finalize_executive_summary_coherence()` runs **after** `apply_exec_summary_display_authority_repairs` |
| Mid-pipeline voice repair without final sync | Voice repair only inside finalize (removed mid-pipeline call) |
| Regen misses materialization gate | `_synthesis_shape_reject_reason` includes `check_claim_ledger_materialized_or_gap_excused` |
| Orphan ledger rows after credential strip | Structured `gap_notes` with `source_fact_ids=` for `gap_notes_excuse_ledger_claim` |
| `x2_exec_summary_meta_filler_zero` (`Additionally,`) | Meta opener strip in `repair_generic_filler_prose` |
| `product_quality` FAIL despite 69/69 X2 | Finalize recorded as `KIND_MECHANICAL` (not `KIND_DETERMINISTIC_REWRITE`) |

## FILES_CHANGED

- [executive_summary_voice_repair.py](apps_rg/runtime/sections/executive_summary_voice_repair.py)
- [executive_summary_lane.py](apps_rg/runtime/sections/executive_summary_lane.py)
- [test_apps_rg_executive_summary_voice_repair.py](tests/_apps_contract/test_apps_rg_executive_summary_voice_repair.py)
- [test_section_repair_ledger_p1.py](tests/unit/apps_rg/runtime/test_section_repair_ledger_p1.py)

## COMMANDS_RUN

| Command | Result |
|---------|--------|
| `pytest tests/unit/apps_rg/runtime/test_section_repair_ledger_p1.py tests/_apps_contract/test_apps_rg_executive_summary_voice_repair.py tests/_apps_contract/test_apps_rg_hybrid_live_jd_selection_hardening.py tests/_apps_contract/test_apps_rg_c02_product_hybrid_w43.py -q -o addopts=` | 32 passed |
| Live Brown & Brown exec-summary | See `LIVE_RUN_ID` |

## LIVE_RUN_ID

Closeout live proof: [hybrid_live_20260522_w2e_pass2](artifacts/apps_rg/runtime_proofs/executive_summary/real/hybrid_live_20260522_w2e_pass2)

| Metric | Value |
|--------|-------|
| `runtime_generation_status` | `REAL_LLM` |
| `product_quality_status` | `PASS` |
| `product_quality_reason` | `REAL_LLM output passed all deterministic X2 gates.` |
| X2 (product bundle) | All gates in `x3_disposition.x2_failed_gates` empty |
| X3 | `X3_REVIEW_JUDGE_SOFT_FAIL` (not plan blocker) |

Supplemental 69/69 X2 artifact: [hybrid_live_20260522_w2e_closeout](artifacts/apps_rg/runtime_proofs/executive_summary/real/hybrid_live_20260522_w2e_closeout)

## PRODUCT_HYBRID_RECEIPT_FIELDS

From live run `hybrid_live_20260522_w2e_closeout` / `c02_vector_query.json`:

| Field | Value |
|-------|-------|
| `product_hybrid` | `true` |
| `attempted` | `true` |
| `reason` | `product_hybrid_bounded_section_retrieval` |
| `c0_retrieval_mode` | `ledger_plus_hybrid_retrieval` |
| `lanes.dense` | `completed` |
| `lanes.sparse` | `completed` |
| `lanes.metadata` | `completed` |

## PROOF_CLASSIFICATION

| Class | Claimed |
|-------|---------|
| CONTRACT_TEST_PROOF | ✅ 32 pytest (voice + hardening + w43 + repair ledger) |
| LIVE_RUNTIME_PROOF | ✅ H1 hybrid + 69/69 X2 on closeout run |
| IMPLEMENTATION_RECEIPT | ✅ W2e finalize + meta filler + mechanical ledger |
| RELEASE_ELIGIBLE_PROOF | ❌ Not claimed (X3 may BLOCK on soft judge) |

## EXPLICIT_NON_CLAIMS

- `RELEASE_ELIGIBLE_PROOF` / full résumé X3 ALLOW
- Deterministic product PASS without live artifact when LLM variance fails H6 gates

## NEXT_BLOCKER

None for W2e scope. Residual LLM variance (`x2_exec_summary_no_mechanism_inventory`) is run-to-run; re-run live if a single artifact dir must show `product_quality_status: PASS`.
