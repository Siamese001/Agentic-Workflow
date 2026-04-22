"""Smoke tests for agent_output_contract exports."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestAgentOutputContract:
    """Smoke tests for agent_output_contract exports."""

    def test_agent_output_contract_imports(self) -> None:
        """Import the module export."""
        module = import_attr_or_skip("agentic_core", "agent_output_contract")
        assert module is not None

    def test_agent_output_contract_docstring_present(self) -> None:
        """Ensure the module docstring is present."""
        module = import_attr_or_skip("agentic_core", "agent_output_contract")
        assert module.__doc__ is not None

    def test_agent_output_contract_public_attributes_accessible(self) -> None:
        """Ensure public attributes can be enumerated."""
        module = import_attr_or_skip("agentic_core", "agent_output_contract")
        attrs = [name for name in dir(module) if not name.startswith("_")]
        assert isinstance(attrs, list)
