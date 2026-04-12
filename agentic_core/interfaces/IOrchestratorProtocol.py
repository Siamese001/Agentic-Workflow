"""
IOrchestratorProtocol - Sovereign Protocol for Orchestration Operations

Zero-Ambiguity Standard: Protocol interface for all orchestrators
Category: PROTOCOL (Abstract interface contract)

This protocol defines the contract for any component that orchestrates
workflows, pipelines, or multi-agent coordination.

Also includes IHealable and ITieredAgent protocols (merged from L5_safety/types/).
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

    async def orchestrate(self, task: str, context: dict[str, Any] | None = None, **kwargs) -> dict[str, Any]:
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


@runtime_checkable
class IHealable(Protocol):
    """
    Protocol for agents that can heal repository issues.

    This is the canonical signature for heal_repository that all
    healing agents must implement.
    """

    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs: Any) -> dict[str, Any]:
        """
        Heal repository issues within this agent's domain.

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, execute healing actions
            **kwargs: Additional agent-specific parameters

        Returns:
            Dictionary with standardized keys:
                - violations_found (int): Number of violations detected
                - violations_fixed (int): Number of violations fixed
                - status (str): 'PASS', 'FAIL', 'ERROR', 'SKIPPED'
                - errors (int): Number of errors encountered
        """
        ...


@runtime_checkable
class ITieredAgent(Protocol):
    """
    Protocol for agents that operate within the tiered execution model.

    Tiered agents have a defined execution tier (0-4) that determines
    when they run in the healing sequence.
    """

    @property
    def tier(self) -> int:
        """
        Return the execution tier for this agent.

        Tier 0: Pre-flight (syntax validation)
        Tier 1: Structural stabilization
        Tier 2: Architectural alignment
        Tier 3: Dynamic healing
        Tier 4: Final safety gate
        """
        ...

    def is_ready(self) -> bool:
        """
        Check if the agent is ready to execute.

        Returns:
            True if all prerequisites are met
            False if agent should be skipped
        """
        ...


__all__ = ["IOrchestratorProtocol", "IHealable", "ITieredAgent"]
