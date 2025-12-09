"""Performance tests for SDK latency budgets."""
from __future__ import annotations
import time
from unittest.mock import MagicMock, patch
import pytest

from agentic_workflow.runtime.shared.sdk_registry import (
    validate_sdk, SDK_REGISTRY, reset_all_clients, get_vector_store,
)
from agentic_workflow.runtime.shared.cache import generate_llm_cache_key

class TestSDKValidationLatency:
    def test_validate_sdk_under_100ms(self):
        """SDK validation completes within 100ms."""
        start = time.perf_counter()
        for _ in range(10):
            validate_sdk("openai")
        elapsed = time.perf_counter() - start
        avg_ms = (elapsed / 10) * 1000
        assert avg_ms < 100, f"Avg validation took {avg_ms:.2f}ms"

    def test_registry_lookup_under_1ms(self):
        """Registry lookup is sub-millisecond."""
        start = time.perf_counter()
        for _ in range(1000):
            _ = SDK_REGISTRY.get("openai")
        elapsed = time.perf_counter() - start
        avg_us = (elapsed / 1000) * 1_000_000
        assert avg_us < 1000, f"Avg lookup took {avg_us:.2f}us"

class TestCacheKeyLatency:
    def test_cache_key_generation_under_1ms(self):
        """Cache key generation is sub-millisecond."""
        messages = [{"role": "user", "content": "Test message"}]
        start = time.perf_counter()
        for _ in range(1000):
            generate_llm_cache_key(model="gpt-4o", messages=messages)
        elapsed = time.perf_counter() - start
        avg_us = (elapsed / 1000) * 1_000_000
        assert avg_us < 1000, f"Avg key gen took {avg_us:.2f}us"

class TestVectorStoreInitLatency:
    def test_vector_store_init_under_500ms(self):
        """Vector store initialization within 500ms."""
        reset_all_clients()
        with patch("agentic_workflow.runtime.shared.sdk_registry.chromadb") as mock:
            mock.Client.return_value = MagicMock()
            start = time.perf_counter()
            get_vector_store("chromadb")
            elapsed = (time.perf_counter() - start) * 1000
            assert elapsed < 500, f"Init took {elapsed:.2f}ms"
