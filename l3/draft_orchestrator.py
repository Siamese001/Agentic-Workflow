"""
L3 orchestration layer for résumé drafting workflow.

Coordinates planning and execution to create comprehensive résumé improvements.
"""

from typing import Any
from l1.draft_planning import plan_drafting
from l2.draft_executor import DraftExecutor
from runtime.observability import record_event

class DraftOrchestrator:
    """
    Coordinates résumé drafting workflow across all layers.

    Ensures systematic integration of planning and execution for optimal résumé enhancement.
    """
    
    def __init__(self, draft_executor: DraftExecutor):
        self.draft_executor = draft_executor
    
    def orchestrate_draft(self, strategy_result: Any, job: Any, resume: Any) -> str:
        """
        Orchestrates complete résumé drafting workflow.

        Integrates planning and execution to generate tailored résumé content aligned with job requirements.
        """
        record_event("draft_orchestration_start", {})
        
        # L1: Pure planning
        draft_plan = plan_drafting(strategy_result, job, resume)
        
        # L2: Pure execution
        result = self.draft_executor.execute_draft(
            f"Execute draft for sections: {draft_plan.sections}"
        )
        
        record_event("draft_orchestration_complete", {})
        return result
