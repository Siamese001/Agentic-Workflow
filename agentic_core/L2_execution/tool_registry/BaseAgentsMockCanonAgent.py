"""
Mock Canon Base Agent - L2 Execution (Phase 11 – Dec 26, 2025)
Standard mock for cognitive testing without LLM costs.

DDD Compliance:
- Implements CanonBaseAgentInterface from SharedContracts
- Zero-cost alternative for unit testing L1 cognition
- Enables architectural testing without external dependencies
"""
from typing import Any, Dict, List
from apps_shared.class_agent_interface import CanonBaseAgentInterface

class BaseAgentsMockCanonAgent:
    """
    Zero-cost mock implementation for architectural testing.
    
    Phase 11: Configurable Implementation Factory
    - Enables unit testing of L1 cognition without LLM API calls
    - Provides deterministic responses for test scenarios
    - Maintains interface compatibility with real implementation
    """

    def __init__(self, ctx=None):
        """
        Initialize mock agent with optional context.
        
        Args:
            ctx: Optional context object (typically None for pure unit tests)
        """
        self.ctx = ctx
        self.name = 'MockAgent'
        self._capabilities = ['mock_action', 'mock_validation', 'mock_execution']
        self._state_valid = True

    async def execute(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mock execution - returns success without actual processing.
        Args:
            goal: The goal to execute (logged but not processed)
            context: Execution context (logged but not processed)
            
        Returns:
            Dict with mock success response
        """
        return {'status': 'success', 'goal': goal, 'mode': 'mock', 'agent': self.name, 'message': 'Mock execution completed successfully'}

    def get_capabilities(self) -> List[str]:
        """
        Return mock capabilities list.
        
        Returns:
            List of mock capability strings
        """
        return self._capabilities

    def validate_state(self) -> bool:
        """
        Mock state validation - always returns True unless explicitly set.
        
        Returns:
            Boolean indicating mock state validity
        """
        return self._state_valid

    def set_state_valid(self, valid: bool) -> Any:
        """
        Setter for testing state validation failures.
        
        Args:
            valid: Whether the mock should report valid state
        """
        self._state_valid = valid

    def add_capability(self, capability: str) -> Any:
        """
        Add a mock capability for testing.
        
        Args:
            capability: Capability string to add
        """
        if capability not in self._capabilities:
            self._capabilities.append(capability)

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f'MockCanonBaseAgent(name={self.name}, capabilities={len(self._capabilities)})'
