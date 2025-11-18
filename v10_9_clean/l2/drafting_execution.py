# FILE: v10_9_clean/l2/drafting_execution.py
"""
L2 — Draft Execution (v10_9)

Executes narrative or structured draft generation based on an L1 PlanObject.

Consumes:
    • plan.steps[0]["sections"]
    • plan.steps[0]["tone"]
    • plan.steps[0]["audience"]
    • plan.steps[0]["hints"]

Produces:
    • ExecutionResult(status=SUCCESS, payload={...})

No planning, no state mutation, no external dependencies except model clients.
"""

from __future__ import annotations
from typing import Any, Dict, List

from shared.models import ExecutionResult, PlanObject
from shared.exceptions import ToolExecutionError

from l2.clients import build_client


async def execute_drafting(plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult:
    """
    Generate a narrative or structured draft using an LLM client.

    This function:
        • extracts plan parameters
        • builds a stable deterministic stub (until prompting wired)
        • packages results into an ExecutionResult
    """

    try:
        if not plan.steps:
            raise ValueError("Drafting plan missing steps")

        step = plan.steps[0]

        sections: List[str] = step.get("sections") or []
        tone: str = step.get("tone") or "Professional"
        audience: str = step.get("audience") or "general"
        hints: List[str] = step.get("hints") or []

        # LLM client — future: loaded from plan.handoff or routing
        client = build_client(plan.handoff.get("model") or "gpt-4.1")

        # Deterministic placeholder implementation until prompt_system integrated
        draft_paragraphs: List[str] = []
        for sec in sections:
            line = (
                f"[{sec.upper()} — tone={tone}, audience={audience}] "
                f"Generated narrative aligned to hints: {', '.join(hints[:2])}"
            )
            draft_paragraphs.append(line)

        payload = {
            "sections": sections,
            "tone": tone,
            "audience": audience,
            "hints": hints,
            "draft": draft_paragraphs,
        }

        return ExecutionResult(
            status=ExecutionResult.__fields__["status"].type_.SUCCESS,
            payload=payload,
            model=client.model,
            usage={},
        )

    except Exception as exc:
        raise ToolExecutionError(f"Draft execution failed: {exc}") from exc
