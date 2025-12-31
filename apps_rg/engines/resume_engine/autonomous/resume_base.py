"""
ResumeAgent - Base class for all autonomous resume generation agents.

All specialized agents inherit from this base class and implement
the execute() method for their specific functionality.
"""
from typing import Any, Optional, Protocol, Dict, List


import asyncio
from abc import ABC, abstractmethod
from typing import Any, Optional

from .context import ResumeEngineContext


class ResumeAgent(ABC):
    """
    Base class for all resume generation agents.

    Each agent has:
    - A reference to the shared context
    - A name for identification
    - An execute() method that performs the agent's work
    """

    def __init__(self, ctx: ResumeEngineContext):
        self.ctx = ctx
        self.name = self.__class__.__name__

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

    async def call_llm(self, prompt: str, max_tokens: int = 2000) -> Optional[str]:
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
