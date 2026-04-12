"""Test InstructionPacketTypes functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestInstructionPacketTypes:
    """Test InstructionPacketTypes functionality."""

    def test_instruction_packet_types_imports(self):
        """Test instruction_packet_types module imports."""
        from agentic_core import instruction_packet_types

        assert instruction_packet_types is not None

    def test_instruction_packet_types_class(self):
        """Test InstructionPacketTypes class exists."""
        from agentic_core import InstructionPacketTypes

        assert InstructionPacketTypes is not None

    def test_instruction_packet_types_callable(self):
        """Test instruction_packet_types functions are callable."""
        from agentic_core import validate_instruction_packet_types

        assert callable(validate_instruction_packet_types)
