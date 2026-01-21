"""
L3OrchestrationBaseAgent - Layer 3 Orchestration Base Class

This module provides the base class for all L3 orchestration agents.
All orchestration agents should inherit from this class to ensure
consistent behavior and MRO compliance.

SSOT PRINCIPLE:
    All L3 orchestration agents inherit from L3OrchestrationBaseAgent,
    which inherits from SovereignBaseAgent (the root of the MRO chain).
"""

from __future__ import annotations

from dataclasses import dataclass

from agentic_core.observability.SovereignBaseAgent import SovereignBaseAgent


@dataclass
class L3OrchestrationBaseAgent(SovereignBaseAgent):
    """
    Base class for all L3 Orchestration layer agents.

    Provides:
    - Workflow orchestration capabilities
    - Strategy pattern support
    - Mission execution framework

    All L3 agents should inherit from this class to ensure:
    - Consistent MRO (L3OrchestrationBaseAgent -> SovereignBaseAgent -> MCPHardenedMixin)
    - Standard heal_repository interface
    - Unified logging and telemetry
    """

    _layer: str = "L3_orchestration"
    _healing_enabled: bool = True

    def __post_init__(self) -> None:
        """Initialize L3 orchestration base agent."""
        super().__post_init__()

    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
    ) -> dict[str, int]:
        """
        L3 orchestration healing - coordinates healing across agents.

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
            # L3 orchestration healing - delegate to strategy if available
            return {"skipped": 1, "layer": "L3_orchestration"}
        finally:
            _call_path.discard(agent_name)
