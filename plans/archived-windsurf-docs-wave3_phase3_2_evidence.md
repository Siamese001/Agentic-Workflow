---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\wave3_phase3_2_evidence.md'
original_relative_path: 'wave3_phase3_2_evidence.md'
source_sha256: 073706cbeb790be0d5a35a914ec9f8bd5d4957d14a098fbaef8c35efecb69fcb
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-05'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Wave 3 Phase 3.2 - Boundary Hardening

## Scope

Add 44-test branch-coverage suite for boundary hardening across L2-L6 and architecture component presence.
Covers: analyze_l2_execution (validator loop), analyze_l3_orchestration (orchestrator branch),
analyze_l4_state (blob_storage threshold), analyze_l5_safety (enforcement loop),
analyze_l6_observability (telemetry loop), analyze_architecture_component_presence (MISSING/WEAK),
_dedupe_gaps (deduplication + priority ordering), real codebase invariants.
No analyzer code changes. N=1 file declared.

- tests/architecture/test_wave3_phase3_2_boundary_hardening.py

## CODE_COMMIT

84d667cf7

## EVIDENCE_COMMIT

5f0a90cf7

## FILES_CHANGED_CODE

```
tests/architecture/test_wave3_phase3_2_boundary_hardening.py
```

## FILES_CHANGED_EVIDENCE

```
docs/reports/plans/wave3_phase3_2_evidence.md
tools/evidence/wave3_phase3_2_runner.py
```

## INSPECTED_FILES

- tests/architecture/test_wave3_phase3_2_boundary_hardening.py

## Pytest - Phase 3.2 Tests

$ python -m pytest -q --color=no tests/architecture/test_wave3_phase3_2_boundary_hardening.py
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 44 items

tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_l2_validator_cache_in_name_skipped
-------------------------------- live log call --------------------------------
2026-03-05 23:40:27 [    INFO] tools.semantic_gap_analyzer: Analyzing L2 Execution Layer...
PASSED                                                                   [  2%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_l2_validator_parse_fail_skipped
-------------------------------- live log call --------------------------------
2026-03-05 23:40:27 [    INFO] tools.semantic_gap_analyzer: Analyzing L2 Execution Layer...
PASSED                                                                   [  4%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_l2_validator_no_cache_import_generates_gap
-------------------------------- live log call --------------------------------
2026-03-05 23:40:27 [    INFO] tools.semantic_gap_analyzer: Analyzing L2 Execution Layer...
PASSED                                                                   [  6%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_l2_validator_with_cache_module_no_gap
-------------------------------- live log call --------------------------------
2026-03-05 23:40:27 [    INFO] tools.semantic_gap_analyzer: Analyzing L2 Execution Layer...
PASSED                                                                   [  9%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_l2_validator_with_symbol_cache_no_gap
-------------------------------- live log call --------------------------------
2026-03-05 23:40:27 [    INFO] tools.semantic_gap_analyzer: Analyzing L2 Execution Layer...
PASSED                                                                   [ 11%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_l2_no_validator_files_no_gap
-------------------------------- live log call --------------------------------
2026-03-05 23:40:27 [    INFO] tools.semantic_gap_analyzer: Analyzing L2 Execution Layer...
PASSED                                                                   [ 13%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_l3_orchestrator_parse_fail_no_gap
-------------------------------- live log call --------------------------------
2026-03-05 23:40:27 [    INFO] tools.semantic_gap_analyzer: Analyzing L3 Orchestration Layer...
PASSED                                                                   [ 15%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_l3_orchestrator_no_cache_generates_gap
-------------------------------- live log call --------------------------------
2026-03-05 23:40:27 [    INFO] tools.semantic_gap_analyzer: Analyzing L3 Orchestration Layer...
PASSED                                                                   [ 18%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_l3_orchestrator_with_cache_module_no_gap
-------------------------------- live log call --------------------------------
2026-03-05 23:40:27 [    INFO] tools.semantic_gap_analyzer: Analyzing L3 Orchestration Layer...
PASSED                                                                   [ 20%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_l3_orchestrator_file_missing_no_gap
-------------------------------- live log call --------------------------------
2026-03-05 23:40:27 [    INFO] tools.semantic_gap_analyzer: Analyzing L3 Orchestration Layer...
PASSED                                                                   [ 22%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_l4_blob_parse_fail_no_gap
-------------------------------- live log call --------------------------------
2026-03-05 23:40:27 [    INFO] tools.semantic_gap_analyzer: Analyzing L4 State Layer...
PASSED                                                                   [ 25%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_l4_blob_exactly_ten_accesses_no_gap
-------------------------------- live log call --------------------------------
2026-03-05 23:40:27 [    INFO] tools.semantic_gap_analyzer: Analyzing L4 State Layer...
PASSED                                                                   [ 27%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_l4_blob_eleven_accesses_generates_gap
-------------------------------- live log call --------------------------------
2026-03-05 23:40:27 [    INFO] tools.semantic_gap_analyzer: Analyzing L4 State Layer...
PASSED                                                                   [ 29%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_l4_blob_file_missing_no_gap
-------------------------------- live log call --------------------------------
2026-03-05 23:40:27 [    INFO] tools.semantic_gap_analyzer: Analyzing L4 State Layer...
PASSED                                                                   [ 31%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_l5_enforcement_cache_in_name_skipped
-------------------------------- live log call --------------------------------
2026-03-05 23:40:27 [    INFO] tools.semantic_gap_analyzer: Analyzing L5 Safety Layer...
PASSED                                                                   [ 34%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_l5_enforcement_parse_fail_skipped
-------------------------------- live log call --------------------------------
2026-03-05 23:40:27 [    INFO] tools.semantic_gap_analyzer: Analyzing L5 Safety Layer...
PASSED                                                                   [ 36%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_l5_enforcement_policy_in_name_no_cache_generates_gap
-------------------------------- live log call --------------------------------
2026-03-05 23:40:27 [    INFO] tools.semantic_gap_analyzer: Analyzing L5 Safety Layer...
PASSED                                                                   [ 38%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_l5_enforcement_no_policy_in_name_no_gap
-------------------------------- live log call --------------------------------
2026-03-05 23:40:27 [    INFO] tools.semantic_gap_analyzer: Analyzing L5 Safety Layer...
PASSED                                                                   [ 40%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_l5_enforcement_with_cache_import_no_gap
-------------------------------- live log call --------------------------------
2026-03-05 23:40:27 [    INFO] tools.semantic_gap_analyzer: Analyzing L5 Safety Layer...
PASSED                                                                   [ 43%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_l5_no_enforcement_files_no_gap
-------------------------------- live log call --------------------------------
2026-03-05 23:40:27 [    INFO] tools.semantic_gap_analyzer: Analyzing L5 Safety Layer...
PASSED                                                                   [ 45%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_l6_telemetry_parse_fail_skipped
-------------------------------- live log call --------------------------------
2026-03-05 23:40:27 [    INFO] tools.semantic_gap_analyzer: Analyzing L6 Observability Layer...
PASSED                                                                   [ 47%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_l6_telemetry_no_cache_import_generates_gap
-------------------------------- live log call --------------------------------
2026-03-05 23:40:27 [    INFO] tools.semantic_gap_analyzer: Analyzing L6 Observability Layer...
PASSED                                                                   [ 50%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_l6_telemetry_with_cache_module_no_gap
-------------------------------- live log call --------------------------------
2026-03-05 23:40:27 [    INFO] tools.semantic_gap_analyzer: Analyzing L6 Observability Layer...
PASSED                                                                   [ 52%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_l6_telemetry_with_symbol_cache_no_gap
-------------------------------- live log call --------------------------------
2026-03-05 23:40:27 [    INFO] tools.semantic_gap_analyzer: Analyzing L6 Observability Layer...
PASSED                                                                   [ 54%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_l6_no_telemetry_files_no_gap
-------------------------------- live log call --------------------------------
2026-03-05 23:40:27 [    INFO] tools.semantic_gap_analyzer: Analyzing L6 Observability Layer...
PASSED                                                                   [ 56%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_arch_component_missing_file_generates_missing_gap
-------------------------------- live log call --------------------------------
2026-03-05 23:40:27 [    INFO] tools.semantic_gap_analyzer: Analyzing Architecture Component Presence...
PASSED                                                                   [ 59%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_arch_component_parse_fail_no_gap
-------------------------------- live log call --------------------------------
2026-03-05 23:40:27 [    INFO] tools.semantic_gap_analyzer: Analyzing Architecture Component Presence...
PASSED                                                                   [ 61%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_arch_component_signals_present_no_gap
-------------------------------- live log call --------------------------------
2026-03-05 23:40:27 [    INFO] tools.semantic_gap_analyzer: Analyzing Architecture Component Presence...
PASSED                                                                   [ 63%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_arch_component_no_signals_generates_weak_gap
-------------------------------- live log call --------------------------------
2026-03-05 23:40:27 [    INFO] tools.semantic_gap_analyzer: Analyzing Architecture Component Presence...
PASSED                                                                   [ 65%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_dedupe_gaps_empty_input PASSED [ 68%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_dedupe_gaps_no_duplicates_all_retained PASSED [ 70%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_dedupe_gaps_duplicate_key_keeps_higher_priority PASSED [ 72%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_dedupe_gaps_sorted_by_priority PASSED [ 75%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_analyze_l2_execution_returns_list
-------------------------------- live log call --------------------------------
2026-03-05 23:40:27 [    INFO] tools.semantic_gap_analyzer: Analyzing L2 Execution Layer...
PASSED                                                                   [ 77%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_analyze_l3_orchestration_returns_list
-------------------------------- live log call --------------------------------
2026-03-05 23:40:27 [    INFO] tools.semantic_gap_analyzer: Analyzing L3 Orchestration Layer...
PASSED                                                                   [ 79%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_analyze_l4_state_returns_list
-------------------------------- live log call --------------------------------
2026-03-05 23:40:27 [    INFO] tools.semantic_gap_analyzer: Analyzing L4 State Layer...
PASSED                                                                   [ 81%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_analyze_l5_safety_returns_list
-------------------------------- live log call --------------------------------
2026-03-05 23:40:27 [    INFO] tools.semantic_gap_analyzer: Analyzing L5 Safety Layer...
PASSED                                                                   [ 84%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_analyze_l6_observability_returns_list
-------------------------------- live log call --------------------------------
2026-03-05 23:40:28 [    INFO] tools.semantic_gap_analyzer: Analyzing L6 Observability Layer...
PASSED                                                                   [ 86%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_analyze_architecture_component_presence_returns_list
-------------------------------- live log call --------------------------------
2026-03-05 23:40:28 [    INFO] tools.semantic_gap_analyzer: Analyzing Architecture Component Presence...
PASSED                                                                   [ 88%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_l2_validator_gaps_are_high_priority
-------------------------------- live log call --------------------------------
2026-03-05 23:40:28 [    INFO] tools.semantic_gap_analyzer: Analyzing L2 Execution Layer...
PASSED                                                                   [ 90%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_l3_gap001_is_medium_if_present
-------------------------------- live log call --------------------------------
2026-03-05 23:40:28 [    INFO] tools.semantic_gap_analyzer: Analyzing L3 Orchestration Layer...
PASSED                                                                   [ 93%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_l4_gap001_is_high_if_present
-------------------------------- live log call --------------------------------
2026-03-05 23:40:28 [    INFO] tools.semantic_gap_analyzer: Analyzing L4 State Layer...
PASSED                                                                   [ 95%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_l5_policy_gaps_are_medium_if_present
-------------------------------- live log call --------------------------------
2026-03-05 23:40:28 [    INFO] tools.semantic_gap_analyzer: Analyzing L5 Safety Layer...
PASSED                                                                   [ 97%]
tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_l6_config_gaps_are_low_if_present
-------------------------------- live log call --------------------------------
2026-03-05 23:40:28 [    INFO] tools.semantic_gap_analyzer: Analyzing L6 Observability Layer...
PASSED                                                                   [100%]

============================ slowest 10 durations =============================
0.21s call     tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_analyze_l5_safety_returns_list
0.17s call     tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_l5_policy_gaps_are_medium_if_present
0.02s call     tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_analyze_architecture_component_presence_returns_list
0.01s call     tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_analyze_l3_orchestration_returns_list
0.01s call     tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_l3_gap001_is_medium_if_present
0.01s call     tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_analyze_l2_execution_returns_list
0.01s call     tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_l2_validator_gaps_are_high_priority
0.01s call     tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_analyze_l6_observability_returns_list
0.01s call     tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_l6_config_gaps_are_low_if_present
0.01s call     tests/architecture/test_wave3_phase3_2_boundary_hardening.py::test_analyze_l4_state_returns_list
============================= 44 passed in 0.49s ==============================
```

collected 44 / executed 44

## BRANCH_INVENTORY

| File | Function | Branch Type | Condition | Expected | Test |
|------|----------|-------------|-----------|----------|------|
| `semantic_gap_analyzer.py` | `analyze_l2_execution` | boundary | 'cache' in validator filename | no gap | `test_l2_validator_cache_in_name_skipped` |
| `semantic_gap_analyzer.py` | `analyze_l2_execution` | boundary | parse failure | no gap | `test_l2_validator_parse_fail_skipped` |
| `semantic_gap_analyzer.py` | `analyze_l2_execution` | success | no schema_validator_cache import | L2-GAP-VALIDATOR HIGH | `test_l2_validator_no_cache_import_generates_gap` |
| `semantic_gap_analyzer.py` | `analyze_l2_execution` | negative | schema_validator_cache module imported | no gap | `test_l2_validator_with_cache_module_no_gap` |
| `semantic_gap_analyzer.py` | `analyze_l2_execution` | negative | SchemaValidatorCache symbol imported | no gap | `test_l2_validator_with_symbol_cache_no_gap` |
| `semantic_gap_analyzer.py` | `analyze_l2_execution` | boundary | no validator files | no gaps | `test_l2_no_validator_files_no_gap` |
| `semantic_gap_analyzer.py` | `analyze_l3_orchestration` | boundary | parse failure | no L3-GAP-001 | `test_l3_orchestrator_parse_fail_no_gap` |
| `semantic_gap_analyzer.py` | `analyze_l3_orchestration` | success | no plan cache import | L3-GAP-001 MEDIUM | `test_l3_orchestrator_no_cache_generates_gap` |
| `semantic_gap_analyzer.py` | `analyze_l3_orchestration` | negative | orchestration_plan_cache imported | no gap | `test_l3_orchestrator_with_cache_module_no_gap` |
| `semantic_gap_analyzer.py` | `analyze_l3_orchestration` | boundary | file does not exist | no gaps | `test_l3_orchestrator_file_missing_no_gap` |
| `semantic_gap_analyzer.py` | `analyze_l4_state` | boundary | parse failure | no L4-GAP-001 | `test_l4_blob_parse_fail_no_gap` |
| `semantic_gap_analyzer.py` | `analyze_l4_state` | boundary | exactly 10 l4_state_accesses | no L4-GAP-001 (boundary <= 10) | `test_l4_blob_exactly_ten_accesses_no_gap` |
| `semantic_gap_analyzer.py` | `analyze_l4_state` | success | 11 l4_state_accesses | L4-GAP-001 HIGH (> 10) | `test_l4_blob_eleven_accesses_generates_gap` |
| `semantic_gap_analyzer.py` | `analyze_l4_state` | boundary | file does not exist | no gaps | `test_l4_blob_file_missing_no_gap` |
| `semantic_gap_analyzer.py` | `analyze_l5_safety` | boundary | 'cache' in enforcement filename | no gap | `test_l5_enforcement_cache_in_name_skipped` |
| `semantic_gap_analyzer.py` | `analyze_l5_safety` | boundary | parse failure | no gap | `test_l5_enforcement_parse_fail_skipped` |
| `semantic_gap_analyzer.py` | `analyze_l5_safety` | success | 'policy' in name + no cache import | L5-GAP-POLICY MEDIUM | `test_l5_enforcement_policy_in_name_no_cache_generates_gap` |
| `semantic_gap_analyzer.py` | `analyze_l5_safety` | negative | 'policy' not in name | no gap | `test_l5_enforcement_no_policy_in_name_no_gap` |
| `semantic_gap_analyzer.py` | `analyze_l5_safety` | negative | policy_registry_cache imported | no gap | `test_l5_enforcement_with_cache_import_no_gap` |
| `semantic_gap_analyzer.py` | `analyze_l5_safety` | boundary | no enforcement files | no gaps | `test_l5_no_enforcement_files_no_gap` |
| `semantic_gap_analyzer.py` | `analyze_l6_observability` | boundary | parse failure | no gap | `test_l6_telemetry_parse_fail_skipped` |
| `semantic_gap_analyzer.py` | `analyze_l6_observability` | success | no config_file_cache import | L6-GAP-CONFIG LOW | `test_l6_telemetry_no_cache_import_generates_gap` |
| `semantic_gap_analyzer.py` | `analyze_l6_observability` | negative | config_file_cache module imported | no gap | `test_l6_telemetry_with_cache_module_no_gap` |
| `semantic_gap_analyzer.py` | `analyze_l6_observability` | negative | ConfigFileCache symbol imported | no gap | `test_l6_telemetry_with_symbol_cache_no_gap` |
| `semantic_gap_analyzer.py` | `analyze_l6_observability` | boundary | no telemetry files | no gaps | `test_l6_no_telemetry_files_no_gap` |
| `semantic_gap_analyzer.py` | `analyze_architecture_component_presence` | boundary | file does not exist | ARCH-COMPONENT-MISSING | `test_arch_component_missing_file_generates_missing_gap` |
| `semantic_gap_analyzer.py` | `analyze_architecture_component_presence` | boundary | parse failure | no gap | `test_arch_component_parse_fail_no_gap` |
| `semantic_gap_analyzer.py` | `analyze_architecture_component_presence` | negative | signals present | no ARCH-COMPONENT-WEAK | `test_arch_component_signals_present_no_gap` |
| `semantic_gap_analyzer.py` | `analyze_architecture_component_presence` | success | no signals found | ARCH-COMPONENT-WEAK | `test_arch_component_no_signals_generates_weak_gap` |
| `semantic_gap_analyzer.py` | `_dedupe_gaps` | boundary | empty input | empty output | `test_dedupe_gaps_empty_input` |
| `semantic_gap_analyzer.py` | `_dedupe_gaps` | negative | no duplicate keys | all retained | `test_dedupe_gaps_no_duplicates_all_retained` |
| `semantic_gap_analyzer.py` | `_dedupe_gaps` | success | dup key, HIGH vs MEDIUM | HIGH wins | `test_dedupe_gaps_duplicate_key_keeps_higher_priority` |
| `semantic_gap_analyzer.py` | `_dedupe_gaps` | contract | sorted by priority rank | HIGH < MEDIUM < LOW | `test_dedupe_gaps_sorted_by_priority` |
| `agentic_core (real)` | `analyze_l2_execution` | integration | returns list | list | `test_analyze_l2_execution_returns_list` |
| `agentic_core (real)` | `analyze_l3_orchestration` | integration | returns list | list | `test_analyze_l3_orchestration_returns_list` |
| `agentic_core (real)` | `analyze_l4_state` | integration | returns list | list | `test_analyze_l4_state_returns_list` |
| `agentic_core (real)` | `analyze_l5_safety` | integration | returns list | list | `test_analyze_l5_safety_returns_list` |
| `agentic_core (real)` | `analyze_l6_observability` | integration | returns list | list | `test_analyze_l6_observability_returns_list` |
| `agentic_core (real)` | `analyze_architecture_component_presence` | integration | returns list | list | `test_analyze_architecture_component_presence_returns_list` |
| `agentic_core (real)` | `L2-GAP-VALIDATOR priority` | contract | HIGH | all HIGH | `test_l2_validator_gaps_are_high_priority` |
| `agentic_core (real)` | `L3-GAP-001 priority` | contract | MEDIUM | MEDIUM | `test_l3_gap001_is_medium_if_present` |
| `agentic_core (real)` | `L4-GAP-001 priority` | contract | HIGH | HIGH | `test_l4_gap001_is_high_if_present` |
| `agentic_core (real)` | `L5-GAP-POLICY priority` | contract | MEDIUM | all MEDIUM | `test_l5_policy_gaps_are_medium_if_present` |
| `agentic_core (real)` | `L6-GAP-CONFIG priority` | contract | LOW | all LOW | `test_l6_config_gaps_are_low_if_present` |

## ROBUSTNESS_MATRIX

| Surface | Success IDs | Edge/Boundary IDs | Failure IDs | Determinism |
|---------|-------------|-------------------|-------------|-------------|
| analyze_l2_execution | test_l2_validator_no_cache_import_generates_gap | test_l2_validator_cache_in_name_skipped, test_l2_no_validator_files_no_gap | test_l2_validator_parse_fail_skipped | idempotent |
| analyze_l3_orchestration | test_l3_orchestrator_no_cache_generates_gap | test_l3_orchestrator_file_missing_no_gap | test_l3_orchestrator_parse_fail_no_gap | idempotent |
| analyze_l4_state | test_l4_blob_eleven_accesses_generates_gap | test_l4_blob_exactly_ten_accesses_no_gap, test_l4_blob_file_missing_no_gap | test_l4_blob_parse_fail_no_gap | idempotent |
| analyze_l5_safety | test_l5_enforcement_policy_in_name_no_cache_generates_gap | test_l5_enforcement_no_policy_in_name_no_gap, test_l5_enforcement_cache_in_name_skipped, test_l5_no_enforcement_files_no_gap | test_l5_enforcement_parse_fail_skipped | idempotent |
| analyze_l6_observability | test_l6_telemetry_no_cache_import_generates_gap | test_l6_no_telemetry_files_no_gap | test_l6_telemetry_parse_fail_skipped | idempotent |
| analyze_architecture_component_presence | test_arch_component_no_signals_generates_weak_gap, test_arch_component_missing_file_generates_missing_gap | - | test_arch_component_parse_fail_no_gap | idempotent |
| _dedupe_gaps | test_dedupe_gaps_duplicate_key_keeps_higher_priority, test_dedupe_gaps_sorted_by_priority | test_dedupe_gaps_empty_input, test_dedupe_gaps_no_duplicates_all_retained | - | deterministic |

## DEFECT_MODEL

| Defect Mechanism | Covered By |
|-----------------|------------|
| L2 validator file named '*_cache.py' wrongly gets L2-GAP-VALIDATOR | test_l2_validator_cache_in_name_skipped |
| L3-GAP-001 wrong priority (not MEDIUM) | test_l3_gap001_is_medium_if_present, test_l3_orchestrator_no_cache_generates_gap |
| L4-GAP-001 threshold off-by-one (fires at 10, should fire at >10) | test_l4_blob_exactly_ten_accesses_no_gap, test_l4_blob_eleven_accesses_generates_gap |
| L4-GAP-001 wrong priority (not HIGH) | test_l4_gap001_is_high_if_present, test_l4_blob_eleven_accesses_generates_gap |
| L5-GAP-POLICY fires for non-policy enforcement files | test_l5_enforcement_no_policy_in_name_no_gap |
| L6-GAP-CONFIG wrong priority (not LOW) | test_l6_config_gaps_are_low_if_present, test_l6_telemetry_no_cache_import_generates_gap |
| ARCH-COMPONENT-MISSING gap not generated for missing file | test_arch_component_missing_file_generates_missing_gap |
| ARCH-COMPONENT-WEAK gap generated despite signals present | test_arch_component_signals_present_no_gap |
| _dedupe_gaps drops lower-priority duplicate instead of higher-priority | test_dedupe_gaps_duplicate_key_keeps_higher_priority |
| _dedupe_gaps output not sorted by priority | test_dedupe_gaps_sorted_by_priority |

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

