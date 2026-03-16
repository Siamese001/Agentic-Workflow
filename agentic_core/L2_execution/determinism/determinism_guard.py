"""Determinism guard context managers for REQ-111 and REQ-114.

Provides context managers to assert absence of uuid4 and wall-clock usage
in determinism-critical code paths.
"""

from __future__ import annotations

import time
import uuid
from contextlib import contextmanager
from typing import Generator

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "determinism_guard")
emit_determinism_digest("p0", "determinism_guard")

_emit_dispatches_healing_run("p1", "determinism_guard", "L2")
_emit_routes_through("p1", "determinism_guard", "L2")
_emit_escalates_to_human("p1", "determinism_guard", "L2")
_emit_reads_policy_state("p1", "determinism_guard", "L2")


@contextmanager
def assert_no_uuid4() -> Generator[None, None, None]:
    """Context manager to assert no uuid4 is used within the context.

    Raises:
        RuntimeError: If uuid.uuid4() is called within the context.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "assert_no_uuid4", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "assert_no_uuid4", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "assert_no_uuid4")
    original_uuid4 = uuid.uuid4

    def tracking_uuid4() -> uuid.UUID:
        raise RuntimeError(
            "uuid.uuid4() called in determinism-critical context. Use deterministic UUID generation instead."
        )

    uuid.uuid4 = tracking_uuid4
    try:
        yield
    finally:
        uuid.uuid4 = original_uuid4


@contextmanager
def assert_no_wallclock() -> Generator[None, None, None]:
    """Context manager to assert no wall-clock is used within the context.

    Note: Cannot patch datetime.now directly as it's immutable, so we track
    time module functions which are the most common wall-clock sources.

    Raises:
        RuntimeError: If time.time(), time.sleep(), or similar wall-clock functions are called.
    """
    original_time = time.time
    original_sleep = time.sleep
    original_monotonic = getattr(time, "monotonic", None)

    def tracking_time() -> float:
        raise RuntimeError(
            "time.time() called in determinism-critical context. Use semantic clock ticks instead."
        )

    def tracking_sleep(seconds: float) -> None:
        raise RuntimeError(
            "time.sleep() called in determinism-critical context. Use deterministic delay mechanisms instead."
        )

    def tracking_monotonic() -> float:
        raise RuntimeError(
            "time.monotonic() called in determinism-critical context. Use semantic clock ticks instead."
        )

    time.time = tracking_time
    time.sleep = tracking_sleep
    if original_monotonic is not None:
        time.monotonic = tracking_monotonic
    try:
        yield
    finally:
        time.time = original_time
        time.sleep = original_sleep
        if original_monotonic is not None:
            time.monotonic = original_monotonic


@contextmanager
def assert_deterministic_context() -> Generator[None, None, None]:
    """Combined context manager asserting both no uuid4 and no wall-clock.

    This is a convenience wrapper that enables both guards simultaneously.
    """
    with assert_no_uuid4(), assert_no_wallclock():
        yield
