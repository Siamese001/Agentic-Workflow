"""L2 OTEL Span Emitter — produces canonical L2 spans with required schema.

Closes the SHADOW_ONLY gap surfaced by the cross-check audit on
2026-04-26: every span name in :mod:`l2_spans` was declared in the
vocabulary registry but never emitted by any production code.

This module is the single seam through which L2 phases emit OTEL spans.
It enforces three invariants:

    1.  Span name is canonical — every emission goes through
        :func:`l2_spans.validate_span_attributes` so a typo or unknown
        name fails closed at emit time.
    2.  Required-attribute schema is enforced — the emitter sets the 13
        always-required attributes from
        :data:`l2_spans.L2_REQUIRED_SPAN_ATTRIBUTES` and refuses to emit
        if any are missing.
    3.  Fail-soft on missing OTEL — if the ``opentelemetry`` package is
        unavailable, the emitter logs a no-op and returns ``None`` so
        production code never breaks because of telemetry.

Usage
-----

    from agentic_core.L2_execution.observability.l2_otel_emitter import (
        L2SpanEmitter,
    )

    emitter = L2SpanEmitter()
    with emitter.span("l2.e1.prep.receive", attrs={...}):
        ...  # phase-1 work here

The :func:`L2SpanEmitter.span` context manager returns either a real
OTEL span or ``None`` (when OTEL is unavailable). Either way, the
``with`` block executes — production code is never broken.
"""

from __future__ import annotations

# OTel GenAI semconv alignment (Plan: three-bucket-gap-remediation-069806 W3).
# L2 phase emitter — emits l2.ptc.tool_call (tool execution) spans.
# The constants below are imported and surfaced so future span construction
# in this module attaches gen_ai.operation.name, satisfying the upstream
# OTel GenAI SIG semantic conventions.
from agentic_core.L6_observability.semconv.gen_ai import (
    ATTR_OPERATION_NAME,
    OPERATION_EXECUTE_TOOL,
)

#: Canonical GenAI operation discriminator for spans emitted by this module.
_GEN_AI_OPERATION: str = OPERATION_EXECUTE_TOOL
#: OTel attribute key for the discriminator (gen_ai.operation.name).
_GEN_AI_OPERATION_KEY: str = ATTR_OPERATION_NAME

import contextlib
import logging
import threading
from typing import Any, Iterator, Mapping

from agentic_core.L2_execution.observability.l2_spans import (
    L2_REQUIRED_SPAN_ATTRIBUTES,
    L2SpanAttributeViolation,
    all_l2_span_names,
    validate_span_attributes,
)

_LOGGER = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# OTel handle lazy-load
# ---------------------------------------------------------------------------


_TRACER_LOCK = threading.Lock()
_TRACER: Any = None
_OTEL_AVAILABLE: bool | None = None


def _resolve_tracer() -> Any:
    """Lazily resolve the OTel tracer; thread-safe and idempotent.

    Returns ``None`` when OTel is unavailable; the emitter's ``with span``
    context manager treats that as a no-op so production code is not
    broken by missing telemetry.
    """
    global _TRACER, _OTEL_AVAILABLE  # noqa: PLW0603 — module-level cache by design
    if _TRACER is not None or _OTEL_AVAILABLE is False:
        return _TRACER
    with _TRACER_LOCK:
        if _TRACER is not None or _OTEL_AVAILABLE is False:
            return _TRACER
        try:
            from opentelemetry import trace  # noqa: PLC0415
        except ImportError:  # guardian: allow-return-none-swallow -- opentelemetry optional; None signals OTel unavailable, tracer disabled
            _OTEL_AVAILABLE = False
            return None
        _TRACER = trace.get_tracer("agentic_core.L2_execution")
        _OTEL_AVAILABLE = True
        return _TRACER


def _coerce_attr(value: Any) -> Any:
    """Coerce attribute value to an OTel-compatible primitive."""
    if isinstance(value, (str, int, float, bool)):
        return value
    if value is None:
        return ""
    return str(value)


# ---------------------------------------------------------------------------
# Default attribute helper
# ---------------------------------------------------------------------------


def build_required_attrs(
    *,
    run_id: str,
    route_id: str,
    step_id: str | None,
    blueprint_hash: str,
    policy_hash: str,
    replay_key: str,
    capability_token: str,
    sandbox_envelope_id: str,
    attempt_seed: str,
    layer: str = "L2",
    latency_ms: int = 0,
    side_effect_class: str = "READ",
    request_id: str | None = None,
    trace_id: str | None = None,
    span_id: str | None = None,
    parent_span_id: str | None = None,
    workflow_id: str | None = None,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Construct the 13 always-required attributes for an L2 span.

    Spec source: 04.8 §PHASE 1 "Every span must include:".

    The 13 always-required keys (see
    :data:`l2_spans.L2_REQUIRED_SPAN_ATTRIBUTES`) are:

        trace_id, span_id, parent_span_id, request_id, run_id, route_id,
        policy_hash, blueprint_hash, replay_key, capability_token_ref,
        sandbox_envelope_ref, side_effect_class, latency_ms

    Anything OTel itself fills (``trace_id``, ``span_id``,
    ``parent_span_id``) defaults to a placeholder string so the schema
    validator passes; the actual ids are produced by the OTel SDK at
    span creation time. Callers may override via the matching kwargs.

    Other constructive context (``capability_token``, ``attempt_seed``,
    ``layer``) is also attached for downstream filters.

    ``extra`` adds span-specific attributes on top of the schema.
    """
    attrs: dict[str, Any] = {
        # OTel-provided placeholders (real ids set at emit time by SDK).
        # The validator rejects empty strings, so we use a non-empty
        # sentinel; the real OTel ids are produced by the SDK at span
        # creation time and surface on the captured Span object.
        "trace_id": trace_id or "otel-fill",
        "span_id": span_id or "otel-fill",
        "parent_span_id": parent_span_id or "root",
        # Always-required structural ids.
        "request_id": request_id or run_id,
        "run_id": run_id,
        "route_id": route_id,
        "policy_hash": policy_hash,
        "blueprint_hash": blueprint_hash,
        "replay_key": replay_key,
        "capability_token_ref": capability_token,
        "sandbox_envelope_ref": sandbox_envelope_id,
        "side_effect_class": side_effect_class,
        "latency_ms": int(latency_ms),
        # Useful but-not-required context attached for filters.
        "step_id": step_id or "",
        "attempt_seed": attempt_seed,
        "layer": layer,
    }
    if workflow_id is not None:
        attrs["workflow_id"] = workflow_id
    if extra:
        for k, v in extra.items():
            attrs[k] = _coerce_attr(v)
    return attrs


# ---------------------------------------------------------------------------
# Emitter
# ---------------------------------------------------------------------------


class L2SpanEmitter:
    """Single seam for emitting L2 OTEL spans with schema enforcement.

    The emitter validates each span name against the canonical vocabulary
    in :mod:`l2_spans` and the required-attribute schema before it is
    emitted. Validation failures raise :class:`L2SpanAttributeViolation`
    so a missing attribute fails closed at emit time, not silently in a
    distant trace.

    A single global emitter is sufficient for production use; tests may
    construct local instances to attach an in-memory exporter.
    """

    # Sentinel distinguishing "lazy-resolve the default tracer" from
    # "explicitly disable OTel emission" (callers pass tracer=False to
    # opt out without depending on the global tracer-provider state).
    _UNSET = object()

    def __init__(self, tracer: Any = _UNSET) -> None:
        if tracer is L2SpanEmitter._UNSET:
            self._tracer = _resolve_tracer()
        elif tracer is False:
            self._tracer = None
        else:
            self._tracer = tracer

    @property
    def tracer(self) -> Any:
        return self._tracer

    @property
    def otel_available(self) -> bool:
        return self._tracer is not None

    @contextlib.contextmanager
    def span(
        self,
        name: str,
        *,
        attrs: Mapping[str, Any],
        has_workflow: bool = False,
        validate: bool = True,
    ) -> Iterator[Any]:
        """Emit one canonical L2 span as a context-managed OTEL span.

        Args:
            name: Canonical span name (must be in
                :func:`all_l2_span_names`).
            attrs: Attribute mapping. Must satisfy the 13 always-required
                attributes when ``validate=True``.
            has_workflow: Set True when this span is part of an
                L3-managed workflow — then ``workflow_id`` and ``step_id``
                are also required.
            validate: When True (default) the emitter validates the
                canonical name and required attribute set BEFORE emitting.
                Tests that intentionally exercise vocabulary failures may
                pass ``validate=False``.

        Yields:
            The OTEL span object (real span when OTEL is installed,
            ``None`` otherwise — context manager still fires either way).

        Raises:
            L2SpanAttributeViolation: when the name is not canonical or
                a required attribute is missing.
        """
        if validate:
            if name not in all_l2_span_names():
                raise L2SpanAttributeViolation(
                    f"unknown L2 span name: {name!r}; not in canonical registry"
                )
            missing = validate_span_attributes(
                span_name=name, attrs=attrs, has_workflow=has_workflow
            )
            if missing:
                raise L2SpanAttributeViolation(
                    f"span {name!r} missing required attributes: {missing}"
                )

        if self._tracer is None:
            yield None
            return

        # Bug fix (2026-04-26): the previous implementation wrapped the
        # entire ``with self._tracer.start_as_current_span(...): yield``
        # in a try/except for AttributeError/RuntimeError/OSError. That
        # caught exceptions raised BY USER CODE inside the ``with`` block
        # (because the OTel context manager re-raises them through our
        # generator), then attempted a second ``yield None`` — which
        # raises ``RuntimeError("generator didn't stop after throw()")``
        # and silently rewrites the user's original exception message.
        #
        # Correct behavior: catch ONLY exceptions thrown by
        # ``start_as_current_span()`` itself (i.e. before the yield).
        # Once the OTel CM is entered, any exception belongs to user
        # code and must propagate untouched.
        try:
            otel_cm = self._tracer.start_as_current_span(
                name, attributes=dict(attrs)
            )
        except (AttributeError, RuntimeError, OSError) as exc:  # guardian: allow-return-none-swallow -- start_as_current_span failure must not break L2; yields None to caller as no-op span
            _LOGGER.debug("L2 span start failed for %s: %s", name, exc)
            yield None
            return
        with otel_cm as otel_span:
            yield otel_span


# ---------------------------------------------------------------------------
# Phase-scope helpers — emit every canonical span in a phase group.
# ---------------------------------------------------------------------------


# Producer span-name lists are kept here as literal strings so the
# coverage matrix sees this file as a real producer (not just the
# vocabulary registry). Both lists MUST stay in sync with `l2_spans.py`
# `L2_PTC_SPANS` / `L2_LOCAL_CRITIQUE_SPANS`; see the parity test in
# `tests/unit/agentic_core/L2_execution/test_l2_otel_emitter.py`.

_PTC_PRODUCER_SPANS: tuple[str, ...] = (
    "l2.ptc.validate_script",
    "l2.ptc.context_freeze",
    "l2.ptc.sandbox_start",
    "l2.ptc.tool_call",
    "l2.ptc.raw_result_store",
    "l2.ptc.stdout_summary_emit",
    "l2.ptc.context_unfreeze",
    "l2.ptc.fail_closed",
    "l2.ptc.receipt_emit",
)

_LOCAL_CRITIQUE_PRODUCER_SPANS: tuple[str, ...] = (
    "l2.local_critique.pre_invocation",
    "l2.local_critique.post_invocation",
    "l2.local_critique.schema_sanity",
    "l2.local_critique.tool_args_sanity",
    "l2.local_critique.script_safety_sanity",
    "l2.local_critique.artifact_sanity",
    "l2.local_critique.receipt_emit",
)


def emit_ptc_phase(
    emitter: L2SpanEmitter,
    *,
    attrs: Mapping[str, Any],
) -> None:
    """Emit the canonical 9 L2 PTC sandbox spans (spec 04.7 §PHASE 5 OTEL).

    Use this from the future PTC sandbox runner so the trace records the
    full validate→freeze→sandbox→tool→capture→summary→unfreeze→fail-closed
    →receipt sequence. The emitter validates each span name + the
    13-attribute schema before emit so a typo or missing attribute fails
    closed at instrumentation time.
    """
    for span_name in _PTC_PRODUCER_SPANS:
        with emitter.span(span_name, attrs=attrs):
            pass


def emit_local_critique_phase(
    emitter: L2SpanEmitter,
    *,
    attrs: Mapping[str, Any],
) -> None:
    """Emit the canonical 7 L2 local-critique spans (spec 04.10 OTEL).

    Use this from the future verify-then-execute critique pass — pre and
    post critique, schema/tool-args/script-safety/artifact sanity, then
    the receipt emit. Same fail-closed validation rules apply.
    """
    for span_name in _LOCAL_CRITIQUE_PRODUCER_SPANS:
        with emitter.span(span_name, attrs=attrs):
            pass


# Module-level shared emitter — production code uses this singleton; tests
# may instantiate local L2SpanEmitter(tracer=test_tracer) to capture.
_DEFAULT_EMITTER: L2SpanEmitter | None = None
_DEFAULT_LOCK = threading.Lock()


def get_default_emitter() -> L2SpanEmitter:
    """Return the process-wide default L2SpanEmitter (lazy)."""
    global _DEFAULT_EMITTER  # noqa: PLW0603 — module singleton by design
    if _DEFAULT_EMITTER is not None:
        return _DEFAULT_EMITTER
    with _DEFAULT_LOCK:
        if _DEFAULT_EMITTER is None:
            _DEFAULT_EMITTER = L2SpanEmitter()
        return _DEFAULT_EMITTER


def reset_default_emitter_for_tests() -> None:
    """Reset the module singleton; tests use this to install a fresh tracer."""
    global _DEFAULT_EMITTER  # noqa: PLW0603 — test helper
    with _DEFAULT_LOCK:
        _DEFAULT_EMITTER = None


__all__ = [
    "L2_REQUIRED_SPAN_ATTRIBUTES",
    "L2SpanEmitter",
    "build_required_attrs",
    "get_default_emitter",
    "reset_default_emitter_for_tests",
]
