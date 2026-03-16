import warnings

from agentic_core.L3_orchestration.engines.omni_context_engine import *
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

emit_replay_key("p0", "context_util")
emit_determinism_digest("p0", "context_util")

_emit_dispatches_healing_run("p1", "context_util", "L4")
_emit_routes_through("p1", "context_util", "L4")
_emit_escalates_to_human("p1", "context_util", "L4")
_emit_reads_policy_state("p1", "context_util", "L4")

_emit_snapshots_state("p0", "context_util", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "context_util", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "context_util")

warnings.warn("Deprecated. Import from 'omni_context' instead.", DeprecationWarning, stacklevel=2)
