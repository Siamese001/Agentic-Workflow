from __future__ import annotations

"""
Canon Validator Swarm Scheduler

Orchestrates the execution of validation agents in phases for the
Canon Validator system. Manages mission execution, convergence checking,
and human-in-the-loop intervention.
"""
import asyncio
from typing import TYPE_CHECKING, Any

from agentic_core.L1_cognition.P2_domain.context import ValidationContext

# [SSOT IMPORT] Structure blueprint is the single source of truth

if TYPE_CHECKING:
    from agentic_core.InterventionServer import approval_event, start_intervention_server


class CanonSwarmScheduler:
    """
    Orchestrates validation agent execution in phases.

    Phases:
    1. INTEGRITY (Sequential) - Hard gate checks
    2. CURATION (Sequential) - File hygiene and style
    3. TESTING (Sequential) - Regression testing
    4. MEMORY (Parallel) - Vector embeddings and context
    5. RESILIENCE (Parallel) - Security and performance
    6. RESOURCE SAFETY (Parallel) - Concurrency safety
    7. ENGINEERING (Parallel) - Refactoring and patterns
    8. REFINEMENT (Parallel) - Naming, docs, types
    9. BENCHMARKING (Sequential) - Empirical validation
    10. OPTIMIZATION (Conditional) - Architectural evolution
    """

    def __init__(self, agent_classes: dict = None):
        """
        Initialize the scheduler.

        Args:
            agent_classes: Dictionary mapping agent names to their classes.
                          If None, agents must be set via set_phases().
        """
        self.ctx = ValidationContext()
        self.phases = {}
        self._agent_classes = agent_classes or {}

    def set_phases(self, phases: dict) -> Any:
        """Set the phase configuration with instantiated agents."""
        self.phases = phases

    def build_default_phases(self) -> Any:
        """Build default phase configuration using agent classes."""
        if not self._agent_classes:
            raise ValueError(
                "No agent classes provided. Call set_phases() or provide agent_classes in constructor."
            )
        from agentic_core.L2_execution.ToolRegistry.governance import DependencySentinelAgent
        from agentic_core.L2_execution.ToolRegistry.infrastructure import (
            BenchmarkingAgent,
            Historian,
        )
        from agentic_core.L2_execution.ToolRegistry.quality import (
            CodeStyleGuardian,
            HygieneGuardian,
            PerformanceEnforcer,
        )
        from agentic_core.L2_execution.ToolRegistry.repair import TestPilot, ToolsmithAgent
        from agentic_core.L2_execution.ToolRegistry.security import (
            ConcurrencyGuardianAgent,
            SafetyInspectorAgent,
            SecurityEnforcer,
        )
        from agentic_core.L2_execution.ToolRegistry.specialized import (
            DocEnforcer,
            NamingEnforcer,
            TheCartographer,
            TheOmniContext,
            TheStrategist,
            TypeEnforcer,
        )
        from agentic_core.L5_safety.unified.UnifiedCodeEnforcerAgent import (
            StructuralEngineer,
            UnifiedCodeEnforcerAgent,
        )

        self.phases = {
            "integrity_seq": [
                Historian(self.ctx),
                ArchitectureGovernor(self.ctx),
                DependencySentinelAgent(self.ctx),
            ],
            "curation_seq": [HygieneGuardian(self.ctx), CodeStyleGuardian(self.ctx)],
            "test_seq": [TestPilot(self.ctx)],
            "memory_parallel": [TheCartographer(self.ctx), TheOmniContext(self.ctx)],
            "resilience_parallel": [
                SafetyInspectorAgent(self.ctx),
                SecurityEnforcer(self.ctx),
                PerformanceEnforcer(self.ctx),
            ],
            "resource_safety_parallel": [ConcurrencyGuardianAgent(self.ctx)],
            "engineering_parallel": [
                StructuralEngineer(self.ctx),
                UnifiedCodeEnforcerAgent(self.ctx),
                ToolsmithAgent(self.ctx),
            ],
            "refinement_parallel": [
                NamingEnforcer(self.ctx),
                DocEnforcer(self.ctx),
                TypeEnforcer(self.ctx),
            ],
            "benchmarking_seq": [BenchmarkingAgent(self.ctx)],
            "optimization_conditional": [TheStrategist(self.ctx)],
        }

    async def run_mission(self, target_scope: str = None) -> Any:
        """
        Run the validation mission.

        Args:
            target_scope: Optional file path for surgical validation (L5 Watchman mode).
                         If provided, only validates this file and its dependents (blast radius).
        """
        if target_scope:
            print(f"🎯 SURGICAL MISSION: Targeting {target_scope}")
            if not self.ctx.code_graph.graph:
                self.ctx.code_graph.build(self.ctx.python_files)
            BlastRadius: Any = {target_scope}
            dependents: Any = self.ctx.code_graph.get_impact_radius(target_scope)
            BlastRadius.update(dependents)
            original_files: Any = self.ctx.python_files.copy()
            self.ctx.python_files = [
                f
                for f in self.ctx.python_files
                if f in BlastRadius or any(f.endswith(b.lstrip("./")) for b in BlastRadius)
            ]
            print(f"   ☢️ BLAST RADIUS: {len(self.ctx.python_files)} files in scope")
            for f in self.ctx.python_files[:5]:
                print(f"      - {f}")
            if len(self.ctx.python_files) > 5:
                print(f"      ... and {len(self.ctx.python_files) - 5} more")
        else:
            print("[START] STARTING SUBATOMIC MISSION (Tri-Brain Enabled)")
        max_cycles: Any = 10
        for cycle in range(max_cycles):
            print(f"\n{'=' * 60}")
            print(f"CYCLE {cycle + 1}/{max_cycles}")
            print(f"{'=' * 60}")
            self.ctx.modified_files.clear()
            self.ctx.signals.clear()
            converged: Any = await self._execute_all_phases()
            if await self._check_intervention_required():
                if "VETOED" in self.ctx.signals:
                    print("\n🛑 ACTION VETOED BY HUMAN - Mission aborted!")
                    break
            if converged:
                print("\n[OK] CONVERGENCE ACHIEVED - All checks passed!")
                break
            if "CRITICAL_FAIL" in self.ctx.signals:
                print("\n[X] CRITICAL FAILURE - Mission aborted!")
                break
        self._generate_mission_report()
        if target_scope and "original_files" in locals():
            self.ctx.python_files = original_files

    async def _check_intervention_required(self) -> bool:
        """
        L5 Human-in-the-Loop: Check if intervention is required and wait for approval.
        Returns True if intervention was triggered (approval received or vetoed).
        """
        high_risk = "HIGH_RISK" in self.ctx.signals
        many_modifications = len(self.ctx.modified_files) > 3
        strategic_plan = getattr(self.ctx, "strategic_plan", None)
        if high_risk or (many_modifications and strategic_plan):
            print("\n[ALERT] INTERVENTION REQUIRED")
            print(f"   Risk Level: {('HIGH' if high_risk else 'ELEVATED')}")
            print(f"   Modified Files: {len(self.ctx.modified_files)}")
            print("   Approval URL: http://127.0.0.1:8080")
            start_intervention_server(self.ctx)
            print("   ⏳ Waiting for human approval...")
            await approval_event.wait()
            approval_event.clear()
            return True
        return False

    async def _execute_all_phases(self):
        """Execute all phases in order with early abort logic."""
        print("\n[PHASE 1] INTEGRITY CHECK (Sequential)")
        if not await self._run_sequential("integrity_seq"):
            if "CRITICAL_FAIL" in self.ctx.signals:
                return False
        print("\n[PHASE 2] CURATION (Sequential)")
        await self._run_sequential("curation_seq")
        print("\n[PHASE 3] TESTING (Sequential)")
        await self._run_sequential_with_scheduler("test_seq")
        print("\n[PHASE 4] MEMORY ENHANCEMENT (Parallel)")
        await self._run_parallel("memory_parallel")
        print("\n[PHASE 5] RESILIENCE HARDENING (Parallel)")
        await self._run_parallel("resilience_parallel")
        print("\n[PHASE 6] RESOURCE SAFETY (Parallel)")
        await self._run_parallel("resource_safety_parallel")
        print("\n[PHASE 7] ENGINEERING (Parallel)")
        await self._run_parallel("engineering_parallel")
        print("\n[PHASE 8] REFINEMENT (Parallel)")
        await self._run_parallel("refinement_parallel")
        print("\n[PHASE 9] BENCHMARKING (Sequential)")
        await self._run_sequential("benchmarking_seq")
        print("\n[PHASE 10] OPTIMIZATION (Conditional)")
        if self._is_converged():
            await self._run_sequential("optimization_conditional")
        else:
            print("   ⏭️  Skipping optimization - not fully converged")
        return self._is_converged()

    async def _run_sequential(self, phase_name: str) -> bool:
        """Execute a phase sequentially."""
        agents = self.phases.get(phase_name, [])
        for agent in agents:
            await agent.execute()
            if phase_name == "integrity_seq" and "CRITICAL_FAIL" in self.ctx.signals:
                print(f"   [ALERT] CRITICAL FAIL from {agent.name} - Aborting {phase_name}")
                return False
        return True

    async def _run_sequential_with_scheduler(self, phase_name: str):
        """Execute a phase sequentially, passing scheduler reference to agents."""
        agents = self.phases.get(phase_name, [])
        for agent in agents:
            if hasattr(agent, "set_scheduler"):
                agent.set_scheduler(self)
            await agent.execute()

    async def _run_parallel(self, phase_name: str):
        """Execute a phase in parallel."""
        agents = self.phases.get(phase_name, [])
        if not agents:
            return
        tasks = []
        for agent in agents:
            if hasattr(agent, "execute"):
                tasks.append(agent.execute())
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def _is_converged(self) -> bool:
        """Check if all agents have passed."""
        if not self.ctx.results:
            return False
        return all(r.get("passed", False) for r in self.ctx.results.values())

    def _generate_mission_report(self):
        """Generate final mission report."""
        print("\n" + "=" * 60)
        print("MISSION REPORT")
        print("=" * 60)
        total_keys = len(self.ctx.results)
        passed_keys = sum(1 for r in self.ctx.results.values() if r.get("passed", False))
        print("\n[STATS] SUMMARY:")
        print(f"   Total Keys Checked: {total_keys}")
        print(f"   Keys Passed: {passed_keys}")
        print(f"   Keys Failed: {total_keys - passed_keys}")
        if total_keys > 0:
            print(f"   Success Rate: {passed_keys / total_keys * 100:.1f}%")
        if self._is_converged():
            print("\n[OK] MISSION SUCCESS - Full convergence achieved!")
        else:
            print("\n[!]  MISSION INCOMPLETE - Some issues remain")
        print("\n📝 DETAILED RESULTS:")
        for key, result in sorted(self.ctx.results.items()):
            status = "[OK] PASS" if result.get("passed", False) else "[X] FAIL"
            print(f"   {status} Key {key:02d}: {result.get('agent', 'Unknown')}")
        print("\n" + "=" * 60)


SwarmScheduler: Any = CanonSwarmScheduler
IntelligentOrchestratorAgent: Any = CanonSwarmScheduler
