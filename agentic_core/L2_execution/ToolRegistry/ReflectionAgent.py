"""
ReflectionAgent - Extracted for one-class-per-file pattern.

Originally from: StrategicPlannerAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""


from __future__ import annotations

class ReflectionAgent(HealerMixin, MCPHardenedMixin, SubatomicTestingMixin, SubAtomicAgent):
    """
    ROLE: Consolidation and self-critique.
    Consolidates successful mutations into long-term memory and performs self-critique.
    """
    def __init__(self, ctx) -> None:
        super().__init__(ctx)
        self.name = "ReflectionAgent"

    async def execute(self) -> None:
                    
        print(f"\n[>>>] {self.name} ACTIVATED: Performing Self-Critique...")
        if not self.ctx.successful_traces:
            return

        # Consolidate mutations into memory
        recent_trace = self.ctx.successful_traces[-1]
        prompt = f"Critique and consolidate the following mutation into long-term memory: {recent_trace}"

        critique = await self.ctx.resilient_mutation(self.name, prompt)
        print(f"   🧐 CRITIQUE: {critique[:100]}...")

        if not hasattr(self.ctx, 'long_term_memory'):
            self.ctx.long_term_memory = []
        self.ctx.long_term_memory.append({"trace": recent_trace, "critique": critique})
    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
