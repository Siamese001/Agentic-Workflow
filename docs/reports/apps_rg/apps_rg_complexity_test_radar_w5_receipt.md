# apps_rg Complexity Test Radar — W5 Closeout Receipt

```text
STATUS: PASS
PLAN_ID: apps-rg-complexity-test-radar-605dcc
WAVE_ID: W5
WAVE_TITLE: CI + closeout
SCOPE_MATCH: yes — W1–W5 delivered per plan scope (contract/static proof only)
SCOPE_DRIFT: none
FILES_CHANGED:
- (includes all W1–W4 files listed in W1 receipt plus W2–W4 test modules below)
- tests/unit/apps_rg/test_executive_summary_repair_stack_order.py
- tests/unit/apps_rg/test_executive_summary_evidence_capsule_authority.py
- tests/unit/apps_rg/test_competencies_rigor_constants_derived_from_ssot.py
- tests/unit/apps_rg/test_headline_format_repair_single_regen_cap.py
- tests/unit/apps_rg/test_headline_fact_id_resolution_vs_shared_typo_repair.py
- tests/unit/apps_rg/section_rigor/lanes/test_ibm_narrative_runtime_execution_seam.py
- tests/unit/apps_rg/runtime/spine/test_section_cli_runners_dispatch_matrix.py
- tests/_apps_contract/test_apps_rg_proof_pool_forbidden_authority.py
- tests/_apps_contract/test_final_resume_aggregation_negatives.py
COMMANDS_RUN:
- python -m pytest tests/unit/apps_rg/section_rigor/test_rigor_runtime_x2_emission_parity.py tests/unit/apps_rg/section_rigor/test_parallel_dispatch_quality_paths.py tests/unit/apps_rg/section_rigor/test_section_complexity_budget.py -q -p pytest_timeout -> exit 0
- python -m pytest tests/unit/apps_rg/test_executive_summary_repair_stack_order.py tests/unit/apps_rg/test_executive_summary_evidence_capsule_authority.py tests/unit/apps_rg/test_competencies_rigor_constants_derived_from_ssot.py tests/unit/apps_rg/test_headline_format_repair_single_regen_cap.py tests/unit/apps_rg/section_rigor/lanes/test_ibm_narrative_runtime_execution_seam.py tests/unit/apps_rg/runtime/spine/test_section_cli_runners_dispatch_matrix.py tests/_apps_contract/test_apps_rg_proof_pool_forbidden_authority.py tests/_apps_contract/test_final_resume_aggregation_negatives.py -q -p pytest_timeout -> exit 0 (34 passed, 1 skipped)
- python ops_scripts/ci/check_apps_rg_complexity_baseline.py -> exit 0
- python ops_scripts/apps_rg/section_complexity_reduction_audit.py -> exit 0
- python ops_scripts/ci/run_contract_gates.py -> not run (full CI suite deferred)
TESTS_GATES:
- New radar tests: PASS (scoped slices)
- check_apps_rg_complexity_baseline.py: PASS
- run_contract_gates.py: not executed this closeout
ARTIFACTS_WRITTEN:
- docs/reports/apps_rg/apps_rg_complexity_test_radar_w1_receipt.md
- docs/reports/apps_rg/apps_rg_complexity_test_radar_w5_receipt.md
- tests/unit/apps_rg/section_rigor/fixtures/complexity_baseline.json
PROOF_CLASSIFICATION: CONTRACT_TEST_PROOF, STATIC_COMPLEXITY_PROOF
FORBIDDEN_FILES_TOUCHED:
- agentic_core: no edits authored by this plan implementation
- ops_scripts/ci/check_apps_rg_complexity_baseline.py: new governance CI script (touches_governance_ci=true)
EXPLICIT_NON_CLAIMS:
- Not LIVE_RUNTIME_PROOF (no python -m apps_rg --section <lane> with real provider artifacts in this pass)
- Full tests/unit/apps_rg/section_rigor/ directory has 8 pre-existing failures in test_section_product_shape_ssot.py (unrelated to this plan)
- run_contract_gates.py not run
NEXT_BLOCKER: none (optional: register check_apps_rg_complexity_baseline.py in run_contract_gates.py; W3.2 unify metric companion tests)
```
