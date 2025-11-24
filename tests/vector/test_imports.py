"""Test that all vector search modules can be imported."""

def test_import_vector_modules():
    """Test that all vector search related modules can be imported."""
    # L1 Planning
    import l1.vector_search_planning  # noqa: F401
    
    # L2 Execution
    import l2.vector_search_executor  # noqa: F401
    
    # Providers
    import providers.pinecone_client  # noqa: F401
    
    # If we get here, all imports worked
    assert True






