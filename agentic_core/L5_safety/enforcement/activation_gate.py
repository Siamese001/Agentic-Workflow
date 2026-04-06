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

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "assert_activation_allowed")
    missing: list[str] = []
    for module_path, symbol_name, short_key in _REQUIRED_COMPONENTS:
        try:
            mod: Any = __import__(module_path, fromlist=[symbol_name])
            if not hasattr(mod, symbol_name):
                missing.append(short_key)
        # guardian: allow-silent-swallow - optional dependency
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
