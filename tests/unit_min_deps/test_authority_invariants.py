"""Unit tests for system_learning.enforcement.authority_invariants.

Covers:
  - EXECUTE mode => raises AuthorityViolation
  - ACTIVATE mode => raises AuthorityViolation
  - WRITE to audit surface => raises AuthorityViolation
  - Known audit-write operations => raises AuthorityViolation
  - READ from audit surface => no exception
  - Side-channel activation operations => raises AuthorityViolation
  - Direct ACTIVATE mode in no-side-channel guard => raises AuthorityViolation
"""

import pytest

from system_learning.enforcement.authority_invariants import (
    AuthorityContext,
    AuthorityViolation,
    assert_no_side_channel_activation,
    assert_read_only_audit_access,
    assert_zero_execution_authority,
)

pytestmark = pytest.mark.unit_min_deps


# =============================================================================
# assert_zero_execution_authority
# =============================================================================


class TestAssertZeroExecutionAuthority:
    def test_execute_mode_raises(self):
        ctx = AuthorityContext(
            caller_layer="system_learning.test",
            operation="run_agent",
            target="l2_execution",
            mode="EXECUTE",
        )
        with pytest.raises(AuthorityViolation) as exc_info:
            assert_zero_execution_authority(ctx)
        assert "ZERO_EXECUTION_AUTHORITY" in str(exc_info.value)
        assert "EXECUTE" in str(exc_info.value)

    def test_activate_mode_raises(self):
        ctx = AuthorityContext(
            caller_layer="system_learning.test",
            operation="activate_package",
            target="l4_versioned_store",
            mode="ACTIVATE",
        )
        with pytest.raises(AuthorityViolation) as exc_info:
            assert_zero_execution_authority(ctx)
        assert "ZERO_EXECUTION_AUTHORITY" in str(exc_info.value)
        assert "ACTIVATE" in str(exc_info.value)

    def test_read_mode_allowed(self):
        ctx = AuthorityContext(
            caller_layer="system_learning.test",
            operation="read_audit_slice",
            target="l4_audit",
            mode="READ",
        )
        # Must not raise
        assert_zero_execution_authority(ctx)
        assert True  # no-exception contract

    def test_write_mode_allowed_by_this_guard(self):
        """WRITE is permitted by zero-execution guard (audit guard handles write restrictions)."""
        ctx = AuthorityContext(
            caller_layer="system_learning.test",
            operation="write_change_package",
            target="l4_versioned_store",
            mode="WRITE",
        )
        # Must not raise — WRITE to versioned store is permitted
        assert_zero_execution_authority(ctx)
        assert True  # no-exception contract

    def test_violation_message_contains_caller(self):
        ctx = AuthorityContext(
            caller_layer="system_learning.engines.rca",
            operation="execute_work_contract",
            target="l2_execution",
            mode="EXECUTE",
        )
        with pytest.raises(AuthorityViolation) as exc_info:
            assert_zero_execution_authority(ctx)
        assert "system_learning.engines.rca" in str(exc_info.value)

    def test_violation_message_contains_operation(self):
        ctx = AuthorityContext(
            caller_layer="system_learning.test",
            operation="execute_work_contract",
            target="l2_execution",
            mode="EXECUTE",
        )
        with pytest.raises(AuthorityViolation) as exc_info:
            assert_zero_execution_authority(ctx)
        assert "execute_work_contract" in str(exc_info.value)


# =============================================================================
# assert_read_only_audit_access
# =============================================================================


class TestAssertReadOnlyAuditAccess:
    def test_write_audit_operation_raises(self):
        ctx = AuthorityContext(
            caller_layer="system_learning.test",
            operation="write_audit",
            target="l4_audit",
            mode="WRITE",
        )
        with pytest.raises(AuthorityViolation) as exc_info:
            assert_read_only_audit_access(ctx)
        assert "AUDIT_WRITE_FORBIDDEN" in str(exc_info.value)

    def test_append_audit_operation_raises(self):
        ctx = AuthorityContext(
            caller_layer="system_learning.test",
            operation="append_audit",
            target="l4_audit",
            mode="WRITE",
        )
        with pytest.raises(AuthorityViolation) as exc_info:
            assert_read_only_audit_access(ctx)
        assert "AUDIT_WRITE_FORBIDDEN" in str(exc_info.value)

    def test_delete_audit_operation_raises(self):
        ctx = AuthorityContext(
            caller_layer="system_learning.test",
            operation="delete_audit",
            target="l4_audit",
            mode="WRITE",
        )
        with pytest.raises(AuthorityViolation) as exc_info:
            assert_read_only_audit_access(ctx)
        assert "AUDIT_WRITE_FORBIDDEN" in str(exc_info.value)

    def test_write_mode_to_audit_target_raises(self):
        ctx = AuthorityContext(
            caller_layer="system_learning.test",
            operation="some_operation",
            target="l4_audit_log",
            mode="WRITE",
        )
        with pytest.raises(AuthorityViolation) as exc_info:
            assert_read_only_audit_access(ctx)
        assert "AUDIT_SURFACE_NON_READ" in str(exc_info.value)

    def test_read_from_audit_allowed(self):
        ctx = AuthorityContext(
            caller_layer="system_learning.test",
            operation="read_audit_slice",
            target="l4_audit",
            mode="READ",
        )
        # Must not raise
        assert_read_only_audit_access(ctx)
        assert True  # no-exception contract

    def test_write_to_non_audit_target_allowed(self):
        """Writing to non-audit targets (e.g., versioned store) is not blocked by this guard."""
        ctx = AuthorityContext(
            caller_layer="system_learning.test",
            operation="write_change_package",
            target="l4_versioned_store",
            mode="WRITE",
        )
        # Must not raise — this guard only restricts audit surfaces
        assert_read_only_audit_access(ctx)
        assert True  # no-exception contract


# =============================================================================
# assert_no_side_channel_activation
# =============================================================================


class TestAssertNoSideChannelActivation:
    def test_update_activation_pointer_raises(self):
        ctx = AuthorityContext(
            caller_layer="system_learning.test",
            operation="update_activation_pointer",
            target="l4_versioned_store",
            mode="WRITE",
        )
        with pytest.raises(AuthorityViolation) as exc_info:
            assert_no_side_channel_activation(ctx)
        assert "SIDE_CHANNEL_ACTIVATION_FORBIDDEN" in str(exc_info.value)

    def test_set_active_version_raises(self):
        ctx = AuthorityContext(
            caller_layer="system_learning.test",
            operation="set_active_version",
            target="l4_versioned_store",
            mode="WRITE",
        )
        with pytest.raises(AuthorityViolation) as exc_info:
            assert_no_side_channel_activation(ctx)
        assert "SIDE_CHANNEL_ACTIVATION_FORBIDDEN" in str(exc_info.value)

    def test_activate_change_package_raises(self):
        ctx = AuthorityContext(
            caller_layer="system_learning.test",
            operation="activate_change_package",
            target="l4_versioned_store",
            mode="WRITE",
        )
        with pytest.raises(AuthorityViolation) as exc_info:
            assert_no_side_channel_activation(ctx)
        assert "SIDE_CHANNEL_ACTIVATION_FORBIDDEN" in str(exc_info.value)

    def test_activate_mode_raises(self):
        ctx = AuthorityContext(
            caller_layer="system_learning.test",
            operation="some_operation",
            target="l4_versioned_store",
            mode="ACTIVATE",
        )
        with pytest.raises(AuthorityViolation) as exc_info:
            assert_no_side_channel_activation(ctx)
        assert "DIRECT_ACTIVATE_FORBIDDEN" in str(exc_info.value)

    def test_write_change_package_allowed(self):
        """Writing a ChangePackage to versioned store is permitted (Stage A of 2PC)."""
        ctx = AuthorityContext(
            caller_layer="system_learning.test",
            operation="write_change_package",
            target="l4_versioned_store",
            mode="WRITE",
        )
        # Must not raise
        assert_no_side_channel_activation(ctx)
        assert True  # no-exception contract

    def test_read_allowed(self):
        ctx = AuthorityContext(
            caller_layer="system_learning.test",
            operation="get_change_package",
            target="l4_versioned_store",
            mode="READ",
        )
        # Must not raise
        assert_no_side_channel_activation(ctx)
        assert True  # no-exception contract
