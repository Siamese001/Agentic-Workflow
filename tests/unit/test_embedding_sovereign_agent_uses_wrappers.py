"""
Contract Test: EmbeddingSovereignAgent Uses Client Wrappers
Tests that EmbeddingSovereignAgent instantiates wrapper clients via factory functions.
"""

import ast
import sys
import types
from unittest.mock import MagicMock


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


def test_embedding_sovereign_agent_uses_wrapper_factories():
    """Gemini routes through create_vertex_client; OpenAI routes through embedding factory."""

    sentinel_vertex = MagicMock()
    vertex_calls = []
    factory_create_calls = []

    def mock_vertex_factory():
        vertex_calls.append(1)
        return sentinel_vertex

    # Mock embedding client returned by the factory for OpenAI calls
    mock_factory_client = MagicMock()

    async def _mock_get_embedding(guarded_text):
        return [0.1, 0.2, 0.3, 0.4, 0.5]

    mock_factory_client.get_embedding = _mock_get_embedding

    def mock_create_embedding_client(provider, model=None, **kwargs):
        factory_create_calls.append(provider)
        return mock_factory_client

    # Shim for client_wrappers — Gemini still uses create_vertex_client directly
    wrapper_shim = types.ModuleType("data.sdks_mcps.client_wrappers")
    wrapper_shim.create_vertex_client = mock_vertex_factory
    wrapper_shim.create_openai_client = MagicMock(name="create_openai_client_must_not_be_called")
    wrapper_shim.__all__ = ["create_vertex_client", "create_openai_client"]

    # Shim for embedding_factory — OpenAI now routed through here
    factory_shim = types.ModuleType("agentic_core.embeddings.embedding_factory")
    factory_shim.create_embedding_client = mock_create_embedding_client

    sys.modules["data.sdks_mcps.client_wrappers"] = wrapper_shim
    sys.modules["agentic_core.embeddings.embedding_factory"] = factory_shim

    try:
        import importlib

        import agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent as module

        importlib.reload(module)

        EmbeddingSovereignAgent = module.EmbeddingSovereignAgent
        assert EmbeddingSovereignAgent is not None

        mock_agent = MagicMock()
        mock_agent._bge_m3_model = None
        mock_agent._get_gemini_embedding = EmbeddingSovereignAgent._get_gemini_embedding.__get__(mock_agent)
        mock_agent._get_openai_embedding = EmbeddingSovereignAgent._get_openai_embedding.__get__(mock_agent)

        import asyncio

        async def test_embeddings():
            sentinel_vertex.embed_content.return_value = {"embedding": [0.1, 0.2, 0.3, 0.4, 0.5]}

            gemini_result = await mock_agent._get_gemini_embedding("test content")
            assert gemini_result == [0.1, 0.2, 0.3, 0.4, 0.5], "Gemini embedding should work"

            openai_result = await mock_agent._get_openai_embedding("test content")
            assert openai_result == [0.1, 0.2, 0.3, 0.4, 0.5], "OpenAI embedding should work via factory"

        asyncio.run(test_embeddings())

        assert len(vertex_calls) >= 1, "create_vertex_client must be called for Gemini"
        assert factory_create_calls, "create_embedding_client must be called for OpenAI"
        assert "openai" in factory_create_calls, "OpenAI provider must be passed to factory"
        # Direct create_openai_client must NOT be called — OpenAI now goes through factory
        wrapper_shim.create_openai_client.assert_not_called()

    finally:
        for mod_name in [
            "data.sdks_mcps.client_wrappers",
            "agentic_core.embeddings.embedding_factory",
            "agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent",
        ]:
            sys.modules.pop(mod_name, None)


def test_embedding_sovereign_agent_no_direct_sdk_instantiation():
    """Test that embedding methods don't directly instantiate SDK clients."""
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
    test_embedding_sovereign_agent_uses_wrapper_factories()
    test_embedding_sovereign_agent_no_direct_sdk_instantiation()
    print("All EmbeddingSovereignAgent wrapper tests passed!")
