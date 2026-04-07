"""
Source Discovery Agent — apps_research/reasoning

Agent for discovering research sources.
Aligned with apps_lic agent patterns with lifecycle trace integration.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_agent,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    _emit_records_execution_trace,
    _emit_records_telemetry_event,
    _emit_snapshots_state,
    emit_determinism_digest,
    emit_replay_key,
)
from apps_research.services.source_discovery_service import SourceDiscoveryService

_log = logging.getLogger(__name__)


class SourceDiscoveryAgent:
    """Agent for discovering research sources."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self._discovery_service = SourceDiscoveryService(config)

        emit_replay_key("source_discovery", "agent_init")
        emit_determinism_digest("source_discovery", "agent_init")
        _emit_applies_guardrail("p0", "source_discovery_agent", "agent_init")
        _emit_reads_policy_state("p0", "source_discovery_agent", "policy_binding")
        _emit_snapshots_state("p0", "source_discovery_agent", "agent_state")

    async def discover_sources(
        self,
        research_topic: str,
        source_types: list[str] | None = None,
        max_sources: int = 20,
    ) -> dict[str, Any]:
        """Discover sources for a research topic."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "SourceDiscoveryAgent.discover_sources",
        )
        _emit_orchestrates_workflow("p3", "source_discovery_agent", "discovery_workflow")
        _emit_dispatches_agent("p3", "source_discovery_agent", "discovery_dispatch")
        _emit_records_telemetry_event("p4", "source_discovery_agent", "discovery_start")

        sources = self._discovery_service.discover_from_query(
            research_topic, source_types, max_sources,
        )

        _log.info("Discovered %d sources for topic: %s", len(sources), research_topic[:50])
        _emit_records_telemetry_event(
            "p4", "source_discovery_agent", f"discovery_complete:{len(sources)}",
        )

        return {
            "success": True,
            "trace_id": _trace_id,
            "sources_discovered": len(sources),
            "sources": sources,
            "topic": research_topic,
        }

    @staticmethod
    def _make_trace_id(topic: str) -> str:
        raw = f"discover:{topic[:100]}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
