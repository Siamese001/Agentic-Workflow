"""
L3 — QA Orchestrator

Responsibilities:
    • Govern validation workflows driven by L2 QA execution agents.
    • Align verification steps with L1 reasoning intents and L5 safety directives.
    • Aggregate validation artifacts into L4 state for traceability.

This file is scaffolded for Priority 0; implementation comes later.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from l1_strategy_reasoner import StrategyReasoner
from l2_qa_validation import QAValidationAgent
from l3_graph_orchestrator import OrchestrationResult
from l4_state_adapter import StateAdapter
from l5_safety_gateway import SafetyGateway
from utils_types import StatePatch


class QAOrchestrator:
    """Govern QA validation without embedding lower-layer logic."""

    def __init__(
        self,
        reasoner: StrategyReasoner | None = None,
        executor: QAValidationAgent | None = None,
        state_adapter: StateAdapter | None = None,
        safety_gateway: SafetyGateway | None = None,
    ) -> None:
        self.reasoner = reasoner or StrategyReasoner()
        self.executor = executor or QAValidationAgent()
        self.state_adapter = state_adapter or StateAdapter()
        self.safety_gateway = safety_gateway or SafetyGateway()

    def orchestrate(self, state: Optional[Dict[str, Any]] = None) -> OrchestrationResult:
        """Run plan→execute→patch→safety in order."""

        if state is not None:
            self.state_adapter.apply_patch(StatePatch(state))

        current_state = self.state_adapter.state
        plan = self.reasoner.plan(current_state)
        execution_patch = self.executor.execute(plan, current_state)
        updated_state = self.state_adapter.apply_patch(execution_patch)

        safety_patch = self.safety_gateway.evaluate(
            {"content": updated_state.get("qa_report", {}), "intent": plan}
        )
        final_state = self.state_adapter.apply_patch(safety_patch)

        return OrchestrationResult(plan, execution_patch, safety_patch, final_state)
