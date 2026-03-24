"""Comprehensive Test Suite for System Learning Infrastructure Integrations

Rigorous testing for all infrastructure integration components:
- Enhanced RAG Retrieval Cache with embedding infrastructure
- System Learning Cache Admission Gate with validation
- System Learning Telemetry Integration with lifecycle tracing
- System Learning Policy Integration with compliance checking
- System Learning State Management with enterprise patterns

Test coverage includes unit tests, integration tests, performance tests,
and failure scenario testing to ensure robustness and reliability.
"""

import asyncio
import logging
import time
from typing import Any

import pytest

# Import system learning infrastructure components
from system_learning.engines.enhanced_rag_retrieval_cache import (
    EnhancedRagRetrievalCache,
)
from system_learning.engines.system_learning_admission_gate import (
    SystemLearningAdmissionContext,
    SystemLearningCacheAdmissionGate,
)
from system_learning.policy.system_learning_policy import (
    PolicyComplianceStatus,
    PolicyContext,
    PolicyValidationType,
    SystemLearningPolicyValidator,
)
from system_learning.state.system_learning_state_manager import (
    StateLineageType,
    SystemLearningStateManager,
    SystemLearningStateSnapshot,
    SystemLearningStateType,
)
from system_learning.telemetry.system_learning_telemetry import (
    SystemLearningEventType,
    SystemLearningOperationType,
    SystemLearningTelemetryEmitter,
)

# Mock external dependencies
try:
    from agentic_core.embeddings.embedding_input_guard import GuardedText
    from agentic_core.runtime.types.cache_entry_types import CacheMiss, SemanticCacheHit

    DEPENDENCIES_AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    DEPENDENCIES_AVAILABLE = False
    logging.warning("Dependencies not available - using mocks")

    # Define mock types for testing
    class GuardedText:
        def __init__(self, redacted_text: str):
            self.redacted_text = redacted_text

    class SemanticCacheHit:
        def __init__(self, response, similarity, metadata):
            self.response = response
            self.similarity = similarity
            self.metadata = metadata

    class CacheMiss:
        def __init__(self, prompt, reason):
            self.prompt = prompt
            self.reason = reason


logger = logging.getLogger(__name__)


class MockEmbeddingClient:
    """Mock embedding client for testing."""

    def __init__(self, dimension: int = 1536):
        self.dimension = dimension
        self.call_count = 0

    async def get_embedding(self, guarded_text: GuardedText) -> list[float]:
        """Mock embedding generation."""
        self.call_count += 1
        # Generate deterministic mock embeddings
        text_hash = hash(guarded_text.redacted_text) % 1000
        return [0.1 * (i + text_hash) % 1.0 for i in range(self.dimension)]

    async def get_embeddings_batch(self, guarded_texts: list[GuardedText]) -> list[list[float]]:
        """Mock batch embedding generation."""
        results = []
        for text in guarded_texts:
            result = await self.get_embedding(text)
            results.append(result)
        return results


class MockRedisCache:
    """Mock Redis cache for testing."""

    def __init__(self):
        self._storage: dict[str, Any] = {}
        self._ttl: dict[str, float] = {}
        self.call_stats = {"get": 0, "set": 0, "delete": 0}

    def get_json(self, key: str, replay_mode: bool = False) -> Any | None:
        """Mock JSON get."""
        self.call_stats["get"] += 1
        if replay_mode:
            return None
        return self._storage.get(key)

    def set_json(self, key: str, value: Any, ttl_seconds: int = 3600) -> None:
        """Mock JSON set."""
        self.call_stats["set"] += 1
        self._storage[key] = value
        if ttl_seconds > 0:
            self._ttl[key] = time.time() + ttl_seconds

    def delete(self, key: str) -> None:
        """Mock delete."""
        self.call_stats["delete"] += 1
        self._storage.pop(key, None)
        self._ttl.pop(key, None)


class MockSemanticCache:
    """Mock semantic cache for testing."""

    def __init__(self):
        self._storage: dict[str, Any] = {}
        self.call_count = 0

    def get(self, query_text: str) -> SemanticCacheHit | CacheMiss:
        """Mock semantic cache get."""
        self.call_count += 1
        if query_text in self._storage:
            return SemanticCacheHit(
                response=self._storage[query_text], similarity=0.9, metadata={"cached": True}
            )
        return CacheMiss(prompt=query_text, reason="not_found")

    def set(self, query_text: str, response: Any) -> None:
        """Mock semantic cache set."""
        self._storage[query_text] = response


# Fixtures
@pytest.fixture
def mock_embedding_client():
    """Fixture providing mock embedding client."""
    return MockEmbeddingClient()


@pytest.fixture
def mock_redis_cache():
    """Fixture providing mock Redis cache."""
    return MockRedisCache()


@pytest.fixture
def mock_semantic_cache():
    """Fixture providing mock semantic cache."""
    return MockSemanticCache()


@pytest.fixture
def sample_retrieval_results():
    """Fixture providing sample retrieval results."""
    return [
        {
            "chunk_id": "chunk_1",
            "score": 0.95,
            "text": "Sample text 1",
            "source": "test_source_1",
        },
        {
            "chunk_id": "chunk_2",
            "score": 0.87,
            "text": "Sample text 2",
            "source": "test_source_2",
        },
        {
            "chunk_id": "chunk_3",
            "score": 0.76,
            "text": "Sample text 3",
            "source": "test_source_3",
        },
    ]


@pytest.fixture
def sample_policy_context():
    """Fixture providing sample policy context."""
    return PolicyContext(
        policy_hash="test_policy_hash",
        policy_version="1.0",
        policy_type=PolicyValidationType.CACHE_POLICY,
        max_cache_size=1000000,
        min_similarity_threshold=0.7,
        max_drift_tolerance=0.2,
    )


# Enhanced RAG Retrieval Cache Tests
class TestEnhancedRagRetrievalCache:
    """Test suite for EnhancedRagRetrievalCache."""

    @pytest.mark.asyncio
    async def test_cache_initialization(self, mock_embedding_client, mock_redis_cache):
        """Test cache initialization with dependencies."""
        cache = EnhancedRagRetrievalCache(
            embedding_client=mock_embedding_client,
            cache=mock_redis_cache,
            enable_semantic_matching=True,
            enable_policy_aware_caching=True,
        )

        assert cache._embedding_client == mock_embedding_client
        assert cache._cache == mock_redis_cache
        assert cache._enable_semantic_matching is True
        assert cache._enable_policy_aware_caching is True
        assert cache._enable_semantic_matching is True

    @pytest.mark.asyncio
    async def test_cache_miss_and_set(
        self, mock_embedding_client, mock_redis_cache, sample_retrieval_results
    ):
        """Test cache miss followed by set operation."""
        cache = EnhancedRagRetrievalCache(
            embedding_client=mock_embedding_client,
            cache=mock_redis_cache,
        )

        # Test cache miss
        result = await cache.get(
            u0_hash="test_u0_hash",
            embedder_version="v1.0",
            seed_pack_manifest_hash="test_manifest",
            k=3,
            cutoff=0.7,
            query_text="test query",
        )

        assert result is None
        assert cache._metrics["cache_misses"] == 1
        assert cache._metrics["cache_hits"] == 0

        # Test cache set
        success = await cache.set(
            u0_hash="test_u0_hash",
            embedder_version="v1.0",
            seed_pack_manifest_hash="test_manifest",
            k=3,
            cutoff=0.7,
            results=sample_retrieval_results,
            query_text="test query",
        )

        assert success is True
        assert mock_redis_cache.call_stats["set"] == 1

    @pytest.mark.asyncio
    async def test_cache_hit(self, mock_embedding_client, mock_redis_cache, sample_retrieval_results):
        """Test cache hit scenario."""
        cache = EnhancedRagRetrievalCache(
            embedding_client=mock_embedding_client,
            cache=mock_redis_cache,
        )

        # Pre-populate cache
        await cache.set(
            u0_hash="test_u0_hash",
            embedder_version="v1.0",
            seed_pack_manifest_hash="test_manifest",
            k=3,
            cutoff=0.7,
            results=sample_retrieval_results,
        )

        # Test cache hit
        result = await cache.get(
            u0_hash="test_u0_hash",
            embedder_version="v1.0",
            seed_pack_manifest_hash="test_manifest",
            k=3,
            cutoff=0.7,
        )

        assert result is not None
        assert len(result) == 3
        assert result[0]["chunk_id"] == "chunk_1"
        assert cache._metrics["cache_hits"] == 1
        assert cache._metrics["cache_misses"] == 0

    @pytest.mark.asyncio
    async def test_semantic_matching(
        self, mock_embedding_client, mock_redis_cache, mock_semantic_cache, sample_retrieval_results
    ):
        """Test semantic similarity matching."""
        cache = EnhancedRagRetrievalCache(
            embedding_client=mock_embedding_client,
            cache=mock_redis_cache,
            semantic_similarity_threshold=0.8,
        )

        # Mock semantic cache
        cache._semantic_cache = mock_semantic_cache

        # Pre-populate semantic cache
        mock_semantic_cache.set("similar_query", sample_retrieval_results)

        # Test semantic match
        result = await cache.get(
            u0_hash="different_u0_hash",
            embedder_version="v1.0",
            seed_pack_manifest_hash="test_manifest",
            k=3,
            cutoff=0.7,
            query_text="similar_query",
        )

        assert result is not None
        assert cache._metrics["semantic_hits"] == 1
        assert mock_embedding_client.call_count >= 1  # Should call embedding for similarity

    @pytest.mark.asyncio
    async def test_policy_aware_caching(
        self, mock_embedding_client, mock_redis_cache, sample_retrieval_results
    ):
        """Test policy-aware cache key generation."""
        cache = EnhancedRagRetrievalCache(
            embedding_client=mock_embedding_client,
            cache=mock_redis_cache,
            enable_policy_aware_caching=True,
        )

        # Set with policy hash
        await cache.set(
            u0_hash="test_u0_hash",
            embedder_version="v1.0",
            seed_pack_manifest_hash="test_manifest",
            k=3,
            cutoff=0.7,
            results=sample_retrieval_results,
            policy_hash="test_policy_hash",
        )

        # Try to get without policy hash (should miss)
        result = await cache.get(
            u0_hash="test_u0_hash",
            embedder_version="v1.0",
            seed_pack_manifest_hash="test_manifest",
            k=3,
            cutoff=0.7,
        )

        assert result is None

        # Try to get with policy hash (should hit)
        result = await cache.get(
            u0_hash="test_u0_hash",
            embedder_version="v1.0",
            seed_pack_manifest_hash="test_manifest",
            k=3,
            cutoff=0.7,
            policy_hash="test_policy_hash",
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_replay_mode(self, mock_embedding_client, mock_redis_cache, sample_retrieval_results):
        """Test replay mode bypass."""
        cache = EnhancedRagRetrievalCache(
            embedding_client=mock_embedding_client,
            cache=mock_redis_cache,
        )

        # Pre-populate cache
        await cache.set(
            u0_hash="test_u0_hash",
            embedder_version="v1.0",
            seed_pack_manifest_hash="test_manifest",
            k=3,
            cutoff=0.7,
            results=sample_retrieval_results,
        )

        # Test replay mode (should bypass cache)
        result = await cache.get(
            u0_hash="test_u0_hash",
            embedder_version="v1.0",
            seed_pack_manifest_hash="test_manifest",
            k=3,
            cutoff=0.7,
            replay_mode=True,
        )

        assert result is None  # Should bypass cache

    def test_metrics_tracking(self, mock_embedding_client, mock_redis_cache):
        """Test metrics tracking functionality."""
        cache = EnhancedRagRetrievalCache(
            embedding_client=mock_embedding_client,
            cache=mock_redis_cache,
        )

        # Check initial metrics
        metrics = cache.get_metrics()
        assert metrics["cache_hits"] == 0
        assert metrics["cache_misses"] == 0
        assert metrics["semantic_hits"] == 0
        assert metrics["total_requests"] == 0

        # Reset metrics
        cache.reset_metrics()
        metrics = cache.get_metrics()
        assert metrics["cache_hits"] == 0
        assert metrics["cache_misses"] == 0


# System Learning Cache Admission Gate Tests
class TestSystemLearningCacheAdmissionGate:
    """Test suite for SystemLearningCacheAdmissionGate."""

    @pytest.mark.asyncio
    async def test_admission_gate_initialization(self):
        """Test admission gate initialization."""
        gate = SystemLearningCacheAdmissionGate(
            support_threshold=0.3,
            completeness_threshold=0.6,
            learning_quality_threshold=0.7,
            drift_tolerance=0.2,
        )

        assert gate.support_threshold == 0.3
        assert gate.completeness_threshold == 0.6
        assert gate.learning_quality_threshold == 0.7
        assert gate.drift_tolerance == 0.2

    @pytest.mark.asyncio
    async def test_successful_admission(self, sample_retrieval_results):
        """Test successful cache admission."""
        gate = SystemLearningCacheAdmissionGate()

        context = SystemLearningAdmissionContext(
            u0_hash="test_u0_hash",
            policy_hash="test_policy_hash",
            embedder_version="v1.0",
            confidence_threshold=0.6,
        )

        decision = await gate.evaluate_admission(
            context=context,
            retrieval_results=sample_retrieval_results,
            query_text="test query",
        )

        assert decision.admitted is True
        assert decision.learning_score >= 0.6
        assert decision.quality_confidence >= 0.6

    @pytest.mark.asyncio
    async def test_learning_quality_failure(self, sample_retrieval_results):
        """Test admission failure due to learning quality."""
        gate = SystemLearningCacheAdmissionGate(
            learning_quality_threshold=0.9,  # High threshold
        )

        context = SystemLearningAdmissionContext(
            u0_hash="test_u0_hash",
            policy_hash="test_policy_hash",
            embedder_version="v1.0",
            confidence_threshold=0.9,
        )

        decision = await gate.evaluate_admission(
            context=context,
            retrieval_results=sample_retrieval_results,
            query_text="test query",
        )

        assert decision.admitted is False
        assert "learning_quality" in decision.explanation.lower()

    @pytest.mark.asyncio
    async def test_drift_detection_failure(self, sample_retrieval_results):
        """Test admission failure due to drift detection."""
        gate = SystemLearningCacheAdmissionGate(
            drift_tolerance=0.1,  # Low tolerance
        )

        context = SystemLearningAdmissionContext(
            u0_hash="test_u0_hash",
            policy_hash="test_policy_hash",
            embedder_version="v1.0",
            drift_detection_enabled=True,
            drift_tolerance=0.05,  # Very low tolerance
        )

        # Create results with high scores (potential drift)
        high_score_results = [{**result, "score": 0.98} for result in sample_retrieval_results]

        decision = await gate.evaluate_admission(
            context=context,
            retrieval_results=high_score_results,
        )

        assert decision.admitted is False
        assert "drift" in decision.explanation.lower()

    @pytest.mark.asyncio
    async def test_policy_validation_integration(self, sample_retrieval_results):
        """Test policy validation integration."""
        gate = SystemLearningCacheAdmissionGate(
            enable_policy_aware_caching=True,
        )

        context = SystemLearningAdmissionContext(
            u0_hash="test_u0_hash",
            policy_hash="test_policy_hash",
            embedder_version="v1.0",
        )

        decision = await gate.evaluate_admission(
            context=context,
            retrieval_results=sample_retrieval_results,
            query_text="test query",
        )

        assert decision.learning_context == context
        assert decision.policy_hash == context.policy_hash

    def test_metrics_tracking(self):
        """Test metrics tracking functionality."""
        gate = SystemLearningCacheAdmissionGate()

        # Check initial metrics
        metrics = gate.get_metrics()
        assert metrics["total_evaluations"] == 0
        assert metrics["admissions"] == 0
        assert metrics["denials"] == 0
        assert metrics["admission_rate"] == 0.0

        # Reset metrics
        gate.reset_metrics()
        metrics = gate.get_metrics()
        assert metrics["total_evaluations"] == 0


# System Learning Telemetry Integration Tests
class TestSystemLearningTelemetryIntegration:
    """Test suite for SystemLearningTelemetryEmitter."""

    def test_telemetry_emitter_initialization(self):
        """Test telemetry emitter initialization."""
        emitter = SystemLearningTelemetryEmitter("test_component")

        assert emitter.component_name == "test_component"
        assert emitter.session_id is not None
        assert len(emitter.session_id) > 0
        assert isinstance(emitter._metrics, dict)

    def test_operation_tracking(self):
        """Test operation tracking functionality."""
        emitter = SystemLearningTelemetryEmitter("test_component")

        # Start operation
        context = emitter.start_operation(
            SystemLearningOperationType.CACHE_GET,
            memory_usage_mb=100.0,
            cache_size=1000,
        )

        assert context.operation_type == SystemLearningOperationType.CACHE_GET
        assert context.start_time is not None
        assert context.memory_usage_mb == 100.0
        assert context.cache_size == 1000
        assert context.trace_id is not None

        # End operation successfully
        emitter.end_operation(
            context,
            success=True,
            result={"key": "test_key", "value": "test_value"},
            cache_hit=True,
        )

        assert context.end_time is not None
        assert context.duration_ms is not None
        assert context.duration_ms > 0

    def test_operation_tracking_with_error(self):
        """Test operation tracking with error."""
        emitter = SystemLearningTelemetryEmitter("test_component")

        # Start operation
        context = emitter.start_operation(
            SystemLearningOperationType.EMBEDDING_GENERATE,
        )

        # End operation with error
        test_error = ValueError("Test error")
        emitter.end_operation(
            context,
            success=False,
            error=test_error,
        )

        assert context.error_type == "ValueError"
        assert context.error_message == "Test error"
        assert context.error_type in emitter._error_counts

    def test_metric_emission(self):
        """Test metric emission functionality."""
        emitter = SystemLearningTelemetryEmitter("test_component")

        # Emit counter metric
        emitter.emit_metric(
            "cache_operations",
            42,
            unit="operations",
            tags={"operation": "get"},
            is_counter=True,
        )

        # Emit gauge metric
        emitter.emit_metric(
            "cache_size",
            1024,
            unit="bytes",
            tags={"component": "test_component"},
            is_gauge=True,
        )

        # Check metrics
        metrics = emitter.get_metrics_summary()
        assert "cache_operations" in metrics["metrics"]
        assert "cache_size" in metrics["metrics"]
        assert metrics["metrics"]["cache_operations"]["value"] == 42
        assert metrics["metrics"]["cache_operations"]["unit"] == "operations"

    def test_learning_event_emission(self):
        """Test learning event emission."""
        emitter = SystemLearningTelemetryEmitter("test_component")

        # Emit learning event
        emitter.emit_learning_event(
            SystemLearningEventType.LEARNING_SESSION_START,
            data={
                "model_version": "1.0",
                "batch_size": 32,
                "learning_rate": 0.001,
            },
            session_type="training",
        )

        # Check metrics (should be updated)
        metrics = emitter.get_metrics_summary()
        assert metrics["component"] == "test_component"
        assert metrics["session_id"] == emitter.session_id

    def test_embedding_event_emission(self):
        """Test embedding event emission."""
        emitter = SystemLearningTelemetryEmitter("test_component")

        # Emit embedding event
        emitter.emit_embedding_event(
            operation="generate",
            text_length=100,
            embedding_dimension=1536,
            model_version="text-embedding-3-large",
        )

        # Check metrics
        metrics = emitter.get_metrics_summary()
        assert "embedding_generate_text_length" in metrics["metrics"]
        assert "embedding_generate_dimension" in metrics["metrics"]

    def test_cache_event_emission(self):
        """Test cache event emission."""
        emitter = SystemLearningTelemetryEmitter("test_component")

        # Emit cache event
        emitter.emit_cache_event(
            operation="get",
            key="test_key",
            hit=True,
            size_bytes=1024,
            ttl_seconds=3600,
        )

        # Check metrics
        metrics = emitter.get_metrics_summary()
        assert "cache_get_hit_rate" in metrics["metrics"]
        assert "cache_get_size" in metrics["metrics"]

    def test_drift_event_emission(self):
        """Test drift event emission."""
        emitter = SystemLearningTelemetryEmitter("test_component")

        # Emit drift event
        emitter.emit_drift_event(
            drift_score=0.25,
            drift_type="score_distribution",
            indicators={
                "high_score_ratio": 0.8,
                "score_variance": 0.15,
            },
            threshold=0.2,
        )

        # Check metrics
        metrics = emitter.get_metrics_summary()
        assert "drift_score_score_distribution" in metrics["metrics"]

    def test_metrics_summary(self):
        """Test metrics summary functionality."""
        emitter = SystemLearningTelemetryEmitter("test_component")

        # Add some operations and metrics
        emitter.start_operation(SystemLearningOperationType.CACHE_GET)
        emitter.emit_metric("test_metric", 42, unit="count")

        # Get summary
        summary = emitter.get_metrics_summary()

        assert "component" in summary
        assert "session_id" in summary
        assert "total_metrics" in summary
        assert "operation_counts" in summary
        assert "metrics" in summary
        assert summary["component"] == "test_component"

    def test_metrics_reset(self):
        """Test metrics reset functionality."""
        emitter = SystemLearningTelemetryEmitter("test_component")

        # Add some data
        emitter.emit_metric("test_metric", 42)
        emitter.start_operation(SystemLearningOperationType.CACHE_GET)

        # Reset metrics
        emitter.reset_metrics()

        # Check reset
        summary = emitter.get_metrics_summary()
        assert summary["total_metrics"] == 0
        assert len(summary["operation_counts"]) == 0
        assert len(summary["error_counts"]) == 0


# System Learning Policy Integration Tests
class TestSystemLearningPolicyIntegration:
    """Test suite for SystemLearningPolicyValidator."""

    @pytest.mark.asyncio
    async def test_policy_validator_initialization(self):
        """Test policy validator initialization."""
        validator = SystemLearningPolicyValidator("test_component")

        assert validator.component_name == "test_component"
        assert validator.enable_policy_caching is True
        assert validator.policy_cache_ttl == 3600
        assert isinstance(validator._policy_contexts, dict)
        assert isinstance(validator._validation_cache, dict)

    @pytest.mark.asyncio
    async def test_policy_context_registration(self, sample_policy_context):
        """Test policy context registration."""
        validator = SystemLearningPolicyValidator("test_component")

        validator.register_policy_context(sample_policy_context)

        policy_key = f"{sample_policy_context.policy_type.value}:{sample_policy_context.policy_hash}"
        assert policy_key in validator._policy_contexts
        assert validator._policy_contexts[policy_key] == sample_policy_context

    @pytest.mark.asyncio
    async def test_cache_operation_validation(self, sample_policy_context):
        """Test cache operation validation."""
        validator = SystemLearningPolicyValidator("test_component")
        validator.register_policy_context(sample_policy_context)

        result = await validator.validate_cache_operation(
            operation="get",
            cache_key="test_key",
            data_size=1024,
            policy_hash=sample_policy_context.policy_hash,
        )

        assert result.validation_type == PolicyValidationType.CACHE_POLICY
        assert result.policy_context == sample_policy_context
        assert result.is_compliant is True
        assert result.status == PolicyComplianceStatus.COMPLIANT
        assert result.score >= 0.0

    @pytest.mark.asyncio
    async def test_retrieval_operation_validation(self, sample_policy_context):
        """Test retrieval operation validation."""
        validator = SystemLearningPolicyValidator("test_component")
        validator.register_policy_context(sample_policy_context)

        result = await validator.validate_retrieval_operation(
            query_text="test query text",
            result_count=5,
            similarity_scores=[0.9, 0.8, 0.7, 0.6, 0.5],
            policy_hash=sample_policy_context.policy_hash,
        )

        assert result.validation_type == PolicyValidationType.RETRIEVAL_POLICY
        assert result.policy_context == sample_policy_context
        assert result.is_compliant is True
        assert result.status == PolicyComplianceStatus.COMPLIANT

    @pytest.mark.asyncio
    async def test_embedding_operation_validation(self, sample_policy_context):
        """Test embedding operation validation."""
        validator = SystemLearningPolicyValidator("test_component")
        validator.register_policy_context(sample_policy_context)

        result = await validator.validate_embedding_operation(
            text_length=1000,
            embedding_dimension=1536,
            model_name="text-embedding-3-large",
            policy_hash=sample_policy_context.policy_hash,
        )

        assert result.validation_type == PolicyValidationType.EMBEDDING_POLICY
        assert result.policy_context == sample_policy_context
        assert result.is_compliant is True
        assert result.status == PolicyComplianceStatus.COMPLIANT

    @pytest.mark.asyncio
    async def test_learning_operation_validation(self, sample_policy_context):
        """Test learning operation validation."""
        validator = SystemLearningPolicyValidator("test_component")
        validator.register_policy_context(sample_policy_context)

        result = await validator.validate_learning_operation(
            learning_rate=0.001,
            batch_size=32,
            model_version="1.0",
            policy_hash=sample_policy_context.policy_hash,
        )

        assert result.validation_type == PolicyValidationType.LEARNING_POLICY
        assert result.policy_context == sample_policy_context
        assert result.is_compliant is True
        assert result.status == PolicyComplianceStatus.COMPLIANT

    @pytest.mark.asyncio
    async def test_policy_violation_detection(self):
        """Test policy violation detection."""
        validator = SystemLearningPolicyValidator("test_component")

        # Create restrictive policy context
        restrictive_policy = PolicyContext(
            policy_hash="restrictive_policy",
            policy_version="1.0",
            policy_type=PolicyValidationType.CACHE_POLICY,
            max_cache_size=100,  # Very small limit
        )
        validator.register_policy_context(restrictive_policy)

        # Try to validate operation that violates policy
        result = await validator.validate_cache_operation(
            operation="set",
            cache_key="test_key",
            data_size=1000,  # Exceeds limit
            policy_hash="restrictive_policy",
        )

        assert result.is_compliant is False
        assert result.status == PolicyComplianceStatus.NON_COMPLIANT
        assert len(result.violations) > 0
        assert "exceeds limit" in result.violations[0].lower()

    @pytest.mark.asyncio
    async def test_policy_caching(self, sample_policy_context):
        """Test policy validation caching."""
        validator = SystemLearningPolicyValidator(
            "test_component",
            enable_policy_caching=True,
        )
        validator.register_policy_context(sample_policy_context)

        # First validation (should cache)
        result1 = await validator.validate_cache_operation(
            operation="get",
            cache_key="test_key",
            policy_hash=sample_policy_context.policy_hash,
        )

        # Second validation (should use cache)
        result2 = await validator.validate_cache_operation(
            operation="get",
            cache_key="test_key",
            policy_hash=sample_policy_context.policy_hash,
        )

        assert result1.validation_type == result2.validation_type
        assert result1.is_compliant == result2.is_compliant
        assert validator._metrics["policy_cache_hits"] >= 1

    def test_policy_aware_cache_key_building(self):
        """Test policy-aware cache key building."""
        validator = SystemLearningPolicyValidator("test_component")

        # Test without policy hash
        key1 = validator.build_policy_aware_cache_key("base_key")
        assert key1 == "base_key"

        # Test with policy hash
        key2 = validator.build_policy_aware_cache_key("base_key", "policy_hash_123")
        assert key2 == "base_key:policy:policy_h"
        assert key2.endswith("policy_h")  # Truncated hash

    def test_metrics_tracking(self):
        """Test metrics tracking functionality."""
        validator = SystemLearningPolicyValidator("test_component")

        # Check initial metrics
        metrics = validator.get_metrics()
        assert metrics["validations_performed"] == 0
        assert metrics["compliant_operations"] == 0
        assert metrics["non_compliant_operations"] == 0
        assert metrics["compliance_rate"] == 0.0

        # Reset metrics
        validator.reset_metrics()
        metrics = validator.get_metrics()
        assert metrics["validations_performed"] == 0


# System Learning State Management Tests
class TestSystemLearningStateManager:
    """Test suite for SystemLearningStateManager."""

    @pytest.mark.asyncio
    async def test_state_manager_initialization(self):
        """Test state manager initialization."""
        manager = SystemLearningStateManager("test_component")

        assert manager.component_name == "test_component"
        assert manager.enable_state_caching is True
        assert manager.enable_lineage_tracking is True
        assert manager.max_snapshots_per_type == 1000
        assert isinstance(manager._snapshots, dict)
        assert isinstance(manager._lineage, list)

    @pytest.mark.asyncio
    async def test_state_snapshot_creation(self):
        """Test state snapshot creation."""
        manager = SystemLearningStateManager("test_component")

        snapshot = await manager.create_state_snapshot(
            state_type=SystemLearningStateType.LEARNING_SESSION,
            state_data={
                "model_version": "1.0",
                "batch_size": 32,
                "learning_rate": 0.001,
            },
            config_hashes={"model_config": "config_hash_123"},
            policy_hashes={"learning_policy": "policy_hash_456"},
        )

        assert snapshot.state_type == SystemLearningStateType.LEARNING_SESSION
        assert snapshot.component_name == "test_component"
        assert snapshot.state_id is not None
        assert snapshot.snapshot_hash is not None
        assert len(snapshot.snapshot_hash) == 64  # SHA-256 hex
        assert snapshot.version == 1
        assert snapshot.is_validated is True
        assert len(snapshot.validation_errors) == 0
        assert snapshot.state_data["model_version"] == "1.0"

    @pytest.mark.asyncio
    async def test_state_snapshot_retrieval(self):
        """Test state snapshot retrieval."""
        manager = SystemLearningStateManager("test_component")

        # Create snapshot
        snapshot = await manager.create_state_snapshot(
            state_type=SystemLearningStateType.MODEL_STATE,
            state_data={"weights": [0.1, 0.2, 0.3]},
        )

        # Retrieve snapshot
        retrieved = await manager.get_state_snapshot(snapshot.state_id)

        assert retrieved is not None
        assert retrieved.state_id == snapshot.state_id
        assert retrieved.snapshot_hash == snapshot.snapshot_hash
        assert retrieved.state_data == snapshot.state_data
        assert retrieved.access_count == 1
        assert retrieved.last_accessed is not None

    @pytest.mark.asyncio
    async def test_state_snapshot_update(self):
        """Test state snapshot update."""
        manager = SystemLearningStateManager("test_component")

        # Create initial snapshot
        snapshot = await manager.create_state_snapshot(
            state_type=SystemLearningStateType.CONFIG_STATE,
            state_data={"param1": "value1"},
        )

        # Update with new version
        updated = await manager.update_state_snapshot(
            state_id=snapshot.state_id,
            state_data={"param1": "value1", "param2": "value2"},
            create_new_version=True,
        )

        assert updated is not None
        assert updated.state_id != snapshot.state_id  # New snapshot created
        assert updated.version == 2
        assert updated.parent_snapshot_hash == snapshot.snapshot_hash
        assert updated.state_data["param2"] == "value2"

    @pytest.mark.asyncio
    async def test_state_lineage_tracking(self):
        """Test state lineage tracking."""
        manager = SystemLearningStateManager(
            "test_component",
            enable_lineage_tracking=True,
        )

        # Create parent snapshot
        parent = await manager.create_state_snapshot(
            state_type=SystemLearningStateType.TRAINING_STATE,
            state_data={"epoch": 1},
        )

        # Create child snapshot
        child = await manager.create_state_snapshot(
            state_type=SystemLearningStateType.TRAINING_STATE,
            state_data={"epoch": 2},
            parent_state_id=parent.state_id,
        )

        # Check lineage
        lineage = await manager.get_state_lineage(child.state_id)

        assert len(lineage) > 0
        assert lineage[0].parent_state_id == parent.state_id
        assert lineage[0].child_state_id == child.state_id
        assert lineage[0].lineage_type == StateLineageType.PARENT_CHILD

    @pytest.mark.asyncio
    async def test_snapshots_by_type_retrieval(self):
        """Test retrieving snapshots by type."""
        manager = SystemLearningStateManager("test_component")

        # Create snapshots of different types
        await manager.create_state_snapshot(
            state_type=SystemLearningStateType.CACHE_STATE,
            state_data={"size": 1000},
        )
        await manager.create_state_snapshot(
            state_type=SystemLearningStateType.CACHE_STATE,
            state_data={"size": 2000},
        )
        await manager.create_state_snapshot(
            state_type=SystemLearningStateType.EMBEDDING_STATE,
            state_data={"dimension": 1536},
        )

        # Get cache state snapshots
        cache_snapshots = await manager.get_snapshots_by_type(SystemLearningStateType.CACHE_STATE)

        assert len(cache_snapshots) == 2
        assert all(s.state_type == SystemLearningStateType.CACHE_STATE for s in cache_snapshots)

        # Get embedding state snapshots
        embedding_snapshots = await manager.get_snapshots_by_type(SystemLearningStateType.EMBEDDING_STATE)

        assert len(embedding_snapshots) == 1
        assert embedding_snapshots[0].state_type == SystemLearningStateType.EMBEDDING_STATE

    @pytest.mark.asyncio
    async def test_state_snapshot_deletion(self):
        """Test state snapshot deletion."""
        manager = SystemLearningStateManager("test_component")

        # Create snapshot
        snapshot = await manager.create_state_snapshot(
            state_type=SystemLearningStateType.PERFORMANCE_STATE,
            state_data={"accuracy": 0.95},
        )

        # Delete snapshot
        success = await manager.delete_state_snapshot(snapshot.state_id)

        assert success is True

        # Try to retrieve deleted snapshot
        retrieved = await manager.get_state_snapshot(snapshot.state_id)
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_state_validation(self):
        """Test state snapshot validation."""
        manager = SystemLearningStateManager("test_component")

        # Create valid snapshot
        valid_snapshot = await manager.create_state_snapshot(
            state_type=SystemLearningStateType.TELEMETRY_STATE,
            state_data={"events": 100},
        )

        assert valid_snapshot.is_validated is True
        assert len(valid_snapshot.validation_errors) == 0

        # Manually corrupt snapshot for testing
        corrupted_snapshot = SystemLearningStateSnapshot(
            state_id="test_id",
            state_type=SystemLearningStateType.TELEMETRY_STATE,
            component_name="test_component",
            snapshot_hash="invalid_hash",  # Invalid hash
            state_data={"events": 100},
        )

        await manager._validate_snapshot(corrupted_snapshot)

        assert corrupted_snapshot.is_validated is False
        assert len(corrupted_snapshot.validation_errors) > 0
        assert "Hash mismatch" in corrupted_snapshot.validation_errors[0]

    @pytest.mark.asyncio
    async def test_state_caching(self):
        """Test state snapshot caching."""
        manager = SystemLearningStateManager(
            "test_component",
            enable_state_caching=True,
        )

        # Create snapshot (should be cached)
        snapshot = await manager.create_state_snapshot(
            state_type=SystemLearningStateType.DRIFT_STATE,
            state_data={"drift_score": 0.1},
        )

        # Retrieve from cache
        cached_snapshot = await manager._get_cached_snapshot(snapshot.state_id)

        assert cached_snapshot is not None
        assert cached_snapshot.state_id == snapshot.state_id
        assert cached_snapshot.snapshot_hash == snapshot.snapshot_hash

    def test_metrics_tracking(self):
        """Test metrics tracking functionality."""
        manager = SystemLearningStateManager("test_component")

        # Check initial metrics
        metrics = manager.get_metrics()
        assert metrics["snapshots_created"] == 0
        assert metrics["snapshots_accessed"] == 0
        assert metrics["total_snapshots"] == 0
        assert metrics["total_lineage_entries"] == 0
        assert metrics["validation_success_rate"] == 0.0

        # Reset metrics
        manager.reset_metrics()
        metrics = manager.get_metrics()
        assert metrics["snapshots_created"] == 0


# Integration Tests
class TestInfrastructureIntegration:
    """Integration tests for all infrastructure components."""

    @pytest.mark.asyncio
    async def test_end_to_end_workflow(
        self, mock_embedding_client, mock_redis_cache, sample_retrieval_results
    ):
        """Test end-to-end workflow with all components."""
        # Initialize components
        cache = EnhancedRagRetrievalCache(
            embedding_client=mock_embedding_client,
            cache=mock_redis_cache,
        )

        admission_gate = SystemLearningCacheAdmissionGate()

        telemetry_emitter = SystemLearningTelemetryEmitter("integration_test")

        policy_validator = SystemLearningPolicyValidator("integration_test")

        state_manager = SystemLearningStateManager("integration_test")

        # Start telemetry operation
        op_context = telemetry_emitter.start_operation(SystemLearningOperationType.RETRIEVAL_QUERY)

        try:
            # 1. Validate retrieval operation against policy
            policy_result = await policy_validator.validate_retrieval_operation(
                query_text="test query for integration",
                result_count=len(sample_retrieval_results),
                similarity_scores=[r["score"] for r in sample_retrieval_results],
            )

            assert policy_result.is_compliant is True

            # 2. Check cache admission
            admission_context = SystemLearningAdmissionContext(
                u0_hash="integration_u0_hash",
                policy_hash="integration_policy_hash",
                embedder_version="v1.0",
                confidence_threshold=0.6,
            )

            admission_decision = await admission_gate.evaluate_admission(
                context=admission_context,
                retrieval_results=sample_retrieval_results,
                query_text="test query for integration",
            )

            assert admission_decision.admitted is True

            # 3. Cache the results
            cache_success = await cache.set(
                u0_hash="integration_u0_hash",
                embedder_version="v1.0",
                seed_pack_manifest_hash="integration_manifest",
                k=3,
                cutoff=0.7,
                results=sample_retrieval_results,
                query_text="test query for integration",
                policy_hash="integration_policy_hash",
            )

            assert cache_success is True

            # 4. Create state snapshot
            state_snapshot = await state_manager.create_state_snapshot(
                state_type=SystemLearningStateType.RETRIEVAL_STATE,
                state_data={
                    "query": "test query for integration",
                    "result_count": len(sample_retrieval_results),
                    "policy_compliant": policy_result.is_compliant,
                    "admission_approved": admission_decision.admitted,
                    "cached": cache_success,
                },
                config_hashes={
                    "cache_config": "cache_config_hash",
                    "policy_config": "policy_config_hash",
                },
            )

            assert state_snapshot.state_type == SystemLearningStateType.RETRIEVAL_STATE

            # 5. Retrieve from cache
            cached_results = await cache.get(
                u0_hash="integration_u0_hash",
                embedder_version="v1.0",
                seed_pack_manifest_hash="integration_manifest",
                k=3,
                cutoff=0.7,
                policy_hash="integration_policy_hash",
            )

            assert cached_results is not None
            assert len(cached_results) == len(sample_retrieval_results)

            # End telemetry operation successfully
            telemetry_emitter.end_operation(
                op_context,
                success=True,
                result={"cached_results_count": len(cached_results)},
                cache_hit=True,
                policy_compliant=policy_result.is_compliant,
                admission_approved=admission_decision.admitted,
            )

        except Exception as e:
            # End telemetry operation with error
            telemetry_emitter.end_operation(
                op_context,
                success=False,
                error=e,
            )
            raise

        # Verify all components have metrics
        cache_metrics = cache.get_metrics()
        assert cache_metrics["cache_hits"] >= 1
        assert cache_metrics["cache_misses"] >= 0

        admission_metrics = admission_gate.get_metrics()
        assert admission_metrics["admissions"] >= 1
        assert admission_metrics["denials"] >= 0

        telemetry_metrics = telemetry_emitter.get_metrics_summary()
        assert telemetry_metrics["total_metrics"] > 0
        assert telemetry_metrics["operation_counts"].get("retrieval_query", 0) >= 1

        policy_metrics = policy_validator.get_metrics()
        assert policy_metrics["validations_performed"] >= 1
        assert policy_metrics["compliant_operations"] >= 1

        state_metrics = state_manager.get_metrics()
        assert state_metrics["snapshots_created"] >= 1
        assert state_metrics["total_snapshots"] >= 1

    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self, mock_redis_cache):
        """Test error handling and recovery mechanisms."""

        # Test with failing embedding client
        class FailingEmbeddingClient:
            async def get_embedding(self, guarded_text):
                raise RuntimeError("Embedding service unavailable")

            async def get_embeddings_batch(self, guarded_texts):
                raise RuntimeError("Embedding service unavailable")

        failing_client = FailingEmbeddingClient()

        cache = EnhancedRagRetrievalCache(
            embedding_client=failing_client,
            cache=mock_redis_cache,
        )

        telemetry_emitter = SystemLearningTelemetryEmitter("error_test")

        # Start operation
        op_context = telemetry_emitter.start_operation(SystemLearningOperationType.EMBEDDING_GENERATE)

        try:
            # Try cache operation with failing embedding client
            result = await cache.get(
                u0_hash="error_test_u0_hash",
                embedder_version="v1.0",
                seed_pack_manifest_hash="error_test_manifest",
                k=3,
                cutoff=0.7,
                query_text="test query with failing embedding",
            )

            # Should return None due to embedding failure
            assert result is None

            # End operation with error
            telemetry_emitter.end_operation(
                op_context,
                success=False,
                error=RuntimeError("Embedding service unavailable"),
            )

        except Exception as e:
            telemetry_emitter.end_operation(op_context, success=False, error=e)
            raise

        # Verify error metrics
        telemetry_metrics = telemetry_emitter.get_metrics_summary()
        assert telemetry_metrics["error_counts"].get("RuntimeError", 0) >= 1

        # Verify cache handled error gracefully
        cache_metrics = cache.get_metrics()
        assert cache_metrics["fallback_activations"] >= 1

    @pytest.mark.asyncio
    async def test_performance_under_load(self, mock_embedding_client, mock_redis_cache):
        """Test performance under concurrent load."""
        import concurrent.futures

        cache = EnhancedRagRetrievalCache(
            embedding_client=mock_embedding_client,
            cache=mock_redis_cache,
        )

        telemetry_emitter = SystemLearningTelemetryEmitter("performance_test")

        # Performance test parameters
        num_operations = 50
        concurrent_workers = 5

        async def perform_cache_operation(operation_id: int):
            """Perform a cache operation with telemetry."""
            op_context = telemetry_emitter.start_operation(SystemLearningOperationType.CACHE_SET)

            try:
                # Set cache entry
                success = await cache.set(
                    u0_hash=f"perf_test_u0_{operation_id}",
                    embedder_version="v1.0",
                    seed_pack_manifest_hash="perf_test_manifest",
                    k=3,
                    cutoff=0.7,
                    results=[{"chunk_id": f"chunk_{operation_id}", "score": 0.8}],
                    query_text=f"performance test query {operation_id}",
                )

                # Get cache entry
                result = await cache.get(
                    u0_hash=f"perf_test_u0_{operation_id}",
                    embedder_version="v1.0",
                    seed_pack_manifest_hash="perf_test_manifest",
                    k=3,
                    cutoff=0.7,
                )

                telemetry_emitter.end_operation(
                    op_context,
                    success=True,
                    result={"cache_hit": result is not None},
                    operation_id=operation_id,
                )

                return success and result is not None

            except Exception as e:
                telemetry_emitter.end_operation(op_context, success=False, error=e)
                return False

        # Run concurrent operations
        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_workers) as executor:
            futures = [
                executor.submit(asyncio.run, perform_cache_operation(i)) for i in range(num_operations)
            ]

            results = [future.result() for future in concurrent.futures.as_completed(futures)]

        end_time = time.time()
        duration = end_time - start_time

        # Verify performance
        success_rate = sum(results) / len(results)
        operations_per_second = num_operations / duration

        assert success_rate >= 0.9, f"Success rate: {success_rate}"
        assert operations_per_second >= 10, f"Ops/sec: {operations_per_second}"

        # Verify metrics
        cache_metrics = cache.get_metrics()
        telemetry_metrics = telemetry_emitter.get_metrics_summary()

        assert cache_metrics["cache_hits"] >= num_operations * 0.8
        assert telemetry_metrics["total_metrics"] >= num_operations

        logger.info(
            f"Performance test completed: {num_operations} ops in {duration:.2f}s "
            f"({operations_per_second:.2f} ops/sec, {success_rate:.2%} success rate)"
        )


# Test Configuration
def pytest_configure(config):
    """Configure pytest for system learning infrastructure tests."""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")


# Test Execution Entry Point
if __name__ == "__main__":
    # Run tests when executed directly
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "-x",  # Stop on first failure
            "--disable-warnings",
        ]
    )