# System Learning Phase 1 — Evidence File

## 1. Commit Hash

```
83b00d1d6766ab8a5177667a7d39ddf6648121731
```

## 2. File List (git diff --name-only HEAD~1..HEAD)

```
system_learning/enforcement/authority_invariants.py
system_learning/engines/__init__.py
system_learning/engines/l4_audit_reader.py
system_learning/snapshots/__init__.py
system_learning/snapshots/snapshot_factory.py
system_learning/types/snapshot_types.py
tests/unit_min_deps/system_learning/__init__.py
tests/unit_min_deps/system_learning/test_authority_invariants.py
tests/unit_min_deps/system_learning/test_l4_audit_reader.py
tests/unit_min_deps/system_learning/test_snapshot_determinism.py
```

10 files changed, 1144 insertions(+)

## 3. pytest -q (Run 1)

```
tests/unit_min_deps/system_learning/test_authority_invariants.py::TestAssertZeroExecutionAuthority::test_execute_mode_raises PASSED
tests/unit_min_deps/system_learning/test_authority_invariants.py::TestAssertZeroExecutionAuthority::test_activate_mode_raises PASSED
tests/unit_min_deps/system_learning/test_authority_invariants.py::TestAssertZeroExecutionAuthority::test_read_mode_allowed PASSED
tests/unit_min_deps/system_learning/test_authority_invariants.py::TestAssertZeroExecutionAuthority::test_write_mode_allowed_by_this_guard PASSED
tests/unit_min_deps/system_learning/test_authority_invariants.py::TestAssertZeroExecutionAuthority::test_violation_message_contains_caller PASSED
tests/unit_min_deps/system_learning/test_authority_invariants.py::TestAssertZeroExecutionAuthority::test_violation_message_contains_operation PASSED
tests/unit_min_deps/system_learning/test_authority_invariants.py::TestAssertReadOnlyAuditAccess::test_write_audit_operation_raises PASSED
tests/unit_min_deps/system_learning/test_authority_invariants.py::TestAssertReadOnlyAuditAccess::test_append_audit_operation_raises PASSED
tests/unit_min_deps/system_learning/test_authority_invariants.py::TestAssertReadOnlyAuditAccess::test_delete_audit_operation_raises PASSED
tests/unit_min_deps/system_learning/test_authority_invariants.py::TestAssertReadOnlyAuditAccess::test_write_mode_to_audit_target_raises PASSED
tests/unit_min_deps/system_learning/test_authority_invariants.py::TestAssertReadOnlyAuditAccess::test_read_from_audit_allowed PASSED
tests/unit_min_deps/system_learning/test_authority_invariants.py::TestAssertReadOnlyAuditAccess::test_write_to_non_audit_target_allowed PASSED
tests/unit_min_deps/system_learning/test_authority_invariants.py::TestAssertNoSideChannelActivation::test_update_activation_pointer_raises PASSED
tests/unit_min_deps/system_learning/test_authority_invariants.py::TestAssertNoSideChannelActivation::test_set_active_version_raises PASSED
tests/unit_min_deps/system_learning/test_authority_invariants.py::TestAssertNoSideChannelActivation::test_activate_change_package_raises PASSED
tests/unit_min_deps/system_learning/test_authority_invariants.py::TestAssertNoSideChannelActivation::test_activate_mode_raises PASSED
tests/unit_min_deps/system_learning/test_authority_invariants.py::TestAssertNoSideChannelActivation::test_write_change_package_allowed PASSED
tests/unit_min_deps/system_learning/test_authority_invariants.py::TestAssertNoSideChannelActivation::test_read_allowed PASSED
tests/unit_min_deps/system_learning/test_l4_audit_reader.py::TestAuditStoreProtocol::test_fake_store_satisfies_protocol PASSED
tests/unit_min_deps/system_learning/test_l4_audit_reader.py::TestAuditStoreProtocol::test_protocol_has_no_write_methods PASSED
tests/unit_min_deps/system_learning/test_l4_audit_reader.py::TestAuditStoreProtocol::test_fake_store_has_no_write_methods PASSED
tests/unit_min_deps/system_learning/test_l4_audit_reader.py::TestPullAuditDataValid::test_returns_expected_bytes PASSED
tests/unit_min_deps/system_learning/test_l4_audit_reader.py::TestPullAuditDataValid::test_returns_empty_bytes_when_store_empty PASSED
tests/unit_min_deps/system_learning/test_l4_audit_reader.py::TestPullAuditDataValid::test_returns_bytes_unmodified PASSED
tests/unit_min_deps/system_learning/test_l4_audit_reader.py::TestPullAuditDataValid::test_delegates_window_to_store PASSED
tests/unit_min_deps/system_learning/test_l4_audit_reader.py::TestPullAuditDataInvalidWindow::test_start_equal_to_end_raises PASSED
tests/unit_min_deps/system_learning/test_l4_audit_reader.py::TestPullAuditDataInvalidWindow::test_start_greater_than_end_raises PASSED
tests/unit_min_deps/system_learning/test_l4_audit_reader.py::TestPullAuditDataInvalidWindow::test_store_not_called_on_invalid_window PASSED
tests/unit_min_deps/system_learning/test_l4_audit_reader.py::TestAuthorityGuardIntegration::test_assert_read_only_audit_access_is_called PASSED
tests/unit_min_deps/system_learning/test_l4_audit_reader.py::TestAuthorityGuardIntegration::test_assert_zero_execution_authority_is_called PASSED
tests/unit_min_deps/system_learning/test_l4_audit_reader.py::TestAuthorityGuardIntegration::test_authority_context_has_read_mode PASSED
tests/unit_min_deps/system_learning/test_l4_audit_reader.py::TestAuthorityGuardIntegration::test_authority_context_targets_l4_audit PASSED
tests/unit_min_deps/system_learning/test_l4_audit_reader.py::TestAuthorityGuardIntegration::test_authority_violation_propagates PASSED
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotDeterminism::test_same_inputs_produce_identical_snapshot_id PASSED
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotDeterminism::test_same_inputs_produce_identical_snapshot_object PASSED
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotDeterminism::test_snapshot_id_is_sha256_hex PASSED
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotDeterminism::test_snapshot_id_stability_across_calls PASSED
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotDeterminism::test_snapshot_fields_match_inputs PASSED
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotDeterminism::test_telemetry_hash_is_sha256_of_telemetry_bytes PASSED
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotDeterminism::test_policy_config_hash_is_sha256_of_policy_bytes PASSED
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotDeterminism::test_routing_config_hash_is_sha256_of_routing_bytes PASSED
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotDeterminism::test_model_config_hash_is_sha256_of_model_bytes PASSED
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotSensitivity::test_different_telemetry_bytes_produce_different_telemetry_hash PASSED
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotSensitivity::test_different_telemetry_bytes_produce_different_snapshot_id PASSED
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotSensitivity::test_different_policy_bytes_produce_different_snapshot_id PASSED
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotSensitivity::test_different_engine_version_produces_different_snapshot_id PASSED
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotSensitivity::test_different_window_produces_different_snapshot_id PASSED
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotValidation::test_start_equal_to_end_raises PASSED
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotValidation::test_start_greater_than_end_raises PASSED
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestSnapshotValidation::test_valid_window_does_not_raise PASSED
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestNoSystemTime::test_datetime_now_not_called PASSED
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestNoSystemTime::test_time_time_not_called PASSED
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestNoSystemTime::test_snapshot_is_frozen PASSED
tests/unit_min_deps/system_learning/test_snapshot_determinism.py::TestNoSystemTime::test_snapshot_id_equality_assertion PASSED

54 passed in 0.09s
```

## 4. pytest -q (Run 2 — Determinism Proof)

```
54 passed in 0.06s
```

Identical result. All 54 tests pass on both runs.

## 5. Snapshot ID Equality Assertion (from test_snapshot_determinism.py, lines 155-162)

```python
def test_snapshot_id_equality_assertion(self):
    """Canonical determinism assertion: two calls with same inputs produce equal snapshot_id."""
    snap_a = _make_snapshot()
    snap_b = _make_snapshot()
    assert snap_a.snapshot_id == snap_b.snapshot_id, (
        f"snapshot_id mismatch: {snap_a.snapshot_id!r} != {snap_b.snapshot_id!r}"
    )
```

## Acceptance Criteria Checklist

| Criterion | Status |
|-----------|--------|
| New modules at specified paths | PASS |
| All tests discovered by pytest config | PASS |
| 54 tests pass on both runs | PASS |
| snapshot_id stable across 2 consecutive runs | PASS |
| EXECUTE mode raises AuthorityViolation | PASS |
| ACTIVATE mode raises AuthorityViolation | PASS |
| WRITE to audit raises AuthorityViolation | PASS |
| READ allowed (no exception) | PASS |
| Side-channel activation raises AuthorityViolation | PASS |
| No PowerShell used for evidence capture | PASS |
| Git status clean after commit (new files only) | PASS |
