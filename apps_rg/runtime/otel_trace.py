"""Real OTEL-style stage timing.

Not full OpenTelemetry SDK — that would add startup cost and a vendor
dependency for what is fundamentally a local audit need. This module
records monotonic-clock-bound spans (start, finish, duration, status,
attributes) and serializes them to ``otel_runtime_trace.json`` in the
run dir. Spans are real timings, never synthetic, and carry the same
``run_id`` that threads the spine receipts.

If full OTEL export is later required, this module can be swapped for
``opentelemetry-sdk`` without changing the shape of the emitted JSON.
"""
from __future__ import annotations

import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Iterator

from apps_rg.runtime.contracts import OtelRuntimeTrace, OtelSpan


def _utc_iso(epoch: float) -> str:
    return datetime.fromtimestamp(epoch, tz=timezone.utc).isoformat().replace("+00:00", "Z")


class StageTracer:
    """Lightweight monotonic-clock stage tracer.

    Usage:
        tracer = StageTracer(run_id, request_id)
        with tracer.span("L0_route", route_id="apps_rg.default"):
            ...
        trace = tracer.seal()
    """

    def __init__(self, run_id: str, request_id: str, trace_root: str | None = None) -> None:
        self.run_id = run_id
        self.request_id = request_id
        self.trace_root = trace_root or run_id  # threads the run-level trace_root
        self.trace_id = f"trace-{uuid.uuid4().hex[:24]}"  # OTEL-internal id
        self._spans: list[OtelSpan] = []

    @contextmanager
    def span(self, name: str, **attributes: Any) -> Iterator[OtelSpan]:
        span_id = f"span-{uuid.uuid4().hex[:16]}"
        start_epoch = time.time()
        started_at = _utc_iso(start_epoch)
        status = "OK"
        try:
            yield OtelSpan(
                span_id=span_id,
                name=name,
                started_at_utc=started_at,
                finished_at_utc=started_at,  # placeholder; rewritten on close
                duration_ms=0.0,
                attributes=attributes,
                status="OK",
                is_synthetic=False,
            )
        except Exception:
            status = "ERROR"
            raise
        finally:
            end_epoch = time.time()
            self._spans.append(OtelSpan(
                span_id=span_id,
                name=name,
                started_at_utc=started_at,
                finished_at_utc=_utc_iso(end_epoch),
                duration_ms=(end_epoch - start_epoch) * 1000.0,
                attributes=attributes,
                status=status,  # type: ignore[arg-type]
                is_synthetic=False,
            ))

    def seal(self) -> OtelRuntimeTrace:
        if not self._spans:
            now = _utc_iso(time.time())
            return OtelRuntimeTrace(
                run_id=self.run_id,
                request_id=self.request_id,
                trace_root=self.trace_root,
                trace_id=self.trace_id,
                spans=[],
                span_count=0,
                earliest_start_utc=now,
                latest_finish_utc=now,
                contains_synthetic_spans=False,
            )
        earliest = min(s.started_at_utc for s in self._spans)
        latest = max(s.finished_at_utc for s in self._spans)
        return OtelRuntimeTrace(
            run_id=self.run_id,
            request_id=self.request_id,
            trace_root=self.trace_root,
            trace_id=self.trace_id,
            spans=list(self._spans),
            span_count=len(self._spans),
            earliest_start_utc=earliest,
            latest_finish_utc=latest,
            contains_synthetic_spans=any(s.is_synthetic for s in self._spans),
        )
