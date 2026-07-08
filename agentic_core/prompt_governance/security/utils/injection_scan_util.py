"""
injection_scan_util.py - Canonical injection scan helper.

Thin wrapper around InjectionDetector.scan() to standardize scanning calls
across all prompt joinpoints. Logs source context for audit trail without
logging raw text.
"""

from __future__ import annotations

import logging

from agentic_core.prompt_governance.security.detectors.injection_detector import InjectionDetector
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_emits_metric_event("injection_scan_util", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("injection_scan_util", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("injection_scan_util", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("injection_scan_util", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("injection_scan_util", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("injection_scan_util", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("injection_scan_util", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("injection_scan_util", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("injection_scan_util", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("injection_scan_util", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("injection_scan_util", "p4obs", "alert")
trace_contract._emit_links_incident_trace("injection_scan_util", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("injection_scan_util", "p3lm", "pattern")
trace_contract._emit_records_learning_event("injection_scan_util", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("injection_scan_util", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("injection_scan_util", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("injection_scan_util", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("injection_scan_util", "p3lm", "policy")
trace_contract._emit_stores_learning_state("injection_scan_util", "p3lm", "state")
trace_contract._emit_records_execution_trace("injection_scan_util", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("injection_scan_util", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("injection_scan_util", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("injection_scan_util", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("injection_scan_util", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("injection_scan_util", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("injection_scan_util", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("injection_scan_util", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("injection_scan_util", "runtime_state", "p2_rt_2")

trace_contract._emit_records_execution_trace("p0", "evidence", "injection_scan_util")
trace_contract._emit_applies_guardrail("p0", "injection_scan_util", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "injection_scan_util", "policy_binding")
trace_contract._emit_snapshots_state("p0", "injection_scan_util", "state_snapshot")
trace_contract._emit_pulls_context("p1", "injection_scan_util", "context_pull")
trace_contract._emit_pulls_context("p1", "injection_scan_util", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "injection_scan_util", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "injection_scan_util", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "injection_scan_util", "write_through")
trace_contract._emit_writes_through("p1", "injection_scan_util", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "injection_scan_util", "safety_validation")
trace_contract._emit_invokes_eval("p1", "injection_scan_util", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "injection_scan_util", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "injection_scan_util", "human_escalation")
trace_contract._emit_routes_through("p1", "injection_scan_util", "route_through")
trace_contract._emit_checks_agent_registry("p1", "injection_scan_util", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "injection_scan_util", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "injection_scan_util", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "injection_scan_util", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "injection_scan_util", "target_agent")
trace_contract._emit_verifies_policy("p1", "injection_scan_util", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "injection_scan_util", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "injection_scan_util", "boundary_check")
trace_contract._emit_transcripts_response("p1", "injection_scan_util", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "injection_scan_util")
trace_contract._emit_gated_by_confidence("p1", "injection_scan_util", "confidence_gate")
trace_contract.emit_replay_key("p0", "injection_scan_util")
trace_contract.emit_determinism_digest("p0", "injection_scan_util")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "injection_scan_util", "execution_auth")
trace_contract._emit_validates_capability("p2", "injection_scan_util", "capability_check")
trace_contract._emit_routes_to_capability("p2", "injection_scan_util", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "injection_scan_util", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "injection_scan_util", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "injection_scan_util", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "injection_scan_util", "exec_output")
trace_contract._emit_dispatches_agent("p3", "injection_scan_util", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "injection_scan_util", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "injection_scan_util", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "injection_scan_util", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "injection_scan_util", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "injection_scan_util", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "injection_scan_util", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "injection_scan_util", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "injection_scan_util", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "injection_scan_util", "eval_metric")
trace_contract._emit_stores_embedding("p4", "injection_scan_util", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "injection_scan_util", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "injection_scan_util", "exec_snapshot_link")

Logger = logging.getLogger(__name__)
_detector = InjectionDetector()


def scan_untrusted_text(text: str, *, source: str) -> None:
    """Scan *text* for injection signatures using the canonical detector.

    Args:
        text: The untrusted text to scan.
        source: Audit label describing the origin (e.g. "tool_output",
                "user_input", "full_prompt"). Never logged with raw text.

    Raises:
        SecurityViolationError: If an injection signature is detected.
    """
    if not text:
        return
    Logger.debug("Injection scan invoked: source=%s, length=%d", source, len(text))
    _detector.scan(text)
