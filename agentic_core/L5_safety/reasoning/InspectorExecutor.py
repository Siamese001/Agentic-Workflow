"""InspectorExecutor — Canonical parameterized inspector agent.

Consolidates: DagRuntimeInspectorAgent, SignatureVerifierAgent, TokenBudgetInspectorAgent
Created: 2026-02-08 (Structural Agent Count Reduction)
"""

from __future__ import annotations

from dataclasses import dataclass, field

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.mixins.inspection_capability_mixin import InspectionCapability


@dataclass
class InspectorExecutor(InspectionCapability, SovereignBaseAgent):
    """Parameterized inspector that dispatches to domain-specific check logic.

    Usage:
        inspector = InspectorExecutor(inspector_type="dag_runtime")
    """

    inspector_type: str = "generic"
    INSPECTION_LOG_PREFIX: str = field(init=False, default="Inspector")

    def __post_init__(self) -> None:
        prefixes = {
            "dag_runtime": "DagRuntime",
            "signature": "Signature",
            "token_budget": "TokenBudget",
        }
        self.INSPECTION_LOG_PREFIX = prefixes.get(self.inspector_type, "Inspector")

    # perform_checks() inherited from InspectionCapability (default structural checks).
    # Override here when domain-specific logic is added per inspector_type.
