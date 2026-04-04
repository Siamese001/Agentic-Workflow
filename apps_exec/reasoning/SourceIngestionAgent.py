"""
Source Ingestion Agent — apps_exec/reasoning

Agent for ingesting and processing source documents.
Aligned with apps_lic agent patterns with lifecycle trace integration.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
from apps_exec.services.document_ingestion_service import DocumentIngestionService

_log = logging.getLogger(__name__)


class SourceIngestionAgent:
    """Agent for ingesting source documents."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self._ingestion_service = DocumentIngestionService(config)

        emit_replay_key("source_ingestion", "agent_init")
        emit_determinism_digest("source_ingestion", "agent_init")
        _emit_applies_guardrail("p0", "source_ingestion_agent", "agent_init")
        _emit_reads_policy_state("p0", "source_ingestion_agent", "policy_binding")
        _emit_snapshots_state("p0", "source_ingestion_agent", "agent_state")

    async def ingest_sources(
        self,
        source_dirs: list[str],
        extensions: list[str] | None = None,
    ) -> dict[str, Any]:
        """Ingest source documents from directories."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "SourceIngestionAgent.ingest_sources"
        )
        _emit_orchestrates_workflow("p3", "source_ingestion_agent", "ingestion_workflow")
        _emit_dispatches_agent("p3", "source_ingestion_agent", "ingestion_dispatch")
        _emit_records_telemetry_event("p4", "source_ingestion_agent", "ingestion_start")

        ingested: list[dict[str, Any]] = []
        for source_dir in source_dirs:
            docs = self._ingestion_service.ingest_directory(source_dir, extensions=set(extensions or []))
            ingested.extend(docs)

        _log.info("Ingested %d documents", len(ingested))
        _emit_records_telemetry_event("p4", "source_ingestion_agent", f"ingestion_complete:{len(ingested)}")

        return {
            "success": True,
            "trace_id": _trace_id,
            "documents_ingested": len(ingested),
            "documents": ingested,
        }

    @staticmethod
    def _make_trace_id(source_dirs: list[str]) -> str:
        raw = f"ingest:{','.join(sorted(source_dirs))}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
