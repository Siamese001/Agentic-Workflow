"""
IOrchestratorAgent Protocol - Phase 1 Foundation

Defines the canonical interface for all orchestrator agents in the L3 layer.
This protocol ensures consistent behavior across the 28+ orchestrator implementations.

Usage:
    @runtime_checkable
    class IOrchestratorAgent(Protocol):
        ...

    # Type checking
    if isinstance(agent, IOrchestratorAgent):
        result = agent.run_mission(agents, dry_run=True)

Author: Cascade
Date: January 19, 2026
Phase: 1 - Foundation & Zero-Loss Protocols
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    pass


class ExecutionPhase(str, Enum):
    """Execution phases for orchestrator lifecycle."""

    PLANNING = "planning"
    VALIDATION = "validation"
    EXECUTION = "execution"
    VERIFICATION = "verification"
    ROLLBACK = "rollback"
    COMPLETE = "complete"


@dataclass
class ExecutionContext:
    """
    Context passed through orchestrator execution chain.

    Provides shared state and configuration for mission execution.

    [PHASE 1] Forward-Rolling Recursion Enhancement:
    - accumulated_context: Zero-loss context preservation across successor spawns
    - successor_chain tracking in metadata for DNA integrity
    """

    dry_run: bool = True
    execute: bool = False
    # guardian: allow-magic-config
    max_depth: int = 3
    current_depth: int = 0
    phase: ExecutionPhase = ExecutionPhase.PLANNING
    call_path: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    accumulated_context: dict[str, Any] = field(default_factory=dict)

    # §P4.1 — Semantic handoff fields (additive, default None)
    task_description: str | None = None
    input_data: dict | None = None
    expected_output_schema: dict | None = None
    upstream_summary: str | None = None

    def with_depth(self, new_depth: int) -> ExecutionContext:
        """Create new context with updated depth."""
        return ExecutionContext(
            dry_run=self.dry_run,
            execute=self.execute,
            max_depth=self.max_depth,
            current_depth=new_depth,
            phase=self.phase,
            call_path=self.call_path.copy(),
            metadata=self.metadata.copy(),
            accumulated_context=self.accumulated_context.copy(),
            task_description=self.task_description,
            input_data=self.input_data,
            expected_output_schema=self.expected_output_schema,
            upstream_summary=self.upstream_summary,
        )

    def with_phase(self, new_phase: ExecutionPhase) -> ExecutionContext:
        """Create new context with updated phase."""
        return ExecutionContext(
            dry_run=self.dry_run,
            execute=self.execute,
            max_depth=self.max_depth,
            current_depth=self.current_depth,
            phase=new_phase,
            call_path=self.call_path.copy(),
            metadata=self.metadata.copy(),
            accumulated_context=self.accumulated_context.copy(),
            task_description=self.task_description,
            input_data=self.input_data,
            expected_output_schema=self.expected_output_schema,
            upstream_summary=self.upstream_summary,
        )

    def with_accumulated_context(self, new_context: dict[str, Any]) -> ExecutionContext:
        """Create new context with merged accumulated_context for DNA preservation."""
        merged = self.accumulated_context.copy()
        merged.update(new_context)
        return ExecutionContext(
            dry_run=self.dry_run,
            execute=self.execute,
            max_depth=self.max_depth,
            current_depth=self.current_depth,
            phase=self.phase,
            call_path=self.call_path.copy(),
            metadata=self.metadata.copy(),
            accumulated_context=merged,
            task_description=self.task_description,
            input_data=self.input_data,
            expected_output_schema=self.expected_output_schema,
            upstream_summary=self.upstream_summary,
        )

    def get_successor_chain(self) -> list[str]:
        """Get the current successor chain from metadata."""
        return self.metadata.get("successor_chain", [])

    def get_depth(self) -> int:
        """Get current recursion depth from metadata or current_depth."""
        return self.metadata.get("depth", self.current_depth)


@dataclass
class AgentResult:
    """
    Standardized result from agent execution.

    Provides consistent return format for orchestrator coordination.
    """

    agent_name: str
    success: bool
    violations_found: int = 0
    violations_fixed: int = 0
    errors: int = 0
    skipped: int = 0
    status: str = "UNKNOWN"
    message: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "agent_name": self.agent_name,
            "success": self.success,
            "violations_found": self.violations_found,
            "violations_fixed": self.violations_fixed,
            "errors": self.errors,
            "skipped": self.skipped,
            "status": self.status,
            "message": self.message,
            "metadata": self.metadata,
        }


@dataclass
class MissionResult:
    """
    Aggregated result from mission execution.

    Combines results from multiple agents into a unified summary.
    """

    success: bool
    total_agents: int
    successful_agents: int
    failed_agents: int
    total_violations_found: int = 0
    total_violations_fixed: int = 0
    total_errors: int = 0
    agent_results: list[AgentResult] = field(default_factory=list)
    phase: ExecutionPhase = ExecutionPhase.COMPLETE
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "success": self.success,
            "total_agents": self.total_agents,
            "successful_agents": self.successful_agents,
            "failed_agents": self.failed_agents,
            "total_violations_found": self.total_violations_found,
            "total_violations_fixed": self.total_violations_fixed,
            "total_errors": self.total_errors,
            "agent_results": [r.to_dict() for r in self.agent_results],
            "phase": self.phase.value,
            "metadata": self.metadata,
        }


@runtime_checkable
class IOrchestratorAgent(Protocol):
    """
    Protocol defining the canonical interface for orchestrator agents.

    All orchestrators in L3_orchestration should implement this protocol
    to ensure consistent behavior and enable unified orchestration.

    Methods:
        run_mission: Execute a mission across multiple agents
        run_agent: Execute a single agent with standardized result
        get_available_agents: List agents this orchestrator can coordinate
        validate_mission: Pre-flight validation before execution

    Usage:
        @runtime_checkable allows isinstance() checks at runtime:

        if isinstance(agent, IOrchestratorAgent):
            result = agent.run_mission(agents, dry_run=True)
    """

    def run_mission(
        self,
        agents: list[str],
        dry_run: bool = True,
        execute: bool = False,
        context: ExecutionContext | None = None,
    ) -> MissionResult:
        """
        Execute a mission across multiple agents.

        Args:
            agents: List of agent names to coordinate
            dry_run: If True, only simulate execution
            execute: If True, apply changes (opposite of dry_run)
            context: Optional execution context for shared state

        Returns:
            MissionResult with aggregated outcomes
        """
        ...

    def run_agent(
        self,
        agent_name: str,
        dry_run: bool = True,
        context: ExecutionContext | None = None,
    ) -> AgentResult:
        """
        Execute a single agent with standardized result.

        Args:
            agent_name: Name of the agent to execute
            dry_run: If True, only simulate execution
            context: Optional execution context

        Returns:
            AgentResult with execution outcome
        """
        ...

    def get_available_agents(self) -> list[str]:
        """
        Get list of agents this orchestrator can coordinate.

        Returns:
            List of agent class names
        """
        ...

    def validate_mission(self, agents: list[str], context: ExecutionContext | None = None) -> bool:
        """
        Pre-flight validation before mission execution.

        Args:
            agents: List of agent names to validate
            context: Optional execution context

        Returns:
            True if mission can proceed, False otherwise
        """
        ...


@runtime_checkable
class IHealable(Protocol):
    """
    Protocol for agents that support healing operations.

    This is a superset of the signatures found in BiasAuditorAgent,
    NamingAgent, and other healing-capable agents.

    Zero-Loss Guarantee:
        All existing heal_repository signatures are compatible with this protocol.
        The **kwargs ensures backward compatibility with legacy callers.
    """

    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Repository-level healing method.

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes
            depth: Current recursion depth
            max_depth: Maximum recursion depth
            **kwargs: Additional arguments for backward compatibility

        Returns:
            Dict with healing summary (violations_found, violations_fixed, etc.)
        """
        ...


__all__ = [
    "IOrchestratorAgent",
    "IHealable",
    "ExecutionPhase",
    "ExecutionContext",
    "AgentResult",
    "MissionResult",
]
