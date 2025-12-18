"""
Base Agent for Outreach Engine

Provides the abstract base class for all outreach agents.
"""

from abc import ABC, abstractmethod
from typing import Optional

from .context import OutreachEngineContext


class OutreachAgent(ABC):
    """
    Abstract base class for all outreach agents.
    
    Each agent:
    - Has a name and description
    - Operates on the shared context
    - Can add signals and record results
    - Implements execute() for its specific logic
    """
    
    def __init__(self, ctx: OutreachEngineContext):
        self.ctx = ctx
        self.name = self.__class__.__name__
        self.description = self.__doc__ or "No description"
    
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
            return "\n".join(f"- {i}" for i in instructions)
        return ""
    
    async def call_llm(self, prompt: str) -> Optional[str]:
        """Call the LLM if available."""
        if not self.ctx.intelligence_enabled or not self.ctx.gemini_model:
            return None
        
        try:
            response = self.ctx.gemini_model.generate_content(prompt)
            self.ctx.budget.record_llm_call(len(prompt) + len(response.text))
            return response.text
        except Exception as e:
            print(f"   [{self.name}] ⚠️ LLM call failed: {e}")
            return None
