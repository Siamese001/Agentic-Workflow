# Canonical definitions moved to agentic_core/mixins/state_validation_mixin.py
# Re-export for backward compatibility
from agentic_core.mixins.state_validation_mixin import (  # noqa: F401
    StateValidationError,
    StateValidationMixin,
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

emit_replay_key("p0", "state_validation_types")
emit_determinism_digest("p0", "state_validation_types")

_emit_dispatches_healing_run("p1", "state_validation_types", "L4")
_emit_routes_through("p1", "state_validation_types", "L4")
_emit_escalates_to_human("p1", "state_validation_types", "L4")
_emit_reads_policy_state("p1", "state_validation_types", "L4")

_emit_snapshots_state("p0", "state_validation_types", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "state_validation_types", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "state_validation_types")
