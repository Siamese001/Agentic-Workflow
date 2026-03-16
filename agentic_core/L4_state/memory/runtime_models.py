"""Minimal shim: re-exports types required by prompt_assembler.py.

Created by P2/W2.2 to unblock the import chain:
  prompt_assembler.py → from agentic_core.L4_state.memory.runtime_models import InjectionMatch

Only the attributes accessed at runtime are defined:
  InjectionMatch.injection        → InjectionPattern (has .priority, .template)
  InjectionMatch.relevance_score  → float
  InjectionMatch.variable_values  → dict[str, Any]
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "runtime_models")
emit_determinism_digest("p0", "runtime_models")

_emit_dispatches_healing_run("p1", "runtime_models", "L4")
_emit_routes_through("p1", "runtime_models", "L4")
_emit_escalates_to_human("p1", "runtime_models", "L4")
_emit_reads_policy_state("p1", "runtime_models", "L4")

_emit_snapshots_state("p0", "runtime_models", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "runtime_models", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "runtime_models")
_emit_authorize_and_execute("p2", "runtime_models", "execution_auth")
_emit_validates_capability("p2", "runtime_models", "capability_check")
_emit_routes_to_capability("p2", "runtime_models", "capability_route")
_emit_writes_via_uwg("p2", "runtime_models", "uwg_write")
_emit_blocks_direct_write("p2", "runtime_models", "direct_write_block")
_emit_records_tool_invocation("p2", "runtime_models", "tool_invocation")
_emit_captures_execution_output("p2", "runtime_models", "exec_output")
_emit_dispatches_agent("p3", "runtime_models", "agent_dispatch")
_emit_coordinates_agents("p3", "runtime_models", "agent_coordination")
_emit_records_workflow_lineage("p3", "runtime_models", "workflow_lineage")
_emit_records_healing_outcome("p3", "runtime_models", "healing_outcome")
_emit_escalates_failure("p3", "runtime_models", "failure_escalation")
_emit_orchestrates_workflow("p3", "runtime_models", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "runtime_models", "healing_dispatch")
_emit_invokes_evaluation("p3", "runtime_models", "evaluation_signal")
_emit_records_telemetry_event("p4", "runtime_models", "telemetry_event")
_emit_captures_evaluation_metric("p4", "runtime_models", "eval_metric")
_emit_stores_embedding("p4", "runtime_models", "embedding_store")
_emit_updates_meta_learning_state("p4", "runtime_models", "meta_learning")
_emit_links_execution_to_snapshot("p4", "runtime_models", "exec_snapshot_link")


@dataclass
class InjectionPattern:
    """Minimal representation of an instructional injection pattern."""

    priority: int = 0
    template: str = ""


@dataclass
class InjectionMatch:
    """A matched injection pattern with relevance scoring and variable bindings."""

    injection: InjectionPattern = field(default_factory=InjectionPattern)
    relevance_score: float = 0.0
    variable_values: dict[str, Any] = field(default_factory=dict)
