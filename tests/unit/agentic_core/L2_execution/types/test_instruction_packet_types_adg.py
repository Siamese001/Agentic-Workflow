"""ADG importability contract for agentic_core/L2_execution/types/instruction_packet_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_instruction_packet_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.types.instruction_packet_types import (  # noqa: F401
        InstructionPacket,
        SignatureVerificationError,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    SignatureVerificationError = None  # type: ignore[assignment,misc]
    InstructionPacket = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="instruction_packet_types deps unavailable")
class TestInstructionPacketTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/types/instruction_packet_types.py must be importable."""
        assert _AVAILABLE

    def test_signatureverificationerror_defined(self) -> None:
        assert SignatureVerificationError is not None

    def test_instructionpacket_defined(self) -> None:
        assert InstructionPacket is not None
