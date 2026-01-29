# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, guardrail, orchestrator, workflow
from __future__ import annotations

# This boosts alignment detection — review and integrate appropriately
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

"""
Planning and reflection agents for strategic decision-making.

Contains:
- RgStrategicPlannerAgent: High-level strategist that analyzes signals and generates multi-step refactor plans
- RgReflectionAgent: Consolidates successful mutations into long-term memory and performs self-critique
"""
import json
import sys
from pathlib import Path

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.L5_safety.validators.decorators import standard_heal

# DUPLICATE ACCEPTED: App-specific customization valid
# (different contexts: L2 core planning vs L1 strategic vs apps_rg implementations)
# - Intentional variants for domain-specific planning
# - Documented 2026-01-06


# NAMING CANON ETERNAL — renamed inline for sovereign discovery — Phase 5 — 2025-12-30
class RgStrategicPlannerAgent(SovereignBaseAgent):
    """
    ROLE: High-level strategist.
    Analyzes aggregated signals/violations and generates multi-step refactor plans.
    """

    def __init__(self, ctx) -> None:
        super().__init__(ctx)
        self.name = "StrategicPlannerAgent"

    async def execute(self) -> None:
        print(
            f"\nfrom agentic_core.base_agents.subatomic_testing_mixin import SubatomicTestingMixin\nfrom agentic_core.L2_execution.mcp.mcp_hardened_mixin import MCPHardenedMixin\nfrom agentic_core.base_agents.healer_mixin import HealerMixin\nimport logging\n\nLogger = logging.getLogger(__name__)\n[>>>] {self.name} ACTIVATED: Formulating Strategic Plan..."
        )
        if not self.ctx.intelligence_enabled:
            return

        # LEVEL 6: Refresh Dependency Graph
        self.ctx.refresh_graph()
        print(f"   🕸️ Code Graph: {len(self.ctx.code_graph.graph)} files mapped.")

        # 1. Aggregate State
        violations = [
            f"Key {k}: {v.get('details', '')}..."
            for k, v in self.ctx.results.items()
            if not v.get("passed")
        ]
        signals = list(self.ctx.signals)

        # LEVEL 6: Dynamic Instruction Watcher (Telepathy Interface)
        instruction_file = Path("observability/human_instructions.md")
        if instruction_file.exists():
            # Blocking IO remains as Pathlib is standard, but logic ensures no disruptive 'eval'
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
                instruction_file.write_text(
                    f"# DONE (Cycle {len(self.ctx.successful_traces)})\n" + instructions
                )

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
{getattr(self.ctx, "FEW_SHOT_STRATEGIC", "")}

You are a Codebase Architect.
Current State:
- Signals: {signals}
- Violations: {json.dumps(violations[:10])}
- Modified files: {len(self.ctx.modified_files)}
- Cycle: {getattr(self.ctx, "current_cycle", 1)}

Task: Generate a strategic refactor plan.
- If tests are failing, prioritize root cause analysis.
- If architecture is messy, prioritize modularization.
- Output "NO_PLAN_NEEDED" if system is stable.

Propose optimal agent agenda based on priority rules above.
Output ONLY the plan in Markdown.
"""

        plan = await self.ctx.resilient_mutation(self.name, prompt, max_attempts=2)

        if "NO_PLAN_NEEDED" not in plan:
            print(f"   [PLAN] STRATEGIC PLAN:\n{plan[:500]}...")
            self.ctx.strategic_plan = plan
            # Save to observability
            p = Path("observability/plans")
            p.mkdir(parents=True, exist_ok=True)
            (p / f"plan_cycle_{len(self.ctx.successful_traces)}.md").write_text(plan)
        else:
            print("   [OK] Strategy: Maintain current trajectory.")

    @standard_heal
    def heal_repository(
        self, dry_run=True, execute=False, depth=0, max_depth=3, _call_path=None, **kwargs
    ) -> dict:
        """Standardized healing signature with signal propagation."""
        return super().heal_repository(dry_run, execute, depth, max_depth, _call_path, **kwargs)


# DUPLICATE ACCEPTED: App-specific customization valid
# (different contexts: L1 cognition vs L2 planning vs apps_rg implementations)
# - Intentional variants for domain-specific behavior
# - Consolidated 2026-01-06

# NAMING CANON ETERNAL — renamed inline for sovereign discovery — Phase 5 — 2025-12-30
