# orchestrator.py
# FILE: v10_9_clean/l3/orchestrator.py
"""
L3 — Global Orchestrator (v10_9)

This is the central L3 coordinator that:
    • Accepts ANY L1 plan (strategy, rag, bullets, drafting, qa, safety)
    • Chooses the correct domain orchestrator for that plan
    • Applies top-level phase transitions via ControlFlow
    • Returns a WorkflowState for integration by L4

Domain orchestrators:
    rag     → RAGOrchestrator
    bullets → BulletOrchestrator
    drafting→ DraftOrchestrator
    strategy→ StrategyOrchestrator
    qa      → QAOrchestrator
    safety  → SafetyOrchestrator
"""

from __future__ import annotations
from typing import Any, Dict

from shared.models import PlanObject, WorkflowState, PhaseMetadata
from shared.constants import WorkflowPhase
from shared.exceptions import OrchestrationError

from l3.control_flow import ControlFlow

# Domain orchestrators
from l3.rag_orchestrator import RAGOrchestrator
from l3.bullet_orchestrator import BulletOrchestrator
from l3.draft_orchestrator import DraftOrchestrator
from l3.strategy_orchestrator import StrategyOrchestrator
from l3.qa_orchestrator import QAOrchestrator
from l3.safety_orchestrator import SafetyOrchestrator


class Orchestrator:
    """Global L3 workflow orchestrator."""

    def __init__(self) -> None:
        self.cf = ControlFlow()

        # Instantiate domain orchestrators
        self._rag = RAGOrchestrator()
        self._bullets = BulletOrchestrator()
        self._draft = DraftOrchestrator()
        self._strategy = StrategyOrchestrator()
        self._qa = QAOrchestrator()
        self._safety = SafetyOrchestrator()

    async def run(self, plan: PlanObject, state: Dict[str, Any]) -> WorkflowState:
        """
        Routes the plan to the correct domain orchestrator based on plan.mode.

        Steps:
            1. INIT → PLANNING
            2. Route based on plan.mode
            3. Execute domain orchestration
            4. REVIEWING → COMPLETE
        """
        try:
            # INIT → PLANNING
            phase_plan = self.cf.next_phase("init")

            mode = (plan.mode or "").lower()

            # Domain routing
            if mode == "rag":
                result = await self._rag.run(plan, state)
            elif mode == "bullets":
                result = await self._bullets.run(plan, state)
            elif mode == "drafting":
                result = await self._draft.run(plan, state)
            elif mode == "strategy":
                result = await self._strategy.run(plan, state)
            elif mode == "qa":
                result = await self._qa.run(plan, state)
            elif mode == "safety":
                result = await self._safety.run(plan, state)
            else:
                raise OrchestrationError(f"Unsupported plan mode: {mode}")

            # REVIEWING → COMPLETE
            phase_complete = self.cf.next_phase("reviewing")

            fin_state = dict(result.state)
            fin_state["phase"] = phase_complete.value

            return WorkflowState(
                workflow_id=fin_state.get("workflow_id", "unknown"),
                phase=phase_complete,
                nodes=result.nodes,
                state=fin_state,
                phase_metadata=PhaseMetadata(
                    phase=phase_complete,
                    note="Global orchestration cycle complete."
                ),
            )

        except Exception as exc:
            raise OrchestrationError(f"Global Orchestrator failed: {exc}") from exc

