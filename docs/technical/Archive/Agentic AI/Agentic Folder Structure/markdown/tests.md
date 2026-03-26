tests/
│
├── __init__.py
│
├── data/
│   ├── __init__.py
│   ├── sample_rg_resume_input.json
│   ├── sample_lic_outreach_input.json
│   ├── sample_company_kg.json
│   └── sample_contact_kg.json
│
├── fixtures/
│   ├── __init__.py
│   ├── rg_resume_fixtures.py
│   ├── lic_outreach_fixtures.py
│   ├── memory_fixtures.py
│   ├── rag_fixtures.py
│   └── model_stub_fixtures.py
│
├── e2e/
│   ├── __init__.py
│   ├── test_e2e_rg_resume_flow.py
│   ├── test_e2e_lic_outreach_flow.py
│   ├── test_e2e_tool_error_recovery.py
│   ├── test_e2e_multi_turn_state.py
│   └── test_e2e_safety_blocking_flows.py
│
├── integration/
│   ├── __init__.py
│   ├── test_cross_layer_purity.py
│   ├── test_model_routing.py
│   ├── test_rag_pipeline_integration.py
│   ├── test_kg_pipeline_integration.py
│   ├── test_memory_integration.py
│   ├── test_tool_calls.py
│   └── test_observability_integration.py
│
├── regression/
│   ├── __init__.py
│   ├── test_regression_rg_resume_outputs.py
│   ├── test_regression_lic_outreach_outputs.py
│   ├── test_regression_temporal_memory.py
│   ├── test_api_stability.py
│   ├── test_output_stability.py
│   └── test_performance_stability.py
│
├── l1_planning/
│   ├── __init__.py
│   │
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_l1_rg_planning_integration.py
│   │   └── test_l1_lic_planning_integration.py
│   │
│   └── unit/
│       ├── __init__.py
│       ├── test_rg_message_planner.py
│       ├── test_rg_research_planner.py
│       ├── test_rg_strategy_planner.py
│       ├── test_rg_safety_planner.py
│       ├── test_rg_refinement_planner.py
│       ├── test_lic_message_planner.py
│       ├── test_lic_research_planner.py
│       ├── test_lic_strategy_planner.py
│       ├── test_lic_safety_planner.py
│       ├── test_lic_refinement_planner.py
│       └── test_planning_schema_validation.py
│
├── l2_execution/
│   ├── __init__.py
│   │
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_l2_rg_execution_integration.py
│   │   └── test_l2_lic_execution_integration.py
│   │
│   └── unit/
│       ├── __init__.py
│       ├── test_rg_company_research_executor.py
│       ├── test_rg_contact_research_executor.py
│       ├── test_rg_message_generation_executor.py
│       ├── test_lic_company_research_executor.py
│       ├── test_lic_contact_research_executor.py
│       ├── test_lic_message_generation_executor.py
│       ├── test_tool_request_builder.py
│       └── test_tool_response_parser.py
│
├── l3_orchestration/
│   ├── __init__.py
│   │
│   └── dag/
│       ├── __init__.py
│       ├── test_rg_resume_engine_dag.py
│       ├── test_lic_outreach_engine_dag.py
│       ├── test_self_correction_loops.py
│       ├── test_dag_validity.py
│       └── test_fallback_paths.py
│
├── l4_memory/
│   ├── __init__.py
│   │
│   └── providers/
│       ├── __init__.py
│       ├── test_rg_memory_mappings.py
│       ├── test_rg_temporal_memory.py
│       ├── test_lic_memory_mappings.py
│       ├── test_lic_temporal_memory.py
│       ├── test_provider_registry.py
│       ├── test_long_term_memory.py
│       └── test_memory_schema_validation.py
│
└── l5_safety/
    ├── __init__.py
    │
    └── rules/
        ├── __init__.py
        ├── test_filters.py
        ├── test_policy_engine.py
        ├── test_prompt_injection_protection.py
        ├── test_validators.py
        ├── test_safety_schema_validation.py
        └── test_llm_guardrails.py


### Directory Structure

```plaintext
├── agentic_core.md
├── apps.md
├── config.md
├── data.md
├── observability.md
├── prompt_governance.md
├── runtime.md
├── schemas.md
├── scripts.md
├── tests.md
└── update_markdown_trees.py
```
