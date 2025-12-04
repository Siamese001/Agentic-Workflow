"""
L3 unified workflow orchestrator for resume job alignment.

Coordinates all atomic layers for resume processing workflows.
"""

from typing import Any, Dict, Protocol
from l1.strategy_planning import plan_strategy
from l1.draft_planning import plan_drafting
from l1.qa_planning import plan_qa
from l1.safety_planning import plan_safety
from l1.result_parser import ResultParser
from l2.llm_caller import LLMCaller
from l2.strategy_executor import StrategyExecutor
from l2.draft_executor import DraftExecutor
from l2.qa_executor import QAExecutor
from l2.safety_executor import SafetyExecutor
from l3.strategy_orchestrator import StrategyOrchestrator
from l3.draft_orchestrator import DraftOrchestrator
from l3.qa_orchestrator import QAOrchestrator
from l3.safety_orchestrator import SafetyOrchestrator
from runtime.observability import record_event

# Protocol interfaces for L4/L5 dependency injection
class StateManagerInterface(Protocol):
    def save_state(self, state: Any) -> None: ...
    def load_state(self) -> Any: ...

class SafetyValidatorInterface(Protocol):
    def is_safe(self, content: str) -> bool: ...
    def validate_content(self, content: str) -> list: ...

class UnifiedWorkflowOrchestrator:
    """Pure orchestration for resume job alignment layer coordination."""
    
    def __init__(self, routing_policy: Any, sandbox: Any, state_manager: StateManagerInterface, safety_validator: SafetyValidatorInterface, meta_profile: Any = None):
        # L2: Pure execution components
        self.llm_caller = LLMCaller(routing_policy, sandbox, meta_profile)
        self.strategy_executor = StrategyExecutor(routing_policy, sandbox, meta_profile)
        self.draft_executor = DraftExecutor(routing_policy, sandbox, meta_profile)
        self.qa_executor = QAExecutor(routing_policy, sandbox, meta_profile)
        self.safety_executor = SafetyExecutor(routing_policy, sandbox, meta_profile)
        
        # L3: Pure orchestration components
        self.strategy_orchestrator = StrategyOrchestrator(self.strategy_executor)
        self.draft_orchestrator = DraftOrchestrator(self.draft_executor)
        self.qa_orchestrator = QAOrchestrator(self.qa_executor)
        self.safety_orchestrator = SafetyOrchestrator(self.safety_executor)
        
        # L4/L5: Injected dependencies (no direct imports)
        self.state_manager = state_manager
        self.safety_validator = safety_validator
    
    def orchestrate_full_workflow(self, job: Any, resume: Any, config: Any) -> Dict[str, Any]:
        """Orchestrates complete resume workflow for job alignment processing."""
        record_event("full_workflow_start", {})
        
        # Strategy Phase
        plan_strategy(job, resume, config)  # L1: Pure planning
        strategy_result = self.strategy_orchestrator.orchestrate_strategy(job, resume, config)
        parsed_strategy = ResultParser().parse_strategy_result(strategy_result)
        
        # Draft Phase
        plan_drafting(parsed_strategy, job, resume)  # L1: Pure planning
        draft_result = self.draft_orchestrator.orchestrate_draft(parsed_strategy, job, resume)
        parsed_draft = ResultParser().parse_draft_result(draft_result)
        
        # QA Phase
        plan_qa(parsed_draft, job, resume)  # L1: Pure planning
        qa_result = self.qa_orchestrator.orchestrate_qa(parsed_draft, job, resume)
        parsed_qa = ResultParser().parse_qa_result(qa_result)
        
        # Safety Phase
        plan_safety(parsed_draft, job, resume)  # L1: Pure planning
        safety_result = self.safety_orchestrator.orchestrate_safety(parsed_draft, job, resume)
        parsed_safety = ResultParser().parse_safety_result(safety_result)
        
        # L4: State persistence (via injected dependency)
        workflow_state = {
            "job_data": {"title": getattr(job, "title", "")},
            "resume_data": {"summary": getattr(resume, "summary", "")},
            "strategy_result": parsed_strategy.strategy,
            "draft_result": parsed_draft.content,
            "metadata": {"workflow_complete": True}
        }
        self.state_manager.save_state(workflow_state)
        
        # L5: Final safety validation (via injected dependency)
        final_content = parsed_draft.content
        if not self.safety_validator.is_safe(final_content):
            violations = self.safety_validator.validate_content(final_content)
            raise ValueError(f"Content failed safety validation: {violations}")
        
        record_event("full_workflow_complete", {})
        
        return {
            "strategy": parsed_strategy,
            "draft": parsed_draft,
            "qa": parsed_qa,
            "safety": parsed_safety,
            "state": workflow_state
        }
