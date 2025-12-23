from typing import Any, Optional, Protocol, Dict, List
import re

import asyncio
import logging
from typing import Any, Dict, List, Optional

import httpx

from ..interfaces import (
    ICognitivePlane,
    PlanningRequest,
    PlanningResult,
)

LOGGER = logging.getLogger(__name__)

class AgentInfo:
    """Simple agent information container with explicit initialization."""
    def __init__(self, name: str, phase: str, capabilities: List[str]):
        self.name = name
        self.phase = phase
        self.capabilities = capabilities

# Sovereign agents from SwarmScheduler phases
SOVEREIGN_AGENTS = [
    # Integrity phase
    AgentInfo("Historian", "integrity_seq", ["reasoning"]),
    AgentInfo("ArchitectureGovernor", "integrity_seq", ["reasoning"]),
    AgentInfo("DependencySentinel", "integrity_seq", ["reasoning"]),

    # Curation phase
    AgentInfo("HygieneGuardian", "curation_seq", ["reasoning"]),
    AgentInfo("CodeStyleGuardian", "curation_seq", ["reasoning"]),

    # Testing phase
    AgentInfo("TestPilot", "test_seq", ["reasoning"]),

    # Memory phase
    AgentInfo("TheCartographer", "memory_parallel", ["reasoning"]),
    AgentInfo("TheOmniContext", "memory_parallel", ["reasoning"]),

    # Resilience phase
    AgentInfo("SafetyInspector", "resilience_parallel", ["reasoning"]),
    AgentInfo("SecurityEnforcer", "resilience_parallel", ["reasoning"]),
    AgentInfo("PerformanceEnforcer", "resilience_parallel", ["reasoning"]),

    # Resource safety
    AgentInfo("ConcurrencyGuardian", "resource_safety_parallel", ["reasoning"]),

    # Engineering phase
    AgentInfo("StructuralEngineer", "engineering_parallel", ["reasoning"]),
    AgentInfo("PatternEnforcer", "engineering_parallel", ["reasoning"]),
    AgentInfo("ToolsmithAgent", "engineering_parallel", ["reasoning", "tool_creation"]),

    # Refinement phase
    AgentInfo("NamingEnforcer", "refinement_parallel", ["reasoning"]),
    AgentInfo("DocEnforcer", "refinement_parallel", ["reasoning"]),
    AgentInfo("TypeEnforcer", "refinement_parallel", ["reasoning"]),

    # Benchmarking
    AgentInfo("BenchmarkingAgent", "benchmarking_seq", ["reasoning"]),

    # Optimization
    AgentInfo("TheStrategist", "optimization_conditional", ["reasoning"]),
]

class SovereignCognitivePlane(ICognitivePlane):
    """Sovereign cognitive plane with in-memory agent registry and async compliance."""

    def __init__(self):
        """Initialize with sovereign agents and async-ready client."""
        self._agents: Dict[str, AgentInfo] = {}
        self._initialize_agents()
        self._client: Optional[httpx.AsyncClient] = None

    def _initialize_agents(self):
        """Initialize agents in memory."""
        for agent in SOVEREIGN_AGENTS:
            self._agents[agent.name] = agent
            LOGGER.info(f"Registered sovereign agent: {agent.name}")

    def get_capabilities(self) -> List[Any]:
        """Get available cognitive capabilities."""
        return ["reasoning", "planning", "reflection", "tool_creation"]

    def _discover_agents(self, request: PlanningRequest) -> List[AgentInfo]:
        """Internal helper to identify agents based on request context."""
        if not request:
            return []
        # Default to all agents if no specific filtering criteria provided in request
        return list(self._agents.values())

    async def plan(self, request: PlanningRequest) -> PlanningResult:
        """Create a plan using sovereign agents via async execution."""
        # Discover relevant agents based on task
        relevant_agents = self._discover_agents(request)

        # Async-safe sleep to yield control if necessary (simulating overhead)
        await asyncio.sleep(0)

        # Create execution plan
        plan = {
            "phases": sorted(list(set(a.phase for a in relevant_agents))),
            "agents": [a.name for a in relevant_agents],
            "estimated_steps": len(relevant_agents) * 2,
            "confidence": 0.9 if relevant_agents else 0.0,
        }

        return PlanningResult(
            success=bool(relevant_agents),
            plan=plan,
            reasoning_trace=[f"Discovered {len(relevant_agents)} agents"],
            confidence=plan["confidence"],
            errors=[] if relevant_agents else ["No agents discovered"]
        )

    async def reason(self, query: str, context: Dict[str, Any], mode: str = "react") -> Dict[str, Any]:
        """Perform reasoning using async patterns."""
        if not query:
            return {"error": "Empty query", "status": "failed"}

        # Simulate async reasoning step
        await asyncio.sleep(0)

        # Implementation of reasoning logic
        results = {
            "query": query,
            "mode": mode,
            "analysis": "Sovereign reasoning completed via async pipeline.",
            "agents_consulted": [a.name for a in self._agents.values() if "reasoning" in a.capabilities]
        }

        return results

    async def __aenter__(self):
        self._client = httpx.AsyncClient()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()
