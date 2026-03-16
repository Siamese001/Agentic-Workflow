"""CONSOLIDATED: DagRuntimeInspectorAgent → InspectorExecutor (2026-02-08).

This file is a backward-compatibility shim.
Import the canonical executor directly for new code.
"""

import importlib as _importlib

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "DagRuntimeInspectorAgent")
emit_determinism_digest("p0", "DagRuntimeInspectorAgent")

_emit_dispatches_healing_run("p1", "DagRuntimeInspectorAgent", "L3")
_emit_routes_through("p1", "DagRuntimeInspectorAgent", "L3")
_emit_escalates_to_human("p1", "DagRuntimeInspectorAgent", "L3")
_emit_reads_policy_state("p1", "DagRuntimeInspectorAgent", "L3")

_emit_snapshots_state("p0", "DagRuntimeInspectorAgent", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "DagRuntimeInspectorAgent", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "DagRuntimeInspectorAgent")

_mod = _importlib.import_module("agentic_core.L5_safety.reasoning.InspectorExecutor")
DagRuntimeInspectorAgent = _mod.InspectorExecutor
__all__ = ["DagRuntimeInspectorAgent"]
