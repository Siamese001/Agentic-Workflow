# apps_lic Canonical Hardening W0 Characterization Receipt

Generated: 2026-06-08

Scope: W0 only for `.claude/plans/apps-lic-canonical-hardening-wireup-4c9d2a.md`. No production code was changed.

## Classification

| Module/function | Current status | Evidence | Required final status |
|---|---|---|---|
| `c0_retrieve_apps_lic` | Live but inline-only | `run_canonical_apps_lic_spine` calls it and `c0_binding.py` documents inline app_payload evidence only | Live governed C0 readiness authority |
| `derive_recipient_class` / `derive_recipient_class_from_store` | Present but not canonical authority | ADG nodes exist for `recipient_classification.py`; PA still reads `lead_profile.seniority_class` from L1 | Live in C0, with U0 seniority as hint only |
| Sender proof packet builder/resolver | Present but not packed by canonical PA | ADG nodes exist for `sender_proof_graph.py`; PA receipts do not carry sender proof packet authority | Live before PA and referenced by proof IDs |
| `run_x2_validation` | Dead from canonical path | Spy characterization shows `run_canonical_apps_lic_spine` does not call `validation_exit.run_x2_validation` | Live after L2 and before required X1D/Exit clearance |
| `run_claude_x1d_judges` | Adapter/test-only for canonical clearance | W7 tests call it directly; canonical dispatch does not invoke it as clearance authority | Live when risk tier requires X1D |
| `exit_finalize_apps_lic` | Live but generic defaults | Canonical dispatch calls it; `_build_exit_review_packet` hardcodes C0 PASS and perfect groundedness/faithfulness/citation precision | Consume apps_lic proof bundle and real C0/X2/X1D evidence |
| `GenerationEngine` SC metadata | Live but not materialized batch | L2 generated content records `candidate_count`/`max_candidates`, not a candidate batch with selected ID | Emit or adapt to externally inspectable candidate batch |
| AIG validation terms | Live globally | `ValidationEngine` requires `_AIG_OPERATING_TERMS` for all messages | Profile-scoped only; non-AIG profiles use generic source-backed gates |

## W0 Tests

Added `tests/apps_lic/test_w0_canonical_hardening_characterization.py`.

The tests are `xfail(strict=True)` because they describe the required hardened behavior while the current branch still demonstrates the unsafe behavior:

- `test_current_inline_c0_named_outreach_should_not_pass_after_hardening`
- `test_current_pa_unknown_class_falls_back_to_recruiter_gap`
- `test_current_canonical_dispatch_does_not_call_app_x2_gap`
- `test_current_exit_hardcodes_c0_pass_gap`
- `test_current_sc3_candidate_count_is_metadata_gap`
- `test_current_global_aig_terms_block_non_aig_gap`

## Holdout Deferral

Locked holdout companies remain:

| Company | JD | Briefing |
|---|---|---|
| AIG | `apps_rg/config/targeting/aig_vp_global_head_agentic_ai_jd.txt` | `apps_rg/config/targeting/aig_vp_global_head_agentic_ai_briefing.md` |
| Citi | `apps_rg/config/targeting/citi_head_of_ai_strategy_jd.txt` | `apps_rg/config/targeting/citi_head_of_ai_strategy_briefing.md` |
| Neo4j | `apps_rg/config/targeting/neo4j_vp_product_management_agentic_ai_jd.txt` | `apps_rg/config/targeting/neo4j_vp_product_management_agentic_ai_briefing.md` |

The 30-contact-per-company validation is intentionally deferred until after W7. Running the benchmark before C0/C0.3/X2/X1D/Exit hardening would measure known unsafe pre-hardening behavior rather than quality-gate readiness.
