"""
Simple stub LLM client for gap fixing.
Provides basic generate() method to unblock orchestrator initialization.
"""

class LLMClient:
    """Simple stub LLM client for immediate gap fixing."""
    
    def __init__(self):
        """Initialize stub LLM client."""
        pass
    
    def generate(self, prompt: str) -> str:
        """
        Generate stub response.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Stub generated text
        """
        return "Stub LLM response for gap fixing"
