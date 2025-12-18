"""
L5 Orchestrator Types - Resume Engine.

Dataclasses and enums for L5+ autonomous orchestration.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set


@dataclass
class ExecutionPhase:
    """Definition of an execution phase."""
    
    name: str
    agents: List[str]
    execution_mode: str = "sequential"  # sequential, parallel
    is_hard_gate: bool = False
    condition: Optional[Callable] = None


@dataclass
class CycleState:
    """State for a single convergence cycle."""
    
    cycle: int
    modified_items: Set[str] = field(default_factory=set)
    quality_scores: Dict[str, float] = field(default_factory=dict)
    execution_log: List[Dict[str, Any]] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None


@dataclass
class WorkflowSnapshot:
    """Snapshot of workflow state for rollback."""
    
    cycle: int
    context: Dict[str, Any]
    outputs: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
