"""L1 RAG planning stack."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from bullet_planning import extract_job_profile, extract_resume_profile


def describe_experience(resume_profile: Dict[str, Any]) -> List[str]:
    experiences = []
    for item in resume_profile.get("experience", []) if isinstance(resume_profile, dict) else []:
        if isinstance(item, dict):
            title = item.get("title") or item.get("role") or "Experience"
            desc = item.get("description") or ""
            experiences.append(f"{title}: {desc}")
    return experiences


class RAGPlan(BaseModel):
    goal: str = "Retrieve evidence to strengthen bullets."
    context_inputs: List[str] = []
    retrieval_queries: List[str] = []
    prioritization: str = "hybrid"
    risk_checks: List[str] = []


class RAGPlanningStack:
    async def run_async(
        self, state: Dict[str, Any], workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        job_profile = extract_job_profile(state)
        resume_profile = extract_resume_profile(state)
        experiences = describe_experience(resume_profile)

        queries = []
        if isinstance(job_profile, dict):
            queries.extend([str(v) for v in job_profile.values() if isinstance(v, str)])
        queries.extend(experiences)
        queries = [q for q in queries if q]

        plan = RAGPlan(
            context_inputs=experiences,
            retrieval_queries=queries[:5],
            risk_checks=["ensure relevance", "avoid hallucination"],
        )

        return {"rag": {"plan": plan.model_dump()}}
