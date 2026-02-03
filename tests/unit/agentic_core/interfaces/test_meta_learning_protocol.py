"""Tests for MetaLearningProtocol."""

import pytest
from agentic_core.interfaces.meta_learning_protocol import (
    MetaLearningProtocol,
    LearningContext,
    LearningResult,
)


class TestLearningContext:
    """Tests for LearningContext dataclass."""

    def test_create_context(self):
        """Test creating a learning context."""
        context = LearningContext(
            context_key="test_key",
            agent_name="TestAgent",
            operation_type="classify",
            input_hash="abc123",
        )
        assert context.context_key == "test_key"
        assert context.agent_name == "TestAgent"
        assert context.operation_type == "classify"
        assert context.input_hash == "abc123"
        assert context.metadata == {}

    def test_create_context_with_metadata(self):
        """Test creating context with metadata."""
        metadata = {"file_type": "python", "size": 1024}
        context = LearningContext(
            context_key="test_key",
            agent_name="TestAgent",
            operation_type="classify",
            input_hash="abc123",
            metadata=metadata,
        )
        assert context.metadata == metadata

    def test_context_to_cache_key(self):
        """Test generating cache key from context."""
        context = LearningContext(
            context_key="test_key",
            agent_name="TestAgent",
            operation_type="classify",
            input_hash="abc123",
        )
        cache_key = context.to_cache_key()
        assert cache_key == "TestAgent:classify:abc123"

    def test_context_none_metadata_defaults_to_empty_dict(self):
        """Test that None metadata becomes empty dict."""
        context = LearningContext(
            context_key="test_key",
            agent_name="TestAgent",
            operation_type="classify",
            input_hash="abc123",
            metadata=None,
        )
        assert context.metadata == {}


class TestLearningResult:
    """Tests for LearningResult dataclass."""

    def test_create_cache_hit_result(self):
        """Test creating a cache hit result."""
        result = LearningResult(
            success=True,
            from_cache=True,
            result={"classification": "validator"},
            confidence=0.95,
            cache_key="TestAgent:classify:abc123",
        )
        assert result.success is True
        assert result.from_cache is True
        assert result.result == {"classification": "validator"}
        assert result.confidence == 0.95
        assert result.cache_key == "TestAgent:classify:abc123"

    def test_create_cache_miss_result(self):
        """Test creating a cache miss result."""
        result = LearningResult(
            success=True,
            from_cache=False,
            result={"classification": "executor"},
            execution_time_ms=150.5,
        )
        assert result.success is True
        assert result.from_cache is False
        assert result.execution_time_ms == 150.5

    def test_create_failure_result(self):
        """Test creating a failure result."""
        result = LearningResult(
            success=False,
            from_cache=False,
            result=None,
            metadata={"error": "execution_failed"},
        )
        assert result.success is False
        assert result.result is None
        assert result.metadata == {"error": "execution_failed"}

    def test_result_default_confidence(self):
        """Test default confidence value."""
        result = LearningResult(
            success=True,
            from_cache=False,
            result="test",
        )
        assert result.confidence == 1.0

    def test_result_none_metadata_defaults_to_empty_dict(self):
        """Test that None metadata becomes empty dict."""
        result = LearningResult(
            success=True,
            from_cache=False,
            result="test",
            metadata=None,
        )
        assert result.metadata == {}


class MockMetaLearningService(MetaLearningProtocol):
    """Mock implementation for testing."""

    def __init__(self, available: bool = True):
        self._available = available
        self._cache: dict[str, tuple[any, float]] = {}
        self._stats = {"hits": 0, "misses": 0, "learns": 0}

    def recall_or_execute(
        self,
        context: LearningContext,
        execution_fn,
    ) -> LearningResult:
        cache_key = context.to_cache_key()

        # Check cache
        if cache_key in self._cache:
            self._stats["hits"] += 1
            cached_result, confidence = self._cache[cache_key]
            return LearningResult(
                success=True,
                from_cache=True,
                result=cached_result,
                confidence=confidence,
                cache_key=cache_key,
            )

        # Execute
        self._stats["misses"] += 1
        try:
            result = execution_fn()
            # Learn from success
            self.learn_experience(context, result, success=True)
            return LearningResult(
                success=True,
                from_cache=False,
                result=result,
                cache_key=cache_key,
            )
        except Exception as e:
            return LearningResult(
                success=False,
                from_cache=False,
                result=None,
                metadata={"error": str(e)},
            )

    def learn_experience(
        self,
        context: LearningContext,
        result: any,
        success: bool,
    ) -> bool:
        if not success:
            return False

        cache_key = context.to_cache_key()
        self._cache[cache_key] = (result, 1.0)
        self._stats["learns"] += 1
        return True

    def invalidate_cache(
        self,
        context_key: str | None = None,
        agent_name: str | None = None,
    ) -> int:
        if context_key is None and agent_name is None:
            count = len(self._cache)
            self._cache.clear()
            return count

        keys_to_remove = []
        for key in self._cache:
            if context_key and context_key in key:
                keys_to_remove.append(key)
            elif agent_name and key.startswith(f"{agent_name}:"):
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self._cache[key]
        return len(keys_to_remove)

    def get_cache_stats(self) -> dict[str, any]:
        return {
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "learns": self._stats["learns"],
            "cache_size": len(self._cache),
            "hit_rate": (
                self._stats["hits"] / (self._stats["hits"] + self._stats["misses"])
                if (self._stats["hits"] + self._stats["misses"]) > 0
                else 0.0
            ),
        }

    def is_available(self) -> bool:
        return self._available


class TestMetaLearningProtocol:
    """Tests for MetaLearningProtocol."""

    def test_mock_recall_or_execute_cache_miss(self):
        """Test recall_or_execute with cache miss."""
        service = MockMetaLearningService()
        context = LearningContext(
            context_key="test",
            agent_name="TestAgent",
            operation_type="classify",
            input_hash="abc123",
        )

        result = service.recall_or_execute(
            context=context,
            execution_fn=lambda: "executed_result",
        )

        assert result.success is True
        assert result.from_cache is False
        assert result.result == "executed_result"

    def test_mock_recall_or_execute_cache_hit(self):
        """Test recall_or_execute with cache hit."""
        service = MockMetaLearningService()
        context = LearningContext(
            context_key="test",
            agent_name="TestAgent",
            operation_type="classify",
            input_hash="abc123",
        )

        # First call - cache miss
        service.recall_or_execute(
            context=context,
            execution_fn=lambda: "first_result",
        )

        # Second call - cache hit
        result = service.recall_or_execute(
            context=context,
            execution_fn=lambda: "second_result",  # Should not be called
        )

        assert result.success is True
        assert result.from_cache is True
        assert result.result == "first_result"  # Cached result

    def test_mock_recall_or_execute_failure(self):
        """Test recall_or_execute handles execution failure."""
        service = MockMetaLearningService()
        context = LearningContext(
            context_key="test",
            agent_name="TestAgent",
            operation_type="classify",
            input_hash="abc123",
        )

        def failing_fn():
            raise ValueError("test error")

        result = service.recall_or_execute(
            context=context,
            execution_fn=failing_fn,
        )

        assert result.success is False
        assert result.from_cache is False
        assert "error" in result.metadata

    def test_mock_learn_experience(self):
        """Test learning from experience."""
        service = MockMetaLearningService()
        context = LearningContext(
            context_key="test",
            agent_name="TestAgent",
            operation_type="classify",
            input_hash="abc123",
        )

        success = service.learn_experience(context, "learned_result", success=True)
        assert success is True

        # Verify it's in cache
        stats = service.get_cache_stats()
        assert stats["cache_size"] == 1

    def test_mock_learn_experience_failure_not_cached(self):
        """Test that failed experiences are not cached."""
        service = MockMetaLearningService()
        context = LearningContext(
            context_key="test",
            agent_name="TestAgent",
            operation_type="classify",
            input_hash="abc123",
        )

        success = service.learn_experience(context, "result", success=False)
        assert success is False

        stats = service.get_cache_stats()
        assert stats["cache_size"] == 0

    def test_mock_invalidate_cache_all(self):
        """Test invalidating all cache entries."""
        service = MockMetaLearningService()

        # Add some entries
        for i in range(3):
            context = LearningContext(
                context_key=f"test_{i}",
                agent_name="TestAgent",
                operation_type="classify",
                input_hash=f"hash{i}",
            )
            service.learn_experience(context, f"result_{i}", success=True)

        assert service.get_cache_stats()["cache_size"] == 3

        count = service.invalidate_cache()
        assert count == 3
        assert service.get_cache_stats()["cache_size"] == 0

    def test_mock_invalidate_cache_by_agent(self):
        """Test invalidating cache by agent name."""
        service = MockMetaLearningService()

        # Add entries for different agents
        for agent in ["Agent1", "Agent2"]:
            context = LearningContext(
                context_key=f"test_{agent}",
                agent_name=agent,
                operation_type="classify",
                input_hash="hash",
            )
            service.learn_experience(context, f"result_{agent}", success=True)

        assert service.get_cache_stats()["cache_size"] == 2

        count = service.invalidate_cache(agent_name="Agent1")
        assert count == 1
        assert service.get_cache_stats()["cache_size"] == 1

    def test_mock_get_cache_stats(self):
        """Test getting cache statistics."""
        service = MockMetaLearningService()
        context = LearningContext(
            context_key="test",
            agent_name="TestAgent",
            operation_type="classify",
            input_hash="abc123",
        )

        # First call - miss
        service.recall_or_execute(context, lambda: "result")
        # Second call - hit
        service.recall_or_execute(context, lambda: "result")

        stats = service.get_cache_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["learns"] == 1
        assert stats["cache_size"] == 1
        assert stats["hit_rate"] == 0.5

    def test_mock_is_available(self):
        """Test is_available method."""
        service = MockMetaLearningService(available=True)
        assert service.is_available() is True

        service = MockMetaLearningService(available=False)
        assert service.is_available() is False
