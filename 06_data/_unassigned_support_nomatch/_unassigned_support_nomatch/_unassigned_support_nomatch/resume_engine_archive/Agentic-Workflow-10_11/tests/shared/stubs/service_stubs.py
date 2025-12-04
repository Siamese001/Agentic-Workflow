"""Service Stubs for Testing."""

class StubRAGService:
    """Stub RAG service for testing."""
    
    def __init__(self):
        self.queries = []
    
    def search(self, query, top_k=10):
        """Stub search method."""
        self.queries.append(query)
        return [{"id": f"doc_{i}", "score": 0.9 - i * 0.1} for i in range(min(top_k, 3))]

class StubLLMService:
    """Stub LLM service for testing."""
    
    def __init__(self, responses=None):
        self.responses = responses or ["Default response"]
        self.call_count = 0
    
    def generate(self, prompt):
        """Stub generate method."""
        response = self.responses[self.call_count % len(self.responses)]
        self.call_count += 1
        return response

def test_stub_rag_service():
    """Test StubRAGService."""
    rag = StubRAGService()
    results = rag.search("python developer")
    assert len(results) == 3
    assert len(rag.queries) == 1

def test_stub_llm_service():
    """Test StubLLMService."""
    llm = StubLLMService(responses=["Response A", "Response B"])
    assert llm.generate("prompt1") == "Response A"
    assert llm.generate("prompt2") == "Response B"
