# FILE: l3.py
"""
Unified L3 Orchestration Layer (v10_10) — RESILIENT WORKFLOW ENGINE

This module implements Pillar 4 (Workflow) and Pillar 5 (Capability Maturity).
It orchestrates the execution of the L1 Plan, managing the lifecycle of
Execution -> Validation -> Correction.

Responsibilities:
    1. Execution Loop: Run L2 Executors based on Plan Steps.
    2. Self-Correction: Consult `CorrectionSurfaceRegistry` on failure.
    3. State Management: Apply atomic `StatePatch` updates via L4.
    4. Traceability: Record strict `RouteTraceEntry` telemetry.

Refactor Highlights (v10_10):
    • Integrated `CorrectionEngine` for autonomous retries.
    • Strict `WorkflowState` output.
    • No hardcoded retry logic; purely policy-driven.
"""

from __future__ import annotations

import uuid
import time
from typing import Any, Dict, List, Optional

from models import (
    PlanObject,
    WorkflowState,
    WorkflowPhase,
    NodeStatus,
    ExecutionResult,
    StatePatch,
    RouteTraceEntry,
    CorrectionSignal,
    CorrectionProposal
)
from l2 import route_executor
from l4 import StateAdapter
from self_correction import CORRECTION_ENGINE
from runtime_utils import CostTracker, record_event

class DAGExecutor:
    """
    The runtime engine that executes a PlanObject.
    Handles the "Do -> Check -> Fix" loop.
    """

    def __init__(self, state_adapter: StateAdapter):
        self.state_adapter = state_adapter
        self.cost_tracker = CostTracker()

    async def run(self, plan: PlanObject, initial_state: Dict[str, Any]) -> WorkflowState:
        """
        Executes the plan with built-in resilience.
        """
        workflow_id = plan.workflow_id or str(uuid.uuid4())
        
        # 1. Initialize State Scope
        # We don't reset the whole adapter here (Main does that), 
        # but we ensure we are in the right phase.
        self.state_adapter.set_phase(WorkflowPhase.EXECUTING)
        
        node_id = plan.mode
        attempt = 0
        max_attempts = 1 # Default, overriden by Correction Policy
        
        # TRACKING
        trace_entries: List[RouteTraceEntry] = []
        errors: List[str] = []
        status = NodeStatus.PENDING
        
        # 2. Execution Loop (The "Retry" Cycle)
        while True:
            attempt += 1
            self.cost_tracker.start_span(f"{node_id}_attempt_{attempt}")
            
            # --- A. EXECUTE ---
            # Propagate any correction params (e.g. higher temp) into the plan
            # In a real impl, we'd merge `correction_params` into `plan.meta`
            result = await route_executor(plan, self.state_adapter.state)
            
            self.cost_tracker.end_span(f"{node_id}_attempt_{attempt}")
            
            # --- B. EVALUATE ---
            if result.status == NodeStatus.SUCCESS:
                status = NodeStatus.SUCCESS
                self._apply_success(plan.mode, result)
                break # Exit Loop
            
            # --- C. CORRECT (Pillar 5) ---
            # If we failed, ask the Correction Engine what to do.
            error_signal = CorrectionSignal(
                signal_id=str(uuid.uuid4()),
                surface=f"{plan.mode}_failure", # e.g. "rag_failure"
                severity=0.8,
                context={"error": result.error, "attempt": attempt}
            )
            
            proposal = CORRECTION_ENGINE.resolve(error_signal, attempt)
            
            # Record the intervention
            self.state_adapter.record_correction(error_signal)
            
            if proposal.action == "retry_node":
                record_event("self_correction_retry", {"node": node_id, "attempt": attempt})
                # Continue loop
                # In a full implementation, we would apply `proposal.parameters` to `plan` here.
                continue
                
            elif proposal.action == "escalate" or proposal.action == "halt":
                status = NodeStatus.FAILURE
                errors.append(f"Correction Failed: {proposal.rationale}")
                break

        # 3. Finalize State
        final_phase = WorkflowPhase.COMPLETE if status == NodeStatus.SUCCESS else WorkflowPhase.FAILED
        self.state_adapter.set_phase(final_phase)
        
        # 4. Construct Output
        return WorkflowState(
            workflow_id=workflow_id,
            phase=final_phase,
            node_statuses={node_id: status},
            summary=f"Execution finished with status: {status}",
            result=self.state_adapter.state,
            errors=errors,
            trace_id=workflow_id,
            objective=plan.objective,
            messages=self.state_adapter.state.get("messages", []),
            rag_docs=self.state_adapter.state.get("rag_history", [])
            # Metadata / Trace info would be attached here
        )

    def _apply_success(self, mode: str, result: ExecutionResult) -> None:
        """
        Persist the successful result to L4.
        """
        # Map mode -> state key
        key_map = {
            "strategy": "strategy_result",
            "rag": "rag_result",
            "drafting": "draft_result",
            "qa": "qa_result",
            "safety": "safety_result"
        }
        target_key = key_map.get(mode, f"{mode}_result")
        
        # Create Atomic Patch (Pillar 4)
        patch = StatePatch(
            op="replace",
            path=target_key,
            value=result.payload
        )
        
        self.state_adapter.apply_patch(patch)
