# === CONSOLIDATED FILE ===
# TIMESTAMP: 2025-11-17T16:29:33.163202Z
# TARGET: shared_runtime_utils.py
# SOURCE FILES:
# - /workspace/Agentic-Workflow/_latest_extract/stacks_v/init_.py | SHA256: fc9b756e59f3093e503ddac766d63d750d07c310d16d86e22c873fc71122067b
# - /workspace/Agentic-Workflow/_latest_extract/stacks_v/planning_utils.py | SHA256: bdc97534515df2e7f6655f6dea7e018a71f0678a371d508224ed09c9f812cc08
# - /workspace/Agentic-Workflow/_latest_extract/stacks_v/prompt_renderer_stack.py | SHA256: f9b01bd0c51db913a50efa62673f258a697500b3a000411d02d8fd9341b3f5e4
# MERGE RULE: 10_8 overrides 10_7; namespace collisions suffixed with __srcN


# ==== BEGIN SOURCE: /workspace/Agentic-Workflow/_latest_extract/stacks_v/init_.py (sha256=fc9b756e59f3093e503ddac766d63d750d07c310d16d86e22c873fc71122067b) ====
"""v10.8 planning + execution stacks used across the workflow."""

from .rag_planning import RAGPlanningStack
from .bullet_planning import BulletPlanningStack
from .draft_planning import DraftPlanningStack
from .rag_execution import RAGExecutionStack
from .bullet_execution import BulletExecutionStack
from .drafting_execution import DraftingExecutionStack
from .rag_orchestration import RAGOrchestratorStack
from .draft_orchestration import DraftOrchestratorStack

__all__ = [
    "RAGPlanningStack",
    "BulletPlanningStack",
    "DraftPlanningStack",
    "RAGExecutionStack",
    "BulletExecutionStack",
    "DraftingExecutionStack",
    "RAGOrchestratorStack",
    "DraftOrchestratorStack",
]
# ==== END SOURCE: /workspace/Agentic-Workflow/_latest_extract/stacks_v/init_.py ====
# ==== BEGIN SOURCE: /workspace/Agentic-Workflow/_latest_extract/stacks_v/planning_utils.py (sha256=bdc97534515df2e7f6655f6dea7e018a71f0678a371d508224ed09c9f812cc08) ====
"""Shared helpers for lightweight L1 planning stacks."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List


def extract_job_profile(state: Dict[str, Any]) -> Dict[str, Any]:
    job = state.get("job") or {}

    def _first(*keys: str) -> str:
        for key in keys:
            value = job.get(key)
            if value:
                return str(value)
        return ""

    raw_requirements = (
        job.get("top_requirements")
        or job.get("required_skills")
        or job.get("keywords")
        or job.get("skills")
        or []
    )
    requirements: List[str]
    if isinstance(raw_requirements, str):
        requirements = [part.strip() for part in raw_requirements.split(",") if part.strip()]
    elif isinstance(raw_requirements, Iterable):
        requirements = [str(item).strip() for item in raw_requirements if str(item).strip()]
    else:
        requirements = []

    return {
        "title": _first("job_title", "title", "role"),
        "company": _first("company", "employer", "organization"),
        "summary": _first("summary", "description", "jd_excerpt", "jd"),
        "team": _first("team", "org_unit", "department"),
        "location": _first("location", "city"),
        "requirements": requirements,
    }


def extract_resume_profile(state: Dict[str, Any]) -> Dict[str, Any]:
    resume = state.get("resume") or {}
    master_resume = resume.get("master_resume") or {}
    summary = (
        master_resume.get("summary")
        or master_resume.get("professional_summary")
        or master_resume.get("profile")
        or ""
    )
    experiences = master_resume.get("professional_experience")
    if not isinstance(experiences, list):
        experiences = []
    return {"summary": str(summary), "experiences": experiences}


def describe_experience(experience: Dict[str, Any]) -> str:
    title = experience.get("title") or experience.get("role") or "Role"
    company = experience.get("company") or experience.get("employer") or "Company"
    scope = (
        experience.get("impact_summary")
        or experience.get("summary")
        or experience.get("description")
        or ""
    )
    description = f"{title} @ {company}".strip()
    if scope:
        description = f"{description} – {scope}".strip()
    return description


def detect_metrics(experiences: List[Dict[str, Any]]) -> List[str]:
    metrics: List[str] = []
    for exp in experiences:
        text_parts: List[str] = []
        for key in ("impact_summary", "summary", "description"):
            value = exp.get(key)
            if value:
                text_parts.append(str(value))
        bullet_pool = exp.get("bullet_pool")
        if isinstance(bullet_pool, list):
            text_parts.extend(str(item) for item in bullet_pool)
        combined = " ".join(text_parts)
        if any(char.isdigit() for char in combined):
            metrics.append(f"Quantify results from {describe_experience(exp)}")
    if not metrics:
        metrics.append("Quantify at least one outcome per bullet")
    return metrics


def collect_sections(state: Dict[str, Any]) -> List[str]:
    draft = state.get("draft") or {}
    sections = draft.get("sections")
    if isinstance(sections, dict) and sections:
        return list(sections.keys())
    return ["summary", "experience", "skills"]


def missing_requirements(requirements: List[str], experiences: List[Dict[str, Any]]) -> List[str]:
    if not requirements:
        return []
    combined = " ".join(
        str(exp.get("impact_summary") or exp.get("summary") or "") for exp in experiences
    ).lower()
    missing = [req for req in requirements if req.lower() not in combined]
    return missing
# ==== END SOURCE: /workspace/Agentic-Workflow/_latest_extract/stacks_v/planning_utils.py ====
# ==== BEGIN SOURCE: /workspace/Agentic-Workflow/_latest_extract/stacks_v/prompt_renderer_stack.py (sha256=f9b01bd0c51db913a50efa62673f258a697500b3a000411d02d8fd9341b3f5e4) ====
"""Render PromptEnvelope into a final prompt string with L5 safety signals."""

from __future__ import annotations

from typing import Any, Dict, Optional

from core_v10_7 import BaseAgent, PromptEnvelope


class PromptRendererStack(BaseAgent):
    """L2 stack responsible for rendering prompts from a PromptEnvelope."""

    async def run_async(
        self, state: Dict[str, Any], workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        env = PromptEnvelope.model_validate(state["prompts"]["prompt_envelope"])

        # Collect L5 signals
        inj = self.context.prompt_injection_detector.detect(str(env))
        pol = self.context.policy_stack.guard_output(env.model_dump())
        cr = self.context.constitutional_engine.review_text(str(env))

        env.safety_context = {
            "injection": inj,
            "policy": pol.dict(),
            "constitution": cr.dict(),
        }

        final = self._render(env)
        return {"prompts": {"final_prompt": final}}

    def _render(self, env: PromptEnvelope) -> str:
        return f"""
[FRAMING]
{env.framing}

[CONTEXT]
{env.context}

[REASONING]
{env.reasoning}

[INSTRUCTIONS]
{env.instructions}

[TOOL CONTEXT]
{env.tool_context}

[SAFETY SIGNALS]
{env.safety_context}

[OUTPUT SCHEMA]
{env.output_schema}
"""
# ==== END SOURCE: /workspace/Agentic-Workflow/_latest_extract/stacks_v/prompt_renderer_stack.py ====
