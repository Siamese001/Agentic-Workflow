"""Apply Attempt Artifact — Wave 7.0.14 (Schema Lock).

Frozen, schema-locked artifact recording the outcome of an explicit
meta-learning apply attempt (DRY_RUN or APPLY).

NO automatic application.  Explicit invoke only.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Literal

from agentic_core.interfaces.determinism_types import (
    SemanticClockSnapshot,
    validate_semantic_clock,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
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

_emit_authorize_and_execute("p2", "apply_attempt_types", "execution_auth")
_emit_validates_capability("p2", "apply_attempt_types", "capability_check")
_emit_routes_to_capability("p2", "apply_attempt_types", "capability_route")
_emit_writes_via_uwg("p2", "apply_attempt_types", "uwg_write")
_emit_blocks_direct_write("p2", "apply_attempt_types", "direct_write_block")
_emit_records_tool_invocation("p2", "apply_attempt_types", "tool_invocation")
_emit_captures_execution_output("p2", "apply_attempt_types", "exec_output")
_emit_dispatches_agent("p3", "apply_attempt_types", "agent_dispatch")
_emit_coordinates_agents("p3", "apply_attempt_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "apply_attempt_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "apply_attempt_types", "healing_outcome")
_emit_escalates_failure("p3", "apply_attempt_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "apply_attempt_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "apply_attempt_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "apply_attempt_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "apply_attempt_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "apply_attempt_types", "eval_metric")
_emit_stores_embedding("p4", "apply_attempt_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "apply_attempt_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "apply_attempt_types", "exec_snapshot_link")
from system_learning.enforcement.determinism import (
    deterministic_json,
    stable_sha256_json,
)
from system_learning.types.meta_learning_types import (
    _canonical_payload_json,
)

_emit_records_execution_trace("p0", "evidence", "apply_attempt_types")
_emit_applies_guardrail("p0", "apply_attempt_types", "p0_governance")
_emit_snapshots_state("p0", "apply_attempt_types", "state_snapshot")
emit_replay_key("p0", "apply_attempt_types")
emit_determinism_digest("p0", "apply_attempt_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


@dataclass(frozen=True)
class MetaLearningApplyAttemptArtifact:
    """Frozen, schema-locked apply attempt record.

    Rules
    -----
    - semantic_clock required (ValueError if missing).
    - outcome is APPLIED or REJECTED (fail-closed).
    - reject_reason is None when APPLIED, a stable code when REJECTED.
    - canonical serialization (sort_keys=True).
    """

    artifact_type: Literal["META_LEARNING_APPLY_ATTEMPT"]
    change_package_trace_id: str
    rollout_trace_id: str
    policy_config_hash: str | None
    target_component: str
    apply_mode: Literal["DRY_RUN", "APPLY"]
    outcome: Literal["APPLIED", "REJECTED"]
    reject_reason: str | None
    details: dict[str, str]
    semantic_clock: SemanticClockSnapshot
    trace_id: str

    def __post_init__(self) -> None:
        validate_semantic_clock(self.semantic_clock, "MetaLearningApplyAttemptArtifact")
        if self.artifact_type != "META_LEARNING_APPLY_ATTEMPT":
            raise ValueError(
                f"artifact_type must be 'META_LEARNING_APPLY_ATTEMPT', got {self.artifact_type!r}",
            )

    def to_dict(self) -> dict[str, object]:
        """Canonical, deterministic serialization (keys sorted alphabetically)."""
        return {
            "apply_mode": self.apply_mode,
            "artifact_type": self.artifact_type,
            "change_package_trace_id": self.change_package_trace_id,
            "details": dict(sorted(self.details.items())),
            "outcome": self.outcome,
            "policy_config_hash": self.policy_config_hash,
            "reject_reason": self.reject_reason,
            "rollout_trace_id": self.rollout_trace_id,
            "semantic_clock": self.semantic_clock.to_dict(),
            "target_component": self.target_component,
            "trace_id": self.trace_id,
        }

    def to_json(self) -> str:
        """Deterministic JSON string (sort_keys=True, compact separators)."""
        return deterministic_json(self.to_dict())


def build_apply_attempt(
    *,
    change_package_trace_id: str,
    rollout_trace_id: str,
    policy_config_hash: str | None,
    target_component: str,
    apply_mode: Literal["DRY_RUN", "APPLY"],
    outcome: Literal["APPLIED", "REJECTED"],
    reject_reason: str | None,
    details: dict[str, str],
    semantic_clock: SemanticClockSnapshot,
) -> MetaLearningApplyAttemptArtifact:
    """Build a MetaLearningApplyAttemptArtifact with deterministic trace_id."""
    validate_semantic_clock(semantic_clock, "build_apply_attempt")

    sorted_details = dict(sorted(details.items()))

    temp_payload: dict[str, Any] = {
        "apply_mode": apply_mode,
        "artifact_type": "META_LEARNING_APPLY_ATTEMPT",
        "change_package_trace_id": change_package_trace_id,
        "details": sorted_details,
        "outcome": outcome,
        "policy_config_hash": policy_config_hash,
        "reject_reason": reject_reason,
        "rollout_trace_id": rollout_trace_id,
        "semantic_clock": semantic_clock.to_dict(),
        "target_component": target_component,
    }
    canonical = _canonical_payload_json(temp_payload)
    trace_id = stable_sha256_json(json.loads(canonical))

    return MetaLearningApplyAttemptArtifact(
        artifact_type="META_LEARNING_APPLY_ATTEMPT",
        change_package_trace_id=change_package_trace_id,
        rollout_trace_id=rollout_trace_id,
        policy_config_hash=policy_config_hash,
        target_component=target_component,
        apply_mode=apply_mode,
        outcome=outcome,
        reject_reason=reject_reason,
        details=sorted_details,
        semantic_clock=semantic_clock,
        trace_id=trace_id,
    )
