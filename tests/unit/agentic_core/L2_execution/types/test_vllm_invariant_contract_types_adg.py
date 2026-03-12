"""ADG-driven tests for L2_execution/types/vllm_invariant_contract_types.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.types.vllm_invariant_contract_types import InvariantId


class TestInvariantId:
    def test_is_str_enum(self):
        import enum
        assert issubclass(InvariantId, str)
        assert issubclass(InvariantId, enum.Enum)

    def test_has_expected_members(self):
        members = {m.name for m in InvariantId}
        assert "INV_NO_GPU_IMPORTS_IN_L0_L6" in members
        assert "INV_LOCAL_REQUEST_TEMPERATURE_ZERO" in members

    def test_values_match_names(self):
        for member in InvariantId:
            assert member.value == member.name

    def test_has_at_least_seven_members(self):
        assert len(list(InvariantId)) >= 7
