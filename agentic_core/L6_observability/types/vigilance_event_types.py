"""
§Wave4.1 — VigilanceEventArtifact: L6 → L0 routing signal.

Deterministic event artifact emitted by TieredVigilanceMonitor (L6)
and consumed by L0 routing intake. Carries semantic_clock from Phase 3.2,
a deterministic vigilance tier, and sorted normalized signal codes.

Forbidden: elapsed_ms, wall-clock timestamps, uuid4.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import Enum
from typing import Any

from agentic_core.L0_maintenance.types.v15_p2_types import (
    SemanticClockSnapshot,
    validate_semantic_clock,
)


class VigilanceSeverity(str, Enum):
    """§Wave4.1 — Routing-oriented vigilance severity.

    Maps to L0 routing decisions:
      LOW/MEDIUM  → L5 rules-first (STANDARD_VALIDATION)
      HIGH/CRITICAL → HIL (HUMAN_ESCALATION)
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Fixed precedence: CRITICAL > HIGH > MEDIUM > LOW
_SEVERITY_PRECEDENCE: dict[VigilanceSeverity, int] = {
    VigilanceSeverity.LOW: 0,
    VigilanceSeverity.MEDIUM: 1,
    VigilanceSeverity.HIGH: 2,
    VigilanceSeverity.CRITICAL: 3,
}


@dataclass(frozen=True)
class VigilanceEventArtifact:
    """§Wave4.1 — Normalized L6 detection event for L0 routing.

    Required fields:
      event_type       — fixed string identifying the event class
      semantic_clock   — required; reuse Phase 3.2 contract
      vigilance_tier   — VigilanceSeverity enum
      signals          — sorted tuple of normalized signal codes
      trace_id         — deterministic (no uuid4)
      policy_config_hash — policy hash if available (empty string default)
    """

    event_type: str
    semantic_clock: SemanticClockSnapshot
    vigilance_tier: VigilanceSeverity
    signals: tuple[str, ...]
    trace_id: str
    policy_config_hash: str = ""

    def __post_init__(self) -> None:
        if not self.event_type:
            raise ValueError("VigilanceEventArtifact: event_type must be non-empty")
        validate_semantic_clock(self.semantic_clock)
        if not isinstance(self.vigilance_tier, VigilanceSeverity):
            raise TypeError(
                f"VigilanceEventArtifact: vigilance_tier must be VigilanceSeverity, "
                f"got {type(self.vigilance_tier).__name__}",
            )
        if not isinstance(self.signals, tuple):
            raise TypeError("VigilanceEventArtifact: signals must be a tuple")
        if list(self.signals) != sorted(self.signals):
            raise ValueError(
                "VigilanceEventArtifact: signals must be sorted",
            )
        if not self.trace_id:
            raise ValueError("VigilanceEventArtifact: trace_id must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        """Deterministic serialization with sorted keys."""
        return {
            "event_type": self.event_type,
            "policy_config_hash": self.policy_config_hash,
            "semantic_clock": self.semantic_clock.to_dict(),
            "signals": list(self.signals),
            "trace_id": self.trace_id,
            "vigilance_tier": self.vigilance_tier.value,
        }


def build_deterministic_trace_id(signals: tuple[str, ...], tick: int) -> str:
    """§Wave4.1 — Deterministic trace_id from signal content + clock tick.

    No uuid4. SHA-256 prefix of canonical input.
    """
    canonical = f"{tick}:{','.join(signals)}"
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


__all__ = [
    "VigilanceEventArtifact",
    "VigilanceSeverity",
    "build_deterministic_trace_id",
]
