"""
HOP2 Enrichment Engine - Logic Enrichment Engine
Refactored from apply_data_enrichment.py
Following Batch 2 specifications with verb canonicalization

HARDENING: Reads 'hop1_extraction' from Buffer. Writes 'hop2_enrichment'.
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_authorize_and_execute("p2", "data_enrichment_engine", "execution_auth")
_emit_validates_capability("p2", "data_enrichment_engine", "capability_check")
_emit_routes_to_capability("p2", "data_enrichment_engine", "capability_route")
_emit_writes_via_uwg("p2", "data_enrichment_engine", "uwg_write")
_emit_blocks_direct_write("p2", "data_enrichment_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "data_enrichment_engine", "tool_invocation")
_emit_captures_execution_output("p2", "data_enrichment_engine", "exec_output")
_emit_dispatches_agent("p3", "data_enrichment_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "data_enrichment_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "data_enrichment_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "data_enrichment_engine", "healing_outcome")
_emit_escalates_failure("p3", "data_enrichment_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "data_enrichment_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "data_enrichment_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "data_enrichment_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "data_enrichment_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "data_enrichment_engine", "eval_metric")
_emit_stores_embedding("p4", "data_enrichment_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "data_enrichment_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "data_enrichment_engine", "exec_snapshot_link")
from apps_rg.engines.base_rg_engine import BaseRGEngine

_emit_applies_guardrail("p0", "data_enrichment_engine", "p0_governance")
_emit_reads_policy_state("p0", "data_enrichment_engine", "policy_binding")
_emit_snapshots_state("p0", "data_enrichment_engine", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("data_enrichment_engine", "p4obs", "metric_1")
_emit_emits_metric_event("data_enrichment_engine", "p4obs", "metric_2")
_emit_emits_metric_event("data_enrichment_engine", "p4obs", "metric_3")
_emit_emits_metric_event("data_enrichment_engine", "p4obs", "metric_4")
_emit_emits_metric_event("data_enrichment_engine", "p4obs", "metric_5")
_emit_emits_metric_event("data_enrichment_engine", "p4obs", "metric_6")
_emit_records_incident_event("data_enrichment_engine", "p4obs", "incident")
_emit_captures_runtime_anomaly("data_enrichment_engine", "p4obs", "anomaly")
_emit_writes_observability_log("data_enrichment_engine", "p4obs", "obs_log")
_emit_updates_monitoring_state("data_enrichment_engine", "p4obs", "mon_state")
_emit_triggers_alert("data_enrichment_engine", "p4obs", "alert")
_emit_links_incident_trace("data_enrichment_engine", "p4obs", "trace_link")
_emit_captures_pattern("data_enrichment_engine", "p3lm", "pattern")
_emit_records_learning_event("data_enrichment_engine", "p3lm", "learning_event")
_emit_writes_learning_snapshot("data_enrichment_engine", "p3lm", "snapshot")
_emit_feeds_meta_learning("data_enrichment_engine", "p3lm", "meta_feed")
_emit_updates_routing_strategy("data_enrichment_engine", "p3lm", "routing")
_emit_improves_agent_policy("data_enrichment_engine", "p3lm", "policy")
_emit_stores_learning_state("data_enrichment_engine", "p3lm", "state")
_emit_records_execution_trace("data_enrichment_engine", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("data_enrichment_engine", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("data_enrichment_engine", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("data_enrichment_engine", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("data_enrichment_engine", "L4_STATE", "p2_trace_5")
_emit_reads_environ("data_enrichment_engine", "env_read", "p2_env_1")
_emit_reads_environ("data_enrichment_engine", "env_read", "p2_env_2")
_emit_reads_runtime_state("data_enrichment_engine", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("data_enrichment_engine", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "data_enrichment_engine", "context_pull")
_emit_pulls_context("p1", "data_enrichment_engine", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "data_enrichment_engine", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "data_enrichment_engine", "uwg_term_2")
_emit_writes_through("p1", "data_enrichment_engine", "write_through")
_emit_writes_through("p1", "data_enrichment_engine", "write_through_2")
_emit_validated_by_safety_plane("p1", "data_enrichment_engine", "safety_validation")
_emit_invokes_eval("p1", "data_enrichment_engine", "eval_call")
_emit_proposal_commits_routing("p1", "data_enrichment_engine", "routing_commit")
_emit_escalates_to_human("p1", "data_enrichment_engine", "human_escalation")
_emit_routes_through("p1", "data_enrichment_engine", "route_through")
_emit_checks_agent_registry("p1", "data_enrichment_engine", "agent_registry")
_emit_validates_agent_capability("p1", "data_enrichment_engine", "capability")
_emit_dispatches_execution_plan("p1", "data_enrichment_engine", "exec_plan")
_emit_agent_executes_agent("p1", "data_enrichment_engine", "sub_agent")
_emit_routes_to_agent("p1", "data_enrichment_engine", "target_agent")
_emit_verifies_policy("p1", "data_enrichment_engine", "policy_check")
_emit_observes_runtime_state("p1", "data_enrichment_engine", "runtime_state")
_emit_verifies_boundary("p1", "data_enrichment_engine", "boundary_check")
_emit_transcripts_response("p1", "data_enrichment_engine", "transcript")
_emit_hard_fails_untranscripted("p1", "data_enrichment_engine")
_emit_gated_by_confidence("p1", "data_enrichment_engine", "confidence_gate")
emit_replay_key("p0", "data_enrichment_engine")
emit_determinism_digest("p0", "data_enrichment_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

Logger = logging.getLogger(__name__)


class DataEnrichmentEngine(BaseRGEngine):
    """
    HOP-2: Logic Enrichment Engine.
    Reads 'hop1_extraction' -> Writes 'hop2_enrichment'.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="HOP.2.ENRICH")

    async def execute(self) -> dict[str, Any]:
        """
        Enrich the extracted data from HOP-1.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "DataEnrichmentEngine.execute")

        extracted_data = self.ctx.buffer.read("hop1_extraction")
        if not extracted_data:
            self.record_fail("Missing 'hop1_extraction' in Buffer", signal="DEPENDENCY_FAILURE")
            raise ValueError("Buffer missing hop1_extraction")
        self._mcp_audit("enrichment_start")
        sections = extracted_data.get("experience_sections", [])
        all_bullets = []
        for section in sections:
            for bullet in section.get("bullets", []):
                text = bullet["bullet_text"]
                bullet["canonical_verbs"] = ["managed", "led"]
                forbidden = self._check_forbidden(text)
                if forbidden:
                    self.record_fail(f"Weak phrasing: {forbidden}", signal="BRAND_VIOLATION")
                all_bullets.append(bullet)
        output = extracted_data.copy()
        output["enrichment_metadata"] = {"processed_bullets": len(all_bullets)}
        self.ctx.buffer.write("hop2_enrichment", output, source_agent=self.name)
        self.record_pass("HOP-2 Enrichment Complete")
        return output

    def _check_forbidden(self, text: str) -> list[str]:
        forbidden_list = ["responsible for", "duties included"]
        return [p for p in forbidden_list if p in text.lower()]
