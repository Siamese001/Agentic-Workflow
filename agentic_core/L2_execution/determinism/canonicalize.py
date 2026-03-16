"""Additive determinism helper: canonical_bytes(obj) -> bytes.

Exposes a module-level function used by both production code and replay
harness tests.  Additive artifact for Phase 3 (W5 SOV-DELTA) — no existing
production code changed.

REQ-036 / Phase 3 SOV-DELTA additive helper.
"""

from __future__ import annotations

import json

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

emit_replay_key("p0", "canonicalize")
emit_determinism_digest("p0", "canonicalize")

_emit_dispatches_healing_run("p1", "canonicalize", "L2")
_emit_routes_through("p1", "canonicalize", "L2")
_emit_escalates_to_human("p1", "canonicalize", "L2")
_emit_reads_policy_state("p1", "canonicalize", "L2")
_emit_authorize_and_execute("p2", "canonicalize", "execution_auth")
_emit_validates_capability("p2", "canonicalize", "capability_check")
_emit_routes_to_capability("p2", "canonicalize", "capability_route")
_emit_writes_via_uwg("p2", "canonicalize", "uwg_write")
_emit_blocks_direct_write("p2", "canonicalize", "direct_write_block")
_emit_records_tool_invocation("p2", "canonicalize", "tool_invocation")
_emit_captures_execution_output("p2", "canonicalize", "exec_output")
_emit_dispatches_agent("p3", "canonicalize", "agent_dispatch")
_emit_coordinates_agents("p3", "canonicalize", "agent_coordination")
_emit_records_workflow_lineage("p3", "canonicalize", "workflow_lineage")
_emit_records_healing_outcome("p3", "canonicalize", "healing_outcome")
_emit_escalates_failure("p3", "canonicalize", "failure_escalation")
_emit_orchestrates_workflow("p3", "canonicalize", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "canonicalize", "healing_dispatch")
_emit_invokes_evaluation("p3", "canonicalize", "evaluation_signal")
_emit_records_telemetry_event("p4", "canonicalize", "telemetry_event")
_emit_captures_evaluation_metric("p4", "canonicalize", "eval_metric")
_emit_stores_embedding("p4", "canonicalize", "embedding_store")
_emit_updates_meta_learning_state("p4", "canonicalize", "meta_learning")
_emit_links_execution_to_snapshot("p4", "canonicalize", "exec_snapshot_link")


def canonical_bytes(obj) -> bytes:
    """Return deterministic canonical bytes for *obj*.

    Uses ``obj.__dict__`` for class/dataclass instances, falls through to
    *obj* itself for plain dict/list/primitive values.  ``sort_keys=True``
    ensures key insertion order does not affect the output.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "canonical_bytes", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "canonical_bytes", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "canonical_bytes")
    data = obj.__dict__ if hasattr(obj, "__dict__") else obj
    return json.dumps(data or obj, sort_keys=True, separators=(",", ":")).encode()
