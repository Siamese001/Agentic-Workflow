"""
L5 Safety - Validators
======================
Core validation and safety enforcement agents.

Note: Imports are lazy to avoid circular import issues.
Use direct imports when needed:
    from agentic_core.L5_safety.reasoning.LocationAgent import LocationAgent
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace  # noqa: E402
from agentic_core.runtime.lifecycle_trace_contract import _emit_applies_guardrail  # noqa: E402
from agentic_core.runtime.lifecycle_trace_contract import _emit_signs_execution_trace  # noqa: E402
from agentic_core.runtime.lifecycle_trace_contract import _emit_snapshots_state  # noqa: E402
_emit_snapshots_state("p0", "__init__", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "__init__", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "__init__")
"""
