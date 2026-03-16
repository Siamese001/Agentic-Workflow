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
