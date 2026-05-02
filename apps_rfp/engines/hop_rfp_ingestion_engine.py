"""HOP1 rfp_ingestion — wraps RfpIngestionEngine."""

from __future__ import annotations

from typing import Any


class HopRfpIngestionEngine:
    """Adapter for stage 1 — RFP document ingestion / parsing."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        from apps_rfp.engines.rfp_ingestion_engine import RfpIngestionEngine

        request = context.get("rfp_request")

        engine = RfpIngestionEngine()

        ingested: Any = None
        for method_name in ("ingest", "run", "execute", "parse"):
            method = getattr(engine, method_name, None)
            if callable(method):
                try:
                    ingested = method(request) if request is not None else method()
                    break
                except TypeError:
                    continue

        return {
            "ingested_rfp": ingested,
            "rfp_ingestion_completed": ingested is not None,
        }
