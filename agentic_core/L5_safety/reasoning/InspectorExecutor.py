"""InspectorExecutor — Canonical parameterized inspector agent.

Consolidates: DagRuntimeInspectorAgent, SignatureVerifierAgent, TokenBudgetInspectorAgent
Created: 2026-02-08 (Structural Agent Count Reduction)
"""

from __future__ import annotations

from dataclasses import dataclass, field

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.mixins.inspection_capability_mixin import InspectionCapability
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

_emit_dispatches_healing_run("p1", "InspectorExecutor", "L5")
_emit_routes_through("p1", "InspectorExecutor", "L5")
_emit_escalates_to_human("p1", "InspectorExecutor", "L5")
_emit_reads_policy_state("p1", "InspectorExecutor", "L5")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "InspectorExecutor")
_emit_applies_guardrail("p0", "InspectorExecutor", "p0_governance")
_emit_snapshots_state("p0", "InspectorExecutor", "state_snapshot")


@dataclass
class InspectorExecutor(InspectionCapability, SovereignBaseAgent):
    """Parameterized inspector that dispatches to domain-specific check logic.

    Usage:
        inspector = InspectorExecutor(inspector_type="dag_runtime")
    """

    inspector_type: str = "generic"
    INSPECTION_LOG_PREFIX: str = field(init=False, default="Inspector")

    def __post_init__(self) -> None:
        prefixes = {"dag_runtime": "DagRuntime", "signature": "Signature", "token_budget": "TokenBudget"}
        self.INSPECTION_LOG_PREFIX = prefixes.get(self.inspector_type, "Inspector")
