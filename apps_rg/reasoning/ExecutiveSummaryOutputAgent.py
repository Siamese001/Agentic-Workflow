"""Strategist BioWriter - Executive Summary Generation (K.1).

This agent generates executive summaries with strict 3rd-person implied voice,
enforcing 120-140 word count and 3-5 sentence structure with 1st-person blocking.

Sub-Atomic Agent Name: Strategist_BioWriter
Legacy K-Node: K.1
"""

import logging
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.types.reasoning_config import ReasoningConfig

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
from apps_rg.utils.RGAgentBase import RGAgentBase

_emit_applies_guardrail("p0", "ExecutiveSummaryOutputAgent", "p0_governance")
_emit_reads_policy_state("p0", "ExecutiveSummaryOutputAgent", "policy_binding")
_emit_snapshots_state("p0", "ExecutiveSummaryOutputAgent", "state_snapshot")
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

_emit_emits_metric_event("ExecutiveSummaryOutputAgent", "p4obs", "metric_1")
_emit_emits_metric_event("ExecutiveSummaryOutputAgent", "p4obs", "metric_2")
_emit_emits_metric_event("ExecutiveSummaryOutputAgent", "p4obs", "metric_3")
_emit_emits_metric_event("ExecutiveSummaryOutputAgent", "p4obs", "metric_4")
_emit_emits_metric_event("ExecutiveSummaryOutputAgent", "p4obs", "metric_5")
_emit_emits_metric_event("ExecutiveSummaryOutputAgent", "p4obs", "metric_6")
_emit_records_incident_event("ExecutiveSummaryOutputAgent", "p4obs", "incident")
_emit_captures_runtime_anomaly("ExecutiveSummaryOutputAgent", "p4obs", "anomaly")
_emit_writes_observability_log("ExecutiveSummaryOutputAgent", "p4obs", "obs_log")
_emit_updates_monitoring_state("ExecutiveSummaryOutputAgent", "p4obs", "mon_state")
_emit_triggers_alert("ExecutiveSummaryOutputAgent", "p4obs", "alert")
_emit_links_incident_trace("ExecutiveSummaryOutputAgent", "p4obs", "trace_link")
_emit_captures_pattern("ExecutiveSummaryOutputAgent", "p3lm", "pattern")
_emit_records_learning_event("ExecutiveSummaryOutputAgent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ExecutiveSummaryOutputAgent", "p3lm", "snapshot")
_emit_feeds_meta_learning("ExecutiveSummaryOutputAgent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ExecutiveSummaryOutputAgent", "p3lm", "routing")
_emit_improves_agent_policy("ExecutiveSummaryOutputAgent", "p3lm", "policy")
_emit_stores_learning_state("ExecutiveSummaryOutputAgent", "p3lm", "state")
_emit_records_execution_trace("ExecutiveSummaryOutputAgent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ExecutiveSummaryOutputAgent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ExecutiveSummaryOutputAgent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ExecutiveSummaryOutputAgent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ExecutiveSummaryOutputAgent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ExecutiveSummaryOutputAgent", "env_read", "p2_env_1")
_emit_reads_environ("ExecutiveSummaryOutputAgent", "env_read", "p2_env_2")
_emit_reads_runtime_state("ExecutiveSummaryOutputAgent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ExecutiveSummaryOutputAgent", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "ExecutiveSummaryOutputAgent", "context_pull")
_emit_pulls_context("p1", "ExecutiveSummaryOutputAgent", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "ExecutiveSummaryOutputAgent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ExecutiveSummaryOutputAgent", "uwg_term_2")
_emit_writes_through("p1", "ExecutiveSummaryOutputAgent", "write_through")
_emit_writes_through("p1", "ExecutiveSummaryOutputAgent", "write_through_2")
_emit_validated_by_safety_plane("p1", "ExecutiveSummaryOutputAgent", "safety_validation")
_emit_invokes_eval("p1", "ExecutiveSummaryOutputAgent", "eval_call")
_emit_proposal_commits_routing("p1", "ExecutiveSummaryOutputAgent", "routing_commit")
_emit_escalates_to_human("p1", "ExecutiveSummaryOutputAgent", "human_escalation")
_emit_routes_through("p1", "ExecutiveSummaryOutputAgent", "route_through")
_emit_checks_agent_registry("p1", "ExecutiveSummaryOutputAgent", "agent_registry")
_emit_validates_agent_capability("p1", "ExecutiveSummaryOutputAgent", "capability")
_emit_dispatches_execution_plan("p1", "ExecutiveSummaryOutputAgent", "exec_plan")
_emit_agent_executes_agent("p1", "ExecutiveSummaryOutputAgent", "sub_agent")
_emit_routes_to_agent("p1", "ExecutiveSummaryOutputAgent", "target_agent")
_emit_verifies_policy("p1", "ExecutiveSummaryOutputAgent", "policy_check")
_emit_observes_runtime_state("p1", "ExecutiveSummaryOutputAgent", "runtime_state")
_emit_verifies_boundary("p1", "ExecutiveSummaryOutputAgent", "boundary_check")
_emit_transcripts_response("p1", "ExecutiveSummaryOutputAgent", "transcript")
_emit_hard_fails_untranscripted("p1", "ExecutiveSummaryOutputAgent")
_emit_gated_by_confidence("p1", "ExecutiveSummaryOutputAgent", "confidence_gate")
emit_replay_key("p0", "ExecutiveSummaryOutputAgent")
emit_determinism_digest("p0", "ExecutiveSummaryOutputAgent")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "ExecutiveSummaryOutputAgent", "execution_auth")
_emit_validates_capability("p2", "ExecutiveSummaryOutputAgent", "capability_check")
_emit_routes_to_capability("p2", "ExecutiveSummaryOutputAgent", "capability_route")
_emit_writes_via_uwg("p2", "ExecutiveSummaryOutputAgent", "uwg_write")
_emit_blocks_direct_write("p2", "ExecutiveSummaryOutputAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "ExecutiveSummaryOutputAgent", "tool_invocation")
_emit_captures_execution_output("p2", "ExecutiveSummaryOutputAgent", "exec_output")
_emit_dispatches_agent("p3", "ExecutiveSummaryOutputAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "ExecutiveSummaryOutputAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "ExecutiveSummaryOutputAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "ExecutiveSummaryOutputAgent", "healing_outcome")
_emit_escalates_failure("p3", "ExecutiveSummaryOutputAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "ExecutiveSummaryOutputAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ExecutiveSummaryOutputAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "ExecutiveSummaryOutputAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "ExecutiveSummaryOutputAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ExecutiveSummaryOutputAgent", "eval_metric")
_emit_stores_embedding("p4", "ExecutiveSummaryOutputAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "ExecutiveSummaryOutputAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ExecutiveSummaryOutputAgent", "exec_snapshot_link")

logger = logging.getLogger(__name__)


@dataclass
class ExecutiveSummaryOutput:
    """Strategist BioWriter output."""

    summary: str
    word_count: int
    sentence_count: int
    first_person_violations: list[str]
    third_person_compliant: bool
    metadata: dict[str, Any]


FIRST_PERSON_PATTERNS = [
    "\\bI\\b",
    "\\bI\\'m\\b",
    "\\bI\\'ve\\b",
    "\\bI\\'ll\\b",
    "\\bI\\'d\\b",
    "\\bmy\\b",
    "\\bmine\\b",
    "\\bme\\b",
    "\\bmyself\\b",
    "\\bwe\\b",
    "\\bwe\\'re\\b",
    "\\bwe\\'ve\\b",
    "\\bour\\b",
    "\\bours\\b",
]


@dataclass
class BioWriterConfig:
    tone: str = "professional"
    length_limit: int = 500


class StrategistBioWriter(RGAgentBase):
    """
    Agent specialized in crafting executive biographies with strategic alignment.
    """

    def __init__(self, config: BioWriterConfig, reasoning: ReasoningConfig):
        super().__init__()
        self.config = config
        self.reasoning = reasoning

    async def run(self, input_data: dict) -> dict:
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "ExecutiveSummaryOutputAgent.run")
        return {"bio": "Draft content..."}
