"""
Search Filter Builder - Build search filters
Refactored from build_search_filters.py
"""

from __future__ import annotations

import logging
from typing import Any

from apps_rg.engines.base_rg_engine import BaseRGEngine

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

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
        self._mcp_audit("filter_building")

        filters = {"keywords": [], "date_range": {}, "metadata_filters": {}}

        # Build keyword filters
        if criteria.get("skills"):
            filters["keywords"].extend(criteria["skills"])

        if criteria.get("role"):
            filters["keywords"].append(criteria["role"])

        # Build date filters
        if criteria.get("date_from") or criteria.get("date_to"):
            filters["date_range"] = {
                "from": criteria.get("date_from"),
                "to": criteria.get("date_to"),
            }

        # Build metadata filters
        if criteria.get("company"):
            filters["metadata_filters"]["company"] = criteria["company"]

        self.record_pass(f"Built filters with {len(filters['keywords'])} keywords")
        return filters
