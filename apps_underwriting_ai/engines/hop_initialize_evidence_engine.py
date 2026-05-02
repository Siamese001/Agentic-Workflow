"""HOP1 initialize_evidence — wraps EvidenceRegisterEngine.initialize.

Thin substrate-compatible adapter for the HOP pipeline substrate (plan
apps-hop-substrate-f7751b). The existing ``UnderwritingEngine.run()``
remains the primary entry point; this adapter is used when the shared
``HopPipelineExecutor`` drives the 5-stage walk declaratively.
"""

from __future__ import annotations

from typing import Any


class HopInitializeEvidenceEngine:
    """Adapter for stage 1 — evidence register initialization."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        from apps_underwriting_ai.engines.evidence_register_engine import (
            EvidenceRegisterEngine,
        )

        request = context.get("underwriting_request")
        request_id = getattr(request, "request_id", "") if request else ""

        engine = EvidenceRegisterEngine()
        register = engine.initialize(request_id)

        return {"evidence_register": register}
