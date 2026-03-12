"""ADG-driven tests for L5_safety/reasoning/SecurityManagerAgent.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.reasoning.SecurityManagerAgent import (
    PermissionLevel,
    SecurityAction,
    SecurityManagerAgent,
)


class TestPermissionLevel:
    def test_none_value_0(self):
        assert PermissionLevel.NONE.value == 0

    def test_admin_highest(self):
        assert PermissionLevel.ADMIN.value > PermissionLevel.SECURE_WRITER.value

    def test_all_levels_present(self):
        for level in ("NONE", "SECURE_READER", "SECURE_WRITER", "ADMIN"):
            assert hasattr(PermissionLevel, level)


class TestSecurityAction:
    def test_read_config_member(self):
        assert hasattr(SecurityAction, "READ_CONFIG")

    def test_write_config_member(self):
        assert hasattr(SecurityAction, "WRITE_CONFIG")

    def test_create_checkpoint_member(self):
        assert hasattr(SecurityAction, "CREATE_CHECKPOINT")


class TestSecurityManagerAgent:
    def test_creates(self):
        agent = SecurityManagerAgent()
        assert agent is not None

    def test_has_heal_repository(self):
        assert hasattr(SecurityManagerAgent, "heal_repository")
