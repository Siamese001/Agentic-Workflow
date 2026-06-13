# execute_ssot Technical Debt Removal

## Scope

Debt-1: Replace [BMG-GPU] string heuristic in _compute_novelty_score with hash-fallback vector comparison.
Debt-2: Add VectorSourceMismatchError class + dim-mismatch guard in _compute_novelty_score.
Debt-3: Add deterministic sort tie-break (score DESC, content_hash ASC, trace_id ASC) to retrieve_similar_incidents().
Debt-4: Fix adapter sentinel bug in _fire_meta_learning_intake (adapter = None before first try-block).
Debt-5: Remove inline import hashlib from _wc_digest; add module-level import instead.
Tests: 10 new tests in test_execute_ssot_debt_removal.py + 1 in test_phase_b_memory_routing.py.

## CODE_COMMIT

c94c9d50de4a6b9d78cb9026e93384cacb3e7562

## EVIDENCE_COMMIT

8020297a159bef570347b55b12a6c9cd39ffae1a

## FILES_CHANGED_CODE

agentic_core/L0_routing/scripts/execute_ssot.py
agentic_core/L1_cognition/memory/healing_memory_retriever.py
ops_scripts/hooks/landmine_baseline.txt
system_learning/pipelines/meta_learning_pipeline.py
tests/unit/test_execute_ssot_debt_removal.py
tests/unit/test_phase_b_memory_routing.py

## FILES_CHANGED_EVIDENCE

docs/reports/plans/execute-ssot-debt-removal-evidence.md

## INSPECTED_FILES

agentic_core/L0_routing/scripts/execute_ssot.py
agentic_core/L1_cognition/memory/healing_memory_retriever.py
system_learning/pipelines/meta_learning_pipeline.py
tests/unit/test_execute_ssot_debt_removal.py
tests/unit/test_phase_b_memory_routing.py
docs/reports/plans/embedding-lifecycle-gap-analysis.md

## Full Phase Test Suite (A + B + C + Debt)

$ python -m pytest tests/system_learning/test_phase_a_learning_loop.py tests/unit/test_phase_b_memory_routing.py tests/system_learning/test_phase_c_pipeline_integration.py tests/unit/test_execute_ssot_debt_removal.py -q --color=no --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
collected 46 items

tests/system_learning/test_phase_a_learning_loop.py::test_fallback_vector_never_none PASSED [  2%]
tests/system_learning/test_phase_a_learning_loop.py::test_fallback_vector_determinism PASSED [  4%]
tests/system_learning/test_phase_a_learning_loop.py::test_fallback_vector_l2_normalized PASSED [  6%]
tests/system_learning/test_phase_a_learning_loop.py::test_fallback_vector_different_inputs_differ PASSED [  8%]
tests/system_learning/test_phase_a_learning_loop.py::test_healing_outcome_event_cluster_id_and_files_touched PASSED [ 10%]
tests/system_learning/test_phase_a_learning_loop.py::test_healing_outcome_event_defaults_none PASSED [ 13%]
tests/system_learning/test_phase_a_learning_loop.py::test_persist_to_disk_writes_three_files PASSED [ 15%]
tests/system_learning/test_phase_a_learning_loop.py::test_persist_to_disk_prints_determinism_digest PASSED [ 17%]
tests/system_learning/test_phase_a_learning_loop.py::test_persist_to_disk_digest_deterministic PASSED [ 19%]
tests/system_learning/test_phase_a_learning_loop.py::test_load_from_disk_round_trip PASSED [ 21%]
tests/system_learning/test_phase_a_learning_loop.py::test_manifest_tamper_raises_integrity_error PASSED [ 23%]
tests/system_learning/test_phase_a_learning_loop.py::test_load_missing_manifest_raises PASSED [ 26%]
tests/unit/test_phase_b_memory_routing.py::test_null_retriever_returns_empty_list PASSED [ 28%]
tests/unit/test_phase_b_memory_routing.py::test_null_retriever_is_not_active PASSED [ 30%]
tests/unit/test_phase_b_memory_routing.py::test_healing_retriever_is_active PASSED [ 32%]
tests/unit/test_phase_b_memory_routing.py::test_healing_retriever_empty_signal_returns_empty PASSED [ 34%]
tests/unit/test_phase_b_memory_routing.py::test_healing_retriever_returns_advisory_only_incidents PASSED [ 36%]
tests/unit/test_phase_b_memory_routing.py::test_build_retriever_returns_null_when_embeddings_disabled PASSED [ 39%]
tests/unit/test_phase_b_memory_routing.py::test_build_retriever_returns_null_when_base_path_none PASSED [ 41%]
tests/unit/test_phase_b_memory_routing.py::test_sovereign_engine_accepts_retriever_kwarg PASSED [ 43%]
tests/unit/test_phase_b_memory_routing.py::test_sovereign_engine_default_retriever_is_none PASSED [ 45%]
tests/unit/test_phase_b_memory_routing.py::test_advisory_result_never_alters_routing_score PASSED [ 47%]
tests/unit/test_phase_b_memory_routing.py::test_retrieve_similar_incidents_prints_wb_digest PASSED [ 50%]
tests/unit/test_phase_b_memory_routing.py::test_wb_digest_is_deterministic PASSED [ 52%]
tests/unit/test_phase_b_memory_routing.py::test_sovereignty_error_on_advisory_only_false PASSED [ 54%]
tests/unit/test_phase_b_memory_routing.py::test_retrieve_similar_incidents_sort_is_deterministic PASSED [ 56%]
tests/system_learning/test_phase_c_pipeline_integration.py::test_retrieval_profile_embeddings_enabled_false_by_default PASSED [ 58%]
tests/system_learning/test_phase_c_pipeline_integration.py::test_retrieval_profile_embeddings_enabled_true_from_env PASSED [ 60%]
tests/system_learning/test_phase_c_pipeline_integration.py::test_fallback_vector_has_16_dims PASSED [ 63%]
tests/system_learning/test_phase_c_pipeline_integration.py::test_old_4dim_vector_no_longer_produced PASSED [ 65%]
tests/system_learning/test_phase_c_pipeline_integration.py::test_retrieve_semantic_context_disabled_has_vector_source PASSED [ 67%]
tests/system_learning/test_phase_c_pipeline_integration.py::test_retrieve_semantic_context_retrieval_failed_has_vector_source PASSED [ 69%]
tests/system_learning/test_phase_c_pipeline_integration.py::test_live_run_adapter_record_count_empty PASSED [ 71%]
tests/system_learning/test_phase_c_pipeline_integration.py::test_live_run_adapter_record_count_nonzero PASSED [ 73%]
tests/system_learning/test_phase_c_pipeline_integration.py::test_retrieve_semantic_context_wc_digest_in_return_dict PASSED [ 76%]
tests/system_learning/test_phase_c_pipeline_integration.py::test_wc_digest_is_deterministic PASSED [ 78%]
tests/system_learning/test_phase_c_pipeline_integration.py::test_activation_without_dual_approval_raises PASSED [ 80%]
tests/unit/test_execute_ssot_debt_removal.py::test_novelty_score_disabled_no_vectors_returns_1 PASSED [ 82%]
tests/unit/test_execute_ssot_debt_removal.py::test_novelty_score_disabled_uses_fallback_vector_not_bmg_string PASSED [ 84%]
tests/unit/test_execute_ssot_debt_removal.py::test_novelty_score_disabled_completely_novel_returns_3 PASSED [ 86%]
tests/unit/test_execute_ssot_debt_removal.py::test_novelty_score_disabled_legacy_bmg_gpu_string_no_longer_used PASSED [ 89%]
tests/unit/test_execute_ssot_debt_removal.py::test_vector_source_mismatch_error_exported PASSED [ 91%]
tests/unit/test_execute_ssot_debt_removal.py::test_novelty_score_dim_mismatch_raises_vector_source_mismatch_error PASSED [ 93%]
tests/unit/test_execute_ssot_debt_removal.py::test_fire_meta_learning_intake_no_name_error_when_intake_fails PASSED [ 95%]
tests/unit/test_execute_ssot_debt_removal.py::test_fire_meta_learning_intake_adapter_sentinel_is_none_on_early_fail PASSED [ 97%]
tests/unit/test_execute_ssot_debt_removal.py::test_wc_digest_no_inline_hashlib_import PASSED [100%]

46 passed in 0.50s

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

