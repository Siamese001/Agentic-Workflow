from __future__ import annotations
'\nOrchestration Types for agentic_core\n\nCore types used across orchestration components to avoid circular dependencies.\n'
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

class ExecutionPhaseSignal(Enum):
    """Signal enum for phase logic checks."""
    PLANNING: Any = auto()
    EXECUTION: Any = auto()
    VALIDATION: Any = auto()
    HEALING: Any = auto()

@dataclass
class ExecutionPhase:
    """Definition of an execution phase - sovereign template for apps to extend."""
    name: str
    agents: list[str]
    execution_mode: str = 'sequential'
    is_hard_gate: bool = False
    condition: Callable | None = None
    signal: ExecutionPhaseSignal = None

    def __post_init__(self):
        """Map name to signal enum for logic checks."""
        if self.signal is None:
            signal_map = {'planning': ExecutionPhaseSignal.PLANNING, 'execution': ExecutionPhaseSignal.EXECUTION, 'validation': ExecutionPhaseSignal.VALIDATION, 'healing': ExecutionPhaseSignal.HEALING}
            self.signal = signal_map.get(self.name.lower(), ExecutionPhaseSignal.PLANNING)

@dataclass
class WorkflowSnapshot:
    """Snapshot of workflow state for rollback - sovereign core type."""
    cycle: int
    context: dict[str, Any]
    outputs: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
