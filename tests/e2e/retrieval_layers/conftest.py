"""Pytest configuration for retrieval layers tests."""

import os
import sys

import pytest

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


@pytest.fixture
def mock_redis_client():
    """Mock Redis client for Layer 1 tests."""
    class MockRedis:
        def __init__(self):
            self.cache = {}

        def get(self, key):
            return self.cache.get(key)

        def set(self, key, value):
            self.cache[key] = value
            return True

        def ping(self):
            return True

    return MockRedis()


@pytest.fixture
def mock_embedding_service():
    """Mock BGE-M3 embedding service for Layer 2 tests."""
    class MockEmbeddingService:
        def embed(self, text):
            # Return mock 768-dim embedding
            return [0.1] * 768

        def similarity(self, vec1, vec2):
            import math
            dot = sum(a * b for a, b in zip(vec1, vec2))
            norm1 = math.sqrt(sum(a * a for a in vec1))
            norm2 = math.sqrt(sum(a * a for a in vec2))
            return dot / (norm1 * norm2)

    return MockEmbeddingService()


@pytest.fixture
def mock_faiss_store():
    """Mock FAISS vector store for Layer 3 tests."""
    class MockFAISSStore:
        def __init__(self):
            self.vectors = {
                "chunk_1": [0.1] * 768,
                "chunk_2": [0.2] * 768,
                "chunk_3": [0.3] * 768,
            }

        def search(self, query_vector, k=5):
            # Return mock results
            return [
                ("chunk_1", 0.95),
                ("chunk_2", 0.89),
                ("chunk_3", 0.85),
            ][:k]

    return MockFAISSStore()


@pytest.fixture
def mock_adg_graph():
    """Mock ADG graph for Layer 3 tests."""
    class MockADGGraph:
        def __init__(self):
            self.edges = {
                "chunk_1": [("chunk_4", "calls"), ("chunk_5", "imports")],
                "chunk_2": [("chunk_6", "references")],
            }

        def expand(self, chunk_id):
            return self.edges.get(chunk_id, [])

    return MockADGGraph()


@pytest.fixture
def mock_langgraph_orchestrator():
    """Mock LangGraph orchestrator for Layer 4 tests."""
    class MockLangGraph:
        def execute(self, plan):
            return {
                "steps_executed": len(plan.get("steps", [])),
                "success": True,
                "results": [],
            }

    return MockLangGraph()


@pytest.fixture
def mock_llm_client():
    """Mock LLM client for Layer 5 tests."""
    class MockLLMClient:
        def generate(self, prompt, context=None):
            return {
                "generated_text": f"Response to: {prompt[:50]}...",
                "tokens_used": 150,
                "model": "gpt-4-mock",
            }

    return MockLLMClient()


@pytest.fixture
def sample_query():
    """Sample query for testing."""
    return "How do I implement caching in Python?"


@pytest.fixture
def layer_telemetry():
    """Sample telemetry data structure."""
    return {
        "l1": {"hit": False, "latency_ms": 0.5, "timestamp": 1234567890},
        "l2": {"hit": False, "latency_ms": 15.0, "timestamp": 1234567891},
        "l3": {"hit": True, "latency_ms": 150.0, "chunks": 3, "timestamp": 1234567892},
    }
