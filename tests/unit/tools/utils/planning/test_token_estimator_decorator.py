"""Decorator Enforcement and Preflight Hook Integration Tests

Tests for decorator-based enforcement, preflight hook integration, and comprehensive workflow scenarios.
"""

import json
import tempfile
import time
from importlib.util import find_spec
from pathlib import Path

import pytest

# Check if token_estimator modules are available
TOKEN_ESTIMATOR_AVAILABLE = (
    find_spec("agentic_core.planning.token_estimator") is not None
    and find_spec("agentic_core.planning.preflight_hook") is not None
)


pytestmark = pytest.mark.skipif(
    not TOKEN_ESTIMATOR_AVAILABLE,
    reason="token estimator modules not available",
)


# Lazy imports to avoid collection-time conflicts
@pytest.fixture
def token_estimator_classes():
    from tools.utils.planning.preflight_hook import (
        PlanningPreflightHook,
        TokenBudgetExceededError,
        require_token_budget,
    )
    from tools.utils.planning.token_estimator import (
        ContextSource,
        ContextWindowEstimator,
        TokenBudget,
        TokenEstimate,
    )

    return (
        ContextWindowEstimator,
        TokenBudget,
        TokenEstimate,
        ContextSource,
        PlanningPreflightHook,
        TokenBudgetExceededError,
        require_token_budget,
    )


class TestDecoratorEnforcementIntegration:
    """Decorator enforcement and preflight hook integration tests"""

    def setup_method(self):
        """Setup test fixtures"""
        from tools.utils.planning.preflight_hook import (
            PlanningPreflightHook,
        )

        self.temp_dir = Path(tempfile.mkdtemp())
        self.budget_file = self.temp_dir / "decorator_test_budget.json"
        self.hook = PlanningPreflightHook(budget_file=self.budget_file)

    def teardown_method(self):
        """Cleanup test fixtures"""
        if self.budget_file.exists():
            self.budget_file.unlink()
        if self.temp_dir.exists():
            self.temp_dir.rmdir()

    def test_decorator_basic_functionality(self):
        """Test basic decorator functionality"""
        from tools.utils.planning.preflight_hook import require_token_budget

        @require_token_budget(self.hook)
        def simple_function(system_prompt, user_prompt, files, **kwargs):
            return {"status": "success", "processed": True}

        # Test with normal inputs
        result = simple_function(
            system_prompt="Simple test",
            user_prompt="User input",
            files=[{"path": "test.py", "content": "test content"}],
        )

        assert result["status"] == "success"
        assert result["processed"] == True

        # Verify budget was recorded
        summary = self.hook.get_budget_summary()
        assert summary["total_steps"] == 1
        assert summary["total_tokens"] > 0

    def test_decorator_budget_enforcement(self):
        """Test decorator enforces budget limits"""
        from tools.utils.planning.preflight_hook import TokenBudgetExceededError, require_token_budget

        @require_token_budget(self.hook)
        def budget_sensitive_function(system_prompt, user_prompt, files, **kwargs):
            return {"status": "success"}

        # Test with content that should exceed budget
        large_content = "x" * 1000000  # Very large content

        with pytest.raises(TokenBudgetExceededError):
            budget_sensitive_function(
                system_prompt=large_content,
                user_prompt=large_content,
                files=[{"path": "large.py", "content": large_content}],
            )

        # Should not have recorded the failed attempt
        summary = self.hook.get_budget_summary()
        assert summary["total_steps"] == 0

    def test_decorator_with_various_signatures(self):
        """Test decorator works with different function signatures"""
        from tools.utils.planning.preflight_hook import require_token_budget

        @require_token_budget(self.hook)
        def function_with_kwargs(system_prompt, **kwargs):
            return {"kwargs": list(kwargs.keys())}

        @require_token_budget(self.hook)
        def function_with_args(system_prompt, user_prompt, *args, **kwargs):
            return {"args_count": len(args), "kwargs_count": len(kwargs)}

        @require_token_budget(self.hook)
        def function_no_files(system_prompt, user_prompt):
            return {"no_files": True}

        # Test each function
        result1 = function_with_kwargs(
            system_prompt="Test",
            user_prompt="User",
            files=[],
            extra_param="value",
        )
        assert "extra_param" in result1["kwargs"]

        result2 = function_with_args(system_prompt="Test", user_prompt="User", files=[], extra="value")
        assert result2["args_count"] == 0
        assert result2["kwargs_count"] == 2  # files and extra

        result3 = function_no_files(system_prompt="Test", user_prompt="User")
        assert result3["no_files"] == True

        # Verify all were recorded
        summary = self.hook.get_budget_summary()
        assert summary["total_steps"] == 3

    def test_decorator_error_propagation(self):
        """Test decorator properly propagates function errors"""
        from tools.utils.planning.preflight_hook import require_token_budget

        @require_token_budget(self.hook)
        def error_function(system_prompt, user_prompt, files, **kwargs):
            raise ValueError("Test error")

        # Should propagate the original error but budget check is still recorded
        with pytest.raises(ValueError, match="Test error"):
            error_function(system_prompt="Test", user_prompt="User", files=[])

        # Budget check is recorded even if function fails
        summary = self.hook.get_budget_summary()
        assert summary["total_steps"] == 1  # Budget check was performed

    def test_nested_decorators(self):
        """Test decorator works with nested decorators"""
        from tools.utils.planning.preflight_hook import require_token_budget

        def timing_decorator(func):
            def wrapper(*args, **kwargs):
                start = time.time()
                result = func(*args, **kwargs)
                end = time.time()
                result["timing"] = end - start
                return result

            return wrapper

        @require_token_budget(self.hook)
        @timing_decorator
        def nested_function(system_prompt, user_prompt, files, **kwargs):
            return {"status": "success"}

        result = nested_function(
            system_prompt="Nested test",
            user_prompt="User input",
            files=[{"path": "nested.py", "content": "nested content"}],
        )

        assert result["status"] == "success"
        assert "timing" in result
        assert result["timing"] >= 0

        # Verify budget was recorded
        summary = self.hook.get_budget_summary()
        assert summary["total_steps"] == 1

    def test_decorator_class_methods(self):
        """Test decorator works with class methods"""
        from tools.utils.planning.preflight_hook import require_token_budget

        class TestProcessor:
            def __init__(self, name):
                self.name = name

            @require_token_budget(self.hook)
            def process(self, system_prompt, user_prompt, files, **kwargs):
                return {"processor": self.name, "processed": True}

            @classmethod
            @require_token_budget(self.hook)
            def class_process(cls, system_prompt, user_prompt, files, **kwargs):
                return {"class": cls.__name__, "processed": True}

        processor = TestProcessor("test_processor")

        # Test instance method
        result1 = processor.process(
            system_prompt="Instance test",
            user_prompt="User input",
            files=[{"path": "instance.py", "content": "instance content"}],
        )
        assert result1["processor"] == "test_processor"
        assert result1["processed"] == True

        # Test class method
        result2 = TestProcessor.class_process(
            system_prompt="Class test",
            user_prompt="User input",
            files=[{"path": "class.py", "content": "class content"}],
        )
        assert result2["class"] == "TestProcessor"
        assert result2["processed"] == True

        # Verify both were recorded
        summary = self.hook.get_budget_summary()
        assert summary["total_steps"] == 2

    def test_multiple_hooks_same_function(self):
        """Test using multiple hooks with different functions"""
        from tools.utils.planning.preflight_hook import PlanningPreflightHook, require_token_budget

        hook1 = PlanningPreflightHook(budget_file=self.temp_dir / "hook1.json")
        hook2 = PlanningPreflightHook(budget_file=self.temp_dir / "hook2.json")

        @require_token_budget(hook1)
        def function1(system_prompt, user_prompt, files, **kwargs):
            return {"function": "function1"}

        @require_token_budget(hook2)
        def function2(system_prompt, user_prompt, files, **kwargs):
            return {"function": "function2"}

        # Test both functions
        result1 = function1(
            system_prompt="Test 1",
            user_prompt="User 1",
            files=[{"path": "test1.py", "content": "content1"}],
        )

        result2 = function2(
            system_prompt="Test 2",
            user_prompt="User 2",
            files=[{"path": "test2.py", "content": "content2"}],
        )

        assert result1["function"] == "function1"
        assert result2["function"] == "function2"

        # Verify each hook recorded separately
        summary1 = hook1.get_budget_summary()
        summary2 = hook2.get_budget_summary()

        assert summary1["total_steps"] == 1
        assert summary2["total_steps"] == 1

        # Cleanup
        (self.temp_dir / "hook1.json").unlink(missing_ok=True)
        (self.temp_dir / "hook2.json").unlink(missing_ok=True)

    def test_decorator_compression_handling(self):
        """Test decorator handles compression correctly"""
        from tools.utils.planning.preflight_hook import require_token_budget

        @require_token_budget(self.hook)
        def compressible_function(system_prompt, user_prompt, files, **kwargs):
            return {"status": "success"}

        # Create content that should trigger compression but not exceed hard limit
        medium_content = "x" * 100000  # Large but manageable

        result = compressible_function(
            system_prompt=medium_content,
            user_prompt=medium_content,
            files=[{"path": "medium.py", "content": medium_content}],
        )

        assert result["status"] == "success"

        # Should have been recorded (compression should have handled it)
        summary = self.hook.get_budget_summary()
        assert summary["total_steps"] == 1

        # Check if compression was applied (status might be yellow)
        # We can't directly check compression from decorator, but function succeeded

    def test_decorator_with_complex_data_structures(self):
        """Test decorator with complex data structures"""
        from tools.utils.planning.preflight_hook import require_token_budget

        @require_token_budget(self.hook)
        def complex_function(system_prompt, user_prompt, files, **kwargs):
            return {"processed": True}

        # Test with complex file structures
        complex_files = [
            {
                "path": "complex.py",
                "content": "Complex content with nested structures",
                "metadata": {"type": "python", "lines": 100},
            },
            {
                "path": "data.json",
                "content": json.dumps({"key": "value", "nested": {"data": [1, 2, 3]}}),
                "metadata": {"type": "json"},
            },
        ]

        complex_retrieved = [
            {"content": "Retrieved content 1", "source": "doc1", "relevance": 0.9},
            {"content": "Retrieved content 2", "source": "doc2", "relevance": 0.8},
        ]

        complex_prior = ["Prior step 1 result", "Prior step 2 result with more detail"]

        result = complex_function(
            system_prompt="Complex test",
            user_prompt="Complex user input",
            files=complex_files,
            diffs=[{"path": "diff.py", "content": "diff content"}],
            logs=[{"source": "app.log", "content": "log content"}],
            retrieved_context=complex_retrieved,
            prior_steps=complex_prior,
        )

        assert result["processed"] == True

        # Verify complex data was handled
        summary = self.hook.get_budget_summary()
        assert summary["total_steps"] == 1
        assert summary["total_tokens"] > 0

    def test_decorator_async_compatibility(self):
        """Test decorator is compatible with async functions (if needed)"""
        from tools.utils.planning.preflight_hook import require_token_budget
        # Note: This test shows the decorator doesn't interfere with async functions
        # but actual async support would require async-specific implementation

        def sync_async_test_function(system_prompt, user_prompt, files, **kwargs):
            """Simulates what would be an async function"""
            return {"async_compatible": True}

        # Apply decorator to sync function (would need async decorator for real async)
        decorated_sync = require_token_budget(self.hook)(sync_async_test_function)

        result = decorated_sync(
            system_prompt="Async test",
            user_prompt="User input",
            files=[{"path": "async.py", "content": "async content"}],
        )

        assert result["async_compatible"] == True

        summary = self.hook.get_budget_summary()
        assert summary["total_steps"] == 1

    def test_decorator_performance_impact(self):
        """Test decorator performance impact"""
        from tools.utils.planning.preflight_hook import require_token_budget

        @require_token_budget(self.hook)
        def performance_function(system_prompt, user_prompt, files, **kwargs):
            return {"processed": True}

        # Measure multiple calls
        times = []
        for i in range(50):
            start = time.time()

            result = performance_function(
                system_prompt=f"Performance test {i}",
                user_prompt=f"User input {i}",
                files=[{"path": f"perf_{i}.py", "content": f"content {i}" * 100}],
            )

            end = time.time()
            times.append(end - start)

            assert result["processed"] == True

        avg_time = sum(times) / len(times)
        max_time = max(times)

        # Performance assertions (decorator shouldn't add significant overhead)
        assert avg_time < 0.1, f"Average time too high: {avg_time:.4f}s"
        assert max_time < 0.5, f"Max time too high: {max_time:.4f}s"

        # Verify all calls were recorded
        summary = self.hook.get_budget_summary()
        assert summary["total_steps"] == 50

        print(f"Decorator performance: avg={avg_time:.4f}s, max={max_time:.4f}s")

    def test_integration_with_real_workflow_pattern(self):
        """Test decorator integration with realistic workflow pattern"""
        from tools.utils.planning.preflight_hook import require_token_budget

        class PlanningWorkflow:
            def __init__(self, hook):
                self.hook = hook
                self.results = []

            @require_token_budget(self.hook)
            def analyze_requirements(self, requirements_text):
                """Analyze requirements and return analysis"""
                return {
                    "step": "analyze_requirements",
                    "requirements_analyzed": len(requirements_text),
                    "status": "completed",
                }

            @require_token_budget(self.hook)
            def design_architecture(self, requirements_analysis):
                """Design system architecture"""
                return {
                    "step": "design_architecture",
                    "components": ["auth", "database", "api"],
                    "status": "completed",
                }

            @require_token_budget(self.hook)
            def plan_implementation(self, architecture_design):
                """Plan implementation steps"""
                return {"step": "plan_implementation", "implementation_steps": 5, "status": "completed"}

            def execute_workflow(self, requirements):
                """Execute complete workflow"""
                step1 = self.analyze_requirements(requirements)
                step2 = self.design_architecture(step1)
                step3 = self.plan_implementation(step2)

                return [step1, step2, step3]

        # Execute workflow
        workflow = PlanningWorkflow(self.hook)
        requirements = "Build a user authentication system with JWT tokens"

        results = workflow.execute_workflow(requirements)

        # Verify workflow completed
        assert len(results) == 3
        assert all(r["status"] == "completed" for r in results)

        # Verify budget tracking
        summary = self.hook.get_budget_summary()
        assert summary["total_steps"] == 3
        assert summary["total_tokens"] > 0

        # Verify step names in budget (if available)
        print(f"Workflow completed with {summary['total_steps']} steps")
        print(f"Total tokens used: {summary['total_tokens']:,}")

    def test_decorator_error_recovery(self):
        """Test decorator error recovery scenarios"""
        from tools.utils.planning.preflight_hook import require_token_budget

        @require_token_budget(self.hook)
        def sometimes_failing_function(system_prompt, user_prompt, files, **kwargs):
            if "fail" in system_prompt.lower():
                raise RuntimeError("Intentional failure")
            return {"status": "success"}

        # Successful call
        result1 = sometimes_failing_function(
            system_prompt="Normal operation",
            user_prompt="User input",
            files=[],
        )
        assert result1["status"] == "success"

        # Failing call
        with pytest.raises(RuntimeError, match="Intentional failure"):
            sometimes_failing_function(system_prompt="This will fail", user_prompt="User input", files=[])

        # Successful call after failure
        result2 = sometimes_failing_function(
            system_prompt="Recovery operation",
            user_prompt="User input",
            files=[],
        )
        assert result2["status"] == "success"

        # Verify all budget checks were recorded (including the failed one)
        summary = self.hook.get_budget_summary()
        assert summary["total_steps"] == 3  # All budget checks performed

    def test_decorator_state_isolation(self):
        """Test decorator maintains proper state isolation"""
        from tools.utils.planning.preflight_hook import require_token_budget

        @require_token_budget(self.hook)
        def stateful_function(system_prompt, user_prompt, files, **kwargs):
            # Function shouldn't be affected by decorator state
            return {
                "input_length": len(system_prompt + user_prompt),
                "file_count": len(files),
                "status": "success",
            }

        # Multiple calls with different inputs
        results = []
        for i in range(10):
            result = stateful_function(
                system_prompt=f"Test {i}",
                user_prompt=f"User {i}",
                files=[{"path": f"file_{i}.py", "content": f"content {i}"}],
            )
            results.append(result)

        # Verify each call got correct inputs
        for i, result in enumerate(results):
            assert result["input_length"] == len(f"Test {i}User {i}")
            assert result["file_count"] == 1
            assert result["status"] == "success"

        # Verify all were recorded
        summary = self.hook.get_budget_summary()
        assert summary["total_steps"] == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
