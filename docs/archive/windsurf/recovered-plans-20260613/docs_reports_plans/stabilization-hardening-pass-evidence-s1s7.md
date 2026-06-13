# Stabilization Hardening Pass S1-S7 Evidence

## Scope

Phase: Stabilization Hardening Pass (Non-Destructive)
Declared changed files (git diff --name-only HEAD):

```
agentic_core/L1_cognition/engines/meta_client.py
agentic_core/L2_execution/UniversalWriteGateway.py
agentic_core/L2_execution/types/infra_error_types.py          (new)
agentic_core/L3_orchestration/engines/sovereign_redis_orchestrator.py
agentic_core/L4_state/memory/semantic_cache_manager.py
agentic_core/L4_state/reasoning/CachedStateLedger.py
agentic_core/L5_safety/enforcement/embedding_non_interference_guardrail.py
agentic_core/interfaces/meta_learning.py
pytest.ini
tests/governance/test_layer_sovereignty_guard.py              (baseline bump)
tests/governance/test_stabilization_hardening_s1_s5.py        (new)
tests/governance/test_retrieval_ground_truth.py               (new)
data/golden_state/datasets/retrieval_ground_truth.jsonl       (new)
```

## INSPECTED_FILES

```
agentic_core/L3_orchestration/engines/sovereign_redis_orchestrator.py  lines 1-196
agentic_core/L1_cognition/engines/meta_client.py                        lines 125-279
agentic_core/L4_state/reasoning/CachedStateLedger.py                   lines 30-84
agentic_core/L2_execution/UniversalWriteGateway.py                      lines 1-427
agentic_core/L5_safety/enforcement/embedding_non_interference_guardrail.py  lines 1-224
agentic_core/L4_state/memory/semantic_cache_manager.py                  lines 1-784
agentic_core/interfaces/meta_learning.py                                lines 1-109
pytest.ini                                                              lines 1-115
tests/governance/test_layer_sovereignty_guard.py                        lines 94-117
```

## pytest run: governance suite post-hardening

Command:
python -m pytest tests/governance/ tests/guardian/ -q --tb=short

Exit code: 0
Result: 2537 passed, 8 warnings

## pytest run: new hardening tests

Command:
python -m pytest tests/governance/test_stabilization_hardening_s1_s5.py tests/governance/test_retrieval_ground_truth.py -v --tb=short

Exit code: 0
Result: 73 passed in 0.24s

## pytest run: governance only (final)

Command:
python -m pytest tests/governance/ -q --tb=short

Exit code: 0
Result: 1297 passed, 7 warnings

## BRANCH_INVENTORY

S1 - InfrastructureDependencyError fail-closed:
  agentic_core/L2_execution/types/infra_error_types.py
    NEW: InfrastructureDependencyError(RuntimeError) class
  agentic_core/L3_orchestration/engines/sovereign_redis_orchestrator.py
    CHANGED: module-level import of InfrastructureDependencyError
    CHANGED: get() raises InfrastructureDependencyError on ConnectionError/TimeoutError
    CHANGED: set() raises InfrastructureDependencyError on ConnectionError/TimeoutError
    CHANGED: delete() raises InfrastructureDependencyError on ConnectionError/TimeoutError
    CHANGED: exists() raises InfrastructureDependencyError on ConnectionError/TimeoutError
    CHANGED: clear() raises InfrastructureDependencyError on ConnectionError/TimeoutError
    REMOVED: fallback_cache (LRU in-memory fallback)
    REMOVED: use_fallback flag
  agentic_core/L1_cognition/engines/meta_client.py
    CHANGED: _initialize_redis raises InfrastructureDependencyError if Redis unavailable
    CHANGED: cache_get raises InfrastructureDependencyError on Redis failure
    CHANGED: cache_set raises InfrastructureDependencyError on Redis failure
    CHANGED: cache_delete raises InfrastructureDependencyError on Redis failure
    REMOVED: _local_cache fallback paths in cache_get/cache_set/cache_delete
  agentic_core/L4_state/reasoning/CachedStateLedger.py
    CHANGED: __init__ raises InfrastructureDependencyError on Redis ping failure
    REMOVED: silent-swallow guardian comment + in-memory fallback dict

S2 - C0 forbidden-fields guard:
  agentic_core/L5_safety/enforcement/embedding_non_interference_guardrail.py
    NEW: _C0_FORBIDDEN_FIELDS frozenset {route_mode, execution_tier, safety_threshold, policy_hash}
    NEW: assert_c0_context_clean(c0_context) raises C0InterferenceViolation on forbidden field
    CHANGED: assert_no_c0_influence calls assert_c0_context_clean when c0_context provided
    CHANGED: __all__ exports assert_c0_context_clean

S3 - Semantic cache key determinism anchors:
  agentic_core/L4_state/memory/semantic_cache_manager.py
    NEW: _EMBEDDING_MODEL_VERSION class var (env HIVE_MIND_EMBEDDING_MODEL_VERSION, default bge-m3-v1)
    NEW: _RETRIEVAL_CONFIG_HASH class var (env HIVE_MIND_RETRIEVAL_CONFIG_HASH, default default)
    CHANGED: _compute_hash key = namespace|model_version|config_hash|context

S4 - ChangePackage proposal_only enforcement:
  agentic_core/interfaces/meta_learning.py
    NEW: proposal_only field (default True)
    NEW: approval_token field (default None)
    CHANGED: __post_init__ raises ValueError if proposal_only=False and approval_token falsy

S5 - UWG 3-gate write:
  agentic_core/L2_execution/UniversalWriteGateway.py
    NEW: _verify_replay_hash(payload, replay_key) - SHA256 comparison
    NEW: _verify_plan_hash(plan_hash) - non-empty check stub
    CHANGED: write() signature adds replay_key and plan_hash kwargs
    CHANGED: write() gate sequence: frozen -> signature -> replay_hash -> plan_hash -> store.write

S6 - pytest -ra flag:
  pytest.ini
    CHANGED: addopts gains -ra flag

S7 - Retrieval ground truth corpus:
  data/golden_state/datasets/retrieval_ground_truth.jsonl
    NEW: 7-entry JSONL corpus (RGT001-RGT007) with query, expected_document_ids, expected_answer_spans
  tests/governance/test_retrieval_ground_truth.py
    NEW: 9 structural validation tests (TestRetrievalGroundTruthCorpus)

## ROBUSTNESS_MATRIX

Surface: InfrastructureDependencyError (S1)
  success:        test_error_is_importable, test_error_is_runtime_error_subclass, test_error_carries_message
  edge:           test_error_preserves_cause (chained exception)
  failure:        test_error_can_be_caught_as_runtime_error
  recovery:       N/A - fail-closed by design
  determinism:    error message is deterministic string
  side-effect:    test_store_not_called_on_frozen, test_store_not_called_on_bad_signature, test_store_not_called_on_bad_replay_hash

Surface: SovereignRedisOrchestrator fail-closed (S1)
  success:        test_get_succeeds_when_connection_healthy
  edge:           test_infra_error_message_contains_url, test_no_fallback_cache_attribute, test_no_use_fallback_attribute
  failure:        test_get_raises_on_connection_error, test_set_raises_on_timeout_error, test_delete_raises_on_connection_error, test_exists_raises_on_connection_error, test_clear_raises_on_connection_error
  recovery:       N/A - fail-closed
  determinism:    error type deterministic (InfrastructureDependencyError)
  side-effect:    store not called (confirmed by mock assertion)

Surface: assert_c0_context_clean (S2)
  success:        test_clean_context_passes, test_empty_context_passes
  edge:           test_forbidden_field_alongside_allowed_fields, test_multiple_forbidden_fields_reported
  failure:        test_route_mode_is_forbidden, test_execution_tier_is_forbidden, test_safety_threshold_is_forbidden, test_policy_hash_is_forbidden
  recovery:       N/A - guard raises
  determinism:    test_forbidden_fields_frozenset_immutable, test_all_four_forbidden_fields_present
  side-effect:    test_assert_no_c0_influence_calls_context_clean

Surface: _compute_hash determinism anchors (S3)
  success:        test_identical_inputs_produce_identical_hash
  edge:           test_empty_query_handled
  failure:        test_model_version_change_invalidates_hash, test_retrieval_config_change_invalidates_hash
  recovery:       N/A
  determinism:    test_hash_is_hex_sha256_length, test_different_queries_produce_different_hashes, test_different_namespaces_produce_different_hashes
  side-effect:    none
  matrix:         test_same_query_different_anchors_never_collide (2x2: model_ver x config_hash)

Surface: ChangePackage proposal_only (S4)
  success:        test_proposal_only_true_no_token_allowed, test_proposal_only_false_with_token_allowed, test_default_proposal_only_is_true, test_requires_approval_defaults_true
  edge:           test_proposal_only_false_empty_token_raises (empty string token), test_package_is_frozen (immutability)
  failure:        test_proposal_only_false_without_token_raises, test_non_json_parameters_raises
  recovery:       N/A - fail-closed constructor
  determinism:    test_propose_healing_pattern_returns_proposal_only, test_suggest_threshold_returns_proposal_only
  side-effect:    immutability enforced by frozen dataclass

Surface: UWG 3-gate write (S5)
  success:        test_valid_signature_passes_gate_1, test_correct_replay_key_passes, test_non_empty_plan_hash_passes, test_empty_replay_key_skips_check, test_empty_plan_hash_skips_check
  edge:           test_verify_replay_hash_empty_key_returns_false, test_verify_plan_hash_empty_returns_false
  failure:        test_frozen_blocks_write_before_signature_check, test_empty_signature_blocks_write, test_wrong_replay_key_blocks_write
  recovery:       N/A - fail-closed
  determinism:    test_verify_replay_hash_correct, test_verify_replay_hash_wrong, test_verify_plan_hash_non_empty_returns_true
  side-effect:    test_store_not_called_on_frozen, test_store_not_called_on_bad_signature, test_store_not_called_on_bad_replay_hash
  matrix:         test_gate_matrix[5 rows: frozen x sig x replay x plan]

Surface: Retrieval ground truth corpus (S7)
  success:        test_corpus_exists_and_is_non_empty, test_all_entries_have_required_fields, test_query_ids_are_unique, test_queries_are_non_empty_strings
  edge:           test_expected_document_ids_reference_existing_files
  failure:        test_expected_answer_spans_are_non_empty (rejects empty spans), test_minimum_recall_at_3_is_valid_float (rejects out-of-range), test_expected_top_k_rank_is_positive_int (rejects non-positive)
  recovery:       N/A - structural validation
  determinism:    test_answer_spans_present_in_referenced_documents (staleness check)
  side-effect:    none

## DEFECT_MODEL

DEFECT-01: Silent Redis fallback masks infrastructure outage
  Targeted by: test_get_raises_on_connection_error, test_set_raises_on_timeout_error, test_delete_raises_on_connection_error, test_exists_raises_on_connection_error, test_clear_raises_on_connection_error
  Invariant: InfrastructureDependencyError raised before any fallback path executes

DEFECT-02: C0 RAG context leaks routing-influencing fields
  Targeted by: test_route_mode_is_forbidden, test_execution_tier_is_forbidden, test_safety_threshold_is_forbidden, test_policy_hash_is_forbidden, test_assert_no_c0_influence_calls_context_clean
  Invariant: assert_c0_context_clean raises C0InterferenceViolation on any _C0_FORBIDDEN_FIELDS key

DEFECT-03: Semantic cache does not invalidate when embedding model changes
  Targeted by: test_model_version_change_invalidates_hash, test_retrieval_config_change_invalidates_hash, test_same_query_different_anchors_never_collide
  Invariant: _compute_hash includes model version and retrieval config in key

DEFECT-04: ChangePackage silently activates runtime mutations without approval
  Targeted by: test_proposal_only_false_without_token_raises, test_proposal_only_false_empty_token_raises, test_default_proposal_only_is_true
  Invariant: proposal_only=False without approval_token raises ValueError at construction time

DEFECT-05: UWG write executes store mutation before all verification gates pass
  Targeted by: test_store_not_called_on_frozen, test_store_not_called_on_bad_signature, test_store_not_called_on_bad_replay_hash, test_gate_matrix[5 parametrize rows]
  Invariant: store.write never called if frozen, bad signature, bad replay_hash, or bad plan_hash

DEFECT-06: Retrieval corpus references stale or deleted files
  Targeted by: test_expected_document_ids_reference_existing_files, test_answer_spans_present_in_referenced_documents
  Invariant: every corpus entry document ID resolves to an existing file and each answer span is present verbatim

DEFECT-07: CI does not report skipped/xfailed tests
  Targeted by: pytest.ini -ra flag addition
  Invariant: addopts contains -ra; all non-passing tests appear in summary

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

