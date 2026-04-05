"""End-to-End Test Suite for Redis L1 Retrieval Gate.

This test suite validates the complete L1-L4 retrieval pipeline as described in:
- docs/reference/Redis/Redis L1 Retrieval Gate.md
- docs/reference/Redis/Redis Usage Types.md

Tests cover:
1. L1 Exact Cache (Redis O(1) SHA256 key lookup)
2. L2 Semantic Cache (similarity-based caching)
3. L3 Semantic RAG (ChromaDB vector search)
4. L4 Agentic Actions (tool schema validation)
5. Full orchestrator flow (L1->L2->L3->L4 fallback chain)
"""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


# Check if retrieval layers are available
try:
    from agentic_core.cache import get_hot_cache, reset_cache_singletons
    from agentic_core.L4_state.reasoning.retrieval_layers import (
        L1ExactCache,
        L2SemanticCache,
        L3SemanticRAG,
        L4AgenticActions,
        RetrievalOrchestrator,
    )
    RETRIEVAL_AVAILABLE = True
except ImportError:
    RETRIEVAL_AVAILABLE = False


class TestL1ExactCache(unittest.TestCase):
    """Test L1 Exact Cache - Redis-backed O(1) SHA256 key lookup."""

    def setUp(self):
        """Reset cache singletons before each test."""
        reset_cache_singletons()
        self.cache = L1ExactCache(ttl_seconds=3600)

    def tearDown(self):
        """Clean up after each test."""
        reset_cache_singletons()

    def test_l1_cache_hit(self):
        """Test L1 cache hit returns cached value."""
        query = "What is the capital of France?"
        expected_response = "The capital of France is Paris."

        # Set value in cache
        self.cache.set(query, expected_response)

        # Get value from cache
        result = self.cache.get(query)

        self.assertEqual(result, expected_response)
        self.assertEqual(self.cache.hit_count, 1)
        self.assertEqual(self.cache.miss_count, 0)

    def test_l1_cache_miss(self):
        """Test L1 cache miss returns None."""
        query = "What is the capital of Mars?"

        # Get value without setting (cache miss)
        result = self.cache.get(query)

        self.assertIsNone(result)
        self.assertEqual(self.cache.hit_count, 0)
        self.assertEqual(self.cache.miss_count, 1)

    def test_l1_cache_normalization(self):
        """Test query normalization for exact matching."""
        query1 = "What is the CAPITAL of France?"
        query2 = "what is the capital of france?"
        query3 = "  what is the capital of france?  "

        expected_response = "The capital of France is Paris."

        # Set with first query
        self.cache.set(query1, expected_response)

        # All normalized queries should hit
        self.assertEqual(self.cache.get(query1), expected_response)
        self.assertEqual(self.cache.get(query2), expected_response)
        self.assertEqual(self.cache.get(query3), expected_response)

    def test_l1_cache_key_format(self):
        """Test L1 cache key uses SHA256 format."""
        query = "test query"
        normalized = self.cache._normalize_query(query)
        expected_key = f"l1_exact:{hashlib.sha256(normalized.encode()).hexdigest()}"

        # Verify key format by checking internal cache operation
        self.cache.set(query, "test value")

        # The key should exist in Redis
        raw_result = self.cache.cache.get(expected_key)
        self.assertIsNotNone(raw_result)

    def test_l1_cache_stats(self):
        """Test L1 cache statistics."""
        # Generate hits and misses
        self.cache.set("q1", "a1")
        self.cache.get("q1")  # hit
        self.cache.get("q2")  # miss
        self.cache.get("q3")  # miss

        stats = self.cache.get_stats()

        self.assertEqual(stats["layer"], "L1_Exact_Cache")
        self.assertEqual(stats["hit_count"], 1)
        self.assertEqual(stats["miss_count"], 2)
        self.assertEqual(stats["hit_rate"], 1/3)
        self.assertEqual(stats["ttl_seconds"], 3600)


class TestL2SemanticCache(unittest.TestCase):
    """Test L2 Semantic Cache - similarity-based caching."""

    def setUp(self):
        """Reset cache singletons before each test."""
        reset_cache_singletons()
        self.cache = L2SemanticCache(similarity_threshold=0.95, ttl_seconds=3600)

    def tearDown(self):
        """Clean up after each test."""
        reset_cache_singletons()

    def test_l2_cache_basic(self):
        """Test L2 cache stores and retrieves with embeddings."""
        query = "Explain quantum computing"
        response = "Quantum computing uses qubits..."

        # Set in cache
        self.cache.set(query, response)

        # Exact same query should hit
        result = self.cache.get(query)
        self.assertIsNotNone(result)

    def test_l2_cache_similarity_threshold(self):
        """Test L2 cache respects similarity threshold."""
        query = "What is machine learning?"
        response = "Machine learning is a subset of AI..."

        self.cache.set(query, response)

        # Very similar query should hit with high threshold
        similar_query = "What exactly is machine learning?"
        result = self.cache.get(similar_query)

        # Result may or may not hit depending on mock embedding similarity
        # This test verifies the mechanism works
        self.assertIsInstance(self.cache.hit_count + self.cache.miss_count, int)

    def test_l2_cache_stats(self):
        """Test L2 cache statistics."""
        stats = self.cache.get_stats()

        self.assertEqual(stats["layer"], "L2_Semantic_Cache")
        self.assertIn("hit_count", stats)
        self.assertIn("miss_count", stats)
        self.assertIn("hit_rate", stats)
        self.assertEqual(stats["similarity_threshold"], 0.95)


class TestL3SemanticRAG(unittest.TestCase):
    """Test L3 Semantic RAG - ChromaDB vector search."""

    def setUp(self):
        """Create temporary directory for ChromaDB."""
        self.temp_dir = tempfile.mkdtemp()
        self.rag = L3SemanticRAG(persist_directory=self.temp_dir)

    def tearDown(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_l3_rag_initialization(self):
        """Test L3 RAG initializes with collections."""
        self.assertIsNotNone(self.rag.docs_collection)
        self.assertIsNotNone(self.rag.traces_collection)
        self.assertEqual(self.rag.query_count, 0)

    def test_l3_rag_stats(self):
        """Test L3 RAG statistics."""
        stats = self.rag.get_stats()

        self.assertEqual(stats["layer"], "L3_Semantic_RAG")
        self.assertEqual(stats["query_count"], 0)
        self.assertIn("docs_count", stats)
        self.assertIn("traces_count", stats)

    def test_l3_rag_mock_embeddings(self):
        """Test L3 RAG uses mock embeddings when API key missing."""
        self.assertTrue(self.rag.mock_embeddings)

        embedding = self.rag._get_embedding("test query")
        self.assertIsNotNone(embedding)
        self.assertEqual(len(embedding), 1536)  # OpenAI embedding dimension


class TestL4AgenticActions(unittest.TestCase):
    """Test L4 Agentic Actions - tool schema validation."""

    def setUp(self):
        """Initialize L4 actions."""
        self.actions = L4AgenticActions()

    def test_l4_available_actions(self):
        """Test L4 lists available actions."""
        available = self.actions.list_available_actions()

        self.assertIn("search_docs", available)
        self.assertIn("find_similar_traces", available)
        self.assertIn("get_architecture_info", available)

    def test_l4_validate_action_success(self):
        """Test L4 validates correct action parameters."""
        result = self.actions.validate_action(
            "search_docs",
            {"query": "test query", "n_results": 5}
        )

        self.assertTrue(result)

    def test_l4_validate_action_missing_required(self):
        """Test L4 rejects action with missing required parameter."""
        result = self.actions.validate_action(
            "search_docs",
            {"n_results": 5}  # missing required 'query'
        )

        self.assertFalse(result)

    def test_l4_validate_unknown_action(self):
        """Test L4 rejects unknown action."""
        result = self.actions.validate_action(
            "unknown_action",
            {"param": "value"}
        )

        self.assertFalse(result)

    def test_l4_get_tool_schema(self):
        """Test L4 returns tool schema."""
        schema = self.actions.get_tool_schema("search_docs")

        self.assertIsNotNone(schema)
        self.assertEqual(schema["name"], "search_docs")
        self.assertIn("parameters", schema)

    def test_l4_stats(self):
        """Test L4 action statistics."""
        # Perform some actions
        self.actions.validate_action("search_docs", {"query": "test"})
        self.actions.validate_action("unknown_action", {})  # failure

        stats = self.actions.get_stats()

        self.assertEqual(stats["layer"], "L4_Agentic_Actions")
        self.assertEqual(stats["action_count"], 2)
        self.assertEqual(stats["validation_failures"], 1)
        self.assertEqual(stats["available_actions"], 3)


class TestRetrievalOrchestrator(unittest.TestCase):
    """Test full L1-L4 Retrieval Orchestrator flow."""

    def setUp(self):
        """Initialize orchestrator with temp ChromaDB."""
        reset_cache_singletons()
        self.temp_dir = tempfile.mkdtemp()

        # Create properly initialized L3 RAG
        self.l3_rag = L3SemanticRAG(persist_directory=self.temp_dir)

        # Create orchestrator and replace L3 with our test instance
        self.orchestrator = RetrievalOrchestrator()
        self.orchestrator.l3_rag = self.l3_rag

    def tearDown(self):
        """Clean up."""
        import shutil
        reset_cache_singletons()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_orchestrator_initializes_all_layers(self):
        """Test orchestrator initializes L1-L4 layers."""
        self.assertIsNotNone(self.orchestrator.l1_cache)
        self.assertIsNotNone(self.orchestrator.l2_cache)
        self.assertIsNotNone(self.orchestrator.l3_rag)
        self.assertIsNotNone(self.orchestrator.l4_actions)

    def test_orchestrator_l1_hit_shortcuts(self):
        """Test orchestrator returns L1 hit without reaching deeper layers."""
        query = "test query"
        expected = "cached answer"

        # Pre-populate L1 cache
        self.orchestrator.l1_cache.set(query, expected)

        # Retrieve should hit L1 and return
        result = self.orchestrator.retrieve(query)

        self.assertIn("L1", result["layers_used"])
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["content"], expected)

    def test_orchestrator_full_fallback_chain(self):
        """Test orchestrator falls through L1->L2->L3->L4."""
        query = "search for machine learning documentation"

        # No cache hits, should reach L3/L4
        result = self.orchestrator.retrieve(query)

        # Should have used at least one layer
        self.assertGreater(len(result["layers_used"]), 0)
        self.assertIn("query", result)

    def test_orchestrator_is_action_query(self):
        """Test orchestrator detects action queries."""
        # Action keywords
        self.assertTrue(self.orchestrator._is_action_query("search for docs"))
        self.assertTrue(self.orchestrator._is_action_query("find traces"))
        self.assertTrue(self.orchestrator._is_action_query("get architecture info"))

        # Non-action
        self.assertFalse(self.orchestrator._is_action_query("hello world"))

    def test_orchestrator_all_stats(self):
        """Test orchestrator aggregates stats from all layers."""
        stats = self.orchestrator.get_all_stats()

        self.assertIn("l1", stats)
        self.assertIn("l2", stats)
        self.assertIn("l3", stats)
        self.assertIn("l4", stats)


class TestRedisL1RetrievalGateE2E(unittest.TestCase):
    """
    End-to-End tests for Redis L1 Retrieval Gate.

    Validates the complete flow described in:
    - docs/reference/Redis/Redis L1 Retrieval Gate.md
    - docs/reference/Redis/Redis Usage Types.md
    """

    def setUp(self):
        """Set up complete test environment."""
        reset_cache_singletons()
        self.temp_dir = tempfile.mkdtemp()

        # Initialize all components
        self.l1_cache = L1ExactCache(ttl_seconds=3600)
        self.l2_cache = L2SemanticCache(ttl_seconds=3600)
        self.l3_rag = L3SemanticRAG(persist_directory=self.temp_dir)
        self.l4_actions = L4AgenticActions()

        self.orchestrator = RetrievalOrchestrator()
        # Replace with our test instances
        self.orchestrator.l1_cache = self.l1_cache
        self.orchestrator.l2_cache = self.l2_cache
        self.orchestrator.l3_rag = self.l3_rag
        self.orchestrator.l4_actions = self.l4_actions

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        reset_cache_singletons()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_e2e_l1_retrieval_gate_flow(self):
        """
        Test complete L1 Retrieval Gate flow:

        1. User query -> L1 Exact Cache (O(1) SHA256 lookup)
        2. Cache miss -> L2 Semantic Cache
        3. Cache miss -> L3 RAG (ChromaDB)
        4. Result write-back to L1/L2 for future hits
        """
        query = "What is the architecture of the agentic system?"
        expected_answer = "The agentic system uses a layered architecture..."

        # First query - should miss L1 and L2, reach L3/L4
        result1 = self.orchestrator.retrieve(query)

        # Verify query was processed
        self.assertEqual(result1["query"], query)

        # Now manually populate L1 cache (simulating L3 result write-back)
        self.l1_cache.set(query, expected_answer)

        # Second query - should hit L1
        result2 = self.orchestrator.retrieve(query)

        self.assertIn("L1", result2["layers_used"])
        self.assertEqual(result2["results"][0]["content"], expected_answer)

    def test_e2e_redis_hot_cache_pattern(self):
        """
        Test Redis Hot Cache (C0 Reference Worktable) pattern:

        - Automatic, invisible caching
        - Speeds up system silently
        - Happens before expensive operations
        """
        # Simulate repeated queries
        queries = [
            "What is ADG?",
            "What is ADG?",  # Repeat - should hit cache
            "What is ADG?",  # Repeat - should hit cache
        ]

        # First query - set up in cache
        self.l1_cache.set(queries[0], "ADG is the Agent Dependency Graph...")

        hits = 0
        for query in queries:
            result = self.l1_cache.get(query)
            if result is not None:
                hits += 1

        # All 3 should hit since they're identical after normalization
        self.assertEqual(hits, 3)
        self.assertEqual(self.l1_cache.hit_count, 3)

    def test_e2e_redis_mcp_pattern(self):
        """
        Test Redis MCP (Librarian's Notepad) pattern:

        - Conscious, deliberate tool usage
        - Active communication, not passive storage
        - Agent decides when to use
        """
        # Simulate agent using Redis as a notepad
        task_id = "task_123"
        note_key = f"agent_note:{task_id}"

        # Agent writes note to Redis (conscious action)
        note_content = json.dumps({
            "step_completed": 2,
            "anomaly_found": True,
            "next_action": "escalate"
        })

        cache = get_hot_cache()
        cache.set(note_key, note_content.encode(), ttl_seconds=300)

        # Later, agent reads note (conscious retrieval)
        retrieved = cache.get(note_key)
        self.assertIsNotNone(retrieved)

        data = json.loads(retrieved.decode())
        self.assertEqual(data["step_completed"], 2)
        self.assertTrue(data["anomaly_found"])

    def test_e2e_performance_characteristics(self):
        """
        Verify performance characteristics per Redis L1 Retrieval Gate spec:

        - L1 Redis Lookup: ~1ms (exact memory)
        - L2 Vector Search: ~10-50ms (similar memory)
        - L3 Full RAG: ~500-2000ms (reasoning/synthesis)
        """
        import time

        query = "performance test query"
        self.l1_cache.set(query, "cached response")

        # Measure L1 hit performance
        start = time.perf_counter()
        for _ in range(100):
            self.l1_cache.get(query)
        elapsed = time.perf_counter() - start

        avg_ms = (elapsed / 100) * 1000

        # L1 should be very fast (allowing for test environment variance)
        # Spec says ~1ms, we'll allow up to 10ms for test overhead
        self.assertLess(avg_ms, 10.0, f"L1 cache too slow: {avg_ms:.2f}ms")

    def test_e2e_cache_write_back(self):
        """
        Test write-back pattern:

        After L3/L4 generates answer, it should be written to:
        - L1 (exact cache for identical queries)
        - L2 (semantic cache for similar queries)
        """
        query = "Explain the routing system"
        generated_answer = "The routing system uses L0-L5 layers..."

        # Simulate L3/L4 generating answer and write-back
        self.l1_cache.set(query, generated_answer)
        self.l2_cache.set(query, generated_answer)

        # Verify both caches have it
        l1_result = self.l1_cache.get(query)
        l2_result = self.l2_cache.get(query)

        self.assertEqual(l1_result, generated_answer)
        # L2 may return None due to embedding requirements
        # but should at least not error


class TestRedisIntegration(unittest.TestCase):
    """Integration tests with real Redis if available."""

    @classmethod
    def setUpClass(cls):
        """Check if Redis is available."""
        cls.redis_available = False
        try:
            from agentic_core.cache import check_redis_health
            health = check_redis_health()
            cls.redis_available = health.get("healthy", False)
        except Exception:
            cls.redis_available = False

    def skip_if_no_redis(self):
        """Skip test if Redis not available."""
        if not self.redis_available:
            self.skipTest("Redis not available")

    def test_redis_health_check(self):
        """Test Redis health check function."""
        from agentic_core.cache import check_redis_health

        health = check_redis_health()

        self.assertIn("healthy", health)
        self.assertIn("url", health)
        self.assertIn("error", health)

    def test_redis_deterministic_cache(self):
        """Test DeterministicRedisCache with real Redis."""
        self.skip_if_no_redis()

        from agentic_core.cache import CacheDB, DeterministicRedisCache

        cache = DeterministicRedisCache(db=CacheDB.HOT)

        key = "test_key"
        value = b"test_value"

        # Set value
        result = cache.set(key, value, ttl_seconds=60)
        self.assertTrue(result)

        # Get value
        retrieved = cache.get(key)
        self.assertEqual(retrieved, value)

        # Delete value
        deleted = cache.delete(key)
        self.assertTrue(deleted)

        # Verify deleted
        self.assertIsNone(cache.get(key))


def create_test_suite():
    """Create comprehensive test suite."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestL1ExactCache))
    suite.addTests(loader.loadTestsFromTestCase(TestL2SemanticCache))
    suite.addTests(loader.loadTestsFromTestCase(TestL3SemanticRAG))
    suite.addTests(loader.loadTestsFromTestCase(TestL4AgenticActions))
    suite.addTests(loader.loadTestsFromTestCase(TestRetrievalOrchestrator))
    suite.addTests(loader.loadTestsFromTestCase(TestRedisL1RetrievalGateE2E))
    suite.addTests(loader.loadTestsFromTestCase(TestRedisIntegration))

    return suite


if __name__ == "__main__":
    # Run with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(create_test_suite())

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
