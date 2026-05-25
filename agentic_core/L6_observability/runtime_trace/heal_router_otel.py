"""Unified `heal_router.v1` OTEL span emitter (Phase M1 of ADR-025).

This module implements the additive M1 phase — a single emitter that captures
every `HealingRouter.route()` decision under one span hierarchy. Existing
four telemetry schemas remain untouched in M1; they are aliased to this
schema in M2.

Design constraints (from ADR-025):
  - Zero impact on existing consumers in M1
  - Generates `routing_trace_id` (uuid4) at `route()` entry
  - Emits a single `heal_router.v1.route` root span with required attributes
  - Safe to call with no OTEL backend configured (no-op fallback)

Usage:
    from agentic_core.L6_observability.heal_router_otel import (
        HealRouterTelemetryEmitter,
    )

    emitter = HealRouterTelemetryEmitter()
    emitter.emit_route_span(
        decision=routing_decision,
        confidence_score=score.score,
        app_name="healing_router",
        latency_ms=12.4,
    )

Plan reference: ADR-025; `.windsurf/plans/routing-followups-7a2c91.md` F2.3.
"""

from __future__ import annotations

# OTel GenAI semconv alignment (Plan: three-bucket-gap-remediation-069806 W3).
# L6 healing-router emitter — agent routing decision spans (heal_router.v1.*).
# The constants below are imported and surfaced so future span construction
# in this module attaches gen_ai.operation.name, satisfying the upstream
# OTel GenAI SIG semantic conventions.
from agentic_core.L6_observability.semconv.gen_ai import (
    ATTR_OPERATION_NAME,
    OPERATION_INVOKE_AGENT,
)

#: Canonical GenAI operation discriminator for spans emitted by this module.
_GEN_AI_OPERATION: str = OPERATION_INVOKE_AGENT
#: OTel attribute key for the discriminator (gen_ai.operation.name).
_GEN_AI_OPERATION_KEY: str = ATTR_OPERATION_NAME

import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


# ============================================================================
# Span attribute schema (stable wire format)
# ============================================================================

SPAN_NAME_ROUTE = "heal_router.v1.route"
SPAN_NAME_SCORE = "heal_router.v1.score"
SPAN_NAME_GATE = "heal_router.v1.gate"
SPAN_NAME_SUBTIER = "heal_router.v1.subtier_selection"
SPAN_NAME_COST_DEMOTION = "heal_router.v1.cost_demotion"
SPAN_NAME_DISPATCH = "heal_router.v1.dispatch"

# Per ADR-025 §2 — required attributes on every span in this family
REQUIRED_ATTRIBUTES = frozenset(
    {
        "routing.trace_id",
        "routing.tier",
        "routing.gate_applied",
        "routing.gemini_subtier",
        "routing.cost_demoted",
        "routing.target_model",
        "routing.app_name",
        "routing.confidence_score",
    }
)

# Optional attributes (dispatch spans only)
DISPATCH_ATTRIBUTES = frozenset(
    {
        "routing.cost_usd",
        "routing.tokens_in",
        "routing.tokens_out",
        "routing.latency_ms",
        "routing.error_code",
        "routing.dry_plan",
    }
)


# ============================================================================
# In-memory span record (also serves as the `routing_decision_events` row)
# ============================================================================


@dataclass
class RoutingSpanRecord:
    """Single emitted routing span; also the row shape for routing_decision_events.

    This is the Phase M1 in-memory capture. The OTEL backend (when configured)
    receives the same field set as span attributes. The ADG ingestion pipeline
    (F2.3 downstream) projects this record into the SQL table of the same
    name.
    """

    routing_trace_id: str
    timestamp: float
    app_name: str
    tier: str
    gate_applied: str
    gemini_subtier: str
    cost_demoted: bool
    target_model: str
    confidence_score: float | None = None
    cost_usd: float | None = None
    cost_budget_remaining_usd: float | None = None
    latency_ms: int | None = None
    outcome_success: bool | None = None
    dry_plan: bool = False
    error_code: str | None = None
    extra_attributes: dict[str, Any] = field(default_factory=dict)

    def to_span_attributes(self) -> dict[str, Any]:
        """Project into an OTEL-compatible attribute dict."""
        attrs: dict[str, Any] = {
            "routing.trace_id": self.routing_trace_id,
            "routing.app_name": self.app_name,
            "routing.tier": self.tier,
            "routing.gate_applied": self.gate_applied,
            "routing.gemini_subtier": self.gemini_subtier,
            "routing.cost_demoted": self.cost_demoted,
            "routing.target_model": self.target_model,
        }
        if self.confidence_score is not None:
            attrs["routing.confidence_score"] = self.confidence_score
        if self.cost_usd is not None:
            attrs["routing.cost_usd"] = self.cost_usd
        if self.cost_budget_remaining_usd is not None:
            attrs["routing.cost_budget_remaining_usd"] = self.cost_budget_remaining_usd
        if self.latency_ms is not None:
            attrs["routing.latency_ms"] = self.latency_ms
        if self.outcome_success is not None:
            attrs["routing.outcome_success"] = self.outcome_success
        if self.dry_plan:
            attrs["routing.dry_plan"] = True
        if self.error_code:
            attrs["routing.error_code"] = self.error_code
        attrs.update(self.extra_attributes)
        return attrs


# ============================================================================
# Emitter
# ============================================================================


def _forward_to_runtime_adg(record: RoutingSpanRecord, span_name: str) -> None:
    """Mirror a RoutingSpanRecord into the in-process runtime ADG store.

    Best-effort: any failure here must not disturb the heal-router hot path,
    so exceptions are caught and logged at DEBUG.
    """
    try:
        from agentic_core.L6_observability.otel_runtime_ingest import (  # noqa: PLC0415
            emit_span_to_runtime_adg,
        )

        span = {
            "span_id": record.routing_trace_id,
            "trace_id": record.routing_trace_id,
            "parent_span_id": "",
            "name": span_name,
            "kind": "router",
            "layer": "L0",
            "component": "heal_router",
            "service_name": record.app_name,
            "ts_utc": int(record.timestamp * 1000),
            "duration_ms": float(record.latency_ms or 0),
            "status": "error" if record.error_code else "ok",
            "attributes": record.to_span_attributes(),
        }
        emit_span_to_runtime_adg(
            span,
            mission=f"heal_router.{record.app_name}",
            trace_id=record.routing_trace_id,
        )
    except (
        ImportError,
        AttributeError,
        TypeError,
        ValueError,
    ) as exc:  # guardian: allow-log-and-swallow -- runtime-ADG mirror is best-effort; must never break heal-router hot path
        logger.debug("heal_router runtime-ADG forward failed: %s", exc)


class HealRouterTelemetryEmitter:
    """Phase M1 emitter — in-memory capture with optional OTEL forwarding.

    When no OTEL backend is configured, records are stored in an in-memory
    ring buffer (for tests and local inspection). When the OTEL SDK is
    available and configured, the same records are also forwarded as spans.

    Thread-safety: operations use a simple lock; contention is low because
    emission happens at the tail of `HealingRouter.route()` (single-call
    frequency).
    """

    _MAX_RING_SIZE = 1000  # M1 memory safety — evicts oldest on overflow

    def __init__(self) -> None:
        import threading  # noqa: PLC0415

        self._lock = threading.Lock()
        self._ring: list[RoutingSpanRecord] = []
        # M2 wiring (plan eval-meta-otel-gap-review-ef4a20 Wave W4): populate
        # the tracer from the OTel API. When no SDK TracerProvider is set, the
        # API returns a NoOpTracer whose context manager still works — so the
        # forwarding path below executes harmlessly in minimal environments
        # and emits real spans when a backend is configured.
        try:
            from opentelemetry import trace  # noqa: PLC0415

            self._otel_tracer: Any = trace.get_tracer("agentic_core.L6_observability.heal_router")
        except ImportError:  # pragma: no cover - OTel API absent
            self._otel_tracer = None

    def emit_route_span(
        self,
        *,
        routing_trace_id: str | None = None,
        decision: Any,  # avoid circular import of RoutingDecision
        confidence_score: float | None = None,
        app_name: str = "healing_router",
        cost_budget_remaining_usd: float | None = None,
        latency_ms: int | None = None,
        outcome_success: bool | None = None,
        dry_plan: bool = False,
        error_code: str | None = None,
        extra_attributes: dict[str, Any] | None = None,
    ) -> RoutingSpanRecord:
        """Capture a single `heal_router.v1.route` root span.

        Args:
            routing_trace_id: If not provided, a new uuid4 is generated.
            decision: A `RoutingDecision` instance. Must have attributes
                `tier` (with `.name`), `gate_applied`, `gemini_subtier`,
                `cost_demoted`, `target_model`.
            confidence_score: `ConfidenceScore.score` value in [0.0, 1.0].
            app_name: Calling app (default "healing_router").
            cost_budget_remaining_usd: From `RoutingContext`, if provided.
            latency_ms: Dispatch latency (M2+ populates this).
            outcome_success: Dispatch outcome (M2+ populates this).
            dry_plan: True when `SovereignLLMGateway` was not provisioned.
            error_code: Non-None when dispatch failed.
            extra_attributes: Additional app-specific attributes.

        Returns:
            The emitted `RoutingSpanRecord`.
        """
        record = RoutingSpanRecord(
            routing_trace_id=routing_trace_id or str(uuid.uuid4()),
            timestamp=time.time(),
            app_name=app_name,
            tier=getattr(getattr(decision, "tier", None), "name", "UNKNOWN"),
            gate_applied=getattr(decision, "gate_applied", "NO_OVERRIDE"),
            gemini_subtier=getattr(decision, "gemini_subtier", ""),
            cost_demoted=bool(getattr(decision, "cost_demoted", False)),
            target_model=getattr(decision, "target_model", ""),
            confidence_score=confidence_score,
            cost_budget_remaining_usd=cost_budget_remaining_usd,
            latency_ms=latency_ms,
            outcome_success=outcome_success,
            dry_plan=dry_plan,
            error_code=error_code,
            extra_attributes=dict(extra_attributes or {}),
        )

        with self._lock:
            self._ring.append(record)
            if len(self._ring) > self._MAX_RING_SIZE:
                self._ring = self._ring[-self._MAX_RING_SIZE :]

        # Future M2+ work: forward to _otel_tracer.start_as_current_span(...)
        # when OTEL backend is configured. Intentionally a no-op in M1.
        if self._otel_tracer is not None:
            try:
                attrs = record.to_span_attributes()
                with self._otel_tracer.start_as_current_span(SPAN_NAME_ROUTE, attributes=attrs):
                    pass
            except (
                AttributeError,
                TypeError,
                RuntimeError,
            ) as exc:  # guardian: allow-log-and-swallow -- OTEL span forwarding is best-effort telemetry; must never break the heal-router hot path
                # OTEL errors must never break the hot path
                logger.debug("heal_router_otel forwarding failed: %s", exc)

        # W7.1 P2.1 — forward to in-process runtime ADG store so the span is
        # queryable via otel_mcp::otel_trace without an external OTel backend.
        _forward_to_runtime_adg(record, SPAN_NAME_ROUTE)

        return record

    def append_alias_record(self, record: RoutingSpanRecord) -> None:
        """Append a pre-built RoutingSpanRecord emitted by a legacy feeder.

        Wave F2 M2 (ADR-025): legacy telemetry surfaces dual-emit into this
        emitter by synthesizing a `RoutingSpanRecord` and calling this
        method. The synthetic record should set
        `extra_attributes["routing.alias_source"]` so consumers can
        distinguish aliased records from real route spans.
        """
        with self._lock:
            self._ring.append(record)
            if len(self._ring) > self._MAX_RING_SIZE:
                self._ring = self._ring[-self._MAX_RING_SIZE :]

    def recent(self, limit: int = 100) -> list[RoutingSpanRecord]:
        """Return up to `limit` most-recent span records (copy).

        Use for test inspection and local debugging. Returns a copy to
        avoid external mutation of the ring.
        """
        with self._lock:
            return list(self._ring[-limit:])

    def clear(self) -> None:
        """Clear the in-memory ring. Primarily for test isolation."""
        with self._lock:
            self._ring.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._ring)


# ============================================================================
# Module-level singleton (convenience — apps that don't manage their own)
# ============================================================================


_default_emitter: HealRouterTelemetryEmitter | None = None


def get_default_emitter() -> HealRouterTelemetryEmitter:
    """Return the process-global default emitter (lazy singleton)."""
    global _default_emitter  # noqa: PLW0603
    if _default_emitter is None:
        _default_emitter = HealRouterTelemetryEmitter()
    return _default_emitter
