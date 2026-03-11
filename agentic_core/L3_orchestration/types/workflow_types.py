from __future__ import annotations

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""Types and models for SubatomicOrchestratorAgent."""
import logging
from dataclasses import dataclass, field
from enum import Enum

_logger = logging.getLogger(__name__)


# NAMING FIXED: WorkflowType → WorkflowType
class WorkflowType(Enum):
    """Types of predefined workflows."""


@dataclass
# NAMING FIXED: WorkflowBlueprint → WorkflowBlueprint
class WorkflowBlueprint:
    """Blueprint for a workflow graph."""

    _name: str
    _description: str
    _roles: list[AgentRole]
    _edges: list[tuple[AgentRole, AgentRole]]
    _mutation_hooks: dict[AgentRole, list[tuple[MutationAction, AgentRole]]] = field(default_factory=dict)
    _parallel_groups: list[list[AgentRole]] = field(default_factory=list)
