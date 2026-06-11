---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\wave3_phase3_1_evidence.md'
original_relative_path: 'wave3_phase3_1_evidence.md'
source_sha256: 2e499a4a44fb3e65d4a7a429e8d6a442a744f049a7c67a9b6c9350706579ad05
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-05'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Wave 3 Phase 3.1 - Cache Wirings + Performance

## Scope

Add 30-test branch-coverage suite for analyze_l0_routing_gate and analyze_l1_cognition.
Covers: _analysis_mentions_cache, _contains_module_reference, _contains_symbol_reference,
L0 routing gate (L0-GAP-001 HIGH, L0-GAP-002 MEDIUM), L1 cognition (L1-GAP-001 HIGH,
L1-GAP-PROMPT MEDIUM), parse-fail skips, cache exclusions, real codebase invariants.
No analyzer code changes. N=1 file declared.

- tests/architecture/test_wave3_phase3_1_cache_wirings.py

## CODE_COMMIT

8f2513ca9

## EVIDENCE_COMMIT

43b16fc29

## FILES_CHANGED_CODE

```
tests/architecture/test_wave3_phase3_1_cache_wirings.py
```

## FILES_CHANGED_EVIDENCE

```
docs/reports/plans/wave3_phase3_1_evidence.md
tools/evidence/wave3_phase3_1_runner.py
```

## INSPECTED_FILES

- tests/architecture/test_wave3_phase3_1_cache_wirings.py

## Pytest - Phase 3.1 Tests

$ python -m pytest -q --color=no tests/architecture/test_wave3_phase3_1_cache_wirings.py
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 30 items

tests/architecture/test_wave3_phase3_1_cache_wirings.py::test_analysis_mentions_cache_module_hint_match PASSED [  3%]
tests/architecture/test_wave3_phase3_1_cache_wirings.py::test_analysis_mentions_cache_symbol_hint_match PASSED [  6%]
tests/architecture/test_wave3_phase3_1_cache_wirings.py::test_analysis_mentions_cache_no_match PASSED [ 10%]
tests/architecture/test_wave3_phase3_1_cache_wirings.py::test_analysis_mentions_cache_no_symbol_hint_module_absent PASSED [ 13%]
tests/architecture/test_wave3_phase3_1_cache_wirings.py::test_contains_module_reference_substring_match PASSED [ 16%]
tests/architecture/test_wave3_phase3_1_cache_wirings.py::test_contains_symbol_reference_substring_match PASSED [ 20%]
tests/architecture/test_wave3_phase3_1_cache_wirings.py::test_discovery_py_parse_fail_no_l0_gap001
-------------------------------- live log call --------------------------------
2026-03-05 23:36:41 [    INFO] tools.semantic_gap_analyzer: Analyzing L0 Routing Gate...
PASSED                                                                   [ 23%]
tests/architecture/test_wave3_phase3_1_cache_wirings.py::test_discovery_py_no_cache_generates_l0_gap001
-------------------------------- live log call --------------------------------
2026-03-05 23:36:41 [    INFO] tools.semantic_gap_analyzer: Analyzing L0 Routing Gate...
PASSED                                                                   [ 26%]
tests/architecture/test_wave3_phase3_1_cache_wirings.py::test_discovery_py_with_module_cache_no_l0_gap001
-------------------------------- live log call --------------------------------
2026-03-05 23:36:41 [    INFO] tools.semantic_gap_analyzer: Analyzing L0 Routing Gate...
PASSED                                                                   [ 30%]
tests/architecture/test_wave3_phase3_1_cache_wirings.py::test_discovery_py_with_symbol_cache_no_l0_gap001
-------------------------------- live log call --------------------------------
2026-03-05 23:36:41 [    INFO] tools.semantic_gap_analyzer: Analyzing L0 Routing Gate...
PASSED                                                                   [ 33%]
tests/architecture/test_wave3_phase3_1_cache_wirings.py::test_policy_engine_parse_fail_no_l0_gap002
-------------------------------- live log call --------------------------------
2026-03-05 23:36:41 [    INFO] tools.semantic_gap_analyzer: Analyzing L0 Routing Gate...
PASSED                                                                   [ 36%]
tests/architecture/test_wave3_phase3_1_cache_wirings.py::test_policy_engine_no_cache_generates_l0_gap002
-------------------------------- live log call --------------------------------
2026-03-05 23:36:41 [    INFO] tools.semantic_gap_analyzer: Analyzing L0 Routing Gate...
PASSED                                                                   [ 40%]
tests/architecture/test_wave3_phase3_1_cache_wirings.py::test_policy_engine_with_cache_no_l0_gap002
-------------------------------- live log call --------------------------------
2026-03-05 23:36:41 [    INFO] tools.semantic_gap_analyzer: Analyzing L0 Routing Gate...
PASSED                                                                   [ 43%]
tests/architecture/test_wave3_phase3_1_cache_wirings.py::test_cognitive_engine_parse_fail_no_l1_gap001
-------------------------------- live log call --------------------------------
2026-03-05 23:36:41 [    INFO] tools.semantic_gap_analyzer: Analyzing L1 Cognition Layer...
PASSED                                                                   [ 46%]
tests/architecture/test_wave3_phase3_1_cache_wirings.py::test_cognitive_engine_no_cache_generates_l1_gap001
-------------------------------- live log call --------------------------------
2026-03-05 23:36:41 [    INFO] tools.semantic_gap_analyzer: Analyzing L1 Cognition Layer...
PASSED                                                                   [ 50%]
tests/architecture/test_wave3_phase3_1_cache_wirings.py::test_cognitive_engine_with_cache_no_l1_gap001
-------------------------------- live log call --------------------------------
2026-03-05 23:36:41 [    INFO] tools.semantic_gap_analyzer: Analyzing L1 Cognition Layer...
PASSED                                                                   [ 53%]
tests/architecture/test_wave3_phase3_1_cache_wirings.py::test_cognitive_engine_with_symbol_cache_no_l1_gap001
-------------------------------- live log call --------------------------------
2026-03-05 23:36:41 [    INFO] tools.semantic_gap_analyzer: Analyzing L1 Cognition Layer...
PASSED                                                                   [ 56%]
tests/architecture/test_wave3_phase3_1_cache_wirings.py::test_prompt_file_no_cache_generates_l1_gap_prompt
-------------------------------- live log call --------------------------------
2026-03-05 23:36:41 [    INFO] tools.semantic_gap_analyzer: Analyzing L1 Cognition Layer...
PASSED                                                                   [ 60%]
tests/architecture/test_wave3_phase3_1_cache_wirings.py::test_prompt_file_with_cache_in_name_no_l1_gap_prompt
-------------------------------- live log call --------------------------------
2026-03-05 23:36:41 [    INFO] tools.semantic_gap_analyzer: Analyzing L1 Cognition Layer...
PASSED                                                                   [ 63%]
tests/architecture/test_wave3_phase3_1_cache_wirings.py::test_prompt_file_with_cache_import_no_l1_gap_prompt
-------------------------------- live log call --------------------------------
2026-03-05 23:36:41 [    INFO] tools.semantic_gap_analyzer: Analyzing L1 Cognition Layer...
PASSED                                                                   [ 66%]
tests/architecture/test_wave3_phase3_1_cache_wirings.py::test_prompt_file_parse_fail_no_l1_gap_prompt
-------------------------------- live log call --------------------------------
2026-03-05 23:36:41 [    INFO] tools.semantic_gap_analyzer: Analyzing L1 Cognition Layer...
PASSED                                                                   [ 70%]
tests/architecture/test_wave3_phase3_1_cache_wirings.py::test_no_prompt_files_no_l1_gap_prompt
-------------------------------- live log call --------------------------------
2026-03-05 23:36:41 [    INFO] tools.semantic_gap_analyzer: Analyzing L1 Cognition Layer...
PASSED                                                                   [ 73%]
tests/architecture/test_wave3_phase3_1_cache_wirings.py::test_analyze_l0_routing_gate_returns_list
-------------------------------- live log call --------------------------------
2026-03-05 23:36:41 [    INFO] tools.semantic_gap_analyzer: Analyzing L0 Routing Gate...
PASSED                                                                   [ 76%]
tests/architecture/test_wave3_phase3_1_cache_wirings.py::test_analyze_l1_cognition_returns_list
-------------------------------- live log call --------------------------------
2026-03-05 23:36:41 [    INFO] tools.semantic_gap_analyzer: Analyzing L1 Cognition Layer...
PASSED                                                                   [ 80%]
tests/architecture/test_wave3_phase3_1_cache_wirings.py::test_l0_gap001_is_high_priority_if_present
-------------------------------- live log call --------------------------------
2026-03-05 23:36:41 [    INFO] tools.semantic_gap_analyzer: Analyzing L0 Routing Gate...
PASSED                                                                   [ 83%]
tests/architecture/test_wave3_phase3_1_cache_wirings.py::test_l0_gap002_is_medium_priority_if_present
-------------------------------- live log call --------------------------------
2026-03-05 23:36:41 [    INFO] tools.semantic_gap_analyzer: Analyzing L0 Routing Gate...
PASSED                                                                   [ 86%]
tests/architecture/test_wave3_phase3_1_cache_wirings.py::test_l1_gap001_is_high_priority_if_present
-------------------------------- live log call --------------------------------
2026-03-05 23:36:41 [    INFO] tools.semantic_gap_analyzer: Analyzing L1 Cognition Layer...
PASSED                                                                   [ 90%]
tests/architecture/test_wave3_phase3_1_cache_wirings.py::test_l1_gap_prompt_is_medium_priority_if_present
-------------------------------- live log call --------------------------------
2026-03-05 23:36:41 [    INFO] tools.semantic_gap_analyzer: Analyzing L1 Cognition Layer...
PASSED                                                                   [ 93%]
tests/architecture/test_wave3_phase3_1_cache_wirings.py::test_all_l0_gaps_have_evidence_files
-------------------------------- live log call --------------------------------
2026-03-05 23:36:41 [    INFO] tools.semantic_gap_analyzer: Analyzing L0 Routing Gate...
PASSED                                                                   [ 96%]
tests/architecture/test_wave3_phase3_1_cache_wirings.py::test_all_l1_gaps_have_evidence_files
-------------------------------- live log call --------------------------------
2026-03-05 23:36:41 [    INFO] tools.semantic_gap_analyzer: Analyzing L1 Cognition Layer...
PASSED                                                                   [100%]

============================ slowest 10 durations =============================
0.01s call     tests/architecture/test_wave3_phase3_1_cache_wirings.py::test_analyze_l1_cognition_returns_list
0.01s call     tests/architecture/test_wave3_phase3_1_cache_wirings.py::test_l1_gap001_is_high_priority_if_present
0.01s call     tests/architecture/test_wave3_phase3_1_cache_wirings.py::test_all_l1_gaps_have_evidence_files
0.01s call     tests/architecture/test_wave3_phase3_1_cache_wirings.py::test_l1_gap_prompt_is_medium_priority_if_present

(6 durations < 0.005s hidden.  Use -vv to show these durations.)
============================= 30 passed in 0.07s ==============================
```

collected 30 / executed 30

## BRANCH_INVENTORY

| File | Function | Branch Type | Condition | Expected | Test |
|------|----------|-------------|-----------|----------|------|
| `semantic_gap_analyzer.py` | `_analysis_mentions_cache` | success | module_hint in imported_module_names | True | `test_analysis_mentions_cache_module_hint_match` |
| `semantic_gap_analyzer.py` | `_analysis_mentions_cache` | success | symbol_hint in imported_symbol_names | True | `test_analysis_mentions_cache_symbol_hint_match` |
| `semantic_gap_analyzer.py` | `_analysis_mentions_cache` | negative | neither hint matches | False | `test_analysis_mentions_cache_no_match` |
| `semantic_gap_analyzer.py` | `_analysis_mentions_cache` | negative | no symbol_hint, module absent | False | `test_analysis_mentions_cache_no_symbol_hint_module_absent` |
| `semantic_gap_analyzer.py` | `_contains_module_reference` | success | substring match in module names | True | `test_contains_module_reference_substring_match` |
| `semantic_gap_analyzer.py` | `_contains_symbol_reference` | success | substring match in symbol names | True | `test_contains_symbol_reference_substring_match` |
| `semantic_gap_analyzer.py` | `analyze_l0_routing_gate (L0-GAP-001)` | boundary | discovery_py parse failure | no L0-GAP-001 | `test_discovery_py_parse_fail_no_l0_gap001` |
| `semantic_gap_analyzer.py` | `analyze_l0_routing_gate (L0-GAP-001)` | success | no cache import | L0-GAP-001 HIGH | `test_discovery_py_no_cache_generates_l0_gap001` |
| `semantic_gap_analyzer.py` | `analyze_l0_routing_gate (L0-GAP-001)` | negative | module cache imported | no L0-GAP-001 | `test_discovery_py_with_module_cache_no_l0_gap001` |
| `semantic_gap_analyzer.py` | `analyze_l0_routing_gate (L0-GAP-001)` | negative | symbol cache imported | no L0-GAP-001 | `test_discovery_py_with_symbol_cache_no_l0_gap001` |
| `semantic_gap_analyzer.py` | `analyze_l0_routing_gate (L0-GAP-002)` | boundary | policy_engine parse failure | no L0-GAP-002 | `test_policy_engine_parse_fail_no_l0_gap002` |
| `semantic_gap_analyzer.py` | `analyze_l0_routing_gate (L0-GAP-002)` | success | no policy cache import | L0-GAP-002 MEDIUM | `test_policy_engine_no_cache_generates_l0_gap002` |
| `semantic_gap_analyzer.py` | `analyze_l0_routing_gate (L0-GAP-002)` | negative | policy cache imported | no L0-GAP-002 | `test_policy_engine_with_cache_no_l0_gap002` |
| `semantic_gap_analyzer.py` | `analyze_l1_cognition (L1-GAP-001)` | boundary | cognitive_engine parse failure | no L1-GAP-001 | `test_cognitive_engine_parse_fail_no_l1_gap001` |
| `semantic_gap_analyzer.py` | `analyze_l1_cognition (L1-GAP-001)` | success | no tool cache import | L1-GAP-001 HIGH | `test_cognitive_engine_no_cache_generates_l1_gap001` |
| `semantic_gap_analyzer.py` | `analyze_l1_cognition (L1-GAP-001)` | negative | tool cache module imported | no L1-GAP-001 | `test_cognitive_engine_with_cache_no_l1_gap001` |
| `semantic_gap_analyzer.py` | `analyze_l1_cognition (L1-GAP-001)` | negative | ToolEmbeddingCache symbol imported | no L1-GAP-001 | `test_cognitive_engine_with_symbol_cache_no_l1_gap001` |
| `semantic_gap_analyzer.py` | `analyze_l1_cognition (prompt loop)` | success | no cache import, cache not in name | L1-GAP-PROMPT MEDIUM | `test_prompt_file_no_cache_generates_l1_gap_prompt` |
| `semantic_gap_analyzer.py` | `analyze_l1_cognition (prompt loop)` | negative | 'cache' in filename | no L1-GAP-PROMPT | `test_prompt_file_with_cache_in_name_no_l1_gap_prompt` |
| `semantic_gap_analyzer.py` | `analyze_l1_cognition (prompt loop)` | negative | prompt_artifact_cache imported | no L1-GAP-PROMPT | `test_prompt_file_with_cache_import_no_l1_gap_prompt` |
| `semantic_gap_analyzer.py` | `analyze_l1_cognition (prompt loop)` | boundary | prompt file parse failure | no L1-GAP-PROMPT | `test_prompt_file_parse_fail_no_l1_gap_prompt` |
| `semantic_gap_analyzer.py` | `analyze_l1_cognition (prompt loop)` | boundary | no prompt files found | no L1-GAP-PROMPT | `test_no_prompt_files_no_l1_gap_prompt` |
| `agentic_core (real)` | `analyze_l0_routing_gate` | integration | returns list | list type | `test_analyze_l0_routing_gate_returns_list` |
| `agentic_core (real)` | `analyze_l1_cognition` | integration | returns list | list type | `test_analyze_l1_cognition_returns_list` |
| `agentic_core (real)` | `L0-GAP-001 priority` | contract | HIGH | all HIGH | `test_l0_gap001_is_high_priority_if_present` |
| `agentic_core (real)` | `L0-GAP-002 priority` | contract | MEDIUM | all MEDIUM | `test_l0_gap002_is_medium_priority_if_present` |
| `agentic_core (real)` | `L1-GAP-001 priority` | contract | HIGH | all HIGH | `test_l1_gap001_is_high_priority_if_present` |
| `agentic_core (real)` | `L1-GAP-PROMPT priority` | contract | MEDIUM | all MEDIUM | `test_l1_gap_prompt_is_medium_priority_if_present` |
| `agentic_core (real)` | `L0 gaps evidence_files` | contract | non-empty | all non-empty | `test_all_l0_gaps_have_evidence_files` |
| `agentic_core (real)` | `L1 gaps evidence_files` | contract | non-empty | all non-empty | `test_all_l1_gaps_have_evidence_files` |

## ROBUSTNESS_MATRIX

| Surface | Ingress | Success IDs | Edge IDs | Failure IDs | Recovery IDs | Determinism IDs | Side-Effect IDs |
|---------|---------|-------------|----------|-------------|--------------|-----------------|-----------------|
| _analysis_mentions_cache | module + symbol hints | test_analysis_mentions_cache_module_hint_match, test_analysis_mentions_cache_symbol_hint_match | - | test_analysis_mentions_cache_no_match, test_analysis_mentions_cache_no_symbol_hint_module_absent | - | idempotent | none |
| analyze_l0_routing_gate | discovery_py + policy_engine existence + imports | test_discovery_py_no_cache_generates_l0_gap001, test_policy_engine_no_cache_generates_l0_gap002 | test_discovery_py_parse_fail_no_l0_gap001, test_policy_engine_parse_fail_no_l0_gap002 | test_discovery_py_with_module_cache_no_l0_gap001, test_policy_engine_with_cache_no_l0_gap002 | - | idempotent | none |
| analyze_l1_cognition | cognitive_engine + prompt files | test_cognitive_engine_no_cache_generates_l1_gap001, test_prompt_file_no_cache_generates_l1_gap_prompt | test_cognitive_engine_parse_fail_no_l1_gap001, test_prompt_file_parse_fail_no_l1_gap_prompt, test_no_prompt_files_no_l1_gap_prompt | test_prompt_file_with_cache_in_name_no_l1_gap_prompt, test_prompt_file_with_cache_import_no_l1_gap_prompt | - | idempotent | none |

## DEFECT_MODEL

| Defect Mechanism | Covered By |
|-----------------|------------|
| Parse-failed discovery_py generates L0-GAP-001 | test_discovery_py_parse_fail_no_l0_gap001 |
| Cache-importing file still generates L0-GAP-001 | test_discovery_py_with_module_cache_no_l0_gap001, test_discovery_py_with_symbol_cache_no_l0_gap001 |
| L0-GAP-001 priority not HIGH | test_l0_gap001_is_high_priority_if_present, test_discovery_py_no_cache_generates_l0_gap001 |
| L0-GAP-002 priority not MEDIUM | test_l0_gap002_is_medium_priority_if_present, test_policy_engine_no_cache_generates_l0_gap002 |
| L1-GAP-001 priority not HIGH | test_l1_gap001_is_high_priority_if_present, test_cognitive_engine_no_cache_generates_l1_gap001 |
| Prompt file with 'cache' in name wrongly flagged | test_prompt_file_with_cache_in_name_no_l1_gap_prompt |
| L1-GAP-PROMPT priority not MEDIUM | test_l1_gap_prompt_is_medium_priority_if_present, test_prompt_file_no_cache_generates_l1_gap_prompt |
| Gap missing evidence_files | test_all_l0_gaps_have_evidence_files, test_all_l1_gaps_have_evidence_files |

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

