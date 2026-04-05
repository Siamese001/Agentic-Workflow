"""L0 Routing Utils - Seams for layer integration interfaces.

This module provides controlled seams/interfaces for integration between
layers without creating direct import dependencies.
"""
from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_reads_policy_state,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    emit_determinism_digest,
    emit_replay_key,
)

_emit_records_execution_trace("p0", "evidence", "L0_utils_seams")
_emit_applies_guardrail("p0", "L0_utils_seams", "p0_governance")
_emit_reads_policy_state("p0", "L0_utils_seams", "policy_binding")
_emit_snapshots_state("p0", "L0_utils_seams", "state_snapshot")
emit_replay_key("p0", "L0_utils_seams")
emit_determinism_digest("p0", "L0_utils_seams")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

__all__: list[str] = []
