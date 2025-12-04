"""Shared Fake LLM for Deterministic Testing."""

class FakeLLM:
    """Deterministic fake LLM for testing."""
    
    def __init__(self, responses=None):
        self.responses = responses or ["Default fake response"]
        self.call_count = 0
    
    def generate(self, prompt):
        """Generate deterministic response."""
        response = self.responses[self.call_count % len(self.responses)]
        self.call_count += 1
        return response
    
    def reset(self):
        """Reset call count."""
        self.call_count = 0

def test_fake_llm_deterministic():
    """Test FakeLLM produces deterministic responses."""
    llm = FakeLLM(responses=["Response A", "Response B"])
    
    assert llm.generate("prompt1") == "Response A"
    assert llm.generate("prompt2") == "Response B"
    assert llm.generate("prompt3") == "Response A"
    
    llm.reset()
    assert llm.call_count == 0
