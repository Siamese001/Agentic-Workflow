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

# from archives.legacy_resume_gen.Agentic-Workflow-10_8_core.injection_tooling_profiles import DEFAULT_TOOLING_PROFILE  # INVALID: Cannot import from path with hyphens
# from archives.legacy_resume_gen.Agentic-Workflow-10_8_core.l2_execution import ExecutionAgent  # INVALID: Cannot import from path with hyphens
# from archives.legacy_resume_gen.Agentic-Workflow-10_8_core.utils_types import PlanObject, StatePatch  # INVALID: Cannot import from path with hyphens


def _compose_section(title: str, tone: str, audience: str) -> str:
    """Build a deterministic section string."""

    return f"[{title}] Tone: {tone}; Audience: {audience}."


class DraftingExecutionAgent(ExecutionAgent):
    """Create draft content without performing any tool calls."""

    def execute(self, plan: PlanObject, state: Dict[str, object]) -> StatePatch:
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
