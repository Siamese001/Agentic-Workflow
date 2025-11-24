# Baseline Test Results - Pre-Restructuring

**Date:** 2025-11-25  
**Command:** `python -m pytest tests/ -v --tb=short`  
**Results:** 15 failed, 183 passed, 4 skipped, 62 warnings

## Failed Tests (Baseline)

### ExecutionContext Field Errors (7 tests)

- test_e2e_full_pipeline
- test_e2e_correction_signals_and_ais_snapshot  
- test_e2e_safety_flow
- test_e2e_correction_loop
- test_regression_state_patch_against_golden
- test_multi_scenario_e2e[scenario0]
- test_multi_scenario_e2e[scenario1]
- test_l3_dag_orchestration

**Error:** `ValueError: "ExecutionContext" object has no field "saf..."`

### Retrieval Configuration Errors (1 test)

- test_execute_retrieval_uses_high_quality_profile_retrieval_cfg

**Error:** `KeyError: 'hyde_query'`

### TemporalKG Attribute Errors (2 tests)

- test_add_fact
- test_add_facts_batch

**Error:** `AttributeError: <class 'l4.temporal_kg.TemporalKG'> doe...`

### Integration Errors (2 tests)

- test_hybrid_search_execution
- test_execution_context_with_l4_adapters

**Errors:** `assert 0 > 0`, `TypeError: argument of type 'Mock' is not iterable`

### Vector Search Errors (2 tests)

- test_vector_search_flow
- test_import_vector_modules

**Errors:** `AttributeError`, `ImportError: cannot import name 'Pinecone'`

## Goal After Restructuring

- Same number of failures (15)
- Same number of passes (183)
- No NEW failures introduced
