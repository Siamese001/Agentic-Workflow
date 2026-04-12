"""Low-Risk Fallback.

Constrained fallback generation and policy-compliant responses.
"""

import logging
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_records_telemetry_event,
)

log = logging.getLogger(__name__)


@dataclass
class FallbackResult:
    """Result of fallback generation."""

    response: str
    is_fallback: bool
    risk_level: str  # "low", "medium", "high"
    policy_compliant: bool
    constraints_applied: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class LowRiskFallback:
    """Generates low-risk fallback responses.

    The LowRiskFallback provides constrained responses when normal
    retrieval fails, ensuring policy compliance and risk mitigation.
    """

    def __init__(self):
        """Initialize the fallback generator."""
        self._fallback_templates = self._load_templates()
        log.info("LowRiskFallback initialized")

    def generate(
        self,
        query: str,
        reason: str,
        query_context: dict[str, Any],
    ) -> FallbackResult:
        """Generate fallback response.

        Args:
            query: Original query
            reason: Reason for fallback
            query_context: Query context

        Returns:
            FallbackResult with constrained response
        """
        trace_id = f"fallback_{hash(query) % 10000}"
        _emit_records_execution_trace(
            trace_id,
            LayerSegment.L1_REASONING,
            "LowRiskFallback.generate",
        )

        # Determine risk level
        risk_level = self._assess_risk(query, reason)

        # Select appropriate template
        template = self._select_template(reason, risk_level)

        # Apply constraints
        constraints = self._apply_constraints(template, risk_level)

        # Generate response
        response = self._render_response(template, query, reason)

        result = FallbackResult(
            response=response,
            is_fallback=True,
            risk_level=risk_level,
            policy_compliant=True,
            constraints_applied=constraints,
            metadata={
                "template_used": template,
                "fallback_reason": reason,
            },
        )

        _emit_records_telemetry_event(
            "fallback_generated",
            f"risk_{risk_level}",
        )

        log.debug(f"Generated fallback response (risk={risk_level})")
        return result

    def _load_templates(self) -> dict[str, str]:
        """Load fallback response templates."""
        return {
            "insufficient_support": (
                "I don't have sufficient information to provide a complete answer to your question. "
                "Please try rephrasing your query or provide more specific details."
            ),
            "no_relevant_docs": (
                "I couldn't find relevant documents to answer your question. "
                "The information you're looking for may not be in my knowledge base."
            ),
            "low_confidence": (
                "I'm not confident enough in the available information to provide a reliable answer. "
                "Would you like me to provide what I found with appropriate caveats?"
            ),
            "policy_restriction": (
                "I'm unable to provide an answer due to policy restrictions on this type of query. "
                "Please contact support for assistance."
            ),
            "system_error": (
                "I encountered an issue while processing your request. "
                "Please try again later or contact support if the problem persists."
            ),
        }

    def _assess_risk(self, query: str, reason: str) -> str:
        """Assess risk level for fallback."""
        # Simple risk assessment based on reason
        if "policy" in reason.lower():
            return "high"
        elif "insufficient" in reason.lower():
            return "low"
        elif "error" in reason.lower():
            return "medium"

        return "low"

    def _select_template(self, reason: str, risk_level: str) -> str:
        """Select appropriate template."""
        # Match reason to template
        for key, template in self._fallback_templates.items():
            if key in reason.lower():
                return template

        # Default template
        return self._fallback_templates.get("insufficient_support", "")

    def _apply_constraints(self, template: str, risk_level: str) -> list[str]:
        """Apply constraints based on risk level."""
        constraints = []

        if risk_level == "high":
            constraints.append("No specific information disclosed")
            constraints.append("General response only")
        elif risk_level == "medium":
            constraints.append("Caveats included")
        else:
            constraints.append("Helpful but bounded")

        return constraints

    def _render_response(self, template: str, query: str, reason: str) -> str:
        """Render final response."""
        # Simple template rendering
        return template


# Global instance
_global_fallback: LowRiskFallback | None = None


def get_low_risk_fallback() -> LowRiskFallback:
    """Get or create the global fallback generator."""
    global _global_fallback
    if _global_fallback is None:
        _global_fallback = LowRiskFallback()
    return _global_fallback
