"""
ReflectionAgent - Self-Critique and Memory Consolidation.
Consolidates successful mutations into long-term memory.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from agentic_core..base import SubAtomicAgent


class ReflectionAgent(SubAtomicAgent):
    """
    ROLE: Self-Critique and Memory Consolidation.
    Consolidates successful mutations into long-term memory and performs self-critique.
    """

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Internalizing Lessons...")

        # Self-critique if intelligence is enabled
        if self.ctx.intelligence_enabled:
            await self._perform_self_critique()

        # Memory consolidation
        await self._consolidate_memory()

    async def _perform_self_critique(self):
        """Perform self-critique on the healing cycle."""
        cycle = getattr(self.ctx, 'current_cycle', 1)
        convergence_reached = getattr(self.ctx, 'signal_convergence', False)

        prompt = f"""
You are reflecting on healing cycle {cycle}.
Ask:
1. Did modifications reduce signals? (Goal: zero)
2. Did any new signals appear? → regression?
3. Are files still subatomic and at correct depth?
4. What strategy failed/succeeded?
5. What should change next cycle?

Current state:
Signals: {list(self.ctx.signals)[:10]}
Modified: {list(self.ctx.modified_files)[:10]}
Convergence: {convergence_reached}
Success Rate: {self.ctx.mutation_stats.get('success', 0)}/{self.ctx.mutation_stats.get('total', 0)}

Respond with one keyword only:
CONVERGE_AND_COMMIT | MARK_FLAPPING_SKIP_FILE | ROLLBACK_LAST_CHANGE_AND_RETRY | ESCALATE_TO_HUMAN_WITH_REPORT
"""

        try:
            advice = await self.ctx.resilient_mutation(self.name, prompt, max_attempts=1)
            if advice and len(advice.strip()) > 10:
                print(f"   🪞 Self-Critique: {advice[:300]}...")

                if "converge" in advice.lower():
                    print("   ✅ Reflection suggests convergence achieved.")
                elif "escalat" in advice.lower() or "human" in advice.lower():
                    print("   🚨 Reflection suggests human escalation needed.")
                    self.ctx.signals.add("NEEDS_HUMAN_REVIEW")
                elif "skip" in advice.lower() or "flap" in advice.lower():
                    print("   ⚠️ Reflection detected flapping - marking files to skip.")
        except Exception as e:
            print(f"   ⚠️ Self-critique failed: {e}")

    async def _consolidate_memory(self):
        """Consolidate successful traces into long-term memory."""
        count = 0
        for trace in self.ctx.successful_traces:
            try:
                await self.ctx.upsert_embedding(
                    key=f"trace_{hash(trace['task'])}",
                    text=trace['task'] + "\n" + trace.get('code_before', ''),
                    metadata=trace
                )
                count += 1
            except Exception:
                pass

        self.ctx.successful_traces.clear()

        if count > 0:
            print(f"   🧠 Learned {count} new patterns from this session.")
