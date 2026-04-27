"""L5 v5 governance plane OTEL spans (G2 closure).

13 named spans covering the v5 governance plane lifecycle, modeled after
``agentic_core.L5_safety.runtime_gates.otel_spans``. Wired (lightly) into
``governance_plane.certify_packet`` and ``runtime_binding.emit_runtime_binding``
so trace evidence required by 00A.6 §14 (trace/span evidence) is satisfied.

OTEL is optional at import time — if the SDK is missing the context manager
becomes a no-op. The ``ALL_SPAN_NAMES`` constant is the public catalog used
by ``TraceCompletenessReport`` to validate span presence.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Iterator, Mapping

try:  # pragma: no cover — exercised only when OTEL SDK installed
    from opentelemetry import trace as _otel_trace  # type: ignore[import-not-found]

    _OTEL_AVAILABLE = True
except ImportError:  # pragma: no cover
    _otel_trace = None  # type: ignore[assignment]
    _OTEL_AVAILABLE = False


# --- Span name catalog (13 spans) ---------------------------------------------
SPAN_G0_VALIDATE = "l5.governance.g0_validate"
SPAN_G1_TRIAGE = "l5.governance.g1_triage"
SPAN_G2_AUTHORITY_RESOLVE = "l5.governance.g2_authority_resolve"
SPAN_G2A_ORIGIN_TRUST = "l5.governance.g2a_origin_trust"
SPAN_DECISION_RAIL_EMIT = "l5.governance.decision_rail.emit"
SPAN_REPLAY_AUDIT_SEAL = "l5.governance.replay_audit.seal"
SPAN_CERTIFY_PACKET = "l5.governance.certify_packet"
SPAN_BRIDGE = "l5.governance.bridge"
SPAN_RUNTIME_REGRESSION = "l5.governance.runtime_regression"
SPAN_OUT_OF_BAND_INVARIANT = "l5.governance.out_of_band_invariant"
SPAN_HITL_DISPOSITION = "l5.governance.hitl_disposition"
SPAN_RUNTIME_BINDING_EMIT = "l5.governance.runtime_binding.emit"
SPAN_SNAPSHOT_VERIFY = "l5.governance.snapshot_verify"

ALL_SPAN_NAMES: tuple[str, ...] = (
    SPAN_G0_VALIDATE,
    SPAN_G1_TRIAGE,
    SPAN_G2_AUTHORITY_RESOLVE,
    SPAN_G2A_ORIGIN_TRUST,
    SPAN_DECISION_RAIL_EMIT,
    SPAN_REPLAY_AUDIT_SEAL,
    SPAN_CERTIFY_PACKET,
    SPAN_BRIDGE,
    SPAN_RUNTIME_REGRESSION,
    SPAN_OUT_OF_BAND_INVARIANT,
    SPAN_HITL_DISPOSITION,
    SPAN_RUNTIME_BINDING_EMIT,
    SPAN_SNAPSHOT_VERIFY,
)


@dataclass
class RecordedSpan:
    """In-memory span record produced when OTEL SDK is unavailable.

    Used by tests to verify span emission without requiring a live exporter.
    """

    name: str
    attributes: dict[str, Any] = field(default_factory=dict)


# Module-level recorder for tests + offline verification. Not thread-safe; tests
# clear it between runs.
_RECORDED_SPANS: list[RecordedSpan] = []


def _clear_recorded_spans() -> None:
    """Test helper: drop all recorded spans."""
    _RECORDED_SPANS.clear()


def get_recorded_spans() -> tuple[RecordedSpan, ...]:
    """Return the immutable tuple of spans recorded since last clear."""
    return tuple(_RECORDED_SPANS)


@contextmanager
def emit_span(name: str, attributes: Mapping[str, Any] | None = None) -> Iterator[None]:
    """Emit an OTEL span if the SDK is available; always record locally.

    Falls back to a pure no-op recorder when ``opentelemetry`` is missing or
    when span construction raises (network exporter etc.).
    """

    attrs = dict(attributes or {})
    _RECORDED_SPANS.append(RecordedSpan(name=name, attributes=attrs))
    if _OTEL_AVAILABLE:
        try:  # pragma: no cover — exercised only when SDK is installed
            tracer = _otel_trace.get_tracer("l5.governance")
            with tracer.start_as_current_span(name, attributes=attrs):
                yield
                return
        except (RuntimeError, ValueError, TypeError):  # pragma: no cover
            yield
            return
    yield


def emit_event(name: str, attributes: Mapping[str, Any] | None = None) -> None:
    """Emit a one-shot span (no body)."""
    with emit_span(name, attributes):
        pass


__all__ = [
    "ALL_SPAN_NAMES",
    "RecordedSpan",
    "SPAN_BRIDGE",
    "SPAN_CERTIFY_PACKET",
    "SPAN_DECISION_RAIL_EMIT",
    "SPAN_G0_VALIDATE",
    "SPAN_G1_TRIAGE",
    "SPAN_G2A_ORIGIN_TRUST",
    "SPAN_G2_AUTHORITY_RESOLVE",
    "SPAN_HITL_DISPOSITION",
    "SPAN_OUT_OF_BAND_INVARIANT",
    "SPAN_REPLAY_AUDIT_SEAL",
    "SPAN_RUNTIME_BINDING_EMIT",
    "SPAN_RUNTIME_REGRESSION",
    "SPAN_SNAPSHOT_VERIFY",
    "_clear_recorded_spans",
    "emit_event",
    "emit_span",
    "get_recorded_spans",
]
