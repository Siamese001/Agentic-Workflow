"""HOP1 ingestion — wraps IngestionEngine."""

from __future__ import annotations

from typing import Any


class HopIngestionEngine:
    """Adapter for stage 1 — source document ingestion."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        from apps_exec.engines.ingestion_engine import IngestionEngine

        request = context.get("exec_request")

        engine = IngestionEngine()

        ingested: Any = None
        for method_name in ("execute", "ingest", "run"):
            method = getattr(engine, method_name, None)
            if callable(method):
                try:
                    ingested = method(request) if request is not None else method()
                    break
                except TypeError:
                    continue

        return {
            "ingested_documents": ingested,
            "ingestion_completed": ingested is not None,
        }
