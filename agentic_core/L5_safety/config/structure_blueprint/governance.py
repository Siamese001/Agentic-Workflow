"""
Governance Module — backward-compatible re-export from _constants.

All governance configuration now lives in _constants.py (the leaf node).
This module re-exports them for backward compatibility.
"""

from __future__ import annotations

from agentic_core.L5_safety.config.structure_blueprint._constants import (  # noqa: F401
    AGENT_RESILIENCE_CONFIG,
    DOWNSTREAM_ROOTS,
    GRAVITY_CONFIG,
    GRAVITY_SURGERY_ENABLED,
    HEALING_CONFIG,
    MCP_CAPABILITIES,
    MISSION_CONFIG,
    UPSTREAM_SOVEREIGN_ROOTS,
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

_emit_dispatches_healing_run("p1", "governance", "L5")
_emit_routes_through("p1", "governance", "L5")
_emit_escalates_to_human("p1", "governance", "L5")
_emit_reads_policy_state("p1", "governance", "L5")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "governance")
_emit_applies_guardrail("p0", "governance", "p0_governance")
_emit_snapshots_state("p0", "governance", "state_snapshot")
