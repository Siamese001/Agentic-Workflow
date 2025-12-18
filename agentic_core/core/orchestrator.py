"""
agentic_core/core/orchestrator.py
Depth: 3
Role: Central nervous system. Orchestrates agent execution and human intervention.
"""
import asyncio
import time
import os
import sys
import threading
from typing import List

# Import Domain
from agentic_core.domain.context import ValidationContext

# Import All Agents
from agentic_core.agents.infrastructure import Historian, GitAgent, BenchmarkingAgent, WatchmanHandler
from agentic_core.agents.governance import ArchitectureGovernor, DependencySentinel
from agentic_core.agents.quality import HygieneGuardian, CodeStyleGuardian, PerformanceEnforcer
from agentic_core.agents.security import SafetyInspector, ConcurrencyGuardian, SecurityEnforcer
from agentic_core.agents.engineering import StructuralEngineer, PatternEnforcer
from agentic_core.agents.repair import Sherlock, TestPilot, ToolsmithAgent
from agentic_core.agents.specialized import (
    TheCartographer, TheOmniContext, TheStrategist, 
    NamingEnforcer, DocEnforcer, TypeEnforcer
)

# L5 Human-in-the-Loop Dependencies
try:
    import uvicorn
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

# Global Event for Intervention
approval_event = asyncio.Event()
_intervention_context = None

if FASTAPI_AVAILABLE:
    intervention_app = FastAPI(title="L5 Intervention UI")

    @intervention_app.get("/", response_class=HTMLResponse)
    def get_dashboard():
        ctx = _intervention_context
        signals = list(ctx.signals) if ctx else []
        return f"""<html><body><h1>🚨 L5 INTERVENTION REQUIRED</h1>
        <p>Signals: {signals}</p>
        <button onclick="fetch('/approve', {{method:'POST'}})">APPROVE</button>
        <button onclick="fetch('/veto', {{method:'POST'}})">VETO</button>
        </body></html>"""

    @intervention_app.post("/approve")
    def approve_action():
        approval_event.set()
        return {"status": "APPROVED"}

    @intervention_app.post("/veto")
    def veto_action():
        if _intervention_context: _intervention_context.signals.add("VETOED")
        approval_event.set()
        return {"status": "VETOED"}


def start_intervention_server(ctx):
    global _intervention_context
    _intervention_context = ctx
    if FASTAPI_AVAILABLE:
        t = threading.Thread(target=uvicorn.run, args=(intervention_app,), kwargs={"host": "127.0.0.1", "port": 8080, "log_level": "error"}, daemon=True)
        t.start()
        print("   🌐 Intervention server at http://127.0.0.1:8080")


class SwarmScheduler:
    def __init__(self):
        self.ctx = ValidationContext()
        
        # Define Phases
        self.phases = {
            "integrity_seq": [Historian(self.ctx), ArchitectureGovernor(self.ctx), DependencySentinel(self.ctx)],
            "curation_seq": [HygieneGuardian(self.ctx), CodeStyleGuardian(self.ctx)],
            "test_seq": [TestPilot(self.ctx)],
            "memory_parallel": [TheCartographer(self.ctx), TheOmniContext(self.ctx)],
            "resilience_parallel": [SafetyInspector(self.ctx), SecurityEnforcer(self.ctx), PerformanceEnforcer(self.ctx)],
            "resource_safety_parallel": [ConcurrencyGuardian(self.ctx)],
            "engineering_parallel": [StructuralEngineer(self.ctx), PatternEnforcer(self.ctx), ToolsmithAgent(self.ctx)],
            "refinement_parallel": [NamingEnforcer(self.ctx), DocEnforcer(self.ctx), TypeEnforcer(self.ctx)],
            "benchmarking_seq": [BenchmarkingAgent(self.ctx)],
            "optimization_conditional": [TheStrategist(self.ctx)]
        }

    async def run_mission(self, target_scope: str = None):
        print("🚀 STARTING SUBATOMIC MISSION (Tri-Brain Enabled)")
        if target_scope:
            print(f"🎯 SURGICAL MISSION: {target_scope}")
            # Simplified scope limitation for V2
            self.ctx.python_files = [target_scope]
        
        for cycle in range(5):
            print(f"\n=== CYCLE {cycle + 1}/5 ===")
            self.ctx.signals.clear()
            self.ctx.modified_files.clear()
            
            # Execute Phases
            await self._run_phase("integrity_seq")
            await self._run_phase("curation_seq")
            await self._run_phase("test_seq")
            await self._run_phase("resilience_parallel", parallel=True)
            await self._run_phase("resource_safety_parallel", parallel=True)
            await self._run_phase("engineering_parallel", parallel=True)
            await self._run_phase("refinement_parallel", parallel=True)
            
            # Intervention Check
            if "HIGH_RISK" in self.ctx.signals:
                start_intervention_server(self.ctx)
                print("   ⏳ Waiting for approval...")
                await approval_event.wait()
                approval_event.clear()
                if "VETOED" in self.ctx.signals:
                    print("🛑 VETOED"); break

            if self._is_converged():
                print("\n✅ CONVERGENCE ACHIEVED")
                break
        
        print("\nMISSION COMPLETE")

    async def _run_phase(self, name: str, parallel: bool = False):
        agents = self.phases.get(name, [])
        if not agents: return
        print(f"\n[PHASE] {name}")
        if parallel:
            await asyncio.gather(*(a.execute() for a in agents if a.can_run()))
        else:
            for agent in agents:
                if agent.can_run(): await agent.execute()

    def _is_converged(self):
        return all(r.get("passed", False) for r in self.ctx.results.values())
