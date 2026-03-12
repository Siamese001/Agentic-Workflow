"""
L0 Path Router - Deterministic Path Selection (GAP-02)

Implements strict Path A/B/C/D dispatch semantics with deterministic logic.
No business logic, no wall-clock usage, pure path selection.
"""
from enum import Enum
from ..engines.assembly_stage import GovernedPayload
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

class Path(Enum):
    """Deterministic path enumeration for L0 routing."""
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'

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
        if not payload.check_ids:
            return Path.A
        if payload.sanitized:
            return Path.B
        if len(payload.check_ids) == 1:
            return Path.C
        return Path.D
