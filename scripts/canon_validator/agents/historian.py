"""
Historian Agent - Memory Keeper.
Tracks file changes and skips unchanged files to save tokens.
"""

import asyncio
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    pass

from ..base import SubAtomicAgent


class Historian(SubAtomicAgent):
    """
    ROLE: Memory Keeper. Tracks file changes and skips unchanged files.
    Runs early to save tokens on unchanged code.
    """

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Analyzing file history...")
        await asyncio.sleep(0)

        skipped_count = 0
        for file_path in self.ctx.python_files:
            if self.ctx.should_skip_file(file_path):
                self.ctx.skip_files.add(file_path)
                skipped_count += 1
                # Mark as passed in results to maintain consistency
                key = self.ctx._get_file_key(file_path)
                self.ctx.results[key] = {"passed": True, "details": [], "skipped": True}

        if skipped_count > 0:
            print(f"   📚 {self.name}: Skipping {skipped_count} unchanged files (saved tokens)")

        # Flag flapping files for special attention
        if self.ctx.flapping_files:
            print(f"   🔄 {self.name}: {len(self.ctx.flapping_files)} flapping files detected")
            for file_path in self.ctx.flapping_files:
                self.ctx.inject_instruction(
                    self.name,
                    f"FLAPPING FILE: {file_path} toggles Pass/Fail. Consider rewrite."
                )

    async def recommend_from_memory(self, file_path: str, current_signals: List[str]) -> str:
        """L5+ Use LLM with few-shot to recommend actions based on recalled memories."""
        if not self.ctx.intelligence_enabled:
            return ""

        # Recall relevant memories from Pinecone/local
        memories = []
        if hasattr(self.ctx, 'recall_memory'):
            memories = self.ctx.recall_memory(file_path, limit=5)

        memories_summary = "\n".join([f"- {m}" for m in memories[:5]]) if memories else "No relevant memories found."

        prompt = f"""
{self.ctx.FEW_SHOT_HISTORIAN}

Current issue in {file_path}
Signals: {current_signals[:10]}

Recalled memories:
{memories_summary}

Recommend action based on history.
If similar past success → output "APPLY_MEMORY: <description>"
If past failure → output "AVOID_STRATEGY: <description>"
If no relevant memory → output "PROPOSE_NEW: <description>"
"""

        return await self.ctx.resilient_mutation(
            self.name, prompt, max_attempts=1
        )
