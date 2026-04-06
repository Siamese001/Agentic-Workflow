"""Clock Provider — injectable time source for deterministic testing.

Provides a unified clock interface used by L2 execution types,
guardrails, and error recovery. Supports monkey-patching for
deterministic replay in tests.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_reads_policy_state,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    emit_determinism_digest,
    emit_replay_key,
)

_emit_records_execution_trace("p0", "evidence", "clock_provider")
_emit_applies_guardrail("p0", "clock_provider", "p0_governance")
_emit_reads_policy_state("p0", "clock_provider", "policy_binding")
_emit_snapshots_state("p0", "clock_provider", "state_snapshot")
emit_replay_key("p0", "clock_provider")
emit_determinism_digest("p0", "clock_provider")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class ClockProvider:
    """Injectable clock for deterministic time access.

    Class-level methods delegate to ``datetime.now`` / ``time.time``
    by default.  Override ``_now_fn`` / ``_time_fn`` in tests to
    inject deterministic clocks.
    """

    _now_fn = datetime.now
    _time_fn = time.time

    @classmethod
    def now(cls, tz: timezone | None = None) -> datetime:
        """Return current datetime, optionally in *tz*."""
        if tz is not None:
            return cls._now_fn(tz)
        return cls._now_fn()

    @classmethod
    def time(cls) -> float:
        """Return monotonic-ish epoch seconds (like ``time.time()``)."""
        return cls._time_fn()

    @classmethod
    def reset(cls) -> None:
        """Restore real clock — call in test teardown."""
        cls._now_fn = datetime.now
        cls._time_fn = time.time


__all__ = ["ClockProvider"]
