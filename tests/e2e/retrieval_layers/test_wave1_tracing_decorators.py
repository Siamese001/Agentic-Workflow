"""Wave 1: Trace Semantics and IDs — Verification Tests.

Tests for tracing decorators (@trace_cognitive, @trace_action, @trace_tool, @trace_orchestrator).
"""

from __future__ import annotations

import sys
from typing import Any


class MockTracingAgent:
    """Mock agent with tracing capabilities for testing."""

    def __init__(self):
        self._tracing_service_name = "MockTracingAgent"
        self._span_stack = []
        self._trace_buffer = []
        self._trace_enabled = True

    def start_span(self, operation_name: str, attributes: dict[str, Any] | None = None):
        """Mock start_span context manager."""
        import contextlib

        @contextlib.contextmanager
        def span_context():
            span = MockSpan(operation_name, attributes or {})
            self._span_stack.append(span)
            try:
                yield span
            finally:
                self._span_stack.pop()
                self._trace_buffer.append({
                    "operation_name": operation_name,
                    "attributes": attributes,
                })

        return span_context()


class MockSpan:
    """Mock span for testing."""

    def __init__(self, operation_name: str, attributes: dict[str, Any]):
        self.operation_name = operation_name
        self.attributes = attributes.copy()

    def set_attribute(self, key: str, value: Any) -> None:
        self.attributes[key] = value


def test_trace_cognitive() -> bool:
    """Test @trace_cognitive decorator."""
    try:
        from agentic_core.mixins.tracing_decorators import trace_cognitive

        agent = MockTracingAgent()

        @trace_cognitive(reasoning_mode="chain_of_thought")
        def analyze(self, query: str) -> dict:
            return {"result": f"Analysis of {query}", "confidence": 0.95}

        # Call the decorated method
        result = analyze(agent, "test query")

        # Verify result
        assert result["result"] == "Analysis of test query"
        assert result["confidence"] == 0.95

        # Verify span was created (operation name contains function name)
        assert len(agent._trace_buffer) == 1
        assert "analyze" in agent._trace_buffer[0]["operation_name"]
        assert agent._trace_buffer[0]["attributes"]["reasoning_mode"] == "chain_of_thought"
        assert agent._trace_buffer[0]["attributes"]["span_kind"] == "cognitive"

        print("✓ @trace_cognitive decorator works correctly")
        return True
    except Exception as e:
        print(f"✗ @trace_cognitive test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_trace_action() -> bool:
    """Test @trace_action decorator."""
    try:
        from agentic_core.mixins.tracing_decorators import trace_action

        agent = MockTracingAgent()

        @trace_action(action_name="file_write")
        def save_data(self, data: str, path: str) -> bool:
            return True

        result = save_data(agent, "test data", "/tmp/test.txt")

        assert result is True
        assert len(agent._trace_buffer) == 1
        assert agent._trace_buffer[0]["attributes"]["span_kind"] == "action"

        print("✓ @trace_action decorator works correctly")
        return True
    except Exception as e:
        print(f"✗ @trace_action test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_trace_tool() -> bool:
    """Test @trace_tool decorator."""
    try:
        from agentic_core.mixins.tracing_decorators import trace_tool

        agent = MockTracingAgent()

        @trace_tool(tool_name="pinecone_query")
        def query_vectors(self, query: str, top_k: int = 5) -> list:
            return ["result1", "result2", "result3"]

        result = query_vectors(agent, "test query", top_k=3)

        assert len(result) == 3
        assert len(agent._trace_buffer) == 1
        assert agent._trace_buffer[0]["attributes"]["span_kind"] == "tool"
        assert agent._trace_buffer[0]["attributes"]["tool_name"] == "pinecone_query"

        print("✓ @trace_tool decorator works correctly")
        return True
    except Exception as e:
        print(f"✗ @trace_tool test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_trace_orchestrator() -> bool:
    """Test @trace_orchestrator decorator."""
    try:
        from agentic_core.mixins.tracing_decorators import trace_orchestrator

        agent = MockTracingAgent()

        @trace_orchestrator(orchestrator_name="campaign_workflow")
        def run_campaign(self, config: dict) -> dict:
            return {"status": "success", "agent_count": 5}

        result = run_campaign(agent, {"name": "test_campaign"})

        assert result["status"] == "success"
        assert result["agent_count"] == 5
        assert len(agent._trace_buffer) == 1
        assert agent._trace_buffer[0]["attributes"]["span_kind"] == "orchestrator"

        print("✓ @trace_orchestrator decorator works correctly")
        return True
    except Exception as e:
        print(f"✗ @trace_orchestrator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_trace_router() -> bool:
    """Test @trace_router decorator."""
    try:
        from agentic_core.mixins.tracing_decorators import trace_router

        agent = MockTracingAgent()

        @trace_router(router_name="intent_classifier")
        def classify_intent(self, query: str) -> str:
            return "search_intent"

        result = classify_intent(agent, "find documents about AI")

        assert result == "search_intent"
        assert len(agent._trace_buffer) == 1
        assert agent._trace_buffer[0]["attributes"]["span_kind"] == "router"

        print("✓ @trace_router decorator works correctly")
        return True
    except Exception as e:
        print(f"✗ @trace_router test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_decorator_without_tracing() -> bool:
    """Test that decorators work even without tracing instance."""
    try:
        from agentic_core.mixins.tracing_decorators import trace_cognitive

        # Regular function without tracing
        @trace_cognitive(reasoning_mode="react")
        def regular_function(query: str) -> dict:
            return {"query": query}

        result = regular_function("test")

        assert result["query"] == "test"

        print("✓ Decorators work without tracing instance (graceful degradation)")
        return True
    except Exception as e:
        print(f"✗ Graceful degradation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_decorator_preserves_signature() -> bool:
    """Test that decorators preserve function signatures."""
    try:
        import inspect

        from agentic_core.mixins.tracing_decorators import trace_cognitive

        def original_function(query: str, limit: int = 10) -> dict:
            """Original docstring."""
            return {"query": query, "limit": limit}

        decorated_function = trace_cognitive()(original_function)

        sig = inspect.signature(decorated_function)
        params = list(sig.parameters.keys())

        assert "query" in params
        assert "limit" in params
        assert decorated_function.__doc__ == "Original docstring."

        print("✓ Decorators preserve function signatures and docstrings")
        return True
    except Exception as e:
        print(f"✗ Signature preservation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main() -> int:
    """Run all Wave 1 tests."""
    print("=" * 60)
    print("Wave 1: Trace Semantics and IDs — Verification Tests")
    print("=" * 60)

    tests = [
        ("@trace_cognitive", test_trace_cognitive),
        ("@trace_action", test_trace_action),
        ("@trace_tool", test_trace_tool),
        ("@trace_orchestrator", test_trace_orchestrator),
        ("@trace_router", test_trace_router),
        ("Graceful Degradation", test_decorator_without_tracing),
        ("Signature Preservation", test_decorator_preserves_signature),
    ]

    results = []
    for name, test_func in tests:
        print(f"\n--- {name} ---")
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ Test crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 Wave 1 implementation verified successfully!")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
