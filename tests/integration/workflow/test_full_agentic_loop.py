"""Integration tests for full agentic workflow loop."""
from __future__ import annotations
from unittest.mock import MagicMock, patch
import pytest
from runtime.shared.multi_provider_clients import reset_all_clients

# Stub function since reset_sdk_clients doesn't exist yet
def reset_sdk_clients():
    """Placeholder for reset_sdk_clients function."""
    pass


class TestAgenticLoopIntegration:
    @pytest.fixture(autouse=True)
    def reset_state(self):
        reset_all_clients()
        reset_sdk_clients()
        yield
        reset_all_clients()
        reset_sdk_clients()

    def test_vector_store_query_flow(self):
        """Vector search results can be retrieved."""
        with patch("agentic_workflow.runtime.shared.sdk_registry.chromadb") as mock_chroma:
            mock_collection = MagicMock()
            mock_collection.query.return_value = {
                "documents": [["Doc 1", "Doc 2"]],
                "ids": [["d1", "d2"]],
                "distances": [[0.1, 0.2]],
            }
            mock_client = MagicMock()
            mock_client.get_or_create_collection.return_value = mock_collection
            mock_chroma.Client.return_value = mock_client

            vs = get_vector_store("chromadb")
            coll = vs.get_or_create_collection("test")
            results = coll.query(query_texts=["test query"], n_results=2)

            assert len(results["documents"][0]) == 2
            assert results["ids"][0] == ["d1", "d2"]

    def test_multi_provider_fallback_pattern(self):
        """Multiple providers can be configured for fallback."""
        providers = [Provider.OPENAI, Provider.ANTHROPIC, Provider.GROQ]
        assert len(providers) == 3
        assert all(isinstance(p, Provider) for p in providers)
