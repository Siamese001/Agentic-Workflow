# Canonical definitions moved to agentic_core/mixins/state_validation_mixin.py
# Re-export for backward compatibility
from agentic_core.mixins.state_validation_mixin import (  # noqa: F401
    StateValidationError,
    StateValidationMixin,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_snapshots_state("p0", "state_validation_types", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "state_validation_types", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "state_validation_types")
