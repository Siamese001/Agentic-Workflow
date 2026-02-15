"""
Contract Test: SovereignLLMGateway Uses Client Wrappers
Tests that SovereignLLMGateway instantiates wrapper clients via factory functions.
"""

import ast
from unittest.mock import MagicMock

import pytest

from agentic_core.L2_execution.enforcement.SovereignLLMGateway import SovereignLLMGateway


def test_no_direct_sdk_imports_in_sovereign_llm_gateway():
    """AST-based test that SovereignLLMGateway has no direct SDK imports."""
    import agentic_core.L2_execution.enforcement.SovereignLLMGateway as module

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


def test_sovereign_llm_gateway_uses_wrapper_factories(monkeypatch):
    """Test that SovereignLLMGateway uses client wrapper factories."""
    # Create sentinel objects to replace factory functions
    sentinel_openai = MagicMock()
    sentinel_anthropic = MagicMock()
    sentinel_vertex = MagicMock()

    # Patch the factory functions
    monkeypatch.setattr("data.sdks_mcps.client_wrappers.create_openai_client", lambda: sentinel_openai)
    monkeypatch.setattr("data.sdks_mcps.client_wrappers.create_anthropic_client", lambda: sentinel_anthropic)
    monkeypatch.setattr("data.sdks_mcps.client_wrappers.create_vertex_client", lambda: sentinel_vertex)

    # Reset singleton to ensure fresh instantiation
    SovereignLLMGateway.reset_instance()

    # Create gateway instance
    gateway = SovereignLLMGateway()

    # Access properties to trigger client creation
    openai_client = gateway.openai
    anthropic_client = gateway.anthropic
    google_client = gateway.google

    # Verify clients are the sentinel objects (proving factories were called)
    assert openai_client is sentinel_openai, "OpenAI client should be from factory"
    assert anthropic_client is sentinel_anthropic, "Anthropic client should be from factory"
    assert google_client is sentinel_vertex, "Google client should be from factory"

    # Verify factory functions were called (check call count on sentinels)
    # This proves the lazy loading mechanism still works
    assert gateway._openai_client is sentinel_openai
    assert gateway._anthropic_client is sentinel_anthropic
    assert gateway._google_client is sentinel_vertex


def test_sovereign_llm_gateway_preserves_interface():
    """Test that migration preserves existing public interface."""
    SovereignLLMGateway.reset_instance()
    gateway = SovereignLLMGateway()

    # Check that all expected properties exist
    assert hasattr(gateway, "openai"), "Should have openai property"
    assert hasattr(gateway, "anthropic"), "Should have anthropic property"
    assert hasattr(gateway, "google"), "Should have google property"

    # Check that config property works
    assert hasattr(gateway, "config"), "Should have config property"

    # Check that operation stats exist
    assert hasattr(gateway, "operation_stats"), "Should have operation_stats"
    assert "openai" in gateway.operation_stats
    assert "anthropic" in gateway.operation_stats
    assert "google" in gateway.operation_stats

    # Check that audit log exists
    assert hasattr(gateway, "audit_log"), "Should have audit_log"
    assert isinstance(gateway.audit_log, list), "Audit log should be a list"


if __name__ == "__main__":
    test_no_direct_sdk_imports_in_sovereign_llm_gateway()
    test_sovereign_llm_gateway_uses_wrapper_factories(pytest.MonkeyPatch())
    test_sovereign_llm_gateway_preserves_interface()
    print("All SovereignLLMGateway wrapper tests passed!")
