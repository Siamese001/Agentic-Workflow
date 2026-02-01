"""
Integrated Test Suite: Phases 1-4 Sovereignty Infrastructure

Tests the complete integration of all Phase 1-4 components working together:
- Phase 1: Cost Guardrails, Token Monitoring, Context Standardization
- Phase 2: Tool Reliability, Distributed Tracing, Vector Memory
- Phase 3: HITL Integration, Approval Workflows, Human Escalation
- Phase 4: Architecture Refinement, Performance Tuning

These tests verify that all mixins work correctly when combined in the
InfrastructureMixin and that cross-cutting concerns are properly handled.
"""

from __future__ import annotations

import pytest
import time

from agentic_core.base_agents.infrastructure_mixin import InfrastructureMixin
from agentic_core.base_agents.cost_guardrail_mixin import (
    BudgetExceededError,
)
from agentic_core.base_agents.context_management_mixin import (
    ContextPriority,
)
from agentic_core.base_agents.hitl_mixin import (
    RiskLevel,
)
from agentic_core.base_agents.performance_mixin import PerformanceMixin
from agentic_core.base_agents.tracing_mixin import TracingMixin


# =============================================================================
# Test Fixtures
# =============================================================================


class IntegratedSovereignAgent(InfrastructureMixin):
    """
    Fully integrated agent with all Phase 1-4 capabilities.

    This agent demonstrates the complete sovereignty infrastructure
    working together in a realistic scenario.
    """

    def __init__(self):
        # Reset tracing circuit breaker for clean tests
        TracingMixin._circuit_breaker_open = False
        TracingMixin._circuit_breaker_failures = 0
        super().__init__()

        # Configure all phases
        self._configure_phases()

    def _configure_phases(self):
        """Configure all phase components."""
        # Phase 1: Cost Guardrails
        self.configure_budget(
            max_tokens_per_request=5000,
            max_tokens_per_session=50000,
            max_recursive_depth=5,
        )

        # Phase 1: Context Management
        self.configure_context(
            max_context_tokens=10000,
            target_context_tokens=8000,
        )

        # Phase 2: Tool Reliability
        self.configure_tool_retry("llm_call", max_retries=3, base_delay_seconds=0.01)
        self.configure_circuit_breaker("external_api", failure_threshold=3)

        # Phase 3: HITL
        self.configure_hitl(default_timeout_seconds=60.0)
        self.register_sensitive_operation("delete_files", RiskLevel.HIGH, "Delete repository files")
        self.register_sensitive_operation(
            "deploy_production", RiskLevel.CRITICAL, "Deploy to production"
        )

        # Phase 4: Performance
        self.configure_performance(
            cache_max_size=100,
            cache_default_ttl=60.0,
            batch_size=10,
        )

    @PerformanceMixin.cached(ttl=30)
    def cached_computation(self, key: str) -> str:
        """A cached computation method."""
        return f"computed_{key}_{time.time()}"

    @PerformanceMixin.timed
    def timed_operation(self, duration: float = 0.01) -> str:
        """A timed operation for metrics."""
        time.sleep(duration)
        return "completed"

    async def simulate_llm_call(self, prompt: str, fail_count: int = 0) -> dict:
        """Simulate an LLM call with optional failures."""
        call_state = {"attempts": 0}

        async def operation():
            call_state["attempts"] += 1
            if call_state["attempts"] <= fail_count:
                raise ConnectionError("Simulated LLM failure")
            return {
                "content": f"Response to: {prompt}",
                "usage": {"prompt_tokens": 100, "completion_tokens": 50},
            }

        return await self.with_retry("llm_call", operation)


@pytest.fixture
def integrated_agent():
    """Create a fresh integrated agent for each test."""
    return IntegratedSovereignAgent()


# =============================================================================
# Infrastructure Integration Tests
# =============================================================================


class TestInfrastructureIntegration:
    """Test that all infrastructure components initialize correctly."""

    def test_all_phases_initialized(self, integrated_agent):
        """Verify all phase components are initialized."""
        # Phase 1
        assert integrated_agent._cost_guardrail_initialized is True
        assert integrated_agent._context_management_initialized is True

        # Phase 2
        assert integrated_agent._tool_reliability_initialized is True
        assert hasattr(integrated_agent, "_tracing_service_name")

        # Phase 3
        assert integrated_agent._hitl_initialized is True

        # Phase 4
        assert integrated_agent._performance_initialized is True

    def test_infrastructure_status(self, integrated_agent):
        """Test getting infrastructure status."""
        status = integrated_agent.get_infrastructure_status()
        assert status["infra_initialized"] is True
        assert "class_name" in status

    def test_mro_order(self, integrated_agent):
        """Verify MRO includes all expected mixins."""
        mro_names = [cls.__name__ for cls in type(integrated_agent).__mro__]

        expected = [
            "IntegratedSovereignAgent",
            "InfrastructureMixin",
            "CostGuardrailMixin",
            "ContextManagementMixin",
            "ToolReliabilityMixin",
            "HITLMixin",
            "PerformanceMixin",
        ]

        for name in expected:
            assert name in mro_names, f"{name} not in MRO"


# =============================================================================
# Cross-Phase Integration Tests
# =============================================================================


class TestPhase1And2Integration:
    """Test integration between Phase 1 (Cost) and Phase 2 (Reliability)."""

    @pytest.mark.asyncio
    async def test_retry_with_cost_tracking(self, integrated_agent):
        """Test that retried operations track costs correctly."""
        # Simulate LLM call with 1 retry
        result = await integrated_agent.simulate_llm_call("test prompt", fail_count=1)

        # Record token usage
        integrated_agent.record_token_usage(
            result["usage"]["prompt_tokens"],
            result["usage"]["completion_tokens"],
            "gpt-4o",
        )

        # Verify cost tracking
        status = integrated_agent.get_budget_status()
        assert status["session_tokens"] == 150

    @pytest.mark.asyncio
    async def test_context_with_tracing(self, integrated_agent):
        """Test context management with distributed tracing."""
        with integrated_agent.start_span("context_operation"):
            integrated_agent.add_context("User query", ContextPriority.HIGH)
            integrated_agent.add_context("System response", ContextPriority.MEDIUM)

        # Verify both context and tracing worked
        context_status = integrated_agent.get_context_status()
        assert context_status["item_count"] == 2

        traces = integrated_agent.flush_traces()
        assert len(traces) >= 1


class TestPhase2And3Integration:
    """Test integration between Phase 2 (Reliability) and Phase 3 (HITL)."""

    def test_approval_with_tool_health(self, integrated_agent):
        """Test approval workflow with tool health tracking."""
        # Register a tool and record some failures
        integrated_agent.configure_tool_retry("risky_tool")
        integrated_agent._record_failure("risky_tool", ValueError("Error"))
        integrated_agent._record_failure("risky_tool", ValueError("Error"))

        # Create approval request with tool health context
        tool_health = integrated_agent.get_tool_health("risky_tool")
        request = integrated_agent.create_approval_request(
            "delete_files",
            context={"tool_health": tool_health},
        )

        # Verify context includes tool health
        assert "tool_health" in request.context
        assert request.context["tool_health"]["failed_calls"] == 2

    @pytest.mark.asyncio
    async def test_retry_respects_approval(self, integrated_agent):
        """Test that retry operations can be gated by approval."""
        # This demonstrates the pattern of checking approval before retry

        # Check if operation needs approval
        needs_approval = integrated_agent.check_approval_required("deploy_production")
        assert needs_approval is True

        # In real usage, you'd get approval first, then proceed with retry


class TestPhase3And4Integration:
    """Test integration between Phase 3 (HITL) and Phase 4 (Performance)."""

    def test_cached_approval_check(self, integrated_agent):
        """Test that approval checks can be cached."""
        # First check - should compute
        result1 = integrated_agent.check_approval_required("delete_files")

        # Cache the result manually (demonstrating the pattern)
        integrated_agent.cache_set("approval_check:delete_files", result1)

        # Second check - from cache
        hit, cached_result = integrated_agent.cache_get("approval_check:delete_files")
        assert hit is True
        assert cached_result == result1

    def test_approval_history_with_metrics(self, integrated_agent):
        """Test approval history with performance metrics."""
        # Create and approve a request
        request = integrated_agent.create_approval_request("delete_files")
        integrated_agent.approve(request.request_id, "admin", "Approved")

        # Get history
        history = integrated_agent.get_approval_history()
        assert len(history) == 1

        # Verify performance status
        perf_status = integrated_agent.get_performance_status()
        assert "cache" in perf_status


class TestPhase1And4Integration:
    """Test integration between Phase 1 (Cost) and Phase 4 (Performance)."""

    def test_cached_cost_estimation(self, integrated_agent):
        """Test caching cost estimations."""
        # First estimation
        cost1 = integrated_agent.estimate_cost(1000, 500, "gpt-4o")

        # Cache it
        integrated_agent.cache_set("cost:1000:500:gpt-4o", cost1)

        # Retrieve from cache
        hit, cached_cost = integrated_agent.cache_get("cost:1000:500:gpt-4o")
        assert hit is True
        assert cached_cost == cost1

    def test_context_with_performance_metrics(self, integrated_agent):
        """Test context operations with performance tracking."""
        # Add context items
        for i in range(5):
            integrated_agent.add_context(f"Content {i}", ContextPriority.MEDIUM)

        # Get context status
        context_status = integrated_agent.get_context_status()
        assert context_status["item_count"] == 5

        # Verify performance tracking is available
        perf_status = integrated_agent.get_performance_status()
        assert perf_status["config"]["cache_enabled"] is True


# =============================================================================
# Full Workflow Integration Tests
# =============================================================================


class TestFullWorkflowIntegration:
    """Test complete workflows using all phases together."""

    @pytest.mark.asyncio
    async def test_complete_llm_workflow(self, integrated_agent):
        """Test a complete LLM workflow with all phases."""
        # Phase 4: Start performance tracking
        with integrated_agent.start_span("complete_workflow"):
            # Phase 1: Add context
            integrated_agent.add_context(
                "System: You are a helpful assistant",
                ContextPriority.CRITICAL,
            )
            integrated_agent.add_context(
                "User: Hello, how are you?",
                ContextPriority.HIGH,
            )

            # Phase 2: Make LLM call with retry
            result = await integrated_agent.simulate_llm_call("Hello")

            # Phase 1: Track costs
            integrated_agent.record_token_usage(100, 50, "gpt-4o")

            # Phase 1: Add response to context
            integrated_agent.add_context(
                result["content"],
                ContextPriority.MEDIUM,
            )

        # Verify all phases worked
        context_status = integrated_agent.get_context_status()
        assert context_status["item_count"] == 3

        budget_status = integrated_agent.get_budget_status()
        assert budget_status["session_tokens"] == 150

        traces = integrated_agent.flush_traces()
        assert len(traces) >= 1

    @pytest.mark.asyncio
    async def test_high_risk_operation_workflow(self, integrated_agent):
        """Test a high-risk operation workflow with approval."""
        # Phase 2: Start tracing
        with integrated_agent.start_span("high_risk_workflow"):
            # Phase 3: Check if approval needed
            needs_approval = integrated_agent.check_approval_required("delete_files")
            assert needs_approval is True

            # Phase 3: Create approval request
            request = integrated_agent.create_approval_request(
                "delete_files",
                context={"files": ["test.py"], "reason": "cleanup"},
            )

            # Phase 3: Approve (simulating human approval)
            integrated_agent.approve(request.request_id, "admin", "Approved for cleanup")

            # Phase 4: Cache the approval result
            integrated_agent.cache_set(
                f"approved:{request.request_id}",
                True,
                ttl=300,
            )

        # Verify workflow completed
        history = integrated_agent.get_approval_history()
        assert len(history) == 1
        assert history[0]["status"] == "approved"

    def test_batch_processing_workflow(self, integrated_agent):
        """Test batch processing with all phases."""
        # Phase 4: Add items to batch
        for i in range(15):
            integrated_agent.batch_add("process_queue", f"item_{i}")

            # Phase 4: Check if should flush
            if integrated_agent.should_flush_batch("process_queue"):
                items = integrated_agent.batch_flush("process_queue")

                # Phase 1: Track processing cost
                integrated_agent.record_token_usage(len(items) * 10, len(items) * 5, "gpt-4o")

        # Flush remaining
        integrated_agent.batch_flush("process_queue")

        # Verify
        budget_status = integrated_agent.get_budget_status()
        assert budget_status["session_tokens"] > 0


# =============================================================================
# Error Handling Integration Tests
# =============================================================================


class TestErrorHandlingIntegration:
    """Test error handling across phases."""

    def test_budget_exceeded_with_tracing(self, integrated_agent):
        """Test budget exceeded error is traced."""
        integrated_agent.configure_budget(max_tokens_per_request=100)

        with integrated_agent.start_span("budget_test"):
            with pytest.raises(BudgetExceededError):
                integrated_agent.record_token_usage(100, 50, "gpt-4o")

        # Verify span captured error
        traces = integrated_agent.flush_traces()
        assert len(traces) >= 1

    @pytest.mark.asyncio
    async def test_retry_exhausted_with_fallback(self, integrated_agent):
        """Test retry exhaustion with fallback and tracing."""
        integrated_agent.configure_tool_retry(
            "failing_tool", max_retries=2, base_delay_seconds=0.01
        )

        async def failing_operation():
            raise ValueError("Always fails")

        def fallback():
            return "fallback_result"

        with integrated_agent.start_span("retry_test"):
            result = await integrated_agent.with_retry(
                "failing_tool",
                failing_operation,
                fallback=fallback,
            )

        assert result == "fallback_result"

        # Verify tool health recorded failures
        health = integrated_agent.get_tool_health("failing_tool")
        assert health["failed_calls"] == 3  # Initial + 2 retries

    def test_approval_rejection_handling(self, integrated_agent):
        """Test handling of rejected approvals."""
        request = integrated_agent.create_approval_request("delete_files")
        integrated_agent.reject(request.request_id, "admin", "Too risky")

        history = integrated_agent.get_approval_history()
        assert history[0]["status"] == "rejected"
        assert history[0]["resolution_notes"] == "Too risky"


# =============================================================================
# Status and Monitoring Integration Tests
# =============================================================================


class TestStatusMonitoringIntegration:
    """Test status and monitoring across all phases."""

    def test_comprehensive_status(self, integrated_agent):
        """Test getting comprehensive status from all phases."""
        # Do some operations
        integrated_agent.add_context("Test", ContextPriority.MEDIUM)
        integrated_agent.record_token_usage(100, 50, "gpt-4o")
        integrated_agent.cache_set("key", "value")
        integrated_agent.timed_operation()

        # Get all statuses
        budget_status = integrated_agent.get_budget_status()
        context_status = integrated_agent.get_context_status()
        hitl_status = integrated_agent.get_hitl_status()
        perf_status = integrated_agent.get_performance_status()
        tracing_status = integrated_agent.get_tracing_status()

        # Verify all return valid data
        assert budget_status["session_tokens"] == 150
        assert context_status["item_count"] == 1
        assert hitl_status["enabled"] is True
        assert perf_status["cache"]["size"] == 1
        assert "service_name" in tracing_status

    def test_reset_all_states(self, integrated_agent):
        """Test resetting states across phases."""
        # Add some state
        integrated_agent.record_token_usage(100, 50, "gpt-4o")
        integrated_agent.add_context("Test", ContextPriority.MEDIUM)
        integrated_agent.cache_set("key", "value")

        # Reset
        integrated_agent.reset_session()
        integrated_agent.clear_context(preserve_critical=False)
        integrated_agent.cache_clear()
        integrated_agent.reset_metrics()

        # Verify reset
        assert integrated_agent.get_budget_status()["session_tokens"] == 0
        assert integrated_agent.get_context_status()["item_count"] == 0
        assert integrated_agent.cache_stats()["size"] == 0


# =============================================================================
# Thread Safety Integration Tests
# =============================================================================


class TestThreadSafetyIntegration:
    """Test thread safety across all phases."""

    def test_concurrent_operations(self, integrated_agent):
        """Test concurrent operations across phases."""
        import threading

        errors = []
        operations_completed = {"count": 0}

        def worker():
            try:
                for i in range(10):
                    # Phase 1
                    integrated_agent.add_context(f"Content {i}", ContextPriority.LOW)

                    # Phase 4
                    integrated_agent.cache_set(f"key_{i}", f"value_{i}")

                    # Phase 2
                    integrated_agent._record_success("test_tool")

                operations_completed["count"] += 1
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert operations_completed["count"] == 5


# =============================================================================
# Performance Benchmark Tests
# =============================================================================


class TestPerformanceBenchmarks:
    """Test performance characteristics of integrated system."""

    def test_cache_improves_performance(self, integrated_agent):
        """Test that caching improves performance."""
        # First call - uncached
        start = time.time()
        result1 = integrated_agent.cached_computation("test_key")
        uncached_time = time.time() - start

        # Second call - cached
        start = time.time()
        result2 = integrated_agent.cached_computation("test_key")
        cached_time = time.time() - start

        # Results should be same (cached)
        assert result1 == result2

        # Cached should be faster (or at least not slower)
        # Note: In practice, cached is much faster
        assert cached_time <= uncached_time + 0.01

    def test_metrics_overhead_minimal(self, integrated_agent):
        """Test that metrics collection has minimal overhead."""
        # Run timed operation
        integrated_agent.timed_operation(0.01)

        metrics = integrated_agent.get_performance_metrics("timed_operation")

        # Overhead should be minimal (less than 10ms on Windows)
        # Windows has lower timer resolution, so we allow more variance
        overhead = metrics["total_time_ms"] - 10  # Expected ~10ms
        assert overhead < 10, f"Metrics overhead too high: {overhead}ms"
