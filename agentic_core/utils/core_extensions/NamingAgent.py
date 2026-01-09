"""
NamingAgent - Agent for handling naming conventions and validation.

Re-exported from L5_safety for backwards compatibility.
"""
TREE_SITTER_AVAILABLE = False  # Stub - tree-sitter not required for tests


class PlacementResult:
    """Result of placement analysis."""
    def __init__(self, path: str = "", confidence: float = 1.0):
        self.path = path
        self.confidence = confidence
        self.suggestions = []


try:
    from agentic_core.L5_safety.validators.NamingAgent import NamingAgent
except ImportError:
    # Stub implementation if original not available
    class NamingAgent:
        """Stub NamingAgent for backwards compatibility."""
        def __init__(self, *args, **kwargs):
            pass
        def validate_name(self, name: str) -> bool:
            return True
        def suggest_name(self, context: str) -> str:
            return context
        def analyze_placement(self, code: str) -> PlacementResult:
            return PlacementResult()

def get_naming_agent():
    """Get a NamingAgent instance."""
    return NamingAgent()

__all__ = ['NamingAgent', 'get_naming_agent', 'TREE_SITTER_AVAILABLE', 'PlacementResult']
