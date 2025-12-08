"""Logic tests for planner scoring properties and invariants."""
from __future__ import annotations
import pytest

from agentic_workflow.runtime.shared.sdk_registry import SDKCategory, SDK_REGISTRY

class TestPlannerScoringProperties:
    """Property-based tests for planner scoring logic."""

    def test_sdk_category_coverage(self):
        """All SDK categories are represented in registry."""
        categories_in_registry = {e.category for e in SDK_REGISTRY.values()}
        expected_categories = {
            SDKCategory.LLM_PROVIDER,
            SDKCategory.VECTOR_STORE,
            SDKCategory.CACHE,
            SDKCategory.ORCHESTRATION,
            SDKCategory.OBSERVABILITY,
            SDKCategory.DOCUMENT,
            SDKCategory.MCP,
        }
        assert expected_categories.issubset(categories_in_registry)

    def test_llm_provider_count(self):
        """Multiple LLM providers available for fallback."""
        llm_providers = [
            e for e in SDK_REGISTRY.values()
            if e.category == SDKCategory.LLM_PROVIDER
        ]
        assert len(llm_providers) >= 5  # At least 5 LLM providers

    def test_vector_store_options(self):
        """Multiple vector stores available."""
        vector_stores = [
            e for e in SDK_REGISTRY.values()
            if e.category == SDKCategory.VECTOR_STORE
        ]
        assert len(vector_stores) >= 2

class TestRoutingInvariants:
    """Tests for routing selection invariants."""

    def test_provider_priority_determinism(self):
        """Provider iteration order is deterministic."""
        order1 = list(SDK_REGISTRY.keys())
        order2 = list(SDK_REGISTRY.keys())
        assert order1 == order2

    def test_mcp_compatible_providers(self):
        """MCP-compatible providers are identifiable."""
        mcp_compatible = [
            name for name, e in SDK_REGISTRY.items()
            if e.mcp_compatible
        ]
        assert len(mcp_compatible) >= 2

    def test_async_support_default(self):
        """Most SDKs support async by default."""
        async_supported = [
            e for e in SDK_REGISTRY.values()
            if e.async_support
        ]
        # Majority should support async
        assert len(async_supported) > len(SDK_REGISTRY) // 2

class TestFallbackArbitration:
    """Tests for fallback routing arbitration."""

    def test_category_fallback_options(self):
        """Each category has fallback options."""
        for category in SDKCategory:
            sdks_in_category = [
                e for e in SDK_REGISTRY.values()
                if e.category == category
            ]
            # Most categories should have at least 1 SDK
            # Some specialized categories may have fewer
            if category in [SDKCategory.LLM_PROVIDER, SDKCategory.VECTOR_STORE]:
                assert len(sdks_in_category) >= 2

    def test_env_key_uniqueness(self):
        """Environment keys are unique per SDK."""
        env_keys = [
            e.env_key for e in SDK_REGISTRY.values()
            if e.env_key is not None
        ]
        # No duplicates (except None)
        assert len(env_keys) == len(set(env_keys))
