"""
agentic_core/agents/base.py
Depth: 3
Role: Abstract Base Class for all SubAtomic Agents.
"""
import time
import asyncio
from agentic_core.domain.context import ValidationContext

class SubAtomicAgent:
    """Base class for all validation agents with async support."""

    def __init__(self, context: ValidationContext):
        self.ctx = context
        self.name = self.__class__.__name__

    def can_run(self) -> bool:
        """Default: Run unless a critical failure exists."""
        return "CRITICAL_FAIL" not in self.ctx.signals

    async def execute(self):
        """Execute agent's validation logic asynchronously."""
        raise NotImplementedError
    
    async def run_with_broadcast(self):
        """Wrapper that broadcasts agent lifecycle events."""
        # Set current agent context
        self.ctx._current_agent = self.name
        
        try:
            # Execute the actual agent logic
            await self.execute()
            
        except Exception as e:
            print(f"   ❌ [{self.name}] Error: {e}")
            raise
