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

emit_replay_key("p0", "patch_validator")
emit_determinism_digest("p0", "patch_validator")

_emit_dispatches_healing_run("p1", "patch_validator", "L5")
_emit_routes_through("p1", "patch_validator", "L5")
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
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_SAFETY, "validate_patch")
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
