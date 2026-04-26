"""L2 Execution observability — OTEL spans, replay proof, telemetry shape.

Public surface:

  * :mod:`agentic_core.L2_execution.observability.l2_spans` — canonical
    span name registry + required attribute schema (doc 04.8).
"""

from agentic_core.L2_execution.observability.l2_spans import (
    L2_E1_SPANS,
    L2_E2_SPANS,
    L2_E3_SPANS,
    L2_E4_SPANS,
    L2_E5_SPANS,
    L2_PTC_SPANS,
    L2_REQUIRED_SPAN_ATTRIBUTES,
    L2SpanAttributeViolation,
    all_l2_span_names,
    validate_span_attributes,
)

__all__ = [
    "L2_E1_SPANS",
    "L2_E2_SPANS",
    "L2_E3_SPANS",
    "L2_E4_SPANS",
    "L2_E5_SPANS",
    "L2_PTC_SPANS",
    "L2_REQUIRED_SPAN_ATTRIBUTES",
    "L2SpanAttributeViolation",
    "all_l2_span_names",
    "validate_span_attributes",
]
