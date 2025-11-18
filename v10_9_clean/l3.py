# FILE: v10_9_clean/l3.py
"""
Unified L3 Orchestration Layer (v10_9)

This module combines ALL L3 responsibilities:

    • ControlFlow (phase transitions)
    • Workflow contracts
    • Domain orchestrators:
         - StrategyOrchestrator
         - RAGOrchestrator
         - BulletOrchestrator
         - DraftOrchestrator
         - QAOrchestrator
         - SafetyOrchestrator
    • Global Orchestrator:
         - routes any L1 plan to correct domain orchestrator
         - manages cross-plan transitions (INIT → PLANNING → EXECUTING → REVIEWING → COMPLETE)

Pure orchestration only:
    • NO planning (L1)
    • NO execution (L2)
    • NO state mutation (L4)
"""

from __future__ import annotations
from typing import Any, Dict, Optional
from dataclasses import dataclass

from models import WorkflowState, PhaseMetadata, PlanObject, ExecutionResult
from exceptions import OrchestrationError
from constants import WorkflowPhase
from l2 import (
    execute_strategy,
    execute_rag,
    execute_bullets,
    execute_drafting,
    execute_qa,
    execute_safety,
)


# ============================================================================
# CONTROL FLOW (Phase Machine)
# ============================================================================

class ControlFlow:
    """
    Handles phase transitions for L3 orchestration.
    """

    _allowed = {
        "init": ["planning", "failed"],
        "planning": ["executing", "failed"],
        "executing": ["reviewing", "failed"],
        "reviewing": ["complete", "planning", "failed"],
        "complete": [],
        "failed": [],
    }

    def __init__(self) -> None:
        self.current = "init"

    def next_phase(self, target: str) -> WorkflowPhase:
        target = target.lower()
        if target not in self._allowed.get(self.current, []):
            raise OrchestrationError(f"Illegal phase transition: {self.current} → {target}")
        self.current = target
        return WorkflowPhase(target)


# ============================================================================
# WORKFLOW CONTRACTS
# ============================================================================

@dataclass
class WorkflowStepResult:
    phase: WorkflowPhase
    state: Dict[str, Any]
    note: str = ""


# ============================================================================
# DOMAIN ORCHESTRATORS
# ============================================================================

class StrategyOrchestrator:
    async def run(self, plan: PlanObject, state: Dict[str, Any]) -> WorkflowState:
        cf = ControlFlow()
        cf.next_phase("planning")
        result: ExecutionResult = await execute_strategy(plan, state)
        cf.next_phase("reviewing")

        new_state = dict(state)
        new_state["strategy_result"] = result.payload

        return WorkflowState(
            workflow_id=new_state.get("workflow_id", "unknown"),
            phase=cf.next_phase("complete"),
            nodes={},
            state=new_state,
            phase_metadata=PhaseMetadata(phase=WorkflowPhase.COMPLETE, note="Strategy done"),
        )


class RAGOrchestrator:
    async def run(self, plan: PlanObject, state: Dict[str, Any]) -> WorkflowState:
        cf = ControlFlow()
        cf.next_phase("planning")
        result = await execute_rag(plan, state)
        cf.next_phase("reviewing")

        new_state = dict(state)
        new_state["rag_result"] = result.payload

        return WorkflowState(
            workflow_id=new_state.get("workflow_id", "unknown"),
            phase=cf.next_phase("complete"),
            nodes={},
            state=new_state,
            phase_metadata=PhaseMetadata(phase=WorkflowPhase.COMPLETE, note="RAG done"),
        )


class BulletOrchestrator:
    async def run(self, plan: PlanObject, state: Dict[str, Any]) -> WorkflowState:
        cf = ControlFlow()
        cf.next_phase("planning")
        result = await execute_bullets(plan, state)
        cf.next_phase("reviewing")

        new_state = dict(state)
        new_state["bullet_result"] = result.payload

        return WorkflowState(
            workflow_id=new_state.get("workflow_id", "unknown"),
            phase=cf.next_phase("complete"),
            nodes={},
            state=new_state,
            phase_metadata=PhaseMetadata(phase=WorkflowPhase.COMPLETE, note="Bullets done"),
        )


class DraftOrchestrator:
    async def run(self, plan: PlanObject, state: Dict[str, Any]) -> WorkflowState:
        cf = ControlFlow()
        cf.next_phase("planning")
        result = await execute_drafting(plan, state)
        cf.next_phase("reviewing")

        new_state = dict(state)
        new_state["draft_result"] = result.payload

        return WorkflowState(
            workflow_id=new_state.get("workflow_id", "unknown"),
            phase=cf.next_phase("complete"),
            nodes={},
            state=new_state,
            phase_metadata=PhaseMetadata(phase=WorkflowPhase.COMPLETE, note="Draft done"),
        )


class QAOrchestrator:
    async def run(self, plan: PlanObject, state: Dict[str, Any]) -> WorkflowState:
        cf = ControlFlow()
        cf.next_phase("planning")
        result = await execute_qa(plan, state)
        cf.next_phase("reviewing")

        new_state = dict(state)
        new_state["qa_result"] = result.payload

        return WorkflowState(
            workflow_id=new_state.get("workflow_id", "unknown"),
            phase=cf.next_phase("complete"),
            nodes={},
            state=new_state,
            phase_metadata=PhaseMetadata(phase=WorkflowPhase.COMPLETE, note="QA done"),
        )


class SafetyOrchestrator:
    async def run(self, plan: PlanObject, state: Dict[str, Any]) -> WorkflowState:
        cf = ControlFlow()
        cf.next_phase("planning")
        result = await execute_safety(plan, state)
        cf.next_phase("reviewing")

        new_state = dict(state)
        new_state["safety_result"] = result.payload

        return WorkflowState(
            workflow_id=new_state.get("workflow_id", "unknown"),
            phase=cf.next_phase("complete"),
            nodes={},
            state=new_state,
            phase_metadata=PhaseMetadata(phase=WorkflowPhase.COMPLETE, note="Safety done"),
        )


# ============================================================================
# GLOBAL L3 ORCHESTRATOR
# ============================================================================

class Orchestrator:
    """
    Routes ANY PlanObject (from L1) to the correct domain orchestrator.
    """

    def __init__(self) -> None:
        self._map = {
            "strategy": StrategyOrchestrator(),
            "rag": RAGOrchestrator(),
            "bullets": BulletOrchestrator(),
            "drafting": DraftOrchestrator(),
            "qa": QAOrchestrator(),
            "safety": SafetyOrchestrator(),
        }

    async def run(self, plan: PlanObject, state: Dict[str, Any]) -> WorkflowState:
        mode = (plan.mode or "").lower()
        if mode not in self._map:
            raise OrchestrationError(f"Unsupported L1 plan mode: {mode}")

        orchestrator = self._map[mode]
        return await orchestrator.run(plan, state)
