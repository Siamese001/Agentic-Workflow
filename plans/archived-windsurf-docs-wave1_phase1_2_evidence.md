---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\wave1_phase1_2_evidence.md'
original_relative_path: 'wave1_phase1_2_evidence.md'
source_sha256: e301beeb708b711dd386f878373c5750b52d7c309bc1f6a855c84a3f1aa07815
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-05'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Wave 1 Phase 1.2 - Sovereignty: Direct Provider Import Detection Fix

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Scope

Fix direct provider import detection to eliminate 8 false-positive internal
agentic_core.*.vllm_* module flaggings. Add 24-test sovereignty branch suite.
N=2 files declared.

- tools/semantic_gap_analyzer.py
- tests/architecture/test_wave1_phase1_2_sovereignty.py

## CODE_COMMIT

445fdeab1

## EVIDENCE_COMMIT

e33f0277e

## FILES_CHANGED_CODE

```
tests/architecture/test_wave1_phase1_2_sovereignty.py
tools/semantic_gap_analyzer.py
```

## FILES_CHANGED_EVIDENCE

```
docs/reports/plans/wave1_phase1_2_evidence.md
tools/evidence/wave1_phase1_2_runner.py
```

## INSPECTED_FILES

- tools/semantic_gap_analyzer.py
- tests/architecture/test_wave1_phase1_2_sovereignty.py

## False-Positive Elimination Check

$ python -c '<false-positive elimination check>'
```
OK: shadow_router_classifier.py no false positives
OK: shadow_routing_types.py no false positives
OK: vllm_backpressure_types.py no false positives
OK: vllm_concurrency_types.py no false positives
OK: vllm_gateway_adapter_types.py no false positives
OK: vllm_gateway_integration_types.py no false positives
OK: vllm_invariant_verifier_types.py no false positives
OK: vllm_replay_validator_types.py no false positives
```

## Real Provider Import Detection

$ python -c '<real provider import detection>'
```
OK: healing_provider_adapters.py correctly flags openai
OK: qwen_vllm_inference.py correctly flags vllm
```

## Pytest - Phase 1.2 Tests

$ python -m pytest -q --color=no tests/architecture/test_wave1_phase1_2_sovereignty.py
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 24 items

tests/architecture/test_wave1_phase1_2_sovereignty.py::test_import_openai_flagged_as_direct_provider PASSED [  4%]
tests/architecture/test_wave1_phase1_2_sovereignty.py::test_import_vllm_flagged_as_direct_provider PASSED [  8%]
tests/architecture/test_wave1_phase1_2_sovereignty.py::test_import_vllm_submodule_flagged_as_direct_provider PASSED [ 12%]
tests/architecture/test_wave1_phase1_2_sovereignty.py::test_import_agentic_core_vllm_type_not_flagged PASSED [ 16%]
tests/architecture/test_wave1_phase1_2_sovereignty.py::test_import_anthropic_flagged PASSED [ 20%]
tests/architecture/test_wave1_phase1_2_sovereignty.py::test_import_litellm_flagged PASSED [ 25%]
tests/architecture/test_wave1_phase1_2_sovereignty.py::test_import_stdlib_not_flagged PASSED [ 29%]
tests/architecture/test_wave1_phase1_2_sovereignty.py::test_import_agentic_core_never_flagged PASSED [ 33%]
tests/architecture/test_wave1_phase1_2_sovereignty.py::test_from_openai_import_flagged PASSED [ 37%]
tests/architecture/test_wave1_phase1_2_sovereignty.py::test_from_vllm_import_flagged PASSED [ 41%]
tests/architecture/test_wave1_phase1_2_sovereignty.py::test_from_agentic_core_vllm_types_not_flagged PASSED [ 45%]
tests/architecture/test_wave1_phase1_2_sovereignty.py::test_from_agentic_core_vllm_infra_fingerprint_not_flagged PASSED [ 50%]
tests/architecture/test_wave1_phase1_2_sovereignty.py::test_google_generativeai_lazy_import_still_detected PASSED [ 54%]
tests/architecture/test_wave1_phase1_2_sovereignty.py::test_detect_upward_imports_l2_importing_l1_is_upward PASSED [ 58%]
tests/architecture/test_wave1_phase1_2_sovereignty.py::test_detect_upward_imports_l1_importing_l0_is_flagged PASSED [ 62%]
tests/architecture/test_wave1_phase1_2_sovereignty.py::test_detect_upward_imports_no_layer_returns_empty PASSED [ 66%]
tests/architecture/test_wave1_phase1_2_sovereignty.py::test_detect_upward_imports_no_refs_returns_empty PASSED [ 70%]
tests/architecture/test_wave1_phase1_2_sovereignty.py::test_detect_upward_imports_same_layer_not_upward PASSED [ 75%]
tests/architecture/test_wave1_phase1_2_sovereignty.py::test_detect_upward_imports_l2_importing_l3_is_not_flagged PASSED [ 79%]
tests/architecture/test_wave1_phase1_2_sovereignty.py::test_direct_provider_patterns_are_top_level_package_names PASSED [ 83%]
tests/architecture/test_wave1_phase1_2_sovereignty.py::test_direct_provider_patterns_does_not_contain_agentic_core PASSED [ 87%]
tests/architecture/test_wave1_phase1_2_sovereignty.py::test_no_real_provider_imports_outside_l2
-------------------------------- live log call --------------------------------
2026-03-05 23:12:33 [ WARNING] tools.semantic_gap_analyzer: Failed to parse C:\Git\Agentic-Workflow\agentic_core\L5_safety\reasoning\FileClassificationAgent.py: unexpected indent (FileClassificationAgent.py, line 2075)
PASSED                                                                   [ 91%]
tests/architecture/test_wave1_phase1_2_sovereignty.py::test_l2_real_provider_imports_are_in_expected_files PASSED [ 95%]
tests/architecture/test_wave1_phase1_2_sovereignty.py::test_internal_vllm_type_modules_produce_no_direct_provider_gap PASSED [100%]

============================ slowest 10 durations =============================
1.94s call     tests/architecture/test_wave1_phase1_2_sovereignty.py::test_no_real_provider_imports_outside_l2
0.26s call     tests/architecture/test_wave1_phase1_2_sovereignty.py::test_l2_real_provider_imports_are_in_expected_files
0.01s call     tests/architecture/test_wave1_phase1_2_sovereignty.py::test_internal_vllm_type_modules_produce_no_direct_provider_gap

(7 durations < 0.005s hidden.  Use -vv to show these durations.)
============================= 24 passed in 2.26s ==============================
```

collected 24 / executed 24

## BRANCH_INVENTORY

| File | Function | Branch Type | Condition | Expected | Test |
|------|----------|-------------|-----------|----------|------|
| `semantic_gap_analyzer.py` | `analyze_file (ast.Import)` | success | bare external SDK import | flagged | `test_import_openai_flagged_as_direct_provider` |
| `semantic_gap_analyzer.py` | `analyze_file (ast.Import)` | success | vllm top-level | flagged | `test_import_vllm_flagged_as_direct_provider` |
| `semantic_gap_analyzer.py` | `analyze_file (ast.Import)` | boundary | vllm.submodule prefix match | flagged | `test_import_vllm_submodule_flagged_as_direct_provider` |
| `semantic_gap_analyzer.py` | `analyze_file (ast.Import)` | negative | agentic_core.*.vllm_* internal | not flagged | `test_import_agentic_core_vllm_type_not_flagged` |
| `semantic_gap_analyzer.py` | `analyze_file (ast.Import)` | negative | agentic_core.* all internals | not flagged | `test_import_agentic_core_never_flagged` |
| `semantic_gap_analyzer.py` | `analyze_file (ast.Import)` | success | anthropic top-level | flagged | `test_import_anthropic_flagged` |
| `semantic_gap_analyzer.py` | `analyze_file (ast.Import)` | success | litellm top-level | flagged | `test_import_litellm_flagged` |
| `semantic_gap_analyzer.py` | `analyze_file (ast.Import)` | negative | stdlib import | not flagged | `test_import_stdlib_not_flagged` |
| `semantic_gap_analyzer.py` | `analyze_file (ast.ImportFrom)` | success | from openai import | flagged | `test_from_openai_import_flagged` |
| `semantic_gap_analyzer.py` | `analyze_file (ast.ImportFrom)` | boundary | from vllm import | flagged | `test_from_vllm_import_flagged` |
| `semantic_gap_analyzer.py` | `analyze_file (ast.ImportFrom)` | negative | from agentic_core...vllm_types import | not flagged | `test_from_agentic_core_vllm_types_not_flagged` |
| `semantic_gap_analyzer.py` | `analyze_file (ast.ImportFrom)` | negative | vllm_infrastructure_fingerprint regression | not flagged | `test_from_agentic_core_vllm_infra_fingerprint_not_flagged` |
| `semantic_gap_analyzer.py` | `analyze_file (ast.Import)` | boundary | lazy google.generativeai in function body | flagged (AST walks all nodes) | `test_google_generativeai_lazy_import_still_detected` |
| `semantic_gap_analyzer.py` | `_detect_upward_imports` | negative | L2 file imports L1 (rank 1 < 2) | violation reported | `test_detect_upward_imports_l2_importing_l1_is_upward` |
| `semantic_gap_analyzer.py` | `_detect_upward_imports` | contract | L1 imports L0 flagged by lower-rank rule | reported | `test_detect_upward_imports_l1_importing_l0_is_flagged` |
| `semantic_gap_analyzer.py` | `_detect_upward_imports` | boundary | non-layer file returns empty list | empty | `test_detect_upward_imports_no_layer_returns_empty` |
| `semantic_gap_analyzer.py` | `_detect_upward_imports` | boundary | empty imported_layer_refs | empty | `test_detect_upward_imports_no_refs_returns_empty` |
| `semantic_gap_analyzer.py` | `_detect_upward_imports` | boundary | same-layer import (L2->L2) | not flagged | `test_detect_upward_imports_same_layer_not_upward` |
| `semantic_gap_analyzer.py` | `_detect_upward_imports` | boundary | L2 imports L3 (rank 3 > 2) | not flagged | `test_detect_upward_imports_l2_importing_l3_is_not_flagged` |
| `semantic_gap_analyzer.py` | `DIRECT_PROVIDER_IMPORT_PATTERNS` | contract | all patterns are strings | non-empty strings | `test_direct_provider_patterns_are_top_level_package_names` |
| `semantic_gap_analyzer.py` | `DIRECT_PROVIDER_IMPORT_PATTERNS` | invariant | no agentic_core in patterns | invariant holds | `test_direct_provider_patterns_does_not_contain_agentic_core` |
| `agentic_core (real)` | `L0/L1/L3/L4/L5/L6 files` | codebase-invariant | no provider SDK imports outside L2 | zero violations | `test_no_real_provider_imports_outside_l2` |
| `agentic_core (real)` | `L2_execution adapter files` | codebase-success | known adapters have correct SDKs | healing_provider_adapters + qwen_vllm | `test_l2_real_provider_imports_are_in_expected_files` |
| `agentic_core (real)` | `vllm_* type files` | regression | 8 false-positive files produce zero flags | zero | `test_internal_vllm_type_modules_produce_no_direct_provider_gap` |

## ROBUSTNESS_MATRIX

| Surface | Ingress | Success IDs | Edge IDs | Failure IDs | Recovery IDs | Determinism IDs | Side-Effect IDs |
|---------|---------|-------------|----------|-------------|--------------|-----------------|-----------------|
| ast.Import provider detection | analyze_file AST walk | test_import_openai_flagged, test_import_vllm_flagged, test_import_anthropic_flagged, test_import_litellm_flagged | test_import_vllm_submodule_flagged, test_google_generativeai_lazy_import | test_import_agentic_core_vllm_type_not_flagged, test_import_agentic_core_never_flagged, test_import_stdlib_not_flagged | - | idempotent: same file same result | read-only |
| ast.ImportFrom provider detection | analyze_file AST walk | test_from_openai_import_flagged, test_from_vllm_import_flagged | test_from_vllm_import_flagged | test_from_agentic_core_vllm_types_not_flagged, test_from_agentic_core_vllm_infra_fingerprint_not_flagged | - | idempotent | read-only |
| _detect_upward_imports | _detect_upward_imports(path, analysis) | test_detect_upward_imports_l2_importing_l1_is_upward | test_detect_upward_imports_no_layer_returns_empty, test_detect_upward_imports_no_refs_returns_empty, test_detect_upward_imports_same_layer_not_upward, test_detect_upward_imports_l2_importing_l3_is_not_flagged | - | - | test_detect_upward_imports_l1_importing_l0_is_flagged | read-only |
| Codebase invariants | full L0-L6 rglob scan | test_no_real_provider_imports_outside_l2, test_l2_real_provider_imports_are_in_expected_files | test_internal_vllm_type_modules_produce_no_direct_provider_gap | - | - | deterministic file scan | read-only |

## DEFECT_MODEL

| Defect Mechanism | Covered By |
|-----------------|------------|
| Substring match 'vllm' in internal module path causes false positive | test_import_agentic_core_vllm_type_not_flagged, test_from_agentic_core_vllm_infra_fingerprint_not_flagged, test_internal_vllm_type_modules_produce_no_direct_provider_gap |
| Missing dotted-prefix match drops google.generativeai detection | test_google_generativeai_lazy_import_still_detected |
| Guard omission: internal imports escape agentic_core.* guard | test_import_agentic_core_never_flagged, test_from_agentic_core_vllm_types_not_flagged |
| Off-by-one: same-layer imports wrongly flagged as upward | test_detect_upward_imports_same_layer_not_upward |
| Hidden fallback: missing layer returns non-empty violation list | test_detect_upward_imports_no_layer_returns_empty |
| Duplicate mutation: non-L2 provider SDK imports go undetected | test_no_real_provider_imports_outside_l2 |

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

