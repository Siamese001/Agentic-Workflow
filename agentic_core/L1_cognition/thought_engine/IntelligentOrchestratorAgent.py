from __future__ import annotations
"""
Canon Validator Intelligent Orchestrator

Orchestrates all validation agents in dependency order.
"""
import asyncio
import re
from typing import Any, Dict, List, Optional, Protocol
from agentic_core.utils.core_extensions.timeout_decorator import timeout
from agentic_core.canon_agents_core import GenerativeGuard, HealerAgent, SystemArchitect
from agentic_core.L1_cognition.thought_engine.PatternEnforcerAgent import PatternEnforcerAgent
from agentic_core.canon_agents_pattern import SemanticMapperAgent, UIValidationAgent
from agentic_core.L1_cognition.thought_engine.DocumentationAgent import DocumentationAgent
from agentic_core.canon_agents_quality import NamingAgent, SafetyInspectorAgent
from agentic_core.L1_cognition.thought_engine.BudgetAgent import BudgetAgent
from agentic_core.L1_cognition.thought_engine.TypeMechanicAgent import TypeMechanicAgent
from agentic_core.canon_agents_syntax import CodeJanitor, DependencySentinelAgent

# GRAVITY FIXED (Intra-Core): Dynamic import for L2 dependency
import importlib
_struct_mod = importlib.import_module('agentic_core.L2_execution.ToolRegistry.StructuralEngineerAgent')
StructuralEngineerAgent = getattr(_struct_mod, 'StructuralEngineerAgent')
from agentic_core.runtime.shared.canon_validation_context import ValidationContext
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.mixins import SubatomicTestingMixin

class IntelligentOrchestratorAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin):
    """Orchestrates all validation agents in dependency order."""

    def __init__(self, target: Optional[str]=None) -> None:
        """
        Initializes the IntelligentOrchestratorAgent with a validation context and a swarm of agents.

        Args:
            target (Optional[str]): The target scope for validation, e.g., a file path or directory.
                                    Defaults to the current directory ".".
        """
        self.ctx: ValidationContext = ValidationContext(target_scope=target or '.')
        self.swarm = [HealerAgent(self.ctx), SystemArchitect(self.ctx), GenerativeGuard(self.ctx), CodeJanitor(self.ctx), DependencySentinelAgent(self.ctx), SafetyInspectorAgent(self.ctx), PatternEnforcerAgent(self.ctx), DocumentationAgent(self.ctx), NamingAgent(self.ctx), BudgetAgent(self.ctx), TypeMechanicAgent(self.ctx), UIValidationAgent(self.ctx), SemanticMapperAgent(self.ctx), StructuralEngineerAgent(self.ctx)]

    async def run_mission(self) -> None:
        """
        Execute all agents in sequence.

        Agents are run in their defined dependency order. If an agent's dependencies
        are not met, it will stand down. Critical failures can abort the mission.
        """
        print('🤖 SWARM INTELLIGENCE ONLINE. Initializing Blackboard...')
        print(f'\nfrom agentic_core.utils.mixins import SubatomicTestingMixin\nfrom agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin\nimport logging\n\nLogger = logging.getLogger(__name__)\n[MISSION] Starting validation sweep across {len(self.ctx.python_files)} files...')
        agents_executed: Any = 0
        agents_passed: Any = 0
        agents_failed: Any = 0
        await self.ctx.services.init_mcp_async()
        for i, agent in enumerate(self.swarm, 1):
            print(f'\n[MISSION] Agent {i}/{len(self.swarm)}: {agent.name}')
            if not agent.can_run():
                print(f'   ⛔ {agent.name} STANDING DOWN (Dependencies not met).')
                continue
            agents_executed += 1
            try:
                print(f'   ⚡ Executing {agent.name}...')
                result: Any = agent.execute()
                if asyncio.iscoroutine(result):
                    await result
                agents_passed += 1
                print(f'   ✅ {agent.name} completed successfully')
            except Exception as e:
                print(f'   ❌ [ALERT] AGENT CRASH ({agent.name}): {e}')
                agents_failed += 1
            if 'CRITICAL_FAIL' in self.ctx.signals:
                print('\n🛑 MISSION ABORTED: Critical Architecture Failure.')
                print('   Action: Fix Key 40/41/50 immediately.')
                break
        print(f'\n[MISSION] Agent Execution Summary:')
        print(f'   • Total Agents: {len(self.swarm)}')
        print(f'   • Executed: {agents_executed}')
        print(f'   • Passed: {agents_passed} ✅')
        print(f'   • Failed: {agents_failed} ❌')
        self.print_mission_report()

    def print_mission_report(self) -> None:
        """
        Print the final validation report.

        Summarizes the total checks, passed/failed counts, open violations,
        and autonomous repairs performed.
        """
        print('\n' + '=' * 60)
        print('🏁 MISSION REPORT')
        print('=' * 60)
        total_checks: Any = len(self.ctx.results)
        passed_checks: Any = sum((1 for r in self.ctx.results.values() if r['passed']))
        failed_checks: Any = total_checks - passed_checks
        print(f'Total Checks: {total_checks}')
        print(f'Passed:       {passed_checks}')
        print(f'Failed:       {failed_checks}')
        if failed_checks > 0:
            print('\n[X] OPEN VIOLATIONS:')
            for key, result in sorted(self.ctx.results.items()):
                if not result['passed']:
                    print(f'   Key {key}')
        if self.ctx.modified_files:
            print(f'\n✨ AUTONOMOUS REPAIRS COMPLETED ({len(self.ctx.modified_files)} files):')
            for fp in sorted(self.ctx.modified_files):
                history: Any = self.ctx.healing_history.get(fp, [])
                history_str: Any = f" ({', '.join(history)})" if history else ''
                print(f'   • {fp}{history_str}')
        print(f'\nHealing budget: {self.ctx.healing_budget_used}/{self.ctx.global_healing_budget} used')
        if failed_checks == 0:
            print('\n🎯 LEVEL 5 SUBATOMIC CANON ACHIEVED – FULL AUTONOMOUS INTEGRITY')
        else:
            print(f'\n[!]  Canon incomplete – {failed_checks} keys remain violated.')
            print('   Run again with healing enabled for further convergence.')

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """L1 cognition agent - operational only."""
        # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
        super().heal_repository()

        _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L1 cognition - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)