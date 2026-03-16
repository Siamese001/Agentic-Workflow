from __future__ import annotations

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

emit_replay_key("p0", "micro_stage_types")
emit_determinism_digest("p0", "micro_stage_types")

_emit_dispatches_healing_run("p1", "micro_stage_types", "L4")
_emit_routes_through("p1", "micro_stage_types", "L4")
_emit_escalates_to_human("p1", "micro_stage_types", "L4")
_emit_reads_policy_state("p1", "micro_stage_types", "L4")

_emit_snapshots_state("p0", "micro_stage_types", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "micro_stage_types", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "micro_stage_types")
_emit_authorize_and_execute("p2", "micro_stage_types", "execution_auth")
_emit_validates_capability("p2", "micro_stage_types", "capability_check")
_emit_routes_to_capability("p2", "micro_stage_types", "capability_route")
_emit_writes_via_uwg("p2", "micro_stage_types", "uwg_write")
_emit_blocks_direct_write("p2", "micro_stage_types", "direct_write_block")
_emit_records_tool_invocation("p2", "micro_stage_types", "tool_invocation")
_emit_captures_execution_output("p2", "micro_stage_types", "exec_output")
_emit_dispatches_agent("p3", "micro_stage_types", "agent_dispatch")
_emit_coordinates_agents("p3", "micro_stage_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "micro_stage_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "micro_stage_types", "healing_outcome")
_emit_escalates_failure("p3", "micro_stage_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "micro_stage_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "micro_stage_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "micro_stage_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "micro_stage_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "micro_stage_types", "eval_metric")
_emit_stores_embedding("p4", "micro_stage_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "micro_stage_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "micro_stage_types", "exec_snapshot_link")

"\nMicro-Runtime & Execution Schemas\n=================================\nDefines the atomic stages (Subatomic Hops) and state transitions\nfor the Sovereign runtime.\n"
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class MicroStage(str, Enum):
    """The 5 atomic micro-stages of a Subatomic Hop."""

    INIT = "init"
    THINK = "think"
    ACT = "act"
    CRITIQUE = "critique"
    COMMIT = "commit"


class HopState(str, Enum):
    """Overall state of a Subatomic Hop."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RetryPolicy(BaseModel):
    """Retry policy for micro-stages."""

    max_retries: int = Field(default=3, ge=0, le=10)
    retry_delay: float = Field(default=1.0, ge=0.0)
    exponential_backoff: bool = Field(default=True)
    retryable_stages: list[MicroStage] = Field(
        default=[MicroStage.THINK, MicroStage.ACT, MicroStage.CRITIQUE]
    )


class MicroCheckpoint(BaseModel):
    """Checkpoint data for a micro-stage to support recovery."""

    hop_id: str
    stage: MicroStage
    timestamp: float
    state: HopState
    data: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class StageTransition(BaseModel):
    """Record of a stage transition within a hop."""

    from_stage: MicroStage | None = None
    to_stage: MicroStage
    timestamp: float
    reason: str | None = None
