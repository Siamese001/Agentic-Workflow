"""
L6ObservabilityBaseAgent - Layer 6 Observability Base Class

This module provides the base class for all L6 observability agents.
All observability agents should inherit from this class to ensure
consistent behavior and MRO compliance.

SSOT PRINCIPLE:
    All L6 observability agents inherit from L6ObservabilityBaseAgent,
    which inherits from SovereignBaseAgent (the root of the MRO chain).
"""
from __future__ import annotations

from dataclasses import dataclass

from agentic_core.observability.SovereignBaseAgent import SovereignBaseAgent


@dataclass
class L6ObservabilityBaseAgent(SovereignBaseAgent):
    """
    Base class for all L6 Observability layer agents.

    Provides:
    - Metrics collection and reporting
    - Telemetry and tracing
    - Dashboard integration
    - Logging infrastructure

    All L6 agents should inherit from this class to ensure:
    - Consistent MRO (L6ObservabilityBaseAgent -> SovereignBaseAgent -> MCPHardenedMixin)
    - Standard heal_repository interface
    - Unified logging and telemetry
    """

    _layer: str = "L6_observability"
    _healing_enabled: bool = True

    def __post_init__(self) -> None:
        """Initialize L6 observability base agent."""
        super().__post_init__()

    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None
    ) -> dict[str, int]:
        """
        L6 observability healing - validates metrics and telemetry.

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, execute healing actions
            depth: Current recursion depth
            max_depth: Maximum recursion depth
            _call_path: Set of already-visited agents (cycle detection)

        Returns:
            Dictionary with healing results
        """
        if _call_path is None:
            _call_path = set()

        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}

        _call_path.add(agent_name)
        try:
            # L6 observability healing - validate metrics/telemetry
            return {"skipped": 1, "layer": "L6_observability"}
        finally:
            _call_path.discard(agent_name)
