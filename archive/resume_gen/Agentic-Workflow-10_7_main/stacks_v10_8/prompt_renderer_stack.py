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
