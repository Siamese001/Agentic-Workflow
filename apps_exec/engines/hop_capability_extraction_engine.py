"""HOP3 capability_extraction — wraps CapabilityExtractionEngine."""

from __future__ import annotations

from typing import Any


class HopCapabilityExtractionEngine:
    """Adapter for stage 3 — capability evidence extraction."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        from apps_exec.engines.capability_extraction_engine import (
            CapabilityExtractionEngine,
        )

        ingested = context.get("ingested_documents")

        engine = CapabilityExtractionEngine()

        extracted: Any = None
        for method_name in ("execute", "extract", "run"):
            method = getattr(engine, method_name, None)
            if callable(method):
                try:
                    extracted = (
                        method(ingested) if ingested is not None else method()
                    )
                    break
                except TypeError:
                    continue

        return {
            "extracted_capabilities": extracted,
            "capability_extraction_completed": extracted is not None,
        }
