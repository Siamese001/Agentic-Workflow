---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\eval_spine_phases1_5_hardening_evidence.md'
original_relative_path: 'eval_spine_phases1_5_hardening_evidence.md'
source_sha256: a11bb57efbff68fa666d87a9cd74813d0e224722d0709667263cb2311a6ac6d7
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-06'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Evaluation Spine Phases 1-5 Hardening Evidence

## Scope

Constitutional review and hardening of all Evaluation Spine phases 1-5 per `.windsurfrules`.
New test file: `tests/evaluation/test_hardening.py` (135 tests added).
No source files modified — all gaps were test coverage gaps only.

## INSPECTED_FILES

- `agentic_core/evaluation/metrics/precision_at_k.py`
- `agentic_core/evaluation/metrics/recall_at_k.py`
- `agentic_core/evaluation/metrics/mrr.py`
- `agentic_core/evaluation/metrics/ndcg.py`
- `agentic_core/evaluation/metrics/groundedness.py`
- `agentic_core/evaluation/metrics/answer_correctness.py`
- `agentic_core/evaluation/retrieval/fusion.py`
- `agentic_core/evaluation/retrieval/reranker.py`
- `agentic_core/evaluation/retrieval/profiles.py`
- `agentic_core/evaluation/chunking/policies.py`
- `agentic_core/evaluation/chunking/validators.py`
- `agentic_core/evaluation/monitoring/snapshots.py`
- `agentic_core/evaluation/monitoring/drift_monitor.py`
- `agentic_core/evaluation/monitoring/shadow_eval_runner.py`
- `agentic_core/evaluation/feedback/schemas.py`
- `agentic_core/evaluation/feedback/dpo_batch_builder.py`
- `agentic_core/evaluation/feedback/proposer_bridge.py`
- `tests/evaluation/test_phase1_schemas.py`
- `tests/evaluation/test_phase1_metrics.py`
- `tests/evaluation/test_phase1_runners.py`
- `tests/evaluation/test_phase2_retrieval.py`
- `tests/evaluation/test_phase3_chunking.py`
- `tests/evaluation/test_phase4_monitoring.py`
- `tests/evaluation/test_phase5_feedback.py`
- `tests/evaluation/test_hardening.py`

## Test Execution

Command: `python -m pytest tests/evaluation/ -q --color=no --tb=short`

```
466 passed, 182 warnings in 0.35s
```

Collected: 466
Executed: 466
Difference: 0 (no silent deselection)

Authoritative command exit code: 0

---

## BRANCH_INVENTORY

| # | File | Function/Method | Branch Condition | Expected Outcome | Test Name |
|---|------|-----------------|-----------------|------------------|-----------|
| 1 | `metrics/precision_at_k.py` | `PrecisionAtK.__init__` | `k <= 0` | raise ValueError | `TestPrecisionAtK::test_invalid_k_raises` |
| 2 | `metrics/precision_at_k.py` | `PrecisionAtK.compute` | `not prediction` | return 0.0 | `TestPrecisionAtK::test_empty_prediction_returns_zero` |
| 3 | `metrics/precision_at_k.py` | `PrecisionAtK.compute` | `not ground_truth` | return 0.0 | `TestPrecisionAtK::test_empty_ground_truth_returns_zero` |
| 4 | `metrics/precision_at_k.py` | `PrecisionAtK.compute` | prediction shorter than k | denominator = k | `TestBoundaryPrecisionAtK::test_prediction_k_minus_one` |
| 5 | `metrics/precision_at_k.py` | `PrecisionAtK.compute` | prediction longer than k | truncated to k | `TestBoundaryPrecisionAtK::test_prediction_k_plus_one_truncated` |
| 6 | `metrics/recall_at_k.py` | `RecallAtK.__init__` | `k <= 0` | raise ValueError | `TestRecallAtK::test_invalid_k_raises` |
| 7 | `metrics/recall_at_k.py` | `RecallAtK.compute` | `not prediction` | return 0.0 | `TestRecallAtK::test_empty_prediction_returns_zero` |
| 8 | `metrics/recall_at_k.py` | `RecallAtK.compute` | `not ground_truth` | return 0.0 | `TestRecallAtK::test_empty_ground_truth_returns_zero` |
| 9 | `metrics/recall_at_k.py` | `RecallAtK.compute` | duplicate doc_ids in top_k | deduped before count | `TestRegressionRecallDuplicates::test_regression_three_duplicates_capped_at_one` |
| 10 | `metrics/recall_at_k.py` | `RecallAtK.compute` | relevant doc at position k | counted | `TestBoundaryRecallAtK::test_relevant_at_position_k_exactly` |
| 11 | `metrics/recall_at_k.py` | `RecallAtK.compute` | relevant doc at position k+1 | not counted | `TestBoundaryRecallAtK::test_relevant_at_position_k_plus_one_missed` |
| 12 | `metrics/mrr.py` | `MeanReciprocalRank.compute` | `not prediction` | return 0.0 | `TestMeanReciprocalRank::test_empty_prediction_returns_zero` |
| 13 | `metrics/mrr.py` | `MeanReciprocalRank.compute` | `not ground_truth` | return 0.0 | `TestMeanReciprocalRank::test_empty_ground_truth_returns_zero` |
| 14 | `metrics/mrr.py` | `MeanReciprocalRank.compute` | first hit at rank 1 | return 1.0 | `TestMeanReciprocalRank::test_first_rank_hit` |
| 15 | `metrics/mrr.py` | `MeanReciprocalRank.compute` | no hit in prediction | return 0.0 | `TestMeanReciprocalRank::test_no_hit_returns_zero` |
| 16 | `metrics/mrr.py` | `MeanReciprocalRank.mean` | empty list | return 0.0 | `TestMeanReciprocalRank::test_mean_helper_empty_returns_zero` |
| 17 | `metrics/ndcg.py` | `NDCG.__init__` | `k <= 0` | raise ValueError | `TestNDCG::test_invalid_k_raises` |
| 18 | `metrics/ndcg.py` | `NDCG.compute` | `not prediction` | return 0.0 | `TestNDCG::test_empty_prediction_returns_zero` |
| 19 | `metrics/ndcg.py` | `NDCG.compute` | `context is not None` | use graded relevance | `TestNDCG::test_graded_relevance_via_context` |
| 20 | `metrics/ndcg.py` | `NDCG.compute` | `context is None` and `not ground_truth` | return 0.0 | `TestNDCG::test_empty_ground_truth_returns_zero` |
| 21 | `metrics/ndcg.py` | `NDCG.compute` | all zero graded relevance | IDCG=0, return 0.0 | `TestBoundaryNDCG::test_all_zero_relevance_in_context` |
| 22 | `metrics/groundedness.py` | `Groundedness.compute` | `not prediction` | return 0.0 (guard before judge) | `TestExceptionPathGroundedness::test_judge_returns_zero_for_empty_prediction` |
| 23 | `metrics/groundedness.py` | `Groundedness.compute` | `context is None` | fall back to ground_truth | `TestExceptionPathGroundedness::test_no_judge_none_context_falls_back_to_ground_truth` |
| 24 | `metrics/groundedness.py` | `Groundedness.compute` | `isinstance(context, list)` | join to string | `TestExceptionPathGroundedness::test_judge_receives_context_string` |
| 25 | `metrics/groundedness.py` | `Groundedness.compute` | `not context_str` | return 0.0 | `TestExceptionPathGroundedness::test_no_judge_empty_context_returns_zero_no_exception` |
| 26 | `metrics/groundedness.py` | `Groundedness.compute` | `self._judge is not None` | call judge | `TestGroundedness::test_judge_injection` |
| 27 | `metrics/groundedness.py` | `Groundedness.compute` | judge raises | exception propagates | `TestExceptionPathGroundedness::test_judge_raises_propagates` |
| 28 | `metrics/answer_correctness.py` | `AnswerCorrectness.compute` | `not prediction` | return 0.0 | `TestExceptionPathAnswerCorrectness::test_judge_not_called_when_prediction_empty` |
| 29 | `metrics/answer_correctness.py` | `AnswerCorrectness.compute` | `not ground_truth` | return 0.0 | `TestExceptionPathAnswerCorrectness::test_judge_not_called_when_ground_truth_empty` |
| 30 | `metrics/answer_correctness.py` | `AnswerCorrectness.compute` | `self._judge is not None` | call judge | `TestAnswerCorrectness::test_judge_injection` |
| 31 | `metrics/answer_correctness.py` | `AnswerCorrectness.compute` | judge raises | exception propagates | `TestExceptionPathAnswerCorrectness::test_judge_raises_propagates` |
| 32 | `retrieval/fusion.py` | `ReciprocalRankFusion.__init__` | `k <= 0` | raise ValueError | `TestReciprocalRankFusion::test_invalid_k_raises` |
| 33 | `retrieval/fusion.py` | `ReciprocalRankFusion.merge` | doc in both lists | accumulate RRF score | `TestReciprocalRankFusion::test_shared_doc_accumulates_score` |
| 34 | `retrieval/fusion.py` | `ReciprocalRankFusion.merge` | empty one side | still merges | `TestStatefulRetrievalOrderingStability::test_rrf_empty_one_side_still_returns` |
| 35 | `retrieval/fusion.py` | `ScoreFusion._normalize` | `max_s == min_s` (all equal) | all scores -> 1.0 | `TestScoreFusion::test_all_same_scores_normalized_to_one` |
| 36 | `retrieval/fusion.py` | `ScoreFusion._normalize` | single element list | normalized to 1.0 | `TestDeterministicScoreFusion::test_all_equal_scores_single_element` |
| 37 | `retrieval/fusion.py` | `ScoreFusion.merge` | doc in both lists | appears once | `TestDeterministicScoreFusion::test_doc_in_both_lists_counts_once` |
| 38 | `retrieval/reranker.py` | `HeuristicReranker.rerank` | `not candidates` | return [] | `TestHeuristicReranker::test_empty_candidates` |
| 39 | `retrieval/reranker.py` | `HeuristicReranker.rerank` | `scorer` injected | use custom scorer | `TestHeuristicReranker::test_scorer_injection` |
| 40 | `retrieval/reranker.py` | `HeuristicReranker.rerank` | `top_k` truncation | returns <= top_k | `TestHeuristicReranker::test_top_k_truncation` |
| 41 | `retrieval/reranker.py` | `_query_term_overlap` | `not query_tokens` | return 0.0 | `TestDeterministicHeuristicReranker::test_zero_query_overlap_all_score_zero` |
| 42 | `retrieval/profiles.py` | `RetrievalPipeline.retrieve` | mode == vector_only | call _vector_only | `TestRetrievalPipeline::test_vector_only_uses_vector_retriever` |
| 43 | `retrieval/profiles.py` | `RetrievalPipeline.retrieve` | mode == hybrid | call _hybrid | `TestRetrievalPipeline::test_hybrid_merges_both` |
| 44 | `retrieval/profiles.py` | `RetrievalPipeline.retrieve` | mode == hybrid_reranked | call _hybrid_reranked | `TestRetrievalPipeline::test_hybrid_reranked_applies_reranker` |
| 45 | `retrieval/profiles.py` | `RetrievalPipeline.retrieve` | unknown mode | raise ValueError | `TestRetrievalPipeline::test_unknown_mode_raises` |
| 46 | `retrieval/profiles.py` | `RetrievalPipeline._vector_only` | `vector_retriever is None` | return [] | `TestRetrievalPipeline::test_vector_only_no_retriever_returns_empty` |
| 47 | `retrieval/profiles.py` | `RetrievalPipeline._hybrid` | lexical_retriever None | skip lexical | `TestMatrixRetrievalPipelineMode::test_mode_x_retriever_matrix[hybrid-False-True-False]` |
| 48 | `retrieval/profiles.py` | `RetrievalPipeline._hybrid` | vector_retriever None | skip vector | `TestMatrixRetrievalPipelineMode::test_mode_x_retriever_matrix[hybrid-True-False-False]` |
| 49 | `retrieval/profiles.py` | `make_profile` | mode not in valid_modes | raise ValueError | `TestMakeProfile::test_invalid_mode_raises` |
| 50 | `chunking/policies.py` | `FixedTokenChunkPolicy.__init__` | `chunk_size <= 0` | raise ValueError | `TestFixedTokenChunkPolicy::test_invalid_chunk_size_raises` |
| 51 | `chunking/policies.py` | `FixedTokenChunkPolicy.chunk` | empty document | return [] | `TestFixedTokenChunkPolicy::test_empty_document_returns_empty` |
| 52 | `chunking/policies.py` | `FixedTokenChunkPolicy.chunk` | doc exactly chunk_size | one chunk | `TestStatefulFixedTokenEdge::test_document_length_exactly_chunk_size` |
| 53 | `chunking/policies.py` | `FixedTokenChunkPolicy.chunk` | doc is chunk_size+1 | two chunks | `TestStatefulFixedTokenEdge::test_document_length_chunk_size_plus_one` |
| 54 | `chunking/policies.py` | `OverlapWindowChunkPolicy.__init__` | `chunk_size <= 0` | raise ValueError | `TestOverlapWindowChunkPolicy::test_invalid_chunk_size_raises` |
| 55 | `chunking/policies.py` | `OverlapWindowChunkPolicy.__init__` | `overlap < 0` | raise ValueError | `TestOverlapWindowChunkPolicy::test_negative_overlap_raises` |
| 56 | `chunking/policies.py` | `OverlapWindowChunkPolicy.__init__` | `overlap >= chunk_size` | raise ValueError | `TestOverlapWindowChunkPolicy::test_overlap_gte_chunk_size_raises` |
| 57 | `chunking/policies.py` | `OverlapWindowChunkPolicy.chunk` | step <= 0 guard | step = 1 | `TestStatefulOverlapWindowEdge::test_step_equals_one_produces_dense_overlap` |
| 58 | `chunking/policies.py` | `SemanticChunkPolicy.__init__` | `target_size <= 0` | raise ValueError | `TestSemanticChunkPolicy::test_invalid_target_size_raises` |
| 59 | `chunking/policies.py` | `SemanticChunkPolicy.chunk` | `current_tokens + token_count > target_size and current_group` | flush group | `TestSemanticChunkPolicy::test_groups_by_size` |
| 60 | `chunking/policies.py` | `SemanticChunkPolicy.chunk` | `current_group` not empty at end | append final group | `TestSemanticChunkPolicy::test_last_group_appended` |
| 61 | `monitoring/drift_monitor.py` | `RetrievalDriftMonitor.measure` | `n == 0` | raise ValueError | `TestRetrievalDriftMonitor::test_empty_queries_raises` |
| 62 | `monitoring/drift_monitor.py` | `RetrievalDriftMonitor.measure` | `n == 1` | top_k_stability = 1.0 | `TestBoundaryDriftMonitorThresholds::test_n_equals_one_no_stability_drift` |
| 63 | `monitoring/drift_monitor.py` | `RetrievalDriftMonitor.check_alerts` | `hit_rate < threshold` | emit alert | `TestBoundaryDriftMonitorThresholds::test_hit_rate_one_below_threshold_alerts` |
| 64 | `monitoring/drift_monitor.py` | `RetrievalDriftMonitor.check_alerts` | `hit_rate >= threshold` | no alert | `TestBoundaryDriftMonitorThresholds::test_hit_rate_exactly_at_threshold_no_alert` |
| 65 | `monitoring/drift_monitor.py` | `RetrievalDriftMonitor.check_alerts` | `score_std > threshold` | emit alert | `TestBoundaryDriftMonitorThresholds::test_score_std_one_above_threshold_alerts` |
| 66 | `monitoring/drift_monitor.py` | `RetrievalDriftMonitor.check_alerts` | `score_std <= threshold` | no alert | `TestBoundaryDriftMonitorThresholds::test_score_std_exactly_at_threshold_no_alert` |
| 67 | `monitoring/drift_monitor.py` | `RetrievalDriftMonitor.check_alerts` | `stability < threshold` | emit alert | `TestBoundaryDriftMonitorThresholds::test_stability_one_below_threshold_alerts` |
| 68 | `monitoring/drift_monitor.py` | `RetrievalDriftMonitor.check_alerts` | `stability >= threshold` | no alert | `TestBoundaryDriftMonitorThresholds::test_stability_exactly_at_threshold_no_alert` |
| 69 | `monitoring/drift_monitor.py` | `RetrievalDriftMonitor.measure` | `l4_store is not None` | call _persist | `TestRetrievalDriftMonitor::test_l4_persist_graceful_on_exception` |
| 70 | `monitoring/drift_monitor.py` | `EmbeddingDriftMonitor.measure` | `len(embeddings) == 0` | raise ValueError | `TestEmbeddingDriftMonitor::test_empty_embeddings_raises` |
| 71 | `monitoring/drift_monitor.py` | `EmbeddingDriftMonitor.check_alerts` | `norm_std > threshold` | emit alert | `TestBoundaryEmbeddingDriftMonitor::test_norm_std_one_above_threshold_alerts` |
| 72 | `monitoring/drift_monitor.py` | `EmbeddingDriftMonitor.check_alerts` | `norm_std <= threshold` | no alert | `TestBoundaryEmbeddingDriftMonitor::test_norm_std_exactly_at_threshold_no_alert` |
| 73 | `monitoring/drift_monitor.py` | `EmbeddingDriftMonitor.check_alerts` | `sim_mean < threshold` | emit alert | `TestBoundaryEmbeddingDriftMonitor::test_similarity_one_below_threshold_alerts` |
| 74 | `monitoring/drift_monitor.py` | `EmbeddingDriftMonitor.check_alerts` | `sim_mean >= threshold` | no alert | `TestBoundaryEmbeddingDriftMonitor::test_similarity_exactly_at_threshold_no_alert` |
| 75 | `monitoring/drift_monitor.py` | `EmbeddingDriftMonitor.check_alerts` | `version_mismatch_detected` | emit critical alert | `TestEmbeddingDriftMonitor::test_alert_on_version_mismatch` |
| 76 | `monitoring/drift_monitor.py` | `AnswerQualityMonitor.measure` | `len(groundedness_scores) == 0` | raise ValueError | `TestAnswerQualityMonitor::test_empty_groundedness_scores_raises` |
| 77 | `monitoring/drift_monitor.py` | `AnswerQualityMonitor.check_alerts` | `groundedness < threshold` | emit alert | `TestBoundaryAnswerQualityMonitor::test_groundedness_one_below_threshold_alerts` |
| 78 | `monitoring/drift_monitor.py` | `AnswerQualityMonitor.check_alerts` | `groundedness >= threshold` | no alert | `TestBoundaryAnswerQualityMonitor::test_groundedness_exactly_at_threshold_no_alert` |
| 79 | `monitoring/drift_monitor.py` | `AnswerQualityMonitor.check_alerts` | `hallucination > threshold` | emit alert | `TestBoundaryAnswerQualityMonitor::test_hallucination_one_above_threshold_critical` |
| 80 | `monitoring/drift_monitor.py` | `AnswerQualityMonitor.check_alerts` | `hallucination <= threshold` | no alert | `TestBoundaryAnswerQualityMonitor::test_hallucination_exactly_at_threshold_no_alert` |
| 81 | `monitoring/drift_monitor.py` | `AnswerQualityMonitor.check_alerts` | `override > threshold` | emit alert | `TestBoundaryAnswerQualityMonitor::test_override_one_above_threshold_alerts` |
| 82 | `monitoring/drift_monitor.py` | `AnswerQualityMonitor.check_alerts` | `override <= threshold` | no alert | `TestBoundaryAnswerQualityMonitor::test_override_exactly_at_threshold_no_alert` |
| 83 | `feedback/dpo_batch_builder.py` | `DPOBatchBuilder.__init__` | `min_score_delta < 0` | raise ValueError | `TestDPOBatchBuilder::test_invalid_min_score_delta_raises` |
| 84 | `feedback/dpo_batch_builder.py` | `DPOBatchBuilder.generate_pairs` | empty input | return batch with 0 pairs | `TestDPOBatchBuilder::test_empty_input_returns_empty_batch` |
| 85 | `feedback/dpo_batch_builder.py` | `DPOBatchBuilder.generate_pairs` | only positives | no pairs generated | `TestDPOBatchBuilder::test_only_positives_no_pairs` |
| 86 | `feedback/dpo_batch_builder.py` | `DPOBatchBuilder.generate_pairs` | delta < min_score_delta | pair filtered out | `TestDPOBatchBuilder::test_min_score_delta_filters_pairs` |
| 87 | `feedback/dpo_batch_builder.py` | `DPOBatchBuilder.generate_pairs` | `l4_store is not None` | call persist | `TestExceptionPathL4Persist::test_dpo_builder_persist_called_once` |
| 88 | `feedback/dpo_batch_builder.py` | `DPOBatchBuilder._persist` | persist raises | exception swallowed | `TestExceptionPathL4Persist::test_dpo_builder_persist_ioerror_does_not_raise` |
| 89 | `feedback/proposer_bridge.py` | `EvaluatorProposerBridge.propose` | `eval_report is not None` | extract signals | `TestEvaluatorProposerBridge::test_eval_report_signals_extracted` |
| 90 | `feedback/proposer_bridge.py` | `EvaluatorProposerBridge.propose` | `retrieval_snapshot is not None` | extract signals | `TestEvaluatorProposerBridge::test_retrieval_snapshot_signal_added` |
| 91 | `feedback/proposer_bridge.py` | `EvaluatorProposerBridge.propose` | `answer_snapshot is not None` | extract signals | `TestEvaluatorProposerBridge::test_answer_snapshot_signals_added` |
| 92 | `feedback/proposer_bridge.py` | `EvaluatorProposerBridge.propose` | `dpo_batch is None` | dpo_count = 0 | `TestEvaluatorProposerBridge::test_empty_inputs_produces_proposal` |
| 93 | `feedback/proposer_bridge.py` | `EvaluatorProposerBridge._signals_from_eval` | `delta >= 0` | priority = ok | `TestBoundaryProposerBridgeThresholds::test_delta_exactly_zero_is_ok` |
| 94 | `feedback/proposer_bridge.py` | `EvaluatorProposerBridge._signals_from_eval` | `-0.15 < delta < 0` | priority = warning | `TestBoundaryProposerBridgeThresholds::test_delta_minus_0_14_is_warning_not_critical` |
| 95 | `feedback/proposer_bridge.py` | `EvaluatorProposerBridge._signals_from_eval` | `delta <= -0.15` | priority = critical | `TestBoundaryProposerBridgeThresholds::test_delta_minus_0_15_is_critical` |
| 96 | `feedback/proposer_bridge.py` | `EvaluatorProposerBridge._signals_from_retrieval` | `delta >= 0` | priority = ok | `TestBoundaryProposerBridgeThresholds::test_retrieval_hit_rate_exactly_at_ok_boundary` |
| 97 | `feedback/proposer_bridge.py` | `EvaluatorProposerBridge._signals_from_retrieval` | `delta < -0.20` | priority = critical | `TestBoundaryProposerBridgeThresholds::test_retrieval_hit_critical_threshold` |
| 98 | `feedback/proposer_bridge.py` | `EvaluatorProposerBridge._recommend_actions` | `dpo_count > 10` | trigger_dpo_finetuning | `TestBoundaryProposerBridgeThresholds::test_dpo_count_eleven_triggers_finetuning` |
| 99 | `feedback/proposer_bridge.py` | `EvaluatorProposerBridge._recommend_actions` | `dpo_count == 10` | NOT > 10, accumulate | `TestBoundaryProposerBridgeThresholds::test_dpo_count_exactly_ten_no_finetuning` |
| 100 | `feedback/proposer_bridge.py` | `EvaluatorProposerBridge._recommend_actions` | `dpo_count > 0 and <= 10` | accumulate_more_dpo_pairs | `TestEvaluatorProposerBridge::test_dpo_count_low_suggests_accumulate` |
| 101 | `feedback/proposer_bridge.py` | `EvaluatorProposerBridge._compute_health_score` | `not signals` | return 1.0 | `TestEvaluatorProposerBridge::test_empty_inputs_produces_proposal` |
| 102 | `feedback/proposer_bridge.py` | `EvaluatorProposerBridge._compute_health_score` | all critical | return 0.0 | `TestEvaluatorProposerBridge::test_health_score_zero_when_all_critical` |
| 103 | `feedback/proposer_bridge.py` | `EvaluatorProposerBridge.propose` | `requires_intervention`: critical signal present | True | `TestEvaluatorProposerBridge::test_critical_signal_triggers_intervention` |
| 104 | `feedback/proposer_bridge.py` | `EvaluatorProposerBridge.propose` | `requires_intervention`: health < 0.60 | True | `TestBoundaryProposerBridgeThresholds::test_health_score_boundary_requires_intervention_at_0_59` |
| 105 | `feedback/proposer_bridge.py` | `EvaluatorProposerBridge._persist` | persist raises | exception swallowed | `TestExceptionPathL4Persist::test_bridge_persist_typeerror_does_not_raise` |

---

## ROBUSTNESS_MATRIX

| Surface | Success Tests | Edge Tests | Failure Tests | Recovery Tests | Determinism Tests | Side-Effect Tests |
|---------|--------------|------------|---------------|----------------|-------------------|-------------------|
| `PrecisionAtK.compute` | test_perfect_precision | test_k_equals_one_boundary, test_prediction_k_minus_one | test_empty_prediction_returns_zero, test_invalid_k_raises | N/A | test_deterministic_identical_inputs | N/A |
| `RecallAtK.compute` | test_perfect_recall | test_k_boundary_exact, test_relevant_at_position_k_exactly | test_empty_prediction_returns_zero, test_k_boundary_plus_one | N/A | (identical input → identical output) | test_recall_caps_at_one (dedup side-effect) |
| `MeanReciprocalRank.compute` | test_first_rank_hit | test_fifth_rank_hit | test_no_hit_returns_zero, test_empty_prediction | N/A | test_deterministic_identical_input | N/A |
| `NDCG.compute` | test_perfect_ranking_binary, test_graded_relevance_via_context | test_single_relevant_at_rank_1, test_dcg_formula_exact | test_no_relevant_in_retrieved, test_all_zero_relevance_in_context | N/A | test_deterministic | N/A |
| `Groundedness.compute` | test_perfect_groundedness, test_judge_injection | test_no_judge_none_context_falls_back_to_ground_truth | test_judge_raises_propagates, test_empty_prediction_zero | guard fires before judge | test_no_judge_matrix (parametrized) | test_judge_receives_context_string |
| `AnswerCorrectness.compute` | test_perfect_match | test_partial_overlap | test_empty_prediction, test_judge_raises_propagates | guard fires before judge | test_with_judge_matrix (parametrized) | test_judge_receives_correct_args |
| `_token_f1` | test_perfect, test_f1_identical_inputs_is_one | test_f1_range_always_zero_to_one | test_disjoint_is_zero, test_empty_prediction | N/A | test_f1_is_symmetric | test_f1_contradiction_adding_irrelevant_token |
| `ReciprocalRankFusion.merge` | test_shared_doc_accumulates_score | test_single_result_each_side, test_rrf_empty_one_side | test_result_sorted_by_descending_score | N/A | test_deterministic_same_input, test_normalized_equivalent_input | test_score_metadata_field_set |
| `ScoreFusion.merge` | test_shared_doc_gets_averaged_score | test_all_same_scores_normalized_to_one, test_single_element | test_result_sorted_descending | N/A | test_identical_input_same_output, test_key_order_independence | test_doc_in_both_lists_counts_once |
| `HeuristicReranker.rerank` | test_sorted_by_descending_rerank_score | test_tie_scores_deterministic_order, test_top_k_larger_than_docs | test_empty_candidates | N/A | test_deterministic, test_tie_scores_deterministic_order | test_metadata_includes_rerank_score |
| `RetrievalPipeline.retrieve` | test_vector_only, test_hybrid, test_hybrid_reranked | test_hybrid_only_lexical | test_unknown_mode_raises | test_vector_only_no_retriever | test_mode_x_retriever_matrix (7 cases) | test_to_retrieval_fn_returns_doc_ids |
| `FixedTokenChunkPolicy.chunk` | test_produces_correct_chunks | test_document_length_exactly_chunk_size, test_single_token_document | test_invalid_chunk_size_raises | N/A | (pure function, fixed input) | test_chunk_ids_are_unique |
| `OverlapWindowChunkPolicy.chunk` | test_produces_overlapping_chunks | test_document_shorter_than_chunk_size, test_step_equals_one | test_invalid_chunk_size_raises, test_overlap_gte_chunk_size_raises | step clamped to 1 | (fixed input) | N/A |
| `RetrievalDriftMonitor.measure` | test_full_hit_rate | test_n_equals_one_no_stability_drift | test_empty_queries_raises | N/A | (deterministic formula) | test_l4_persist_graceful_on_exception |
| `RetrievalDriftMonitor.check_alerts` | test_no_alerts_above_thresholds | exact boundary tests (×3) | below threshold alerts (×3) | N/A | N/A | alert fields set correctly |
| `EmbeddingDriftMonitor.check_alerts` | test_no_alerts_when_healthy | exact boundary (×2) | threshold exceeded (×2), version mismatch | N/A | N/A | alert_type set |
| `AnswerQualityMonitor.check_alerts` | test_no_alerts_when_healthy | exact boundary (×3) | threshold exceeded (×3) | empty_flags_handled | N/A | severity field set |
| `DPOBatchBuilder.generate_pairs` | test_one_positive_one_negative | test_min_score_delta boundary, test_delta_filter_matrix | test_invalid_delta_raises, test_only_positives_no_pairs | N/A | test_deterministic_output_order, test_identical_input_same_pairs | test_l4_persist_called, test_persist_no_side_effects_before_completion |
| `EvaluatorProposerBridge.propose` | test_eval_report_signals, test_retrieval_snapshot | exact threshold boundaries (×6) | test_empty_inputs_produces_proposal | persist exception swallowed | test_recommended_actions_sorted | test_bridge_persist_called_once_per_propose |

---

## DEFECT_MODEL

| Defect Class | Targeted By |
|---|---|
| **D1: Recall inflation via duplicate predictions** | `TestRegressionRecallDuplicates` (4 tests), `TestBoundaryRecallAtK` |
| **D2: NDCG zero for graded context with empty ground_truth** | `TestRegressionNDCGGradedContext` (3 tests), `TestBoundaryNDCG` |
| **D3: Threshold off-by-one (>=, <=, >, <)** | `TestBoundaryDriftMonitorThresholds`, `TestBoundaryProposerBridgeThresholds`, `TestBoundaryEmbeddingDriftMonitor`, `TestBoundaryAnswerQualityMonitor` |
| **D4: Silent exception masking in persist paths** | `TestExceptionPathL4Persist` (5 tests) |
| **D5: Judge callable raises propagated vs. swallowed** | `TestExceptionPathGroundedness`, `TestExceptionPathAnswerCorrectness` |
| **D6: Guard clause fires before judge (side-effect safety)** | `test_judge_not_called_when_prediction_empty`, `test_judge_returns_zero_for_empty_prediction` |
| **D7: Non-deterministic ordering (tie-score instability)** | `TestDeterministicRRF`, `TestDeterministicScoreFusion`, `TestDeterministicHeuristicReranker` |
| **D8: ScoreFusion key-order dependency** | `TestDeterministicScoreFusion::test_key_order_independence` |
| **D9: Serialization field loss on roundtrip** | `TestMetamorphicSerializationRoundtrip` (5 tests) |
| **D10: Frozen dataclass mutation not blocked** | `TestContradictionImmutability` (3 tests) |
| **D11: Context-string join for list vs. scalar mismatch** | `TestExceptionPathGroundedness::test_judge_receives_context_string` |
| **D12: RRF score independence from absolute magnitudes** | `TestDeterministicRRF::test_normalized_equivalent_input_same_output` |
| **D13: Chunk boundary off-by-one (doc == chunk_size, +1)** | `TestStatefulFixedTokenEdge` (3 tests) |
| **D14: Overlap step clamped to 1 (step <= 0 guard)** | `TestStatefulOverlapWindowEdge::test_step_equals_one_produces_dense_overlap` |
| **D15: DPO exact dpo_count boundary (> 10 vs == 10)** | `TestBoundaryProposerBridgeThresholds::test_dpo_count_exactly_ten_no_finetuning`, `test_dpo_count_eleven_triggers_finetuning` |
| **D16: token_F1 asymmetry / range violation** | `TestMetamorphicTokenF1` (5 tests) |
| **D17: Matrix coverage: judge × empty-input combinations** | `TestMatrixGroundednessJudge`, `TestMatrixAnswerCorrectnessJudge` |
| **D18: Matrix coverage: pipeline mode × retriever presence** | `TestMatrixRetrievalPipelineMode` (7 parametrized cases) |
| **D19: n=1 stability edge case in drift monitor** | `TestBoundaryDriftMonitorThresholds::test_n_equals_one_no_stability_drift` |
| **D20: Mutation sensitivity: guard removal makes score > 1.0** | `TestRegressionRecallDuplicates::test_mutation_sensitivity_operator_flip` |

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

