"""Test that all vector search modules can be imported."""
import pytest


def _can_import_pinecone() -> bool:
    """Check if Pinecone SDK is properly installed."""
    try:
        from pinecone import Pinecone  # noqa: F401
        return True
    except ImportError:
        return False


def test_import_vector_modules():
    """Test that all vector search related modules can be imported."""
    # L1 Planning
    import l2.agents.planning.vector_search_planning  # noqa: F401
    
    # L2 Execution
    import l2.agents.execution.vector_search_executor  # noqa: F401
    
    # If we get here, core imports worked
    assert True


@pytest.mark.skipif(
    not _can_import_pinecone(),
    reason="Pinecone SDK not properly installed or incompatible version"
)
def test_import_pinecone_provider():
    """Test that pinecone provider can be imported when SDK is available."""
    import providers.pinecone_client  # noqa: F401
    assert True






