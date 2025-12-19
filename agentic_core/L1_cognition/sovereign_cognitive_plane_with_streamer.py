import asyncio
import httpx
import logging
from typing import Any, Dict, List

from agentic_core.interfaces import (
    ICognitivePlane,
    PlanningRequest,
    PlanningResult,
)

LOGGER = logging.getLogger(__name__)


class AgentInfo:
    """Simple agent information container."""
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
    """Sovereign cognitive plane with in-memory agent registry and L5 streaming."""
    
    def __init__(self, enable_streaming: bool = True):
        """
        Initialize with sovereign agents.
        
        Args:
            enable_streaming: Whether to enable L5 reasoning broadcast
        """
        self._agents: Dict[str, AgentInfo] = {}
        self._initialize_agents()
        
        # L5 Streamer integration
        self.enable_streaming = enable_streaming
        self._streamer = None
        
        if enable_streaming:
            try:
                from agentic_core.L5_safety.streamer import get_l5_streamer
                self._streamer = get_l5_streamer()
                LOGGER.info("L5 Streamer integrated with SovereignCognitivePlane")
            except (ImportError, ModuleNotFoundError):
                LOGGER.warning("L5 Streamer not available - reasoning broadcast disabled")
    
    async def start_streaming(self):
        """Start the L5 streamer if enabled."""
        if self._streamer:
            await self._streamer.start_streamer()
    
    async def stop_streaming(self):
        """Stop the L5 streamer."""
        if self._streamer:
            await self._streamer.stop_streamer()
    
    def _initialize_agents(self):
        """Initialize agents in memory."""
        for agent in SOVEREIGN_AGENTS:
            self._agents[agent.name] = agent
            LOGGER.info(f"Registered sovereign agent: {agent.name}")
    
    def get_capabilities(self) -> List[Any]:
        """Get available cognitive capabilities."""
        capabilities = set()
        for agent in self._agents.values():
            for cap in agent.capabilities:
                capabilities.add(cap)
        return list(capabilities)

    async def plan(self, request: PlanningRequest) -> PlanningResult:
        """Async plan implementation replacing blocking logic."""
        if self._streamer:
            await self._streamer.broadcast_reasoning(f"Processing planning request: {request.task_id}")
        
        # Simulate async processing
        await asyncio.sleep(0)
        
        return PlanningResult(
            plan_id=f"sovereign_{request.task_id}",
            steps=["analyze_context", "select_agents", "generate_strategy"]
        )