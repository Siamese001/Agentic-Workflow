"""
L3 — RAG Orchestrator

Responsibilities:
    • Manage control flow for retrieval-augmented reasoning cycles.
    • Align L1 RAG planning outputs with L2 retrieval execution steps.
    • Record orchestration outcomes for L4 state persistence and audits.

This file is scaffolded for Priority 0; implementation comes later.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from l1_rag_reasoner import RAGReasoner
from l2_rag_execution import RAGExecutionAgent
from l3_graph_orchestrator import OrchestrationResult
from l4_state_adapter import StateAdapter
from l5_safety_gateway import SafetyGateway
from utils_types import StatePatch


class RAGOrchestrator:
    """Manage the deterministic RAG orchestration sequence."""

    def __init__(
        self,
        reasoner: RAGReasoner | None = None,
        executor: RAGExecutionAgent | None = None,
        state_adapter: StateAdapter | None = None,
        safety_gateway: SafetyGateway | None = None,
    ) -> None:
        self.reasoner = reasoner or RAGReasoner()
        self.executor = executor or RAGExecutionAgent()
        self.state_adapter = state_adapter or StateAdapter()
        self.safety_gateway = safety_gateway or SafetyGateway()

    def orchestrate(self, state: Optional[Dict[str, Any]] = None) -> OrchestrationResult:
        """Plan, execute, patch, and evaluate safety in order."""

        if state is not None:
            self.state_adapter.apply_patch(StatePatch(state))

        current_state = self.state_adapter.state
        plan = self.reasoner.plan(current_state)
        execution_patch = self.executor.execute(plan, current_state)
        updated_state = self.state_adapter.apply_patch(execution_patch)

        safety_patch = self.safety_gateway.evaluate(
            {"content": updated_state.get("last_retrieval", {}), "intent": plan}
        )
        final_state = self.state_adapter.apply_patch(safety_patch)

        return OrchestrationResult(plan, execution_patch, safety_patch, final_state)
