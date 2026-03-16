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
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
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
