"""Orchestration Handshake Agent - Backward compatibility shim.

DEPRECATED: This agent has been converted to a utility script.
Use agentic_core.L3_orchestration.utils.orchestration_handshake_util instead.

This module maintains backward compatibility by delegating to the utility.
Will be removed in a future release.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L3_orchestration.utils.orchestration_handshake_util import (
    discover_capable_agents as _discover_capable_agents,
    delegate_task as _delegate_task,
    build_handshake_artifact as _build_handshake_artifact,
    HandshakeResult,
)


class OrchestrationHandshakeAgent(SovereignBaseAgent):
    """
    DEPRECATED: Orchestration Handshake Agent - now delegates to orchestration_handshake_util.

    This class is maintained for backward compatibility only.
    New code should use agentic_core.L3_orchestration.utils.orchestration_handshake_util directly.
    """

    def __init__(self, project_root: Path, requesting_agent: str):
        """Initialize OrchestrationHandshakeAgent (deprecated, use orchestration_handshake_util instead)."""
        super().__init__(name="OrchestrationHandshakeAgent", layer="L3")

        warnings.warn(
            "OrchestrationHandshakeAgent is deprecated. Use agentic_core.L3_orchestration.utils.orchestration_handshake_util instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        self.project_root = project_root
        self.requesting_agent = requesting_agent
        self.registry = None  # Set by caller if needed

    def discover_capable_agents(self, task: str, min_confidence: float = 0.85) -> list[dict[str, Any]]:
        """Discover agents/methods capable of handling a task."""
        return _discover_capable_agents(
            registry=self.registry,
            task=task,
            min_confidence=min_confidence,
            use_cache=True,
            redis_client=getattr(self, 'redis', None),
        )

    def delegate_task(
        self,
        task: str,
        args: dict | None = None,
        kwargs: dict | None = None,
        min_confidence: float = 0.85,
    ) -> HandshakeResult:
        """Delegate a task to the most capable agent."""
        return _delegate_task(
            registry=self.registry,
            task=task,
            args=args,
            kwargs=kwargs,
            min_confidence=min_confidence,
        )

    def build_handshake_artifact(
        self,
        trace_id: str,
        chosen: dict[str, Any],
        candidates: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Build a handshake routing decision artifact."""
        return _build_handshake_artifact(trace_id, chosen, candidates)
