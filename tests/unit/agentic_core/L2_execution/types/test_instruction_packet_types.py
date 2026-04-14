"""Smoke tests for instruction_packet_types exports."""

from __future__ import annotations

import pytest

from L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestInstructionPacketTypes:
    """Smoke tests for instruction_packet_types exports."""

    def test_instruction_packet_types_imports(self) -> None:
        """Import the module export."""
        module = import_attr_or_skip("agentic_core", "instruction_packet_types")
        assert module is not None

    def test_instruction_packet_types_class(self) -> None:
        """Import the class export."""
        klass = import_attr_or_skip("agentic_core", "InstructionPacketTypes")
        assert klass is not None

    def test_instruction_packet_types_callable(self) -> None:
        """Import the validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_instruction_packet_types")
        assert callable(validator)
