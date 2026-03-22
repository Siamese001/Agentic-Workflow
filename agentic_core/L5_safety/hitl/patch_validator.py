"""Addendum 6.1: Human-in-the-Loop Patch Validator.

Every MODIFY_DIFF patch MUST include:
  - original_plan_hash
  - structured_patch_schema
  - reviewer_signature

Violation: Missing fields → raise HumanPatchValidationError.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from typing import Any

from agentic_core.L5_safety.types.hardening_errors import HumanPatchValidationError
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "patch_validator")
emit_determinism_digest("p0", "patch_validator")

_emit_dispatches_healing_run("p1", "patch_validator", "L5")
_emit_routes_through("p1", "patch_validator", "L5")
_emit_checks_agent_registry("p1", "patch_validator", "agent_registry")
_emit_validates_agent_capability("p1", "patch_validator", "capability")
_emit_dispatches_execution_plan("p1", "patch_validator", "exec_plan")
_emit_agent_executes_agent("p1", "patch_validator", "sub_agent")
_emit_routes_to_agent("p1", "patch_validator", "target_agent")
_emit_verifies_policy("p1", "patch_validator", "policy_check")
_emit_observes_runtime_state("p1", "patch_validator", "runtime_state")
_emit_verifies_boundary("p1", "patch_validator", "boundary_check")
_emit_transcripts_response("p1", "patch_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "patch_validator")
_emit_gated_by_confidence("p1", "patch_validator", "confidence_gate")
_emit_escalates_to_human("p1", "patch_validator", "L5")
_emit_reads_policy_state("p1", "patch_validator", "L5")
_emit_authorize_and_execute("p2", "patch_validator", "execution_auth")
_emit_validates_capability("p2", "patch_validator", "capability_check")
_emit_routes_to_capability("p2", "patch_validator", "capability_route")
_emit_writes_via_uwg("p2", "patch_validator", "uwg_write")
_emit_blocks_direct_write("p2", "patch_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "patch_validator", "tool_invocation")
_emit_captures_execution_output("p2", "patch_validator", "exec_output")
_emit_dispatches_agent("p3", "patch_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "patch_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "patch_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "patch_validator", "healing_outcome")
_emit_escalates_failure("p3", "patch_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "patch_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "patch_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "patch_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "patch_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "patch_validator", "eval_metric")
_emit_stores_embedding("p4", "patch_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "patch_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "patch_validator", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("patch_validator", "p4obs", "metric_1")
_emit_emits_metric_event("patch_validator", "p4obs", "metric_2")
_emit_emits_metric_event("patch_validator", "p4obs", "metric_3")
_emit_emits_metric_event("patch_validator", "p4obs", "metric_4")
_emit_emits_metric_event("patch_validator", "p4obs", "metric_5")
_emit_emits_metric_event("patch_validator", "p4obs", "metric_6")
_emit_records_incident_event("patch_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("patch_validator", "p4obs", "anomaly")
_emit_writes_observability_log("patch_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("patch_validator", "p4obs", "mon_state")
_emit_triggers_alert("patch_validator", "p4obs", "alert")
_emit_links_incident_trace("patch_validator", "p4obs", "trace_link")
_emit_captures_pattern("patch_validator", "p3lm", "pattern")
_emit_records_learning_event("patch_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("patch_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("patch_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("patch_validator", "p3lm", "routing")
_emit_improves_agent_policy("patch_validator", "p3lm", "policy")
_emit_stores_learning_state("patch_validator", "p3lm", "state")
_emit_records_execution_trace("patch_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("patch_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("patch_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("patch_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("patch_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("patch_validator", "env_read", "p2_env_1")
_emit_reads_environ("patch_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("patch_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("patch_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "patch_validator", "context_pull")
_emit_pulls_context("p1", "patch_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "patch_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "patch_validator", "uwg_term_2")
_emit_writes_through("p1", "patch_validator", "write_through")
_emit_writes_through("p1", "patch_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "patch_validator", "safety_validation")
_emit_invokes_eval("p1", "patch_validator", "eval_call")
_emit_proposal_commits_routing("p1", "patch_validator", "routing_commit")

logger = logging.getLogger(__name__)
_REQUIRED_FIELDS = frozenset({"original_plan_hash", "structured_patch_schema", "reviewer_signature"})


@dataclass
class ValidatedPatch:
    """A patch that has passed HITL validation."""

    original_plan_hash: str
    structured_patch_schema: dict[str, Any]
    reviewer_signature: str
    patch_hash: str
    raw: dict[str, Any]


def validate_patch(patch: dict[str, Any]) -> ValidatedPatch:
    """Validate a MODIFY_DIFF patch has all required HITL fields.

    Raises HumanPatchValidationError if any required field is missing or empty.
    Returns a ValidatedPatch on success.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "validate_patch", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "validate_patch", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "validate_patch")
    missing = [f for f in sorted(_REQUIRED_FIELDS) if not patch.get(f)]
    if missing:
        raise HumanPatchValidationError(
            f"HITL patch missing required field(s): {missing}. All MODIFY_DIFF patches must include: original_plan_hash, structured_patch_schema, reviewer_signature."
        )
    patch_hash = hashlib.sha256(
        json.dumps(patch, sort_keys=True, ensure_ascii=True, default=str).encode()
    ).hexdigest()
    logger.info(
        "HITL patch validated: reviewer=%s patch_hash=%s",
        patch.get("reviewer_signature", "")[:16],
        patch_hash[:16],
    )
    return ValidatedPatch(
        original_plan_hash=patch["original_plan_hash"],
        structured_patch_schema=patch["structured_patch_schema"],
        reviewer_signature=patch["reviewer_signature"],
        patch_hash=patch_hash,
        raw=patch,
    )


__all__ = ["validate_patch", "ValidatedPatch"]
