# Phase 1 Gap Remediation Execution Evidence

## Scope

Wave 1 (W1.1-W1.5): Gateway SDK bypass removal (openai/anthropic), CI allowlist
  hardening, egress guard test (REQ-414), provider substitution test (REQ-415).
Wave 2 (W2.1-W2.3): uuid4 removal from tracing_mixin + governance_contracts,
  wall-clock CI scanner (REQ-111/REQ-114).
Precondition gap: agentic_core/L5_safety/enforcement/runtime_mutation_guard.py
  not yet created; scheduled for Phase 2 / Wave 4.

## CODE_COMMIT

d6d98db83c6a9c55c9cb82fd2e727e93875bff59

## EVIDENCE_COMMIT

PENDING

## FILES_CHANGED_CODE

agentic_core/L0_routing/enforcement/governance_contracts.py
agentic_core/mixins/tracing_mixin.py
apps_rg/reasoning/HardenedopenaiexecutorStrategy.py
apps_rg/utils/providers_anthropic_client_util.py
ops_scripts/ci/check_llm_sdk_imports.py
ops_scripts/ci/check_wall_clock_in_determinism.py
tests/governance/test_req414_egress_guard.py
tests/governance/test_req415_provider_substitution.py

## FILES_CHANGED_EVIDENCE

PENDING

## INSPECTED_FILES

agentic_core/L0_routing/enforcement/governance_contracts.py
agentic_core/mixins/tracing_mixin.py
apps_rg/reasoning/HardenedopenaiexecutorStrategy.py
apps_rg/utils/providers_anthropic_client_util.py
ops_scripts/ci/check_llm_sdk_imports.py
ops_scripts/ci/check_wall_clock_in_determinism.py
tests/governance/test_req414_egress_guard.py
tests/governance/test_req415_provider_substitution.py
agentic_core/L2_execution/enforcement/SovereignLLMGateway.py
agentic_core/L2_execution/types/gateway_types.py

## PytestGovernanceTests

$ python -m pytest -q --color=no tests/governance/test_req414_egress_guard.py tests/governance/test_req415_provider_substitution.py
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 7 items

tests/governance/test_req414_egress_guard.py::test_gateway_has_egress_audit_log 
-------------------------------- live log call --------------------------------
2026-02-27 11:42:53 [    INFO] agentic_core.agents.agent_registry: Validating compile-time frozen registry sovereignty...
2026-02-27 11:42:53 [    INFO] agentic_core.agents.agent_registry: Registry sovereignty validated: 20 total agents, 16 LLM_API, 4 DETERMINISTIC
PASSED                                                                   [ 14%]
tests/governance/test_req414_egress_guard.py::test_route_generation_writes_egress_audit PASSED [ 28%]
tests/governance/test_req414_egress_guard.py::test_route_generation_egress_payload_contains_agent_id PASSED [ 42%]
tests/governance/test_req415_provider_substitution.py::test_allowlist_excludes_anthropic_util PASSED [ 57%]
tests/governance/test_req415_provider_substitution.py::test_blocked_sdk_import_detected PASSED [ 71%]
tests/governance/test_req415_provider_substitution.py::test_clean_file_passes_sdk_check PASSED [ 85%]
tests/governance/test_req415_provider_substitution.py::test_sovereign_gateway_is_sole_allowed_openai_seam PASSED [100%]

============================ slowest 10 durations =============================
0.03s call     tests/governance/test_req414_egress_guard.py::test_gateway_has_egress_audit_log
0.02s setup    tests/governance/test_req415_provider_substitution.py::test_blocked_sdk_import_detected

(8 durations < 0.005s hidden.  Use -vv to show these durations.)
============================== 7 passed in 0.11s ==============================

## CICheckLLMSdkImports

$ python ops_scripts/ci/check_llm_sdk_imports.py
FAIL: 5 LLM/network SDK import violation(s):
  agentic_core/L2_execution/healers/healing_provider_adapters.py:117: blocked import 'openai'
  agentic_core/L2_execution/healers/vllm_process_manager.py:106: blocked import 'requests'
  apps_rg/utils/deep_brain_harvester_util.py:79: blocked import 'openai'
  apps_shared/utils/late_interaction_reranker_util.py:44: blocked import 'sentence_transformers'
  apps_shared/utils/late_interaction_reranker_util.py:63: blocked import 'sentence_transformers'

NOTE: 5 violations are PRE-EXISTING in files outside Phase 1 scope:
  agentic_core/L2_execution/healers/healing_provider_adapters.py (openai)
  agentic_core/L2_execution/healers/vllm_process_manager.py (requests)
  apps_rg/utils/deep_brain_harvester_util.py (openai)
  apps_shared/utils/late_interaction_reranker_util.py (sentence_transformers x2)
Phase 1 CLOSED: apps_rg/utils/providers_anthropic_client_util.py removed from
  ALLOWED_PATHS (W1.3). No new violations introduced by Phase 1.
EXIT CODE: 1

## CICheckWallClockInDeterminism

$ python ops_scripts/ci/check_wall_clock_in_determinism.py
FAIL: 140 wall-clock usage(s) in determinism paths:
  agentic_core/L0_routing/enforcement/mutation_prohibition.py:96: wall-clock call 'datetime.now'
  agentic_core/L0_routing/meta_control/meta_apply_ops.py:288: wall-clock call 'time.time'
  agentic_core/L0_routing/meta_control/meta_apply_ops.py:306: wall-clock call 'time.time'
  agentic_core/L0_routing/scripts/archive_duplicates_util.py:9: wall-clock call 'datetime.now'
  agentic_core/L0_routing/scripts/archive_duplicate_tests_util.py:43: wall-clock call 'datetime.now'
  agentic_core/L0_routing/scripts/bloat_analysis_util.py:250: wall-clock call 'datetime.now'
  agentic_core/L0_routing/scripts/bulk_hierarchy_heal_util.py:52: wall-clock call 'datetime.now'
  agentic_core/L0_routing/scripts/bulk_hierarchy_heal_util.py:72: wall-clock call 'datetime.now'
  agentic_core/L0_routing/scripts/class_info.py:528: wall-clock call 'datetime.now'
  agentic_core/L0_routing/scripts/colors.py:777: wall-clock call 'datetime.now'
  agentic_core/L0_routing/scripts/colors.py:779: wall-clock call 'datetime.now'
  agentic_core/L0_routing/scripts/colors.py:174: wall-clock call 'datetime.now'
  agentic_core/L0_routing/scripts/colors.py:218: wall-clock call 'datetime.now'
  agentic_core/L0_routing/scripts/colors.py:194: wall-clock call 'datetime.now'
  agentic_core/L0_routing/scripts/colors.py:251: wall-clock call 'datetime.now'
  agentic_core/L0_routing/scripts/colors.py:762: wall-clock call 'datetime.now'
  agentic_core/L0_routing/scripts/c_c_measurement.py:27: wall-clock call 'datetime.now'
  agentic_core/L0_routing/scripts/error_handler.py:148: wall-clock call 'time.time'
  agentic_core/L0_routing/scripts/error_handler.py:185: wall-clock call 'time.time'
  agentic_core/L0_routing/scripts/execute_ssot.py:551: wall-clock call 'datetime.now'
  agentic_core/L0_routing/scripts/execute_ssot.py:1319: wall-clock call 'datetime.now'
  agentic_core/L0_routing/scripts/execute_ssot.py:1366: wall-clock call 'datetime.now'
  agentic_core/L0_routing/scripts/execute_ssot.py:1654: wall-clock call 'datetime.now'
  agentic_core/L0_routing/scripts/execute_ssot.py:757: wall-clock call 'datetime.now'
  agentic_core/L0_routing/scripts/execute_ssot.py:925: wall-clock call 'time.time'
  agentic_core/L0_routing/scripts/execute_ssot.py:2280: wall-clock call 'datetime.now'
  agentic_core/L0_routing/scripts/execute_ssot.py:1338: wall-clock call 'datetime.now'
  agentic_core/L0_routing/scripts/execute_ssot.py:1349: wall-clock call 'datetime.now'
  agentic_core/L0_routing/scripts/execute_ssot.py:2325: wall-clock call 'datetime.now'
  agentic_core/L0_routing/scripts/execute_ssot.py:3149: wall-clock call 'time.time'
  agentic_core/L0_routing/scripts/extract_agent_duplicates_util.py:80: wall-clock call 'datetime.now'
  agentic_core/L0_routing/scripts/find_real_duplicates_v2_util.py:100: wall-clock call 'datetime.now'
  agentic_core/L0_routing/scripts/fission_executor_util.py:71: wall-clock call 'datetime.now'
  agentic_core/L0_routing/scripts/forensic_discovery_prep.py:397: wall-clock call 'datetime.now'
  agentic_core/L0_routing/scripts/forward_rolling_facade.py:161: wall-clock call 'time.time'
  agentic_core/L0_routing/scripts/forward_rolling_facade.py:203: wall-clock call 'time.time'
  agentic_core/L0_routing/scripts/full_agent_discovery.py:533: wall-clock call 'datetime.now'
  agentic_core/L0_routing/scripts/generate_dashboard_ssot_util.py:100: wall-clock call 'datetime.now'
  agentic_core/L0_routing/scripts/generate_dashboard_ssot_util.py:269: wall-clock call 'datetime.now'
  agentic_core/L0_routing/scripts/ssot_cli.py:164: wall-clock call 'datetime.now'
  agentic_core/L0_routing/types/routing_config_seal.py:46: wall-clock call 'datetime.now'
  agentic_core/L0_routing/utils/complexity_visitor_util.py:1281: wall-clock call 'time.time'
  agentic_core/L0_routing/utils/complexity_visitor_util.py:1648: wall-clock call 'time.time'
  agentic_core/L0_routing/utils/complexity_visitor_util.py:460: wall-clock call 'datetime.utcnow'
  agentic_core/L0_routing/utils/force_annexation_util.py:48: wall-clock call 'datetime.now'
  agentic_core/L0_routing/utils/json_formatter_util.py:21: wall-clock call 'datetime.now'
  agentic_core/L0_routing/utils/scorched_earth_merge_util.py:80: wall-clock call 'datetime.now'
  agentic_core/mixins/atomic_execution_mixin.py:100: wall-clock call 'datetime.utcnow'
  agentic_core/mixins/audit_trail_mixin.py:148: wall-clock call 'time.time'
  agentic_core/mixins/audit_trail_mixin.py:276: wall-clock call 'time.time'
  agentic_core/mixins/audit_trail_mixin.py:151: wall-clock call 'datetime.now'
  agentic_core/mixins/audit_trail_mixin.py:415: wall-clock call 'time.time'
  agentic_core/mixins/audit_trail_mixin.py:170: wall-clock call 'datetime.now'
  agentic_core/mixins/audit_trail_mixin.py:139: wall-clock call 'datetime.now'
  agentic_core/mixins/autonomy_mixin.py:31: wall-clock call 'time.time'
  agentic_core/mixins/autonomy_mixin.py:41: wall-clock call 'time.time'
  agentic_core/mixins/caching_mixin.py:37: wall-clock call 'time.time'
  agentic_core/mixins/circuit_breaker_mixin.py:148: wall-clock call 'datetime.utcnow'
  agentic_core/mixins/circuit_breaker_mixin.py:161: wall-clock call 'datetime.utcnow'
  agentic_core/mixins/circuit_breaker_mixin.py:170: wall-clock call 'datetime.utcnow'
  agentic_core/mixins/circuit_breaker_mixin.py:176: wall-clock call 'datetime.utcnow'
  agentic_core/mixins/circuit_breaker_mixin.py:183: wall-clock call 'datetime.utcnow'
  agentic_core/mixins/circuit_breaker_mixin.py:190: wall-clock call 'datetime.utcnow'
  agentic_core/mixins/context_management_mixin.py:356: wall-clock call 'time.time'
  agentic_core/mixins/context_management_mixin.py:328: wall-clock call 'time.time'
  agentic_core/mixins/cost_mixin.py:123: wall-clock call 'time.time'
  agentic_core/mixins/cost_mixin.py:410: wall-clock call 'time.time'
  agentic_core/mixins/cost_mixin.py:404: wall-clock call 'time.time'
  agentic_core/mixins/feature_flagged_agent_mixin.py:451: wall-clock call 'time.time'
  agentic_core/mixins/hardening_mixin.py:100: wall-clock call 'time.time'
  agentic_core/mixins/hardening_mixin.py:117: wall-clock call 'time.time'
  agentic_core/mixins/hardening_mixin.py:130: wall-clock call 'time.time'
  agentic_core/mixins/hardening_mixin.py:145: wall-clock call 'time.time'
  agentic_core/mixins/hardening_mixin.py:158: wall-clock call 'time.time'
  agentic_core/mixins/hitl_mixin.py:422: wall-clock call 'time.time'
  agentic_core/mixins/hitl_mixin.py:472: wall-clock call 'time.time'
  agentic_core/mixins/hitl_mixin.py:72: wall-clock call 'time.time'
  agentic_core/mixins/hitl_mixin.py:325: wall-clock call 'time.time'
  agentic_core/mixins/hitl_mixin.py:538: wall-clock call 'time.time'
  agentic_core/mixins/lifecycle_mixin.py:169: wall-clock call 'time.time'
  agentic_core/mixins/lifecycle_mixin.py:215: wall-clock call 'time.time'
  agentic_core/mixins/lifecycle_mixin.py:239: wall-clock call 'time.time'
  agentic_core/mixins/mcp_operation_mixin.py:85: wall-clock call 'time.monotonic'
  agentic_core/mixins/mcp_operation_mixin.py:153: wall-clock call 'time.time'
  agentic_core/mixins/mcp_operation_mixin.py:92: wall-clock call 'time.monotonic'
  agentic_core/mixins/mcp_operation_mixin.py:97: wall-clock call 'time.monotonic'
  agentic_core/mixins/mcp_operation_mixin.py:108: wall-clock call 'time.monotonic'
  agentic_core/mixins/metrics_mixin.py:174: wall-clock call 'time.time'
  agentic_core/mixins/metrics_mixin.py:190: wall-clock call 'time.time'
  agentic_core/mixins/metrics_mixin.py:182: wall-clock call 'time.time'
  agentic_core/mixins/metrics_mixin.py:198: wall-clock call 'time.time'
  agentic_core/mixins/migration_mixin.py:83: wall-clock call 'datetime.utcnow'
  agentic_core/mixins/performance_mixin.py:525: wall-clock call 'time.time'
  agentic_core/mixins/performance_mixin.py:541: wall-clock call 'time.time'
  agentic_core/mixins/performance_mixin.py:48: wall-clock call 'time.time'
  agentic_core/mixins/performance_mixin.py:533: wall-clock call 'time.time'
  agentic_core/mixins/performance_mixin.py:549: wall-clock call 'time.time'
  agentic_core/mixins/pinecone_vector_mixin.py:139: wall-clock call 'time.time'
  agentic_core/mixins/pinecone_vector_mixin.py:271: wall-clock call 'time.time'
  agentic_core/mixins/pinecone_vector_mixin.py:235: wall-clock call 'time.time'
  agentic_core/mixins/pinecone_vector_mixin.py:293: wall-clock call 'time.time'
  agentic_core/mixins/pinecone_vector_mixin.py:176: wall-clock call 'time.time'
  agentic_core/mixins/pinecone_vector_mixin.py:204: wall-clock call 'time.time'
  agentic_core/mixins/pinecone_vector_mixin.py:283: wall-clock call 'time.time'
  agentic_core/mixins/pinecone_vector_mixin.py:228: wall-clock call 'time.time'
  agentic_core/mixins/rate_limit_mixin.py:79: wall-clock call 'time.time'
  agentic_core/mixins/redis_cache_mixin.py:52: wall-clock call 'time.time'
  agentic_core/mixins/redis_cache_mixin.py:151: wall-clock call 'time.time'
  agentic_core/mixins/redis_cache_mixin.py:200: wall-clock call 'time.time'
  agentic_core/mixins/redis_cache_mixin.py:63: wall-clock call 'time.time'
  agentic_core/mixins/redis_cache_mixin.py:178: wall-clock call 'time.time'
  agentic_core/mixins/redis_cache_mixin.py:183: wall-clock call 'time.time'
  agentic_core/mixins/redis_cache_mixin.py:213: wall-clock call 'time.time'
  agentic_core/mixins/redis_cache_mixin.py:236: wall-clock call 'time.time'
  agentic_core/mixins/redis_cache_mixin.py:162: wall-clock call 'time.time'
  agentic_core/mixins/redis_cache_mixin.py:223: wall-clock call 'time.time'
  agentic_core/mixins/secrets_management_mixin.py:64: wall-clock call 'time.time'
  agentic_core/mixins/secrets_management_mixin.py:86: wall-clock call 'time.time'
  agentic_core/mixins/self_diagnosis_mixin.py:54: wall-clock call 'datetime.utcnow'
  agentic_core/mixins/ssot_audit_trail_mixin.py:84: wall-clock call 'time.time'
  agentic_core/mixins/ssot_caching_mixin.py:80: wall-clock call 'time.time'
  agentic_core/mixins/ssot_caching_mixin.py:50: wall-clock call 'time.time'
  agentic_core/mixins/ssot_circuit_breaker_mixin.py:90: wall-clock call 'time.time'
  agentic_core/mixins/ssot_circuit_breaker_mixin.py:118: wall-clock call 'time.time'
  agentic_core/mixins/ssot_cognitive_recovery_mixin.py:69: wall-clock call 'time.time'
  agentic_core/mixins/ssot_meta_learning_mixin.py:126: wall-clock call 'time.time'
  agentic_core/mixins/ssot_metrics_mixin.py:63: wall-clock call 'time.time'
  agentic_core/mixins/ssot_rate_limit_mixin.py:76: wall-clock call 'time.time'
  agentic_core/mixins/ssot_rate_limit_mixin.py:102: wall-clock call 'time.time'
  agentic_core/mixins/ssot_self_diagnosis_mixin.py:55: wall-clock call 'time.time'
  agentic_core/mixins/ssot_state_validation_mixin.py:71: wall-clock call 'time.time'
  agentic_core/mixins/ssot_state_validation_mixin.py:105: wall-clock call 'time.time'
  agentic_core/mixins/ssot_tracing_mixin.py:64: wall-clock call 'time.time'
  agentic_core/mixins/ssot_tracing_mixin.py:86: wall-clock call 'time.time'
  agentic_core/mixins/tool_reliability_mixin.py:316: wall-clock call 'time.time'
  agentic_core/mixins/tool_reliability_mixin.py:333: wall-clock call 'time.time'
  agentic_core/mixins/tool_reliability_mixin.py:294: wall-clock call 'time.time'
  agentic_core/mixins/tool_reliability_mixin.py:343: wall-clock call 'time.time'
  agentic_core/mixins/tool_reliability_mixin.py:349: wall-clock call 'time.time'
  system_learning/engines/seed_pack_build_cli.py:211: wall-clock call 'time.time'
EXIT CODE: 1

## Uuid4EliminationTracingMixin

$ python -c "import ast; src=open('agentic_core/mixins/tracing_mixin.py').read(); ..."
uuid4 refs in tracing_mixin.py: []

## Uuid4EliminationGovernanceContracts

$ python -c "import ast; src=open('agentic_core/L0_routing/enforcement/governance_contracts.py').read(); ..."
uuid4 refs in governance_contracts.py: []

## PreconditionStatus

REQ-417 runtime_mutation_guard.py exists: False (Phase 2 / Wave 4 deliverable)
CI AST guard check_llm_sdk_imports.py: ACTIVE
CI wall-clock guard check_wall_clock_in_determinism.py: ACTIVE

## FullSuiteBaseline

Pre-existing failures in tests/system_learning/ (175 failures).
Root cause: ModuleNotFoundError for system_learning engine modules not yet implemented.
Phase 1 changes do NOT touch any system_learning module.
Counts: 3442 passed, 175 failed (pre-existing), 19 skipped, 10 xfailed.
Phase 1 acceptance criterion: governance tests 7/7 PASSED.

