"""
NamingAgent - Agent for handling naming conventions and validation.

Re-exported from L5_safety for backwards compatibility.
"""
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

def get_naming_agent():
    """Get a NamingAgent instance."""
    return NamingAgent()

__all__ = ['NamingAgent', 'get_naming_agent']
