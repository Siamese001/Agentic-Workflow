from __future__ import annotations
"""Orchestrator Interface - The Nervous System.

Phase 2 - Pillar 1: Layering Model
Coordinates between Brain (cognitive) and Hands (action).
L3 Orchestration: Manages the Think-Act-Observe cycle.

Updated December 2025: Aligned with SubatomicAgent interface and consolidated orchestrator.
"""
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Protocol
Logger: Any = logging.getLogger(__name__)

@dataclass
class OrchestratorConfig:
    """Configuration for the orchestrator."""
    max_iterations: int = 10
    enable_reflection: bool = True
    enable_tracing: bool = True
    enable_safety_checks: bool = True
    timeout_seconds: int = 300

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {'max_iterations': self.max_iterations, 'enable_reflection': self.enable_reflection, 'enable_tracing': self.enable_tracing, 'enable_safety_checks': self.enable_safety_checks, 'timeout_seconds': self.timeout_seconds}

@dataclass
class ExecutionContext:
    """Context for orchestrated execution."""
    mission: str
    scene: Dict[str, Any] = field(default_factory=dict)
    state: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {'mission': self.mission, 'scene': self.scene, 'state': self.state, 'history': self.history, 'metadata': self.metadata}

@dataclass
class ExecutionResult:
    """Result from orchestrated execution."""
    success: bool
    output: Any = None
    final_state: Dict[str, Any] = field(default_factory=dict)
    execution_trace: List[Dict[str, Any]] = field(default_factory=list)
    iterations: int = 0
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {'success': self.success, 'output': self.output, 'final_state': self.final_state, 'execution_trace': self.execution_trace, 'iterations': self.iterations, 'errors': self.errors, 'metadata': self.metadata}

# NOT_AN_AGENT — Abstract interface/protocol, not a true agent — excluded from agent discovery
class IOrchestratorAgent(HealerMixin, MCPHardenedMixin, SubatomicTestingMixin, ABC):
    """Interface for the Orchestrator (Nervous System).

    The orchestrator coordinates between cognitive and action planes:
    - Manages the Think-Act-Observe cycle
    - Enforces architectural boundaries
    - Provides observability and tracing
    - Handles state persistence

    L3 Constraint: Orchestrator is the ONLY component that can:
    - Call both cognitive and action planes
    - Manage execution state
    - Control the execution loop
    """

    @abstractmethod
    def __init__(self, cognitive_plane: ICognitivePlane, action_plane: IActionPlane, config: Optional[OrchestratorConfig]=None) -> None:
        """Initialize orchestrator with planes.

        Args:
            cognitive_plane: The brain (planning/reasoning)
            action_plane: The hands (tool execution)
            config: Orchestrator configuration
        """

    @abstractmethod
    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        """Execute a mission through the Think-Act-Observe cycle.

        Args:
            context: Execution context with mission and scene

        Returns:
            ExecutionResult with output and trace
        """

    @abstractmethod
    async def execute_step(self, phase: ExecutionPhase, context: ExecutionContext) -> Dict[str, Any]:
        """Execute a single phase of the cycle.

        Args:
            phase: Which phase to execute
            context: Current execution context

        Returns:
            Phase result
        """

    @abstractmethod
    async def think(self, context: ExecutionContext) -> Dict[str, Any]:
        """Execute the THINK phase (cognitive planning).

        Args:
            context: Current execution context

        Returns:
            Planning result with next actions
        """

    @abstractmethod
    async def act(self, actions: List[Any], context: ExecutionContext) -> List[Dict[str, Any]]:
        """Execute the ACT phase (action execution).

        Args:
            actions: Actions to execute
            context: Current execution context

        Returns:
            List of action results
        """

    @abstractmethod
    async def observe(self, action_results: List[Dict[str, Any]], context: ExecutionContext) -> Dict[str, Any]:
        """Execute the OBSERVE phase (result interpretation).

        Args:
            action_results: Results from actions
            context: Current execution context

        Returns:
            Observations and state updates
        """

    @abstractmethod
    async def should_continue(self, context: ExecutionContext) -> bool:
        """Determine if execution should continue.

        Args:
            context: Current execution context

        Returns:
            True if should continue, False if done
        """

    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        """Get current orchestrator state.

        Returns:
            Current state snapshot
        """

    @abstractmethod
    async def save_state(self, path: str) -> None:
        """Save orchestrator state to disk.

        Args:
            path: Path to save state
        """

    @abstractmethod
    async def load_state(self, path: str) -> None:
        """Load orchestrator state from disk.

        Args:
            path: Path to load state from
        """
