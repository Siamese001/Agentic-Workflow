"""
OmniContextAgent - Extracted for one-class-per-file pattern.

Originally from: CartographerAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""


from __future__ import annotations
import asyncio
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin

class OmniContextAgent(SubAtomicAgent, MCPHardenedMixin):
    """
    ROLE: Wisdom & Semantic Retrieval. Provides context-aware answers.
    """
    async def execute(self) -> None:
                    
        print(f"\n[>>>] {self.name} ACTIVATED: Initializing semantic wisdom...")
        await asyncio.sleep(0)
        self.ctx.OmniContext = self

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
