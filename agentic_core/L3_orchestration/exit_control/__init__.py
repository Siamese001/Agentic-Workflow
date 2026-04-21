"""L3 runtime HITL exit-control dispatch plane.

Per ADR-023 §3.2, L3 owns dispatch mechanics while L5 owns policy. This package
provides:

- ``exit_controller.classify_exit`` — the single step [5] decision primitive
- ``runtime_hitl_ledger`` — persistent per-run state store
- ``hitl_spans`` — OTel span emission for hitl.escalate/approved/denied/timeout

Scope: RUNTIME HITL (v30 step [5]). NOT developer-loop Author-Gate.
"""

from agentic_core.L3_orchestration.exit_control.exit_controller import (
    ExitAction,
    ExitDecision,
    ExitController,
    classify_exit,
)
from agentic_core.L3_orchestration.exit_control.hitl_spans import (
    emit_approved,
    emit_denied,
    emit_escalate,
    emit_timeout,
)
from agentic_core.L3_orchestration.exit_control.runtime_hitl_ledger import (
    LedgerEntry,
    LedgerState,
    RuntimeHitlLedger,
)

__all__ = [
    "ExitAction",
    "ExitController",
    "ExitDecision",
    "LedgerEntry",
    "LedgerState",
    "RuntimeHitlLedger",
    "classify_exit",
    "emit_approved",
    "emit_denied",
    "emit_escalate",
    "emit_timeout",
]
