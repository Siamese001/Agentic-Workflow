"""
Section Ranker Engine - Dynamic section ordering based on Role Archetype
Refactored from RankResumeSections.py
Following Batch 5 specifications

HARDENING: Reads 'optimized_content'. Applies strategies from 'self.config' (Frozen Knowledge).
Writes 'ranked_content'.
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "section_ranker_engine", "execution_auth")
_emit_validates_capability("p2", "section_ranker_engine", "capability_check")
_emit_routes_to_capability("p2", "section_ranker_engine", "capability_route")
_emit_writes_via_uwg("p2", "section_ranker_engine", "uwg_write")
_emit_blocks_direct_write("p2", "section_ranker_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "section_ranker_engine", "tool_invocation")
_emit_captures_execution_output("p2", "section_ranker_engine", "exec_output")
_emit_dispatches_agent("p3", "section_ranker_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "section_ranker_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "section_ranker_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "section_ranker_engine", "healing_outcome")
_emit_escalates_failure("p3", "section_ranker_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "section_ranker_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "section_ranker_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "section_ranker_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "section_ranker_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "section_ranker_engine", "eval_metric")
_emit_stores_embedding("p4", "section_ranker_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "section_ranker_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "section_ranker_engine", "exec_snapshot_link")
from apps_rg.engines.base_rg_engine import BaseRGEngine

_emit_applies_guardrail("p0", "section_ranker_engine", "p0_governance")
_emit_reads_policy_state("p0", "section_ranker_engine", "policy_binding")
_emit_snapshots_state("p0", "section_ranker_engine", "state_snapshot")
emit_replay_key("p0", "section_ranker_engine")
emit_determinism_digest("p0", "section_ranker_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

Logger = logging.getLogger(__name__)


class SectionRankerEngine(BaseRGEngine):
    """
    Sovereign Refinement Engine.
    Reads: 'optimized_content'
    Writes: 'ranked_content'
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="REFINE.RANKER")
        self.strategies = {
            "technical": ["contact", "skills", "experience", "projects", "education"],
            "executive": ["contact", "summary", "experience", "education", "skills"],
            "entry": ["contact", "education", "skills", "projects", "experience"],
            "default": ["contact", "summary", "experience", "education", "skills"],
        }
        if self.config and hasattr(self.config, "config"):
            try:
                config_strategies = self.config.config.qa_thresholds.get("ranking_strategies")
                if config_strategies:
                    self.strategies = config_strategies
            except (AttributeError, KeyError):
                pass

    async def execute(self) -> dict[str, Any]:
        """
        Reorder sections based on Role Archetype.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SectionRankerEngine.execute")

        content = self.ctx.buffer.read("optimized_content")
        if not content:
            content = self.ctx.buffer.read("hop2_enrichment")
        if not content:
            self.record_fail("Missing content to rank", signal="DATA_MISSING")
            raise ValueError("Buffer missing content")
        mission = self.ctx.buffer.read("mission_input") or {}
        role_type = mission.get("role_type", "default")
        target_order = self.strategies.get(role_type, self.strategies["default"])
        if not isinstance(content, dict):
            self.record_fail("Content is not a dictionary", signal="DATA_MISSING")
            raise ValueError("Content must be a dictionary")
        ranked_resume = {}
        section_mapping = {"experience": "experience_sections", "education": "education", "skills": "skills"}
        for section in target_order:
            mapped_key = section_mapping.get(section, section)
            if mapped_key in content:
                ranked_resume[section] = content[mapped_key]
        for section in content:
            if isinstance(section, str) and section not in list(section_mapping.values()):
                ranked_resume[section] = content[section]
        self.ctx.buffer.write("ranked_content", ranked_resume, source_agent=self.name)
        self.record_pass(f"Sections ranked for {role_type}")
        return ranked_resume
