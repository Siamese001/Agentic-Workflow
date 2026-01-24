"""
RG Agent Base Class - LIC-Aligned Sovereign Architecture.

Defines the standard interface for all RG Sovereign Architecture agents.
Enforces configuration loading, immutable state interaction, and automatic tracing.
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import Any

from agentic_core.L2_execution.mcp.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.base_agents.healer_mixin import HealerMixin
from apps_rg.domain.config.loader import load_rg_specs
from apps_rg.domain.config.schemas import RGAgentSpecs
from apps_rg.shared.reasoning.toggles import ReasoningToggles
from apps_rg.shared.core.immutable_buffer import ImmutableStagingBuffer
from apps_rg.shared.core.trace_registry import TraceRegistry


class RGAgentBase(MCPHardenedMixin, HealerMixin, ABC):
    """
    Abstract base class for RG Sovereign Architecture Agents.

    Responsibilities:
    1. Auto-load configuration & Toggles.
    2. Enforce standard execution signature.
    3. Manage automatic tracing (Start/End/Error).
    4. Provide MCP hardening and Self-Healing capabilities.

    Aligned with LIC LICAgentBase pattern.
    """

    def __init__(self, llm_client: Any | None = None) -> None:
        """
        Initialize base components.

        Args:
            llm_client: Optional LLM provider. If None, agent runs in Heuristic-Only mode.
        """
        super().__init__()
        self.config: RGAgentSpecs = load_rg_specs()
        self.toggles: ReasoningToggles = ReasoningToggles()
        self.llm = llm_client

    def run_phase(self, buffer: ImmutableStagingBuffer, registry: TraceRegistry) -> None:
        """
        Public entry point for the agent phase (synchronous wrapper).
        Wraps the core logic with Tracing and Error Handling.

        Args:
            buffer: The shared immutable state.
            registry: The audit log for execution tracing.

        Raises:
            RuntimeError: If the agent fails after healing attempts.
        """
        agent_name = self.__class__.__name__

        try:
            registry.add_trace("PHASE_START", {"agent": agent_name})

            # Run async _process in sync context
            asyncio.run(self._process(buffer, registry))

            registry.add_trace("PHASE_COMPLETE", {"agent": agent_name})

        except Exception as e:
            registry.add_trace("PHASE_ERROR", {"agent": agent_name, "error": str(e)})
            raise RuntimeError(f"{agent_name} execution failed") from e

    async def run_phase_async(
        self, buffer: ImmutableStagingBuffer, registry: TraceRegistry
    ) -> None:
        """
        Public entry point for the agent phase (async version).
        Wraps the core logic with Tracing and Error Handling.

        Args:
            buffer: The shared immutable state.
            registry: The audit log for execution tracing.

        Raises:
            RuntimeError: If the agent fails after healing attempts.
        """
        agent_name = self.__class__.__name__

        try:
            registry.add_trace("PHASE_START", {"agent": agent_name})
            await self._process(buffer, registry)
            registry.add_trace("PHASE_COMPLETE", {"agent": agent_name})

        except Exception as e:
            registry.add_trace("PHASE_ERROR", {"agent": agent_name, "error": str(e)})
            raise RuntimeError(f"{agent_name} execution failed") from e

    @abstractmethod
    async def _process(self, buffer: ImmutableStagingBuffer, registry: TraceRegistry) -> None:
        """
        Core logic implementation (async).

        Must be implemented by subclasses.

        Args:
            buffer: Read/Write access to the immutable buffer.
            registry: Registry for adding granular debug traces.
        """
        pass

    async def call_llm(self, prompt: str, system_message: str | None = None) -> str | None:
        """
        Hardened LLM invocation with budget tracking.

        Args:
            prompt: The prompt to send to the LLM.
            system_message: Optional system message.

        Returns:
            LLM response or None if unavailable/budget exhausted.
        """
        if not self.llm:
            return None

        try:
            if hasattr(self.llm, "generate"):
                return await self.llm.generate(prompt, system_message=system_message)
            elif hasattr(self.llm, "analyze"):
                return self.llm.analyze(prompt, {})
            return None
        except Exception:
            return None

    def heal_repository(self) -> dict[str, int]:
        """
        V2 Self-Healing.

        The base class handles Mixin logic. Subclasses can add domain-specific checks.
        """
        return super().heal_repository()
