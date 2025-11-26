"""Deterministic Fake LLM for Testing."""

class DeterministicFakeLLM:
    """Deterministic fake LLM for testing."""
    
    def __init__(self, responses=None):
        self.responses = responses or ["Default fake LLM response"]
        self.call_count = 0
        self.prompts = []
    
    def generate(self, prompt, **kwargs):
        """Generate deterministic response."""
        self.prompts.append(prompt)
        response = self.responses[self.call_count % len(self.responses)]
        self.call_count += 1
        return {
            "content": response,
            "tokens_used": len(response.split()),
            "model": "fake-llm-v1"
        }
    
    def reset(self):
        """Reset call count and prompts."""
        self.call_count = 0
        self.prompts = []

def test_deterministic_fake_llm():
    """Test DeterministicFakeLLM produces deterministic responses."""
    llm = DeterministicFakeLLM(responses=["Response A", "Response B", "Response C"])
    
    result1 = llm.generate("prompt1")
    assert result1["content"] == "Response A"
    
    result2 = llm.generate("prompt2")
    assert result2["content"] == "Response B"
    
    result3 = llm.generate("prompt3")
    assert result3["content"] == "Response C"
    
    result4 = llm.generate("prompt4")
    assert result4["content"] == "Response A"
    
    assert llm.call_count == 4
    assert len(llm.prompts) == 4
    
    llm.reset()
    assert llm.call_count == 0
