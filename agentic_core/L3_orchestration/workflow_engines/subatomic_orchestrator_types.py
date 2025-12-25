"""Types and models for subatomic_orchestrator."""
from typing import Any, Dict, List, Optional, Protocol, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
import logging

_logger = logging.getLogger(__name__)


class WorkflowType(Enum):
    """Types of predefined workflows."""


@dataclass
class WorkflowBlueprint:
    """Blueprint for a workflow graph."""

    _name: str
    _description: str
    _roles: List[AgentRole]
    _edges: List[Tuple[AgentRole, AgentRole]]
    _mutation_hooks: Dict[AgentRole, List[Tuple[MutationAction, AgentRole]]] = field(
        default_factory=dict
    )
    _parallel_groups: List[List[AgentRole]] = field(default_factory=list)
