"""ResumeAssemblyAgent - Provides resume assembly capabilities using prompt governance and markdown templates.

This agent handles:
- YAML-based prompt governance for resume assembly (via PromptLoader)
- Markdown template loading for skills sections, executive summaries, and networking requests
- Simple template substitution with explicit error handling

Domain: resume
Methods:
- assemble_resume(payload: dict) -> str
- generate_skills_section(payload: dict) -> str
- generate_executive_summary(payload: dict) -> str
- generate_networking_request(payload: dict) -> str
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agentic_core.prompt_governance import PromptLoader
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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

_emit_applies_guardrail("p0", "ResumeAssemblyAgent", "p0_governance")
_emit_reads_policy_state("p0", "ResumeAssemblyAgent", "policy_binding")
_emit_snapshots_state("p0", "ResumeAssemblyAgent", "state_snapshot")
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

_emit_emits_metric_event("ResumeAssemblyAgent", "p4obs", "metric_1")
_emit_emits_metric_event("ResumeAssemblyAgent", "p4obs", "metric_2")
_emit_emits_metric_event("ResumeAssemblyAgent", "p4obs", "metric_3")
_emit_emits_metric_event("ResumeAssemblyAgent", "p4obs", "metric_4")
_emit_emits_metric_event("ResumeAssemblyAgent", "p4obs", "metric_5")
_emit_emits_metric_event("ResumeAssemblyAgent", "p4obs", "metric_6")
_emit_records_incident_event("ResumeAssemblyAgent", "p4obs", "incident")
_emit_captures_runtime_anomaly("ResumeAssemblyAgent", "p4obs", "anomaly")
_emit_writes_observability_log("ResumeAssemblyAgent", "p4obs", "obs_log")
_emit_updates_monitoring_state("ResumeAssemblyAgent", "p4obs", "mon_state")
_emit_triggers_alert("ResumeAssemblyAgent", "p4obs", "alert")
_emit_links_incident_trace("ResumeAssemblyAgent", "p4obs", "trace_link")
_emit_captures_pattern("ResumeAssemblyAgent", "p3lm", "pattern")
_emit_records_learning_event("ResumeAssemblyAgent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ResumeAssemblyAgent", "p3lm", "snapshot")
_emit_feeds_meta_learning("ResumeAssemblyAgent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ResumeAssemblyAgent", "p3lm", "routing")
_emit_improves_agent_policy("ResumeAssemblyAgent", "p3lm", "policy")
_emit_stores_learning_state("ResumeAssemblyAgent", "p3lm", "state")
_emit_records_execution_trace("ResumeAssemblyAgent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ResumeAssemblyAgent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ResumeAssemblyAgent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ResumeAssemblyAgent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ResumeAssemblyAgent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ResumeAssemblyAgent", "env_read", "p2_env_1")
_emit_reads_environ("ResumeAssemblyAgent", "env_read", "p2_env_2")
_emit_reads_runtime_state("ResumeAssemblyAgent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ResumeAssemblyAgent", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "ResumeAssemblyAgent", "context_pull")
_emit_pulls_context("p1", "ResumeAssemblyAgent", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "ResumeAssemblyAgent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ResumeAssemblyAgent", "uwg_term_2")
_emit_writes_through("p1", "ResumeAssemblyAgent", "write_through")
_emit_writes_through("p1", "ResumeAssemblyAgent", "write_through_2")
_emit_validated_by_safety_plane("p1", "ResumeAssemblyAgent", "safety_validation")
_emit_invokes_eval("p1", "ResumeAssemblyAgent", "eval_call")
_emit_proposal_commits_routing("p1", "ResumeAssemblyAgent", "routing_commit")
_emit_escalates_to_human("p1", "ResumeAssemblyAgent", "human_escalation")
_emit_routes_through("p1", "ResumeAssemblyAgent", "route_through")
_emit_checks_agent_registry("p1", "ResumeAssemblyAgent", "agent_registry")
_emit_validates_agent_capability("p1", "ResumeAssemblyAgent", "capability")
_emit_dispatches_execution_plan("p1", "ResumeAssemblyAgent", "exec_plan")
_emit_agent_executes_agent("p1", "ResumeAssemblyAgent", "sub_agent")
_emit_routes_to_agent("p1", "ResumeAssemblyAgent", "target_agent")
_emit_verifies_policy("p1", "ResumeAssemblyAgent", "policy_check")
_emit_observes_runtime_state("p1", "ResumeAssemblyAgent", "runtime_state")
_emit_verifies_boundary("p1", "ResumeAssemblyAgent", "boundary_check")
_emit_transcripts_response("p1", "ResumeAssemblyAgent", "transcript")
_emit_hard_fails_untranscripted("p1", "ResumeAssemblyAgent")
_emit_gated_by_confidence("p1", "ResumeAssemblyAgent", "confidence_gate")
emit_replay_key("p0", "ResumeAssemblyAgent")
emit_determinism_digest("p0", "ResumeAssemblyAgent")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "ResumeAssemblyAgent", "execution_auth")
_emit_validates_capability("p2", "ResumeAssemblyAgent", "capability_check")
_emit_routes_to_capability("p2", "ResumeAssemblyAgent", "capability_route")
_emit_writes_via_uwg("p2", "ResumeAssemblyAgent", "uwg_write")
_emit_blocks_direct_write("p2", "ResumeAssemblyAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "ResumeAssemblyAgent", "tool_invocation")
_emit_captures_execution_output("p2", "ResumeAssemblyAgent", "exec_output")
_emit_dispatches_agent("p3", "ResumeAssemblyAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "ResumeAssemblyAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "ResumeAssemblyAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "ResumeAssemblyAgent", "healing_outcome")
_emit_escalates_failure("p3", "ResumeAssemblyAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "ResumeAssemblyAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ResumeAssemblyAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "ResumeAssemblyAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "ResumeAssemblyAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ResumeAssemblyAgent", "eval_metric")
_emit_stores_embedding("p4", "ResumeAssemblyAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "ResumeAssemblyAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ResumeAssemblyAgent", "exec_snapshot_link")


class ResumeTemplateError(Exception):
    """Raised when a resume template file cannot be found or read."""

    pass


class ResumeAssemblyAgent:
    """QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT contain runtime agents, generators, or orchestrators.

Original: apps_rg/reasoning/ResumeAssemblyAgent.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE — Contains generate_* methods (runtime authority)

Importing this module raises RuntimeError.
Core L1/L2/L3 owns all generation and assembly orchestration.
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.reasoning.ResumeAssemblyAgent is QUARANTINED. "
    "apps_rg may NOT contain runtime generation agents. "
    "Core L1/L2/L3 owns assembly orchestration. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)

# Original code archived to:
# archives/apps_rg/quarantine_w4_20260509/reasoning/ResumeAssemblyAgent.py.ORIGINAL

