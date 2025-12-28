import asyncio
import os
import re

import uvicorn

try:
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

from agentic_core.agents.engineering import PatternEnforcer, StructuralEngineer
from agentic_core.agents.governance import ArchitectureGovernor, DependencySentinel
from agentic_core.agents.infrastructure import BenchmarkingAgent, Historian
from agentic_core.agents.quality import (
    CodeStyleGuardian,
    HygieneGuardian,
    PerformanceEnforcer,
)
from agentic_core.agents.repair import TestPilot, ToolsmithAgent
from agentic_core.agents.security import (
    ConcurrencyGuardian,
    SafetyInspector,
    SecurityEnforcer,
)
from agentic_core.agents.specialized import (
    DocEnforcer,
    NamingEnforcer,
    TheCartographer,
    TheOmniContext,
    TheStrategist,
    TypeEnforcer,
)

# Import Domain
from agentic_core.L1_cognition.P2_domain.context import ValidationContext

# Global Event for Intervention
approval_event = asyncio.Event()
_intervention_context = None

if FASTAPI_AVAILABLE:
    intervention_app = FastAPI(title="L5 Intervention UI")

    @intervention_app.get("/", response_class=HTMLResponse)
    async def get_dashboard():
        ctx = _intervention_context
        signals = list(ctx.signals) if ctx else []
        return f"""<html><body><h1>[ALERT] L5 INTERVENTION REQUIRED</h1>
        <p>Signals: {signals}</p>
        <button onclick="fetch('/approve', {{method:'POST'}})">APPROVE</button>
        <button onclick="fetch('/veto', {{method:'POST'}})">VETO</button>
        </body></html>"""

    @intervention_app.post("/approve")
    async def approve_action():
        approval_event.set()
        return {"status": "APPROVED"}

    @intervention_app.post("/veto")
    async def veto_action():
        if _intervention_context:
            _intervention_context.signals.add("VETOED")
        approval_event.set()
        return {"status": "VETOED"}


async def start_intervention_server(ctx):
    global _intervention_context
    _intervention_context = ctx
    if FASTAPI_AVAILABLE:
        host = os.getenv("INTERVENTION_HOST", "127.0.0.1")
        port = int(os.getenv("INTERVENTION_PORT", "8080"))
        config = uvicorn.Config(
            intervention_app,
            host=host,
            port=port,
            log_level="error"
        )
        server = uvicorn.Server(config)
        # Replaced blocking thread with async background task
        asyncio.create_task(server.serve())
        print(f"   🌐 Intervention server at http://{host}:{port}")


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
        print("[START] STARTING SUBATOMIC MISSION (Tri-Brain Enabled)")
        if target_scope:
            print(f"🎯 SURGICAL MISSION: {target_scope}")
            self.ctx.python_files = [target_scope]

        await start_intervention_server(self.ctx)

        for cycle in range(5):
            print(f"\n=== CYCLE {cycle + 1}/5 ===")
            self.ctx.signals.clear()

            # Sequential Integrity and Curation
            for agent in self.phases["integrity_seq"]:
                await agent.run()
            for agent in self.phases["curation_seq"]:
                await agent.run()

            # Parallel Context and Resilience Analysis
            await asyncio.gather(*(agent.run() for agent in self.phases["memory_parallel"]))
            await asyncio.gather(*(agent.run() for agent in self.phases["resilience_parallel"]))
            await asyncio.gather(*(agent.run() for agent in self.phases["resource_safety_parallel"]))

            if "INTERVENTION_REQUIRED" in self.ctx.signals:
                print("✋ INTERVENTION REQUIRED. Waiting for human approval...")
                await approval_event.wait()
                approval_event.clear()
                if "VETOED" in self.ctx.signals:
                    print("🛑 MISSION VETOED BY HUMAN.")
                    return

            # Parallel Engineering and Refinement
            await asyncio.gather(*(agent.run() for agent in self.phases["engineering_parallel"]))
            await asyncio.gather(*(agent.run() for agent in self.phases["refinement_parallel"]))

            # Testing and Final Benchmarking
            for agent in self.phases["test_seq"]:
                await agent.run()

            if cycle == 4:
                for agent in self.phases["benchmarking_seq"]:
                    await agent.run()
                if "OPTIMIZE" in self.ctx.signals:
                    for agent in self.phases["optimization_conditional"]:
                        await agent.run()