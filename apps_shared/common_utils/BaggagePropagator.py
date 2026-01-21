"""
baggage_propagator.py - Context Propagator Module

Domain: tracing
Generated: 2025-12-07T12:07:59.853999
"""

import logging

logger = logging.getLogger(__name__)


class BaggagePropagator:
    """Context propagator for tracing domain."""

    HEADER_TRACE_ID = "X-Trace-ID"
    HEADER_SPAN_ID = "X-Span-ID"
    HEADER_SAMPLED = "X-Sampled"

    def __init__(self, config: dict[str, object] | None = None):
        self.config = config or {}
        logger.info(f"Initialized {self.__class__.__name__}")

    def inject(self, context: dict[str, object], carrier: dict[str, str]) -> None:
        """Inject context into carrier."""
        if "trace_id" in context:
            carrier[self.HEADER_TRACE_ID] = context["trace_id"]
        if "span_id" in context:
            carrier[self.HEADER_SPAN_ID] = context["span_id"]
        if "sampled" in context:
            carrier[self.HEADER_SAMPLED] = "1" if context["sampled"] else "0"

    def extract(self, carrier: dict[str, str]) -> dict[str, object]:
        """Extract context from carrier."""
        context = {}

        if self.HEADER_TRACE_ID in carrier:
            context["trace_id"] = carrier[self.HEADER_TRACE_ID]
        if self.HEADER_SPAN_ID in carrier:
            context["span_id"] = carrier[self.HEADER_SPAN_ID]
        if self.HEADER_SAMPLED in carrier:
            context["sampled"] = carrier[self.HEADER_SAMPLED] == "1"

        return context


def inject_context(
    context: dict[str, object], carrier: dict[str, str], config: dict | None = None
) -> None:
    """Inject context into carrier."""
    BaggagePropagator(config).inject(context, carrier)


def extract_context(carrier: dict[str, str], config: dict | None = None) -> dict[str, object]:
    """Extract context from carrier."""
    return BaggagePropagator(config).extract(carrier)
