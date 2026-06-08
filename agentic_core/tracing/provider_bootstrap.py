"""Generic, env-gated OpenTelemetry ``TracerProvider`` bootstrap for agentic_core.

Installs a *recording* SDK ``TracerProvider`` + span exporter **once per process**,
but only when the operator opts in via the standard OTEL environment variables.
Default is a clean no-op, so product runs carry zero telemetry overhead unless
explicitly enabled.

Why this exists
---------------
The hot-path span emitters (``L2_execution.observability.l2_otel_emitter``,
``L3_orchestration.exit_eval.otel_sdk_sink``, and the apps_rg spine
``runtime.spine.spine_span_emit``) only ever call ``trace.get_tracer(...)`` —
none of them installs a provider. Without a provider installed first, those
calls bind to OpenTelemetry's default ``ProxyTracerProvider``, which produces
non-recording, no-op spans that are silently dropped. ``l2_otel_emitter`` then
caches that no-op tracer for the lifetime of the process.

This module is the single, generic seam that fixes that: call
``ensure_tracer_provider_from_env()`` once, early on the shared run path
(``run_integrated_single_action_spine``), before any emitter resolves its
tracer. It is generic infrastructure — it works for every app and contains no
app-specific literals; per-app identity flows only through ``OTEL_SERVICE_NAME``.

Activation (opt-in — default OFF)
---------------------------------
::

    OTEL_TRACES_EXPORTER        = otlp | console      # unset/empty => disabled
    OTEL_EXPORTER_OTLP_PROTOCOL = http | http/protobuf | http/json | grpc
    OTEL_EXPORTER_OTLP_ENDPOINT = http://localhost:4318
    OTEL_SERVICE_NAME           = <service>           # default "agentic_core"

The OTLP exporters read ``OTEL_EXPORTER_OTLP_ENDPOINT`` (and the traces-specific
override) from the environment themselves, matching standard OTEL semantics.

Contract
--------
``ensure_tracer_provider_from_env()`` is idempotent, env-gated, and **fail-soft**
— it never raises. It returns a short status string describing what happened
(useful for receipts and tests).
"""

from __future__ import annotations

import logging
import os
import threading

_LOGGER = logging.getLogger(__name__)

_BOOTSTRAP_LOCK = threading.Lock()
_BOOTSTRAPPED = False

#: Generic default service name. NOT an app literal — apps override via env.
_DEFAULT_SERVICE_NAME = "agentic_core"

#: ``OTEL_EXPORTER_OTLP_PROTOCOL`` values that select the HTTP exporter.
_HTTP_PROTOCOLS = frozenset({"http", "http/protobuf", "http/json"})

__all__ = ["ensure_tracer_provider_from_env", "otel_activation_status"]


def otel_activation_status() -> str:
    """Return the current opt-in state without installing anything.

    ``"enabled:<kind>"`` when ``OTEL_TRACES_EXPORTER`` is set, else ``"disabled"``.
    """
    kind = os.environ.get("OTEL_TRACES_EXPORTER", "").strip().lower()
    return f"enabled:{kind}" if kind else "disabled"


def ensure_tracer_provider_from_env() -> str:
    """Install a recording ``TracerProvider`` + exporter iff OTEL env opts in.

    Idempotent (once per process), env-gated (no-op when ``OTEL_TRACES_EXPORTER``
    is unset/empty), and fail-soft (never raises). Returns a status string:

    ``disabled_env_unset`` · ``already_bootstrapped`` · ``provider_already_installed``
    · ``sdk_unavailable`` · ``otlp_http_installed`` · ``otlp_grpc_installed``
    · ``console_installed`` · ``unknown_exporter:<kind>`` · ``bootstrap_failed:<ExcType>``.
    """
    global _BOOTSTRAPPED  # noqa: PLW0603 — once-per-process install guard by design

    exporter_kind = os.environ.get("OTEL_TRACES_EXPORTER", "").strip().lower()
    if not exporter_kind:
        return "disabled_env_unset"

    if _BOOTSTRAPPED:
        return "already_bootstrapped"

    with _BOOTSTRAP_LOCK:
        if _BOOTSTRAPPED:
            return "already_bootstrapped"
        try:
            return _install_provider(exporter_kind)
        except Exception as exc:  # guardian: allow-broad-exception -- telemetry bootstrap is best-effort; must never break the run path
            _LOGGER.warning("otel_provider_bootstrap_failed: %r", exc)
            return f"bootstrap_failed:{type(exc).__name__}"


def _install_provider(exporter_kind: str) -> str:
    """Construct + install the SDK provider. Caller holds ``_BOOTSTRAP_LOCK``."""
    global _BOOTSTRAPPED  # noqa: PLW0603

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import (
            BatchSpanProcessor,
            SimpleSpanProcessor,
        )
    except ImportError as exc:
        _LOGGER.warning("otel_sdk_unavailable: %r", exc)
        # Mark bootstrapped so we don't re-attempt an impossible import each call.
        _BOOTSTRAPPED = True
        return "sdk_unavailable"

    # If a real SDK provider is already installed (e.g. apps_shared.get_tracer()
    # ran first), do NOT call set_tracer_provider again — it is once-per-process
    # and OTEL ignores+warns on a second real provider. Treat as success.
    existing = trace.get_tracer_provider()
    if isinstance(existing, TracerProvider):
        _BOOTSTRAPPED = True
        _reset_emitter_caches()
        return "provider_already_installed"

    exporter, status = _build_exporter(exporter_kind)
    if exporter is None:
        # Unknown exporter kind: a provider with no processor would silently drop
        # spans, so report honestly and leave the default provider in place.
        return status

    service_name = os.environ.get("OTEL_SERVICE_NAME", "").strip() or _DEFAULT_SERVICE_NAME
    provider = TracerProvider(resource=Resource.create(_resource_attributes(service_name)))
    # Console export is synchronous (immediate, no queue left pending at exit);
    # OTLP is batched for throughput.
    processor = (
        SimpleSpanProcessor(exporter)
        if exporter_kind == "console"
        else BatchSpanProcessor(exporter)
    )
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    _BOOTSTRAPPED = True
    _reset_emitter_caches()
    return status


def _build_exporter(exporter_kind: str):
    """Return ``(exporter, status)`` for the env-selected exporter kind.

    Returns ``(None, "unknown_exporter:<kind>")`` for an unrecognised kind.
    Exporter import/construction errors propagate to the fail-soft outer guard.
    """
    if exporter_kind == "console":
        from opentelemetry.sdk.trace.export import ConsoleSpanExporter

        return ConsoleSpanExporter(), "console_installed"

    if exporter_kind == "otlp":
        protocol = os.environ.get("OTEL_EXPORTER_OTLP_PROTOCOL", "").strip().lower()
        if protocol in _HTTP_PROTOCOLS:
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
                OTLPSpanExporter,
            )

            # No explicit endpoint: the exporter reads OTEL_EXPORTER_OTLP_ENDPOINT
            # (and the traces override) from the environment per OTEL conventions.
            return OTLPSpanExporter(), "otlp_http_installed"

        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter as GrpcOTLPSpanExporter,
        )

        return GrpcOTLPSpanExporter(), "otlp_grpc_installed"

    return None, f"unknown_exporter:{exporter_kind}"


def _resource_attributes(service_name: str) -> dict[str, str]:
    """Build OTEL resource attributes (Anthropic-alignment, ADR-024)."""
    attrs: dict[str, str] = {
        "service.name": service_name,
        "service.version": os.environ.get("OTEL_SERVICE_VERSION", "").strip() or "unknown",
        "deployment.environment": os.environ.get("OTEL_DEPLOYMENT_ENVIRONMENT", "").strip()
        or "unknown",
    }
    for pair in os.environ.get("OTEL_RESOURCE_ATTRIBUTES", "").split(","):
        if "=" in pair:
            key, value = pair.split("=", 1)
            key, value = key.strip(), value.strip()
            if key and value:
                attrs[key] = value
    return attrs


def _reset_emitter_caches() -> None:
    """Best-effort: invalidate downstream tracer caches populated before bootstrap.

    The L2 emitter caches its tracer on first resolution; if that happened before
    this bootstrap, the cache holds a no-op proxy tracer. Clearing it lets the
    next resolution pick up the now-recording provider. Fail-soft: a missing or
    not-yet-present reset hook must never break the bootstrap.
    """
    try:
        from agentic_core.L2_execution.observability.l2_otel_emitter import (
            reset_l2_tracer_cache,
        )

        reset_l2_tracer_cache()
    except Exception as exc:  # guardian: allow-broad-exception -- cache reset is best-effort; downstream import/availability must not break bootstrap
        _LOGGER.debug("l2_tracer_cache_reset_skipped: %r", exc)


def _reset_for_tests() -> None:
    """Test-only: clear the once-per-process guard.

    Does NOT uninstall the OTEL global provider (``set_tracer_provider`` is
    once-per-process); after the first install, subsequent calls return
    ``provider_already_installed``.
    """
    global _BOOTSTRAPPED  # noqa: PLW0603
    with _BOOTSTRAP_LOCK:
        _BOOTSTRAPPED = False
