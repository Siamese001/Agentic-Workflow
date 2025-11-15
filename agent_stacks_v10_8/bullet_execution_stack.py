"""Bullet-generation stack shim for v10.8."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Sequence

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
        prompt: str,
        experiences: Sequence[Dict[str, Any]],
        strategy: Any,
        workflow_id: str,
    ) -> Dict[str, Any]:
        """Delegate bullet generation to the v10.7 AsyncBulletGeneratorAgent."""

        generated: List[Dict[str, Any]] = []
        for experience in experiences:
            raw_bullets = await self._generator.run_async(
                prompt,
                experience,
                strategy,
                workflow_id,
            )
            generated.extend(
                [
                    {
                        "text": bullet_text,
                        "experience": experience,
                    }
                    for bullet_text in raw_bullets
                ]
            )

        return {"bullets": {"generated_bullets": generated}}

    async def critique_async(
        self,
        bullets: Iterable[Dict[str, Any]],
        critique_prompt: str,
        workflow_id: str,
    ) -> Dict[str, Any]:
        """Delegate bullet critique to the v10.7 AsyncBulletCritiqueAgent."""

        critiques = await self._critique_agent.run_async(
            list(bullets), critique_prompt, workflow_id
        )
        return {"bullets": {"critiqued_bullets": critiques}}
