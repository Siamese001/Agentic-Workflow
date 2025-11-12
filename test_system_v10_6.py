"""Focused regression tests for the v10.6 core components.

The original suite attempted to exercise the entire orchestration graph
which made the tests brittle and slow.  These replacements target the parts
of the system that provide configuration, resiliency and caching guarantees,
covering the behaviours that downstream components rely on.
"""

import asyncio
from typing import Any, Dict, List

import pytest

from core_v10_6 import (
    CacheManager,
    CircuitBreaker,
    CircuitBreakerOpenError,
    ConfigV10_6,
    ModelAPIError,
    exponential_backoff_retry,
)


# ---------------------------------------------------------------------------
# Helper doubles used across multiple tests
# ---------------------------------------------------------------------------


class InMemoryRedis:
    """Minimal Redis substitute supporting the subset used by CacheManager."""

    def __init__(self) -> None:
        self.store: Dict[str, str] = {}

    def setex(self, name: str, ttl: int, value: str) -> None:
        self.store[name] = value

    def get(self, name: str) -> str | None:
        return self.store.get(name)


class FakeCollection:
    def __init__(self) -> None:
        self.records: Dict[str, Dict[str, Any]] = {}

    def add(
        self,
        *,
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str],
    ) -> None:
        for doc, metadata, record_id in zip(documents, metadatas, ids):
            self.records[record_id] = {"document": doc, "metadata": metadata}

    def query(
        self,
        *,
        query_embeddings: List[List[float]],
        n_results: int,
        where: Dict[str, Any],
    ) -> Dict[str, Any]:
        for record in self.records.values():
            metadata = record["metadata"]
            if all(metadata.get(key) == value for key, value in where.items()):
                # Return a high similarity (low distance) result
                return {
                    "distances": [[0.02]],
                    "documents": [[record["document"]]],
                }
        return {"distances": [[]], "documents": [[]]}


class FakeChromaClient:
    def __init__(self, collection: FakeCollection) -> None:
        self.collection = collection

    def get_or_create_collection(self, name: str, embedding_function: Any) -> FakeCollection:
        return self.collection


class DummyEmbeddingFunction:
    """Callable that mimics the chromadb embedding interface."""

    def __call__(self, prompts: List[str]) -> List[List[float]]:
        return [[float(len(prompt))] for prompt in prompts]


@pytest.fixture()
def config() -> ConfigV10_6:
    return ConfigV10_6("master_config_v10_6.json")


@pytest.fixture()
def cache_manager(config: ConfigV10_6) -> CacheManager:
    collection = FakeCollection()
    chroma = FakeChromaClient(collection)
    redis_client = InMemoryRedis()
    embedding_fn = DummyEmbeddingFunction()
    return CacheManager(config, redis_client, chroma, embedding_fn)


# ---------------------------------------------------------------------------
# Config loader
# ---------------------------------------------------------------------------


def test_config_provides_nested_sections(config: ConfigV10_6) -> None:
    assert config.logging_config.log_level == "INFO"
    assert config.agent_stacks.enable_constitutional_review is True
    assert config.agent_stacks.conductor_max_steps == 10


def test_config_missing_section_raises_attribute_error(config: ConfigV10_6) -> None:
    with pytest.raises(AttributeError):
        _ = config.this_section_does_not_exist


# ---------------------------------------------------------------------------
# Circuit breaker behaviour
# ---------------------------------------------------------------------------


def test_circuit_breaker_trips_after_failures() -> None:
    breaker = CircuitBreaker(failure_threshold=2)

    breaker.record_failure()
    assert breaker.is_open is False

    breaker.record_failure()
    assert breaker.is_open is True

    with pytest.raises(CircuitBreakerOpenError):
        breaker.check()


def test_circuit_breaker_resets_on_success() -> None:
    breaker = CircuitBreaker(failure_threshold=1)
    breaker.record_failure()
    assert breaker.is_open is True

    breaker.record_success()
    assert breaker.is_open is False
    breaker.check()  # Should not raise after reset


# ---------------------------------------------------------------------------
# Exponential backoff decorator
# ---------------------------------------------------------------------------


def test_exponential_backoff_retry_eventually_succeeds() -> None:
    attempts: Dict[str, int] = {"count": 0}

    @exponential_backoff_retry(max_retries=3, initial_delay=0)
    async def flaky_call() -> str:
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise ModelAPIError("temporary issue")
        return "success"

    result = asyncio.run(flaky_call())
    assert result == "success"
    assert attempts["count"] == 3


def test_exponential_backoff_retry_propagates_after_max_attempts() -> None:
    @exponential_backoff_retry(max_retries=2, initial_delay=0)
    async def always_fail() -> None:
        raise ModelAPIError("still broken")

    with pytest.raises(ModelAPIError):
        asyncio.run(always_fail())


# ---------------------------------------------------------------------------
# CacheManager integration
# ---------------------------------------------------------------------------


def test_cache_manager_reads_exact_cache(cache_manager: CacheManager) -> None:
    asyncio.run(
        cache_manager.set_llm_cache(
            provider="openai",
            model="gpt-test",
            prompt="hello",
            temperature=0.1,
            response={"content": "cached"},
        )
    )

    cached = asyncio.run(cache_manager.get_llm_cache("openai", "gpt-test", "hello", 0.1))
    assert cached == {"content": "cached"}


def test_cache_manager_falls_back_to_semantic_cache(cache_manager: CacheManager) -> None:
    asyncio.run(
        cache_manager.set_llm_cache(
            provider="anthropic",
            model="claude",
            prompt="goodbye",
            temperature=0.2,
            response={"content": "semantic"},
        )
    )

    # Evict the exact cache entry to force a semantic lookup.
    cache_manager.redis.store.clear()

    cached = asyncio.run(cache_manager.get_llm_cache("anthropic", "claude", "goodbye", 0.2))
    assert cached == {"content": "semantic"}


def test_tool_cache_handles_unserialisable_input(cache_manager: CacheManager) -> None:
    result = cache_manager.get_tool_cache("ExampleTool", {"payload": object()})
    assert result is None


def test_tool_cache_round_trip(cache_manager: CacheManager) -> None:
    cache_manager.set_tool_cache("ExampleTool", {"value": 1}, {"result": 2})
    result = cache_manager.get_tool_cache("ExampleTool", {"value": 1})
    assert result == {"result": 2}
