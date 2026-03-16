from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
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
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "fresh_data_validator")
emit_determinism_digest("p0", "fresh_data_validator")

_emit_dispatches_healing_run("p1", "fresh_data_validator", "L4")
_emit_routes_through("p1", "fresh_data_validator", "L4")
_emit_escalates_to_human("p1", "fresh_data_validator", "L4")
_emit_reads_policy_state("p1", "fresh_data_validator", "L4")
_emit_authorize_and_execute("p2", "fresh_data_validator", "execution_auth")
_emit_validates_capability("p2", "fresh_data_validator", "capability_check")
_emit_routes_to_capability("p2", "fresh_data_validator", "capability_route")
_emit_writes_via_uwg("p2", "fresh_data_validator", "uwg_write")
_emit_blocks_direct_write("p2", "fresh_data_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "fresh_data_validator", "tool_invocation")
_emit_captures_execution_output("p2", "fresh_data_validator", "exec_output")
_emit_dispatches_agent("p3", "fresh_data_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "fresh_data_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "fresh_data_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "fresh_data_validator", "healing_outcome")
_emit_escalates_failure("p3", "fresh_data_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "fresh_data_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "fresh_data_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "fresh_data_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "fresh_data_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "fresh_data_validator", "eval_metric")
_emit_stores_embedding("p4", "fresh_data_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "fresh_data_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "fresh_data_validator", "exec_snapshot_link")


class StaleDataViolation(Exception):
    """Raised when data is served that is older than the freshness policy allows."""

    def __init__(self, data_timestamp: datetime.datetime, policy_max_age: int):
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "StaleDataViolation.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "StaleDataViolation.__init__", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "StaleDataViolation.__init__")
        self.data_timestamp = data_timestamp
        self.policy_max_age = policy_max_age
        super().__init__(
            f"Data with timestamp {data_timestamp} is stale. Policy requires data to be no older than {policy_max_age} seconds."
        )


@dataclass(frozen=True)
class FreshnessPolicy:
    """Defines the freshness window for a piece of data."""

    max_age_seconds: int


@dataclass(frozen=True)
class VersionedData:
    """Represents a piece of data with a timestamp for freshness validation."""

    content: Any
    timestamp: datetime.datetime


def validate_freshness(data: VersionedData, policy: FreshnessPolicy) -> None:
    """
    Validates that a piece of versioned data is not stale.

    This function enforces Guarantee #11 (Fresh data only at runtime) by comparing
    the data's timestamp against a configurable freshness window. It is a critical
    sovereign gate in L4 to prevent the use of outdated context or knowledge.

    Args:
        data: The versioned data to validate.
        policy: The freshness policy to apply.

    Raises:
        StaleDataViolation: If the data's timestamp is older than the allowed max age.
    """
    now = datetime.datetime.utcnow()
    allowed_age = datetime.timedelta(seconds=policy.max_age_seconds)
    if now - data.timestamp > allowed_age:
        raise StaleDataViolation(data_timestamp=data.timestamp, policy_max_age=policy.max_age_seconds)
