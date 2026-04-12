"""C0 G1: WHAT KIND OF POWER? - Triage mode selection.

10C-REQ-110: Triage select mode static policy vs runtime enforcement
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class TriageLevel(Enum):
    """Governance triage levels."""

    NONE = auto()  # No governance needed
    STATIC = auto()  # Pre-runtime static checks only
    RUNTIME = auto()  # Full runtime enforcement
    MAXIMUM = auto()  # Strict with human-in-the-loop


class AccessType(Enum):
    """Types of access being requested."""

    READ = auto()
    TOOL = auto()
    MODEL = auto()
    NETWORK = auto()
    MEMORY = auto()
    WRITE = auto()


@dataclass
class TriageResult:
    """Result of triage selection."""

    level: TriageLevel
    access_type: AccessType
    requires_authority: bool
    reason: str


class TriageSelector:
    """C0 G1: Triage mode selector.

    10C-REQ-110: Classify access type read tool model network memory write
    determine appropriate governance level.
    """

    def __init__(self) -> None:
        self._level_rules: dict[AccessType, TriageLevel] = {
            AccessType.READ: TriageLevel.STATIC,
            AccessType.TOOL: TriageLevel.RUNTIME,
            AccessType.MODEL: TriageLevel.RUNTIME,
            AccessType.NETWORK: TriageLevel.MAXIMUM,
            AccessType.MEMORY: TriageLevel.RUNTIME,
            AccessType.WRITE: TriageLevel.MAXIMUM,
        }

    def triage(self, access_type: AccessType, risk_score: float = 0.0) -> TriageResult:
        """Select governance level for access request."""
        base_level = self._level_rules.get(access_type, TriageLevel.RUNTIME)

        # Elevate based on risk score
        if risk_score > 0.8 and base_level.value < TriageLevel.MAXIMUM.value:
            final_level = TriageLevel.MAXIMUM
            reason = f"elevated_risk:{risk_score:.2f}"
        elif risk_score > 0.5 and base_level.value < TriageLevel.RUNTIME.value:
            final_level = TriageLevel.RUNTIME
            reason = f"moderate_risk:{risk_score:.2f}"
        else:
            final_level = base_level
            reason = "default_rule"

        return TriageResult(
            level=final_level,
            access_type=access_type,
            requires_authority=final_level in (TriageLevel.RUNTIME, TriageLevel.MAXIMUM),
            reason=reason,
        )

    def set_level_rule(self, access_type: AccessType, level: TriageLevel) -> None:
        """Set governance level for an access type."""
        self._level_rules[access_type] = level

    def classify_request(self, request: dict[str, Any]) -> AccessType:
        """Classify request to access type."""
        operation = request.get("operation", "").lower()

        if "write" in operation or "commit" in operation:
            return AccessType.WRITE
        elif "tool" in operation or "execute" in operation:
            return AccessType.TOOL
        elif "model" in operation or "llm" in operation:
            return AccessType.MODEL
        elif "network" in operation or "fetch" in operation or "http" in operation:
            return AccessType.NETWORK
        elif "memory" in operation or "store" in operation or "retrieve" in operation:
            return AccessType.MEMORY
        else:
            return AccessType.READ
