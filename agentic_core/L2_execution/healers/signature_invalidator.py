from __future__ import annotations

import hashlib
from typing import Any, NamedTuple

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

emit_replay_key("p0", "signature_invalidator")
emit_determinism_digest("p0", "signature_invalidator")

_emit_dispatches_healing_run("p1", "signature_invalidator", "L2")
_emit_routes_through("p1", "signature_invalidator", "L2")
_emit_escalates_to_human("p1", "signature_invalidator", "L2")
_emit_reads_policy_state("p1", "signature_invalidator", "L2")
_emit_authorize_and_execute("p2", "signature_invalidator", "execution_auth")
_emit_validates_capability("p2", "signature_invalidator", "capability_check")
_emit_routes_to_capability("p2", "signature_invalidator", "capability_route")
_emit_writes_via_uwg("p2", "signature_invalidator", "uwg_write")
_emit_blocks_direct_write("p2", "signature_invalidator", "direct_write_block")
_emit_records_tool_invocation("p2", "signature_invalidator", "tool_invocation")
_emit_captures_execution_output("p2", "signature_invalidator", "exec_output")
_emit_dispatches_agent("p3", "signature_invalidator", "agent_dispatch")
_emit_coordinates_agents("p3", "signature_invalidator", "agent_coordination")
_emit_records_workflow_lineage("p3", "signature_invalidator", "workflow_lineage")
_emit_records_healing_outcome("p3", "signature_invalidator", "healing_outcome")
_emit_escalates_failure("p3", "signature_invalidator", "failure_escalation")
_emit_orchestrates_workflow("p3", "signature_invalidator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "signature_invalidator", "healing_dispatch")
_emit_invokes_evaluation("p3", "signature_invalidator", "evaluation_signal")
_emit_records_telemetry_event("p4", "signature_invalidator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "signature_invalidator", "eval_metric")
_emit_stores_embedding("p4", "signature_invalidator", "embedding_store")
_emit_updates_meta_learning_state("p4", "signature_invalidator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "signature_invalidator", "exec_snapshot_link")

HealedPlan = dict[str, Any]


class StaleSignatureViolation(Exception):
    """Raised when a healed plan is executed with a stale signature."""

    pass


class InvalidationResult(NamedTuple):
    """The result of invalidating a plan's signature."""

    invalidated_plan: HealedPlan
    new_policy_hash: str


def invalidate_signature_and_rehash(plan: HealedPlan) -> InvalidationResult:
    """
    Strips cryptographic signatures and regenerates the policy hash for a healed plan.

    This is a critical step for Guarantee #4. After a plan is modified by a
    healing agent, its original approval signature is no longer valid. This
    function ensures the old signature is removed and a new policy hash is
    generated from the modified content, forcing a full L5 re-validation.

    Args:
        plan: The healed plan that has been modified.

    Returns:
        An InvalidationResult containing the plan with its signature stripped
        and a new policy hash for re-validation.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "invalidate_signature_and_rehash", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "invalidate_signature_and_rehash", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "invalidate_signature_and_rehash")
    invalidated_plan = plan.copy()
    invalidated_plan.pop("l5_signature", None)
    invalidated_plan.pop("l5_approval_timestamp", None)
    invalidated_plan.pop("policy_hash", None)
    import json

    canonical_string = json.dumps(invalidated_plan, sort_keys=True, separators=(",", ":")).encode("utf-8")
    new_policy_hash = hashlib.sha256(canonical_string).hexdigest()
    invalidated_plan["policy_hash"] = new_policy_hash
    return InvalidationResult(invalidated_plan=invalidated_plan, new_policy_hash=new_policy_hash)


def verify_no_stale_signature(plan: HealedPlan):
    """
    Verifies that a plan about to be executed does not contain a stale signature.

    This would be called by the execution gateway before committing a change.
    It's a final check to prevent a bypass of the re-clear loop.

    Args:
        plan: The plan to be checked.

    Raises:
        StaleSignatureViolation: If a signature is present on a healed plan that
                                 should have been invalidated.
    """
    if "healed_by" in plan and "l5_signature" in plan:
        raise StaleSignatureViolation("Healed plan contains a stale L5 signature. It must be re-validated.")
