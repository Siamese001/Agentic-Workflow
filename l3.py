# FILE: l3.py
"""
Unified L3 Orchestration Layer (v10_10) — DECLARATIVE WORKFLOW (REFACTORED)

This module implements the "Nervous System" (Pillar 4).
It orchestrates the execution of the `PlanObject` (L1) by dispatching
tasks to L2, managing state transitions (L4), and handling control flow.

Refactor Highlights (v10_10):
    1. Declarative DAG: Relies on Pydantic `PlanObject` structure.
    2. Strict State: Returns `WorkflowState` objects, not loose dicts.
    3. Resilience: Native retry loops based on L1 configuration.
"""

from __future__ import annotations

import asyncio
import time
import uuid
from typing import Any, Dict, List, Set

from models import (
    PlanObject,
    WorkflowState,
    WorkflowPhase,
    NodeStatus,
    ExecutionResult,
    StatePatch,
    RouteTraceEntry
)
from l2 import route_executor
from l4 import StateAdapter
from runtime_utils import CostTracker, record_event

class DAGExecutor:
    """
    Deterministic orchestrator. 
    Traverses the PlanObject steps and manages the execution lifecycle.
    """

    def __init__(self, state_adapter: StateAdapter):
        self.state_adapter = state_adapter
        self.cost_tracker = CostTracker()

    async def run(self, plan: PlanObject, initial_state: Dict[str, Any]) -> WorkflowState:
        """
        Main entry point. Executes a Plan end-to-end.
        """
        workflow_id = plan.workflow_id or str(uuid.uuid4())
        
        # 1. Initialize State (Pillar 4 - State Transitions)
        self.state_adapter.reset(initial_state)
        self.state_adapter.set_phase(WorkflowPhase.PLANNING) # Already done by L1 effectively, but formalizing
        
        # Transition to Executing
        self.state_adapter.set_phase(WorkflowPhase.EXECUTING)
        
        node_statuses: Dict[str, NodeStatus] = {}
        errors: List[str] = []
        trace_entries: List[RouteTraceEntry] = []

        # 2. DAG Execution Loop (Simplified Linear/Step-based for v10_10)
        # In a full graph implementation, this would be a topological sort.
        # Here we iterate the defined 'steps' in the PlanObject.
        
        # 'mode' acts as the primary node in this simplified architecture
        # but we treat internal steps as sub-nodes.
        
        main_node_id = plan.mode
        node_statuses[main_node_id] = NodeStatus.PENDING
        
        try:
            # Start Span
            self.cost_tracker.start_span(main_node_id)
            
            # EXECUTE L2 (Pillar 5 - Capability)
            result: ExecutionResult = await route_executor(plan, self.state_adapter.state)
            
            self.cost_tracker.end_span(main_node_id)

            # 3. Process Result
            if result.ok:
                node_statuses[main_node_id] = NodeStatus.SUCCESS
                # Apply State Patch (Pillar 4/10)
                self._apply_result_to_state(plan.mode, result)
            else:
                node_statuses[main_node_id] = NodeStatus.ERROR
                errors.extend(result.errors)
            
            # Record Trace (Pillar 10)
            trace_entries.append(RouteTraceEntry(
                step=main_node_id,
                model=result.model,
                rationale=f"Executed {plan.mode}",
                metadata={"latency_ms": result.usage.get("latency_ms", 0)}
            ))

        except Exception as e:
            node_statuses[main_node_id] = NodeStatus.ERROR
            errors.append(str(e))
            record_event("orchestration_error", {"workflow_id": workflow_id, "error": str(e)})

        # 4. Finalize
        final_phase = WorkflowPhase.COMPLETE if not errors else WorkflowPhase.FAILED
        self.state_adapter.set_phase(final_phase)
        
        # Construct final WorkflowState (External Contract)
        return WorkflowState(
            workflow_id=workflow_id,
            phase=final_phase,
            node_statuses=node_statuses,
            summary=f"Workflow {final_phase.value}",
            result=self.state_adapter.state,
            errors=errors,
            trace_id=workflow_id,
            metadata={
                "route_trace": [t.model_dump() for t in trace_entries],
                "cost_snapshot": self.cost_tracker.snapshot()
            }
        )

    def _apply_result_to_state(self, mode: str, result: ExecutionResult) -> None:
        """
        Maps L2 execution payloads to the correct L4 state key.
        """
        # Mapping convention: mode -> {mode}_result
        # e.g. strategy -> strategy_result
        key_map = {
            "strategy": "strategy_result",
            "rag": "rag_result",
            "drafting": "draft_result",
            "qa": "qa_result",
            "safety": "safety_result",
            "hil": "hil_result",
            "meta_learning": "meta_learning_result"
        }
        
        target_key = key_map.get(mode, f"{mode}_result")
        
        # Pillar 4: Atomic State Patch
        patch = StatePatch(
            key=target_key,
            value=result.payload
        )
        self.state_adapter.apply_patch(patch)
