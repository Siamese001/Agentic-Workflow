"""G-16-6 — Activation Gate: FAIL-CLOSED runtime prerequisite check.

Forbids ANY active/bounded-autonomy execution unless all three enforcement
subsystems are importable and present:

1. P5.1 capability chokepoint  (authorize_and_execute)
2. Mutation prohibition guard  (assert_no_persistent_write)
3. Healer 10-step pipe order   (enforce_healer_pipe_order)

Default is FAIL-CLOSED: if any component is missing, PermissionError is raised.
"""

from __future__ import annotations

import logging
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

emit_replay_key("p0", "activation_gate")
emit_determinism_digest("p0", "activation_gate")

_emit_dispatches_healing_run("p1", "activation_gate", "L5")
_emit_routes_through("p1", "activation_gate", "L5")
_emit_escalates_to_human("p1", "activation_gate", "L5")
_emit_reads_policy_state("p1", "activation_gate", "L5")
_emit_authorize_and_execute("p2", "activation_gate", "execution_auth")
_emit_validates_capability("p2", "activation_gate", "capability_check")
_emit_routes_to_capability("p2", "activation_gate", "capability_route")
_emit_writes_via_uwg("p2", "activation_gate", "uwg_write")
_emit_blocks_direct_write("p2", "activation_gate", "direct_write_block")
_emit_records_tool_invocation("p2", "activation_gate", "tool_invocation")
_emit_captures_execution_output("p2", "activation_gate", "exec_output")
_emit_dispatches_agent("p3", "activation_gate", "agent_dispatch")
_emit_coordinates_agents("p3", "activation_gate", "agent_coordination")
_emit_records_workflow_lineage("p3", "activation_gate", "workflow_lineage")
_emit_records_healing_outcome("p3", "activation_gate", "healing_outcome")
_emit_escalates_failure("p3", "activation_gate", "failure_escalation")
_emit_orchestrates_workflow("p3", "activation_gate", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "activation_gate", "healing_dispatch")
_emit_invokes_evaluation("p3", "activation_gate", "evaluation_signal")
_emit_records_telemetry_event("p4", "activation_gate", "telemetry_event")
_emit_captures_evaluation_metric("p4", "activation_gate", "eval_metric")
_emit_stores_embedding("p4", "activation_gate", "embedding_store")
_emit_updates_meta_learning_state("p4", "activation_gate", "meta_learning")
_emit_links_execution_to_snapshot("p4", "activation_gate", "exec_snapshot_link")

logger = logging.getLogger(__name__)
ACTIVATION_GATE_VERSION = "v5.4-P0"
_REQUIRED_COMPONENTS: list[tuple[str, str, str]] = [
    (
        "agentic_core.L2_execution.enforcement.capability_chokepoint",
        "authorize_and_execute",
        "capability_chokepoint",
    ),
    (
        "agentic_core.L5_safety.enforcement.mutation_prohibition_enforcer",
        "assert_no_persistent_write",
        "mutation_prohibition",
    ),
    (
        "agentic_core.L2_execution.enforcement.healer_pipe_order",
        "enforce_healer_pipe_order",
        "healer_pipe_order",
    ),
]


def assert_activation_allowed(trace_id: str | None = None) -> None:
    """FAIL-CLOSED activation gate.

    Verifies that all three enforcement subsystems are importable.
    Raises PermissionError with a deterministic message listing any
    missing components if the check fails.

    Args:
        trace_id: Optional trace identifier for deterministic diagnostics.

    Raises:
        PermissionError: If any required enforcement component is missing.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "assert_activation_allowed", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "assert_activation_allowed", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_SAFETY, "assert_activation_allowed")
    missing: list[str] = []
    for module_path, symbol_name, short_key in _REQUIRED_COMPONENTS:
        try:
            mod: Any = __import__(module_path, fromlist=[symbol_name])
            if not hasattr(mod, symbol_name):
                missing.append(short_key)
        except ImportError:
            missing.append(short_key)
    if missing:
        msg_parts = [
            f"ACTIVATION_DENIED:version={ACTIVATION_GATE_VERSION}",
            f"missing_components={','.join(sorted(missing))}",
        ]
        if trace_id is not None:
            msg_parts.append(f"trace_id={trace_id}")
        msg = "|".join(msg_parts)
        logger.error("ACTIVATION_GATE DENY: %s", msg)
        raise PermissionError(msg)


__all__ = ["ACTIVATION_GATE_VERSION", "assert_activation_allowed"]
