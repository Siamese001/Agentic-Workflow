"""ADG contract tests for L3_orchestration/types/permission_scope_types.py."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_permission_scope_types_adg")
_emit_applies_guardrail("p0", "test_permission_scope_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_permission_scope_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_permission_scope_types_adg", "state_snapshot")
emit_replay_key("p0", "test_permission_scope_types_adg")
emit_determinism_digest("p0", "test_permission_scope_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
pytestmark = pytest.mark.unit
from agentic_core.L3_orchestration.types.permission_scope_types import (
    Permission,
    PermissionAction,
    PermissionScope,
)


class TestPermissionScope:
    def test_is_enum(self):
        import enum; assert issubclass(PermissionScope, enum.Enum)
    def test_has_tool_execution(self):
        assert PermissionScope.TOOL_EXECUTION.value == "tool_execution"

class TestPermissionAction:
    def test_is_enum(self):
        import enum; assert issubclass(PermissionAction, enum.Enum)
    def test_has_admin(self): assert PermissionAction.ADMIN.value == "admin"

class TestPermission:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(Permission)
    def test_matches_exact(self):
        p = Permission(scope=PermissionScope.DATA_ACCESS, action=PermissionAction.READ, resource="file.py")
        assert p.matches(PermissionScope.DATA_ACCESS, PermissionAction.READ, "file.py")
    def test_admin_matches_any_action(self):
        p = Permission(scope=PermissionScope.DATA_ACCESS, action=PermissionAction.ADMIN, resource="*")
        assert p.matches(PermissionScope.DATA_ACCESS, PermissionAction.DELETE, "*")
