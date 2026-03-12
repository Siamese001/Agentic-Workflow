"""ADG-driven tests for L2_execution/types/heal_contract_types.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.types.heal_contract_types import HealStatus


class TestHealStatus:
    def test_is_str_enum(self):
        import enum
        assert issubclass(HealStatus, str)
        assert issubclass(HealStatus, enum.Enum)

    def test_has_members(self):
        members = list(HealStatus)
        assert len(members) > 0

    def test_members_are_strings(self):
        for member in HealStatus:
            assert isinstance(member.value, str)
