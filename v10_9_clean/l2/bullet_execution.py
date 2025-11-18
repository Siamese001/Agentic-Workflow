# FILE: v10_9_clean/l2/bullet_execution.py
"""
L2 — Bullet Execution (v10_9)

Executes L1 bullet-generation plans:
    • Uses model clients from l2/clients.py
    • Consumes PlanObject produced by L1 bullet planning
    • Produces an ExecutionResult with generated bullets

No planning. No state mutation. Pure execution.
"""

from __future__ import annotations

from typing import Any, Dict, List

from shared.models import ExecutionResult, PlanObject
from shared.exceptions import ToolExecutionError

from l2.clients import build_client


async def execute_bullets(plan: PlanObject, state: Dict[str, Any]) -> ExecutionResult:
    """
    Execute bullet generation using an LLM.

    PlanObject fields consumed:
        - steps[0]["target_sections"]
        - steps[0]["highlight_order"]
        - steps[0]["metrics_focus"]
        - steps[0]["style_guidelines"]
        - steps[0]["validation_checks"]

    Returns:
        ExecutionResult(status=SUCCESS, payload={...})
    """

    try:
        if not plan.steps:
            raise ValueError("Bullet plan missing steps")

        step = plan.steps[0]

        target_sections: List[str] = step.get("target_sections") or []
        highlights: List[str] = step.get("highlight_order") or []
        metrics_focus: List[str] = step.get("metrics_focus") or []
        guidelines: List[str] = step.get("style_guidelines") or []
        checks: List[str] = step.get("validation_checks") or []

        # Build the LLM client (future: configurable from plan.handoff)
        client = build_client(plan.handoff.get("model") or "gpt-4.1")

        # Deterministic stub output until wired with actual prompting layer
        bullets: List[str] = []
        for i, h in enumerate(highlights):
            bullets.append(
                f"• Delivered measurable impact: {h} "
                f"(guided by metrics: {', '.join(metrics_focus[:2])})"
            )

        payload = {
            "bullets": bullets,
            "target_sections": target_sections,
            "guidelines": guidelines,
            "validation_checks": checks,
        }

        return ExecutionResult(
            status=ExecutionResult.__fields__["status"].type_.SUCCESS,
            payload=payload,
            model=client.model,
            usage={},
        )

    except Exception as exc:
        raise ToolExecutionError(f"Bullet execution failed: {exc}") from exc
