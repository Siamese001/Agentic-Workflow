"""
L5 Orchestrator Types - Outreach Engine.

Dataclasses and enums for L5+ autonomous orchestration.
"""
from typing import Any, Optional, Protocol, Dict, List
import time


from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set


@dataclass
class OutreachExecutionPhase:
    """Definition of an outreach execution phase."""

    name: str
    agents: List[str]
    execution_mode: str = "sequential"  # sequential, parallel
    is_hard_gate: bool = False
    condition: Optional[Callable] = None


@dataclass
class OutreachCycleState:
    """State for a single convergence cycle."""

    cycle: int
    modified_items: Set[str] = field(default_factory=set)
    quality_scores: Dict[str, float] = field(default_factory=dict)
    execution_log: List[Dict[str, Any]] = field(default_factory=list)
    messages_generated: int = 0
    personalization_score: float = 0.0
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None


@dataclass
class OutreachSnapshot:
    """Snapshot of outreach state for rollback."""

    cycle: int
    context: Dict[str, Any]
    outputs: Dict[str, Any]
    messages: List[Dict[str, Any]]
    timestamp: datetime = field(default_factory=datetime.utcnow)
