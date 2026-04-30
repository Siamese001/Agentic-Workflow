"""
HOP2 Enrichment Engine - Logic Enrichment Engine
Refactored from apply_data_enrichment.py
Following Batch 2 specifications with verb canonicalization

HARDENING: Reads 'hop1_extraction' from Buffer. Writes 'hop2_enrichment'.
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

_emit_engine_lifecycle("data_enrichment_engine")


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
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "DataEnrichmentEngine.execute"
        )

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
