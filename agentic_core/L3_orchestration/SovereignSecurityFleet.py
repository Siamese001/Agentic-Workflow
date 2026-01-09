#!/usr/bin/env python3
"""
SOVEREIGN SECURITY FLEET
------------------------
Master Orchestrator for the complete Sovereign Safety Architecture.
Consolidates all five sentinel agents into a unified health-check suite.

CANONICAL PATH: agentic_core/L3_orchestration/SovereignSecurityFleet.py
VIOLATION JUSTIFICATION: None. L3 Orchestration of L0-L6 agents.

FLEET COMPOSITION:
1. ConvergenceEngine (L3) - Recursive healing loop
2. InterfaceBoundaryAgent (L2) - L0 complexity enforcement
3. ToxicDependencyAuditor (L5) - Fan-in toxicity detection
4. GospelSyncAgent (L0) - Filesystem ↔ Blueprint synchronization
5. RuntimeTelemetryAgent (L6) - Performance overhead monitoring
"""

import time
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class FleetHealthReport:
    """Consolidated health report from all fleet agents."""
    timestamp: float = field(default_factory=time.time)
    agents_executed: int = 0
    agents_passed: int = 0
    agents_failed: int = 0
    total_duration_ms: float = 0.0
    overhead_ratio: float = 0.0
    gospel_synchronized: bool = False
    toxic_hubs_count: int = 0
    boundary_violations: int = 0
    convergence_ready: bool = False
    details: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def fleet_status(self) -> str:
        if self.agents_failed == 0:
            return "✅ FLEET OPERATIONAL"
        elif self.agents_failed < self.agents_executed // 2:
            return "⚠️  FLEET DEGRADED"
        else:
            return "☢️  FLEET CRITICAL"


class SovereignSecurityFleet:
    """
    THE MASTER ORCHESTRATOR
    Coordinates all five sentinel agents for comprehensive architectural health checks.
    """

    def __init__(self, root_dir: str = "."):
        self.root = Path(root_dir)
        self.baseline_startup_time = 0.03  # 30ms baseline
        self.agents_loaded: Dict[str, Any] = {}
        self.report = FleetHealthReport()

    def _load_agent(self, agent_name: str, agent_class: type, *args, **kwargs) -> Optional[Any]:
        """Safely load an agent with error handling."""
        try:
            start = time.perf_counter()
            agent = agent_class(*args, **kwargs)
            duration = time.perf_counter() - start
            self.agents_loaded[agent_name] = {
                "instance": agent,
                "load_time_ms": duration * 1000
            }
            return agent
        except Exception as e:
            print(f"   [!] Failed to load {agent_name}: {e}")
            self.report.agents_failed += 1
            return None

    def run_full_health_check(self) -> FleetHealthReport:
        """
        Execute all five sentinel agents and consolidate results.
        """
        print("\n" + "=" * 70)
        print(" SOVEREIGN SECURITY FLEET - FULL HEALTH CHECK")
        print("=" * 70)
        
        start_time = time.perf_counter()
        
        # === AGENT 1: ConvergenceEngine (L3) ===
        print("\n[1/5] ConvergenceEngine (L3) - Recursive Healing Loop")
        print("-" * 50)
        try:
            # Direct file load to bypass __init__.py import issues
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "mission_controller_convergence",
                self.root / "agentic_core/L3_orchestration/workflow_engines/mission_controller_convergence.py"
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            ConvergenceEngine = module.ConvergenceEngine
            engine = self._load_agent("ConvergenceEngine", ConvergenceEngine, max_rounds=8)
            if engine:
                self.report.convergence_ready = True
                self.report.agents_passed += 1
                print(f"   ✅ Loaded (max_rounds={engine.max_rounds})")
            self.report.agents_executed += 1
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.report.agents_failed += 1
            self.report.agents_executed += 1

        # === AGENT 2: InterfaceBoundaryAgent (L2) ===
        print("\n[2/5] InterfaceBoundaryAgent (L2) - Complexity Enforcement")
        print("-" * 50)
        try:
            from agentic_core.L2_execution.ToolRegistry.InterfaceBoundaryAgent import InterfaceBoundaryAgent
            agent = self._load_agent("InterfaceBoundaryAgent", InterfaceBoundaryAgent, 
                                     root_dir=str(self.root), complexity_threshold=15)
            if agent:
                violations = agent.audit_boundaries()
                self.report.boundary_violations = len(violations)
                self.report.details["boundary_violations"] = violations
                self.report.agents_passed += 1
                print(f"   ✅ Loaded - {len(violations)} complexity violations found")
            self.report.agents_executed += 1
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.report.agents_failed += 1
            self.report.agents_executed += 1

        # === AGENT 3: ToxicDependencyAuditor (L5) ===
        print("\n[3/5] ToxicDependencyAuditor (L5) - Fan-in Toxicity")
        print("-" * 50)
        try:
            from agentic_core.L5_safety.validators.ToxicDependencyAuditor import ToxicDependencyAuditor
            auditor = self._load_agent("ToxicDependencyAuditor", ToxicDependencyAuditor,
                                       root_dir=str(self.root), toxic_threshold=10)
            if auditor:
                toxic_hubs = auditor.audit_toxicity()
                self.report.toxic_hubs_count = len(toxic_hubs)
                self.report.details["toxic_hubs"] = toxic_hubs[:5]  # Top 5
                self.report.agents_passed += 1
                print(f"   ✅ Loaded - {len(toxic_hubs)} toxic hubs identified")
            self.report.agents_executed += 1
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.report.agents_failed += 1
            self.report.agents_executed += 1

        # === AGENT 4: GospelSyncAgent (L0) ===
        print("\n[4/5] GospelSyncAgent (L0) - Filesystem Synchronization")
        print("-" * 50)
        try:
            from agentic_core.L0_maintenance.GospelSyncAgent import GospelSyncAgent
            sync_agent = self._load_agent("GospelSyncAgent", GospelSyncAgent, root_dir=str(self.root))
            if sync_agent:
                sync_result = sync_agent.perform_sync_audit()
                self.report.gospel_synchronized = sync_result.get("synchronized", False)
                self.report.details["gospel_heresy"] = len(sync_result.get("heresy", []))
                self.report.details["gospel_missing"] = len(sync_result.get("missing", []))
                self.report.agents_passed += 1
                status = "✅ SYNCHRONIZED" if self.report.gospel_synchronized else "⚠️  DRIFT DETECTED"
                print(f"   {status}")
            self.report.agents_executed += 1
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.report.agents_failed += 1
            self.report.agents_executed += 1

        # === AGENT 5: RuntimeTelemetryAgent (L6) ===
        print("\n[5/5] RuntimeTelemetryAgent (L6) - Performance Monitoring")
        print("-" * 50)
        try:
            from agentic_core.L6_observability.RuntimeTelemetryAgent import RuntimeTelemetryAgent
            telemetry = self._load_agent("RuntimeTelemetryAgent", RuntimeTelemetryAgent, limit_multiplier=2.0)
            if telemetry:
                # Calculate total fleet startup time
                total_load_time = sum(a["load_time_ms"] for a in self.agents_loaded.values()) / 1000
                overhead_report = telemetry.audit_security_overhead(self.baseline_startup_time, total_load_time)
                self.report.overhead_ratio = overhead_report["ratio"]
                self.report.details["overhead_status"] = overhead_report["status"]
                self.report.agents_passed += 1
                print(f"   ✅ Loaded - Overhead ratio: {overhead_report['ratio']}x")
            self.report.agents_executed += 1
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.report.agents_failed += 1
            self.report.agents_executed += 1

        # Calculate total duration
        self.report.total_duration_ms = (time.perf_counter() - start_time) * 1000
        
        return self.report

    def print_consolidated_report(self) -> None:
        """Print the consolidated fleet health report."""
        print("\n" + "=" * 70)
        print(" SOVEREIGN SECURITY FLEET - CONSOLIDATED REPORT")
        print("=" * 70)
        
        print(f"\n{self.report.fleet_status}")
        print(f"\nAgents Executed: {self.report.agents_executed}/5")
        print(f"Agents Passed: {self.report.agents_passed}")
        print(f"Agents Failed: {self.report.agents_failed}")
        print(f"Total Duration: {self.report.total_duration_ms:.2f}ms")
        
        print("\n" + "-" * 50)
        print("DETAILED METRICS")
        print("-" * 50)
        
        print(f"Convergence Ready: {'✅' if self.report.convergence_ready else '❌'}")
        print(f"Gospel Synchronized: {'✅' if self.report.gospel_synchronized else '❌'}")
        print(f"Boundary Violations: {self.report.boundary_violations}")
        print(f"Toxic Hubs: {self.report.toxic_hubs_count}")
        print(f"Overhead Ratio: {self.report.overhead_ratio}x (limit: 2.0x)")
        
        if self.report.details.get("toxic_hubs"):
            print("\n" + "-" * 50)
            print("TOP TOXIC HUBS")
            print("-" * 50)
            for hub in self.report.details["toxic_hubs"][:3]:
                print(f"  ☢️  {hub['module']}: fan-in = {hub['fan_in']}")
        
        print("\n" + "=" * 70)
        
        # Exit code recommendation
        if self.report.agents_failed == 0:
            print("EXIT CODE: 0 (All systems operational)")
        else:
            print(f"EXIT CODE: 1 ({self.report.agents_failed} agent(s) failed)")
        print("=" * 70)


def main():
    """Main entry point for fleet health check."""
    fleet = SovereignSecurityFleet()
    fleet.run_full_health_check()
    fleet.print_consolidated_report()
    
    # Return appropriate exit code
    return 0 if fleet.report.agents_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
