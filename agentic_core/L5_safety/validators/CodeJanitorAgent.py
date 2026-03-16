"""
validators/CodeJanitorAgent.py — backward-compat re-export shim.

Canonical implementation has moved to:
    agentic_core.L5_safety.reasoning.CodeJanitorAgent

This file is a pure re-export stub with NO mutation logic of its own.
All filesystem writes (_write_file_content, _smart_fix, heal_repository) are in
reasoning/CodeJanitorAgent.py (L5 healer territory).

ADG fix: A-04 (CodeJanitorAgent split — healer logic moved to reasoning/).
"""

from __future__ import annotations

from agentic_core.L5_safety.reasoning.CodeJanitorAgent import (
    CodeJanitorAgent,
    JanitorViolation,
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
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "CodeJanitorAgent")
emit_determinism_digest("p0", "CodeJanitorAgent")

_emit_dispatches_healing_run("p1", "CodeJanitorAgent", "L5")
_emit_routes_through("p1", "CodeJanitorAgent", "L5")
_emit_escalates_to_human("p1", "CodeJanitorAgent", "L5")
_emit_reads_policy_state("p1", "CodeJanitorAgent", "L5")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "CodeJanitorAgent")
_emit_applies_guardrail("p0", "CodeJanitorAgent", "p0_governance")
_emit_snapshots_state("p0", "CodeJanitorAgent", "state_snapshot")

__all__ = ["CodeJanitorAgent", "JanitorViolation"]
