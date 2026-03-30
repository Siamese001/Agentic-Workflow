"""Test AppsTracingMixin gap fixes - G3 and G5.

Validates:
- G3: get_tracing_status() returns expected keys
- G5: AppsTracingMixin handles initialization failures gracefully
"""

import pytest
from unittest.mock import patch, MagicMock


try:
    from apps_shared.mixins.apps_tracing_mixin import AppsTracingMixin, OTEL_AVAILABLE, AGENTIC_CORE_AVAILABLE
    APPS_TRACING_AVAILABLE = True
except ImportError:
    APPS_TRACING_AVAILABLE = False


class TestTracingMixinGaps:
    """Gap fixes validation tests."""

    def test_get_tracing_status_returns_expected_keys(self):
        """G3 FIX: get_tracing_status() returns all expected keys."""
        if not APPS_TRACING_AVAILABLE:
            pytest.skip("AppsTracingMixin not available")
        
        class TestAgent(AppsTracingMixin):
            def __init__(self):
                super().__init__()
        
        agent = TestAgent()
        status = agent.get_tracing_status()
        
        # Verify all expected keys are present
        expected_keys = [
            "service_name",
            "otel_available",
            "agentic_core_available",
            "lifecycle_available",
            "tracing_enabled",
            "tracer_initialized",
        ]
        for key in expected_keys:
            assert key in status, f"Missing key: {key}"
        
        # Verify types
        assert isinstance(status["service_name"], str)
        assert isinstance(status["otel_available"], bool)
        assert isinstance(status["agentic_core_available"], bool)
        assert isinstance(status["lifecycle_available"], bool)
        assert isinstance(status["tracing_enabled"], bool)
        assert isinstance(status["tracer_initialized"], bool)
        
        # Verify service_name is set (will be class name or unknown_agent)
        assert status["service_name"] in ["TestAgent", "unknown_agent"]

    def test_tracing_status_values_consistent(self):
        """G3: Tracing status values are internally consistent."""
        if not APPS_TRACING_AVAILABLE:
            pytest.skip("AppsTracingMixin not available")
        
        class TestAgent(AppsTracingMixin):
            def __init__(self):
                super().__init__()
        
        agent = TestAgent()
        status = agent.get_tracing_status()
        
        # If OTel not available, tracing should be disabled
        if not status["otel_available"]:
            assert status["tracing_enabled"] is False
            assert status["tracer_initialized"] is False

    def test_tracing_disabled_when_otel_unavailable(self):
        """G5 FIX: Tracing gracefully disabled when OTel unavailable."""
        if not APPS_TRACING_AVAILABLE:
            pytest.skip("AppsTracingMixin not available")
        
        # Mock OTEL_AVAILABLE as False
        with patch("apps_shared.mixins.apps_tracing_mixin.OTEL_AVAILABLE", False):
            class TestAgent(AppsTracingMixin):
                def __init__(self):
                    super().__init__()
            
            agent = TestAgent()
            status = agent.get_tracing_status()
            
            assert status["otel_available"] is False
            assert status["tracing_enabled"] is False
            assert status["tracer_initialized"] is False

    def test_tracer_initialization_failure_handled(self):
        """G5 FIX: Tracer initialization failure is handled gracefully."""
        if not APPS_TRACING_AVAILABLE:
            pytest.skip("AppsTracingMixin not available")
        
        # Mock get_tracer to raise exception
        with patch("apps_shared.mixins.apps_tracing_mixin.trace.get_tracer", side_effect=ImportError("No OTel")):
            class TestAgent(AppsTracingMixin):
                def __init__(self):
                    super().__init__()
            
            # Should not raise exception
            agent = TestAgent()
            status = agent.get_tracing_status()
            
            # Tracing should be disabled after failure
            assert status["tracing_enabled"] is False

    def test_span_creation_without_otel(self):
        """G5: Span creation works without OTel using fallback context."""
        if not APPS_TRACING_AVAILABLE:
            pytest.skip("AppsTracingMixin not available")
        
        with patch("apps_shared.mixins.apps_tracing_mixin.OTEL_AVAILABLE", False):
            class TestAgent(AppsTracingMixin):
                def __init__(self):
                    super().__init__()
                
                def do_work(self):
                    with self.start_agent_span("test_operation", {"key": "value"}) as ctx:
                        return ctx
            
            agent = TestAgent()
            ctx = agent.do_work()
            
            # Should return fallback context
            assert ctx is not None
            # Context is a SpanContext object, check attributes directly
            assert hasattr(ctx, 'operation_name') or isinstance(ctx, dict)
            if isinstance(ctx, dict):
                assert ctx["operation_name"] == "test_operation"

    def test_validation_span_without_tracing(self):
        """G5: Validation span works when tracing unavailable."""
        if not APPS_TRACING_AVAILABLE:
            pytest.skip("AppsTracingMixin not available")
        
        with patch("apps_shared.mixins.apps_tracing_mixin.OTEL_AVAILABLE", False):
            class TestAgent(AppsTracingMixin):
                def __init__(self):
                    super().__init__()
                
                def validate(self):
                    with self.start_validation_span("safety", {"content": "test"}) as ctx:
                        return ctx
            
            agent = TestAgent()
            ctx = agent.validate()
            
            # Should return context without raising
            assert ctx is not None

    def test_reasoning_span_without_tracing(self):
        """G5: Reasoning span works when tracing unavailable."""
        if not APPS_TRACING_AVAILABLE:
            pytest.skip("AppsTracingMixin not available")
        
        with patch("apps_shared.mixins.apps_tracing_mixin.OTEL_AVAILABLE", False):
            class TestAgent(AppsTracingMixin):
                def __init__(self):
                    super().__init__()
                
                def reason(self):
                    with self.start_reasoning_span("planning") as ctx:
                        return ctx
            
            agent = TestAgent()
            ctx = agent.reason()
            
            # Should return context without raising
            assert ctx is not None

    def test_tool_span_without_tracing(self):
        """G5: Tool span works when tracing unavailable."""
        if not APPS_TRACING_AVAILABLE:
            pytest.skip("AppsTracingMixin not available")
        
        with patch("apps_shared.mixins.apps_tracing_mixin.OTEL_AVAILABLE", False):
            class TestAgent(AppsTracingMixin):
                def __init__(self):
                    super().__init__()
                
                def call_tool(self):
                    with self.start_tool_span("search", {"query": "test"}) as ctx:
                        return ctx
            
            agent = TestAgent()
            ctx = agent.call_tool()
            
            # Should return context without raising
            assert ctx is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
