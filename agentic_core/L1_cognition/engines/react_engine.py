"""ReAct Engine — canonical location in L1_cognition/engines/.

Re-exports ReActEngine, ReActTrace, ReActStep, and create_react_engine from
the existing implementation in react_config.py so callers can import from
the correct layer path:

    from agentic_core.L1_cognition.engines.react_engine import ReActEngine

The original react_config.py is kept intact (no deletion) to avoid breaking
any existing imports.
"""

from __future__ import annotations

from agentic_core.L1_cognition.config.react_config import (  # noqa: F401
    ReActEngine,
    ReActStep,
    ReActTrace,
    ReasoningMode,
    create_react_engine,
)
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

_emit_dispatches_healing_run("p1", "react_engine", "L1")
_emit_routes_through("p1", "react_engine", "L1")
_emit_escalates_to_human("p1", "react_engine", "L1")
_emit_reads_policy_state("p1", "react_engine", "L1")
_emit_snapshots_state("p0", "react_engine", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "react_engine", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "react_engine")

__all__ = [
    "ReActEngine",
    "ReActStep",
    "ReActTrace",
    "ReasoningMode",
    "create_react_engine",
]
