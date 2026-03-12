"""ADG contract tests for L3_orchestration/types/permission_scope_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
from agentic_core.L3_orchestration.types.permission_scope_types import (
    PermissionScope, PermissionAction, Permission,
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
