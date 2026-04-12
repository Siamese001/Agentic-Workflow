"""C3 Secure Reading Room - Bounded HITL review.

10C-REQ-139: Bounded packet ONLY no free-form bypass to live ops
Decision Approve Modify Reject
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

from .failure_signal import FailureSignal


class HITLDecisionType(Enum):
    """HITL decision types."""

    APPROVE = auto()
    MODIFY = auto()
    REJECT = auto()


@dataclass
class HITLDecision:
    """HITL decision in secure reading room."""

    decision: HITLDecisionType
    reviewer_id: str
    reviewed_at: float
    modification: dict[str, Any] | None = None
    reason: str = ""
    bounded_packet_id: str = ""


class SecureReadingRoom:
    """C3 Secure Reading Room for human review.

    10C-REQ-139: Bounded packet ONLY no free-form bypass to live ops.

    **HITL DESIGN NOTE**: This implements the "secure reading room" pattern
    where humans review bounded packets without direct live system access.
    """

    def __init__(self) -> None:
        self._pending_reviews: dict[str, dict[str, Any]] = {}
        self._decisions: dict[str, HITLDecision] = {}
        self._packet_counter: int = 0

    def create_bounded_packet(
        self,
        signal: FailureSignal,
        proposed_repair: dict[str, Any],
        context: dict[str, Any],
    ) -> str:
        """Create bounded packet for HITL review.

        10C-REQ-139: Packet is bounded - contains only relevant info,
        no full system access.
        """
        self._packet_counter += 1
        packet_id = f"PACKET-{self._packet_counter:08d}"

        # Bounded packet - limited context, no live system access
        bounded_packet = {
            "packet_id": packet_id,
            "failure_signal": {
                "check_id": signal.check_id,
                "error_code": signal.error_code,
                "error_message": signal.error_message,
                "source_layer": signal.source_layer,
                "operation": signal.operation,
            },
            "proposed_repair": proposed_repair,
            "relevant_context": {  # Limited context only
                k: v for k, v in context.items() if k in ["schema", "validation_rules", "data_sample"]
            },
            "actions_available": ["APPROVE", "MODIFY", "REJECT"],
            "actions_not_available": [
                "direct_system_access",
                "modify_other_requests",
                "disable_governance",
            ],
        }

        self._pending_reviews[packet_id] = bounded_packet
        return packet_id

    def submit_decision(
        self,
        packet_id: str,
        reviewer_id: str,
        decision: HITLDecisionType,
        reason: str = "",
        modification: dict[str, Any] | None = None,
    ) -> HITLDecision:
        """Submit HITL decision for packet.

        10C-REQ-139: APPROVE, MODIFY, or REJECT only.
        """
        import time

        if packet_id not in self._pending_reviews:
            raise ValueError(f"Packet {packet_id} not found")

        hitl_decision = HITLDecision(
            decision=decision,
            reviewer_id=reviewer_id,
            reviewed_at=time.time(),
            modification=modification if decision == HITLDecisionType.MODIFY else None,
            reason=reason,
            bounded_packet_id=packet_id,
        )

        self._decisions[packet_id] = hitl_decision

        # Remove from pending
        del self._pending_reviews[packet_id]

        return hitl_decision

    def get_pending_packets(self) -> list[dict[str, Any]]:
        """Get all pending review packets."""
        return list(self._pending_reviews.values())

    def get_decision(self, packet_id: str) -> HITLDecision | None:
        """Get decision for packet."""
        return self._decisions.get(packet_id)

    def is_approved(self, packet_id: str) -> bool:
        """Check if packet was approved."""
        decision = self._decisions.get(packet_id)
        if not decision:
            return False
        return decision.decision == HITLDecisionType.APPROVE
