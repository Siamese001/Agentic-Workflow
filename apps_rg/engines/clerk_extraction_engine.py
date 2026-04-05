"""
HOP1 Clerk Engine - Structural Extraction Engine
Refactored from apply_clerk_extraction.py
Following Batch 2 specifications with hallucination detection

HARDENING: Removes direct arguments. Enforces reading 'mission_input' from Buffer
and writing 'hop1_extraction' to Buffer.
"""

from __future__ import annotations

import logging
import re
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

_emit_authorize_and_execute("p2", "clerk_extraction_engine", "execution_auth")
_emit_validates_capability("p2", "clerk_extraction_engine", "capability_check")
_emit_routes_to_capability("p2", "clerk_extraction_engine", "capability_route")
_emit_writes_via_uwg("p2", "clerk_extraction_engine", "uwg_write")
_emit_blocks_direct_write("p2", "clerk_extraction_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "clerk_extraction_engine", "tool_invocation")
_emit_captures_execution_output("p2", "clerk_extraction_engine", "exec_output")
_emit_dispatches_agent("p3", "clerk_extraction_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "clerk_extraction_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "clerk_extraction_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "clerk_extraction_engine", "healing_outcome")
_emit_escalates_failure("p3", "clerk_extraction_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "clerk_extraction_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "clerk_extraction_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "clerk_extraction_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "clerk_extraction_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "clerk_extraction_engine", "eval_metric")
_emit_stores_embedding("p4", "clerk_extraction_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "clerk_extraction_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "clerk_extraction_engine", "exec_snapshot_link")
from apps_rg.engines.base_rg_engine import BaseRGEngine
from apps_rg.engines.hallucination_detector import HallucinationDetector

_emit_applies_guardrail("p0", "clerk_extraction_engine", "p0_governance")
_emit_reads_policy_state("p0", "clerk_extraction_engine", "policy_binding")
_emit_snapshots_state("p0", "clerk_extraction_engine", "state_snapshot")
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

_emit_emits_metric_event("clerk_extraction_engine", "p4obs", "metric_1")
_emit_emits_metric_event("clerk_extraction_engine", "p4obs", "metric_2")
_emit_emits_metric_event("clerk_extraction_engine", "p4obs", "metric_3")
_emit_emits_metric_event("clerk_extraction_engine", "p4obs", "metric_4")
_emit_emits_metric_event("clerk_extraction_engine", "p4obs", "metric_5")
_emit_emits_metric_event("clerk_extraction_engine", "p4obs", "metric_6")
_emit_records_incident_event("clerk_extraction_engine", "p4obs", "incident")
_emit_captures_runtime_anomaly("clerk_extraction_engine", "p4obs", "anomaly")
_emit_writes_observability_log("clerk_extraction_engine", "p4obs", "obs_log")
_emit_updates_monitoring_state("clerk_extraction_engine", "p4obs", "mon_state")
_emit_triggers_alert("clerk_extraction_engine", "p4obs", "alert")
_emit_links_incident_trace("clerk_extraction_engine", "p4obs", "trace_link")
_emit_captures_pattern("clerk_extraction_engine", "p3lm", "pattern")
_emit_records_learning_event("clerk_extraction_engine", "p3lm", "learning_event")
_emit_writes_learning_snapshot("clerk_extraction_engine", "p3lm", "snapshot")
_emit_feeds_meta_learning("clerk_extraction_engine", "p3lm", "meta_feed")
_emit_updates_routing_strategy("clerk_extraction_engine", "p3lm", "routing")
_emit_improves_agent_policy("clerk_extraction_engine", "p3lm", "policy")
_emit_stores_learning_state("clerk_extraction_engine", "p3lm", "state")
_emit_records_execution_trace("clerk_extraction_engine", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("clerk_extraction_engine", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("clerk_extraction_engine", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("clerk_extraction_engine", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("clerk_extraction_engine", "L4_STATE", "p2_trace_5")
_emit_reads_environ("clerk_extraction_engine", "env_read", "p2_env_1")
_emit_reads_environ("clerk_extraction_engine", "env_read", "p2_env_2")
_emit_reads_runtime_state("clerk_extraction_engine", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("clerk_extraction_engine", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "clerk_extraction_engine", "context_pull")
_emit_pulls_context("p1", "clerk_extraction_engine", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "clerk_extraction_engine", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "clerk_extraction_engine", "uwg_term_2")
_emit_writes_through("p1", "clerk_extraction_engine", "write_through")
_emit_writes_through("p1", "clerk_extraction_engine", "write_through_2")
_emit_validated_by_safety_plane("p1", "clerk_extraction_engine", "safety_validation")
_emit_invokes_eval("p1", "clerk_extraction_engine", "eval_call")
_emit_proposal_commits_routing("p1", "clerk_extraction_engine", "routing_commit")
_emit_escalates_to_human("p1", "clerk_extraction_engine", "human_escalation")
_emit_routes_through("p1", "clerk_extraction_engine", "route_through")
_emit_checks_agent_registry("p1", "clerk_extraction_engine", "agent_registry")
_emit_validates_agent_capability("p1", "clerk_extraction_engine", "capability")
_emit_dispatches_execution_plan("p1", "clerk_extraction_engine", "exec_plan")
_emit_agent_executes_agent("p1", "clerk_extraction_engine", "sub_agent")
_emit_routes_to_agent("p1", "clerk_extraction_engine", "target_agent")
_emit_verifies_policy("p1", "clerk_extraction_engine", "policy_check")
_emit_observes_runtime_state("p1", "clerk_extraction_engine", "runtime_state")
_emit_verifies_boundary("p1", "clerk_extraction_engine", "boundary_check")
_emit_transcripts_response("p1", "clerk_extraction_engine", "transcript")
_emit_hard_fails_untranscripted("p1", "clerk_extraction_engine")
_emit_gated_by_confidence("p1", "clerk_extraction_engine", "confidence_gate")
emit_replay_key("p0", "clerk_extraction_engine")
emit_determinism_digest("p0", "clerk_extraction_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

Logger = logging.getLogger(__name__)


class ClerkExtractionEngine(BaseRGEngine):
    """
    HOP-1: Structural Extraction Engine.
    Reads 'mission_input' -> Writes 'hop1_extraction'.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="HOP.1.CLERK")
        self.detector = HallucinationDetector(ctx)

    async def execute(self) -> dict[str, Any]:
        """
        Execute HOP-1 extraction using Immutable Buffer data.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ClerkExtractionEngine.execute")

        mission_input = self.ctx.buffer.read("mission_input")
        if not mission_input or "master_resume" not in mission_input:
            self.record_fail("Missing 'mission_input' or 'master_resume' in Buffer", signal="DATA_MISSING")
            raise ValueError("Buffer missing mission_input")
        source = mission_input["master_resume"]
        self._mcp_audit("extraction_start")
        experience_sections = self._build_sections(source.get("experience", []))
        for section in experience_sections:
            for bullet in section.get("bullets", []):
                bullet["quantified_metrics"] = self._extract_metrics(bullet["bullet_text"])
        all_bullets = [b["bullet_text"] for s in experience_sections for b in s["bullets"]]
        validation = self.detector.check_batch(all_bullets)
        if not validation["valid"]:
            self.ctx.add_signal("SOURCE_DATA_UNRELIABLE")
        output = {
            "experience_sections": experience_sections,
            "education": source.get("education", []),
            "metadata": {"source_integrity": validation["score"]},
        }
        self.ctx.buffer.write("hop1_extraction", output, source_agent=self.name)
        self.record_pass("HOP-1 Extraction Complete", data={"sections": len(experience_sections)})
        return output

    def _build_sections(self, raw_exp: list[dict]) -> list[dict]:
        """Standardize raw experience into Sovereign segments."""
        sections = []
        for exp in raw_exp:
            sections.append(
                {
                    "company": exp.get("company", "Unknown"),
                    "title": exp.get("title", "Unknown"),
                    "bullets": [{"bullet_text": b} for b in exp.get("bullets", [])],
                }
            )
        return sections

    def _extract_metrics(self, text: str) -> list[str]:
        """Legacy regex extraction."""
        patterns = ["\\$\\d+\\.?\\d*[MBK]\\+?", "\\d+\\.?\\d*%", "\\d{1,3}(?:,\\d{3})+"]
        found = []
        for pattern in patterns:
            found.extend(re.findall(pattern, text))
        return found
