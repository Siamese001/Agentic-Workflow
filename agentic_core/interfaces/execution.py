"""Execution-related types and interfaces.

Defines ExecutionContext, ExecutionResult, and ExecutionPhase for
orchestrating agent execution cycles.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ExecutionPhase(Enum):
    """Phases of the Think-Act-Observe execution cycle."""
    MISSION = "mission"
    SCENE = "scene"
    THINK = "think"
    ACT = "act"
    OBSERVE = "observe"
    REFLECT = "reflect"


@dataclass
class ExecutionContext:
    """Context for agent execution containing mission, scene, and state.
    
    Attributes:
        mission: The goal or task to accomplish
        scene: Environmental context and available resources
        state: Current execution state (mutable during execution)
        history: List of previous execution steps
        metadata: Additional context metadata
    """
    mission: str
    scene: Dict[str, Any] = field(default_factory=dict)
    state: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "mission": self.mission,
            "scene": self.scene,
            "state": self.state,
            "history": self.history,
            "metadata": self.metadata,
        }


@dataclass
class ExecutionResult:
    """Result of an agent execution cycle.
    
    Attributes:
        success: Whether execution completed successfully
        output: Final output/result of execution
        final_state: State at end of execution
        execution_trace: List of execution steps taken
        iterations: Number of Think-Act-Observe iterations
        errors: List of errors encountered
        metadata: Additional result metadata
    """
    success: bool = False
    output: Optional[Any] = None
    final_state: Dict[str, Any] = field(default_factory=dict)
    execution_trace: List[Dict[str, Any]] = field(default_factory=list)
    iterations: int = 0
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "success": self.success,
            "output": self.output,
            "final_state": self.final_state,
            "execution_trace": self.execution_trace,
            "iterations": self.iterations,
            "errors": self.errors,
            "metadata": self.metadata,
        }
