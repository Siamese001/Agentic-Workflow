# G1 — Unclassified / Deferred Modules

Modules whose role could not be narrowed beyond `other` under G1's fixed role enum. Each one is present in `component_inventory.yaml` with `role: other`; this file is the cross-post register for G6 (taxonomy cleanup / special-surface normalization) to refine classification.

**ADG snapshot**: `artifacts/adg/adg_indexed_04172026_0611.sqlite` (04172026_0611).

## Deferral policy

- **Kept in inventory**: `role: other` is a valid value in the role enum defined by `docs/wave_g/G0_full_runtime_plan/output_contracts.md`. These modules are NOT excluded from `component_inventory.yaml`.
- **Deferred for refinement**: G6 is the designated downstream owner. The goal there is to either promote each module to a sharper role (`reasoner`, `util`, `reader`, `runtime-scaffold`, etc.) or record the subsystem as intentionally fine-grained (e.g., many small modules inside an ADG analysis pass).
- **No module is dropped**: the round-trip check (`component_inventory.yaml` vs filesystem walk) shows 0 missing and 0 extra. All 2,014 `.py` files are accounted for.

## Summary

- **Total modules with `role: other`**: 337 of 2014 (16.7%).
- **Subsystems where `other` clusters**: 99.
- **Modules that could NOT be classified at all** (i.e., could not even be placed under a layer or CROSS_CUTTING): **0**.
- **Proposed downstream owner**: G6 for role refinement; G3b / G7 for atom binding where applicable.

## Modules deferred for role refinement (grouped by subsystem)

Each group below lists the paths exactly as they appear in `component_inventory.yaml`. The count in parentheses is the number of `other`-role modules in that subsystem.

### `agentic_core/evaluation/retrieval/` (33)

- `agentic_core/evaluation/retrieval/__init__.py`
- `agentic_core/evaluation/retrieval/answer_correctness.py`
- `agentic_core/evaluation/retrieval/answer_support.py`
- `agentic_core/evaluation/retrieval/apps_engines_aliases.py`
- `agentic_core/evaluation/retrieval/base.py`
- `agentic_core/evaluation/retrieval/completeness.py`
- `agentic_core/evaluation/retrieval/completeness_feedback.py`
- `agentic_core/evaluation/retrieval/completeness_metrics.py`
- `agentic_core/evaluation/retrieval/completeness_monitors.py`
- `agentic_core/evaluation/retrieval/completeness_reranker.py`
- `agentic_core/evaluation/retrieval/completeness_scorer.py`
- `agentic_core/evaluation/retrieval/dpo_batch_builder.py`
- `agentic_core/evaluation/retrieval/drift_monitor.py`
- `agentic_core/evaluation/retrieval/fusion.py`
- `agentic_core/evaluation/retrieval/groundedness.py`
- `agentic_core/evaluation/retrieval/interfaces.py`
- `agentic_core/evaluation/retrieval/l4_registries.py`
- `agentic_core/evaluation/retrieval/late_chunking.py`
- `agentic_core/evaluation/retrieval/meta_learning_bridge.py`
- `agentic_core/evaluation/retrieval/mrr.py`
- `agentic_core/evaluation/retrieval/ndcg.py`
- `agentic_core/evaluation/retrieval/offline_eval_runner.py`
- `agentic_core/evaluation/retrieval/parent_child.py`
- `agentic_core/evaluation/retrieval/precision_at_k.py`
- `agentic_core/evaluation/retrieval/profiles.py`
- `agentic_core/evaluation/retrieval/proposer_bridge.py`
- `agentic_core/evaluation/retrieval/recall_at_k.py`
- `agentic_core/evaluation/retrieval/replay_eval_runner.py`
- `agentic_core/evaluation/retrieval/reranker.py`
- `agentic_core/evaluation/retrieval/schemas.py`
- `agentic_core/evaluation/retrieval/sealed_interface_check_enforcer.py`
- `agentic_core/evaluation/retrieval/shadow_eval_runner.py`
- `agentic_core/evaluation/retrieval/snapshots.py`

### `agentic_core/adg/extraction/` (20)

- `agentic_core/adg/extraction/__init__.py`
- `agentic_core/adg/extraction/agent_registry_scanner.py`
- `agentic_core/adg/extraction/edge_builder.py`
- `agentic_core/adg/extraction/exception_classifier.py`
- `agentic_core/adg/extraction/graph_persister.py`
- `agentic_core/adg/extraction/identity_normalizer.py`
- `agentic_core/adg/extraction/incremental.py`
- `agentic_core/adg/extraction/optimized_tools.py`
- `agentic_core/adg/extraction/scan_cache.py`
- `agentic_core/adg/extraction/semantic_maps.py`
- `agentic_core/adg/extraction/static_analyzer.py`
- `agentic_core/adg/extraction/visitors/context_control.py`
- `agentic_core/adg/extraction/visitors/core.py`
- `agentic_core/adg/extraction/visitors/dynamic.py`
- `agentic_core/adg/extraction/visitors/governance.py`
- `agentic_core/adg/extraction/visitors/learning.py`
- `agentic_core/adg/extraction/visitors/misc.py`
- `agentic_core/adg/extraction/visitors/p4_waves.py`
- `agentic_core/adg/extraction/visitors/runtime_semantic.py`
- `agentic_core/adg/extraction/visitors/structural.py`

### `agentic_core/adg/analysis/` (19)

- `agentic_core/adg/analysis/CanonicalSnapshot.py`
- `agentic_core/adg/analysis/EdgeConfidence.py`
- `agentic_core/adg/analysis/GraphDiff.py`
- `agentic_core/adg/analysis/SymbolIndex.py`
- `agentic_core/adg/analysis/__init__.py`
- `agentic_core/adg/analysis/confidence.py`
- `agentic_core/adg/analysis/coupling_metrics_config.py`
- `agentic_core/adg/analysis/dep_inversion.py`
- `agentic_core/adg/analysis/dep_inversion_types.py`
- `agentic_core/adg/analysis/diff.py`
- `agentic_core/adg/analysis/hotspot_index.py`
- `agentic_core/adg/analysis/hotspot_index_types.py`
- `agentic_core/adg/analysis/prompt_authority.py`
- `agentic_core/adg/analysis/prompt_authority_types.py`
- `agentic_core/adg/analysis/prompt_drift_config.py`
- `agentic_core/adg/analysis/protocol_coverage.py`
- `agentic_core/adg/analysis/schema_migration.py`
- `agentic_core/adg/analysis/snapshot.py`
- `agentic_core/adg/analysis/symbol_index.py`

### `agentic_core/adg/applications/` (16)

- `agentic_core/adg/applications/BlastRadiusResult.py`
- `agentic_core/adg/applications/__init__.py`
- `agentic_core/adg/applications/api_surface.py`
- `agentic_core/adg/applications/api_surface_types.py`
- `agentic_core/adg/applications/architecture_verifier.py`
- `agentic_core/adg/applications/blast_radius.py`
- `agentic_core/adg/applications/execute_ssot_integration.py`
- `agentic_core/adg/applications/guardian_prioritizer.py`
- `agentic_core/adg/applications/guardian_prioritizer_types.py`
- `agentic_core/adg/applications/prompt_impact.py`
- `agentic_core/adg/applications/prompt_impact_config.py`
- `agentic_core/adg/applications/rag_sovereignty.py`
- `agentic_core/adg/applications/refactoring_planner.py`
- `agentic_core/adg/applications/refactoring_planner_config.py`
- `agentic_core/adg/applications/rename_safety.py`
- `agentic_core/adg/applications/rename_safety_types.py`

### `agentic_core/L3_orchestration/inference/` (11)

- `agentic_core/L3_orchestration/inference/__init__.py`
- `agentic_core/L3_orchestration/inference/qwen_vllm/__init__.py`
- `agentic_core/L3_orchestration/inference/qwen_vllm/config.py`
- `agentic_core/L3_orchestration/inference/qwen_vllm/engines.py`
- `agentic_core/L3_orchestration/inference/qwen_vllm/engines/__init__.py`
- `agentic_core/L3_orchestration/inference/qwen_vllm/engines/hardened_vllm_client.py`
- `agentic_core/L3_orchestration/inference/qwen_vllm/engines/optimized_vllm_client.py`
- `agentic_core/L3_orchestration/inference/qwen_vllm/telemetry.py`
- `agentic_core/L3_orchestration/inference/qwen_vllm/tools.py`
- `agentic_core/L3_orchestration/inference/qwen_vllm/tools/__init__.py`
- `agentic_core/L3_orchestration/inference/qwen_vllm/tools/gpu_memory_monitor.py`

### `agentic_core/evaluation/metrics/` (11)

- `agentic_core/evaluation/metrics/__init__.py`
- `agentic_core/evaluation/metrics/answer_correctness.py`
- `agentic_core/evaluation/metrics/base.py`
- `agentic_core/evaluation/metrics/classification.py`
- `agentic_core/evaluation/metrics/f1_score.py`
- `agentic_core/evaluation/metrics/groundedness.py`
- `agentic_core/evaluation/metrics/mrr.py`
- `agentic_core/evaluation/metrics/ndcg.py`
- `agentic_core/evaluation/metrics/precision_at_k.py`
- `agentic_core/evaluation/metrics/ragas_metrics.py`
- `agentic_core/evaluation/metrics/recall_at_k.py`

### `agentic_core/evaluation/judges/` (10)

- `agentic_core/evaluation/judges/__init__.py`
- `agentic_core/evaluation/judges/deterministic_judges.py`
- `agentic_core/evaluation/judges/evidence_assembler.py`
- `agentic_core/evaluation/judges/llm_judge.py`
- `agentic_core/evaluation/judges/llm_judges.py`
- `agentic_core/evaluation/judges/rubric_engine.py`
- `agentic_core/evaluation/judges/scorecard.py`
- `agentic_core/evaluation/judges/source_retriever.py`
- `agentic_core/evaluation/judges/types.py`
- `agentic_core/evaluation/judges/verdict_store.py`

### `agentic_core/knowledge/document_loaders/` (10)

- `agentic_core/knowledge/document_loaders/__init__.py`
- `agentic_core/knowledge/document_loaders/csv_document_loader_config.py`
- `agentic_core/knowledge/document_loaders/csv_loader.py`
- `agentic_core/knowledge/document_loaders/html_loader.py`
- `agentic_core/knowledge/document_loaders/pdf_document_loader_config.py`
- `agentic_core/knowledge/document_loaders/pdf_loader.py`
- `agentic_core/knowledge/document_loaders/research_cache.py`
- `agentic_core/knowledge/document_loaders/source_document_types.py`
- `agentic_core/knowledge/document_loaders/text_document_loader_config.py`
- `agentic_core/knowledge/document_loaders/text_loader.py`

### `agentic_core/prompt_governance/scripts/` (9)

- `agentic_core/prompt_governance/scripts/audit_registry_linkages.py`
- `agentic_core/prompt_governance/scripts/detect_template_drift.py`
- `agentic_core/prompt_governance/scripts/dry_run_compiler.py`
- `agentic_core/prompt_governance/scripts/file_intent.py`
- `agentic_core/prompt_governance/scripts/harden_templates.py`
- `agentic_core/prompt_governance/scripts/import_violation_visitor.py`
- `agentic_core/prompt_governance/scripts/synchronize_registry_hashes.py`
- `agentic_core/prompt_governance/scripts/template_render_visitor.py`
- `agentic_core/prompt_governance/scripts/validate_assembly.py`

### `agentic_core/L2_execution/healers/` (8)

- `agentic_core/L2_execution/healers/__init__.py`
- `agentic_core/L2_execution/healers/activation_state.py`
- `agentic_core/L2_execution/healers/artifact_loader.py`
- `agentic_core/L2_execution/healers/confidence_scorer.py`
- `agentic_core/L2_execution/healers/failure_signal.py`
- `agentic_core/L2_execution/healers/governed_scorer.py`
- `agentic_core/L2_execution/healers/secure_reading_room.py`
- `agentic_core/L2_execution/healers/zero_loss_containment.py`

### `agentic_core/adg/artifact/` (8)

- `agentic_core/adg/artifact/ArtifactPaths.py`
- `agentic_core/adg/artifact/SplitArtifact.py`
- `agentic_core/adg/artifact/__init__.py`
- `agentic_core/adg/artifact/layer_splitter.py`
- `agentic_core/adg/artifact/normalizer.py`
- `agentic_core/adg/artifact/normalizer_config.py`
- `agentic_core/adg/artifact/paths.py`
- `agentic_core/adg/artifact/serializer.py`

### `agentic_core/prompt_governance/security/` (8)

- `agentic_core/prompt_governance/security/__init__.py`
- `agentic_core/prompt_governance/security/assembly_injection_neutralizer.py`
- `agentic_core/prompt_governance/security/detectors/__init__.py`
- `agentic_core/prompt_governance/security/detectors/assembly_injection_neutralizer.py`
- `agentic_core/prompt_governance/security/detectors/injection_detector.py`
- `agentic_core/prompt_governance/security/detectors/pii_scrubber.py`
- `agentic_core/prompt_governance/security/utils/__init__.py`
- `agentic_core/prompt_governance/security/validators/__init__.py`

### `agentic_core/L3_orchestration/reasoning/` (7)

- `agentic_core/L3_orchestration/reasoning/__init__.py`
- `agentic_core/L3_orchestration/reasoning/arbitration/__init__.py`
- `agentic_core/L3_orchestration/reasoning/coordination/__init__.py`
- `agentic_core/L3_orchestration/reasoning/engines/__init__.py`
- `agentic_core/L3_orchestration/reasoning/learning/__init__.py`
- `agentic_core/L3_orchestration/reasoning/ptc/__init__.py`
- `agentic_core/L3_orchestration/reasoning/territory_healing/__init__.py`

### `agentic_core/prompt_governance/core/` (7)

- `agentic_core/prompt_governance/core/__init__.py`
- `agentic_core/prompt_governance/core/governance_hub.py`
- `agentic_core/prompt_governance/core/prompt_assembler.py`
- `agentic_core/prompt_governance/core/prompt_entry_types.py`
- `agentic_core/prompt_governance/core/prompt_loader.py`
- `agentic_core/prompt_governance/core/sovereign_prompt_renderer.py`
- `agentic_core/prompt_governance/core/tier_instructional_enrichment.py`

### `agentic_core/L2_execution/determinism/` (6)

- `agentic_core/L2_execution/determinism/__init__.py`
- `agentic_core/L2_execution/determinism/determinism_digest.py`
- `agentic_core/L2_execution/determinism/determinism_surface.py`
- `agentic_core/L2_execution/determinism/freeze_propagator.py`
- `agentic_core/L2_execution/determinism/replay_envelope.py`
- `agentic_core/L2_execution/determinism/replay_guard.py`

### `agentic_core/L2_execution/capability/` (5)

- `agentic_core/L2_execution/capability/__init__.py`
- `agentic_core/L2_execution/capability/access_classifier.py`
- `agentic_core/L2_execution/capability/call_interceptor.py`
- `agentic_core/L2_execution/capability/invocation_recorder.py`
- `agentic_core/L2_execution/capability/ticket_builder.py`

### `agentic_core/evaluation/monitoring/` (5)

- `agentic_core/evaluation/monitoring/__init__.py`
- `agentic_core/evaluation/monitoring/completeness_monitors.py`
- `agentic_core/evaluation/monitoring/drift_monitor.py`
- `agentic_core/evaluation/monitoring/shadow_eval_runner.py`
- `agentic_core/evaluation/monitoring/snapshots.py`

### `agentic_core/knowledge/canonical/` (5)

- `agentic_core/knowledge/canonical/__init__.py`
- `agentic_core/knowledge/canonical/canonical_store.py`
- `agentic_core/knowledge/canonical/canonical_types.py`
- `agentic_core/knowledge/canonical/chunk_manifest.py`
- `agentic_core/knowledge/canonical/raw_unit_factory.py`

### `agentic_core/knowledge/retrieval/` (5)

- `agentic_core/knowledge/retrieval/__init__.py`
- `agentic_core/knowledge/retrieval/evidence_contract_builder.py`
- `agentic_core/knowledge/retrieval/parent_child_hydrator.py`
- `agentic_core/knowledge/retrieval/prompt_envelope.py`
- `agentic_core/knowledge/retrieval/senior_librarian_reranker.py`

### `agentic_core/adg/client/` (4)

- `agentic_core/adg/client/InMemoryStore.py`
- `agentic_core/adg/client/__init__.py`
- `agentic_core/adg/client/cli.py`
- `agentic_core/adg/client/mcp_client.py`

### `agentic_core/adg/processing/` (4)

- `agentic_core/adg/processing/phase2_disposition_processor.py`
- `agentic_core/adg/processing/phase3_auto_remediation.py`
- `agentic_core/adg/processing/phase3_enhanced_test_coverage.py`
- `agentic_core/adg/processing/phase3_intelligent_disposition.py`

### `agentic_core/evaluation/feedback/` (4)

- `agentic_core/evaluation/feedback/__init__.py`
- `agentic_core/evaluation/feedback/dpo_batch_builder.py`
- `agentic_core/evaluation/feedback/proposer_bridge.py`
- `agentic_core/evaluation/feedback/schemas.py`

### `agentic_core/knowledge/chunking/` (4)

- `agentic_core/knowledge/chunking/__init__.py`
- `agentic_core/knowledge/chunking/chunk_policy_engine.py`
- `agentic_core/knowledge/chunking/chunking_modes.py`
- `agentic_core/knowledge/chunking/corpus_classifier.py`

### `agentic_core/knowledge/concurrency/` (4)

- `agentic_core/knowledge/concurrency/__init__.py`
- `agentic_core/knowledge/concurrency/backpressure_controller.py`
- `agentic_core/knowledge/concurrency/concurrency_manager.py`
- `agentic_core/knowledge/concurrency/rate_limiter.py`

### `agentic_core/knowledge/dispatcher/` (4)

- `agentic_core/knowledge/dispatcher/__init__.py`
- `agentic_core/knowledge/dispatcher/cache_decision_engine.py`
- `agentic_core/knowledge/dispatcher/compute_budget_manager.py`
- `agentic_core/knowledge/dispatcher/hybrid_threshold_manager.py`

### `agentic_core/knowledge/ingestion/` (4)

- `agentic_core/knowledge/ingestion/__init__.py`
- `agentic_core/knowledge/ingestion/intake_clerk.py`
- `agentic_core/knowledge/ingestion/modality_types.py`
- `agentic_core/knowledge/ingestion/visual_detector.py`

### `agentic_core/knowledge/lifecycle/` (4)

- `agentic_core/knowledge/lifecycle/__init__.py`
- `agentic_core/knowledge/lifecycle/change_detector.py`
- `agentic_core/knowledge/lifecycle/reindex_coordinator.py`
- `agentic_core/knowledge/lifecycle/state_sync_manager.py`

### `agentic_core/knowledge/observability/` (4)

- `agentic_core/knowledge/observability/__init__.py`
- `agentic_core/knowledge/observability/error_classifier.py`
- `agentic_core/knowledge/observability/latency_analyzer.py`
- `agentic_core/knowledge/observability/slo_tracker.py`

### `agentic_core/knowledge/query/` (4)

- `agentic_core/knowledge/query/__init__.py`
- `agentic_core/knowledge/query/preprocessing_pipeline.py`
- `agentic_core/knowledge/query/query_vectorizer.py`
- `agentic_core/knowledge/query/routing_signal_detector.py`

### `agentic_core/knowledge/telemetry/` (4)

- `agentic_core/knowledge/telemetry/__init__.py`
- `agentic_core/knowledge/telemetry/performance_attribution.py`
- `agentic_core/knowledge/telemetry/query_tagger.py`
- `agentic_core/knowledge/telemetry/telemetry_collector.py`

### `agentic_core/L3_orchestration/utils/` (3)

- `agentic_core/L3_orchestration/utils/__init__.py`
- `agentic_core/L3_orchestration/utils/registry/__init__.py`
- `agentic_core/L3_orchestration/utils/replay/__init__.py`

### `agentic_core/adg/precision/` (3)

- `agentic_core/adg/precision/__init__.py`
- `agentic_core/adg/precision/precision_extractor.py`
- `agentic_core/adg/precision/precision_schema.py`

### `agentic_core/case_memory/core/` (3)

- `agentic_core/case_memory/core/case_library.py`
- `agentic_core/case_memory/core/graph_neighborhood_memory.py`
- `agentic_core/case_memory/core/memory_card.py`

### `agentic_core/evaluation/runners/` (3)

- `agentic_core/evaluation/runners/__init__.py`
- `agentic_core/evaluation/runners/offline_eval_runner.py`
- `agentic_core/evaluation/runners/replay_eval_runner.py`

### `agentic_core/knowledge/circuit/` (3)

- `agentic_core/knowledge/circuit/circuit_breaker.py`
- `agentic_core/knowledge/circuit/failure_handler.py`
- `agentic_core/knowledge/circuit/recovery_manager.py`

### `agentic_core/knowledge/fallback/` (3)

- `agentic_core/knowledge/fallback/__init__.py`
- `agentic_core/knowledge/fallback/low_risk_fallback.py`
- `agentic_core/knowledge/fallback/reading_room_integration.py`

### `agentic_core/knowledge/static_index/` (3)

- `agentic_core/knowledge/static_index/__init__.py`
- `agentic_core/knowledge/static_index/action_verbs_types.py`
- `agentic_core/knowledge/static_index/skill_taxonomy_types.py`

### `agentic_core/L1_cognition/reasoning/` (2)

- `agentic_core/L1_cognition/reasoning/ml_decision_support/config/__init__.py`
- `agentic_core/L1_cognition/reasoning/ml_decision_support/inference/__init__.py`

### `agentic_core/L3_orchestration/types/` (2)

- `agentic_core/L3_orchestration/types/__init__.py`
- `agentic_core/L3_orchestration/types/contracts/__init__.py`

### `agentic_core/adg/identity/` (2)

- `agentic_core/adg/identity/__init__.py`
- `agentic_core/adg/identity/normalizer.py`

### `agentic_core/evaluation/golden/` (2)

- `agentic_core/evaluation/golden/__init__.py`
- `agentic_core/evaluation/golden/l6_emitter.py`

### `agentic_core/knowledge/enrichment/` (2)

- `agentic_core/knowledge/enrichment/__init__.py`
- `agentic_core/knowledge/enrichment/semantic_enricher.py`

### `agentic_core/knowledge/gates/` (2)

- `agentic_core/knowledge/gates/__init__.py`
- `agentic_core/knowledge/gates/scope_metadata_resolver.py`

### `agentic_core/prompt_governance/optimization/` (2)

- `agentic_core/prompt_governance/optimization/__init__.py`
- `agentic_core/prompt_governance/optimization/optimization_strategy.py`

### `agentic_core/L0_routing/__init__.py/` (1)

- `agentic_core/L0_routing/__init__.py`

### `agentic_core/L1_cognition/__init__.py/` (1)

- `agentic_core/L1_cognition/__init__.py`

### `agentic_core/L2_execution/__init__.py/` (1)

- `agentic_core/L2_execution/__init__.py`

### `agentic_core/L2_execution/_placeholder_smoke.py/` (1)

- `agentic_core/L2_execution/_placeholder_smoke.py`

### `agentic_core/L3_orchestration/__init__.py/` (1)

- `agentic_core/L3_orchestration/__init__.py`

### `agentic_core/L3_orchestration/config/` (1)

- `agentic_core/L3_orchestration/config/__init__.py`

### `agentic_core/L3_orchestration/core/` (1)

- `agentic_core/L3_orchestration/core/summary_adg.py`

### `agentic_core/L3_orchestration/enforcement/` (1)

- `agentic_core/L3_orchestration/enforcement/__init__.py`

### `agentic_core/L4_state/__init__.py/` (1)

- `agentic_core/L4_state/__init__.py`

### `agentic_core/L5_safety/__init__.py/` (1)

- `agentic_core/L5_safety/__init__.py`

### `agentic_core/L5_safety/audit/` (1)

- `agentic_core/L5_safety/audit/__init__.py`

### `agentic_core/L5_safety/enforcement/` (1)

- `agentic_core/L5_safety/enforcement/retrieval/__init__.py`

### `agentic_core/L6_observability/execution/` (1)

- `agentic_core/L6_observability/execution/__init__.py`

### `agentic_core/L_CONTRACTS/__init__.py/` (1)

- `agentic_core/L_CONTRACTS/__init__.py`

### `agentic_core/_compat/__init__.py/` (1)

- `agentic_core/_compat/__init__.py`

### `agentic_core/adg/__init__.py/` (1)

- `agentic_core/adg/__init__.py`

### `agentic_core/adg/adapters/` (1)

- `agentic_core/adg/adapters/__init__.py`

### `agentic_core/adg/ci/` (1)

- `agentic_core/adg/ci/__init__.py`

### `agentic_core/agents/__init__.py/` (1)

- `agentic_core/agents/__init__.py`

### `agentic_core/agents/types/` (1)

- `agentic_core/agents/types/__init__.py`

### `agentic_core/base_agents/__init__.py/` (1)

- `agentic_core/base_agents/__init__.py`

### `agentic_core/case_memory/__init__.py/` (1)

- `agentic_core/case_memory/__init__.py`

### `agentic_core/cloud_native/core/` (1)

- `agentic_core/cloud_native/core/cloud_native_manager.py`

### `agentic_core/config/__init__.py/` (1)

- `agentic_core/config/__init__.py`

### `agentic_core/core/frameworks/` (1)

- `agentic_core/core/frameworks/dependency_manager.py`

### `agentic_core/embeddings/__init__.py/` (1)

- `agentic_core/embeddings/__init__.py`

### `agentic_core/embeddings/bge_runtime.py/` (1)

- `agentic_core/embeddings/bge_runtime.py`

### `agentic_core/embeddings/embedding_factory.py/` (1)

- `agentic_core/embeddings/embedding_factory.py`

### `agentic_core/embeddings/embedding_input_guard.py/` (1)

- `agentic_core/embeddings/embedding_input_guard.py`

### `agentic_core/embeddings/forward_pass.py/` (1)

- `agentic_core/embeddings/forward_pass.py`

### `agentic_core/embeddings/model_loader.py/` (1)

- `agentic_core/embeddings/model_loader.py`

### `agentic_core/embeddings/pipeline.py/` (1)

- `agentic_core/embeddings/pipeline.py`

### `agentic_core/embeddings/tokenizer.py/` (1)

- `agentic_core/embeddings/tokenizer.py`

### `agentic_core/evaluation/__init__.py/` (1)

- `agentic_core/evaluation/__init__.py`

### `agentic_core/evaluation/chunking/` (1)

- `agentic_core/evaluation/chunking/__init__.py`

### `agentic_core/evaluation/schemas/` (1)

- `agentic_core/evaluation/schemas/__init__.py`

### `agentic_core/knowledge/__init__.py/` (1)

- `agentic_core/knowledge/__init__.py`

### `agentic_core/knowledge/engine/` (1)

- `agentic_core/knowledge/engine/__init__.py`

### `agentic_core/knowledge/healing/` (1)

- `agentic_core/knowledge/healing/__init__.py`

### `agentic_core/knowledge/research_cache/` (1)

- `agentic_core/knowledge/research_cache/__init__.py`

### `agentic_core/prompt_governance/__init__.py/` (1)

- `agentic_core/prompt_governance/__init__.py`

### `agentic_core/prompt_governance/meta_prompts/` (1)

- `agentic_core/prompt_governance/meta_prompts/__init__.py`

### `agentic_core/prompt_governance/registry/` (1)

- `agentic_core/prompt_governance/registry/backups/__init__.py`

### `agentic_core/prompt_governance/validation/` (1)

- `agentic_core/prompt_governance/validation/validate_assembly.py`

### `agentic_core/runtime/enforcement/` (1)

- `agentic_core/runtime/enforcement/__init__.py`

### `agentic_core/runtime/engine/` (1)

- `agentic_core/runtime/engine/__init__.py`

### `agentic_core/runtime/exceptions/` (1)

- `agentic_core/runtime/exceptions/__init__.py`

### `agentic_core/runtime/utils/` (1)

- `agentic_core/runtime/utils/__init__.py`

### `agentic_core/seams/__init__.py/` (1)

- `agentic_core/seams/__init__.py`

### `agentic_core/seams/contracts/` (1)

- `agentic_core/seams/contracts/__init__.py`

### `agentic_core/tracing/engines/` (1)

- `agentic_core/tracing/engines/distributed_tracing_coordinator.py`

### `agentic_core/utils/metrics/` (1)

- `agentic_core/utils/metrics/__init__.py`

### `agentic_core/utils/runners/` (1)

- `agentic_core/utils/runners/__init__.py`

### `agentic_core/utils/schemas/` (1)

- `agentic_core/utils/schemas/__init__.py`

### `agentic_core/visualization/engines/` (1)

- `agentic_core/visualization/engines/trace_3d_visualizer.py`

## Reason codes

Every entry above carries the same implicit reason: **G1's role heuristic was not specific enough to assign a narrower role under the fixed enum**. Finer classification requires per-subsystem subject-matter review:

- **ADG subsystems (`adg/extraction`, `adg/analysis`, `adg/applications`, `adg/artifact`, `adg/client`, `adg/processing`)** — dominant contributor. These are internal analyzers and processors of the dependency-graph artefact. Each module is small and single-purpose; role refinement should happen as a dedicated G6 pass grouped by subsystem rather than per-module.
- **Evaluation subsystems (`evaluation/retrieval`, `evaluation/metrics`, `evaluation/judges`, `evaluation/monitoring`, `evaluation/feedback`)** — evaluation internals. G3b will sharpen roles for modules on the exit/eval/replay path; remaining modules belong to G6.
- **Knowledge subsystems (`knowledge/document_loaders`, `knowledge/canonical`, `knowledge/chunking`, etc.)** — knowledge-pipeline primitives. G4 storage pass will illuminate data-store ownership for many of these; G6 will finish role classification.
- **L2_execution inner subsystems (`healers`, `determinism`, `capability`)** — `healers/` base classes likely promote to `healer` role after review; `determinism/` and `capability/` have specialized roles deferrable to G6.
- **L3_orchestration inner subsystems (`inference`, `reasoning`)** — each file's dominant behaviour needs inspection. Candidates for `reasoner` / `orchestrator` / `runtime-scaffold`.
- **Prompt governance subsystems (`scripts`, `security`, `core`)** — likely policy, validator, or runtime-scaffold after inspection.

## Modules that could not be layered or classified as CROSS_CUTTING

**None.** Every `.py` under `agentic_core/` falls either under a layer directory (L0–L6) or is classified as CROSS_CUTTING. The filesystem round-trip passes 2,014/2,014.

## Hand-off to G6

When G6 processes this file:

1. Start with the largest subsystem buckets (`adg/extraction`, `adg/analysis`, `adg/applications`).
2. For each subsystem, decide whether to promote individual modules to sharper roles, or to record the subsystem as intentionally using `role: other` with a subsystem-level purpose note.
3. Update `component_inventory.yaml` in place (this is the only G1 artefact G6 is permitted to modify) and record an erratum line in the YAML header.
4. Produce `G6_taxonomy_cleanup/special_surface_classification.md` with the resulting refinement decisions.
