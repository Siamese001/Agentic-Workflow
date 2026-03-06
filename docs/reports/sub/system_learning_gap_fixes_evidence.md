# System Learning Gap Fixes — Evidence File

EVIDENCE_COMMIT (40-hex): 8825b0185c1f6a3dc2356be7bb49d5ec039b3ae1
SEALED_FROM (40-hex): 2b9159abd2f3c6a9c4b99c6e5e0acf2c3e1db432

## PHASE SUMMARY

Phase: system_learning gap fixes (GAP-002 through GAP-016)
Branch: meta_learning_wiring
Scope: system_learning module — semantic gap fixes from formal gap analysis

## FILES CHANGED

| File | Change |
|------|--------|
| `system_learning/engines/rca_engine.py` | GAP-002: Add RUNTIME error categories (RuntimeError, AttributeError, TypeError, ValueError, KeyError, IndexError) |
| `system_learning/pipelines/meta_learning_pipeline.py` | GAP-003: DPO before Stage 7; GAP-004: real line count for n_observations; GAP-005: de-nest 8.6/8.7; GAP-007: proposal_only=True default; GAP-008: pre-flight dual injection guard; GAP-009: Stage B component extraction; GAP-010: remove embedding metadata from ChangePackage.changes; GAP-014: FreezeGate; GAP-015: clear _shadow_telemetry_batch; GAP-016: intake_record=None init; BUG-FIX: shadow vector dim matching |
| `system_learning/pipelines/pipeline_factory.py` | GAP-013: wire all missing dependency surfaces |
| `system_learning/invariants/commit_proof_invariant.py` | GAP-011: new CommitProofInvariant class |
| `system_learning/invariants/freeze_gate.py` | GAP-014: new FreezeStateReader + JsonFileBackedFreezeReader |
| `tests/system_learning/test_gap_fixes.py` | New: 83-test comprehensive coverage for all GAPs |
| `tests/unit_min_deps/system_learning/test_meta_learning_pipeline_proposal_only.py` | Update: test_proposal_only_default_is_false → test_proposal_only_default_is_true (GAP-007) |

## TEST RESULTS

### Authoritative Command
```
python -m pytest -q --color=no
```

### Counts
- Collected: 8096
- Executed: 8013 passed, 83 skipped, 7 xfailed
- **Failed: 1** (pre-existing flaky: `test_req267_seam_audit_replay` — order-dependent seam audit state, confirmed failing on baseline before these changes)

### Gap-Fix Tests
```
tests/system_learning/test_gap_fixes.py: 83 passed
```

### Pre-existing Flaky Test
`tests/governance/test_req142_267_seam_audit_determinism.py::test_req267_seam_audit_replay`
- Passes in isolation and within its own file
- Fails only in full-suite due to shared seam audit singleton state mutated by other tests
- **Confirmed pre-existing on baseline** (stash/unstash verification shows same failure before these changes)

## BRANCH_INVENTORY

| File | Function | Branch Condition | Expected Outcome | Test |
|------|----------|-----------------|------------------|------|
| `rca_engine.py` | `classify_line` | `CLASSIFICATION_RULES` regex matches RuntimeError | category=RUNTIME | `TestGap002RuntimeCategory::test_analyze_failures_returns_runtime_category` |
| `rca_engine.py` | `classify_line` | `CLASSIFICATION_RULES` regex matches AttributeError | category=RUNTIME | `TestGap002RuntimeCategory::test_attribute_error_classified` |
| `rca_engine.py` | `classify_line` | `CLASSIFICATION_RULES` regex matches TypeError | category=RUNTIME | `TestGap002RuntimeCategory::test_type_error_classified` |
| `rca_engine.py` | `analyze_failures` | same input twice | identical report_hash | `TestGap002RuntimeCategory::test_analyze_failures_deterministic` |
| `rca_engine.py` | `classify_line` | line has no matching pattern | category=UNKNOWN | `TestRcaRuntimeNegativeControls::test_policy_block_not_reclassified_as_runtime` |
| `meta_learning_pipeline.py` | `run_pipeline` | DPO batch appended before Stage 7 | source ordering correct | `TestGap003DpoBeforeStage7::test_dpo_append_before_validation_loop_in_source` |
| `meta_learning_pipeline.py` | `run_pipeline` | n_observations = len(audit_text.splitlines()) | real line count used | `TestGap004NObservations::test_sufficient_audit_passes` |
| `meta_learning_pipeline.py` | `run_pipeline` | SampleSizePolicy.min_observations not met | PipelineError raised | `TestGap004NObservations::test_insufficient_audit_raises` |
| `meta_learning_pipeline.py` | `run_pipeline` | Stage 8.6 runs independently of 8.5 conditional | pattern analysis called | `TestGap005Stage86And87Independent::test_stage_86_runs_when_optimizer_absent` |
| `meta_learning_pipeline.py` | `PipelineConfig` | proposal_only default | True (fail-safe) | `TestGap007ProposalOnlyDefault::test_default_is_true` |
| `meta_learning_pipeline.py` | `run_pipeline` | version_store present, approval_gate absent | PipelineError with 'approval_gate required' | `TestGap008DualInjectionGuard::test_partial_injection_vs_present_ag_absent` |
| `meta_learning_pipeline.py` | `run_pipeline` | approval_gate present, version_store absent | PipelineError with 'version_store required' | `TestGap008DualInjectionGuard::test_partial_injection_ag_present_vs_absent` |
| `meta_learning_pipeline.py` | `run_pipeline` | both absent, proposal_only=False | PipelineError with 'version_store required' | `TestGap008DualInjectionGuard::test_both_absent_raises_version_store` |
| `commit_proof_invariant.py` | `CommitProofInvariant.verify` | implementation_hash is empty string | InvariantError | `TestGap011CommitProofInvariant::test_empty_hash_raises` |
| `commit_proof_invariant.py` | `CommitProofInvariant.verify` | implementation_hash is CHURN sentinel | InvariantError | `TestGap011CommitProofInvariant::test_churn_hash_raises` |
| `commit_proof_invariant.py` | `CommitProofInvariant.verify` | commit_timestamp_utc <= 0 | InvariantError | `TestGap011CommitProofInvariant::test_zero_timestamp_raises` |
| `commit_proof_invariant.py` | `CommitProofInvariant.from_package` | valid package | invariant created | `TestGap011CommitProofInvariant::test_from_package_valid` |
| `pipeline_factory.py` | `build_pipeline_dependencies` | arbitration_engine unavailable | field is None, no error | `TestGap013FactoryWiring::test_factory_wires_arbitration_engine_field` |
| `pipeline_factory.py` | `build_pipeline_dependencies` | freeze_reader wired | field present in deps | `TestGap013FactoryWiring::test_factory_wires_freeze_reader_field` |
| `freeze_gate.py` | `JsonFileBackedFreezeReader.is_frozen` | runtime_state.json freeze=true | returns True | `TestGap014FreezeGate::test_frozen_state_detected` |
| `meta_learning_pipeline.py` | `run_pipeline` | freeze_reader.is_frozen()=True | PipelineError raised | `TestFreezeGateNegativeControls::test_freeze_gate_blocks_pipeline_execution` |
| `meta_learning_pipeline.py` | `run_pipeline` | freeze_reader.is_frozen()=False | pipeline proceeds | `TestFreezeGateNegativeControls::test_no_freeze_does_not_block` |
| `meta_learning_pipeline.py` | `run_pipeline` | _shadow_telemetry_batch cleared at entry | no cross-run contamination | `TestGap015ShadowBatchCleared::test_shadow_batch_cleared_on_pipeline_entry_via_invalid_window` |
| `meta_learning_pipeline.py` | `run_pipeline` | intake_record initialized to None | no NameError risk | `TestGap016IntakeRecordInitialized::test_stage_8_5_guard_uses_intake_record_not_none` |
| `meta_learning_pipeline.py` | `_retrieve_semantic_context` | shadow_vector dim matches query_vector dim | no np.dot shape error | `TestShadowEmbedderW4B::test_shadow_deterministic_clustering_identical_inputs` |

## BUG FIX: Shadow Vector Dimension Mismatch

**Root cause:** `_retrieve_semantic_context` computed shadow vector via `range(0, 8, 2)` → always 4 elements. When `generate_fallback_vector` returns 16-dim vector (which it always does), `np.dot(query_vector, shadow_vector)` raises `ValueError: shapes (16,) and (4,) not aligned`.

**Fix:** Shadow vector loop now derives dimension from `query_vector.shape[0]`, ensuring dim parity.

**Exposed by:** Order-dependent test execution where earlier tests activate embedding service (via `test_cross_agent_meta_learning_hardening.py`), making `embedding_service.is_disabled()` return False and triggering the shadow computation path.
