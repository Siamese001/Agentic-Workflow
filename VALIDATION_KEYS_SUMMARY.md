# Agentic L5 Validation Summary
- **Run ID**: `b4067536`
- **Timestamp**: 2025-11-29T19:22:20Z
- **Total Checks**: 38

## Results by Category

### Structure
- ✅ **max_depth_respected**: `PASS`
  - Depth 5 (limit 12)
- ❌ **no_empty_directories**: `FAIL`
  - Empty dirs 5 (limit 0)

### Layer Purity
- ❌ **l1_planning_purity**: `FAIL`
  - 3 violations
  - **Details**:
    ```
    lic_instructional_injection_v6.py: SyntaxError line 487: unterminated triple-quoted string literal (detected at line 497)
    ```
    ```
    strategy_planning.py:30 Import 'agentic_core.l5_safety.safety_policy.injection_detection' forbidden
    ```
    ```
    strategy_planning.py:32 Import 'agentic_core.l5_safety.safety_policy.policy' forbidden
    ```
- ❌ **l2_execution_purity**: `FAIL`
  - 27 violations
  - **Details**:
    ```
    lic_company_research_executor.py:10 Import 'agentic_core.l4_memory_state.temporal.hybrid_search' forbidden
    ```
    ```
    lic_company_research_executor.py:11 Import 'agentic_core.l4_memory_state.schema.outreach_schema' forbidden
    ```
    ```
    lic_company_research_executor.py:16 Import 'agentic_core.l1_planning.planners.lic_outreach_dataclasses' forbidden
    ```
    ```
    lic_contact_research_executor.py:10 Import 'agentic_core.l4_memory_state.temporal.hybrid_search' forbidden
    ```
    ```
    lic_contact_research_executor.py:11 Import 'agentic_core.l4_memory_state.schema.outreach_schema' forbidden
    ```
    ```
    lic_contact_research_executor.py:12 Import 'agentic_core.l1_planning.planners.lic_outreach_dataclasses' forbidden
    ```
    ```
    lic_kg_retrieval_executor.py:15 Import 'agentic_core.l1_planning.planners.lic_kg_retrieval_planning' forbidden
    ```
    ```
    lic_kg_retrieval_executor.py:21 Import 'agentic_core.l4_memory_state.temporal.triplet_store' forbidden
    ```
    ```
    lic_kg_retrieval_executor.py:437 Import 'agentic_core.l1_planning.planners.lic_kg_retrieval_planning' forbidden
    ```
    ```
    lic_kg_retrieval_executor.py:461 Import 'agentic_core.l1_planning.planners.lic_kg_retrieval_planning' forbidden
    ```
    ```
    message_generation_executor.py:9 Import 'agentic_core.l4_memory_state.schema.outreach_schema' forbidden
    ```
    ```
    message_generation_executor.py:270 Import 'agentic_core.l1_planning.planners.lic_outreach_dataclasses' forbidden
    ```
    ```
    triplet_extraction_executor.py:16 Import 'agentic_core.l4_memory_state.temporal.triplet_store' forbidden
    ```
    ```
    triplet_extraction_executor.py:17 Import 'agentic_core.l4_memory_state.temporal.entity_resolution' forbidden
    ```
    ```
    lic_agents.py:130 Import 'agentic_core.l1_planning.planners.lic_prompt_builder' forbidden
    ```
    ... (6 more lines)
- ❌ **l3_orchestration_purity**: `FAIL`
  - 69 violations
  - **Details**:
    ```
    lic_execution.py:36 Import 'agentic_core.l5_safety.safety_policy.policy' forbidden
    ```
    ```
    lic_execution.py:480 Import 'agentic_core.l5_safety.safety_policy.types' forbidden
    ```
    ```
    lic_meta_loop.py:17 Import 'agentic_core.l5_safety.safety_validator.safety_validator.safety_validator' forbidden
    ```
    ```
    lic_meta_loop.py:18 Import 'agentic_core.l5_safety.safety_policy.types' forbidden
    ```
    ```
    lic_orchestrator.py:3 Import 'agentic_core.l1_planning.planners.lic_lic_planner' forbidden
    ```
    ```
    lic_orchestrator.py:4 Import 'agentic_core.l2_execution.engines.outreach.lic_k1_research' forbidden
    ```
    ```
    lic_orchestrator.py:5 Import 'agentic_core.l2_execution.engines.outreach.lic_k2_insights' forbidden
    ```
    ```
    lic_orchestrator.py:6 Import 'agentic_core.l2_execution.engines.outreach.lic_k3_draft' forbidden
    ```
    ```
    lic_orchestrator.py:7 Import 'agentic_core.l2_execution.engines.outreach.lic_k4_regen' forbidden
    ```
    ```
    lic_orchestrator.py:8 Import 'agentic_core.l2_execution.engines.outreach.lic_k5_validation' forbidden
    ```
    ```
    lic_orchestrator.py:9 Import 'agentic_core.l2_execution.engines.outreach.lic_k6_cta' forbidden
    ```
    ```
    lic_orchestrator.py:10 Import 'agentic_core.l2_execution.engines.outreach.lic_k7_assembly' forbidden
    ```
    ```
    lic_orchestrator_legacy.py:6 Import 'agentic_core.l2_execution.engines.outreach.lic_k1_research' forbidden
    ```
    ```
    lic_orchestrator_legacy.py:7 Import 'agentic_core.l2_execution.engines.outreach.lic_k2_insights' forbidden
    ```
    ```
    lic_orchestrator_legacy.py:8 Import 'agentic_core.l2_execution.engines.outreach.lic_k3_draft' forbidden
    ```
    ... (6 more lines)
- ⚠️ **l4_governance_exists**: `WARN`
  - Layer directory l4_governance missing
- ⚠️ **l5_meta_exists**: `WARN`
  - Layer directory l5_meta missing

### Engine Isolation
- ✅ **no_cross_engine_imports**: `PASS`
  - 0 cross-engine imports found

### Prompt Governance
- ✅ **no_inline_prompts**: `PASS`
  - 0 inline prompts detected
- ✅ **prompts_have_schemas**: `PASS`
  - 1 prompt schemas found

### Tooling
- ❌ **mypy_zero_errors**: `FAIL`
  - mypy: Failed (Code 2)
- ❌ **pytest_zero_errors**: `FAIL`
  - pytest: Failed (Code 1)
- ❌ **ruff_zero_errors**: `FAIL`
  - ruff: Failed (Code 1)

### Circular Imports
- ✅ **no_circular_imports**: `PASS`
  - No cycles found in 40 modules

### Zero Loss
- ❌ **dag_execution_completes**: `FAIL`
  - Status: completed, Valid: True

### Unimplemented
- ⚪ **authn_authz_enforced**: `UNVALIDATED`
  - Not implemented in validator
- ⚪ **cost_tracking_enabled**: `UNVALIDATED`
  - Not implemented in validator
- ⚪ **environment_separation_valid**: `UNVALIDATED`
  - Not implemented in validator
- ⚪ **error_taxonomy_applied**: `UNVALIDATED`
  - Not implemented in validator
- ⚪ **golden_datasets_loaded**: `UNVALIDATED`
  - Not implemented in validator
- ⚪ **hallucination_detector_active**: `UNVALIDATED`
  - Not implemented in validator
- ⚪ **injection_detector_active**: `UNVALIDATED`
  - Not implemented in validator
- ⚪ **kg_lookups_are_deterministic**: `UNVALIDATED`
  - Not implemented in validator
- ⚪ **latency_tracking_enabled**: `UNVALIDATED`
  - Not implemented in validator
- ⚪ **llm_as_judge_runs_successfully**: `UNVALIDATED`
  - Not implemented in validator
- ⚪ **mcp_access_respects_acls**: `UNVALIDATED`
  - Not implemented in validator
- ⚪ **mcp_tools_define_input_output_schemas**: `UNVALIDATED`
  - Not implemented in validator
- ⚪ **mcp_used_for_external_calls**: `UNVALIDATED`
  - Not implemented in validator
- ⚪ **model_versions_pinned**: `UNVALIDATED`
  - Not implemented in validator
- ⚪ **pii_filter_active**: `UNVALIDATED`
  - Not implemented in validator
- ⚪ **rag_calls_are_deterministic**: `UNVALIDATED`
  - Not implemented in validator
- ⚪ **regression_tests_all_pass**: `UNVALIDATED`
  - Not implemented in validator
- ⚪ **reliability_scores_updated**: `UNVALIDATED`
  - Not implemented in validator
- ⚪ **rest_endpoints_secure**: `UNVALIDATED`
  - Not implemented in validator
- ⚪ **safety_runs_on_all_mutating_actions**: `UNVALIDATED`
  - Not implemented in validator
- ⚪ **safety_runs_on_all_outbound_content**: `UNVALIDATED`
  - Not implemented in validator
- ⚪ **temporal_validity_enforced_on_events**: `UNVALIDATED`
  - Not implemented in validator
- ⚪ **toolpath_evaluation_passed**: `UNVALIDATED`
  - Not implemented in validator
