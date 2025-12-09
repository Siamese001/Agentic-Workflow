"""Deterministic Level-1 planner for RAG orchestration."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from core_v10_7 import BaseAgent, RAGPlan

from .planning_utils import describe_experience, extract_job_profile, extract_resume_profile


class RAGPlanningStack(BaseAgent):
    """Produces a lightweight retrieval plan without calling any tools."""

    def __init__(self, context: Any, debug_mode: bool = False) -> None:
        super().__init__(context, debug_mode)

    async def run_async(
        self, state: Dict[str, Any], workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        plan = self._build_plan(state)
        return {"rag": {"plan": plan.model_dump()}}

    def _build_plan(self, state: Dict[str, Any]) -> RAGPlan:
        job_profile = extract_job_profile(state)
        resume_profile = extract_resume_profile(state)
        experiences = resume_profile["experiences"]
        requirements = job_profile["requirements"]
        workflow_goal = self._goal_statement(job_profile)
        context_inputs = self._context_inputs(job_profile, resume_profile)
        retrieval_queries = self._queries(job_profile, experiences, requirements)
        prioritization = self._prioritization(requirements, experiences)
        risk_checks = self._risk_checks(requirements)
        return RAGPlan(
            goal=workflow_goal,
            context_inputs=context_inputs,
            retrieval_queries=retrieval_queries,
            prioritization=prioritization,
            risk_checks=risk_checks,
        )

    def _goal_statement(self, job_profile: Dict[str, Any]) -> str:
        title = job_profile["title"]
        company = job_profile["company"]
        if title and company:
            return f"Surface evidence that proves readiness for {title} at {company}"
        if title:
            return f"Surface evidence tailored to the {title} mandate"
        return "Surface evidence aligned to the target role"

    def _context_inputs(
        self, job_profile: Dict[str, Any], resume_profile: Dict[str, Any]
    ) -> List[str]:
        inputs: List[str] = []
        if job_profile["summary"]:
            inputs.append("job.description")
        if job_profile["requirements"]:
            inputs.append("job.requirements")
        if resume_profile["summary"]:
            inputs.append("resume.summary")
        if resume_profile["experiences"]:
            inputs.append("resume.professional_experience")
        metadata = self.context.prompt_manager.goal_state if self.context else {}
        if metadata:
            inputs.append("prompt.goal_state")
        return inputs

    def _queries(
        self,
        job_profile: Dict[str, Any],
        experiences: List[Dict[str, Any]],
        requirements: List[str],
    ) -> List[str]:
        queries: List[str] = []
        base_role = job_profile["title"] or "target role"
        company = job_profile["company"]
        keyword_suffix = (
            " ".join(requirements[:2]) if requirements else "impact metrics"
        )
        queries.append(f"{base_role} {company} {keyword_suffix}".strip())
        if experiences:
            queries.append(
                f"{describe_experience(experiences[0])} supporting evidence for {base_role}"
            )
        if len(experiences) > 1:
            queries.append(
                f"Leadership examples from {describe_experience(experiences[1])}"
            )
        return [query for query in queries if query]

    def _prioritization(
        self,
        requirements: List[str],
        experiences: List[Dict[str, Any]],
    ) -> List[str]:
        prioritization: List[str] = []
        if requirements:
            prioritization.append(
                f"Match JD keywords first: {', '.join(requirements[:3])}"
            )
        if experiences:
            prioritization.append("Favor most recent quantified roles")
        prioritization.append("Deduplicate overlapping bullets before ranking")
        return prioritization

    def _risk_checks(self, requirements: List[str]) -> List[str]:
        checks = [
            "Verify every plan output references an original resume source",
            "Ensure at least one leadership and one technical example",
        ]
        if requirements:
            checks.append("Confirm each top JD requirement is backed by evidence")
        return checks
