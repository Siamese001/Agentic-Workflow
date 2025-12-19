"""
Planning and reflection agents for strategic decision-making.

Contains:
- StrategicPlanner: High-level strategist that analyzes signals and generates multi-step refactor plans
- ReflectionAgent: Consolidates successful mutations into long-term memory and performs self-critique
"""

import asyncio
import json
import sys
from pathlib import Path

from .base import SubAtomicAgent


class StrategicPlanner(SubAtomicAgent):
    """
    ROLE: High-level strategist.
    Analyzes aggregated signals/violations and generates multi-step refactor plans.
    """
    def __init__(self, ctx):
        super().__init__(ctx)
        self.name = "StrategicPlanner"

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Formulating Strategic Plan...")
        if not self.ctx.intelligence_enabled:
            return
        
        # LEVEL 6: Refresh Dependency Graph
        self.ctx.refresh_graph()
        print(f"   🕸️ Code Graph: {len(self.ctx.code_graph.graph)} files mapped.")

        # 1. Aggregate State
        violations = [f"Key {k}: {v.get('details','')}..." for k, v in self.ctx.results.items() if not v.get('passed')]
        signals = list(self.ctx.signals)
        
        # LEVEL 6: Dynamic Instruction Watcher (Telepathy Interface)
        instruction_file = Path("observability/human_instructions.md")
        if instruction_file.exists():
            instructions = instruction_file.read_text().strip()
            if instructions and not instructions.startswith("# DONE"):
                print(f"   🗣️ HUMAN INTERVENTION: New orders received -> '{instructions[:50]}...'")
                
                # Inject into agenda based on text
                if "stop" in instructions.lower():
                    print("   🛑 Stopping per user request.")
                    sys.exit(0)
                if "test" in instructions.lower():
                    self.ctx.signals.add("TEST_FAILURE")  # Force testing
                if "style" in instructions.lower():
                    self.ctx.modified_files.add("FORCE_STYLE_CHECK")
                
                # Mark handled
                instruction_file.write_text(f"# DONE (Cycle {len(self.ctx.successful_traces)})\n" + instructions)
        
        # LEVEL 6: Analyze Dependency Graph for Blast Radius
        if self.ctx.modified_files:
            print("   🕸️ Analyzing Dependency Graph for Blast Radius...")
            all_impacted = set()
            for f in self.ctx.modified_files:
                deps = self.ctx.code_graph.get_impact_radius(f)
                all_impacted.update(deps)
            
            if all_impacted:
                print(f"      -> ☢️ Blast Radius detected: {len(all_impacted)} dependent files.")
                # Store for TestPilot to use
                self.ctx.impact_zone = all_impacted
        
        # 2. Generate Plan with L5+ Few-Shot Strategic Injection
        prompt = f"""
{self.ctx.FEW_SHOT_STRATEGIC}

You are a Codebase Architect.
Current State:
- Signals: {signals}
- Violations: {json.dumps(violations[:10])}
- Modified files: {len(self.ctx.modified_files)}
- Cycle: {getattr(self.ctx, 'current_cycle', 1)}

Task: Generate a strategic refactor plan.
- If tests are failing, prioritize root cause analysis.
- If architecture is messy, prioritize modularization.
- Output "NO_PLAN_NEEDED" if system is stable.

Propose optimal agent agenda based on priority rules above.
Output ONLY the plan in Markdown.
"""
        
        plan = await self.ctx.resilient_mutation(self.name, prompt, max_attempts=2)
        
        if "NO_PLAN_NEEDED" not in plan:
            print(f"   📋 STRATEGIC PLAN:\n{plan[:500]}...")
            self.ctx.strategic_plan = plan
            # Save to observability
            p = Path("observability/plans")
            p.mkdir(parents=True, exist_ok=True)
            (p / f"plan_cycle_{len(self.ctx.successful_traces)}.md").write_text(plan)
        else:
            print("   ✅ Strategy: Maintain current trajectory.")


class ReflectionAgent(SubAtomicAgent):
    """Consolidates successful mutations into long-term memory and performs self-critique."""
    def __init__(self, ctx):
        super().__init__(ctx)
        self.name = "ReflectionAgent"

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Internalizing Lessons...")
        
        # L5+ Self-Critique Injection: Strategic reflection on healing cycle
        if self.ctx.intelligence_enabled:
            cycle = getattr(self.ctx, 'current_cycle', 1)
            convergence_reached = getattr(self.ctx.signal_convergence, 'reached', False) if hasattr(self.ctx, 'signal_convergence') else False
            
            reflection_prompt = f"""
{self.ctx.FEW_SHOT_REFLECTION_STRATEGY}
{self.ctx.FEW_SHOT_REFLECTION_ENHANCED}

<self_critique_guidance>
You are reflecting on healing cycle {cycle}.
Ask:
1. Did modifications reduce signals? (Goal: zero)
2. Did any new signals appear? → regression?
3. Are files still subatomic and at correct depth?
4. What strategy failed/succeeded?
5. What should change next cycle?
</self_critique_guidance>

Current state:
Signals: {list(self.ctx.signals)[:10]}
Modified: {list(self.ctx.modified_files)[:10]}
Convergence: {convergence_reached}
Success Rate: {self.ctx.mutation_stats.get('success', 0)}/{self.ctx.mutation_stats.get('total', 0)}
Budget spent: {self.ctx.budget.get_status() if hasattr(self.ctx.budget, 'get_status') else 'unknown'}

Based on examples above, recommend next action.
Respond with one keyword only:
CONVERGE_AND_COMMIT | MARK_FLAPPING_SKIP_FILE | ROLLBACK_LAST_CHANGE_AND_RETRY | ESCALATE_TO_HUMAN_WITH_REPORT
"""
            try:
                advice = await self.ctx.resilient_mutation(
                    self.name, reflection_prompt, max_attempts=1
                )
                if advice and len(advice.strip()) > 10:
                    print(f"   🪞 Self-Critique: {advice[:300]}...")
                    
                    # Act on recommendations
                    if "stop" in advice.lower() or "converge" in advice.lower():
                        print("   ✅ Reflection suggests convergence achieved.")
                    elif "escalat" in advice.lower() or "human" in advice.lower():
                        print("   🚨 Reflection suggests human escalation needed.")
                        self.ctx.signals.add("NEEDS_HUMAN_REVIEW")
                    elif "skip" in advice.lower() or "flap" in advice.lower():
                        print("   ⚠️ Reflection detected flapping - marking files to skip.")
            except Exception as e:
                print(f"   ⚠️ Self-critique failed: {e}")
        
        # Original memory consolidation logic
        count = 0
        for trace in self.ctx.successful_traces:
            # Create a "Lesson" for the Deep Brain
            await self.ctx.upsert_embedding(
                key=f"trace_{hash(trace['task'])}",
                text=trace['task'] + "\n" + trace['code_before'],
                metadata=trace
            )
            count += 1
        self.ctx.successful_traces.clear()  # Reset short-term memory
        if count > 0:
            print(f"   🧠 Learned {count} new patterns from this session.")
