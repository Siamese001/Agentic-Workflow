"""
validators/PascalSovereigntyAgent.py — backward-compat re-export shim.

Canonical implementation has moved to:
    agentic_core.L5_safety.reasoning.PascalSovereigntyAgent

This file is a pure re-export stub with NO mutation logic of its own.
All filesystem mutations (rename, delete, import rewrite) are in
reasoning/PascalSovereigntyAgent.py (L5 healer territory).

ADG fix: A-02 (healer misplaced in validators/) + A-01 (validators/ mutation boundary).
"""

from __future__ import annotations

from agentic_core.L5_safety.reasoning.PascalSovereigntyAgent import (
    FileType,
    PascalSovereigntyAgent,
    get_python_files_fast,
    main,
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

emit_replay_key("p0", "PascalSovereigntyAgent")
emit_determinism_digest("p0", "PascalSovereigntyAgent")

_emit_dispatches_healing_run("p1", "PascalSovereigntyAgent", "L5")
_emit_routes_through("p1", "PascalSovereigntyAgent", "L5")
_emit_escalates_to_human("p1", "PascalSovereigntyAgent", "L5")
_emit_reads_policy_state("p1", "PascalSovereigntyAgent", "L5")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "PascalSovereigntyAgent")
_emit_applies_guardrail("p0", "PascalSovereigntyAgent", "p0_governance")
_emit_snapshots_state("p0", "PascalSovereigntyAgent", "state_snapshot")

__all__ = ["FileType", "PascalSovereigntyAgent", "get_python_files_fast", "main"]
