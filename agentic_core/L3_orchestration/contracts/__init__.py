from agentic_core.L3_orchestration.contracts.agent_handoff import (
    AgentHandoff,
    HandoffDispatcher,
    HandoffRecord,
    HandoffStatus,
)
from agentic_core.L3_orchestration.contracts.orchestration_context import OrchestrationContext
from agentic_core.L3_orchestration.contracts.orchestration_handoff_contract import (
    OrchestrationHandoffContract,
    emit_agent_executes_agent,
)
from agentic_core.L3_orchestration.contracts.run_scoped_orchestration_ledger import (
    RunScopedOrchestrationLedger,
    StageOwnershipRecord,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_snapshots_state("p0", "__init__", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "__init__", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "__init__")

__all__ = [
    "AgentHandoff",
    "HandoffDispatcher",
    "HandoffRecord",
    "HandoffStatus",
    "OrchestrationContext",
    "OrchestrationHandoffContract",
    "emit_agent_executes_agent",
    "RunScopedOrchestrationLedger",
    "StageOwnershipRecord",
]
