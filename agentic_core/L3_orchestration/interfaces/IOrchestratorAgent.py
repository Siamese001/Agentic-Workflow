from __future__ import annotations
"""
Sovereign Orchestration Interface (ABC)
Location: interfaces/ (CANONICAL PATH)

Phase 2 - Pillar 1: Layering Model
Coordinates between Brain (cognitive) and Hands (action).
L3 Orchestration: Manages the Think-Act-Observe cycle.

Moved to interfaces/ to satisfy architectural SSOT.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from ..workflow_engines.cognitive_plane import ICognitivePlane, PlanningRequest
from ..workflow_engines.action_plane import IActionPlane, ActionRequest
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.L0_maintenance.mixins.subatomic_testing_mixin import SubatomicTestingMixin


class ExecutionPhase(Enum):
    """Phases of execution in the orchestration cycle."""
    MISSION = "mission"
    SCENE = "scene"
    THINK = "think"
    ACT = "act"
    OBSERVE = "observe"
    REFLECT = "reflect"


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
        return {
            "max_iterations": self.max_iterations,
            "enable_reflection": self.enable_reflection,
            "enable_tracing": self.enable_tracing,
            "enable_safety_checks": self.enable_safety_checks,
            "timeout_seconds": self.timeout_seconds,
        }


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
        return {
            "mission": self.mission,
            "scene": self.scene,
            "state": self.state,
            "history": self.history,
            "metadata": self.metadata,
        }


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
        return {
            "success": self.success,
            "output": self.output,
            "final_state": self.final_state,
            "execution_trace": self.execution_trace,
            "iterations": self.iterations,
            "errors": self.errors,
            "metadata": self.metadata,
        }


class IOrchestratorAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin, ABC):
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
    def __init__(
        self,
        cognitive_plane: ICognitivePlane,
        action_plane: IActionPlane,
        config: Optional[OrchestratorConfig] = None,
    ):
        """Initialize orchestrator with planes.
        
        Args:
            cognitive_plane: The brain (planning/reasoning)
            action_plane: The hands (tool execution)
            config: Orchestrator configuration
        """
        pass
    
    @abstractmethod
    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        """Execute a mission through the Think-Act-Observe cycle.
        
        Args:
            context: Execution context with mission and scene
            
        Returns:
            ExecutionResult with output and trace
        """
        pass
    
    @abstractmethod
    async def execute_step(
        self,
        phase: ExecutionPhase,
        context: ExecutionContext,
    ) -> Dict[str, Any]:
        """Execute a single phase of the cycle.
        
        Args:
            phase: Which phase to execute
            context: Current execution context
            
        Returns:
            Phase result
        """
        pass
    
    @abstractmethod
    async def think(self, context: ExecutionContext) -> Dict[str, Any]:
        """Execute the THINK phase (cognitive planning).
        
        Args:
            context: Current execution context
            
        Returns:
            Planning result with next actions
        """
        pass
    
    @abstractmethod
    async def act(
        self,
        actions: List[ActionRequest],
        context: ExecutionContext,
    ) -> List[Dict[str, Any]]:
        """Execute the ACT phase (action execution).
        
        Args:
            actions: Actions to execute
            context: Current execution context
            
        Returns:
            List of action results
        """
        pass
    
    @abstractmethod
    async def observe(
        self,
        action_results: List[Dict[str, Any]],
        context: ExecutionContext,
    ) -> Dict[str, Any]:
        """Execute the OBSERVE phase (result interpretation).
        
        Args:
            action_results: Results from actions
            context: Current execution context
            
        Returns:
            Observations and state updates
        """
        pass
    
    @abstractmethod
    async def should_continue(self, context: ExecutionContext) -> bool:
        """Determine if execution should continue.
        
        Args:
            context: Current execution context
            
        Returns:
            True if should continue, False if done
        """
        pass
    
    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        """Get current orchestrator state.
        
        Returns:
            Current state snapshot
        """
        pass
    
    @abstractmethod
    async def save_state(self, path: str) -> None:
        """Save orchestrator state to disk.
        
        Args:
            path: Path to save state
        """
        pass
    
    @abstractmethod
    async def load_state(self, path: str) -> None:
        """Load orchestrator state from disk.
        
        Args:
            path: Path to load state from
        """
        pass
