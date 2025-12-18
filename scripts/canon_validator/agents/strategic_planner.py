"""
StrategicPlanner Agent - High-Level Strategist.
Analyzes aggregated signals and generates multi-step refactor plans.
"""

import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from ..base import SubAtomicAgent


class StrategicPlanner(SubAtomicAgent):
    """
    ROLE: High-level strategist.
    Analyzes aggregated signals/violations and generates multi-step refactor plans.
    """

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Formulating Strategic Plan...")

        if not self.ctx.intelligence_enabled:
            print("   ⚠️  Intelligence disabled - skipping strategic planning")
            return

        # Refresh dependency graph
        self.ctx.refresh_graph()
        print(f"   🕸️ Code Graph: {len(self.ctx.code_graph.graph)} files mapped.")

        # Aggregate state
        violations = [
            f"Key {k}: {v.get('details', '')[:50]}..."
            for k, v in self.ctx.results.items()
            if not v.get('passed')
        ]
        signals = list(self.ctx.signals)

        # Check for human instructions
        await self._check_human_instructions()

        # Analyze blast radius if files were modified
        if self.ctx.modified_files:
            await self._analyze_blast_radius()

        # Generate strategic plan
        await self._generate_plan(violations, signals)

    async def _check_human_instructions(self):
        """Check for human intervention instructions."""
        instruction_file = Path("observability/human_instructions.md")
        if instruction_file.exists():
            try:
                instructions = instruction_file.read_text().strip()
                if instructions and not instructions.startswith("# DONE"):
                    print(f"   🗣️ HUMAN INTERVENTION: '{instructions[:50]}...'")

                    if "stop" in instructions.lower():
                        print("   🛑 Stopping per user request.")
                        sys.exit(0)
                    if "test" in instructions.lower():
                        self.ctx.signals.add("TEST_FAILURE")
                    if "style" in instructions.lower():
                        self.ctx.modified_files.add("FORCE_STYLE_CHECK")

                    # Mark handled
                    cycle = len(self.ctx.successful_traces)
                    instruction_file.write_text(f"# DONE (Cycle {cycle})\n" + instructions)
            except Exception:
                pass

    async def _analyze_blast_radius(self):
        """Analyze dependency graph for blast radius."""
        print("   🕸️ Analyzing Dependency Graph for Blast Radius...")
        all_impacted = set()
        for f in self.ctx.modified_files:
            deps = self.ctx.code_graph.get_impact_radius(f)
            all_impacted.update(deps)

        if all_impacted:
            print(f"      -> ☢️ Blast Radius: {len(all_impacted)} dependent files.")
            self.ctx.impact_zone = all_impacted

    async def _generate_plan(self, violations: list, signals: list):
        """Generate strategic refactor plan using LLM."""
        prompt = f"""
You are a Codebase Architect.
Current State:
- Signals: {signals[:10]}
- Violations: {json.dumps(violations[:10])}
- Modified files: {len(self.ctx.modified_files)}
- Cycle: {getattr(self.ctx, 'current_cycle', 1)}

Task: Generate a strategic refactor plan.
- If tests are failing, prioritize root cause analysis.
- If architecture is messy, prioritize modularization.
- Output "NO_PLAN_NEEDED" if system is stable.

Output ONLY the plan in Markdown.
"""

        plan = await self.ctx.resilient_mutation(self.name, prompt, max_attempts=2)

        if plan and "NO_PLAN_NEEDED" not in plan:
            print(f"   📋 STRATEGIC PLAN:\n{plan[:500]}...")
            self.ctx.strategic_plan = plan

            # Save to observability
            p = Path("observability/plans")
            p.mkdir(parents=True, exist_ok=True)
            cycle = len(self.ctx.successful_traces)
            (p / f"plan_cycle_{cycle}.md").write_text(plan)
        else:
            print("   ✅ Strategy: Maintain current trajectory.")
