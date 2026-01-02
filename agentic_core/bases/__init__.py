"""
Consolidated Layer Base Classes - Single Source of Truth

Each layer has ONE base class with ALL standard capabilities:
- HealerMixin: Self-healing via heal_repository()
- MCPHardenedMixin: Hardened MCP operations with retry/timeout
- L{N}SubatomicTestingMixin: Layer-specific testing capabilities

Usage:
    from agentic_core.bases import L2Agent, L3Agent, L4Agent, L5Agent
    
    class MyExecutionAgent(L2Agent):
        pass  # Automatically has healing, MCP, testing
"""

from agentic_core.bases.l0_agent import L0Agent
from agentic_core.bases.l1_agent import L1Agent
from agentic_core.bases.l2_agent import L2Agent
from agentic_core.bases.l3_agent import L3Agent
from agentic_core.bases.l4_agent import L4Agent
from agentic_core.bases.l5_agent import L5Agent

__all__ = ["L0Agent", "L1Agent", "L2Agent", "L3Agent", "L4Agent", "L5Agent"]
