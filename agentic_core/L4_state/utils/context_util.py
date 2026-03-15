import warnings

from agentic_core.L3_orchestration.engines.omni_context_engine import *
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_snapshots_state("p0", "context_util", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "context_util", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "context_util")

warnings.warn("Deprecated. Import from 'omni_context' instead.", DeprecationWarning, stacklevel=2)
