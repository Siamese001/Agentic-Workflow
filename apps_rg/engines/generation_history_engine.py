"""
Generation History Engine - Query past generations
Refactored from query_past_generations.py
"""

from __future__ import annotations

import logging
from typing import Any

from apps_rg.engines.BaseRGEngine import BaseRGEngine

Logger = logging.getLogger(__name__)


class GenerationHistoryEngine(BaseRGEngine):
    """
    Retrieves and queries past generation history.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="RETRIEVAL.HISTORY")

    async def execute(self, query: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Query generation history.
        """
        self._mcp_audit("history_query", {"query": query})

        # Placeholder for actual database query
        results = []

        # In production, would query from persistent storage
        if hasattr(self.ctx, "generation_history"):
            results = self.ctx.generation_history

        # Filter by query parameters
        if query.get("company"):
            results = [r for r in results if r.get("company") == query["company"]]

        if query.get("role"):
            results = [r for r in results if r.get("role") == query["role"]]

        self.record_pass(f"Retrieved {len(results)} historical generations")
        return results
