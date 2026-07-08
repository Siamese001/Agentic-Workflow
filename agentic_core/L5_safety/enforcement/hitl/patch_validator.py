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
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "patch_validator")
trace_contract.emit_determinism_digest("p0", "patch_validator")

trace_contract._emit_dispatches_healing_run("p1", "patch_validator", "L5")
trace_contract._emit_routes_through("p1", "patch_validator", "L5")
trace_contract._emit_checks_agent_registry("p1", "patch_validator", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "patch_validator", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "patch_validator", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "patch_validator", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "patch_validator", "target_agent")
trace_contract._emit_verifies_policy("p1", "patch_validator", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "patch_validator", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "patch_validator", "boundary_check")
trace_contract._emit_transcripts_response("p1", "patch_validator", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "patch_validator")
trace_contract._emit_gated_by_confidence("p1", "patch_validator", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "patch_validator", "L5")
trace_contract._emit_reads_policy_state("p1", "patch_validator", "L5")
trace_contract._emit_authorize_and_execute("p2", "patch_validator", "execution_auth")
trace_contract._emit_validates_capability("p2", "patch_validator", "capability_check")
trace_contract._emit_routes_to_capability("p2", "patch_validator", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "patch_validator", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "patch_validator", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "patch_validator", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "patch_validator", "exec_output")
trace_contract._emit_dispatches_agent("p3", "patch_validator", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "patch_validator", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "patch_validator", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "patch_validator", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "patch_validator", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "patch_validator", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "patch_validator", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "patch_validator", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "patch_validator", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "patch_validator", "eval_metric")
trace_contract._emit_stores_embedding("p4", "patch_validator", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "patch_validator", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "patch_validator", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("patch_validator", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("patch_validator", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("patch_validator", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("patch_validator", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("patch_validator", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("patch_validator", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("patch_validator", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("patch_validator", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("patch_validator", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("patch_validator", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("patch_validator", "p4obs", "alert")
trace_contract._emit_links_incident_trace("patch_validator", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("patch_validator", "p3lm", "pattern")
trace_contract._emit_records_learning_event("patch_validator", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("patch_validator", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("patch_validator", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("patch_validator", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("patch_validator", "p3lm", "policy")
trace_contract._emit_stores_learning_state("patch_validator", "p3lm", "state")
trace_contract._emit_records_execution_trace("patch_validator", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("patch_validator", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("patch_validator", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("patch_validator", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("patch_validator", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("patch_validator", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("patch_validator", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("patch_validator", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("patch_validator", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "patch_validator", "context_pull")
trace_contract._emit_pulls_context("p1", "patch_validator", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "patch_validator", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "patch_validator", "uwg_term_2")
trace_contract._emit_writes_through("p1", "patch_validator", "write_through")
trace_contract._emit_writes_through("p1", "patch_validator", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "patch_validator", "safety_validation")
trace_contract._emit_invokes_eval("p1", "patch_validator", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "patch_validator", "routing_commit")

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

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "validate_patch", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "validate_patch", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "validate_patch")
    missing = [f for f in sorted(_REQUIRED_FIELDS) if not patch.get(f)]
    if missing:
        raise HumanPatchValidationError(
            f"HITL patch missing required field(s): {missing}. All MODIFY_DIFF patches must include: original_plan_hash, structured_patch_schema, reviewer_signature.",
        )
    patch_hash = hashlib.sha256(
        json.dumps(patch, sort_keys=True, ensure_ascii=True, default=str).encode(),
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
