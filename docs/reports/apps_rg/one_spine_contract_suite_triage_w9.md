# One-spine contract suite triage (Wave 9)

**STATUS: INCOMPLETE**
full_apps_contract_suite_certified: **False**
exit_code: 1
timed_out: False
log: `docs/reports/apps_rg/one_spine_contract_suite_w9_run.log`

## Failure buckets

### IN_SCOPE_ONE_SPINE (0 samples)
### PRE_EXISTING_OUT_OF_SCOPE (15 samples)
- `FAILED tests/_apps_contract/test_w6_real_embeddings_and_ingestion.py::test_w1_w5_regressions_still_pass[tests/_apps_contract/test_w2_route_contract_graph_policy.py-W2-RouteContract]`
- `FAILED tests/_apps_contract/test_w6_real_embeddings_and_ingestion.py::test_w1_w5_regressions_still_pass[tests/_apps_contract/test_w3_c03_adapter_registry.py-W3-AdapterRegistry]`
- `FAILED tests/_apps_contract/test_w9_judge_eval_harness.py::TestW9JudgeInfrastructure::test_w9_judges_are_not_stub`
- `FAILED tests/_apps_contract/test_w9_judge_eval_harness.py::TestW9JudgeInfrastructure::test_w9_judges_are_calibrated`
- `FAILED tests/_apps_contract/test_w9_judge_eval_harness.py::TestW9JudgeEvaluations::test_w9_claim_support_produces_evidence`
### ENVIRONMENTAL (0 samples)
### UNKNOWN_NEEDS_TRIAGE (15 samples)
- `_ ERROR collecting tests/_apps_contract/test_exec_summary_pa_w4c_guardrails.py _`
- `_ ERROR at setup of TestL0ToRouteBinding.test_route_carries_app_refs[apps_rg-resume_generation] _`
- `_ ERROR at setup of TestL0ToRouteBinding.test_route_carries_app_refs[apps_lic-outreach_message] _`
- `_ ERROR at setup of TestL0ToRouteBinding.test_route_carries_app_refs[apps_eval-eval_self] _`
- `_ ERROR at setup of TestL0ToRouteBinding.test_route_carries_app_refs[apps_exec-brief_assembly] _`