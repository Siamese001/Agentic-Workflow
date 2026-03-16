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
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
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
