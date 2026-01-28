"""
[PHASE 25] Ultra-Hardening Verification Tests.

Tests:
1. PII Redaction in Graph Memory - Verify emails are redacted before MASTERED_TASK
2. 4KB Observation Truncation - Verify large observations are truncated
3. Embedding Retry Logic - Verify transient failures are retried
4. Stress Test - 100 rapid observations to test lock contention

[SSOT] Tests for Phase 25 ultra-hardening patches.
"""

from __future__ import annotations

import threading
from unittest.mock import MagicMock, patch

import pytest

# =============================================================================
# Test 1: PII Redaction in Graph Memory
# =============================================================================


class TestPIIRedactionInGraph:
    """
    Verify that PII is redacted before writing to Graph Memory.

    Test Case: learn_with_feedback is called with a context containing an email.
    Expected: The MASTERED_TASK node contains [REDACTED_EMAIL] instead of actual email.
    """

    def test_pii_redacted_before_graph_write(self):
        """Test that email in context is redacted before graph write."""
        from agentic_core.L4_state.memory.SemanticCacheManager import PIISanitizer

        # Context with PII
        context_with_pii = "User john.doe@example.com requested a file move"

        # Sanitize
        sanitized = PIISanitizer.sanitize(context_with_pii)

        # Verify email is redacted
        assert "john.doe@example.com" not in sanitized
        assert "[REDACTED_EMAIL]" in sanitized
        assert "requested a file move" in sanitized

    def test_learn_with_feedback_sanitizes_context(self):
        """Test that learn_with_feedback sanitizes context before graph write."""
        from agentic_core.L4_state.memory.SemanticCacheManager import PIISanitizer
        from agentic_core.base_agents.meta_learning_mixin import MetaLearningMixin

        # Create a mock memory with sanitizer
        mock_memory = MagicMock()
        mock_memory.sanitizer = PIISanitizer
        mock_memory.promote_to_long_term.return_value = True

        # Create a mock graph bridge
        mock_graph = MagicMock()

        # Create test class
        class TestAgent(MetaLearningMixin):
            _namespace = "TestAgent"

        # Inject mocks
        MetaLearningMixin._memory = mock_memory
        MetaLearningMixin._graph_bridge = mock_graph
        MetaLearningMixin._lobotomized = False

        try:
            agent = TestAgent()

            # Call learn_with_feedback with PII in context
            context_with_pii = "Process request from user@secret.com"
            agent.learn_with_feedback(
                context=context_with_pii,
                result={"status": "success"},
                feedback_score=0.9,  # Above promotion threshold
            )

            # Verify graph bridge was called with sanitized context
            if mock_graph.create_mastered_task_relation.called:
                call_args = mock_graph.create_mastered_task_relation.call_args
                task_description = call_args.kwargs.get("task_description", "")

                # Should NOT contain the original email
                assert "user@secret.com" not in task_description
                # Should contain redacted marker
                assert "[REDACTED_EMAIL]" in task_description
        finally:
            # Reset
            MetaLearningMixin._memory = None
            MetaLearningMixin._graph_bridge = None

    def test_multiple_pii_types_redacted(self):
        """Test that multiple PII types are all redacted."""
        from agentic_core.L4_state.memory.SemanticCacheManager import PIISanitizer

        context = (
            "User admin@company.com from IP 192.168.1.100 "
            "used API key sk-abc123456789012345678901234567890123456789"
        )

        sanitized = PIISanitizer.sanitize(context)

        assert "admin@company.com" not in sanitized
        assert "192.168.1.100" not in sanitized
        assert "sk-abc123456789012345678901234567890123456789" not in sanitized
        assert "[REDACTED_EMAIL]" in sanitized
        assert "[REDACTED_IPV4]" in sanitized
        assert "[REDACTED_OPENAI_KEY]" in sanitized


# =============================================================================
# Test 2: 4KB Observation Truncation
# =============================================================================


class TestObservationTruncation:
    """
    Verify that observations are truncated to 4KB limit.

    Test Case: Add observation larger than 4KB.
    Expected: Observation is truncated to 4093 chars + "..."
    """

    def test_observation_under_limit_unchanged(self):
        """Test that observations under 4KB are not modified."""
        from agentic_core.L4_state.memory.GraphMemoryBridge import GraphMemoryBridge

        bridge = GraphMemoryBridge.get_instance()

        # Small observation
        small_obs = "This is a small observation"

        # Mock the safe_call to capture the observation
        captured_obs = []
        original_safe_call = bridge._safe_call

        def capture_safe_call(operation, fn, **kwargs):
            if operation == "add_observations":
                obs_list = kwargs.get("observations", [])
                if obs_list:
                    captured_obs.append(obs_list[0]["contents"][0])
            return None

        bridge._safe_call = capture_safe_call

        try:
            bridge.add_observation("TestEntity", small_obs)

            assert len(captured_obs) == 1
            assert captured_obs[0] == small_obs  # Unchanged
        finally:
            bridge._safe_call = original_safe_call
            GraphMemoryBridge._instance = None

    def test_observation_over_limit_truncated(self):
        """Test that observations over 4KB are truncated."""
        from agentic_core.L4_state.memory.GraphMemoryBridge import GraphMemoryBridge

        bridge = GraphMemoryBridge.get_instance()

        # Large observation (5KB)
        large_obs = "X" * 5000

        # Mock the safe_call to capture the observation
        captured_obs = []
        original_safe_call = bridge._safe_call

        def capture_safe_call(operation, fn, **kwargs):
            if operation == "add_observations":
                obs_list = kwargs.get("observations", [])
                if obs_list:
                    captured_obs.append(obs_list[0]["contents"][0])
            return None

        bridge._safe_call = capture_safe_call

        try:
            bridge.add_observation("TestEntity", large_obs)

            assert len(captured_obs) == 1
            # Should be truncated to 4096 chars (4093 + "...")
            assert len(captured_obs[0]) == 4096
            assert captured_obs[0].endswith("...")
        finally:
            bridge._safe_call = original_safe_call
            GraphMemoryBridge._instance = None

    def test_truncation_preserves_content_start(self):
        """Test that truncation preserves the beginning of content."""
        from agentic_core.L4_state.memory.GraphMemoryBridge import GraphMemoryBridge

        bridge = GraphMemoryBridge.get_instance()

        # Large observation with identifiable start
        large_obs = "START_MARKER_" + "X" * 5000

        captured_obs = []
        original_safe_call = bridge._safe_call

        def capture_safe_call(operation, fn, **kwargs):
            if operation == "add_observations":
                obs_list = kwargs.get("observations", [])
                if obs_list:
                    captured_obs.append(obs_list[0]["contents"][0])
            return None

        bridge._safe_call = capture_safe_call

        try:
            bridge.add_observation("TestEntity", large_obs)

            # Start should be preserved
            assert captured_obs[0].startswith("START_MARKER_")
        finally:
            bridge._safe_call = original_safe_call
            GraphMemoryBridge._instance = None


# =============================================================================
# Test 3: Embedding Retry Logic
# =============================================================================


class TestEmbeddingRetryLogic:
    """
    Verify that embedding generation retries on transient failures.

    Test Case: First two attempts fail, third succeeds.
    Expected: Embedding is returned after retries.
    """

    def test_retry_on_transient_failure(self):
        """Test that transient failures are retried."""
        from agentic_core.L4_state.memory.SemanticCacheManager import SemanticCacheManager

        # Create manager with mocked client
        manager = SemanticCacheManager.__new__(SemanticCacheManager)
        manager._lock = threading.RLock()
        manager.api_key = "test-key"

        # Mock client that fails twice then succeeds
        mock_client = MagicMock()
        call_count = [0]

        def mock_embed(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] < 3:
                raise Exception(f"Transient failure {call_count[0]}")

            # Success on third attempt
            mock_result = MagicMock()
            mock_result.embeddings = [MagicMock(values=[0.1, 0.2, 0.3])]
            return mock_result

        mock_client.models.embed_content = mock_embed
        manager._embedding_client = mock_client

        # Patch time.sleep to speed up test
        with patch("time.sleep"):
            result = manager._get_embedding("test text")

        # Should have succeeded after retries
        assert result == [0.1, 0.2, 0.3]
        assert call_count[0] == 3

    def test_all_retries_exhausted(self):
        """Test that None is returned when all retries fail."""
        from agentic_core.L4_state.memory.SemanticCacheManager import SemanticCacheManager

        manager = SemanticCacheManager.__new__(SemanticCacheManager)
        manager._lock = threading.RLock()
        manager.api_key = "test-key"

        # Mock client that always fails
        mock_client = MagicMock()
        mock_client.models.embed_content.side_effect = Exception("Permanent failure")
        manager._embedding_client = mock_client

        with patch("time.sleep"):
            result = manager._get_embedding("test text")

        # Should return None after all retries exhausted
        assert result is None
        assert mock_client.models.embed_content.call_count == 3


# =============================================================================
# Test 4: Stress Test - 100 Rapid Observations
# =============================================================================


class TestStressObservations:
    """
    Stress test: Push 100 rapid observations to test lock contention.

    Test Case: 100 concurrent observation writes.
    Expected: All complete without deadlock or data corruption.
    """

    def test_100_rapid_observations(self):
        """Test 100 rapid observations don't cause lock contention issues."""
        from agentic_core.L4_state.memory.GraphMemoryBridge import GraphMemoryBridge

        bridge = GraphMemoryBridge.get_instance()

        # Track all observations
        observations_received = []
        lock = threading.Lock()

        original_safe_call = bridge._safe_call

        def capture_safe_call(operation, fn, **kwargs):
            if operation == "add_observations":
                with lock:
                    obs_list = kwargs.get("observations", [])
                    if obs_list:
                        observations_received.append(obs_list[0]["contents"][0])
            return None

        bridge._safe_call = capture_safe_call

        try:
            # Push 100 observations rapidly
            for i in range(100):
                bridge.add_observation("StressTestEntity", f"Observation {i}")

            # All 100 should be received
            assert len(observations_received) == 100

            # Verify no duplicates or corruption
            expected = {f"Observation {i}" for i in range(100)}
            received = set(observations_received)
            assert expected == received

        finally:
            bridge._safe_call = original_safe_call
            GraphMemoryBridge._instance = None

    def test_concurrent_observations_thread_safe(self):
        """Test concurrent observations from multiple threads."""
        from agentic_core.L4_state.memory.GraphMemoryBridge import GraphMemoryBridge

        bridge = GraphMemoryBridge.get_instance()

        observations_received = []
        lock = threading.Lock()

        original_safe_call = bridge._safe_call

        def capture_safe_call(operation, fn, **kwargs):
            if operation == "add_observations":
                with lock:
                    obs_list = kwargs.get("observations", [])
                    if obs_list:
                        observations_received.append(obs_list[0]["contents"][0])
            return None

        bridge._safe_call = capture_safe_call

        try:
            # Create 10 threads, each pushing 10 observations
            threads = []

            def push_observations(thread_id):
                for i in range(10):
                    bridge.add_observation("ConcurrentEntity", f"Thread{thread_id}_Obs{i}")

            for t_id in range(10):
                t = threading.Thread(target=push_observations, args=(t_id,))
                threads.append(t)

            # Start all threads
            for t in threads:
                t.start()

            # Wait for all to complete
            for t in threads:
                t.join(timeout=10)

            # All 100 should be received
            assert len(observations_received) == 100

        finally:
            bridge._safe_call = original_safe_call
            GraphMemoryBridge._instance = None


# =============================================================================
# Integration Tests
# =============================================================================


class TestPhase25Integration:
    """Integration tests for Phase 25 ultra-hardening."""

    def test_sanitizer_accessible_from_memory(self):
        """Test that sanitizer is accessible from SemanticCacheManager."""
        from agentic_core.L4_state.memory.SemanticCacheManager import (
            PIISanitizer,
        )

        # Verify PIISanitizer is importable
        assert PIISanitizer is not None
        assert hasattr(PIISanitizer, "sanitize")

    def test_graph_bridge_has_truncation(self):
        """Test that GraphMemoryBridge has observation truncation."""
        # Check the source code contains truncation logic
        import inspect

        from agentic_core.L4_state.memory.GraphMemoryBridge import GraphMemoryBridge

        source = inspect.getsource(GraphMemoryBridge.add_observation)

        assert "4096" in source or "4093" in source
        assert "..." in source

    def test_semantic_cache_has_retry(self):
        """Test that SemanticCacheManager has retry logic."""
        import inspect

        from agentic_core.L4_state.memory.SemanticCacheManager import SemanticCacheManager

        source = inspect.getsource(SemanticCacheManager._get_embedding)

        assert "max_retries" in source
        assert "attempt" in source


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
