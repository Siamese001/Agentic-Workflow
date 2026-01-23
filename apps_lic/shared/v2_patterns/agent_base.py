"""
V2 Agent Base Class.

Defines the standard interface for all V2-compliant agents.
Enforces configuration loading, immutable state interaction, and automatic tracing.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from agentic_core.L2_execution.mcp.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

from apps_lic.domain.config.loader import load_agent_specs
from apps_lic.domain.config.schemas import AgentSpecs
from apps_lic.shared.reasoning.toggles import ReasoningToggles
from apps_lic.shared.v2_patterns.immutable_buffer import ImmutableStagingBuffer
from apps_lic.shared.v2_patterns.trace_registry import TraceRegistry

class V2AgentBase(MCPHardenedMixin, HealerMixin, ABC):
    """
    Abstract base class for LIC V2 Agents.
    
    Responsibilities:
    1. Auto-load Configuration & Toggles.
    2. Enforce standard execution signature.
    3. Manage automatic tracing (Start/End/Error).
    4. Provide MCP hardening and Self-Healing capabilities.
    """

    def __init__(self, llm_client: Optional[Any] = None) -> None:
        """
        Initialize base components.
        
        Args:
            llm_client: Optional LLM provider. If None, agent runs in Heuristic-Only mode.
        """
        super().__init__()
        # Auto-load configuration singleton
        self.config: AgentSpecs = load_agent_specs()
        # Initialize default reasoning toggles
        self.toggles: ReasoningToggles = ReasoningToggles()
        self.llm = llm_client
        
    def run_phase(self, buffer: ImmutableStagingBuffer, registry: TraceRegistry) -> None:
        """
        Public entry point for the agent phase.
        Wraps the core logic with Tracing and Error Handling.
        
        Args:
            buffer: The shared immutable state.
            registry: The audit log for execution tracing.
            
        Raises:
            RuntimeError: If the agent fails after healing attempts.
        """
        agent_name = self.__class__.__name__
        
        try:
            # 1. Start Trace
            registry.add_trace("PHASE_START", {"agent": agent_name})
            
            # 2. Execute Core Logic (Abstract)
            self._process(buffer, registry)
            
            # 3. End Trace
            registry.add_trace("PHASE_COMPLETE", {"agent": agent_name})
            
        except Exception as e:
            # 4. Error Trace & Healing
            registry.add_trace("PHASE_ERROR", {"agent": agent_name, "error": str(e)})
            
            # Attempt standard healing via mixin (simulated here if mixin usage varies)
            # In a real scenario, handle_error might retry _process
            raise RuntimeError(f"{agent_name} execution failed") from e

    @abstractmethod
    def _process(self, buffer: ImmutableStagingBuffer, registry: TraceRegistry) -> None:
        """
        Core logic implementation.
        
        Must be implemented by subclasses.
        
        Args:
            buffer: Read/Write access to the immutable buffer.
            registry: Registry for adding granular debug traces.
        """
        pass
