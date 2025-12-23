"""
L5 Orchestrator Types - Resume Engine.

Dataclasses and enums for L5+ autonomous orchestration.
"""
from typing import Any, Optional, Protocol, Dict, List
import time


from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set

# Import sovereign types from core
from agentic_core.L3_orchestration.P1_core.orchestration_types import (
    ExecutionPhase,
    ExecutionPhaseSignal,
    WorkflowSnapshot,
)


@dataclass
class CycleState:
    """State for a single convergence cycle."""

    cycle: int
    modified_items: Set[str] = field(default_factory=set)
    quality_scores: Dict[str, float] = field(default_factory=dict)
    execution_log: List[Dict[str, Any]] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
