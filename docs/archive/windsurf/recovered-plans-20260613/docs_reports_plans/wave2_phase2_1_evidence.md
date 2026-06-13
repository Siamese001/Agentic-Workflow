# Wave 2 Phase 2.1 - Advanced Governance: Full Stamp Coverage

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

Add 28-test branch-coverage suite for analyze_layer_connection_integrity.
Covers: LAYER-UPWARD-IMPORT, GATEWAY-BYPASS-RISK, NON-L2-MUTATION-RISK,
PATHD-PLAN-HASH-GAP, findings accumulation, real codebase invariants.
No analyzer code changes. N=1 file declared.

- tests/architecture/test_wave2_phase2_1_advanced_governance.py

## CODE_COMMIT

ec0d2e144

## EVIDENCE_COMMIT

5c0f8414c

## FILES_CHANGED_CODE

```
tests/architecture/test_wave2_phase2_1_advanced_governance.py
```

## FILES_CHANGED_EVIDENCE

```
docs/reports/plans/wave2_phase2_1_evidence.md
tools/evidence/wave2_phase2_1_runner.py
```

## INSPECTED_FILES

- tests/architecture/test_wave2_phase2_1_advanced_governance.py

## Pytest - Phase 2.1 Tests

$ python -m pytest -q --color=no tests/architecture/test_wave2_phase2_1_advanced_governance.py
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 28 items

tests/architecture/test_wave2_phase2_1_advanced_governance.py::test_upward_import_generates_layer_upward_import_gap
-------------------------------- live log call --------------------------------
2026-03-05 23:23:54 [    INFO] tools.semantic_gap_analyzer: Analyzing Layer Connection Integrity...
PASSED                                                                   [  3%]
tests/architecture/test_wave2_phase2_1_advanced_governance.py::test_no_upward_import_produces_no_upward_gap
-------------------------------- live log call --------------------------------
2026-03-05 23:23:54 [    INFO] tools.semantic_gap_analyzer: Analyzing Layer Connection Integrity...
PASSED                                                                   [  7%]
tests/architecture/test_wave2_phase2_1_advanced_governance.py::test_same_layer_import_produces_no_upward_gap
-------------------------------- live log call --------------------------------
2026-03-05 23:23:54 [    INFO] tools.semantic_gap_analyzer: Analyzing Layer Connection Integrity...
PASSED                                                                   [ 10%]
tests/architecture/test_wave2_phase2_1_advanced_governance.py::test_higher_layer_import_produces_no_upward_gap
-------------------------------- live log call --------------------------------
2026-03-05 23:23:54 [    INFO] tools.semantic_gap_analyzer: Analyzing Layer Connection Integrity...
PASSED                                                                   [ 14%]
tests/architecture/test_wave2_phase2_1_advanced_governance.py::test_direct_provider_import_generates_gateway_bypass_risk
-------------------------------- live log call --------------------------------
2026-03-05 23:23:54 [    INFO] tools.semantic_gap_analyzer: Analyzing Layer Connection Integrity...
PASSED                                                                   [ 17%]
tests/architecture/test_wave2_phase2_1_advanced_governance.py::test_no_provider_import_generates_no_gateway_bypass_gap
-------------------------------- live log call --------------------------------
2026-03-05 23:23:54 [    INFO] tools.semantic_gap_analyzer: Analyzing Layer Connection Integrity...
PASSED                                                                   [ 21%]
tests/architecture/test_wave2_phase2_1_advanced_governance.py::test_sovereign_llm_gateway_excluded_from_gateway_bypass_gap
-------------------------------- live log call --------------------------------
2026-03-05 23:23:54 [    INFO] tools.semantic_gap_analyzer: Analyzing Layer Connection Integrity...
PASSED                                                                   [ 25%]
tests/architecture/test_wave2_phase2_1_advanced_governance.py::test_gateway_bypass_gap_lists_provider_in_reality
-------------------------------- live log call --------------------------------
2026-03-05 23:23:54 [    INFO] tools.semantic_gap_analyzer: Analyzing Layer Connection Integrity...
PASSED                                                                   [ 28%]
tests/architecture/test_wave2_phase2_1_advanced_governance.py::test_l0_file_with_write_paths_generates_mutation_risk
-------------------------------- live log call --------------------------------
2026-03-05 23:23:54 [    INFO] tools.semantic_gap_analyzer: Analyzing Layer Connection Integrity...
PASSED                                                                   [ 32%]
tests/architecture/test_wave2_phase2_1_advanced_governance.py::test_l3_file_with_write_paths_generates_mutation_risk
-------------------------------- live log call --------------------------------
2026-03-05 23:23:54 [    INFO] tools.semantic_gap_analyzer: Analyzing Layer Connection Integrity...
PASSED                                                                   [ 35%]
tests/architecture/test_wave2_phase2_1_advanced_governance.py::test_l5_file_with_write_paths_generates_mutation_risk
-------------------------------- live log call --------------------------------
2026-03-05 23:23:54 [    INFO] tools.semantic_gap_analyzer: Analyzing Layer Connection Integrity...
PASSED                                                                   [ 39%]
tests/architecture/test_wave2_phase2_1_advanced_governance.py::test_l2_file_with_write_paths_does_not_generate_mutation_risk
-------------------------------- live log call --------------------------------
2026-03-05 23:23:54 [    INFO] tools.semantic_gap_analyzer: Analyzing Layer Connection Integrity...
PASSED                                                                   [ 42%]
tests/architecture/test_wave2_phase2_1_advanced_governance.py::test_l1_file_with_write_paths_does_not_generate_mutation_risk
-------------------------------- live log call --------------------------------
2026-03-05 23:23:54 [    INFO] tools.semantic_gap_analyzer: Analyzing Layer Connection Integrity...
PASSED                                                                   [ 46%]
tests/architecture/test_wave2_phase2_1_advanced_governance.py::test_l0_file_with_empty_write_paths_no_mutation_gap
-------------------------------- live log call --------------------------------
2026-03-05 23:23:54 [    INFO] tools.semantic_gap_analyzer: Analyzing Layer Connection Integrity...
PASSED                                                                   [ 50%]
tests/architecture/test_wave2_phase2_1_advanced_governance.py::test_path_d_file_without_plan_hash_generates_pathd_gap
-------------------------------- live log call --------------------------------
2026-03-05 23:23:54 [    INFO] tools.semantic_gap_analyzer: Analyzing Layer Connection Integrity...
PASSED                                                                   [ 53%]
tests/architecture/test_wave2_phase2_1_advanced_governance.py::test_path_d_file_with_plan_hash_no_pathd_gap
-------------------------------- live log call --------------------------------
2026-03-05 23:23:54 [    INFO] tools.semantic_gap_analyzer: Analyzing Layer Connection Integrity...
PASSED                                                                   [ 57%]
tests/architecture/test_wave2_phase2_1_advanced_governance.py::test_hitl_in_path_generates_pathd_gap_even_without_mentions
-------------------------------- live log call --------------------------------
2026-03-05 23:23:54 [    INFO] tools.semantic_gap_analyzer: Analyzing Layer Connection Integrity...
PASSED                                                                   [ 60%]
tests/architecture/test_wave2_phase2_1_advanced_governance.py::test_no_path_d_no_hitl_no_pathd_gap
-------------------------------- live log call --------------------------------
2026-03-05 23:23:54 [    INFO] tools.semantic_gap_analyzer: Analyzing Layer Connection Integrity...
PASSED                                                                   [ 64%]
tests/architecture/test_wave2_phase2_1_advanced_governance.py::test_layer_connection_finding_keys_are_present
-------------------------------- live log call --------------------------------
2026-03-05 23:23:54 [    INFO] tools.semantic_gap_analyzer: Analyzing Layer Connection Integrity...
PASSED                                                                   [ 67%]
tests/architecture/test_wave2_phase2_1_advanced_governance.py::test_parse_failed_file_not_added_to_findings
-------------------------------- live log call --------------------------------
2026-03-05 23:23:54 [    INFO] tools.semantic_gap_analyzer: Analyzing Layer Connection Integrity...
PASSED                                                                   [ 71%]
tests/architecture/test_wave2_phase2_1_advanced_governance.py::test_healing_provider_adapters_generates_gateway_bypass_risk
-------------------------------- live log call --------------------------------
2026-03-05 23:23:54 [    INFO] tools.semantic_gap_analyzer: Analyzing Layer Connection Integrity...
2026-03-05 23:23:56 [ WARNING] tools.semantic_gap_analyzer: Failed to parse C:\Git\Agentic-Workflow\agentic_core\L5_safety\reasoning\FileClassificationAgent.py: unexpected indent (FileClassificationAgent.py, line 2075)
PASSED                                                                   [ 75%]
tests/architecture/test_wave2_phase2_1_advanced_governance.py::test_qwen_vllm_inference_generates_gateway_bypass_risk
-------------------------------- live log call --------------------------------
2026-03-05 23:23:56 [    INFO] tools.semantic_gap_analyzer: Analyzing Layer Connection Integrity...
2026-03-05 23:23:58 [ WARNING] tools.semantic_gap_analyzer: Failed to parse C:\Git\Agentic-Workflow\agentic_core\L5_safety\reasoning\FileClassificationAgent.py: unexpected indent (FileClassificationAgent.py, line 2075)
PASSED                                                                   [ 78%]
tests/architecture/test_wave2_phase2_1_advanced_governance.py::test_sovereign_llm_gateway_not_in_gateway_bypass_gaps
-------------------------------- live log call --------------------------------
2026-03-05 23:23:59 [    INFO] tools.semantic_gap_analyzer: Analyzing Layer Connection Integrity...
2026-03-05 23:24:01 [ WARNING] tools.semantic_gap_analyzer: Failed to parse C:\Git\Agentic-Workflow\agentic_core\L5_safety\reasoning\FileClassificationAgent.py: unexpected indent (FileClassificationAgent.py, line 2075)
PASSED                                                                   [ 82%]
tests/architecture/test_wave2_phase2_1_advanced_governance.py::test_layer_connection_integrity_returns_list
-------------------------------- live log call --------------------------------
2026-03-05 23:24:02 [    INFO] tools.semantic_gap_analyzer: Analyzing Layer Connection Integrity...
2026-03-05 23:24:03 [ WARNING] tools.semantic_gap_analyzer: Failed to parse C:\Git\Agentic-Workflow\agentic_core\L5_safety\reasoning\FileClassificationAgent.py: unexpected indent (FileClassificationAgent.py, line 2075)
PASSED                                                                   [ 85%]
tests/architecture/test_wave2_phase2_1_advanced_governance.py::test_gateway_bypass_gaps_are_all_high_priority
-------------------------------- live log call --------------------------------
2026-03-05 23:24:04 [    INFO] tools.semantic_gap_analyzer: Analyzing Layer Connection Integrity...
2026-03-05 23:24:06 [ WARNING] tools.semantic_gap_analyzer: Failed to parse C:\Git\Agentic-Workflow\agentic_core\L5_safety\reasoning\FileClassificationAgent.py: unexpected indent (FileClassificationAgent.py, line 2075)
PASSED                                                                   [ 89%]
tests/architecture/test_wave2_phase2_1_advanced_governance.py::test_non_l2_mutation_risk_gaps_are_all_medium_priority
-------------------------------- live log call --------------------------------
2026-03-05 23:24:07 [    INFO] tools.semantic_gap_analyzer: Analyzing Layer Connection Integrity...
2026-03-05 23:24:09 [ WARNING] tools.semantic_gap_analyzer: Failed to parse C:\Git\Agentic-Workflow\agentic_core\L5_safety\reasoning\FileClassificationAgent.py: unexpected indent (FileClassificationAgent.py, line 2075)
PASSED                                                                   [ 92%]
tests/architecture/test_wave2_phase2_1_advanced_governance.py::test_upward_import_gaps_are_all_high_priority
-------------------------------- live log call --------------------------------
2026-03-05 23:24:09 [    INFO] tools.semantic_gap_analyzer: Analyzing Layer Connection Integrity...
2026-03-05 23:24:11 [ WARNING] tools.semantic_gap_analyzer: Failed to parse C:\Git\Agentic-Workflow\agentic_core\L5_safety\reasoning\FileClassificationAgent.py: unexpected indent (FileClassificationAgent.py, line 2075)
PASSED                                                                   [ 96%]
tests/architecture/test_wave2_phase2_1_advanced_governance.py::test_pathd_gaps_are_all_high_priority
-------------------------------- live log call --------------------------------
2026-03-05 23:24:12 [    INFO] tools.semantic_gap_analyzer: Analyzing Layer Connection Integrity...
2026-03-05 23:24:14 [ WARNING] tools.semantic_gap_analyzer: Failed to parse C:\Git\Agentic-Workflow\agentic_core\L5_safety\reasoning\FileClassificationAgent.py: unexpected indent (FileClassificationAgent.py, line 2075)
PASSED                                                                   [100%]

============================ slowest 10 durations =============================
2.66s call     tests/architecture/test_wave2_phase2_1_advanced_governance.py::test_qwen_vllm_inference_generates_gateway_bypass_risk
2.66s call     tests/architecture/test_wave2_phase2_1_advanced_governance.py::test_healing_provider_adapters_generates_gateway_bypass_risk
2.66s call     tests/architecture/test_wave2_phase2_1_advanced_governance.py::test_sovereign_llm_gateway_not_in_gateway_bypass_gaps
2.57s call     tests/architecture/test_wave2_phase2_1_advanced_governance.py::test_upward_import_gaps_are_all_high_priority
2.57s call     tests/architecture/test_wave2_phase2_1_advanced_governance.py::test_layer_connection_integrity_returns_list
2.57s call     tests/architecture/test_wave2_phase2_1_advanced_governance.py::test_pathd_gaps_are_all_high_priority
2.54s call     tests/architecture/test_wave2_phase2_1_advanced_governance.py::test_gateway_bypass_gaps_are_all_high_priority
2.54s call     tests/architecture/test_wave2_phase2_1_advanced_governance.py::test_non_l2_mutation_risk_gaps_are_all_medium_priority

(2 durations < 0.005s hidden.  Use -vv to show these durations.)
============================= 28 passed in 20.80s =============================
```

collected 28 / executed 28

## BRANCH_INVENTORY

| File | Function | Branch Type | Condition | Expected | Test |
|------|----------|-------------|-----------|----------|------|
| `semantic_gap_analyzer.py` | `analyze_layer_connection_integrity` | success | L2 file with L1 upward import ref | LAYER-UPWARD-IMPORT generated | `test_upward_import_generates_layer_upward_import_gap` |
| `semantic_gap_analyzer.py` | `analyze_layer_connection_integrity` | negative | file with empty imported_layer_refs | no LAYER-UPWARD-IMPORT | `test_no_upward_import_produces_no_upward_gap` |
| `semantic_gap_analyzer.py` | `analyze_layer_connection_integrity` | boundary | L2 importing L2 (same rank) | no upward gap | `test_same_layer_import_produces_no_upward_gap` |
| `semantic_gap_analyzer.py` | `analyze_layer_connection_integrity` | boundary | L2 importing L3 (higher rank) | no upward gap | `test_higher_layer_import_produces_no_upward_gap` |
| `semantic_gap_analyzer.py` | `analyze_layer_connection_integrity` | success | non-gateway file with provider import | GATEWAY-BYPASS-RISK generated | `test_direct_provider_import_generates_gateway_bypass_risk` |
| `semantic_gap_analyzer.py` | `analyze_layer_connection_integrity` | negative | file with no provider imports | no GATEWAY-BYPASS-RISK | `test_no_provider_import_generates_no_gateway_bypass_gap` |
| `semantic_gap_analyzer.py` | `analyze_layer_connection_integrity` | allowlist | SovereignLLMGateway.py with provider imports | excluded from GATEWAY-BYPASS-RISK | `test_sovereign_llm_gateway_excluded_from_gateway_bypass_gap` |
| `semantic_gap_analyzer.py` | `analyze_layer_connection_integrity` | contract | GATEWAY-BYPASS-RISK reality field | provider name in reality | `test_gateway_bypass_gap_lists_provider_in_reality` |
| `semantic_gap_analyzer.py` | `analyze_layer_connection_integrity` | success | L0 file with write_paths | NON-L2-MUTATION-RISK generated | `test_l0_file_with_write_paths_generates_mutation_risk` |
| `semantic_gap_analyzer.py` | `analyze_layer_connection_integrity` | success | L3 file with write_paths | NON-L2-MUTATION-RISK generated | `test_l3_file_with_write_paths_generates_mutation_risk` |
| `semantic_gap_analyzer.py` | `analyze_layer_connection_integrity` | success | L5 file with write_paths | NON-L2-MUTATION-RISK generated | `test_l5_file_with_write_paths_generates_mutation_risk` |
| `semantic_gap_analyzer.py` | `analyze_layer_connection_integrity` | negative | L2 file with write_paths (allowed layer) | no NON-L2-MUTATION-RISK | `test_l2_file_with_write_paths_does_not_generate_mutation_risk` |
| `semantic_gap_analyzer.py` | `analyze_layer_connection_integrity` | negative | L1 file with write_paths (not flagged) | no NON-L2-MUTATION-RISK | `test_l1_file_with_write_paths_does_not_generate_mutation_risk` |
| `semantic_gap_analyzer.py` | `analyze_layer_connection_integrity` | boundary | L0 with empty write_paths list | no mutation gap | `test_l0_file_with_empty_write_paths_no_mutation_gap` |
| `semantic_gap_analyzer.py` | `analyze_layer_connection_integrity` | success | path_d_mentions without original_plan_hash | PATHD-PLAN-HASH-GAP generated | `test_path_d_file_without_plan_hash_generates_pathd_gap` |
| `semantic_gap_analyzer.py` | `analyze_layer_connection_integrity` | negative | path_d_mentions WITH original_plan_hash | no PATHD-PLAN-HASH-GAP | `test_path_d_file_with_plan_hash_no_pathd_gap` |
| `semantic_gap_analyzer.py` | `analyze_layer_connection_integrity` | success | hitl in file path triggers PATHD gap | PATHD-PLAN-HASH-GAP generated | `test_hitl_in_path_generates_pathd_gap_even_without_mentions` |
| `semantic_gap_analyzer.py` | `analyze_layer_connection_integrity` | negative | no path_d/hitl markers | no PATHD-PLAN-HASH-GAP | `test_no_path_d_no_hitl_no_pathd_gap` |
| `semantic_gap_analyzer.py` | `analyze_layer_connection_integrity` | contract | findings dict has required keys | all keys present | `test_layer_connection_finding_keys_are_present` |
| `semantic_gap_analyzer.py` | `analyze_layer_connection_integrity` | boundary | parse-failed file skipped | not in findings | `test_parse_failed_file_not_added_to_findings` |
| `agentic_core (real)` | `healing_provider_adapters.py` | codebase-success | openai import -> GATEWAY-BYPASS-RISK | in gap evidence_files | `test_healing_provider_adapters_generates_gateway_bypass_risk` |
| `agentic_core (real)` | `qwen_vllm_inference.py` | codebase-success | vllm import -> GATEWAY-BYPASS-RISK | in gap evidence_files | `test_qwen_vllm_inference_generates_gateway_bypass_risk` |
| `agentic_core (real)` | `SovereignLLMGateway.py` | codebase-invariant | excluded from GATEWAY-BYPASS-RISK | never in gap evidence | `test_sovereign_llm_gateway_not_in_gateway_bypass_gaps` |
| `semantic_gap_analyzer.py` | `analyze_layer_connection_integrity` | integration | returns list without exception | list type | `test_layer_connection_integrity_returns_list` |
| `semantic_gap_analyzer.py` | `GATEWAY-BYPASS-RISK priority` | contract | all gaps are HIGH | all HIGH | `test_gateway_bypass_gaps_are_all_high_priority` |
| `semantic_gap_analyzer.py` | `NON-L2-MUTATION-RISK priority` | contract | all gaps are MEDIUM | all MEDIUM | `test_non_l2_mutation_risk_gaps_are_all_medium_priority` |
| `semantic_gap_analyzer.py` | `LAYER-UPWARD-IMPORT priority` | contract | all gaps are HIGH | all HIGH | `test_upward_import_gaps_are_all_high_priority` |
| `semantic_gap_analyzer.py` | `PATHD-PLAN-HASH-GAP priority` | contract | all gaps are HIGH | all HIGH | `test_pathd_gaps_are_all_high_priority` |

## ROBUSTNESS_MATRIX

| Surface | Ingress | Success IDs | Edge IDs | Failure IDs | Recovery IDs | Determinism IDs | Side-Effect IDs |
|---------|---------|-------------|----------|-------------|--------------|-----------------|-----------------|
| LAYER-UPWARD-IMPORT | _detect_upward_imports result | test_upward_import_generates_layer_upward_import_gap | test_same_layer_import_produces_no_upward_gap, test_higher_layer_import_produces_no_upward_gap | test_no_upward_import_produces_no_upward_gap | - | idempotent | read-only |
| GATEWAY-BYPASS-RISK | direct_provider_imports set | test_direct_provider_import_generates_gateway_bypass_risk, test_gateway_bypass_gap_lists_provider_in_reality | - | test_no_provider_import_generates_no_gateway_bypass_gap | test_sovereign_llm_gateway_excluded_from_gateway_bypass_gap | idempotent | read-only |
| NON-L2-MUTATION-RISK | write_paths list + source_layer | test_l0_file_with_write_paths_generates_mutation_risk, test_l3_file_with_write_paths_generates_mutation_risk, test_l5_file_with_write_paths_generates_mutation_risk | test_l0_file_with_empty_write_paths_no_mutation_gap | test_l2_file_with_write_paths_does_not_generate_mutation_risk, test_l1_file_with_write_paths_does_not_generate_mutation_risk | - | idempotent | read-only |
| PATHD-PLAN-HASH-GAP | path_d_mentions + rel path | test_path_d_file_without_plan_hash_generates_pathd_gap, test_hitl_in_path_generates_pathd_gap_even_without_mentions | - | test_path_d_file_with_plan_hash_no_pathd_gap, test_no_path_d_no_hitl_no_pathd_gap | - | idempotent | read-only |
| findings accumulation | per-file loop | test_layer_connection_finding_keys_are_present | test_parse_failed_file_not_added_to_findings | - | - | idempotent | append to list |

## DEFECT_MODEL

| Defect Mechanism | Covered By |
|-----------------|------------|
| SovereignLLMGateway.py wrongly flagged as bypass risk | test_sovereign_llm_gateway_excluded_from_gateway_bypass_gap, test_sovereign_llm_gateway_not_in_gateway_bypass_gaps |
| L2 mutation wrongly flagged (allowed layer) | test_l2_file_with_write_paths_does_not_generate_mutation_risk |
| Same-layer import wrongly flagged as upward | test_same_layer_import_produces_no_upward_gap |
| Higher-rank import wrongly flagged as upward | test_higher_layer_import_produces_no_upward_gap |
| PATHD gap suppressed when plan hash present | test_path_d_file_with_plan_hash_no_pathd_gap |
| PATHD gap missing for hitl path with no explicit mentions | test_hitl_in_path_generates_pathd_gap_even_without_mentions |
| Parse-failed file adds finding to results | test_parse_failed_file_not_added_to_findings |
| Finding dict missing required governance keys | test_layer_connection_finding_keys_are_present |
| Priority regression: GATEWAY-BYPASS-RISK not HIGH | test_gateway_bypass_gaps_are_all_high_priority |
| Priority regression: NON-L2-MUTATION-RISK not MEDIUM | test_non_l2_mutation_risk_gaps_are_all_medium_priority |

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

