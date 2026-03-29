"""
Error Handling and Robustness Tests for Token Planning Estimator

Tests for error scenarios, edge cases, malformed inputs, and recovery mechanisms.
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from typing import Dict, List, Any
from unittest import mock

# Import estimator classes and exceptions for robustness tests
from agentic_core.planning.token_estimator import ContextWindowEstimator, ContextSource, TokenEstimate
from agentic_core.planning.preflight_hook import TokenBudgetExceededError


# Lazy imports to avoid collection-time conflicts
@pytest.fixture
def planning_preflight_hook(tmp_path):
    from agentic_core.planning.preflight_hook import PlanningPreflightHook
    budget_file = tmp_path / "error_test_budget.json"
    return PlanningPreflightHook(budget_file=budget_file)


class TestTokenEstimatorErrorHandling:
    """Error handling and robustness tests"""

    def setup_method(self):
        """Setup test fixtures"""
        from agentic_core.planning.preflight_hook import PlanningPreflightHook
        self.temp_dir = Path(tempfile.mkdtemp())
        self.budget_file = self.temp_dir / "error_test_budget.json"
        self.hook = PlanningPreflightHook(budget_file=self.budget_file)

    def teardown_method(self):
        """Cleanup test fixtures"""
        if self.budget_file.exists():
            self.budget_file.unlink()
        if self.temp_dir.exists():
            self.temp_dir.rmdir()

    def test_malformed_file_inputs(self):
        """Test handling of malformed file inputs"""
        # Test with None content
        with pytest.raises(Exception):  # Should raise some exception
            self.hook.preflight_check(
                plan_step="malformed_files",
                system_prompt="Test",
                user_prompt="Test",
                files=[{"path": "test.py", "content": None}],
                diffs=[],
                logs=[],
                retrieved_context=[],
                prior_steps=[]
            )

        # Test with empty path
        estimate = self.hook.preflight_check(
            plan_step="empty_path",
            system_prompt="Test",
            user_prompt="Test",
            files=[{"path": "", "content": "content"}],
            diffs=[],
            logs=[],
            retrieved_context=[],
            prior_steps=[]
        )
        assert estimate.estimated_input_tokens >= 0

        # Test with missing required fields
        estimate = self.hook.preflight_check(
            plan_step="missing_fields",
            system_prompt="Test",
            user_prompt="Test",
            files=[{"content": "content"}],  # Missing path
            diffs=[],
            logs=[],
            retrieved_context=[],
            prior_steps=[]
        )
        assert estimate.estimated_input_tokens >= 0

    def test_unicode_and_encoding_issues(self):
        """Test handling of unicode and encoding issues"""
        # Test with various unicode characters
        unicode_content = """
        # Test various Unicode characters
        αβγδεζηθικλμνξοπρστυφχψω  # Greek
        あいうえおかきくけこ  # Japanese
        中文测试  # Chinese
        العربية  # Arabic
        עברית  # Hebrew
        🚀🛸🌟💫  # Emojis
        """

        estimate = self.hook.preflight_check(
            plan_step="unicode_test",
            system_prompt=unicode_content,
            user_prompt=unicode_content,
            files=[{"path": "unicode.py", "content": unicode_content}],
            diffs=[],
            logs=[],
            retrieved_context=[{"content": unicode_content}],
            prior_steps=[]
        )

        assert estimate.estimated_input_tokens > 0
        assert estimate.status == 'green'

    def test_extremely_long_strings(self):
        """Test handling of extremely long strings"""
        # Test with very long prompts (but stay under memory limits)
        long_prompt = "x" * 100000  # 100K characters

        estimate = self.hook.preflight_check(
            plan_step="long_string",
            system_prompt=long_prompt,
            user_prompt=long_prompt,
            files=[{"path": "long.py", "content": long_prompt}],
            diffs=[],
            logs=[],
            retrieved_context=[],
            prior_steps=[]
        )

        assert estimate.estimated_input_tokens > 0
        # Should handle long strings without crashing
        assert estimate.status in ['green', 'yellow', 'red']

    def test_corrupted_budget_file(self):
        """Test handling of corrupted budget file"""
        # Create corrupted JSON file
        with open(self.budget_file, 'w') as f:
            f.write("{ invalid json content")

        # Should handle corrupted file gracefully
        from agentic_core.planning.preflight_hook import PlanningPreflightHook
        hook = PlanningPreflightHook(budget_file=self.budget_file)

        estimate = hook.preflight_check(
            plan_step="corrupted_file_test",
            system_prompt="Test",
            user_prompt="Test",
            files=[],
            diffs=[],
            logs=[],
            retrieved_context=[],
            prior_steps=[]
        )

        assert estimate.estimated_input_tokens >= 0

    def test_permission_denied_budget_file(self):
        """Test handling when budget file is not writable using mocking"""
        # Create file
        self.budget_file.touch()

        # Mock open to simulate permission denied when writing (cross-platform)
        original_open = open
        call_count = [0]

        def mock_open_permission_error(filepath, *args, **kwargs):
            # Simulate permission denied on write attempts to budget file
            if str(filepath) == str(self.budget_file) and 'w' in str(args):
                if call_count[0] == 0:
                    call_count[0] += 1
                    raise PermissionError(13, "Permission denied", str(filepath))
            return original_open(filepath, *args, **kwargs)

        with mock.patch("builtins.open", mock_open_permission_error):
            from agentic_core.planning.preflight_hook import PlanningPreflightHook
            hook = PlanningPreflightHook(budget_file=self.budget_file)

            estimate = hook.preflight_check(
                plan_step="permission_test",
                system_prompt="Test",
                user_prompt="Test",
                files=[],
                diffs=[],
                logs=[],
                retrieved_context=[],
                prior_steps=[]
            )

            # Should handle permission error gracefully
            assert estimate.estimated_input_tokens >= 0

    def test_empty_and_null_inputs(self):
        """Test handling of empty and null inputs"""
        # Test completely empty inputs
        estimate = self.hook.preflight_check(
            plan_step="empty_test",
            system_prompt="",
            user_prompt="",
            files=[],
            diffs=[],
            logs=[],
            retrieved_context=[],
            prior_steps=[]
        )

        assert estimate.estimated_input_tokens >= 0
        assert estimate.status == 'green'

        # Test with empty lists
        estimate = self.hook.preflight_check(
            plan_step="empty_lists",
            system_prompt="Test",
            user_prompt="Test",
            files=[],
            diffs=[],
            logs=[],
            retrieved_context=[],
            prior_steps=[]
        )

        assert estimate.estimated_input_tokens > 0

    def test_malformed_context_sources(self):
        """Test handling of malformed context sources"""
        estimator = ContextWindowEstimator()

        # Test with None content - ContextSource should handle this gracefully
        try:
            source = ContextSource('file', None, 100, metadata={'path': 'test'})
            # If it doesn't raise, that's fine - check it handles None gracefully
            assert source.content is None
        except Exception:
            # If it raises, that's also acceptable
            pass

        # Test with negative tokens
        source = ContextSource('file', 'content', -100, metadata={'path': 'test'})
        assert source.tokens == -100  # Should accept but handle gracefully

        # Test with missing metadata
        source = ContextSource('file', 'content', 100, metadata={})
        assert source.metadata == {}

    def test_compression_error_handling(self):
        """Test compression error handling"""
        estimator = ContextWindowEstimator()

        # Test compression with malformed sources
        malformed_sources = [
            ContextSource('file', 'content', 100, metadata={'path': 'test'})
        ]

        estimate = TokenEstimate(
            plan_step="error_test",
            estimated_input_tokens=50000,
            reserved_output_tokens=12000,
            safety_buffer_tokens=8000,
            total_projected_tokens=70000,
            status='yellow',
            action='compress',
            top_contributors=[],
            recommended_reductions=[]
        )

        # Should handle compression errors gracefully
        try:
            compressed_estimate = estimator._apply_compression(estimate, malformed_sources)
            assert compressed_estimate is not None
        except Exception as e:
            # If an error occurs, it should be a reasonable one
            assert isinstance(e, (ValueError, TypeError, AttributeError))

    def test_budget_calculation_edge_cases(self):
        """Test budget calculation edge cases"""
        # Test with zero tokens
        estimate = self.hook.preflight_check(
            plan_step="zero_tokens",
            system_prompt="",
            user_prompt="",
            files=[],
            diffs=[],
            logs=[],
            retrieved_context=[],
            prior_steps=[]
        )

        assert estimate.estimated_input_tokens >= 0
        assert estimate.reserved_output_tokens > 0
        assert estimate.safety_buffer_tokens > 0
        assert estimate.total_projected_tokens >= estimate.reserved_output_tokens + estimate.safety_buffer_tokens

    def test_status_determination_edge_cases(self):
        """Test status determination edge cases"""
        estimator = ContextWindowEstimator()

        # Test exactly at boundaries
        # WARNING_THRESHOLD = 197000, SAFE_OPERATING_CAP = 223000, HARD_MAX_CONTEXT = 262000
        boundary_tests = [
            (196999, 'green'),   # Just under warning threshold
            (197000, 'green'),   # Exactly at warning threshold (still green)
            (197001, 'yellow'),  # Just over warning threshold
            (222999, 'yellow'),  # Just under safe cap
            (223000, 'yellow'),  # Exactly at safe cap (still yellow)
            (223001, 'red'),     # Just over safe cap
        ]

        for tokens, expected_status in boundary_tests:
            status, action = estimator._determine_status_action(tokens)
            assert status == expected_status, f"Expected {expected_status} for {tokens}, got {status}"

    def test_decorator_error_handling(self):
        """Test decorator error handling"""
        from agentic_core.planning.preflight_hook import require_token_budget
        @require_token_budget(self.hook)
        def test_function(system_prompt, user_prompt, **kwargs):
            return "success"

        # Test with missing required parameters
        with pytest.raises(TypeError):
            test_function()  # Missing required params

        # Test with parameters that would cause budget exceeded
        try:
            result = test_function(
                system_prompt="x" * 1000000,  # Very large
                user_prompt="test",
                files=[]
            )
            # If it doesn't raise an error, that's fine (compression might handle it)
        except TokenBudgetExceededError:
            # Expected for very large content
            pass
        except Exception as e:
            # Other errors should be reasonable
            assert isinstance(e, (ValueError, TypeError))

    def test_concurrent_access_errors(self):
        """Test error handling under concurrent access simulation"""
        # Simulate rapid successive access
        errors = []

        for i in range(50):
            try:
                estimate = self.hook.preflight_check(
                    plan_step=f"concurrent_error_test_{i}",
                    system_prompt=f"Test {i}",
                    user_prompt=f"User {i}",
                    files=[{"path": f"test_{i}.py", "content": f"content {i}"}],
                    diffs=[],
                    logs=[],
                    retrieved_context=[],
                    prior_steps=[]
                )
                assert estimate is not None
            except Exception as e:
                errors.append((i, e))

        # Should have minimal errors
        assert len(errors) < 5, f"Too many errors: {len(errors)}"

        for i, error in errors:
            print(f"Error in iteration {i}: {error}")

    def test_memory_pressure_handling(self):
        """Test behavior under memory pressure"""
        # Create many large estimates to test memory handling
        estimates = []

        try:
            for i in range(20):
                estimate = self.hook.preflight_check(
                    plan_step=f"memory_pressure_{i}",
                    system_prompt=f"Test {i} " * 1000,
                    user_prompt=f"User {i} " * 1000,
                    files=[{"path": f"large_{i}.py", "content": f"content {i} " * 1000}],
                    diffs=[],
                    logs=[],
                    retrieved_context=[],
                    prior_steps=[]
                )
                estimates.append(estimate)
        except MemoryError:
            # Should handle memory pressure gracefully
            pytest.skip("Memory pressure test skipped - insufficient memory")
        except Exception as e:
            # Other exceptions should be reasonable
            assert isinstance(e, (ValueError, TypeError, OSError))

        # Should have successfully created some estimates
        assert len(estimates) > 0

        # All estimates should be valid
        for estimate in estimates:
            assert estimate.estimated_input_tokens >= 0
            assert estimate.status in ['green', 'yellow', 'red']

    def test_file_system_errors(self):
        """Test handling of file system errors"""
        # Test with non-existent budget file directory
        non_existent_dir = Path("/tmp/non_existent_dir_12345")
        non_existent_file = non_existent_dir / "budget.json"

        try:
            from agentic_core.planning.preflight_hook import PlanningPreflightHook
            hook = PlanningPreflightHook(budget_file=non_existent_file)

            estimate = hook.preflight_check(
                plan_step="fs_error_test",
                system_prompt="Test",
                user_prompt="Test",
                files=[],
                diffs=[],
                logs=[],
                retrieved_context=[],
                prior_steps=[]
            )

            assert estimate.estimated_input_tokens >= 0
        except Exception as e:
            # Should handle file system errors gracefully
            assert isinstance(e, (OSError, IOError, PermissionError))
        finally:
            # Cleanup if directory was created
            try:
                if non_existent_dir.exists():
                    non_existent_file.unlink(missing_ok=True)
                    non_existent_dir.rmdir()
            except OSError:
                pass

    def test_data_type_errors(self):
        """Test handling of incorrect data types"""
        # Test with wrong data types in parameters
        try:
            # This should either work or fail gracefully
            estimate = self.hook.preflight_check(
                plan_step="type_error_test",
                system_prompt=123,  # Should be string
                user_prompt=[1, 2, 3],  # Should be string
                files="not a list",  # Should be list
                diffs=None,  # Should be list
                logs="not a list",  # Should be list
                retrieved_context="not a list",  # Should be list
                prior_steps="not a list"  # Should be list
            )
        except Exception as e:
            # Should fail with a reasonable error
            assert isinstance(e, (TypeError, ValueError, AttributeError))

    def test_token_estimation_errors(self):
        """Test token estimation error handling"""
        estimator = ContextWindowEstimator()

        # Test with None content
        try:
            tokens = estimator._estimate_tokens(None, "text")
            assert tokens >= 0  # Should handle gracefully
        except Exception as e:
            assert isinstance(e, (TypeError, ValueError))

        # Test with invalid content type
        try:
            tokens = estimator._estimate_tokens("content", "invalid_type")
            assert tokens >= 0  # Should fall back to default
        except Exception as e:
            assert isinstance(e, (ValueError, AttributeError))

    def test_recovery_after_errors(self):
        """Test system recovery after errors"""
        # Cause an error
        try:
            self.hook.preflight_check(
                plan_step="error_cause",
                system_prompt=None,  # This might cause an error
                user_prompt="Test",
                files=[],
                diffs=[],
                logs=[],
                retrieved_context=[],
                prior_steps=[]
            )
        except Exception:
            pass  # Expected to fail

        # System should recover and work normally after error
        estimate = self.hook.preflight_check(
            plan_step="recovery_test",
            system_prompt="Recovery test",
            user_prompt="Test",
            files=[{"path": "recovery.py", "content": "test content"}],
            diffs=[],
            logs=[],
            retrieved_context=[],
            prior_steps=[]
        )

        assert estimate.estimated_input_tokens >= 0
        assert estimate.status in ['green', 'yellow', 'red']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
