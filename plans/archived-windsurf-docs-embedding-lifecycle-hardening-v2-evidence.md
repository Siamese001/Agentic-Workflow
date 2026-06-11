---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\embedding-lifecycle-hardening-v2-evidence.md'
original_relative_path: 'embedding-lifecycle-hardening-v2-evidence.md'
source_sha256: 585c9d9db7e8615c4a4e9640279e38a3482da069784e5911f3dfe1215acd0d77
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-04'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Embedding Lifecycle Hardening -- Phase B/C Digest + Sovereignty Hardening

## Scope

Phase B: Add W-B-DETERMINISM-DIGEST to retrieve_similar_incidents(), SovereigntyError guard on advisory_only=False.
Phase C: Add W-C-DETERMINISM-DIGEST to _retrieve_semantic_context() all return paths, ActivationAuthorizationError dual-approval gate.
Tests: 6 new hardening tests added to test_phase_b_memory_routing.py and test_phase_c_pipeline_integration.py.

## CODE_COMMIT

57c09de9a29fc1437e059cb36dbf85ee532a4637

## EVIDENCE_COMMIT

9833998de055a0004961280d79e3c479275ef4e3

## FILES_CHANGED_CODE

agentic_core/L0_routing/scripts/execute_ssot.py
agentic_core/L1_cognition/memory/healing_memory_retriever.py
ops_scripts/hooks/landmine_baseline.txt
system_learning/adapters/live_run_pipeline_adapter.py
system_learning/pipelines/meta_learning_pipeline.py
tests/system_learning/test_phase_c_pipeline_integration.py
tests/unit/test_phase_b_memory_routing.py

## FILES_CHANGED_EVIDENCE

docs/reports/plans/embedding-lifecycle-hardening-v2-evidence.md

## INSPECTED_FILES

agentic_core/L1_cognition/memory/healing_memory_retriever.py
agentic_core/L0_routing/scripts/execute_ssot.py
system_learning/adapters/live_run_pipeline_adapter.py
system_learning/pipelines/meta_learning_pipeline.py
tests/unit/test_phase_b_memory_routing.py
tests/system_learning/test_phase_c_pipeline_integration.py
tests/system_learning/test_phase_a_learning_loop.py
docs/reports/plans/embedding-lifecycle-gap-analysis.md

## Phase Tests (A + B + C)

\$ python -m pytest tests/system_learning/test_phase_a_learning_loop.py tests/unit/test_phase_b_memory_routing.py tests/system_learning/test_phase_c_pipeline_integration.py -q --color=no --tb=short
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
collected 36 items

tests/system_learning/test_phase_a_learning_loop.py::test_fallback_vector_never_none PASSED [  2%]
tests/system_learning/test_phase_a_learning_loop.py::test_fallback_vector_determinism PASSED [  5%]
tests/system_learning/test_phase_a_learning_loop.py::test_fallback_vector_l2_normalized PASSED [  8%]
tests/system_learning/test_phase_a_learning_loop.py::test_fallback_vector_different_inputs_differ PASSED [ 11%]
tests/system_learning/test_phase_a_learning_loop.py::test_healing_outcome_event_cluster_id_and_files_touched PASSED [ 13%]
tests/system_learning/test_phase_a_learning_loop.py::test_healing_outcome_event_defaults_none PASSED [ 16%]
tests/system_learning/test_phase_a_learning_loop.py::test_persist_to_disk_writes_three_files PASSED [ 19%]
tests/system_learning/test_phase_a_learning_loop.py::test_persist_to_disk_prints_determinism_digest PASSED [ 22%]
tests/system_learning/test_phase_a_learning_loop.py::test_persist_to_disk_digest_deterministic PASSED [ 25%]
tests/system_learning/test_phase_a_learning_loop.py::test_load_from_disk_round_trip PASSED [ 27%]
tests/system_learning/test_phase_a_learning_loop.py::test_manifest_tamper_raises_integrity_error PASSED [ 30%]
tests/system_learning/test_phase_a_learning_loop.py::test_load_missing_manifest_raises PASSED [ 33%]
tests/unit/test_phase_b_memory_routing.py::test_null_retriever_returns_empty_list PASSED [ 36%]
tests/unit/test_phase_b_memory_routing.py::test_null_retriever_is_not_active PASSED [ 38%]
tests/unit/test_phase_b_memory_routing.py::test_healing_retriever_is_active PASSED [ 41%]
tests/unit/test_phase_b_memory_routing.py::test_healing_retriever_empty_signal_returns_empty PASSED [ 44%]
tests/unit/test_phase_b_memory_routing.py::test_healing_retriever_returns_advisory_only_incidents PASSED [ 47%]
tests/unit/test_phase_b_memory_routing.py::test_build_retriever_returns_null_when_embeddings_disabled PASSED [ 50%]
tests/unit/test_phase_b_memory_routing.py::test_build_retriever_returns_null_when_base_path_none PASSED [ 52%]
tests/unit/test_phase_b_memory_routing.py::test_sovereign_engine_accepts_retriever_kwarg PASSED [ 55%]
tests/unit/test_phase_b_memory_routing.py::test_sovereign_engine_default_retriever_is_none PASSED [ 58%]
tests/unit/test_phase_b_memory_routing.py::test_advisory_result_never_alters_routing_score PASSED [ 61%]
tests/unit/test_phase_b_memory_routing.py::test_retrieve_similar_incidents_prints_wb_digest PASSED [ 63%]
tests/unit/test_phase_b_memory_routing.py::test_wb_digest_is_deterministic PASSED [ 66%]
tests/unit/test_phase_b_memory_routing.py::test_sovereignty_error_on_advisory_only_false PASSED [ 69%]
tests/system_learning/test_phase_c_pipeline_integration.py::test_retrieval_profile_embeddings_enabled_false_by_default PASSED [ 72%]
tests/system_learning/test_phase_c_pipeline_integration.py::test_retrieval_profile_embeddings_enabled_true_from_env PASSED [ 75%]
tests/system_learning/test_phase_c_pipeline_integration.py::test_fallback_vector_has_16_dims PASSED [ 77%]
tests/system_learning/test_phase_c_pipeline_integration.py::test_old_4dim_vector_no_longer_produced PASSED [ 80%]
tests/system_learning/test_phase_c_pipeline_integration.py::test_retrieve_semantic_context_disabled_has_vector_source PASSED [ 83%]
tests/system_learning/test_phase_c_pipeline_integration.py::test_retrieve_semantic_context_retrieval_failed_has_vector_source PASSED [ 86%]
tests/system_learning/test_phase_c_pipeline_integration.py::test_live_run_adapter_record_count_empty PASSED [ 88%]
tests/system_learning/test_phase_c_pipeline_integration.py::test_live_run_adapter_record_count_nonzero PASSED [ 91%]
tests/system_learning/test_phase_c_pipeline_integration.py::test_retrieve_semantic_context_wc_digest_in_return_dict PASSED [ 94%]
tests/system_learning/test_phase_c_pipeline_integration.py::test_wc_digest_is_deterministic PASSED [ 97%]
tests/system_learning/test_phase_c_pipeline_integration.py::test_activation_without_dual_approval_raises PASSED [100%]

36 passed in 0.27s

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

