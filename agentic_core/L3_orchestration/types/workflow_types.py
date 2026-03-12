from __future__ import annotations
'Types and models for SubatomicOrchestratorAgent.'
import logging
from dataclasses import dataclass, field
from enum import Enum
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
_logger = logging.getLogger(__name__)

class WorkflowType(Enum):
    """Types of predefined workflows."""

@dataclass
class WorkflowBlueprint:
    """Blueprint for a workflow graph."""
    _name: str
    _description: str
    _roles: list[AgentRole]
    _edges: list[tuple[AgentRole, AgentRole]]
    _mutation_hooks: dict[AgentRole, list[tuple[MutationAction, AgentRole]]] = field(default_factory=dict)
    _parallel_groups: list[list[AgentRole]] = field(default_factory=list)
