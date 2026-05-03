"""Real monotonic-clock OTEL-style stage timing.

Copied from `apps_rg/runtime/otel_trace.py` with the import swapped to
the generalized contract types in `apps_shared.spine_emission.contracts`.
No behavior change — same StageTracer API, same span shape, same seal
semantics. apps_rg's copy is preserved unchanged so the existing
certified baseline is never disturbed.

Plan: apps-e2e-spine-cert-wireup-e1c4d7 W1.3.
"""
from __future__ import annotations

import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Iterator

from apps_shared.spine_emission.contracts import OtelRuntimeTrace, OtelSpan


def _utc_iso(epoch: float) -> str:
    return datetime.fromtimestamp(epoch, tz=timezone.utc).isoformat().replace("+00:00", "Z")


class StageTracer:
    """Lightweight monotonic-clock stage tracer.

    Records real wall-clock spans (start, finish, duration, status,
    attributes). Spans are never synthetic; `is_synthetic=False` for all
    emitted spans. Threaded with `run_id` / `request_id` / `trace_root`
    so the verifier can prove a single continuous run.
    """

    def __init__(self, app_name: str, run_id: str, request_id: str,
                 trace_root: str | None = None) -> None:
        self.app_name = app_name
        self.run_id = run_id
        self.request_id = request_id
        self.trace_root = trace_root or run_id
        self.trace_id = f"trace-{uuid.uuid4().hex[:24]}"
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
                finished_at_utc=started_at,
                duration_ms=0.0,
                attributes=attributes,
                status="OK",
                is_synthetic=False,
            )
        except Exception:  # guardian: allow-broad-exception -- span status set to ERROR before re-raise; does NOT swallow (explicit raise)
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
                app_name=self.app_name,
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
            app_name=self.app_name,
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


__all__ = ["StageTracer"]
