"""L1 Prompt Builder - Pure prompt building logic only."""

from typing import Any

class PromptBuilder:
    """Pure prompt building - no execution, no orchestration logic."""
    
    @staticmethod
    def build_strategy_prompt(strategy_plan: Any, job: Any, resume: Any, config: Any) -> str:
        """Build strategy prompt - pure string construction only."""
        return f"Strategy planning for job: {job}, resume: {resume}"
    
    @staticmethod
    def build_draft_prompt(draft_plan: Any, job: Any, resume: Any, config: Any) -> str:
        """Build draft prompt - pure string construction only."""
        return f"Draft planning for sections: {draft_plan.sections}"
    
    @staticmethod
    def build_qa_prompt(qa_plan: Any, draft: Any, job: Any, resume: Any) -> str:
        """Build QA prompt - pure string construction only."""
        return f"QA analysis for draft: {draft}"
    
    @staticmethod
    def build_safety_prompt(safety_plan: Any, draft: Any, job: Any, resume: Any) -> str:
        """Build safety prompt - pure string construction only."""
        return f"Safety review for content: {draft}"
