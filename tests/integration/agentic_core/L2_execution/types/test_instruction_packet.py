"""Test InstructionPacket functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestInstructionPacket:
    """Test InstructionPacket functionality."""

    def test_instruction_packet_imports(self):
        """Test instruction_packet module imports."""
        from agentic_core import instruction_packet

        assert instruction_packet is not None

    def test_instruction_packet_class(self):
        """Test InstructionPacket class exists."""
        from agentic_core import InstructionPacket

        assert InstructionPacket is not None

    def test_instruction_packet_callable(self):
        """Test instruction_packet functions are callable."""
        from agentic_core import validate_instruction_packet

        assert callable(validate_instruction_packet)
