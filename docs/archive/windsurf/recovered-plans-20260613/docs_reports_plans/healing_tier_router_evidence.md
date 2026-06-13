# L2.3 Healing Tier Router - Evidence

## Scope

Implement centralized L2.3 healing tier router with:
- HealingInput/HealingDecision/FailureSignal contracts
- L4-backed config (X/Y thresholds, model IDs)
- Deterministic heal_confidence scoring
- Single choke point tier routing
- Tiering allowlist (10 YES_TIERING agents)
- AST-based enforcement (NO_TIERING prohibition)
- Determinism proof (byte-identical decisions)

CODE_COMMIT=a49fe8908505be1446b2641c249adde353b58087
SEALED_FROM=a49fe8908505be1446b2641c249adde353b58087

## Config Values

```
HEAL_CONFIDENCE_X=0.75
HEAL_CONFIDENCE_Y=0.40
MAX_HEAL_RETRIES=3
MODEL_QWEN_VLLM_ID=qwen2.5-coder-32b-instruct
MODEL_GEMINI_2_5_PRO_ID=gemini-2.5-pro
```

## Test Execution

$ C:\Users\amita\AppData\Local\Programs\Python\Python312\python.exe -m pytest tests/agentic_core/L2_execution/healers/test_healing_tier_router.py -v --color=no --tb=short -m unit_min_deps

```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0 -- C:\Users\amita\AppData\Local\Programs\Python\Python312\python.exe
cachedir: .pytest_cache
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 39 items

tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestHealingTierConfig::test_valid_config PASSED [  2%]
tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestHealingTierConfig::test_x_must_be_greater_than_y PASSED [  5%]
tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestHealingTierConfig::test_x_equals_y_rejected PASSED [  7%]
tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestHealingTierConfig::test_max_retries_must_be_positive PASSED [ 10%]
tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestHealingTierConfig::test_empty_model_ids_rejected PASSED [ 12%]
tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestHealingTierConfig::test_load_default_config PASSED [ 15%]
tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestHealingInput::test_valid_input PASSED [ 17%]
tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestHealingInput::test_empty_failure_type_rejected PASSED [ 20%]
tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestHealingInput::test_negative_retry_count_rejected PASSED [ 23%]
tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestHealingInput::test_blast_radius_out_of_range PASSED [ 25%]
tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestHealingInput::test_blast_radius_negative PASSED [ 28%]
tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestHealingDecision::test_valid_decision PASSED [ 30%]
tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestHealingDecision::test_confidence_out_of_range PASSED [ 33%]
tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestComputeHealConfidence::test_high_confidence_syntax_error PASSED [ 35%]
tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestComputeHealConfidence::test_low_confidence_runtime_error PASSED [ 38%]
tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestComputeHealConfidence::test_retry_decay_lowers_score PASSED [ 41%]
tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestComputeHealConfidence::test_historical_success_rate_affects_score PASSED [ 43%]
tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestComputeHealConfidence::test_score_clamped_to_unit_interval PASSED [ 46%]
tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestComputeHealConfidence::test_reason_codes_populated PASSED [ 48%]
tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestRouteHealingTier::test_local_agent_band PASSED [ 51%]
tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestRouteHealingTier::test_qwen_vllm_band PASSED [ 53%]
tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestRouteHealingTier::test_gemini_band PASSED [ 56%]
tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestRouteHealingTier::test_retry_count_forces_gemini PASSED [ 58%]
tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestRouteHealingTier::test_retry_count_above_max_forces_gemini PASSED [ 61%]
tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestRouteHealingTier::test_decision_has_reason_codes PASSED [ 64%]
tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestFailureSignal::test_valid_signal PASSED [ 66%]
tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestFailureSignal::test_to_healing_input PASSED [ 69%]
tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestFailureSignal::test_empty_source_agent_rejected PASSED [ 71%]
tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestTieringAllowlist::test_allowlist_count PASSED [ 74%]
tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestTieringAllowlist::test_yes_tiering_agents_in_allowlist PASSED [ 76%]
tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestTieringAllowlist::test_is_tiering_allowed_yes PASSED [ 79%]
tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestTieringAllowlist::test_is_tiering_allowed_no PASSED [ 82%]
tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestTieringAllowlist::test_is_tiering_allowed_by_path PASSED [ 84%]
tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestNoTieringEnforcement::test_no_tiering_agents_do_not_import_tier_router PASSED [ 87%]
tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestNoTieringEnforcement::test_negative_control_enforcement_would_catch_violation PASSED [ 89%]
tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestDeterminism::test_deterministic_routing_identical_output PASSED [ 92%]
tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestDeterminism::test_deterministic_scoring_identical_output PASSED [ 94%]
tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestDeterminism::test_deterministic_across_all_failure_types PASSED [ 97%]
tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestConfigPrinting::test_print_config_values PASSED [100%]

============================ slowest 10 durations =============================
0.26s call     tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestNoTieringEnforcement::test_no_tiering_agents_do_not_import_tier_router
0.00s setup    tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestHealingTierConfig::test_valid_config
0.00s setup    tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestConfigPrinting::test_print_config_values
0.00s setup    tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestDeterminism::test_deterministic_routing_identical_output
0.00s call     tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestDeterminism::test_deterministic_across_all_failure_types
0.00s call     tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestHealingTierConfig::test_x_must_be_greater_than_y
0.00s call     tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestDeterminism::test_deterministic_routing_identical_output
0.00s setup    tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestComputeHealConfidence::test_high_confidence_syntax_error
0.00s teardown tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestHealingTierConfig::test_valid_config
0.00s setup    tests/agentic_core/L2_execution/healers/test_healing_tier_router.py::TestDeterminism::test_deterministic_scoring_identical_output
============================= 39 passed in 0.34s ==============================
```

## Git Proof Completeness Gate (post evidence-only HEAD)

$ git log -1 --format=%H
0f69d24c752615e234fb5ff0a413810a7eecb2ec

$ git rev-parse HEAD
0f69d24c752615e234fb5ff0a413810a7eecb2ec

$ git rev-parse HEAD~1
a49fe8908505be1446b2641c249adde353b58087

$ git rev-parse HEAD~2
f247074b4b2d55392e4a9dd65d29135bd68a1434

$ git show --name-only --pretty=format: HEAD
docs/reports/plans/healing_tier_router_evidence.md

$ git status --porcelain


## Assertions

OK: git log -1 == git rev-parse HEAD: 0f69d24c752615e234fb5ff0a413810a7eecb2ec
OK: len(porcelain_stdout) == 0
OK: git show --name-only HEAD lists only: docs/reports/plans/healing_tier_router_evidence.md
OK: CODE_COMMIT validated as 40-hex: a49fe8908505be1446b2641c249adde353b58087
OK: SEALED_FROM validated as 40-hex: a49fe8908505be1446b2641c249adde353b58087
OK: HEAD~1 == CODE_COMMIT == SEALED_FROM: a49fe8908505be1446b2641c249adde353b58087

## FILES_CHANGED_CODE

```
tests/agentic_core/L2_execution/healers/test_healing_tier_router.py
tools/evidence/healing_tier_evidence_runner.py
```

## INSPECTED_FILES

```
agentic_core/L2_execution/healers/healing_tier_types.py
agentic_core/L2_execution/healers/healing_tier_config.py
agentic_core/L2_execution/healers/healing_tier_router.py
agentic_core/L2_execution/healers/tiering_allowlist.py
tests/agentic_core/L2_execution/healers/test_healing_tier_router.py
docs/technical/agent_confidence_tiering_recommendations.csv
docs/technical/agent_confidence_tiering_recommendations.md
```

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

