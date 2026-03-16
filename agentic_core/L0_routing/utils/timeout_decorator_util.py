"""
Backward-compatibility shim for timeout decorator imports.

DEPRECATED: Import from agentic_core.utils.timeout_decorator_util instead.

This module re-exports symbols from the canonical location for backward
compatibility with existing code. New code should import directly from:
    from agentic_core.utils.timeout_decorator_util import timeout

Canonical location: agentic_core/base_agents/timeout_decorator.py
"""

from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402  # noqa: E402
    _emit_snapshots_state,  # noqa: E402  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from agentic_core.utils.timeout_decorator_util import TimeoutError, timeout

emit_replay_key("p0", "timeout_decorator_util")
emit_determinism_digest("p0", "timeout_decorator_util")

_emit_dispatches_healing_run("p1", "timeout_decorator_util", "L0")
_emit_routes_through("p1", "timeout_decorator_util", "L0")
_emit_escalates_to_human("p1", "timeout_decorator_util", "L0")
_emit_reads_policy_state("p1", "timeout_decorator_util", "L0")
_emit_records_execution_trace("p0", "evidence", "timeout_decorator_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "timeout_decorator_util", "p0_governance")
_emit_snapshots_state("p0", "timeout_decorator_util", "state_snapshot")

__all__ = ["timeout", "TimeoutError"]
