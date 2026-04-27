"""
W7 -- OTEL emitter adapter for live-runtime wire-up.

This module bridges the contract layer (otel_contract.RuntimeSpanRecorder
+ scenario harness, validated by Phases 5-7) and the live runtime layers
(L0_routing/, L1_cognition/, L2_execution/, L3_orchestration/, L4_state/,
L5_safety/, L6_observability/) WITHOUT modifying any layer's source.

Wiring procedure (per-layer Author-Gate required):

  1. The author-gate session for a layer (e.g. L5 exit-control) opens
     ``RuntimeSpanEmitter.for_request(request_id, run_id, ...)`` at the
     stage entry point.
  2. The session adds ``with emitter.span("exit.x3.disposition", ...):``
     around the existing decision logic.
  3. Required attributes (route_id, gate_id, status, reason_codes, ...)
     are populated from the layer's existing local variables.
  4. On stage exit, ``emitter.flush()`` writes the span batch to the
     active OTEL backend (real OpenTelemetry SDK if available; in-memory
     RuntimeSpanRecorder fallback otherwise -- guaranteed compatible
     with Phase 5 validation, Phase 6 replay, and Phase 7 anti-bypass).
  5. Coverage matrix flips affected records IMPLEMENTED_NOT_PROVEN ->
     IMPLEMENTED_AND_PROVEN once the live trace satisfies all four
     proof phases.

This module DOES NOT auto-instrument any code path. Per the user's
constitutional rules: no broad refactors, no renaming unrelated files,
no fabrication of proof. Live wiring is explicit, per-stage, gated.

Honest gap: this build delivers the adapter; W7+ Author-Gate sessions
deliver the actual ``with emitter.span(...)`` insertions.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Optional

from agentic_core.runtime.prove_requirements.otel_contract import (
    RUNTIME_SPAN_NAMES,
    RuntimeSpanRecorder,
    RuntimeTrace,
    write_trace,
)


# ---------------------------------------------------------------------------
# Backend abstraction
# ---------------------------------------------------------------------------

class _NullOtelBackend:
    """Used when the real OpenTelemetry SDK is not available or not
    configured. Records into RuntimeSpanRecorder which is byte-compatible
    with the harness traces validated by Phase 5/6/7."""

    def __init__(self, recorder: RuntimeSpanRecorder) -> None:
        self._recorder = recorder

    def emit_span(self, name: str, **attrs: Any):
        return self._recorder.span(name, **attrs)


def _try_real_otel_backend() -> Optional[Any]:
    """If OpenTelemetry is configured (env OTEL_EXPORTER_OTLP_ENDPOINT or
    similar), return a real backend. Otherwise return None and the caller
    falls back to the in-memory RuntimeSpanRecorder."""
    if not os.environ.get("OTEL_RUNTIME_PROVE_USE_SDK"):
        return None
    try:
        from opentelemetry import trace as _otel_trace  # type: ignore[import]  # noqa: F401, PLC0415
    except ImportError:
        return None
    # Real-SDK adapter is a future Author-Gate deliverable; for now we
    # honor the env var as a no-op signal that the SDK is available but
    # do NOT spin up a tracer here. Returning None keeps behavior in the
    # validated in-memory recorder path.
    return None


# ---------------------------------------------------------------------------
# Public emitter
# ---------------------------------------------------------------------------

class RuntimeSpanEmitter:
    """Plug-and-play emitter for live runtime layers.

    Usage in a future Author-Gate-approved L5 wire-up::

        from agentic_core.runtime.prove_requirements.otel_emitter import (
            RuntimeSpanEmitter,
        )

        def execute_exit_x3(request_id, run_id, ...):
            emitter = RuntimeSpanEmitter.for_request(
                scenario="live_request",
                request_id=request_id,
                run_id=run_id,
            )
            with emitter.span(
                "exit.x3.disposition",
                route_id=route_id,
                replay_key=replay_key,
                reason_codes=reason_codes,
                status=status,
            ):
                ...  # existing decision logic untouched
            emitter.flush(traces_dir=Path("artifacts/runtime/live_traces"))

    The contract is identical to the harness recorder so all Phase-5/6/7
    validators apply unchanged to live traces.
    """

    def __init__(
        self,
        scenario: str,
        request_id: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> None:
        self._recorder = RuntimeSpanRecorder(
            scenario=scenario,
            request_id=request_id,
            run_id=run_id,
        )
        self._backend = _try_real_otel_backend() or _NullOtelBackend(self._recorder)

    @classmethod
    def for_request(
        cls,
        scenario: str = "live_request",
        request_id: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> "RuntimeSpanEmitter":
        return cls(scenario=scenario, request_id=request_id, run_id=run_id)

    @contextmanager
    def span(self, name: str, **attrs: Any) -> Iterator[str]:
        """Emit a span. Name MUST be in the canonical RUNTIME_SPAN_NAMES."""
        if name not in RUNTIME_SPAN_NAMES:
            raise ValueError(
                f"unknown runtime span name {name!r} -- canonical vocabulary is "
                f"defined in agentic_core.runtime.prove_requirements.otel_contract"
            )
        with self._backend.emit_span(name, **attrs) as span_id:
            yield span_id

    def finalize(self) -> RuntimeTrace:
        return self._recorder.finalize()

    def flush(self, traces_dir: Optional[Path] = None) -> Optional[Path]:
        """Write the captured trace to disk. Returns the path or None when
        traces_dir is omitted (some live use-cases keep traces in-memory)."""
        if traces_dir is None:
            return None
        trace = self.finalize()
        path = traces_dir / f"live_{trace.scenario}_{trace.trace_id[:12]}.json"
        write_trace(trace, path)
        return path


__all__ = ["RuntimeSpanEmitter"]
