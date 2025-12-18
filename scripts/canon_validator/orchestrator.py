"""
SwarmScheduler - Async Orchestrator for Canon Validator.
Manages agent execution phases and convergence detection.
"""

import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import ValidationContext

from .agents import (ArchitectureGovernor, BenchmarkingAgent,
                     CodeStyleGuardian, ConcurrencyGuardian, DeadlockDetector,
                     DependencySentinel, DocEnforcer, Historian,
                     HygieneGuardian, MemoryLeakDetector, NamingEnforcer,
                     PatternEnforcer, PerformanceEnforcer, SafetyInspector,
                     SecurityEnforcer, StructuralEngineer, TestPilot,
                     TheCartographer, TheOmniContext, TheStrategist,
                     ToolsmithAgent, TypeEnforcer)
from .types import ValidationContext


class SwarmScheduler:
    """Async orchestrator for the Canon Validator agent swarm."""

    def __init__(self):
        self.ctx = ValidationContext()

        # NAMED PHASES - Agent execution order
        self.phases = {
            "integrity_seq": [
                Historian(self.ctx),
                ArchitectureGovernor(self.ctx),
                DependencySentinel(self.ctx),
            ],
            "curation_seq": [
                HygieneGuardian(self.ctx),
                CodeStyleGuardian(self.ctx),
            ],
            "test_seq": [
                TestPilot(self.ctx),
            ],
            "memory_parallel": [
                TheCartographer(self.ctx),
                TheOmniContext(self.ctx),
            ],
            "resilience_parallel": [
                SafetyInspector(self.ctx),
                SecurityEnforcer(self.ctx),
                PerformanceEnforcer(self.ctx),
            ],
            "resource_safety_parallel": [
                ConcurrencyGuardian(self.ctx),
                MemoryLeakDetector(self.ctx),
                DeadlockDetector(self.ctx),
            ],
            "engineering_parallel": [
                StructuralEngineer(self.ctx),
                PatternEnforcer(self.ctx),
                ToolsmithAgent(self.ctx),
            ],
            "refinement_parallel": [
                NamingEnforcer(self.ctx),
                DocEnforcer(self.ctx),
                TypeEnforcer(self.ctx),
            ],
            "benchmarking_seq": [
                BenchmarkingAgent(self.ctx),
            ],
            "optimization_conditional": [
                TheStrategist(self.ctx),
            ],
        }

    async def run_mission(self, target_scope: str = None):
        """Run the validation mission."""
        if target_scope:
            print(f"🎯 SURGICAL MISSION: Targeting {target_scope}")
            await self._setup_surgical_scope(target_scope)
        else:
            print("🚀 STARTING SUBATOMIC MISSION (Tri-Brain Enabled)")

        max_cycles = 10
        for cycle in range(max_cycles):
            print(f"\n{'='*60}")
            print(f"CYCLE {cycle + 1}/{max_cycles}")
            print(f"{'='*60}")

            self.ctx.modified_files.clear()
            self.ctx.signals.clear()

            converged = await self._execute_all_phases()

            if converged:
                print("\n✅ CONVERGENCE ACHIEVED - All checks passed!")
                break

            if "CRITICAL_FAIL" in self.ctx.signals:
                print("\n❌ CRITICAL FAILURE - Mission aborted!")
                break

        self._generate_mission_report()

    async def _setup_surgical_scope(self, target_scope: str):
        """Setup surgical validation scope."""
        if not self.ctx.code_graph.graph:
            self.ctx.code_graph.build(self.ctx.python_files)

        blast_radius = {target_scope}
        dependents = self.ctx.code_graph.get_impact_radius(target_scope)
        blast_radius.update(dependents)

        self.ctx.python_files = [
            f for f in self.ctx.python_files
            if f in blast_radius or any(f.endswith(b.lstrip('./')) for b in blast_radius)
        ]

        print(f"   ☢️ BLAST RADIUS: {len(self.ctx.python_files)} files in scope")

    async def _execute_all_phases(self) -> bool:
        """Execute all phases in order."""
        print("\n[PHASE 1] INTEGRITY CHECK (Sequential)")
        if not await self._run_sequential("integrity_seq"):
            if "CRITICAL_FAIL" in self.ctx.signals:
                return False

        print("\n[PHASE 2] CURATION (Sequential)")
        await self._run_sequential("curation_seq")

        print("\n[PHASE 3] TESTING (Sequential)")
        await self._run_sequential("test_seq")

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

        print("\n[PHASE 10] OPTIMIZATION (Always Run)")
        # Phase 10 now runs unconditionally - removed convergence gate
        # If success rate < 30%, trigger targeted remediation first
        success_rate = self._get_success_rate()
        if success_rate < 30.0:
            print(f"   ⚠️  Success rate {success_rate:.1f}% < 30% - triggering targeted remediation")
            await self._targeted_remediation()
        await self._run_sequential("optimization_conditional")

        return self._is_converged()

    async def _run_sequential(self, phase_name: str) -> bool:
        """Execute a phase sequentially."""
        agents = self.phases.get(phase_name, [])
        for agent in agents:
            if hasattr(agent, 'can_run') and not agent.can_run():
                continue
            await agent.execute()

            if phase_name == "integrity_seq" and "CRITICAL_FAIL" in self.ctx.signals:
                print(f"   🚨 CRITICAL FAIL from {agent.name}")
                return False
        return True

    async def _run_parallel(self, phase_name: str):
        """Execute a phase in parallel."""
        agents = self.phases.get(phase_name, [])
        if not agents:
            return

        tasks = []
        for agent in agents:
            if hasattr(agent, 'can_run') and not agent.can_run():
                continue
            if hasattr(agent, 'execute'):
                tasks.append(agent.execute())

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def _is_converged(self) -> bool:
        """Check if all agents have passed."""
        if not self.ctx.results:
            return False
        return all(r.get("passed", False) for r in self.ctx.results.values())

    def _get_success_rate(self) -> float:
        """Calculate current success rate as percentage."""
        if not self.ctx.results:
            return 0.0
        passed = sum(1 for r in self.ctx.results.values() if r.get("passed", False))
        return (passed / len(self.ctx.results)) * 100.0

    async def _targeted_remediation(self):
        """Trigger targeted remediation for Phase 8 agents (Naming, Docs, Types)."""
        print("   🔧 TARGETED REMEDIATION: Activating mutation mode for refinement agents...")
        
        # Get the refinement agents and force mutation mode
        refinement_agents = self.phases.get("refinement_parallel", [])
        for agent in refinement_agents:
            if hasattr(agent, 'mutation_mode'):
                agent.mutation_mode = True
            # Inject mutation instruction
            self.ctx.inject_instruction(
                "SwarmScheduler",
                f"{agent.name}: MUTATION MODE ACTIVE - fix issues immediately, do not just report"
            )
        
        # Re-run refinement phase in mutation mode
        print("   🔄 Re-running REFINEMENT phase in mutation mode...")
        await self._run_parallel("refinement_parallel")

    def _generate_mission_report(self):
        """Generate final mission report."""
        print("\n" + "="*60)
        print("MISSION REPORT")
        print("="*60)

        total_keys = len(self.ctx.results)
        passed_keys = sum(1 for r in self.ctx.results.values() if r.get("passed", False))

        print(f"\n📊 SUMMARY:")
        print(f"   Total Keys Checked: {total_keys}")
        print(f"   Keys Passed: {passed_keys}")
        print(f"   Keys Failed: {total_keys - passed_keys}")
        if total_keys > 0:
            print(f"   Success Rate: {passed_keys/total_keys*100:.1f}%")

        if self._is_converged():
            print("\n✅ MISSION SUCCESS - Full convergence achieved!")
        else:
            print("\n⚠️  MISSION INCOMPLETE - Some issues remain")

        print("\n" + "="*60)


# Legacy alias for backward compatibility
IntelligentOrchestrator = SwarmScheduler


async def main():
    """Main entry point for the Canon Validator."""
    scheduler = SwarmScheduler()
    await scheduler.run_mission()


if __name__ == "__main__":
    asyncio.run(main())
