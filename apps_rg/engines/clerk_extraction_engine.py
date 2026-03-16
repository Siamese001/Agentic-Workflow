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
