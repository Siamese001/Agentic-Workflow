"""L3 Safety Orchestrator - Pure orchestration only."""

from typing import Any
from archives.legacy_resume_gen.Agentic_Workflow-10_10.l1.safety_planning import plan_safety
from archives.legacy_resume_gen.Agentic_Workflow-10_10.l2.safety_executor import SafetyExecutor
from archives.legacy_resume_gen.Agentic_Workflow-10_10.tests.sandbox.test_sandbox_observability import record_event

class SafetyOrchestrator:
    """Pure orchestration - no planning, no execution logic."""
    
    def __init__(self, safety_executor: SafetyExecutor):
        self.safety_executor = safety_executor
    
    def orchestrate_safety(self, draft: Any, job: Any, resume: Any) -> str:
        """Orchestrate safety workflow - pure control flow only."""
        record_event("safety_orchestration_start", {})
        
        # L1: Pure planning
        safety_plan = plan_safety(draft, job, resume)
        
        # L2: Pure execution
        result = self.safety_executor.execute_safety(
            f"Execute safety for rules: {safety_plan.policy_rules}"
        )
        
        record_event("safety_orchestration_complete", {})
        return result
