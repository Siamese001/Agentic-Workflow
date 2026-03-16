"""
Generation History Engine - Query past generations
Refactored from query_past_generations.py
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

_emit_applies_guardrail("p0", "generation_history_engine", "p0_governance")
_emit_reads_policy_state("p0", "generation_history_engine", "policy_binding")
_emit_snapshots_state("p0", "generation_history_engine", "state_snapshot")
emit_replay_key("p0", "generation_history_engine")
emit_determinism_digest("p0", "generation_history_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "GenerationHistoryEngine.execute")

        self._mcp_audit("history_query", {"query": query})
        results = []
        if hasattr(self.ctx, "generation_history"):
            results = self.ctx.generation_history
        if query.get("company"):
            results = [r for r in results if r.get("company") == query["company"]]
        if query.get("role"):
            results = [r for r in results if r.get("role") == query["role"]]
        self.record_pass(f"Retrieved {len(results)} historical generations")
        return results
