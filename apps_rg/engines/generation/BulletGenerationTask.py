"""
Bullet Generation Task - Stateless bullet writer
Refactored from create_experience_bullets.py
"""

from __future__ import annotations

import logging
from typing import Any

from apps_rg.engines.base.base_resume_engine import BaseRGEngine

Logger = logging.getLogger(__name__)


class BulletGenerationTask(BaseRGEngine):
    """
    Stateless bullet writer for experience sections.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="GENERATION.BULLETS")

    async def execute(self, experience_context: dict[str, Any], target_count: int = 5) -> list[str]:
        """
        Generate achievement bullets for an experience section.
        """
        self._mcp_audit("bullet_generation_start", {"target_count": target_count})

        # Get prompt from knowledge base
        prompt_template = self.get_frozen_prompt("bullet_generation") if self.knowledge else ""

        if not prompt_template:
            prompt_template = "Generate {count} achievement bullets for {role} at {company}"

        prompt = prompt_template.format(
            count=target_count,
            role=experience_context.get("role", "Professional"),
            company=experience_context.get("company", "Company"),
        )

        # Call LLM
        raw_output = await self.call_llm(prompt)
        bullets = self._parse_bullets(raw_output)

        # Validate count
        if len(bullets) != target_count:
            self.record_fail(f"Generated {len(bullets)} bullets, expected {target_count}")
        else:
            self.record_pass(f"Generated {len(bullets)} bullets")

        return bullets

    def _parse_bullets(self, text: str) -> list[str]:
        """Parse LLM output into bullet list."""
        if not text:
            return []

        # Simple line-based parsing
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        bullets = [line.lstrip("•-*").strip() for line in lines if line]
        return bullets
