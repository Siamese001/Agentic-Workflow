"""L1 draft planning stack."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from bullet_planning import extract_job_profile, extract_resume_profile, collect_sections, detect_metrics


class DraftPlan(BaseModel):
    goal: str = "Create a polished resume draft."
    tone: str = "Professional"
    structure: List[str] = ["Executive Summary", "Experience", "Skills"]
    key_messages: List[str] = []
    risks: List[str] = []
    review_gates: List[str] = []
    job_profile: Dict[str, Any] = {}
    resume_profile: Dict[str, Any] = {}


class DraftPlanningStack:
    """Prepare a draft plan without mutating state."""

    async def run_async(
        self, state: Dict[str, Any], workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        job_profile = extract_job_profile(state)
        resume_profile = extract_resume_profile(state)
        sections = collect_sections(state)
        metrics = detect_metrics(resume_profile)

        key_messages = []
        if isinstance(job_profile, dict):
            key_messages.extend([str(v) for v in job_profile.values() if isinstance(v, str)])
        if metrics:
            key_messages.extend([f"Metric: {k}={v}" for k, v in metrics.items()])

        structure = ["Executive Summary"] + [s for s in sections if s]
        if not structure:
            structure = ["Executive Summary", "Experience", "Education"]

        plan = DraftPlan(
            tone="Professional",
            structure=structure,
            key_messages=key_messages,
            risks=["hallucination", "missing job alignment"],
            review_gates=["narrative continuity", "quantified impact", "tone"],
            job_profile=job_profile,
            resume_profile=resume_profile,
        )

        return {"draft": {"plan": plan.model_dump()}}
"""L2 drafting execution stack."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from draft_planning import DraftPlan
from bullet_execution import BulletPlan, StrategyPlan


class DraftingExecutionStack:
    """Generate draft sections from bullets and plans."""

    def _load_plan(self, state: Dict[str, Any]) -> DraftPlan:
        plan_data = state.get("draft", {}).get("plan") or {}
        if isinstance(plan_data, DraftPlan):
            return plan_data
        if isinstance(plan_data, dict):
            return DraftPlan(**plan_data)
        return DraftPlan()

    def _load_strategy(self, state: Dict[str, Any]) -> StrategyPlan:
        strategy = state.get("strategy", {}).get("strategy_plan") or {}
        if isinstance(strategy, StrategyPlan):
            return strategy
        if isinstance(strategy, dict):
            return StrategyPlan(**strategy)
        return StrategyPlan()

    def _load_bullets(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        return state.get("bullets", {}).get("generated_bullets") or []

    async def run_async(
        self, state: Dict[str, Any], workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        plan = self._load_plan(state)
        strategy = self._load_strategy(state)
        bullets = self._load_bullets(state)

        sections: Dict[str, Dict[str, Any]] = {}
        structure = plan.structure or ["Executive Summary", "Experience"]

        summary_points = [b.get("text", str(b)) for b in bullets[:3]]
        sections["executive_summary"] = {
            "title": "Executive Summary",
            "content": " \n".join(summary_points) if summary_points else "Summary unavailable.",
            "tone": plan.tone or strategy.tone,
        }

        experience_content = [b.get("text", str(b)) for b in bullets]
        sections["experience"] = {
            "title": "Experience",
            "content": "\n".join(experience_content) if experience_content else "",
            "tone": plan.tone or strategy.tone,
        }

        for section in structure:
            key = section.lower().replace(" ", "_")
            sections.setdefault(key, {"title": section, "content": "", "tone": plan.tone})

        artifacts = {
            "artifacts": {
                "draft": {
                    "structure": {"sections": structure},
                    "narrative": {"summary": sections.get("executive_summary", {})},
                    "compliance": {"checks": ["basic structure applied"]},
                }
            }
        }

        return {
            "draft": {
                "plan": plan.model_dump(),
                "sections": sections,
                "tone": plan.tone,
                "structure": structure,
            },
            "artifacts": artifacts,
        }
"""
L2 — Drafting Execution Agent

Responsibilities:
    • Convert drafting briefs into narrative or structured content.
    • Apply tone, style, and constraint guidance from L1 drafting reasoners.
    • Return deterministic drafts and deltas for L4 state management.

Consumes PlanObject inputs and returns StatePatch outputs deterministically.
"""
from __future__ import annotations

from typing import Any, Dict, List

from injection_tooling_profiles import DEFAULT_TOOLING_PROFILE
from l2_execution import ExecutionAgent
from utils_types import PlanObject, StatePatch


def _compose_section(title: str, tone: str, audience: str) -> str:
    """Build a deterministic section string."""

    return f"[{title}] Tone: {tone}; Audience: {audience}."


class DraftingExecutionAgent(ExecutionAgent):
    """Create draft content without performing any tool calls."""

    def execute(self, plan: PlanObject, state: Dict[str, Any]) -> StatePatch:
        tone = str(plan.get("tone", "neutral"))
        audience = str(plan.get("audience", "general"))
        sections: List[str] = [str(section) for section in plan.get("sections", [])]
        if not sections:
            sections = ["Introduction", "Body", "Conclusion"]

        paragraphs = [_compose_section(title, tone, audience) for title in sections]
        draft = "\n\n".join(paragraphs)

        messages = list(state.get("messages", [])) + [
            {
                "role": "assistant",
                "content": draft,
                "format": "draft",
            }
        ]

        patch: StatePatch = StatePatch(
            {
                "messages": messages,
                "draft": {
                    "objective": plan.get("objective"),
                    "tone": tone,
                    "audience": audience,
                    "sections": sections,
                    "content": draft,
                },
            }
        )
        patch["tooling_injection"] = {
            "tool_feedback_enabled": DEFAULT_TOOLING_PROFILE.tool_feedback_enabled,
            "evidence_binding_enabled": DEFAULT_TOOLING_PROFILE.evidence_binding_enabled,
            "cross_tool_reconciliation": DEFAULT_TOOLING_PROFILE.cross_tool_reconciliation,
        }
        return patch
"""
L1 — Drafting Reasoner

Responsibilities:
    • Plan narrative or structured drafts aligned with task objectives.
    • Translate strategy intents into drafting briefs for L2 execution agents.
    • Incorporate retrieval or bullet inputs while deferring orchestration to L3.

Implements deterministic planning logic that emits only PlanObject instances.
"""
from __future__ import annotations

from typing import Any, Dict, List

from injection_profiles import DEFAULT_FRAMING_PROFILE
from l1_reasoning import Reasoner
from utils_types import PlanObject


def _collect_sections(state: Dict[str, Any]) -> List[str]:
    """Assemble deterministic section headings for the draft."""

    if state.get("outline"):
        return [str(section) for section in state["outline"]]

    bullets = state.get("bullets") or []
    if bullets:
        return [f"Section {index + 1}: {bullet}" for index, bullet in enumerate(bullets)]

    return ["Introduction", "Body", "Conclusion"]


class DraftingReasoner(Reasoner):
    """Create drafting briefs for L2 executors without side effects."""

    def plan(self, state: Dict[str, Any]) -> PlanObject:
        objective = state.get("objective", "unspecified-objective")
        tone = state.get("tone", "neutral")
        audience = state.get("audience", "general")
        sections = _collect_sections(state)

        plan: PlanObject = PlanObject(
            {
                "layer": "l1",
                "mode": "drafting",
                "objective": str(objective),
                "tone": tone,
                "audience": audience,
                "sections": sections,
                "constraints": state.get("constraints", []),
                "handoff": {
                    "target_layer": "l2",
                    "preferred_executor": "drafting",
                    "format": "narrative",
                },
            }
        )
        plan["injection_framing"] = {
            "global_goal": DEFAULT_FRAMING_PROFILE.global_goal,
            "success_criteria": DEFAULT_FRAMING_PROFILE.success_criteria,
            "task_mode": DEFAULT_FRAMING_PROFILE.task_mode,
            "scope_boundaries": DEFAULT_FRAMING_PROFILE.scope_boundaries,
            "cost_latency": DEFAULT_FRAMING_PROFILE.cost_latency,
        }
        plan["injection_reasoning"] = {
            "failure_anticipation_enabled": True,
            "self_consistency_enabled": True,
            "reason_then_answer": True,
            "error_simulation_enabled": True,
        }
        plan["safety_metadata"] = {
            "objective": str(objective),
            "sensitivity": "low",
            "audience": audience,
            "tags": ["planning"],
        }
        return plan
