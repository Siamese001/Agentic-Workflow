"""Test InstructionPacketTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestInstructionPacketTypesAdg:
    """Test InstructionPacketTypesAdg functionality."""

    def test_instruction_packet_types_adg_imports(self):
        """Test instruction_packet_types_adg module imports."""
        from agentic_core import instruction_packet_types_adg

        assert instruction_packet_types_adg is not None

    def test_instruction_packet_types_adg_class(self):
        """Test InstructionPacketTypesAdg class exists."""
        from agentic_core import InstructionPacketTypesAdg

        assert InstructionPacketTypesAdg is not None

    def test_instruction_packet_types_adg_callable(self):
        """Test instruction_packet_types_adg functions are callable."""
        from agentic_core import validate_instruction_packet_types_adg

        assert callable(validate_instruction_packet_types_adg)
