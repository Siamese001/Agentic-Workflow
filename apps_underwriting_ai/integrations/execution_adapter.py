"""ExecutionAdapter — runtime handoff for apps_underwriting_ai.

Mirrors the apps_rfp / apps_research execution-adapter pattern. Wraps an
inbound runtime request, dispatches to UnderwritingEngine.run(), and
returns a structured response.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from apps_underwriting_ai.engines.underwriting_engine import UnderwritingEngine
from apps_underwriting_ai.types.underwriting_types import (
    UnderwritingRequest,
    UnderwritingResult,
)


@dataclass(frozen=True)
class ExecutionRequest:
    """Inbound runtime execution request for an underwriting run."""

    request_id: str
    applicant_id: str
    product_class: str
    documents: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    metadata: dict[str, Any] = field(default_factory=dict)
    trace_id: str = ""


class ExecutionAdapter:
    """Adapts inbound execution requests to UnderwritingEngine runs."""

    def __init__(self, engine: UnderwritingEngine | None = None) -> None:
        self._engine = engine or UnderwritingEngine()

    def execute(self, request: ExecutionRequest) -> UnderwritingResult:
        """Dispatch the inbound request to UnderwritingEngine.

        Args:
            request: ExecutionRequest received from the runtime.

        Returns:
            UnderwritingResult with full pipeline output.
        """
        underwriting_request = UnderwritingRequest(
            request_id=request.request_id,
            applicant_id=request.applicant_id,
            product_class=request.product_class,
            documents=request.documents,
            metadata=request.metadata,
        )
        return self._engine.run(underwriting_request, trace_id=request.trace_id)
