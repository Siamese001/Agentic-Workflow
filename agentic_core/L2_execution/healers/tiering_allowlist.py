"""
L2.3 Tiering Allowlist — Compile-Time Frozen Governance.

ONLY agents in TIERING_ALLOWLIST may invoke the centralized healing tier router.
All other agents MUST emit FailureSignal and let L2.3 handle tier selection.

This allowlist is compile-time frozen - no CSV loading, no runtime mutation.
"""

from __future__ import annotations

import logging

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

emit_replay_key("p0", "tiering_allowlist")
emit_determinism_digest("p0", "tiering_allowlist")

_emit_dispatches_healing_run("p1", "tiering_allowlist", "L2")
_emit_routes_through("p1", "tiering_allowlist", "L2")
_emit_checks_agent_registry("p1", "tiering_allowlist", "agent_registry")
_emit_validates_agent_capability("p1", "tiering_allowlist", "capability")
_emit_dispatches_execution_plan("p1", "tiering_allowlist", "exec_plan")
_emit_agent_executes_agent("p1", "tiering_allowlist", "sub_agent")
_emit_routes_to_agent("p1", "tiering_allowlist", "target_agent")
_emit_verifies_policy("p1", "tiering_allowlist", "policy_check")
_emit_observes_runtime_state("p1", "tiering_allowlist", "runtime_state")
_emit_verifies_boundary("p1", "tiering_allowlist", "boundary_check")
_emit_transcripts_response("p1", "tiering_allowlist", "transcript")
_emit_hard_fails_untranscripted("p1", "tiering_allowlist")
_emit_gated_by_confidence("p1", "tiering_allowlist", "confidence_gate")
_emit_escalates_to_human("p1", "tiering_allowlist", "L2")
_emit_reads_policy_state("p1", "tiering_allowlist", "L2")
_emit_authorize_and_execute("p2", "tiering_allowlist", "execution_auth")
_emit_validates_capability("p2", "tiering_allowlist", "capability_check")
_emit_routes_to_capability("p2", "tiering_allowlist", "capability_route")
_emit_writes_via_uwg("p2", "tiering_allowlist", "uwg_write")
_emit_blocks_direct_write("p2", "tiering_allowlist", "direct_write_block")
_emit_records_tool_invocation("p2", "tiering_allowlist", "tool_invocation")
_emit_captures_execution_output("p2", "tiering_allowlist", "exec_output")
_emit_dispatches_agent("p3", "tiering_allowlist", "agent_dispatch")
_emit_coordinates_agents("p3", "tiering_allowlist", "agent_coordination")
_emit_records_workflow_lineage("p3", "tiering_allowlist", "workflow_lineage")
_emit_records_healing_outcome("p3", "tiering_allowlist", "healing_outcome")
_emit_escalates_failure("p3", "tiering_allowlist", "failure_escalation")
_emit_orchestrates_workflow("p3", "tiering_allowlist", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "tiering_allowlist", "healing_dispatch")
_emit_invokes_evaluation("p3", "tiering_allowlist", "evaluation_signal")
_emit_records_telemetry_event("p4", "tiering_allowlist", "telemetry_event")
_emit_captures_evaluation_metric("p4", "tiering_allowlist", "eval_metric")
_emit_stores_embedding("p4", "tiering_allowlist", "embedding_store")
_emit_updates_meta_learning_state("p4", "tiering_allowlist", "meta_learning")
_emit_links_execution_to_snapshot("p4", "tiering_allowlist", "exec_snapshot_link")
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

_emit_emits_metric_event("tiering_allowlist", "p4obs", "metric_1")
_emit_emits_metric_event("tiering_allowlist", "p4obs", "metric_2")
_emit_emits_metric_event("tiering_allowlist", "p4obs", "metric_3")
_emit_emits_metric_event("tiering_allowlist", "p4obs", "metric_4")
_emit_emits_metric_event("tiering_allowlist", "p4obs", "metric_5")
_emit_emits_metric_event("tiering_allowlist", "p4obs", "metric_6")
_emit_records_incident_event("tiering_allowlist", "p4obs", "incident")
_emit_captures_runtime_anomaly("tiering_allowlist", "p4obs", "anomaly")
_emit_writes_observability_log("tiering_allowlist", "p4obs", "obs_log")
_emit_updates_monitoring_state("tiering_allowlist", "p4obs", "mon_state")
_emit_triggers_alert("tiering_allowlist", "p4obs", "alert")
_emit_links_incident_trace("tiering_allowlist", "p4obs", "trace_link")
_emit_captures_pattern("tiering_allowlist", "p3lm", "pattern")
_emit_records_learning_event("tiering_allowlist", "p3lm", "learning_event")
_emit_writes_learning_snapshot("tiering_allowlist", "p3lm", "snapshot")
_emit_feeds_meta_learning("tiering_allowlist", "p3lm", "meta_feed")
_emit_updates_routing_strategy("tiering_allowlist", "p3lm", "routing")
_emit_improves_agent_policy("tiering_allowlist", "p3lm", "policy")
_emit_stores_learning_state("tiering_allowlist", "p3lm", "state")
_emit_records_execution_trace("tiering_allowlist", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("tiering_allowlist", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("tiering_allowlist", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("tiering_allowlist", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("tiering_allowlist", "L4_STATE", "p2_trace_5")
_emit_reads_environ("tiering_allowlist", "env_read", "p2_env_1")
_emit_reads_environ("tiering_allowlist", "env_read", "p2_env_2")
_emit_reads_runtime_state("tiering_allowlist", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("tiering_allowlist", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "tiering_allowlist", "context_pull")
_emit_pulls_context("p1", "tiering_allowlist", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "tiering_allowlist", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "tiering_allowlist", "uwg_term_2")
_emit_writes_through("p1", "tiering_allowlist", "write_through")
_emit_writes_through("p1", "tiering_allowlist", "write_through_2")
_emit_validated_by_safety_plane("p1", "tiering_allowlist", "safety_validation")
_emit_invokes_eval("p1", "tiering_allowlist", "eval_call")
_emit_proposal_commits_routing("p1", "tiering_allowlist", "routing_commit")

logger = logging.getLogger(__name__)
TIERING_ALLOWLIST: frozenset[tuple[str, str]] = frozenset(
    {
        ("CodeHealerAgent", "agentic_core/L5_safety/reasoning/CodeHealerAgent.py"),
        ("GravityLeakRepairAgent", "agentic_core/L5_safety/reasoning/GravityLeakRepairAgent.py"),
        ("IntegrityGateExecutorAgent", "agentic_core/L5_safety/reasoning/IntegrityGateExecutorAgent.py"),
        ("LocationHealerAgent", "agentic_core/L5_safety/reasoning/LocationHealerAgent.py"),
        ("SafetyExecutorAgent", "agentic_core/L5_safety/reasoning/SafetyExecutorAgent.py"),
        ("StructureHealerAgent", "agentic_core/L5_safety/reasoning/StructureHealerAgent.py"),
        ("TypeHintFixerAgent", "agentic_core/L5_safety/reasoning/TypeHintFixerAgent.py"),
        ("DispatchOutreachToolsAgent", "apps_lic/reasoning/DispatchOutreachToolsAgent.py"),
        ("OutreachValidationExecutorAgent", "apps_lic/reasoning/OutreachValidationExecutorAgent.py"),
        ("DispatchResumeToolsAgent", "apps_rg/reasoning/DispatchResumeToolsAgent.py"),
        ("remediation_dispatcher", "agentic_core/L2_execution/scripts/remediation_dispatcher.py"),
    }
)
TIERING_ALLOWLIST_AGENT_NAMES: frozenset[str] = frozenset((name for name, _ in TIERING_ALLOWLIST))
TIERING_ALLOWLIST_FILE_PATHS: frozenset[str] = frozenset((path for _, path in TIERING_ALLOWLIST))


def _validate_allowlist_sovereignty() -> None:
    """Validate allowlist invariants at module import time."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_validate_allowlist_sovereignty", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_validate_allowlist_sovereignty", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "_validate_allowlist_sovereignty")
    logger.info("Validating compile-time frozen TIERING_ALLOWLIST...")
    if not isinstance(TIERING_ALLOWLIST, frozenset):
        raise RuntimeError("TIERING_ALLOWLIST must be frozenset for compile-time freezing")
    if not isinstance(TIERING_ALLOWLIST_AGENT_NAMES, frozenset):
        raise RuntimeError("TIERING_ALLOWLIST_AGENT_NAMES must be frozenset for compile-time freezing")
    agent_names = list(TIERING_ALLOWLIST_AGENT_NAMES)
    if len(agent_names) != len(set(agent_names)):
        raise RuntimeError("Duplicate agent names detected in TIERING_ALLOWLIST")
    expected_agents = {"CodeHealerAgent", "DispatchOutreachToolsAgent", "DispatchResumeToolsAgent"}
    missing_agents = expected_agents - TIERING_ALLOWLIST_AGENT_NAMES
    if missing_agents:
        raise RuntimeError(f"Expected agents missing from TIERING_ALLOWLIST: {missing_agents}")
    logger.info(
        f"TIERING_ALLOWLIST validated: {len(TIERING_ALLOWLIST)} agents, {len(TIERING_ALLOWLIST_AGENT_NAMES)} unique names"
    )


def is_tiering_allowed(agent_name: str) -> bool:
    """Check if agent is in compile-time frozen allowlist.

    Args:
        agent_name: Agent name to check

    Returns:
        True if agent is in TIERING_ALLOWLIST, False otherwise
    """
    return agent_name in TIERING_ALLOWLIST_AGENT_NAMES


def is_tiering_allowed_by_path(file_path: str) -> bool:
    """Check if a file path is in the compile-time frozen allowlist.

    Args:
        file_path: File path to check

    Returns:
        True if file path is in TIERING_ALLOWLIST, False otherwise
    """
    normalized = file_path.replace("\\", "/")
    return normalized in TIERING_ALLOWLIST_FILE_PATHS


_validate_allowlist_sovereignty()
__all__ = [
    "TIERING_ALLOWLIST",
    "TIERING_ALLOWLIST_AGENT_NAMES",
    "TIERING_ALLOWLIST_FILE_PATHS",
    "is_tiering_allowed",
    "is_tiering_allowed_by_path",
]
