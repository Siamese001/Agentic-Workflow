"""ADG-driven tests for interfaces/execution_contracts.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.interfaces.execution_contracts import (
    _AVAILABLE,
    AgentOutputContract,
    wrap_output,
)


class TestExecutionContracts:
    def test_module_importable(self):
        import agentic_core.interfaces.execution_contracts as m
        assert m is not None

    def test_available_is_bool(self):
        assert isinstance(_AVAILABLE, bool)

    def test_agent_output_contract_present(self):
        # Either available or gracefully set to None
        if _AVAILABLE:
            assert AgentOutputContract is not None
        else:
            assert AgentOutputContract is None

    def test_wrap_output_callable_or_none(self):
        if _AVAILABLE:
            assert callable(wrap_output)
        else:
            assert wrap_output is None
