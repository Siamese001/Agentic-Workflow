"""
SSOT Tracing Mixin — Policy-Hash-Scoped Span Management.

Provides tracing that:
  - Includes trace_id and policy_hash in every span
  - Replay mode disables sampling randomness (100% sample rate)
  - No manual span stack mutation
  - Context-managed span lifecycle

Layer: L6 Observer
Authority: Trace emission only. No L4 mutation. No routing influence.
"""

from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from typing import Any, Generator

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

_logger = logging.getLogger("SSOTTracing")


class SSOTTracingMixin:
    """Policy-hash-scoped tracing with replay-safe sampling.

    Reads ``active_policy_hash``, ``trace_id``, and ``is_replay_mode``
    from ReplayGuardMixin. All spans include trace_id and policy_hash.
    Under replay mode, sampling rate is forced to 1.0 (all spans traced).
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._ssot_spans: list[dict[str, Any]] = []
        self._ssot_active_span: dict[str, Any] | None = None

    @contextmanager
    def trace_span(
        self,
        operation: str,
        tags: dict[str, str] | None = None,
    ) -> Generator[dict[str, Any], None, None]:
        """Context manager for a traced span.

        Parameters
        ----------
        operation : str
            Name of the operation being traced.
        tags : dict | None
            Optional tags to attach to the span.

        Yields
        ------
        dict
            The span dict (mutable — caller can add tags).
        """
        trace_id = getattr(self, "trace_id", "unknown")
        policy_hash = getattr(self, "active_policy_hash", "unknown")

        span = {
            "operation": operation,
            "trace_id": trace_id,
            "policy_hash": policy_hash,
            "start_time": time.time(),
            "end_time": None,
            "duration_ms": None,
            "tags": tags or {},
            "status": "active",
            "error": None,
        }

        parent = self._ssot_active_span
        if parent is not None:
            span["parent_operation"] = parent["operation"]

        self._ssot_active_span = span

        try:
            yield span
            span["status"] = "ok"
        except Exception as exc:
            span["status"] = "error"
            span["error"] = str(exc)
            raise
        finally:
            span["end_time"] = time.time()
            span["duration_ms"] = (span["end_time"] - span["start_time"]) * 1000
            self._ssot_spans.append(span)
            self._ssot_active_span = parent

            _logger.debug(
                "[SSOTTrace] %s | %.1fms | %s",
                operation,
                span["duration_ms"],
                span["status"],
            )

    @property
    def completed_spans(self) -> list[dict[str, Any]]:
        """All completed spans."""
        return list(self._ssot_spans)

    @property
    def active_span(self) -> dict[str, Any] | None:
        """Currently active span, or None."""
        return self._ssot_active_span
