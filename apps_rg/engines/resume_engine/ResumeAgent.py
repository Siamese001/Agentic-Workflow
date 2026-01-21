from __future__ import annotations

"""
ResumeAgent - Base class for all autonomous resume generation agents.

All specialized agents inherit from this base class and implement
the execute() method for their specific functionality.
"""
import asyncio
from abc import ABC, abstractmethod
from typing import Any

from agentic_core.L0_maintenance.mixins.subatomic_testing_mixin import SubatomicTestingMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin

from agentic_core.schemas.models.anomaly_report import AnomalyReport
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout

from .context import ResumeEngineContext


class ResumeAgent(MCPHardenedMixin, HealerMixin, SubatomicTestingMixin, ABC):
    """
    Base class for all resume generation agents.

    Each agent has:
    - A reference to the shared context
    - A name for identification
    - An execute() method that performs the agent's work
    """

    def __init__(self, ctx: ResumeEngineContext) -> None:
        super().__init__()
        self.ctx = ctx
        self.name = self.__class__.__name__
        self._mcp_audit("init")

    def _run_self_tests(self) -> bool:
        """Run self-tests for ResumeAgent."""
        super()._run_self_tests()

        # Verify context is valid
        assert self.ctx is not None, "Context must not be None"
        assert self.name, "Agent name must be set"

        # Verify signals interface
        assert hasattr(self.ctx, 'signals'), "Context must have signals"
        assert hasattr(self.ctx, 'record_result'), "Context must have record_result"

        return True

    def _perform_healing(self, anomaly: AnomalyReport) -> bool:
        """Perform healing for detected anomalies."""
        self._mcp_audit("healing_start", payload=anomaly.to_dict())

        if anomaly.type == "context_corruption":
            # Reset context state
            self.ctx.signals.clear()
            self._mcp_audit("healing_success")
            return True

        if anomaly.type == "budget_exhausted":
            # Reset budget tracking
            self.ctx.budget.reset() if hasattr(self.ctx, 'budget') else None
            self._mcp_audit("healing_success")
            return True

        return False

    @abstractmethod
    async def execute(self) -> None:
        """
        Execute the agent's primary function.

        Implementations should:
        1. Read state from self.ctx
        2. Perform their specific validation/transformation
        3. Update self.ctx.signals with any issues found
        4. Record results via self.ctx.record_result()
        """
        raise NotImplementedError

    def log(self, message: str):
        """Log a message with agent name prefix."""
        print(f"   [{self.name}] {message}")

    def add_signal(self, signal: str):
        """Add a signal to the context."""
        self.ctx.add_signal(signal)
        self.log(f"📡 Signal: {signal}")

    def remove_signal(self, signal: str):
        """Remove a signal from the context."""
        self.ctx.remove_signal(signal)

    def record_pass(self, details: str = "", data: Any = None):
        """Record a passing result."""
        self.ctx.record_result(self.name, passed=True, details=details, data=data)
        self.log(f"✅ {details or 'Passed'}")

    def record_fail(self, details: str, data: Any = None):
        """Record a failing result."""
        self.ctx.record_result(self.name, passed=False, details=details, data=data)
        self.log(f"❌ {details}")

    async def call_llm(self, prompt: str, max_tokens: int = 2000) -> str | None:
        """
        Call the LLM with budget checking.

        Returns the response text or None if budget exceeded or error.
        """
        if not self.ctx.intelligence_enabled:
            self.log("⚠️ LLM not available")
            return None

        if not self.ctx.budget.check_budget():
            self.log(f"💸 Budget exceeded (${self.ctx.budget.current_cost:.4f}/${self.ctx.budget.max_cost})")
            return None

        try:
            response = await asyncio.to_thread(
                self.ctx.client.GenerativeModel(self.ctx.model_id).generate_content,
                prompt
            )

            # Track tokens (estimate if not available)
            input_tokens = len(prompt.split()) * 1.3  # Rough estimate
            output_tokens = len(response.text.split()) * 1.3 if response.text else 0

            cost = self.ctx.budget.track_tokens(
                self.ctx.model_id,
                int(input_tokens),
                int(output_tokens)
            )

            self.log(f"💰 LLM call cost: ${cost:.6f}")

            return response.text if response.text else None

        except Exception as e:
            self.log(f"⚠️ LLM error: {e}")
            return None

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: set | None = None) -> dict[str, int]:
        """Apps_rg/resume_engine base agent - fully chained healing."""
        # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
        super().heal_repository()

        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] Apps_rg/resume_engine - operational with shared chain")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)
