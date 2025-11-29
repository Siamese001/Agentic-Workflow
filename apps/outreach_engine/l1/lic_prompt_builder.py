"""
L1 Prompt Builder for resume generation prompt construction.

Creates structured prompts for consistent resume improvement
and optimal job alignment.
"""

from typing import Any

class PromptBuilder:
    """
    Builds prompts for resume generation without execution logic.

    Ensures consistent prompt structure for improved resume
    quality and job alignment.
    """
    
    @staticmethod
    def build_strategy_prompt(strategy_plan: Any, job: Any, resume: Any, config: Any) -> str:
        """Builds strategy prompt for resume improvement planning.

        Creates structured approach for optimal resume job alignment.
        """
        return f"Strategy planning for job: {job}, resume: {resume}"
    
    @staticmethod
    def build_draft_prompt(draft_plan: Any, job: Any, resume: Any, config: Any) -> str:
        """Builds draft prompt for resume content creation.

        Structures approach for professional resume enhancement.
        """
        return f"Draft planning for sections: {draft_plan.sections}"
    
    @staticmethod
    def build_qa_prompt(qa_plan: Any, draft: Any, job: Any, resume: Any) -> str:
        """Builds QA prompt for resume quality validation.

        Ensures thorough evaluation for resume accuracy.
        """
        return f"QA analysis for draft: {draft}"
    
    @staticmethod
    def build_safety_prompt(safety_plan: Any, draft: Any, job: Any, resume: Any) -> str:
        """Builds safety prompt for resume compliance checking.

        Ensures professional standards in resume content.
        """
        return f"Safety review for content: {draft}"
