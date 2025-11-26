"""
L3 QA orchestrator for resume job alignment workflows.

Coordinates QA planning and execution for resume enhancement.
"""

from typing import Any
from l1.qa_planning import plan_qa
from l2.qa_executor import QAExecutor
from runtime.observability import record_event

class QAOrchestrator:
    """Pure orchestration for resume QA job alignment workflows."""
    
    def __init__(self, qa_executor: QAExecutor):
        self.qa_executor = qa_executor
    
    def orchestrate_qa(self, draft: Any, job: Any, resume: Any) -> str:
        """Orchestrates resume QA workflow for job alignment processing."""
        record_event("qa_orchestration_start", {})
        
        # L1: Pure planning
        qa_plan = plan_qa(draft, job, resume)
        
        # L2: Pure execution
        result = self.qa_executor.execute_qa(
            f"Execute QA for areas: {qa_plan.focus_areas}"
        )
        
        record_event("qa_orchestration_complete", {})
        return result
