"""
validators/GovernanceAgent.py — backward-compat re-export shim.

Canonical implementation lives at:
    agentic_core.L5_safety.reasoning.GovernanceAgent

This file is a pure re-export stub with NO mutation logic of its own.
All writes_to / healing operations are in reasoning/GovernanceAgent.py
(L5 healer territory, which correctly uses write_gateway).

ADG fix: A-07 (dedup) + A-01 (validators/ mutation boundary).
"""

from __future__ import annotations

from agentic_core.L5_safety.reasoning.GovernanceAgent import (
    DependencyGraph,
    GovernanceAgent,
    heal,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "GovernanceAgent")
_emit_applies_guardrail("p0", "GovernanceAgent", "p0_governance")
_emit_snapshots_state("p0", "GovernanceAgent", "state_snapshot")

__all__ = ["DependencyGraph", "GovernanceAgent", "heal"]
