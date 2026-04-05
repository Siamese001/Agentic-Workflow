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

import hashlib
import json
from typing import Sequence

from agentic_core.L2_execution.types.l2_instruction_packet import InstructionPacket
from agentic_core.L2_execution.UniversalWriteGateway import UniversalWriteGateway, get_write_gateway


def compute_replay_key(
    plan_hash: str, tool_calls: Sequence[str], stdout_digest: str, state_diff_hash: str
) -> str:
    """Addendum 2.1: Compute deterministic replay key for a write operation.

    replay_key = SHA256(plan_hash + sorted(tool_calls) + stdout_digest + state_diff_hash)

    All inputs are canonicalised (sorted tool_calls, JSON serialisation) so the
    key is reproducible regardless of call order.
    """
    canonical = json.dumps(
        {
            "plan_hash": plan_hash,
            "tool_calls": sorted(tool_calls),
            "stdout_digest": stdout_digest,
            "state_diff_hash": state_diff_hash,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


__all__ = ["UniversalWriteGateway", "get_write_gateway", "InstructionPacket", "compute_replay_key"]
