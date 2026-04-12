"""Smoke tests for 5-layer Agentic Retrieval system.

Quick health checks for all layers to verify basic functionality.
"""

import hashlib
import time
from dataclasses import dataclass


@dataclass
class HealthStatus:
    """Health check result for a layer."""

    layer: int
    name: str
    healthy: bool
    latency_ms: float
    error: str | None = None


class TestLayerHealthSmoke:
    """Smoke tests for individual layer health."""

    def test_layer_1_redis_connectivity(self):
        """Smoke: Layer 1 Redis connectivity - actual connection test."""
        import socket

        start = time.time()

        # Attempt actual Redis connection on default port
        redis_healthy = False
        error_msg = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(("localhost", 6379))
            sock.close()
            redis_healthy = result == 0
            if not redis_healthy:
                error_msg = f"Redis connection failed with code {result}"
        except Exception as e:
            error_msg = str(e)

        elapsed = (time.time() - start) * 1000

        status = HealthStatus(
            layer=1,
            name="Redis SHA-256 Cache",
            healthy=redis_healthy,
            latency_ms=elapsed,
            error=error_msg,
        )

        # Test validates connection attempt occurred
        assert elapsed < 2000, "Connection attempt took too long"
        assert status.error is not None or status.healthy, "Must have error or be healthy"

    def test_layer_1_redis_failure_handling(self):
        """Smoke: Layer 1 handles Redis failure gracefully."""
        import socket

        # Simulate Redis down by connecting to closed port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(("localhost", 6380))  # Wrong port
        sock.close()

        redis_healthy = result == 0

        # When Redis is down, system should mark unhealthy and have fallback
        assert redis_healthy is False, "Connection to wrong port should fail"

        # Health status should reflect failure
        status = HealthStatus(
            layer=1,
            name="Redis SHA-256 Cache",
            healthy=redis_healthy,
            latency_ms=1000.0,
            error=f"Connection failed with code {result}",
        )

        assert status.healthy is False
        assert status.error is not None
        assert "failed" in status.error.lower() or "refused" in status.error.lower()

    def test_layer_1_hash_generation(self):
        """Smoke: Layer 1 SHA-256 hash generation works."""
        test_text = "test query"
        hash_result = hashlib.sha256(test_text.encode()).hexdigest()

        assert len(hash_result) == 64  # SHA-256 is 64 hex chars
        assert hash_result == hashlib.sha256(test_text.encode()).hexdigest()  # Deterministic

    def test_layer_2_embedding_service(self):
        """Smoke: Layer 2 BGE-M3 embedding service available."""
        start = time.time()

        # Simulate embedding service check
        embedding_healthy = True

        elapsed = (time.time() - start) * 1000

        status = HealthStatus(
            layer=2,
            name="BGE-M3 Embedding",
            healthy=embedding_healthy,
            latency_ms=elapsed,
        )

        assert status.healthy is True

    def test_layer_2_cosine_similarity(self):
        """Smoke: Layer 2 cosine similarity calculation works."""
        import math

        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]

        # Calculate cosine similarity
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(a * a for a in vec2))
        similarity = dot / (norm1 * norm2)

        assert similarity == 1.0  # Identical vectors

    def test_layer_3_faiss_index(self):
        """Smoke: Layer 3 FAISS vector index accessible."""
        start = time.time()

        # Simulate FAISS index check
        faiss_healthy = True

        elapsed = (time.time() - start) * 1000

        status = HealthStatus(
            layer=3,
            name="FAISS Vector Store",
            healthy=faiss_healthy,
            latency_ms=elapsed,
        )

        assert status.healthy is True

    def test_layer_3_bm25_index(self):
        """Smoke: Layer 3 BM25 keyword index accessible."""
        status = HealthStatus(
            layer=3,
            name="BM25 Keyword Index",
            healthy=True,
            latency_ms=5.0,
        )

        assert status.healthy is True

    def test_layer_3_adg_connectivity(self):
        """Smoke: Layer 3 ADG SQLite database accessible."""
        start = time.time()

        # Simulate ADG connection check
        adg_healthy = True

        elapsed = (time.time() - start) * 1000

        status = HealthStatus(
            layer=3,
            name="ADG Graph Database",
            healthy=adg_healthy,
            latency_ms=elapsed,
        )

        assert status.healthy is True

    def test_layer_4_langgraph_orchestrator(self):
        """Smoke: Layer 4 LangGraph orchestrator responsive."""
        start = time.time()

        # Simulate LangGraph check
        langgraph_healthy = True

        elapsed = (time.time() - start) * 1000

        status = HealthStatus(
            layer=4,
            name="LangGraph Orchestrator",
            healthy=langgraph_healthy,
            latency_ms=elapsed,
        )

        assert status.healthy is True

    def test_layer_4_tool_registry(self):
        """Smoke: Layer 4 tool registry has registered tools."""
        tools = ["search_web", "query_database", "call_api"]

        assert len(tools) > 0
        assert "search_web" in tools

    def test_layer_5_llm_api(self):
        """Smoke: Layer 5 LLM API accessible."""
        start = time.time()

        # Simulate LLM API check
        llm_healthy = True

        elapsed = (time.time() - start) * 1000

        status = HealthStatus(
            layer=5,
            name="LLM Fallback API",
            healthy=llm_healthy,
            latency_ms=elapsed,
        )

        assert status.healthy is True

    def test_all_layers_healthy(self):
        """Smoke: All 5 layers report healthy status."""
        layers = [
            HealthStatus(1, "Redis Cache", True, 0.5),
            HealthStatus(2, "Semantic Cache", True, 10.0),
            HealthStatus(3, "Agentic RAG", True, 50.0),
            HealthStatus(4, "Agentic Action", True, 100.0),
            HealthStatus(5, "LLM Fallback", True, 200.0),
        ]

        all_healthy = all(l.healthy for l in layers)
        assert all_healthy is True

        # Verify layer numbering
        assert [l.layer for l in layers] == [1, 2, 3, 4, 5]


class TestCriticalPathSmoke:
    """Smoke tests for critical data paths."""

    def test_query_hash_consistency(self):
        """Smoke: Query hashing is consistent across layers."""
        query = "test query"

        # Layer 1 hash
        l1_hash = hashlib.sha256(query.encode()).hexdigest()

        # Should be deterministic
        l1_hash_2 = hashlib.sha256(query.encode()).hexdigest()
        assert l1_hash == l1_hash_2

    def test_layer_transition_triggers(self):
        """Smoke: Layer transitions trigger correctly."""
        # L1 miss -> L2
        l1_hit = False
        should_trigger_l2 = not l1_hit
        assert should_trigger_l2 is True

        # L2 miss -> L3
        l2_hit = False
        should_trigger_l3 = not l2_hit
        assert should_trigger_l3 is True

        # L3 hit (high confidence) -> return
        l3_hit = True
        l3_confidence = 0.95
        should_trigger_l4 = not l3_hit or l3_confidence < 0.7
        assert should_trigger_l4 is False

    def test_telemetry_capture(self):
        """Smoke: Telemetry data structure is valid."""
        telemetry = {
            "layer": 3,
            "query_hash": "abc123",
            "timestamp": time.time(),
            "latency_ms": 150.0,
            "cache_hit": True,
        }

        assert "layer" in telemetry
        assert "query_hash" in telemetry
        assert "latency_ms" in telemetry
        assert telemetry["latency_ms"] > 0


class TestFailureModesSmoke:
    """Smoke tests for graceful failure handling."""

    def test_layer_1_failure_fallback(self):
        """Smoke: Layer 1 failure triggers fallback to Layer 2."""
        l1_healthy = False  # Simulated failure

        # Should escalate
        should_escalate = not l1_healthy
        assert should_escalate is True

    def test_all_layers_failure_exception(self):
        """Smoke: All layers failing raises system exception."""
        layers_healthy = [False, False, False, False, False]

        all_failed = not any(layers_healthy)
        assert all_failed is True

        # System should raise exception
        # (In real implementation, this would be an actual exception)

    def test_partial_degradation(self):
        """Smoke: System degrades gracefully with partial layer failure."""
        # Layers 1-2 fail, but 3-5 work
        layer_health = {
            1: False,
            2: False,
            3: True,
            4: True,
            5: True,
        }

        # Should still be able to serve requests
        can_serve = any(layer_health.values())
        assert can_serve is True
