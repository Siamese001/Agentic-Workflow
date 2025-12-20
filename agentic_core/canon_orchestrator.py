The provided Python code is already very well-structured and adheres to most syntax and style guidelines. The primary adjustment needed is to conform to PEP 8's recommendation of two blank lines before top-level class definitions.

Here's the fixed code with that minor style adjustment:

"""
Canon Validator Intelligent Orchestrator

Orchestrates all validation agents in dependency order.
"""
import asyncio
from typing import Optional

from apps_shared.canon_validation_context import ValidationContext

# Local application imports (grouped by sub-module for clarity)
from agentic_core.canon_agents_core import SystemArchitect, HealerAgent, GenerativeGuard
from agentic_core.canon_agents_syntax import CodeJanitor, DependencySentinel
from agentic_core.canon_agents_quality import SafetyInspector, DocumentationAgent, NamingAgent
from agentic_core.canon_agents_structural import TypeMechanic, BudgetAgent, StructuralEngineer
from agentic_core.canon_agents_pattern import PatternEnforcer, UIValidationAgent, SemanticMapper


class IntelligentOrchestrator:
    """Orchestrates all validation agents in dependency order."""

    def __init__(self, target: Optional[str] = None):
        """
        Initializes the IntelligentOrchestrator with a validation context and a swarm of agents.

        Args:
            target (Optional[str]): The target scope for validation, e.g., a file path or directory.
                                    Defaults to the current directory ".".
        """
        self.ctx: ValidationContext = ValidationContext(target_scope=target or ".")
        self.swarm = [
            HealerAgent(self.ctx),              # 0. Syntax/RCA (Blocker)
            SystemArchitect(self.ctx),          # 1. Structure (Blocker)
            GenerativeGuard(self.ctx),          # 2. Generative Policy
            CodeJanitor(self.ctx),              # 3. Syntax (Signal: AST_VALID)
            DependencySentinel(self.ctx),       # 4. Imports (Signal: DEPS_VALID)
            SafetyInspector(self.ctx),          # 5. Security (Signal: SECURE)
            PatternEnforcer(self.ctx),          # 6. Patterns
            DocumentationAgent(self.ctx),       # 7. Docs
            NamingAgent(self.ctx),              # 8. Naming
            BudgetAgent(self.ctx),              # 9. Complexity
            TypeMechanic(self.ctx),             # 10. Types
            UIValidationAgent(self.ctx),        # 11. UI Patterns (MCP)
            SemanticMapper(self.ctx),           # 12. Clustering
            StructuralEngineer(self.ctx),       # 13. Refactoring
        ]

    async def run_mission(self) -> None:
        """
        Execute all agents in sequence.

        Agents are run in their defined dependency order. If an agent's dependencies
        are not met, it will stand down. Critical failures can abort the mission.
        """
        print("🤖 SWARM INTELLIGENCE ONLINE. Initializing Blackboard...")

        # Initialize MCP async services for filesystem operations
        await self.ctx.services.init_mcp_async()

        for agent in self.swarm:
            if not agent.can_run():
                print(f"   ⛔ {agent.name} STANDING DOWN (Dependencies not met).")
                continue

            try:
                result = agent.execute()
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                # Catching broad Exception is acceptable here as it's an orchestrator
                # reporting agent failures, not necessarily recovering from them.
                print(f"   🚨 AGENT CRASH ({agent.name}): {e}")

            if "CRITICAL_FAIL" in self.ctx.signals:
                print("\n🛑 MISSION ABORTED: Critical Architecture Failure.")
                print("   Action: Fix Key 40/41/50 immediately.")
                break

        self.print_mission_report()

    def print_mission_report(self) -> None:
        """
        Print the final validation report.

        Summarizes the total checks, passed/failed counts, open violations,
        and autonomous repairs performed.
        """
        print("\n" + "=" * 60)
        print("🏁 MISSION REPORT")
        print("=" * 60)

        total_checks = len(self.ctx.results)
        passed_checks = sum(1 for r in self.ctx.results.values() if r["passed"])
        failed_checks = total_checks - passed_checks

        print(f"Total Checks: {total_checks}")
        print(f"Passed:       {passed_checks}")
        print(f"Failed:       {failed_checks}")

        if failed_checks > 0:
            print("\n❌ OPEN VIOLATIONS:")
            # Sort violations by key for consistent reporting
            for key, result in sorted(self.ctx.results.items()):
                if not result["passed"]:
                    print(f"   Key {key}")

        # L5 Final Autonomy Report
        if self.ctx.modified_files:
            print(f"\n✨ AUTONOMOUS REPAIRS COMPLETED ({len(self.ctx.modified_files)} files):")
            for fp in sorted(self.ctx.modified_files):
                history = self.ctx.healing_history.get(fp, [])
                history_str = f" ({', '.join(history)})" if history else ""
                print(f"   • {fp}{history_str}")

        print(f"\nHealing budget: {self.ctx.healing_budget_used}/{self.ctx.global_healing_budget} used")

        if failed_checks == 0:
            print("\n🎯 LEVEL 5 SUBATOMIC CANON ACHIEVED – FULL AUTONOMOUS INTEGRITY")
        else:
            print(f"\n⚠️  Canon incomplete – {failed_checks} keys remain violated.")
            print("   Run again with healing enabled for further convergence.")
