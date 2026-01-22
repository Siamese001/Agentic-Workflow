from __future__ import annotations
"""
IOrchestrator Protocol - Immutable Contract for Orchestration

This module defines the strict protocol that all orchestrators must implement.
Using runtime_checkable allows isinstance() checks to verify protocol adherence.

USAGE:

    class MyOrchestrator:
        def run_mission(self, context: dict) -> dict:
            ...

        def validate_stability(self, result: dict) -> bool:
            ...

    # Verify adherence
    assert isinstance(MyOrchestrator(), IOrchestrator)

SSOT PRINCIPLE:
    All orchestrators (ConsolidatedOrchestratorAgent, SSOTOrchestratorAgent, etc.)
    must implement this protocol to ensure consistent behavior across the system.
"""

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, guardrail, healer, memory, prompt, validator, workflow
# This boosts alignment detection — review and integrate appropriately


from typing import Any, Protocol, runtime_checkable

from agentic_core.utils.core_extensions.decorators import standard_heal


@runtime_checkable
class IOrchestrator(Protocol):
    """
    Immutable contract for orchestration agents.

    All orchestrators must implement these methods to ensure:
    1. Consistent mission execution interface
    2. Stability validation after mission completion
    3. Predictable return value structures

    This protocol enables:
    - Runtime type checking via isinstance()
    - Static type checking via mypy/pyright
    - Documentation of expected behavior
    """

    def run_mission(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Execute a healing/validation mission across agents.

        Args:
            context: Mission configuration containing:
                - dry_run (bool): If True, only report without fixing
                - execute (bool): If True, execute healing actions
                - agents (List[str], optional): Specific agents to run
                - max_depth (int, optional): Maximum recursion depth

        Returns:
            Mission result dictionary containing:
                - status (str): 'SUCCESS', 'PARTIAL', 'FAILED'
                - total_violations (int): Total violations found
                - total_fixed (int): Total violations fixed
                - agent_results (List[dict]): Per-agent results
                - execution_time_ms (int): Total execution time
                - is_stable (bool): Whether repository is stable
        """
        ...

    def validate_stability(self, result: dict[str, Any]) -> bool:
        """
        Validate whether the mission result indicates a stable repository.

        This method provides a standardized way to determine if the
        repository is in a healthy state after a mission run.

        Args:
            result: Mission result from run_mission()

        Returns:
            True if repository is stable (no unfixed violations, no errors)
            False if repository has issues requiring attention

        Stability Criteria:
            - No unfixed violations (total_violations <= total_fixed)
            - No error status in agent results
            - All critical agents passed
        """
        ...


@runtime_checkable
class IHealable(Protocol):
    """
    Protocol for agents that can heal repository issues.

    This is the canonical signature for heal_repository that all
    healing agents must implement.
    """

    @standard_heal
    def heal_repository(
        self, dry_run: bool = True, execute: bool = False, **kwargs: Any
    ) -> dict[str, Any]:
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


__all__ = [
    "IOrchestrator",
    "IHealable",
    "ITieredAgent",
]