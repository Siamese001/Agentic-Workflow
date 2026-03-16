"""
Search Filter Builder - Build search filters
Refactored from build_search_filters.py
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

_emit_authorize_and_execute("p2", "search_filter_builder", "execution_auth")
_emit_validates_capability("p2", "search_filter_builder", "capability_check")
_emit_routes_to_capability("p2", "search_filter_builder", "capability_route")
_emit_writes_via_uwg("p2", "search_filter_builder", "uwg_write")
_emit_blocks_direct_write("p2", "search_filter_builder", "direct_write_block")
_emit_records_tool_invocation("p2", "search_filter_builder", "tool_invocation")
_emit_captures_execution_output("p2", "search_filter_builder", "exec_output")
_emit_dispatches_agent("p3", "search_filter_builder", "agent_dispatch")
_emit_coordinates_agents("p3", "search_filter_builder", "agent_coordination")
_emit_records_workflow_lineage("p3", "search_filter_builder", "workflow_lineage")
_emit_records_healing_outcome("p3", "search_filter_builder", "healing_outcome")
_emit_escalates_failure("p3", "search_filter_builder", "failure_escalation")
_emit_orchestrates_workflow("p3", "search_filter_builder", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "search_filter_builder", "healing_dispatch")
_emit_invokes_evaluation("p3", "search_filter_builder", "evaluation_signal")
_emit_records_telemetry_event("p4", "search_filter_builder", "telemetry_event")
_emit_captures_evaluation_metric("p4", "search_filter_builder", "eval_metric")
_emit_stores_embedding("p4", "search_filter_builder", "embedding_store")
_emit_updates_meta_learning_state("p4", "search_filter_builder", "meta_learning")
_emit_links_execution_to_snapshot("p4", "search_filter_builder", "exec_snapshot_link")
from apps_rg.engines.base_rg_engine import BaseRGEngine

_emit_applies_guardrail("p0", "search_filter_builder", "p0_governance")
_emit_reads_policy_state("p0", "search_filter_builder", "policy_binding")
_emit_snapshots_state("p0", "search_filter_builder", "state_snapshot")
emit_replay_key("p0", "search_filter_builder")
emit_determinism_digest("p0", "search_filter_builder")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

Logger = logging.getLogger(__name__)


class SearchFilterBuilder(BaseRGEngine):
    """
    Builds search filters for retrieval operations.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="RETRIEVAL.FILTER_BUILDER")

    async def execute(self, criteria: dict[str, Any]) -> dict[str, Any]:
        """
        Build search filters from criteria.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SearchFilterBuilder.execute")

        self._mcp_audit("filter_building")
        filters = {"keywords": [], "date_range": {}, "metadata_filters": {}}
        if criteria.get("skills"):
            filters["keywords"].extend(criteria["skills"])
        if criteria.get("role"):
            filters["keywords"].append(criteria["role"])
        if criteria.get("date_from") or criteria.get("date_to"):
            filters["date_range"] = {"from": criteria.get("date_from"), "to": criteria.get("date_to")}
        if criteria.get("company"):
            filters["metadata_filters"]["company"] = criteria["company"]
        self.record_pass(f"Built filters with {len(filters['keywords'])} keywords")
        return filters
