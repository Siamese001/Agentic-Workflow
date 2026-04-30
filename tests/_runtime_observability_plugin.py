"""Pytest plugin: capture OTel spans and ingest into the runtime ADG store.

W2 P2.1 of plan ``adg-three-bucket-unified-c4f8e2``.

Activation: tests decorated with ``@pytest.mark.runtime_observability`` get an
OTel ``TracerProvider`` backed by ``InMemorySpanExporter`` for the duration of
the test. On teardown, finished spans are converted to the runtime-ADG dict
shape and ingested via :func:`emit_spans_to_runtime_adg`, populating
``v_runtime_proof`` rows downstream.

Unmarked tests are unaffected — the fixture is autouse but no-ops when the
marker is absent. Best-effort by design: any failure in the OTel stack or
the ingest path is logged and swallowed; an observability harness must not
take down the tests it instruments.

Registered as a pytest plugin via ``tests/conftest.py``:
    pytest_plugins = ("tests._runtime_observability_plugin",)
"""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Any

import pytest

# This plugin produces runtime-ADG snapshots; it does not consume ADG views.
__adg_consumer_mode__ = "inventory"

# Plan: adg-three-bucket-unified-c4f8e2 (W2 P2.1). This is a producer-side
# observability harness; GenAI semconv attributes do not apply.
__non_genai_emitter__ = "pytest runtime-observability harness — span capture, not span producer"

if TYPE_CHECKING:
    from opentelemetry.sdk.trace import ReadableSpan

logger = logging.getLogger(__name__)


def _readable_span_to_dict(span: "ReadableSpan") -> dict[str, Any]:
    """Convert an OTel ``ReadableSpan`` to the runtime-ADG materializer shape.

    Required materializer fields per ``system_learning/runtime_adg/materializer.py``:
    ``span_id`` (non-empty str). Optional but consumed: ``name``, ``kind``,
    ``layer``, ``component``, ``ts_utc`` (int), ``duration_ms`` (float),
    ``status`` (``"ok"`` | ``"error"``), ``attributes`` (dict),
    ``parent_span_id``.
    """
    ctx = span.get_span_context()
    parent = span.parent

    end_ns = span.end_time or 0
    start_ns = span.start_time or 0
    duration_ms = (end_ns - start_ns) / 1e6 if (end_ns and start_ns) else 0.0

    attrs: dict[str, Any] = dict(span.attributes or {})
    component = (
        attrs.get("component")
        or attrs.get("service.name")
        or "pytest"
    )
    layer = str(attrs.get("layer", ""))[:8]  # L0..L6 format

    kind_raw = getattr(span, "kind", None)
    kind = kind_raw.name.lower() if kind_raw is not None and hasattr(kind_raw, "name") else "unknown"

    status_obj = getattr(span, "status", None)
    status = "ok"
    if status_obj is not None:
        code = getattr(status_obj, "status_code", None)
        if code is not None and getattr(code, "name", "").upper() == "ERROR":
            status = "error"

    return {
        "span_id": format(ctx.span_id, "016x") if ctx else "",
        "trace_id": format(ctx.trace_id, "032x") if ctx else "",
        "parent_span_id": format(parent.span_id, "016x") if parent else "",
        "name": (span.name or "")[:256],
        "kind": kind,
        "layer": layer,
        "component": str(component)[:128],
        "ts_utc": int(end_ns / 1e9) if end_ns else int(time.time()),
        "duration_ms": duration_ms,
        "status": status,
        "attributes": attrs,
    }


@pytest.fixture(autouse=True)
def runtime_observability_capture(request):
    """Autouse fixture — captures OTel spans only when the marker is present.

    For tests decorated with ``@pytest.mark.runtime_observability``, installs
    a fresh ``TracerProvider`` + ``InMemorySpanExporter``, yields the exporter
    (so tests may inspect spans directly), and on teardown ingests finished
    spans into the runtime ADG store.

    For unmarked tests this fixture is a no-op (yields None) — zero overhead.
    """
    marker = request.node.get_closest_marker("runtime_observability")
    if marker is None:
        yield None
        return

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import SimpleSpanProcessor
        from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
    except ImportError as exc:
        pytest.skip(f"opentelemetry SDK not installed: {exc}")
        return  # unreachable but keeps type checkers happy

    exporter = InMemorySpanExporter()
    processor = SimpleSpanProcessor(exporter)

    # Strategy: attach our exporter to the EXISTING global provider when it is
    # an SDK ``TracerProvider`` (so we observe spans from production code that
    # calls ``trace.get_tracer(__name__)``). When the global is the proxy
    # provider (no SDK installed yet), install a fresh SDK provider with our
    # processor — this is the first-test-of-the-process case.
    current_provider = trace.get_tracer_provider()
    installed_fresh = False
    attached_processor = False

    if isinstance(current_provider, TracerProvider):
        # Existing SDK provider — attach our processor as a passive observer.
        try:
            current_provider.add_span_processor(processor)
            attached_processor = True
            provider_for_teardown = current_provider
        except (RuntimeError, AttributeError) as exc:
            logger.warning("runtime_observability: add_span_processor failed: %s", exc)
            provider_for_teardown = current_provider
    else:
        # Proxy or unknown — install a fresh SDK provider.
        fresh = TracerProvider()
        fresh.add_span_processor(processor)
        try:
            trace.set_tracer_provider(fresh)
            installed_fresh = True
            provider_for_teardown = fresh
        except (RuntimeError, ValueError) as exc:
            logger.warning("runtime_observability: set_tracer_provider failed: %s", exc)
            provider_for_teardown = fresh

    try:
        yield exporter
    finally:
        # Best-effort drain. Any failure is logged and swallowed — observability
        # harness must not fail the test it instruments.
        try:
            provider_for_teardown.force_flush(timeout_millis=5000)
        except (RuntimeError, OSError, TimeoutError, AttributeError) as exc:
            logger.warning("runtime_observability: force_flush failed: %s", exc)

        spans = []
        try:
            spans = list(exporter.get_finished_spans())
        except (RuntimeError, AttributeError) as exc:
            logger.warning("runtime_observability: span drain failed: %s", exc)

        if spans:
            span_dicts = []
            for span in spans:
                try:
                    span_dicts.append(_readable_span_to_dict(span))
                except (AttributeError, ValueError, TypeError) as exc:
                    logger.warning("runtime_observability: span->dict failed: %s", exc)

            if span_dicts:
                try:
                    from agentic_core.L6_observability.otel_runtime_ingest import (
                        emit_spans_to_runtime_adg,
                    )
                except ImportError as exc:
                    logger.warning("runtime_observability: ingest import failed: %s", exc)
                else:
                    nodeid = request.node.nodeid
                    first_trace_id = span_dicts[0].get("trace_id") or None
                    try:
                        result = emit_spans_to_runtime_adg(
                            span_dicts,
                            mission=f"pytest::{nodeid}",
                            trace_id=first_trace_id,
                        )
                        logger.info(
                            "runtime_observability: ingested %d spans for %s -> %s",
                            len(span_dicts),
                            nodeid,
                            result.get("snapshot_id", "?"),
                        )
                    except (RuntimeError, OSError, ValueError) as exc:
                        logger.warning(
                            "runtime_observability: ingest call failed: %s", exc
                        )

        # Detach our processor when we attached to an existing provider; only
        # shut down the provider when we installed it fresh (we own its lifetime).
        if attached_processor:
            try:
                processor.shutdown()
            except (RuntimeError, OSError) as exc:
                logger.debug("runtime_observability: processor.shutdown failed: %s", exc)
        elif installed_fresh:
            try:
                provider_for_teardown.shutdown()
            except (RuntimeError, OSError) as exc:
                logger.debug("runtime_observability: provider.shutdown failed: %s", exc)


def pytest_configure(config):
    """Register the ``runtime_observability`` marker (defensive).

    pytest.ini already declares this marker, but the plugin registers it too
    so the fixture remains usable in environments where the ini is overridden.
    """
    config.addinivalue_line(
        "markers",
        "runtime_observability: capture OTel spans into runtime ADG store on test teardown (W2 P2.1)",
    )
