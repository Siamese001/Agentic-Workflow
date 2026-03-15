from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_snapshots_state("p0", "workflow_types", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "workflow_types", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "workflow_types")

"Types and models for SubatomicOrchestratorAgent."
import logging
from dataclasses import dataclass, field
from enum import Enum

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
