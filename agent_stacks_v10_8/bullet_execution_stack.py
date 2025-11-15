"""Bullet-generation stack shim for v10.8."""

from __future__ import annotations

from typing import Any, Dict, List

from stacks_v10_7.bullet import AsyncBulletCritiqueAgent, AsyncBulletGeneratorAgent


class BulletExecutionStack:
    """Layer-isolated interface for bullet generation and critique."""

    def __init__(self, context: Any, debug_mode: bool = False) -> None:
        self.context = context
        self.debug_mode = debug_mode
        self._generator = AsyncBulletGeneratorAgent(context, debug_mode)
        self._critique_agent = AsyncBulletCritiqueAgent(context, debug_mode)

    async def generate_async(
        self,
        task_context: Dict[str, Any],
        strategy: Any,
        workflow_id: str,
    ) -> Dict[str, Any]:
        """Delegate bullet generation to the v10.7 AsyncBulletGeneratorAgent."""

        return await self._generator.run_async(task_context, strategy, workflow_id)

    async def critique_async(
        self,
        bullets: List[Dict[str, Any]],
        critique_prompt: str,
        workflow_id: str,
    ) -> List[Dict[str, Any]]:
        """Delegate bullet critique to the v10.7 AsyncBulletCritiqueAgent."""

        return await self._critique_agent.run_async(bullets, critique_prompt, workflow_id)
