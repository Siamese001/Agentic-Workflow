"""
Execution Trace Types - W5 Implementation

Defines ExecutionTrace structure and plan_hash binding for L3 orchestration.
Ensures deterministic audit trail with canonical JSON formatting.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from agentic_core.L0_routing.engines.assembly_stage import GovernedPayload


def canonical_json(data: dict[str, Any]) -> str:
    """
    Convert dictionary to canonical JSON string.

    Alphabetical key sort, UTF-8, no whitespace variance.
    """
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


@dataclass
class ExecutionTrace:
    """Execution trace for L3 orchestration audit trail."""

    trace_id: str
    plan_hash: str
    actor: str
    target: str | None = None
    diff: dict[str, Any] | None = None
    policy_hash: str = ""
    timestamp: str = ""
    prev_hash: str = ""
    replay_key: str = ""
    governed_payload_hash: str = ""

    def compute_replay_key(self, transcript_hash: str) -> str:
        """
        Compute replay key: SHA256(trace_id + plan_hash + transcript_hash).

        Args:
            transcript_hash: Hash of the execution transcript

        Returns:
            Replay key for deterministic replay verification
        """
        replay_data = f"{self.trace_id}{self.plan_hash}{transcript_hash}"
        return hashlib.sha256(replay_data.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "trace_id": self.trace_id,
            "plan_hash": self.plan_hash,
            "actor": self.actor,
            "target": self.target,
            "diff": self.diff,
            "policy_hash": self.policy_hash,
            "timestamp": self.timestamp,
            "prev_hash": self.prev_hash,
            "replay_key": self.replay_key,
            "governed_payload_hash": self.governed_payload_hash,
        }


def create_execution_trace_skeleton(
    trace_id: str,
    plan_hash: str,
    governed_payload: GovernedPayload,
    actor: str = "L3_Orchestrator",
    target: str | None = None,
) -> ExecutionTrace:
    """
    Create ExecutionTrace skeleton for L3 orchestration.

    Args:
        trace_id: Unique trace identifier
        plan_hash: Hash of the canonical plan
        governed_payload: The governed payload being processed
        actor: Actor performing the orchestration
        target: Target of the orchestration (optional)

    Returns:
        ExecutionTrace with populated skeleton
    """
    from datetime import datetime

    # Compute governed payload hash
    payload_dict = {
        "s0_system": governed_payload.s0_system,
        "i0_instructional": governed_payload.i0_instructional,
        "c0_context": governed_payload.c0_context,
        "u0_user_prompt": governed_payload.u0_user_prompt,
        "manifest_hash": governed_payload.manifest_hash,
        "routing_hash": governed_payload.routing_hash,
    }
    governed_payload_hash = hashlib.sha256(canonical_json(payload_dict).encode("utf-8")).hexdigest()

    trace = ExecutionTrace(
        trace_id=trace_id,
        plan_hash=plan_hash,
        actor=actor,
        target=target,
        governed_payload_hash=governed_payload_hash,
        timestamp=datetime.utcnow().isoformat() + "Z",
    )

    return trace


def compute_plan_hash(plan: dict[str, Any]) -> str:
    """
    Compute SHA256 hash of canonical plan JSON.

    Args:
        plan: Plan dictionary to hash

    Returns:
        SHA256 hash of canonical plan JSON
    """
    canonical = canonical_json(plan)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


__all__ = [
    "ExecutionTrace",
    "create_execution_trace_skeleton",
    "compute_plan_hash",
    "canonical_json",
]
