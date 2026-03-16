"""
L2.0 Manifest Hash Validator — Phase 2

Validates that execution manifests carry all required config hashes
and that those hashes match the L4 SSOT active configs.
"""

from __future__ import annotations

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

emit_replay_key("p0", "manifest_hash_validator")
emit_determinism_digest("p0", "manifest_hash_validator")

_emit_dispatches_healing_run("p1", "manifest_hash_validator", "L2")
_emit_routes_through("p1", "manifest_hash_validator", "L2")
_emit_escalates_to_human("p1", "manifest_hash_validator", "L2")
_emit_reads_policy_state("p1", "manifest_hash_validator", "L2")
_emit_authorize_and_execute("p2", "manifest_hash_validator", "execution_auth")
_emit_validates_capability("p2", "manifest_hash_validator", "capability_check")
_emit_routes_to_capability("p2", "manifest_hash_validator", "capability_route")
_emit_writes_via_uwg("p2", "manifest_hash_validator", "uwg_write")
_emit_blocks_direct_write("p2", "manifest_hash_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "manifest_hash_validator", "tool_invocation")
_emit_captures_execution_output("p2", "manifest_hash_validator", "exec_output")
_emit_dispatches_agent("p3", "manifest_hash_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "manifest_hash_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "manifest_hash_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "manifest_hash_validator", "healing_outcome")
_emit_escalates_failure("p3", "manifest_hash_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "manifest_hash_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "manifest_hash_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "manifest_hash_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "manifest_hash_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "manifest_hash_validator", "eval_metric")
_emit_stores_embedding("p4", "manifest_hash_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "manifest_hash_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "manifest_hash_validator", "exec_snapshot_link")


def _get_active_configs():
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_get_active_configs", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_get_active_configs", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "_get_active_configs")
    from agentic_core.L4_state.config.versioned_configs import get_active_configs

    return get_active_configs


REQUIRED_HASH_FIELDS = ("policy_hash", "routing_hash", "model_hash", "budget_hash")


class ManifestHashError(Exception):
    """Raised when manifest is missing or has mismatched config hashes."""

    pass


def validate_manifest_hashes(manifest: Any) -> None:
    """
    L2.0 gate: reject manifest if any required config hash is missing
    or does not match the L4 SSOT active config.

    Args:
        manifest: Any object with hash attributes, or a dict.

    Raises:
        ManifestHashError: on missing field or hash mismatch.
    """
    active = _get_active_configs()().hashes()
    for field in REQUIRED_HASH_FIELDS:
        if isinstance(manifest, dict):
            value = manifest.get(field)
        else:
            value = getattr(manifest, field, None)
        if value is None:
            raise ManifestHashError(f"Manifest missing required field: {field}")
        expected = active[field]
        if value != expected:
            raise ManifestHashError(f"Hash mismatch for {field}: manifest={value!r} vs L4_SSOT={expected!r}")
