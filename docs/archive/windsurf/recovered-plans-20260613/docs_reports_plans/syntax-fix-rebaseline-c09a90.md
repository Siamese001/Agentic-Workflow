# Detailed Syntax Recovery Plan: Combined Wave Execution (v2)

This plan outlines 34 combined waves of ≤50 files each to fix 1,656 broken test files across four corruption patterns.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Ground Truth (Mar 26, 2026)
- **Total test files:** 3,031
- **Broken files:** 1,656
- **Fix rate:** ~6.6% (Based on Wave 1/2 performance)
- **Context Window:** 200K (50 files/wave is <30% usage)

## Phase 1: Infrastructure & Script Finalization
- **Objective:** Finalize `tools/wave_combined_fix.py` to handle all four patterns in a single pass.
- **Fix Patterns:**
    - **A (MOVED):** Remove `# # MOVED:` blocks + orphaned `from...import (` lines.
    - **B (Stub):** Re-indent method stubs (docstrings/bodies) to match parent `def`.
    - **C (Empty):** Insert `pass` in empty `def`, `if`, `try`, `except` blocks.
    - **D (Misc):** Handle unmatched parentheses and trailing delimiters.

## Phase 2: Combined Wave Alignment Table

| Wave | Count | Patterns | First File | Last File |
|------|-------|----------|------------|-----------|
| 1 | 50 | A | test_accelerator_wiring.py | test_memory_mcp_adapter.py |
| 2 | 50 | A | test_meta_learning_bus_creative.py | test_hitl_lifecycle_e2e.py |
| 3 | 50 | A | test_ssot_report_storage_e2e.py | test_oscillation_detector_wiring_invariant.py |
| 4 | 50 | A | test_oscillation_freeze.py | test_gravity_validator_hardened.py |
| 5 | 50 | A | test_guardian_aggregation.py | test_replay_key_determinism.py |
| 6 | 50 | A | test_artifact_writers.py | test_healing_confidence.py |
| 7 | 50 | A | test_location_agent_heal.py | test_mcp_client.py |
| 8 | 50 | A | test_schema.py | test_reasoning.py |
| 9 | 50 | A | test_scan_testing_compliance_util.py | test_result_types_adg.py |
| 10 | 50 | A | test_consensus_validator_adg.py | test_kv_cache_headroom_under_concurrency.py |
| 11 | 50 | A | test_l2_phase_spec_adg.py | test_in_memory_vector_cache.py |
| 12 | 50 | A | test_runtime_state_guard_adg.py | test_ssot_scanner_enforcer_adg.py |
| 13 | 50 | A | test_structural_namespace_fence_enforcer.py | test_chaos_healing_integration_types_adg.py |
| 14 | 50 | A | test_code_validator_facade.py | test_healer_exceptions_adg.py |
| 15 | 50 | A | test_runtime_exceptions_adg.py | test_import_boundary_contract.py |
| 16 | 50 | A | test_import_graph_contract.py | test_vllm_contracts.py |
| 17 | 50 | A, B | test_vllm_replay.py | test_base_eval_engine_mixins.py |
| 18 | 50 | B, C | test_base_exec_engine_mixins.py | test_novel_infrastructure_validation.py |
| 19 | 50 | C | test___init___adg.py | test_L6ObservabilityBase_adg.py |
| 20 | 50 | C | test_SovereignBaseAgent.py | test_runtime_guard.py |
| 21 | 50 | C | test_runtime_mutation_guard_adg.py | test_function_tool_adg.py |
| 22 | 50 | C | test_handler_adg.py | test_capability_analyzer_adg.py |
| 23 | 50 | C | test_cognitive_engine_adg.py | test_healing_tier_dispatcher_adg.py |
| 24 | 50 | C | test_healing_tier_router_adg.py | test_tool_args_types_adg.py |
| 25 | 50 | C | test_tool_intent_types_adg.py | test_code_validator_runner_adg.py |
| 26 | 50 | C | test_orchestrator_runner_adg.py | test___init___adg.py |
| 27 | 50 | C | test_discovery_parser_util_adg.py | test_enforce_execution_policy_adg.py |
| 28 | 50 | C | test_invoke_message_service_adg.py | test_manage_false_positives.py |
| 29 | 50 | C | test_refactor_agents_to_subatomic.py | test_unified_signal_pipeline_util.py |
| 30 | 50 | C | test_unified_signal_pipeline_util_adg.py | test_section_balance_agent.py |
| 31 | 50 | C, D | test_type_classification_agent_wins.py | test_plan3_agentic_rag_hardening.py |
| 32 | 50 | D | test_prompt_governance_coverage.py | test_integration_layer.py |
| 33 | 50 | D | test_l4_state_lifecycle.py | test_violation_event.py |
| 34 | 6 | D | test_protected_root_invariant_ast.py | test_write_gateway_guards_original.py |

## Phase 3: Final Validation
- Full scan with `tools/fast_file_analysis.py`
- `pytest --collect-only` verification
- Manual mop-up for remaining SyntaxErrors

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

