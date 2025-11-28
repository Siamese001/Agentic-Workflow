"""
L3 safety orchestrator for resume job alignment workflows.

Coordinates safety planning and execution for resume enhancement.
"""

from typing import Any
from l1.safety_planning import plan_safety
from l2.safety_executor import SafetyExecutor
from runtime.observability import record_event

class SafetyOrchestrator:
    """Pure orchestration for resume safety job alignment workflows."""
    
    def __init__(self, safety_executor: SafetyExecutor):
        self.safety_executor = safety_executor
    
    def orchestrate_safety(self, draft: Any, job: Any, resume: Any) -> str:
        """Orchestrates resume safety workflow for job alignment processing."""
        record_event("safety_orchestration_start", {})
        
        # L1: Pure planning
        safety_plan = plan_safety(draft, job, resume)
        
        # L2: Pure execution
        result = self.safety_executor.execute_safety(
            f"Execute safety for rules: {safety_plan.policy_rules}"
        )
        
        record_event("safety_orchestration_complete", {})
        return result
