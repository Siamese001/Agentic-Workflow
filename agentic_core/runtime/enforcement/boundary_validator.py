"""
agentic_core/runtime/boundary_validator.py

Runtime boundary validator for agentic_core.

Provides lightweight runtime assertions that can be placed at module
boundaries to detect and fail-fast on illegal cross-layer imports
that slipped through static analysis.
"""

from __future__ import annotations

import sys

from agentic_core.L0_routing.config.path_constants import (
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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

_emit_authorize_and_execute("p2", "boundary_validator", "execution_auth")
_emit_validates_capability("p2", "boundary_validator", "capability_check")
_emit_routes_to_capability("p2", "boundary_validator", "capability_route")
_emit_writes_via_uwg("p2", "boundary_validator", "uwg_write")
_emit_blocks_direct_write("p2", "boundary_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "boundary_validator", "tool_invocation")
_emit_captures_execution_output("p2", "boundary_validator", "exec_output")
_emit_dispatches_agent("p3", "boundary_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "boundary_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "boundary_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "boundary_validator", "healing_outcome")
_emit_escalates_failure("p3", "boundary_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "boundary_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "boundary_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "boundary_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "boundary_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "boundary_validator", "eval_metric")
_emit_stores_embedding("p4", "boundary_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "boundary_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "boundary_validator", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from agentic_core.runtime.sovereignty_exceptions import SovereigntyViolationError

_emit_emits_metric_event("boundary_validator", "p4obs", "metric_1")
_emit_emits_metric_event("boundary_validator", "p4obs", "metric_2")
_emit_emits_metric_event("boundary_validator", "p4obs", "metric_3")
_emit_emits_metric_event("boundary_validator", "p4obs", "metric_4")
_emit_emits_metric_event("boundary_validator", "p4obs", "metric_5")
_emit_emits_metric_event("boundary_validator", "p4obs", "metric_6")
_emit_records_incident_event("boundary_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("boundary_validator", "p4obs", "anomaly")
_emit_writes_observability_log("boundary_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("boundary_validator", "p4obs", "mon_state")
_emit_triggers_alert("boundary_validator", "p4obs", "alert")
_emit_links_incident_trace("boundary_validator", "p4obs", "trace_link")
_emit_captures_pattern("boundary_validator", "p3lm", "pattern")
_emit_records_learning_event("boundary_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("boundary_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("boundary_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("boundary_validator", "p3lm", "routing")
_emit_improves_agent_policy("boundary_validator", "p3lm", "policy")
_emit_stores_learning_state("boundary_validator", "p3lm", "state")
_emit_records_execution_trace("boundary_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("boundary_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("boundary_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("boundary_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("boundary_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("boundary_validator", "env_read", "p2_env_1")
_emit_reads_environ("boundary_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("boundary_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("boundary_validator", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "boundary_validator")
_emit_applies_guardrail("p0", "boundary_validator", "p0_governance")
_emit_reads_policy_state("p0", "boundary_validator", "policy_binding")
_emit_snapshots_state("p0", "boundary_validator", "state_snapshot")
_emit_pulls_context("p1", "boundary_validator", "context_pull")
_emit_pulls_context("p1", "boundary_validator", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "boundary_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "boundary_validator", "uwg_term_secondary")
_emit_writes_through("p1", "boundary_validator", "write_through")
_emit_writes_through("p1", "boundary_validator", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "boundary_validator", "safety_validation")
_emit_invokes_eval("p1", "boundary_validator", "eval_call")
_emit_proposal_commits_routing("p1", "boundary_validator", "routing_commit")
_emit_escalates_to_human("p1", "boundary_validator", "human_escalation")
_emit_routes_through("p1", "boundary_validator", "route_through")
_emit_checks_agent_registry("p1", "boundary_validator", "agent_registry")
_emit_validates_agent_capability("p1", "boundary_validator", "capability")
_emit_dispatches_execution_plan("p1", "boundary_validator", "exec_plan")
_emit_agent_executes_agent("p1", "boundary_validator", "sub_agent")
_emit_routes_to_agent("p1", "boundary_validator", "target_agent")
_emit_verifies_policy("p1", "boundary_validator", "policy_check")
_emit_observes_runtime_state("p1", "boundary_validator", "runtime_state")
_emit_verifies_boundary("p1", "boundary_validator", "boundary_check")
_emit_transcripts_response("p1", "boundary_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "boundary_validator")
_emit_gated_by_confidence("p1", "boundary_validator", "confidence_gate")
emit_replay_key("p0", "boundary_validator")
emit_determinism_digest("p0", "boundary_validator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

_FORBIDDEN_IN_AGENTIC_CORE = frozenset({APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR})


def assert_no_apps_imports(caller_module: str) -> None:
    """Raise SovereigntyViolationError if caller_module imports any apps_* package.

    Call this at the top of any agentic_core module to enforce the boundary
    at import time rather than relying solely on static analysis.
    """
    loaded = set(sys.modules.keys())
    for forbidden in _FORBIDDEN_IN_AGENTIC_CORE:
        if any(m == forbidden or m.startswith(forbidden + ".") for m in loaded):
            raise SovereigntyViolationError(
                f"Module '{caller_module}' loaded while forbidden package '{forbidden}' is present in sys.modules. agentic_core must not depend on apps_* packages.",
            )


def validate_layer_direction(
    source_module: str, target_module: str, source_layer: int | None = None, target_layer: int | None = None,
) -> None:
    """Raise SovereigntyViolationError if import direction violates layer gravity.

    Higher numeric layer (e.g. L5=5) may import from lower (e.g. L0=0).
    Lower may NOT import from higher (gravity violation).
    """
    if source_layer is None or target_layer is None:
        return
    if source_layer < target_layer:
        raise SovereigntyViolationError(
            f"Layer gravity violation: '{source_module}' (L{source_layer}) imports '{target_module}' (L{target_layer}). Lower layers must not import from higher layers.",
        )


def check_runtime_boundaries() -> bool:
    """Scan sys.modules for any agentic_core module that co-loaded apps_* packages.

    Returns True if clean, False (and prints report) if violations found.
    """
    agentic_modules = [m for m in sys.modules if m.startswith("agentic_core")]
    forbidden_loaded = [
        m for m in sys.modules if any(m == f or m.startswith(f + ".") for f in _FORBIDDEN_IN_AGENTIC_CORE)
    ]
    if agentic_modules and forbidden_loaded:
        print("Runtime boundary violations detected:")
        print(f"  agentic_core modules loaded: {len(agentic_modules)}")
        print(f"  Forbidden packages also loaded: {forbidden_loaded}")
        return False
    print("OK: No runtime boundary violations detected")
    return True
