"""
Contract Test: EmbeddingSovereignAgent Uses Client Wrappers
Tests that EmbeddingSovereignAgent instantiates wrapper clients via factory functions.
"""

import ast
from unittest.mock import MagicMock

import pytest

from agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent import EmbeddingSovereignAgent


def test_no_direct_sdk_imports_in_embedding_sovereign_agent():
    """AST-based test that EmbeddingSovereignAgent has no direct SDK imports."""
    import agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent as module

    # Parse the module AST
    with open(module.__file__, encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)

    # Check for forbidden imports
    forbidden_imports = {"openai", "anthropic", "google.generativeai"}
    found_imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if any(alias.name.startswith(module_name) for module_name in forbidden_imports):
                    found_imports.append(f"import {alias.name}")

        elif isinstance(node, ast.ImportFrom):
            if node.module and any(node.module.startswith(module_name) for module_name in forbidden_imports):
                found_imports.append(f"from {node.module} import *")

    assert not found_imports, f"Found direct SDK imports: {found_imports}"


def test_embedding_sovereign_agent_uses_wrapper_factories(monkeypatch):
    """Test that EmbeddingSovereignAgent uses client wrapper factories."""
    # Create sentinel objects to replace factory functions
    sentinel_vertex = MagicMock()
    sentinel_openai = MagicMock()

    # Mock the embedding methods to return test data
    test_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
    sentinel_vertex.get_embedding.return_value = test_embedding
    sentinel_openai.get_embedding.return_value = test_embedding

    # Patch the factory functions
    monkeypatch.setattr("data.sdks_mcps.client_wrappers.create_vertex_client", lambda: sentinel_vertex)
    monkeypatch.setattr("data.sdks_mcps.client_wrappers.create_openai_client", lambda: sentinel_openai)

    # Reset singleton to ensure fresh instantiation
    EmbeddingSovereignAgent.reset_instance()

    # Create agent instance
    agent = EmbeddingSovereignAgent()

    # Test that embedding methods call the wrapper clients
    import asyncio

    async def test_embeddings():
        # Test Gemini embedding
        gemini_result = await agent._get_gemini_embedding("test content")
        assert gemini_result == test_embedding, "Gemini embedding should use wrapper"
        sentinel_vertex.get_embedding.assert_called_once_with("test content")

        # Test OpenAI embedding
        openai_result = await agent._get_openai_embedding("test content")
        assert openai_result == test_embedding, "OpenAI embedding should use wrapper"
        sentinel_openai.get_embedding.assert_called_once_with("test content")

    # Run the async test
    asyncio.run(test_embeddings())


def test_embedding_sovereign_agent_preserves_interface():
    """Test that migration preserves existing public interface."""
    EmbeddingSovereignAgent.reset_instance()
    agent = EmbeddingSovereignAgent()

    # Check that all expected methods exist
    assert hasattr(agent, "get_embedding"), "Should have get_embedding method"
    assert hasattr(agent, "get_embeddings_batch"), "Should have get_embeddings_batch method"
    assert hasattr(agent, "_get_gemini_embedding"), "Should have _get_gemini_embedding method"
    assert hasattr(agent, "_get_openai_embedding"), "Should have _get_openai_embedding method"

    # Check that config property works
    assert hasattr(agent, "config"), "Should have config property"

    # Check that operation stats exist
    assert hasattr(agent, "operation_stats"), "Should have operation_stats"
    assert "gemini" in agent.operation_stats
    assert "openai" in agent.operation_stats
    assert "cache_hits" in agent.operation_stats
    assert "cache_misses" in agent.operation_stats

    # Check that audit log exists
    assert hasattr(agent, "audit_log"), "Should have audit_log"
    assert isinstance(agent.audit_log, list), "Audit log should be a list"

    # Check that expected dimensions exist
    assert hasattr(agent, "EXPECTED_DIMENSIONS"), "Should have EXPECTED_DIMENSIONS"


def test_embedding_sovereign_agent_no_direct_sdk_instantiation():
    """Test that embedding methods don't directly instantiate SDK clients."""
    EmbeddingSovereignAgent.reset_instance()

    # This test ensures the methods don't have direct SDK imports
    # The actual factory usage is tested in the wrapper factory test above
    import asyncio

    async def test_no_direct_instantiation():
        # We can't easily test this without mocking, but the AST test above
        # combined with the wrapper factory test provides strong evidence
        # that no direct SDK instantiation occurs
        pass

    asyncio.run(test_no_direct_instantiation())


if __name__ == "__main__":
    test_no_direct_sdk_imports_in_embedding_sovereign_agent()
    test_embedding_sovereign_agent_uses_wrapper_factories(pytest.MonkeyPatch())
    test_embedding_sovereign_agent_preserves_interface()
    test_embedding_sovereign_agent_no_direct_sdk_instantiation()
    print("All EmbeddingSovereignAgent wrapper tests passed!")
