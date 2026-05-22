# apps_rg Hybrid Live — Deferred Scope Receipt (W2d)

Plan: [apps-rg-hybrid-live-jd-selection-f8e2b3](../../.cursor/plans/apps-rg-hybrid-live-jd-selection-f8e2b3.md)

## STATUS

**PASS** — all items from plan `NEXT_BLOCKER` / deferred scope closed on proof run [hybrid_live_20260522_115824](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/hybrid_live_20260522_115824)

## Deferred items

| # | Item | Status | Evidence |
|---|------|--------|----------|
| 1 | `x2_generic_filler_zero` | **PASS** | Voice repair + synthesis shape checks |
| 2 | `x2_no_inferred_bridge_claims` | **PASS** | Strips unsupported `proven track record` |
| 3 | W2B hybrid `source_id` → ledger `fact_id` | **PASS** | `hybrid_informed_order_v1` + `matched_fact_ids` in selected_fact_plan |
| 4 | `graph_pa` pre-PA crash | **FIXED** | Evidence capsule init order |

## FILES_CHANGED

- [executive_summary_voice_repair.py](apps_rg/runtime/sections/executive_summary_voice_repair.py)
- [hybrid_informed_fact_plan_reorder.py](apps_rg/runtime/c0/hybrid_informed_fact_plan_reorder.py)
- [executive_summary_lane.py](apps_rg/runtime/sections/executive_summary_lane.py)
- [executive_summary_evidence_capsule.py](apps_rg/runtime/sections/executive_summary_evidence_capsule.py)
- [executive_summary.generate_scratch_v1.yaml](apps_rg/prompt_assembly/templates/executive_summary.generate_scratch_v1.yaml)
- [test_apps_rg_executive_summary_voice_repair.py](tests/_apps_contract/test_apps_rg_executive_summary_voice_repair.py)
- [test_apps_rg_hybrid_live_jd_selection_hardening.py](tests/_apps_contract/test_apps_rg_hybrid_live_jd_selection_hardening.py)

## COMMANDS_RUN

| Command | Result |
|---------|--------|
| `pytest test_apps_rg_executive_summary_voice_repair.py test_apps_rg_hybrid_live_jd_selection_hardening.py …` | 23 passed |
| Live exec-summary → `hybrid_live_20260522_115824` | REAL_LLM; H6 + deferred X2 PASS |

## PROOF_CLASSIFICATION

| Class | Claimed |
|-------|---------|
| CONTRACT_TEST_PROOF | ✅ |
| LIVE_RUNTIME_PROOF (deferred gates) | ✅ on 115824 artifact dir |
| RELEASE_ELIGIBLE_PROOF | ❌ Not claimed |

## PRODUCT_HYBRID_RECEIPT_FIELDS (reference run)

From [c02_vector_query.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/hybrid_live_20260522_115824/c02_vector_query.json): `ledger_plus_hybrid_retrieval`, all lanes `completed`, `product_hybrid_bounded_section_retrieval`.

## EXPLICIT_NON_CLAIMS

- Full X3 ALLOW / `product_quality_status: PASS` (run exit 1 on auxiliary `x2_claim_ledger_materialized_or_gap_excused` in some runs)
- X1D judge quorum (soft fails may remain)

## NEXT_BLOCKER

None for original deferred scope. Optional: re-run live after `reconcile_claim_ledger_after_voice_repair` overlap matcher for stable `x2_claim_ledger_materialized_or_gap_excused` PASS.
