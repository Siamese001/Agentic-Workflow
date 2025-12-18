"""Sovereign Cognitive Plane Implementation with L5 Streamer Integration.

Bypasses corrupted registry files with a minimal in-memory implementation.
Includes live reasoning broadcast capabilities.
"""

import asyncio
import logging
import re
from typing import Any, Dict, List, Optional

from agentic_core.interfaces import (
    ICognitivePlane,
    PlanningRequest,
    PlanningResult,
)

LOGGER = logging.getLogger(__name__)


# Minimal dataclass for agent info
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
            except ImportError:
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
        return ["reasoning", "planning", "reflection", "tool_creation"]
    
    async def plan(self, request: PlanningRequest) -> PlanningResult:
        """Create a plan using sovereign agents."""
        # Broadcast planning start
        if self._streamer:
            await self._streamer.broadcast_agent_start("SovereignCognitivePlane", "Planning execution")
        
        # Discover relevant agents based on task
        relevant_agents = self._discover_agents(request)
        
        # Create execution plan
        plan = {
            "phases": list(set(a.phase for a in relevant_agents)),
            "agents": [a.name for a in relevant_agents],
            "estimated_steps": len(relevant_agents) * 2,
            "confidence": 0.9 if relevant_agents else 0.0,
        }
        
        result = PlanningResult(
            success=bool(relevant_agents),
            plan=plan,
            reasoning_trace=[f"Discovered {len(relevant_agents)} agents"],
            confidence=plan["confidence"],
            errors=[] if relevant_agents else ["No agents discovered"]
        )
        
        # Broadcast planning complete
        if self._streamer:
            await self._streamer.broadcast_agent_complete("SovereignCognitivePlane", f"Planning complete: {len(relevant_agents)} agents")
        
        return result
    
    async def reason(self, query: str, context: Dict[str, Any], mode: str = "react") -> Dict[str, Any]:
        """Perform reasoning with L5 broadcast."""
        reasoning_text = f"Sovereign reasoning: {query}"
        
        # Broadcast reasoning
        if self._streamer:
            # Wrap in reasoning tags for extraction
            wrapped_reasoning = f"<reasoning>{reasoning_text}</reasoning>"
            await self._streamer.broadcast_reasoning(wrapped_reasoning, agent="SovereignCognitivePlane")
        
        return {
            "query": query,
            "context": context,
            "mode": mode,
            "reasoning": reasoning_text,
            "state_updates": {},
            "mission_complete": False,
        }
    
    async def interpret(self, results: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Interpret results with L5 broadcast."""
        if self._streamer:
            await self._streamer.broadcast(f"Interpreting {len(results)} results", agent="SovereignCognitivePlane")
        
        return {
            "results": results,
            "context": context,
            "interpretation": "Sovereign interpretation complete",
            "state_updates": {},
            "mission_complete": False,
        }
    
    async def reflect(self, execution_trace: List[Dict[str, Any]], outcome: Dict[str, Any]) -> Dict[str, Any]:
        """Reflect on execution with L5 broadcast."""
        if self._streamer:
            await self._streamer.broadcast("Reflecting on execution trace", agent="SovereignCognitivePlane")
        
        phase_stats = {}
        for trace in execution_trace:
            phase = trace.get("phase", "unknown")
            if phase not in phase_stats:
                phase_stats[phase] = {"total": 0, "passed": 0}
            phase_stats[phase]["total"] += 1
            if trace.get("passed", False):
                phase_stats[phase]["passed"] += 1
        
        reflection = "Sovereign reflection complete"
        
        # Broadcast reflection insights
        if self._streamer:
            success_rate = sum(s["passed"] for s in phase_stats.values()) / sum(s["total"] for s in phase_stats.values()) if phase_stats else 0
            await self._streamer.broadcast(f"Reflection: {success_rate:.1%} success rate", agent="SovereignCognitivePlane")
        
        return {
            "reflection": reflection,
            "phase_stats": phase_stats,
            "recommendations": ["Continue with next phase" if all(s["passed"] == s["total"] for s in phase_stats.values()) else "Review failures"]
        }
    
    async def broadcast_agent_thought(self, agent_name: str, thought: str):
        """Broadcast a thought from a specific agent."""
        if self._streamer:
            wrapped_thought = f"<reasoning>{thought}</reasoning>"
            await self._streamer.broadcast_reasoning(wrapped_thought, agent=agent_name)
    
    def _discover_agents(self, request: PlanningRequest) -> List[AgentInfo]:
        """Discover agents relevant to the request."""
        # Simple discovery based on request content
        relevant = []
        
        # Look for keywords in request
        request_text = str(request).lower()
        
        for agent in self._agents.values():
            # Check if agent capabilities match request needs
            if "reasoning" in agent.capabilities:
                relevant.append(agent)
        
        return relevant


def create_sovereign_cognitive_plane(enable_streaming: bool = True) -> SovereignCognitivePlane:
    """Factory function to create a sovereign cognitive plane."""
    return SovereignCognitivePlane(enable_streaming=enable_streaming)
