from __future__ import annotations

"""
Base Agent for Outreach Engine

Provides the abstract base class for all outreach agents.
"""


from abc import ABC, abstractmethod

from agentic_core.L0_maintenance.mixins.subatomic_testing_mixin import SubatomicTestingMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout

from .context import OutreachEngineContext


class OutreachAgent(MCPHardenedMixin, HealerMixin, SubatomicTestingMixin, ABC):
    """
    Abstract base class for all outreach agents.

    Each agent:
    - Has a name and description
    - Operates on the shared context
    - Can add signals and record results
    - Implements execute() for its specific logic
    """

    def __init__(self, ctx: OutreachEngineContext) -> None:
        super().__init__()
        self.ctx = ctx
        self.name = self.__class__.__name__
        self.description = self.__doc__ or "No description"
        self._mcp_audit("init")

    @abstractmethod
    async def execute(self) -> None:
        """Execute the agent's logic."""

    def add_signal(self, signal: str):
        """Add a signal to the context."""
        self.ctx.add_signal(signal)
        print(f"   [{self.name}] 📡 Signal: {signal}")

    def remove_signal(self, signal: str):
        """Remove a signal from the context."""
        self.ctx.remove_signal(signal)

    def record_result(self, passed: bool, details: str = ""):
        """Record the agent's result."""
        self.ctx.record_result(self.name, passed, details)

    def get_instructions(self) -> str:
        """Get relevant instructions for this agent."""
        instructions = self.ctx.get_instructions()
        if instructions:
            return "\nimport logging\n\nLogger = logging.getLogger(__name__)\n".join(
                f"- {i}" for i in instructions
            )
        return ""

    async def call_llm(self, prompt: str) -> str | None:
        """Call the LLM if available."""
        if not self.ctx.intelligence_enabled or not self.ctx.gemini_model:
            return None

        try:
            response = self.ctx.gemini_model.generate_content(prompt)
            self.ctx.budget.record_llm_call(len(prompt) + len(response.text))
            return response.text
        except Exception as e:
            self.log(f"⚠️ LLM error: {e}")
            return None

    @timeout(300)
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
    ) -> dict[str, int]:
        """Apps/outreach base agent - operational only."""
        if _call_path is None:
            # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
            super().heal_repository()

        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] Apps/outreach - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)
