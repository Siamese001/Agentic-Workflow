# FILE: main_v10_10.py
"""
Unified Entry Point (v10_10) — MASTER ORCHESTRATOR (REFACTORED)

This module runs the Agentic Workflow (Pillar 4).
It coordinates the lifecycle: Planning (L1) → Execution (L3) → Governance (L5).

Refactor Highlights (v10_10):
    • Dynamic Pipeline: Re-plans at every stage based on new state.
    • Strict Contracts: Only accepts/returns Pydantic models.
    • Meta-Aware: Injects Observability and Biases into the loop.
"""

from __future__ import annotations

import asyncio
import uuid
from typing import Any, Dict, List, Optional

from models import (
    WorkflowState,
    WorkflowPhase,
    ArbitrationDecision,
    SafetyReport
)
from l1 import PLANNER
from l3 import DAGExecutor
from l4 import StateAdapter
from l5 import SafetyEngine, PolicyEngine, ArbitrationEngine
from observability import summarize_run, trace_span_async
from registry import initialize_registry

# Initialize Governance Layer (Pillar 13)
initialize_registry()

class AgenticWorkflow:
    """
    The runtime engine that drives the agent.
    """

    def __init__(self):
        # L4 State Manager
        self.state_adapter = StateAdapter()
        
        # L3 Executor
        self.dag_executor = DAGExecutor(self.state_adapter)
        
        # L5 Governance
        self.safety_engine = SafetyEngine()
        self.policy_engine = PolicyEngine()
        self.arbitration_engine = ArbitrationEngine()

    @trace_span_async("workflow_execution")
    async def run(self, initial_state: Dict[str, Any]) -> WorkflowState:
        """
        Executes the full cognitive loop.
        """
        workflow_id = str(initial_state.get("workflow_id", uuid.uuid4()))
        
        # 1. Initialize Memory (Pillar 7)
        self.state_adapter.reset(initial_state)
        
        # 2. Define The Macro-Pipeline
        # In a fully autonomous agent, L1 would decide this list.
        # For v10_10 stability, we define the standard "Golden Path".
        pipeline_phases = ["strategy", "rag", "drafting", "qa", "safety"]
        
        phase_history = []
        current_state = self.state_adapter.state

        for mode in pipeline_phases:
            # --- A. COGNITION (L1) ---
            # Ask the Brain: "Given current state, what is the plan for 'mode'?"
            plan = await PLANNER.plan(
                mode=mode,
                state=current_state,
                workflow_id=workflow_id
            )
            
            # --- B. ACTION (L3) ---
            # Do the Work: Execute the strict PlanObject
            workflow_state = await self.dag_executor.run(plan, current_state)
            
            # Update local tracking
            current_state = workflow_state.result
            phase_history.append(mode)
            
            # If execution failed, we stop (Pillar 8: Fail Fast)
            # In a smarter agent, we would loop back to L1 for "Recovery"
            if workflow_state.phase == WorkflowPhase.FAILED:
                return workflow_state

        # 3. GOVERNANCE (L5)
        # The Conscience Check: "Is the final result safe?"
        # We re-use the plan from the last phase for context
        safety_report = await self.safety_engine.evaluate_content(current_state, plan)
        policy_decision = self.policy_engine.review(safety_report)
        arbitration = self.arbitration_engine.arbitrate(policy_decision, safety_report)
        
        # Inject Final Governance Result into State
        self.state_adapter.apply_patch({
            "key": "governance_result", 
            "value": arbitration.model_dump()
        })

        # 4. OBSERVABILITY (Pillar 10)
        # Generate Golden Record
        run_summary = summarize_run(
            workflow_id=workflow_id,
            final_state=self.state_adapter.state,
            phase_history=phase_history
        )

        # 5. Final State Return
        return WorkflowState(
            workflow_id=workflow_id,
            phase=WorkflowPhase.COMPLETE,
            node_statuses={}, # Detailed node stats in summary
            summary="Workflow Completed Successfully",
            result=self.state_adapter.state,
            errors=[],
            metadata={"run_summary": run_summary.model_dump()}
        )

# =============================================================================
# CLI / ENTRYPOINT
# =============================================================================

async def run_workflow_v10_10(initial_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Public API for running the agent.
    """
    engine = AgenticWorkflow()
    final_state_obj = await engine.run(initial_state)
    return final_state_obj.model_dump()

if __name__ == "__main__":
    # Smoke Test
    test_state = {
        "objective": "Draft a strategic memo about AI adoption.",
        "messages": [{"role": "user", "content": "We need an AI strategy."}]
    }
    result = asyncio.run(run_workflow_v10_10(test_state))
    print(f"Workflow ID: {result['workflow_id']}")
    print(f"Status: {result['summary']}")
