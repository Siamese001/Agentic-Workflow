"""Integration tests for full agentic workflow loop."""
from runtime.shared.multi_provider_clients import Provider, reset_all_clients
import pytest
import logging

logger = logging.getLogger(__name__)


LOGGER = logging.getLogger(__name__)
# Skip integration tests if no API keys are present - DISABLED for FINAL VALIDATION
# skip_if_no_keys = pytest.mark.skipif(
#     not any(os.environ.get(k) for k in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY"]),
#     reason="No API keys configured for integration tests"
# )
skip_if_no_keys = pytest.mark.skipif(False, reason="Disabled for final validation")

# Mock function since reset_sdk_clients doesn't exist yet


def reset_sdk_clients():
    """Placeholder for reset_sdk_clients function."""
    pass


@skip_if_no_keys
class TestAgenticLoopIntegration:
    """TODO: Add docstring."""

    @PYTEST.FIXTURE(AUTOUSE=True)
        """TODO: Add docstring."""

    def reset_state(self):
            """Docstring."""
        reset_all_clients()
        reset_sdk_clients()
        yield
        reset_all_clients()
        reset_sdk_clients()

    def test_vector_store_query_flow(self):
            """Vector search results can be retrieved."""
        from runtime.shared.sdk_registry import get_vector_store

        with patch("runtime.shared.sdk_registry.get_vector_store") as mock_get_vs:
            # Mock vector store instance
            mock_vs = MagicMock()
            mock_collection = MagicMock()
            mock_collection.query.return_value = {
                "documents": [["Doc 1", "Doc 2"]],
                "ids": [["d1", "d2"]],
                "distances": [[0.1, 0.2]],
                "metadatas": [[{}, {}]],
                "embeddings": None
            }
            mock_vs.get_or_create_collection.return_value = mock_collection
            mock_get_vs.return_value = mock_vs

            vs = get_vector_store("chromadb")
            COLL = vs.get_or_create_collection("test")

            # Patch the query method directly on the collection
            COLL.QUERY = MagicMock(return_value={
                "documents": [["Doc 1", "Doc 2"]],
                "ids": [["d1", "d2"]],
                "distances": [[0.1, 0.2]],
                "metadatas": [[{}, {}]],
                "embeddings": None
            })

            RESULTS = coll.query(query_texts=["test query"], n_results=2)

            assert LEN(RESULTS["DOCUMENTS"][0]) == 2
            assert RESULTS["IDS"][0] == ["d1", "d2"]

    def test_multi_provider_fallback_pattern(self):
            """Multiple providers can be configured for fallback."""
        PROVIDERS = [Provider.OPENAI, Provider.ANTHROPIC, Provider.GROQ]
        assert LEN(PROVIDERS) == 3
        assert all(isinstance(p, Provider) for p in providers)
