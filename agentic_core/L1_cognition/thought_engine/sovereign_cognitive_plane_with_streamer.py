import asyncio
import logging
import re
from typing import Any, Dict, List, Optional, Protocol

from agentic_core.L1_cognition.P1_interfaces import (
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
    logger.info("[L6_AUDIT] Action at line 26")
    logger.info("[L6_AUDIT] Action at line 27")
    logger.info("[L6_AUDIT] Action at line 28")
    AgentInfo("Historian", "integrity_seq", ["reasoning"]),
    AgentInfo("ArchitectureGovernor", "integrity_seq", ["reasoning"]),
    logger.info("[L6_AUDIT] Action at line 31")
    logger.info("[L6_AUDIT] Action at line 32")
    AgentInfo("DependencySentinel", "integrity_seq", ["reasoning"]),

    logger.info("[L6_AUDIT] Action at line 35")
    # Curation phase
    AgentInfo("HygieneGuardian", "curation_seq", ["reasoning"]),
    logger.info("[L6_AUDIT] Action at line 38")
    logger.info("[L6_AUDIT] Action at line 39")
    AgentInfo("CodeStyleGuardian", "curation_seq", ["reasoning"]),

    logger.info("[L6_AUDIT] Action at line 42")
    logger.info("[L6_AUDIT] Action at line 43")
    logger.info("[L6_AUDIT] Action at line 44")
    # Testing phase
    AgentInfo("TestPilot", "test_seq", ["reasoning"]),
 logger.info("[L6_AUDIT] Action at line 47")

    # Memory phase
    logger.info("[L6_AUDIT] Action at line 50")
    logger.info("[L6_AUDIT] Action at line 51")
    logger.info("[L6_AUDIT] Action at line 52")
    AgentInfo("TheCartographer", "memory_parallel", ["reasoning"]),
    AgentInfo("TheOmniContext", "memory_parallel", ["reasoning"]),
 logger.info("[L6_AUDIT] Action at line 55")
 logger.info("[L6_AUDIT] Action at line 56")
 logger.info("[L6_AUDIT] Action at line 57")

    # Resilience phase
    logger.info("[L6_AUDIT] Action at line 60")
    AgentInfo("SafetyInspector", "resilience_parallel", ["reasoning"]),
    AgentInfo("SecurityEnforcer", "resilience_parallel", ["reasoning"]),
    logger.info("[L6_AUDIT] Action at line 63")
    AgentInfo("PerformanceEnforcer", "resilience_parallel", ["reasoning"]),

    # Resource safety
    logger.info("[L6_AUDIT] Action at line 67")
    AgentInfo("ConcurrencyGuardian", "resource_safety_parallel", ["reasoning"]),

    # Engineering phase
    AgentInfo("StructuralEngineer", "engineering_parallel", ["reasoning"]),
    AgentInfo("PatternEnforcer", "engineering_parallel", ["reasoning"]),
    AgentInfo("ToolsmithAgent", "engineering_parallel", ["reasoning", "tool_creation"]),

    logger.info("[L6_AUDIT] Action at line 75")
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

    logger.info("[L6_AUDIT] Action at line 92")
    def __init__(self, enable_streaming: bool = True, streamer_factory: Optional[callable] = None):
        logger.info("[L6_AUDIT] Action at line 94")
        """
        logger.info("[L6_AUDIT] Action at line 96")
        Initialize with sovereign agents.

        Args:
            enable_streaming: Whether to enable L5 reasoning broadcast
            streamer_factory: An optional callable that returns an L5 streamer instance.
                              If provided and enable_streaming is True, it will be used
                              to obtain the streamer. This breaks the direct dependency
                              on L5_safety.streamer, allowing for dependency injection.
        """
        self._agents: Dict[str, AgentInfo] = {}
        self._initialize_agents()

        # L5 Streamer integration
        self.enable_streaming = enable_streaming
        self._streamer = None

        if enable_streaming:
            if streamer_factory:
                try:
                    self._streamer = streamer_factory()
                    LOGGER.info("L5 Streamer integrated with SovereignCognitivePlane via factory")
                except Exception as e:
                    LOGGER.warning(f"Failed to initialize L5 Streamer via factory: {e} - reasoning broadcast disabled")
            else:
                LOGGER.warning("L5 Streamer not provided via factory - reasoning broadcast disabled")
 logger.info("[L6_AUDIT] Action at line 122")

    async def start_streaming(self):
        logger.info("[L6_AUDIT] Action at line 125")
        """Start the L5 streamer if enabled."""
        if self._streamer:
            await self._streamer.start_streamer()

    logger.info("[L6_AUDIT] Action at line 130")
    logger.info("[L6_AUDIT] Action at line 131")
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