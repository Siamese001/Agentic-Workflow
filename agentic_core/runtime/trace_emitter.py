"""
agentic_core/runtime/trace_emitter.py

TraceEmitter — mixin and decorator for structured execution trace emission.

P0-L6 gap remediation: all boundary-crossing modules across L0–L6 should
inherit TraceEmitter or use @emit_trace to link their execution to the
active ExecutionTrace, producing records_execution_trace ADG edges at runtime.
"""

from __future__ import annotations

import functools
import hashlib
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable

from agentic_core.runtime.execution_trace import (
    ExecutionTrace,
    get_active_execution_trace,
)
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

logger = logging.getLogger(__name__)


@dataclass
class TraceRecord:
    """Single execution trace record emitted by TraceEmitter."""

    trace_id: str
    layer: str
    module: str
    operation: str
    elapsed_ms: float
    determinism_digest: str
    success: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "layer": self.layer,
            "module": self.module,
            "operation": self.operation,
            "elapsed_ms": round(self.elapsed_ms, 3),
            "determinism_digest": self.determinism_digest,
            "success": self.success,
            "metadata": self.metadata,
        }


class TraceEmitter:
    """Mixin that adds structured execution trace emission to any module.

    Usage::

        class MyL1Engine(TraceEmitter):
            _LAYER = "L1"

            def run(self, prompt: str) -> str:
                with self.trace_operation("run"):
                    return self._do_work(prompt)
    """

    _LAYER: str = "UNKNOWN"
    _MODULE: str = ""

    def _module_name(self) -> str:
        return self._MODULE or type(self).__module__ + "." + type(self).__qualname__

    def _current_trace(self) -> ExecutionTrace | None:
        return get_active_execution_trace()

    def _make_digest(self, operation: str, elapsed_ms: float) -> str:
        payload = f"{self._LAYER}:{self._module_name()}:{operation}:{elapsed_ms:.3f}"
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    def emit_trace_record(
        self,
        operation: str,
        elapsed_ms: float,
        success: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> TraceRecord:
        """Emit a structured trace record for this module's operation."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "TraceEmitter.emit_trace_record")

        active = self._current_trace()
        trace_id = active.trace_id if active else "no-active-trace"
        digest = self._make_digest(operation, elapsed_ms)
        record = TraceRecord(
            trace_id=trace_id,
            layer=self._LAYER,
            module=self._module_name(),
            operation=operation,
            elapsed_ms=elapsed_ms,
            determinism_digest=digest,
            success=success,
            metadata=metadata or {},
        )
        logger.debug(
            "TRACE_EMIT layer=%s module=%s op=%s trace_id=%s elapsed_ms=%.1f ok=%s",
            self._LAYER,
            self._module_name(),
            operation,
            trace_id,
            elapsed_ms,
            success,
        )
        return record

    class trace_operation:
        """Context manager for timing and emitting a trace record."""

        def __init__(self, emitter: TraceEmitter, operation: str, metadata: dict[str, Any] | None = None):
            self._emitter = emitter
            self._operation = operation
            self._metadata = metadata or {}
            self._start: float = 0.0
            self._record: TraceRecord | None = None

        def __enter__(self) -> TraceEmitter.trace_operation:
            self._start = time.monotonic()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
            elapsed_ms = (time.monotonic() - self._start) * 1000.0
            success = exc_type is None
            self._record = self._emitter.emit_trace_record(
                self._operation, elapsed_ms, success=success, metadata=self._metadata
            )
            return False

        @property
        def record(self) -> TraceRecord | None:
            return self._record

    def trace_op(
        self, operation: str, metadata: dict[str, Any] | None = None
    ) -> TraceEmitter.trace_operation:
        """Return a context manager that traces `operation`."""
        return TraceEmitter.trace_operation(self, operation, metadata)


def emit_trace(layer: str, operation: str | None = None) -> Callable:
    """Decorator: wrap a callable with TraceEmitter emission.

    Usage::

        @emit_trace("L1", "generate_prompt")
        def generate_prompt(self, prompt: str) -> str:
            ...
    """

    def decorator(fn: Callable) -> Callable:
        op_name = operation or fn.__name__

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            start = time.monotonic()
            active = get_active_execution_trace()
            trace_id = active.trace_id if active else "no-active-trace"
            module_name = (
                f"{args[0].__class__.__module__}.{args[0].__class__.__qualname__}" if args else fn.__module__
            )
            try:
                result = fn(*args, **kwargs)
                elapsed_ms = (time.monotonic() - start) * 1000.0
                digest = hashlib.sha256(
                    f"{layer}:{module_name}:{op_name}:{elapsed_ms:.3f}".encode()
                ).hexdigest()[:16]
                logger.debug(
                    "TRACE_EMIT layer=%s module=%s op=%s trace_id=%s elapsed_ms=%.1f ok=True digest=%s",
                    layer,
                    module_name,
                    op_name,
                    trace_id,
                    elapsed_ms,
                    digest,
                )
                return result
            except Exception:
                elapsed_ms = (time.monotonic() - start) * 1000.0
                logger.debug(
                    "TRACE_EMIT layer=%s module=%s op=%s trace_id=%s elapsed_ms=%.1f ok=False",
                    layer,
                    module_name,
                    op_name,
                    trace_id,
                    elapsed_ms,
                )
                raise

        return wrapper

    return decorator


__all__ = ["TraceEmitter", "TraceRecord", "emit_trace"]
