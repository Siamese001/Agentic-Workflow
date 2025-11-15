"""Prompt building stack for v10.8 that wraps the legacy prompt engineer."""

from __future__ import annotations

from typing import Any, Dict, Optional

from stacks_v10_7.prompting import PromptEngineerAgent


class PromptBuilderStack:
    """Layer-isolated facade for prompt engineering."""

    def __init__(self, context: Any, debug_mode: bool = False) -> None:
        self.context = context
        self.debug_mode = debug_mode
        self._prompt_agent = PromptEngineerAgent(context, debug_mode)

    async def run_async(
        self,
        strategy_plan: Any,
        complexity: str,
        workflow_id: str,
        state: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute prompt engineering and emit a structured state patch."""

        prompts_result = await self._prompt_agent.run_async(
            strategy_plan,
            complexity,
            workflow_id,
            state,
        )

        prompts_payload: Dict[str, Any] = {}
        prompts_model = prompts_result.get("prompts") if isinstance(prompts_result, dict) else None
        if prompts_model is None:
            prompts_payload = prompts_result if isinstance(prompts_result, dict) else {}
        elif hasattr(prompts_model, "model_dump"):
            prompts_payload = prompts_model.model_dump()
        elif isinstance(prompts_model, dict):
            prompts_payload = prompts_model

        return {"prompts": {"prompts": prompts_payload}}
