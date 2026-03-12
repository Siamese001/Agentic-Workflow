from __future__ import annotations
'Execution-related types and interfaces.\n\nDefines ExecutionContext, ExecutionResult, and ExecutionPhase for\norchestrating agent execution cycles.\n'
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

class ExecutionPhase(Enum):
    """Phases of the Think-Act-Observe execution cycle."""
    MISSION: Any = 'mission'
    SCENE: Any = 'scene'
    THINK: Any = 'think'
    ACT: Any = 'act'
    OBSERVE: Any = 'observe'
    REFLECT: Any = 'reflect'

@dataclass
class ExecutionContext:
    """Context for agent execution containing mission, scene, and state.

    Attributes:
        mission: The goal or Task to accomplish
        scene: Environmental context and available resources
        state: Current execution state (mutable during execution)
        history: List of previous execution steps
        metadata: Additional context metadata
        previous_phase_signals: Signals from previous phase execution
    """
    mission: str
    scene: dict[str, Any] = field(default_factory=dict)
    state: dict[str, Any] = field(default_factory=dict)
    history: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    previous_phase_signals: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {'mission': self.mission, 'scene': self.scene, 'state': self.state, 'history': self.history, 'metadata': self.metadata, 'previous_phase_signals': self.previous_phase_signals}

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
    output: Any | None = None
    final_state: dict[str, Any] = field(default_factory=dict)
    execution_trace: list[dict[str, Any]] = field(default_factory=list)
    iterations: int = 0
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {'success': self.success, 'output': self.output, 'final_state': self.final_state, 'execution_trace': self.execution_trace, 'iterations': self.iterations, 'errors': self.errors, 'metadata': self.metadata}
