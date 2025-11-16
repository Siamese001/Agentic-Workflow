"""
L3 — Graph Orchestrator

Responsibilities:
    • Coordinate agentic workflows across a graph of tasks and dependencies.
    • Route intents from L1 reasoners to appropriate L2 execution agents.
    • Integrate safety decisions from L5 without embedding policy logic.

This file is scaffolded for Priority 0; implementation comes later.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from l1_strategy_reasoner import StrategyReasoner
from l2_rag_execution import RAGExecutionAgent
from l4_state_adapter import StateAdapter
from l5_safety_gateway import SafetyGateway
from utils_types import PlanObject, StatePatch


@dataclass
class OrchestrationResult:
    """Container describing the outcome of a single orchestration pass."""

    plan: PlanObject
    execution_patch: StatePatch
    safety_patch: StatePatch
    state: Dict[str, Any]


class GraphOrchestrator:
    """Coordinate planning, execution, patching, and safety evaluation."""

    def __init__(
        self,
        reasoner: StrategyReasoner | None = None,
        executor: RAGExecutionAgent | None = None,
        state_adapter: StateAdapter | None = None,
        safety_gateway: SafetyGateway | None = None,
    ) -> None:
        self.reasoner = reasoner or StrategyReasoner()
        self.executor = executor or RAGExecutionAgent()
        self.state_adapter = state_adapter or StateAdapter()
        self.safety_gateway = safety_gateway or SafetyGateway()

    def orchestrate(self, state: Optional[Dict[str, Any]] = None) -> OrchestrationResult:
        """Execute the deterministic orchestration sequence without side effects."""

        if state is not None:
            self.state_adapter.apply_patch(StatePatch(state))

        current_state = self.state_adapter.state
        plan = self.reasoner.plan(current_state)
        execution_patch = self.executor.execute(plan, current_state)
        updated_state = self.state_adapter.apply_patch(execution_patch)

        safety_payload = {
            "content": self._latest_content(updated_state),
            "intent": plan,
        }
        safety_patch = self.safety_gateway.evaluate(safety_payload)
        final_state = self.state_adapter.apply_patch(safety_patch)

        return OrchestrationResult(plan, execution_patch, safety_patch, final_state)

    @staticmethod
    def _latest_content(state: Dict[str, Any]) -> str:
        """Return the most recent assistant message for safety evaluation."""

        messages = state.get("messages") or []
        if messages:
            last = messages[-1]
            if isinstance(last, dict):
                return str(last.get("content", ""))
        return ""
