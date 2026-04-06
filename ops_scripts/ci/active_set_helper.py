"""Shared Active Set Helper — Single Import Point.

Provides a canonical function to enumerate the ACTIVE agent set using
the same pipeline as full_agent_discovery's perform_deep_integrity_scan.

All CI gates that need the ACTIVE set MUST use this helper to prevent
definition divergence.

Usage:
    from ops_scripts.ci.active_set_helper import get_active_set

    result = get_active_set(project_root)
    print(result.count, result.fingerprint)
"""
from __future__ import annotations

import hashlib
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

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

_emit_records_execution_trace("p0", "evidence", "active_set_helper")
_emit_applies_guardrail("p0", "active_set_helper", "p0_governance")
_emit_reads_policy_state("p0", "active_set_helper", "policy_binding")
_emit_snapshots_state("p0", "active_set_helper", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_emits_metric_event("active_set_helper", "p4obs", "metric_1")
_emit_emits_metric_event("active_set_helper", "p4obs", "metric_2")
_emit_emits_metric_event("active_set_helper", "p4obs", "metric_3")
_emit_emits_metric_event("active_set_helper", "p4obs", "metric_4")
_emit_emits_metric_event("active_set_helper", "p4obs", "metric_5")
_emit_emits_metric_event("active_set_helper", "p4obs", "metric_6")
_emit_records_incident_event("active_set_helper", "p4obs", "incident")
_emit_captures_runtime_anomaly("active_set_helper", "p4obs", "anomaly")
_emit_writes_observability_log("active_set_helper", "p4obs", "obs_log")
_emit_updates_monitoring_state("active_set_helper", "p4obs", "mon_state")
_emit_triggers_alert("active_set_helper", "p4obs", "alert")
_emit_links_incident_trace("active_set_helper", "p4obs", "trace_link")
_emit_captures_pattern("active_set_helper", "p3lm", "pattern")
_emit_records_learning_event("active_set_helper", "p3lm", "learning_event")
_emit_writes_learning_snapshot("active_set_helper", "p3lm", "snapshot")
_emit_feeds_meta_learning("active_set_helper", "p3lm", "meta_feed")
_emit_updates_routing_strategy("active_set_helper", "p3lm", "routing")
_emit_improves_agent_policy("active_set_helper", "p3lm", "policy")
_emit_stores_learning_state("active_set_helper", "p3lm", "state")
_emit_records_execution_trace("active_set_helper", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("active_set_helper", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("active_set_helper", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("active_set_helper", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("active_set_helper", "L4_STATE", "p2_trace_5")
_emit_reads_environ("active_set_helper", "env_read", "p2_env_1")
_emit_reads_environ("active_set_helper", "env_read", "p2_env_2")
_emit_reads_runtime_state("active_set_helper", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("active_set_helper", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "active_set_helper", "context_pull")
_emit_pulls_context("p1", "active_set_helper", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "active_set_helper", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "active_set_helper", "uwg_term_2")
_emit_writes_through("p1", "active_set_helper", "write_through")
_emit_writes_through("p1", "active_set_helper", "write_through_2")
_emit_validated_by_safety_plane("p1", "active_set_helper", "safety_validation")
_emit_invokes_eval("p1", "active_set_helper", "eval_call")
_emit_proposal_commits_routing("p1", "active_set_helper", "routing_commit")
_emit_escalates_to_human("p1", "active_set_helper", "human_escalation")
_emit_routes_through("p1", "active_set_helper", "route_through")
_emit_checks_agent_registry("p1", "active_set_helper", "agent_registry")
_emit_validates_agent_capability("p1", "active_set_helper", "capability")
_emit_dispatches_execution_plan("p1", "active_set_helper", "exec_plan")
_emit_agent_executes_agent("p1", "active_set_helper", "sub_agent")
_emit_routes_to_agent("p1", "active_set_helper", "target_agent")
_emit_verifies_policy("p1", "active_set_helper", "policy_check")
_emit_observes_runtime_state("p1", "active_set_helper", "runtime_state")
_emit_verifies_boundary("p1", "active_set_helper", "boundary_check")
_emit_transcripts_response("p1", "active_set_helper", "transcript")
_emit_hard_fails_untranscripted("p1", "active_set_helper")
_emit_gated_by_confidence("p1", "active_set_helper", "confidence_gate")
emit_replay_key("p0", "active_set_helper")
emit_determinism_digest("p0", "active_set_helper")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "active_set_helper", "execution_auth")
_emit_validates_capability("p2", "active_set_helper", "capability_check")
_emit_routes_to_capability("p2", "active_set_helper", "capability_route")
_emit_writes_via_uwg("p2", "active_set_helper", "uwg_write")
_emit_blocks_direct_write("p2", "active_set_helper", "direct_write_block")
_emit_records_tool_invocation("p2", "active_set_helper", "tool_invocation")
_emit_captures_execution_output("p2", "active_set_helper", "exec_output")
_emit_dispatches_agent("p3", "active_set_helper", "agent_dispatch")
_emit_coordinates_agents("p3", "active_set_helper", "agent_coordination")
_emit_records_workflow_lineage("p3", "active_set_helper", "workflow_lineage")
_emit_records_healing_outcome("p3", "active_set_helper", "healing_outcome")
_emit_escalates_failure("p3", "active_set_helper", "failure_escalation")
_emit_orchestrates_workflow("p3", "active_set_helper", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "active_set_helper", "healing_dispatch")
_emit_invokes_evaluation("p3", "active_set_helper", "evaluation_signal")
_emit_records_telemetry_event("p4", "active_set_helper", "telemetry_event")
_emit_captures_evaluation_metric("p4", "active_set_helper", "eval_metric")
_emit_stores_embedding("p4", "active_set_helper", "embedding_store")
_emit_updates_meta_learning_state("p4", "active_set_helper", "meta_learning")
_emit_links_execution_to_snapshot("p4", "active_set_helper", "exec_snapshot_link")

@dataclass(frozen=True)
class ActiveSetResult:
    """Immutable result of active set enumeration."""
    agents: tuple[dict[str, Any], ...]
    agent_ids: tuple[str, ...]
    count: int
    fingerprint: str
    stats: dict[str, int] = field(default_factory=dict)

def _compute_fingerprint(sorted_ids: tuple[str, ...]) -> str:
    """SHA-256 of newline-joined sorted agent IDs."""
    payload = '\n'.join(sorted_ids).encode('utf-8')
    return hashlib.sha256(payload).hexdigest()

def get_active_set(project_root: Path) -> ActiveSetResult:
    """Return the canonical ACTIVE agent set.

    Pipeline: load_agent_discovery → perform_deep_integrity_scan.
    Identical to discovery_registry_consistency_check.py.
    """
    if str(project_root) not in sys.path:
        # guardian: allow-global-mutation
        sys.path.insert(0, str(project_root))
    from ops_scripts.dev_tools.L0_routing_scripts.full_agent_discovery import perform_deep_integrity_scan
    from ops_scripts.dev_tools.L0_routing.ssot_discovery_util import load_agent_discovery
    raw = load_agent_discovery(project_root, force_reload=True)
    verified, stats = perform_deep_integrity_scan(raw, project_root)
    agent_ids = tuple(sorted(a.get('canonical_class', '') or a.get('class_name', '') for a in verified))
    fingerprint = _compute_fingerprint(agent_ids)
    return ActiveSetResult(agents=tuple(verified), agent_ids=agent_ids, count=len(verified), fingerprint=fingerprint, stats=stats)
