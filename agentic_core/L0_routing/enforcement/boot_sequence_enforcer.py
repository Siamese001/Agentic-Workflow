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

from .boot_sequence import *

_emit_dispatches_healing_run("p1", "boot_sequence_enforcer", "L0")
_emit_routes_through("p1", "boot_sequence_enforcer", "L0")
_emit_escalates_to_human("p1", "boot_sequence_enforcer", "L0")
_emit_reads_policy_state("p1", "boot_sequence_enforcer", "L0")

_emit_records_execution_trace("p0", "evidence", "boot_sequence_enforcer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "boot_sequence_enforcer", "p0_governance")
_emit_snapshots_state("p0", "boot_sequence_enforcer", "state_snapshot")
