"""
Search Filter Builder - Build search filters
Refactored from build_search_filters.py
"""

from __future__ import annotations

import logging
from typing import Any

from apps_rg.engines.base_rg_engine import BaseRGEngine
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

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
