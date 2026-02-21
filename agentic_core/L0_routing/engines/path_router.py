"""
L0 Path Router - Deterministic Path Selection (GAP-02)

Implements strict Path A/B/C/D dispatch semantics with deterministic logic.
No business logic, no wall-clock usage, pure path selection.
"""

from enum import Enum

from ..engines.assembly_stage import GovernedPayload


class Path(Enum):
    """Deterministic path enumeration for L0 routing."""

    A = "A"
    B = "B"
    C = "C"
    D = "D"


class PathRouter:
    """
    Deterministic path router for governed payloads.

    Implements strict Path A/B/C/D dispatch semantics with zero business logic.
    """

    def select_path(self, payload: GovernedPayload) -> Path:
        """
        Select routing path based on payload characteristics.

        Deterministic logic:
        - If payload.check_ids empty → Path.A
        - If payload.sanitized is True → Path.B
        - If len(payload.check_ids) == 1 → Path.C
        - Else → Path.D

        Args:
            payload: GovernedPayload to route

        Returns:
            Selected Path enum value
        """
        # Priority 1: Empty check_ids → Path.A
        if not payload.check_ids:
            return Path.A

        # Priority 2: Sanitized content → Path.B
        if payload.sanitized:
            return Path.B

        # Priority 3: Single check_id → Path.C
        if len(payload.check_ids) == 1:
            return Path.C

        # Priority 4: Multiple check_ids → Path.D
        return Path.D
