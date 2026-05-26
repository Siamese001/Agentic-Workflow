# C03 exec-summary gaps v2 — W1 closeout

**Plan:** [c03-exec-summary-gaps-v2-a8f2e1](../../.cursor/plans/c03-exec-summary-gaps-v2-a8f2e1.md)  
**Wave:** W1 (fact utilization + brushstroke skill refs)  
**Policy:** `fact_certs_*` waived by default (aligns with `no_credential_dump` + B4 display optional)

```text
STATUS: PASS
FILES_CHANGED:
- [executive_summary_x2.py](../../apps_rg/runtime/validators/executive_summary_x2.py)
- [section_product_shape_ssot.py](../../apps_rg/runtime/sections/section_product_shape_ssot.py)
- [c03_allowlist_coherence.py](../../apps_rg/runtime/c0/c03_allowlist_coherence.py)
- [executive_summary_composition.py](../../apps_rg/runtime/sections/executive_summary_composition.py)
- [executive_summary_generation_grade_contract.py](../../apps_rg/runtime/sections/executive_summary_generation_grade_contract.py)
- [executive_summary_lane.py](../../apps_rg/runtime/sections/executive_summary_lane.py)
- [test_executive_summary_allowed_fact_utilization.py](../../tests/unit/apps_rg/test_executive_summary_allowed_fact_utilization.py)
COMMANDS_RUN:
- pytest tests/unit/apps_rg/test_executive_summary_allowed_fact_utilization.py tests/unit/apps_rg/test_section_c03_graph_binding_classification.py tests/_apps_contract/test_exec_summary_c03_allowlist_coherence.py -q -o addopts= -> 16 passed
TESTS_GATES:
- W1 unit + contract slice -> 16 passed
ARTIFACTS: NONE (runtime proof deferred to W5)
REPORTS_GENERATED:
- [c03_exec_summary_gaps_v2_w1_closeout_20260526.md](c03_exec_summary_gaps_v2_w1_closeout_20260526.md)
NOTES:
- New X2 gate x2_exec_summary_allowed_fact_utilization; override via APPS_RG_EXEC_SUMMARY_UTILIZATION_WAIVE_FACT_IDS.
- Brown baseline exec_summary_20260526_211453 would PASS utilization (fact_certs_001 waived).
```

## W1.1 — Allowed-fact utilization X2

- `check_exec_summary_allowed_fact_utilization` — non-waived `allowed_fact_ids` must appear in `claim_ledger` and/or `text_claim_coverage`.
- Default waivers: `fact_certs_*` via `resolve_utilization_waived_fact_ids`.
- Gate id: `x2_exec_summary_allowed_fact_utilization` registered in product shape SSOT.
- Receipt on `parsed_output.allowed_fact_utilization_receipt` and `section_metric_receipt.json`.

## W1.2 — Brushstroke skill refs

- `_brushstroke_for_role` receives `proof_pool_metadata`.
- `_skill_ids_for_facts_from_track_expansion` scopes skills to facts in brushstroke role (not full `c03_selected_skill_ids` dump).

## W1.3 — Cert policy alignment

- `build_exec_summary_allowlist_receipt` emits `waived_fact_ids` + `utilization_policy`.
- Generation law digest documents pool utilization + cert waiver.

## Author-Gate

Deferred: plan policy **waive `fact_certs_*` by default** matches existing `_filter_required_display_fact_ids` and `no_credential_dump` — no surface-FSA mandate added.

**Next:** W2 — `support_target_met` + graph digest SSOT.
