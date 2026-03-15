"""
Backward-compatibility shim for timeout decorator imports.

DEPRECATED: Import from agentic_core.utils.timeout_decorator_util instead.

This module re-exports symbols from the canonical location for backward
compatibility with existing code. New code should import directly from:
    from agentic_core.utils.timeout_decorator_util import timeout
from agentic_core.runtime.lifecycle_trace_contract import _emit_snapshots_state  # noqa: E402
from agentic_core.runtime.lifecycle_trace_contract import _emit_applies_guardrail  # noqa: E402
from agentic_core.runtime.lifecycle_trace_contract import _emit_signs_execution_trace  # noqa: E402
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace  # noqa: E402
_emit_records_execution_trace("p0", "evidence", "timeout_decorator_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "timeout_decorator_util", "p0_governance")
_emit_snapshots_state("p0", "timeout_decorator_util", "state_snapshot")

Canonical location: agentic_core/base_agents/timeout_decorator.py
"""

from __future__ import annotations

from agentic_core.utils.timeout_decorator_util import TimeoutError, timeout

__all__ = ["timeout", "TimeoutError"]
