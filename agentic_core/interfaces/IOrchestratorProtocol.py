"""
IOrchestratorProtocol - Sovereign Protocol for Orchestration Operations

Zero-Ambiguity Standard: Protocol interface for all orchestrators
Category: PROTOCOL (Abstract interface contract)

This protocol defines the contract for any component that orchestrates
workflows, pipelines, or multi-agent coordination.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class IOrchestratorProtocol(Protocol):
    """
    Protocol defining the orchestration contract for sovereign agents.

    Any class implementing this protocol MUST provide:
    - orchestrate(): Main orchestration entry point
    - dispatch(): Dispatch work to sub-components
    """

    async def orchestrate(
        self,
        task: str,
        context: dict[str, Any] | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Orchestrate a task across multiple components.

        Args:
            task: Description of the task to orchestrate
            context: Optional context dictionary
            **kwargs: Additional arguments for specific orchestrators

        Returns:
            Dictionary with orchestration results
        """
        ...

    async def dispatch(
        self,
        action: str,
        target: str,
        payload: dict[str, Any] | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Dispatch an action to a specific target component.

        Args:
            action: Action to perform
            target: Target component identifier
            payload: Optional payload data
            **kwargs: Additional arguments

        Returns:
            Dictionary with dispatch results
        """
        ...
