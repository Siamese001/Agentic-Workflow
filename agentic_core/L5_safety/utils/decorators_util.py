"""
Backward-compatibility shim for decorator imports.

DEPRECATED: Import from agentic_core.utils.decorators_util instead.

This module re-exports symbols from the canonical location for backward
compatibility with existing code. New code should import directly from:
    from agentic_core.utils.decorators_util import standard_heal, HEAL_RESULT_SCHEMA

Canonical location: agentic_core/utils/decorators_util.py
"""

from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)
from agentic_core.utils.decorators_util import (  # noqa: F401
    HEAL_RESULT_SCHEMA,
    standard_heal,
    standard_heal_async,
)

_emit_dispatches_healing_run("p1", "decorators_util", "L5")
_emit_routes_through("p1", "decorators_util", "L5")
_emit_escalates_to_human("p1", "decorators_util", "L5")
_emit_reads_policy_state("p1", "decorators_util", "L5")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "decorators_util")
_emit_applies_guardrail("p0", "decorators_util", "p0_governance")
_emit_snapshots_state("p0", "decorators_util", "state_snapshot")

__all__ = [
    "standard_heal",
    "standard_heal_async",
    "HEAL_RESULT_SCHEMA",
]
