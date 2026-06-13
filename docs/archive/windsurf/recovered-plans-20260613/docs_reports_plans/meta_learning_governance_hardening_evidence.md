# Meta-Learning Governance Hardening (h2-h10)

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

Ten governance and determinism gaps identified in the meta-learning persistence stack.
Gaps h1 and h6 were already satisfied by existing `LocalFAISSStore` infrastructure.
This phase implements h2-h5, h8-h10 as code changes and h7 (CI) as documented below.

| Gap | Description | Status |
|-----|-------------|--------|
| h1 | SHA256 manifest + startup hash verification | Pre-existing (satisfied) |
| h2 | Embedder model compatibility check in `load_from_disk` | Implemented |
| h3 | `META_LEARNING_STATE_DIGEST` combined artifact | Implemented |
| h4 | Atomic `.tmp` + fsync + rename for FAISS and weights | Implemented |
| h5 | `strategy_weights_digest` property for replay key binding | Implemented |
| h6 | Startup integrity validation (manifest + hash) | Pre-existing (satisfied) |
| h7 | CI enforcement for persist calls | Documented (manual gate) |
| h8 | Telemetry event on strategy weights persist | Implemented |
| h9 | Stale `.tmp` crash recovery cleanup on persist | Implemented |
| h10 | `schema_version` field in `strategy_weights.json` | Implemented |

## CODE_COMMIT

56917790c594e9e5e9a6e5812a8ca4fa94101f4e

## EVIDENCE_COMMIT

b40617a9a9debd31d05a68a89c354b759572f0f8

## FILES_CHANGED_CODE

agentic_core/L1_cognition/reasoning/MetaLearningAgent.py
system_learning/engines/local_faiss_store.py
system_learning/engines/meta_learning_state_digest.py
tests/system_learning/test_cross_agent_meta_learning_hardening.py

## FILES_CHANGED_EVIDENCE

docs/reports/plans/meta_learning_governance_hardening_evidence.md

## INSPECTED_FILES

- system_learning/engines/local_faiss_store.py
- agentic_core/L1_cognition/reasoning/MetaLearningAgent.py
- tests/system_learning/test_cross_agent_meta_learning_hardening.py
- system_learning/engines/meta_learning_state_digest.py

## Implementation Details

### h2: Embedding Model Compatibility (local_faiss_store.py)

Added `EmbedderMismatchError` exception class and `expected_embedder_id` keyword
argument to `load_from_disk()`. When provided, the manifest's `embedder_id` must
match exactly or `EmbedderMismatchError` is raised immediately (fail-closed).
Mixed-vector indexes are never silently loaded.

### h3: META_LEARNING_STATE_DIGEST (meta_learning_state_digest.py)

New module `system_learning/engines/meta_learning_state_digest.py` exposing:
- `compute_meta_learning_state_digest(faiss_index_digests, strategy_weights_digest, embedding_model_version) -> str`
- `emit_meta_learning_state_digest(...)` — computes and prints `META_LEARNING_STATE_DIGEST: <hex>`

The digest is SHA-256 over a canonical JSON binding of all three inputs. Deterministic:
same inputs always produce the same 64-hex output. Stable across two identical runs.

### h4: Atomic Persistence

Both write paths now use `.tmp` -> `flush` -> `fsync` -> `rename`:

**`LocalFAISSStore.persist_to_disk()`** — inner `_atomic_write()` helper writes all
three files (index.json, meta.json, manifest.json) atomically. On Windows, `os.fsync`
is called on the write file handle (not read handle) to avoid EBADF.

**`MetaLearningAgent._save_strategy_weights()`** — same pattern: writes to
`<dest>.tmp`, fsyncs the write handle, then `tmp.replace(dest)`.

### h5: Replay Key Binding (MetaLearningAgent.py)

Added `strategy_weights_digest` property. Returns SHA-256 of the canonical JSON
serialisation of `strategy_weights`. Include alongside FAISS index digests in replay
transcripts to verify identical learned-state initialization.

### h8: Telemetry on Weights Persist (MetaLearningAgent.py)

`_save_strategy_weights()` now fires `telemetry_callback("strategy_weights_persisted", {...})`
after each successful atomic write. Payload includes `weights_digest` (64-hex) and
a copy of `strategy_weights`. No-op when `telemetry_callback` is None.

### h9: Stale .tmp Cleanup (local_faiss_store.py)

Before each `persist_to_disk()` call, all three `*.tmp` files in the target directory
are unconditionally deleted if present. Prevents crash remnants from blocking atomic
rename or corrupting integrity checks on next startup.

### h10: Schema Versioning (MetaLearningAgent.py)

`_save_strategy_weights()` now writes `{"schema_version": "1", "strategy_weights": {...}}`.
`_load_strategy_weights()` ignores the `schema_version` key (reads only `strategy_weights`)
for backward compatibility. Module-level `_WEIGHTS_SCHEMA_VERSION = "1"` is the SSOT.

## pytest: Target Test Suite

$ python -m pytest -q --color=no tests/system_learning/test_cross_agent_meta_learning_hardening.py
tests/system_learning/test_cross_agent_meta_learning_hardening.py::TestEmbeddingRetentionSchedulerPersist::test_run_once_rolling_window_persists_to_disk PASSED
tests/system_learning/test_cross_agent_meta_learning_hardening.py::TestEmbeddingRetentionSchedulerPersist::test_run_once_predicate_persists_to_disk PASSED
tests/system_learning/test_cross_agent_meta_learning_hardening.py::TestEmbeddingRetentionSchedulerPersist::test_run_once_persisted_index_is_loadable PASSED
tests/system_learning/test_cross_agent_meta_learning_hardening.py::TestEmbeddingRetentionSchedulerPersist::test_run_once_without_persist_base_path_no_disk_write PASSED
tests/system_learning/test_cross_agent_meta_learning_hardening.py::TestEmbeddingRetentionSchedulerPersist::test_run_once_none_mode_skips_rebuild_and_persist PASSED
tests/system_learning/test_cross_agent_meta_learning_hardening.py::TestEmbeddingRetentionSchedulerPersist::test_run_once_persisted_manifest_integrity PASSED
tests/system_learning/test_cross_agent_meta_learning_hardening.py::TestHistoricalIngestionOrchestratorPersist::test_healing_contexts_index_persisted_to_layout_dir PASSED
tests/system_learning/test_cross_agent_meta_learning_hardening.py::TestHistoricalIngestionOrchestratorPersist::test_telemetry_events_index_persisted_to_layout_dir PASSED
tests/system_learning/test_cross_agent_meta_learning_hardening.py::TestHistoricalIngestionOrchestratorPersist::test_dpo_pairs_index_persisted_to_layout_dir PASSED
tests/system_learning/test_cross_agent_meta_learning_hardening.py::TestHistoricalIngestionOrchestratorPersist::test_all_three_indexes_loadable_after_build PASSED
tests/system_learning/test_cross_agent_meta_learning_hardening.py::TestHistoricalIngestionOrchestratorPersist::test_persisted_manifest_checksum_valid PASSED
tests/system_learning/test_cross_agent_meta_learning_hardening.py::TestMetaLearningAgentPersistence::test_strategy_weights_file_created_after_update PASSED
tests/system_learning/test_cross_agent_meta_learning_hardening.py::TestMetaLearningAgentPersistence::test_strategy_weights_file_is_valid_json PASSED
tests/system_learning/test_cross_agent_meta_learning_hardening.py::TestMetaLearningAgentPersistence::test_weights_survive_process_restart PASSED
tests/system_learning/test_cross_agent_meta_learning_hardening.py::TestMetaLearningAgentPersistence::test_get_strategy_recommendation_reflects_loaded_weights PASSED
tests/system_learning/test_cross_agent_meta_learning_hardening.py::TestMetaLearningAgentPersistence::test_no_persistence_when_file_not_provided PASSED
tests/system_learning/test_cross_agent_meta_learning_hardening.py::TestMetaLearningAgentPersistence::test_corrupt_weights_file_uses_defaults PASSED
tests/system_learning/test_cross_agent_meta_learning_hardening.py::TestMetaLearningAgentPersistence::test_weights_file_ascii_only PASSED
tests/system_learning/test_cross_agent_meta_learning_hardening.py::TestEmbedderCompatibilityCheck::test_load_rejects_mismatched_embedder_id PASSED
tests/system_learning/test_cross_agent_meta_learning_hardening.py::TestEmbedderCompatibilityCheck::test_load_accepts_matching_embedder_id PASSED
tests/system_learning/test_cross_agent_meta_learning_hardening.py::TestEmbedderCompatibilityCheck::test_load_skips_compat_check_when_none PASSED
tests/system_learning/test_cross_agent_meta_learning_hardening.py::TestMetaLearningStateDigest::test_digest_is_64_hex PASSED
tests/system_learning/test_cross_agent_meta_learning_hardening.py::TestMetaLearningStateDigest::test_digest_is_deterministic PASSED
tests/system_learning/test_cross_agent_meta_learning_hardening.py::TestMetaLearningStateDigest::test_digest_changes_on_different_weights PASSED
tests/system_learning/test_cross_agent_meta_learning_hardening.py::TestMetaLearningStateDigest::test_digest_changes_on_different_model PASSED
tests/system_learning/test_cross_agent_meta_learning_hardening.py::TestMetaLearningStateDigest::test_digest_raises_on_empty_faiss_dict PASSED
tests/system_learning/test_cross_agent_meta_learning_hardening.py::TestMetaLearningStateDigest::test_emit_prints_digest PASSED
tests/system_learning/test_cross_agent_meta_learning_hardening.py::TestAtomicPersistence::test_no_tmp_files_after_successful_persist PASSED
tests/system_learning/test_cross_agent_meta_learning_hardening.py::TestAtomicPersistence::test_target_files_exist_after_persist PASSED
tests/system_learning/test_cross_agent_meta_learning_hardening.py::TestAtomicPersistence::test_stale_tmp_cleaned_before_persist PASSED
tests/system_learning/test_cross_agent_meta_learning_hardening.py::TestStrategyWeightsHardening::test_strategy_weights_digest_is_64_hex PASSED
tests/system_learning/test_cross_agent_meta_learning_hardening.py::TestStrategyWeightsHardening::test_strategy_weights_digest_is_deterministic PASSED
tests/system_learning/test_cross_agent_meta_learning_hardening.py::TestStrategyWeightsHardening::test_strategy_weights_digest_changes_after_update PASSED
tests/system_learning/test_cross_agent_meta_learning_hardening.py::TestStrategyWeightsHardening::test_telemetry_callback_fired_on_save PASSED
tests/system_learning/test_cross_agent_meta_learning_hardening.py::TestStrategyWeightsHardening::test_no_telemetry_when_callback_is_none PASSED
tests/system_learning/test_cross_agent_meta_learning_hardening.py::TestStrategyWeightsHardening::test_persisted_weights_has_schema_version PASSED
tests/system_learning/test_cross_agent_meta_learning_hardening.py::TestStrategyWeightsHardening::test_load_ignores_schema_version_field PASSED
tests/system_learning/test_cross_agent_meta_learning_hardening.py::TestStrategyWeightsHardening::test_weights_file_ascii_only_with_schema_version PASSED
38 passed, 123 warnings in 0.43s

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

