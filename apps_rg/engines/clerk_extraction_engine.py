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
from apps_rg.engines.hallucination_detector import HallucinationDetector

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

_emit_engine_lifecycle("clerk_extraction_engine")


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
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "ClerkExtractionEngine.execute"
        )

        mission_input = self.ctx.buffer.read("mission_input")
        if not mission_input or "master_resume" not in mission_input:
            self.record_fail("Missing 'mission_input' or 'master_resume' in Buffer", signal="DATA_MISSING")
            raise ValueError("Buffer missing mission_input")
        source = mission_input["master_resume"]
        self._mcp_audit("extraction_start")
        # P3.1 — Master canonical schema uses `professional_experience`; legacy
        # snapshots use `experience`. Read both, prefer canonical.
        raw_exp = source.get("professional_experience") or source.get("experience", [])
        experience_sections = self._build_sections(raw_exp)
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
        """Standardize raw experience into Sovereign segments.

        P3.1 — Read bullet content from one of three master fields, in priority:
          1. `bullets` (legacy flat list of strings or {bullet_text: ...} dicts)
          2. `bullet_pool` (canonical master_resume_v2.x — rich variant pool)
          3. `highlights` (older role schema, e.g. TraderSense)

        Fan-out a `provenance_field` and `provenance_idx` onto each bullet so
        downstream P2 (VerbatimProvenanceGate) can trace back precisely.
        """
        sections: list[dict] = []
        for role_idx, exp in enumerate(raw_exp):
            company = exp.get("company", "Unknown")
            title = exp.get("title", "Unknown")
            # Pick the first non-empty source field.
            field_used = None
            raw_bullets: list = []
            for field in ("bullets", "bullet_pool", "highlights"):
                candidate = exp.get(field, []) or []
                if candidate:
                    field_used = field
                    raw_bullets = candidate
                    break
            shaped: list[dict] = []
            for b_idx, raw in enumerate(raw_bullets):
                if isinstance(raw, str):
                    text = raw
                elif isinstance(raw, dict):
                    text = raw.get("bullet_text") or raw.get("text") or ""
                else:
                    continue
                if not text:
                    continue
                shaped.append({
                    "bullet_text": text,
                    "source_role_idx": role_idx,
                    "source_field": field_used,
                    "source_idx": b_idx,
                })
            sections.append({
                "company": company,
                "title": title,
                "location": exp.get("location"),
                "dates": exp.get("dates") or exp.get("duration"),
                "bullets": shaped,
            })
        return sections

    def _extract_metrics(self, text: str) -> list[str]:
        """Legacy regex extraction."""
        patterns = ["\\$\\d+\\.?\\d*[MBK]\\+?", "\\d+\\.?\\d*%", "\\d{1,3}(?:,\\d{3})+"]
        found = []
        for pattern in patterns:
            found.extend(re.findall(pattern, text))
        return found
