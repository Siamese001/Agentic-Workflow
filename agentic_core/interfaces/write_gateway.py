"""
agentic_core/interfaces/write_gateway.py

Sovereign Write Gateway interface for L4_state consumption.

Re-exports UniversalWriteGateway and related types so L4_state can
perform write operations without directly importing from L2_execution.

AUTHORITY CONSTRAINTS:
- UniversalWriteGateway is the sole write authority
- All writes must go through signed instruction packets
- No direct file system writes without UWG approval
- Write operations are recorded for audit and replay

USAGE (L4_state):
    from agentic_core.interfaces.write_gateway import (
        UniversalWriteGateway,
        get_write_gateway,
        InstructionPacket,
    )
"""

from __future__ import annotations

from agentic_core.L2_execution.UniversalWriteGateway import UniversalWriteGateway, get_write_gateway
from agentic_core.L2_execution.types.instruction_packet_types import InstructionPacket

__all__ = [
    "UniversalWriteGateway",
    "get_write_gateway",
    "InstructionPacket",
]
