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

from apps_rg.engines.base_rg_engine import BaseRGEngine

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

from apps_rg.engines._lifecycle_emits import _emit_engine_lifecycle

_emit_engine_lifecycle("section_ranker_engine")


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
            "executive": ["contact", "summary", "experience", "competencies", "education", "skills"],
            "strategic_advisory": [
                "contact", "summary", "experience", "competencies",
                "skills", "certifications_and_credentials", "education",
            ],
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
        # P3.2 — RoleArchetypeClassifier writes either `role_type` (strategy
        # key compatible with the existing table) or `role_archetype` (the
        # 7-class archetype). Prefer the more specific archetype if a strategy
        # exists for it, fall back to role_type.
        archetype = mission.get("role_archetype")
        role_type = mission.get("role_type", "default")
        if archetype and archetype in self.strategies:
            target_order = self.strategies[archetype]
        else:
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
