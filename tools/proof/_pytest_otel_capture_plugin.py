"""Pytest plugin that captures OTel spans during a test session.

Installed implicitly by `tools.proof.otel_collector_proof.run_test_file_proof`
via ``-p tools.proof._pytest_otel_capture_plugin``.

Behavior
--------

1. At session start: install a fresh ``TracerProvider`` with an
   ``InMemorySpanExporter`` and set it as the global tracer provider.
2. Per-test: snapshot exporter state before each test, snapshot again
   after, attribute the delta (new spans) to the test's ``nodeid``.
3. At session finish: dump JSON in one of two shapes based on
   ``OTEL_PROOF_OUTPUT_MODE`` env var:
     - ``aggregate`` (default): single flat list of all captured spans
       (the original W1 contract — preserved for run_test_file_proof)
     - ``per_test``: dict mapping ``nodeid`` -> list of spans
       captured during that test (used by the W3 bulk-sweep tool to
       run pytest ONCE on all 198 test files and read back per-REQ
       attribution).

Anti-cheat
----------

The plugin does NOT inject test-only spans. It only captures what
production code actually emitted. Zero spans means zero spans —
the harness reads back an empty array and reports
``status=NO_SPANS_EMITTED``.

Fail-soft
---------

If ``opentelemetry`` is unavailable, the plugin no-ops. If
``OTEL_PROOF_OUTPUT`` is unset, the plugin runs the capture but
skips the dump.
"""

from __future__ import annotations

import json
import os
from typing import Any


_PROVIDER = None
_EXPORTER = None
_PROCESSOR = None
# nodeid -> list of span dicts captured during that test
_PER_TEST_SPANS: dict[str, list[dict[str, Any]]] = {}
# Snapshot count of finished spans before each test starts
_PRE_TEST_SPAN_COUNT: int = 0


def _serialize_span(s) -> dict[str, Any]:
    """Convert a ReadableSpan -> JSON-safe dict."""
    attrs: dict[str, Any] = {}
    try:
        attrs = dict(s.attributes or {})
    except Exception:  # noqa: BLE001
        attrs = {}
    try:
        status_code = s.status.status_code.name if s.status else ""
    except AttributeError:
        status_code = ""
    try:
        kind = s.kind.name if s.kind else ""
    except AttributeError:
        kind = ""
    return {
        "name": s.name,
        "attributes": attrs,
        "status": status_code,
        "kind": kind,
    }


def pytest_configure(config) -> None:  # noqa: D401 — pytest hook signature
    """Install the in-memory tracer at session start."""
    global _PROVIDER, _EXPORTER, _PROCESSOR
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import SimpleSpanProcessor
        from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
            InMemorySpanExporter,
        )
    except ImportError:
        return  # OTel unavailable — plugin no-ops

    current = trace.get_tracer_provider()
    if isinstance(current, TracerProvider):
        _PROVIDER = current
    else:
        _PROVIDER = TracerProvider()
        trace.set_tracer_provider(_PROVIDER)
    _EXPORTER = InMemorySpanExporter()
    _PROCESSOR = SimpleSpanProcessor(_EXPORTER)
    _PROVIDER.add_span_processor(_PROCESSOR)


def pytest_runtest_setup(item) -> None:  # noqa: ARG001 — pytest hook signature
    """Snapshot finished-span count BEFORE each test."""
    global _PRE_TEST_SPAN_COUNT
    if _EXPORTER is None or _PROCESSOR is None:
        return
    try:
        # Force-flush + clear is too aggressive (would lose cross-test
        # state if any plugin uses it). Just record current count.
        _PROCESSOR.force_flush(timeout_millis=500)
    except Exception:  # noqa: BLE001
        pass
    try:
        _PRE_TEST_SPAN_COUNT = len(_EXPORTER.get_finished_spans())
    except Exception:  # noqa: BLE001
        _PRE_TEST_SPAN_COUNT = 0


def pytest_runtest_teardown(item, nextitem) -> None:  # noqa: ARG001
    """Attribute (post-pre) delta to this test's nodeid."""
    if _EXPORTER is None or _PROCESSOR is None:
        return
    try:
        _PROCESSOR.force_flush(timeout_millis=500)
    except Exception:  # noqa: BLE001
        pass
    try:
        all_spans = list(_EXPORTER.get_finished_spans())
        new_spans = all_spans[_PRE_TEST_SPAN_COUNT:]
        if new_spans:
            _PER_TEST_SPANS[item.nodeid] = [_serialize_span(s) for s in new_spans]
        else:
            _PER_TEST_SPANS[item.nodeid] = []
    except Exception:  # noqa: BLE001
        _PER_TEST_SPANS[item.nodeid] = []


def pytest_sessionfinish(session, exitstatus) -> None:  # noqa: D401, ARG001
    """Dump captured spans to OTEL_PROOF_OUTPUT path."""
    out_path = os.environ.get("OTEL_PROOF_OUTPUT")
    if not out_path:
        return
    mode = os.environ.get("OTEL_PROOF_OUTPUT_MODE", "aggregate").lower()
    if _EXPORTER is None or _PROCESSOR is None:
        # OTel was unavailable. Write empty payload of correct shape so
        # harness can distinguish "no spans emitted" from "harness failed
        # to set up".
        try:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump({} if mode == "per_test" else [], f)
        except OSError:
            pass
        return
    try:
        _PROCESSOR.force_flush(timeout_millis=2000)
    except Exception:  # noqa: BLE001
        pass

    if mode == "per_test":
        try:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(_PER_TEST_SPANS, f, default=str)
        except OSError:
            pass
        return

    # default aggregate mode
    captured = []
    try:
        for s in _EXPORTER.get_finished_spans():
            captured.append(_serialize_span(s))
    except Exception as exc:  # noqa: BLE001
        captured = [{"name": "__plugin_error__", "attributes": {"error": str(exc)}, "status": "ERROR", "kind": ""}]
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(captured, f, default=str)
    except OSError:
        pass
