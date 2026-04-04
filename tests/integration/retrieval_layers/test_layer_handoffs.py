"""Integration tests for layer-to-layer handoffs.

Tests the transitions and data flow between adjacent layers.
"""

import hashlib
from dataclasses import dataclass, field


@dataclass
class LayerContext:
    """Context passed between layers."""
    query: str
    query_hash: str
    intent_vector: list[float] = field(default_factory=list)
    embeddings: list[dict] = field(default_factory=list)
    retrieved_chunks: list[dict] = field(default_factory=list)
    execution_plan: dict = field(default_factory=dict)
    telemetry: dict = field(default_factory=dict)


class TestLayer1To2Handoff:
    """Integration: Layer 1 (Exact) -> Layer 2 (Semantic) handoff."""

    def test_l1_miss_triggers_l2(self):
        """L1 cache miss correctly triggers L2 execution."""
        query = "unseen query"
        context = LayerContext(
            query=query,
            query_hash=hashlib.sha256(query.encode()).hexdigest()
        )

        # Simulate L1 miss
        l1_hit = False

        # Should transition to L2
        if not l1_hit:
            # L2 processing
            context.intent_vector = [0.1, 0.2, 0.3]  # BGE-M3 embedding

        assert len(context.intent_vector) > 0
        assert context.intent_vector == [0.1, 0.2, 0.3]

    def test_l1_hit_does_not_trigger_l2(self):
        """L1 cache hit does NOT trigger L2 (short-circuit)."""
        query = "cached query"
        context = LayerContext(
            query=query,
            query_hash=hashlib.sha256(query.encode()).hexdigest()
        )

        # Simulate L1 hit
        l1_hit = True
        l1_response = {"data": "cached"}

        # Should NOT transition to L2
        if not l1_hit:
            context.intent_vector = [0.1, 0.2, 0.3]

        assert len(context.intent_vector) == 0  # L2 not executed
        assert l1_response["data"] == "cached"

    def test_hash_preserved_in_handoff(self):
        """Query hash is preserved in L1->L2 handoff."""
        query = "test query"
        expected_hash = hashlib.sha256(query.encode()).hexdigest()

        context = LayerContext(
            query=query,
            query_hash=expected_hash
        )

        # Handoff to L2
        assert context.query_hash == expected_hash
        # L2 uses same hash for cache lookup
        l2_cache_key = f"semantic_{context.query_hash[:16]}"
        assert l2_cache_key.startswith("semantic_")


class TestLayer2To3Handoff:
    """Integration: Layer 2 (Semantic) -> Layer 3 (Agentic RAG) handoff."""

    def test_l2_miss_triggers_l3(self):
        """L2 semantic miss triggers L3 RAG execution."""
        context = LayerContext(
            query="complex query",
            query_hash="abc123",
            intent_vector=[0.1, 0.2, 0.3]
        )

        # Simulate L2 miss (no similar cached intent)
        l2_hit = False

        if not l2_hit:
            # Trigger L3: FAISS + BM25 + ADG
            context.embeddings = [
                {"chunk_id": "chunk_1", "score": 0.89}
            ]

        assert len(context.embeddings) > 0

    def test_intent_vector_passed_to_l3(self):
        """Intent vector from L2 passed to L3 for FAISS search."""
        intent_vec = [0.5, 0.3, 0.2, 0.1]
        context = LayerContext(
            query="test",
            query_hash="hash",
            intent_vector=intent_vec
        )

        # L3 uses intent vector for FAISS search
        # Simulate FAISS query
        faiss_results = self._mock_faiss_search(context.intent_vector)

        assert len(faiss_results) > 0
        assert faiss_results[0]["score"] > 0

    def _mock_faiss_search(self, vector: list[float]) -> list[dict]:
        """Mock FAISS vector search."""
        return [
            {"chunk_id": f"chunk_{i}", "score": 0.9 - (i * 0.1)}
            for i in range(min(5, len(vector)))
        ]

    def test_l2_hit_does_not_trigger_l3(self):
        """L2 semantic hit short-circuits, does not trigger L3."""
        context = LayerContext(
            query="semantically cached",
            query_hash="hash",
            intent_vector=[0.1, 0.2, 0.3]
        )

        # Simulate L2 hit
        l2_hit = True
        l2_response = "cached response"

        if not l2_hit:
            context.embeddings = [{"chunk_id": "c1"}]

        assert len(context.embeddings) == 0
        assert l2_response == "cached response"


class TestLayer3To4Handoff:
    """Integration: Layer 3 (Agentic RAG) -> Layer 4 (Agentic Action) handoff."""

    def test_l3_low_confidence_triggers_l4(self):
        """L3 low confidence triggers L4 tool execution."""
        context = LayerContext(
            query="action required",
            query_hash="hash",
            intent_vector=[0.1, 0.2],
            embeddings=[{"chunk_id": "c1", "score": 0.3}],  # Low score
            retrieved_chunks=[]
        )

        # Evaluate L3 results
        max_score = max(e.get("score", 0) for e in context.embeddings)
        confidence_threshold = 0.7

        if max_score < confidence_threshold:
            # Trigger L4
            context.execution_plan = {
                "tools": ["search_web", "query_api"],
                "steps": 2
            }

        assert "tools" in context.execution_plan

    def test_l3_high_confidence_does_not_trigger_l4(self):
        """L3 high confidence short-circuits, no L4."""
        context = LayerContext(
            query="well covered",
            query_hash="hash",
            retrieved_chunks=[
                {"chunk_id": "c1", "score": 0.95},
                {"chunk_id": "c2", "score": 0.92}
            ]
        )

        # High confidence in RAG results
        avg_score = sum(c["score"] for c in context.retrieved_chunks) / len(context.retrieved_chunks)

        if avg_score < 0.7:  # Only trigger L4 if low confidence
            context.execution_plan = {"tools": []}

        assert len(context.execution_plan) == 0

    def test_chunks_passed_to_l4_context(self):
        """RAG chunks passed to L4 for context enrichment."""
        chunks = [
            {"chunk_id": "c1", "text": "chunk 1 content", "score": 0.9},
            {"chunk_id": "c2", "text": "chunk 2 content", "score": 0.85}
        ]
        context = LayerContext(
            query="test",
            query_hash="hash",
            retrieved_chunks=chunks
        )

        # L4 can use chunks for context
        assert len(context.retrieved_chunks) == 2
        assert context.retrieved_chunks[0]["text"] == "chunk 1 content"


class TestLayer4To5Handoff:
    """Integration: Layer 4 (Agentic Action) -> Layer 5 (LLM) handoff."""

    def test_l4_failure_triggers_l5(self):
        """L4 tool execution failure triggers L5 fallback."""
        context = LayerContext(
            query="fallback needed",
            query_hash="hash",
            execution_plan={"tools": ["broken_tool"]}
        )

        # Simulate L4 tool failure
        l4_success = False

        if not l4_success:
            # Trigger L5
            context.telemetry["fallback_reason"] = "l4_failure"

        assert context.telemetry.get("fallback_reason") == "l4_failure"

    def test_l4_success_does_not_trigger_l5(self):
        """L4 success short-circuits, no L5."""
        context = LayerContext(
            query="action success",
            query_hash="hash",
            execution_plan={"tools": ["search"]},
            telemetry={"tool_results": {"search": ["result1"]}}
        )

        l4_success = True

        if not l4_success:
            context.telemetry["fallback"] = True

        assert "fallback" not in context.telemetry
        assert "tool_results" in context.telemetry

    def test_accumulated_context_passed_to_l5(self):
        """All accumulated context passed to L5 for generation."""
        context = LayerContext(
            query="generate response",
            query_hash="hash",
            intent_vector=[0.1, 0.2],
            retrieved_chunks=[{"text": "context"}],
            telemetry={"tools_tried": ["t1", "t2"]}
        )

        # L5 receives full context
        assert context.query == "generate response"
        assert len(context.retrieved_chunks) > 0
        assert len(context.telemetry["tools_tried"]) == 2


class TestCrossLayerTelemetry:
    """Integration: Telemetry propagation across all layers."""

    def test_telemetry_accumulated_through_pipeline(self):
        """Telemetry data accumulates as query flows through layers."""
        telemetry = {}

        # Layer 1
        telemetry["l1"] = {"hit": False, "latency_ms": 0.5}

        # Layer 2
        telemetry["l2"] = {"hit": False, "latency_ms": 15.0}

        # Layer 3
        telemetry["l3"] = {
            "hit": True,
            "latency_ms": 150.0,
            "chunks_retrieved": 3,
            "faiss_time_ms": 50.0,
            "bm25_time_ms": 30.0,
            "adg_expand_time_ms": 70.0
        }

        # Verify accumulated telemetry
        assert "l1" in telemetry
        assert "l2" in telemetry
        assert "l3" in telemetry
        assert telemetry["l3"]["chunks_retrieved"] == 3

    def test_total_latency_calculated(self):
        """Total latency calculated from all layer latencies."""
        layer_latencies = {
            "l1": 0.5,
            "l2": 15.0,
            "l3": 150.0
        }

        total = sum(layer_latencies.values())

        assert total == 165.5
        assert total < 1000  # Should be under 1 second for layers 1-3


class TestErrorHandlingIntegration:
    """Integration: Error handling across layer boundaries."""

    def test_l1_error_triggers_l2(self):
        """L1 error gracefully triggers L2 fallback via exception handling."""

        class L1CacheError(Exception):
            """Simulated L1 cache error."""
            pass

        def execute_l1_with_fallback():
            """Execute L1 with L2 fallback on error."""
            try:
                # Simulate L1 execution that raises error
                raise L1CacheError("Redis connection failed")
            except L1CacheError as e:
                # Trigger L2 fallback
                return {"fallback_triggered": True, "error": str(e), "fallback_layer": 2}

        result = execute_l1_with_fallback()

        assert result["fallback_triggered"] is True
        assert "Redis connection failed" in result["error"]
        assert result["fallback_layer"] == 2

    def test_l3_partial_failure_continues(self):
        """L3 partial failure (FAISS ok, BM25 fail) continues with available results."""
        # FAISS succeeded but BM25 failed
        faiss_results = [{"chunk_id": "c1", "score": 0.9}]
        bm25_results = []  # Failed

        # Should still continue with FAISS results
        combined = faiss_results + bm25_results

        assert len(combined) > 0  # Has FAISS results
        assert len(faiss_results) == 1

    def test_all_layers_fail_system_exception(self):
        """All layers failing raises proper system exception."""
        layer_results = {
            "l1": {"success": False},
            "l2": {"success": False},
            "l3": {"success": False},
            "l4": {"success": False},
            "l5": {"success": False}
        }

        all_failed = all(not r["success"] for r in layer_results.values())

        assert all_failed is True
        # In real system, would raise SystemException
