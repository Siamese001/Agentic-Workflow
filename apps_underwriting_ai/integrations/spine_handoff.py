"""SpineHandoff — packaging output for the apps spine surface.

Skeleton implementation. Wraps a final UnderwritingResult into a
spine-friendly handoff envelope. Real spine wiring (governed_app_runner
delegation, PromptEnvelope construction) will be layered on top.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from apps_underwriting_ai.types.underwriting_types import UnderwritingResult


@dataclass(frozen=True)
class SpineHandoffEnvelope:
    """Envelope returned by :meth:`SpineHandoff.package`."""

    app: str
    route: str
    request_id: str
    payload: dict[str, Any]


class SpineHandoff:
    """Packages an UnderwritingResult for spine handoff."""

    APP = "apps_underwriting_ai"
    ROUTE = "R3_grounded_read"

    def package(self, result: UnderwritingResult) -> SpineHandoffEnvelope:
        """Package a result into a spine handoff envelope.

        Args:
            result: UnderwritingResult to package.

        Returns:
            SpineHandoffEnvelope ready for spine consumption.
        """
        return SpineHandoffEnvelope(
            app=self.APP,
            route=self.ROUTE,
            request_id=result.request_id,
            payload={
                "verdict": result.decision.verdict.value,
                "rationale": result.decision.rationale,
                "evidence_refs": list(result.decision.evidence_refs),
                "feature_summary": dict(result.decision.feature_summary),
                "trace_id": result.trace_id,
            },
        )
