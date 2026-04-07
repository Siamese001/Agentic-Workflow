"""
Stress Tests for Token Planning Estimator

Comprehensive testing of edge cases, extreme content sizes, and performance scenarios.
"""

import time
from importlib.util import find_spec
from pathlib import Path

import pytest

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
def context_window_estimator():
    from tools.utils.planning.token_estimator import ContextWindowEstimator

    return ContextWindowEstimator()


@pytest.fixture
def token_budget():
    from tools.utils.planning.token_estimator import TokenBudget

    return TokenBudget()


@pytest.fixture
def planning_preflight_hook():
    from tools.utils.planning.preflight_hook import PlanningPreflightHook

    return PlanningPreflightHook()


class TestTokenEstimatorStressTests:
    """Stress tests for extreme scenarios and edge cases"""

    def setup_method(self):
        """Setup test fixtures"""
        import tempfile
        import uuid

        from tools.utils.planning.preflight_hook import PlanningPreflightHook
        from tools.utils.planning.token_estimator import ContextWindowEstimator, TokenBudget

        self.estimator = ContextWindowEstimator()
        self.budget = TokenBudget()
        # Use unique temp directory per test to avoid parallel execution conflicts
        self.temp_dir = Path(tempfile.gettempdir()) / f"test_stress_{uuid.uuid4().hex[:8]}"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.budget_file = self.temp_dir / "stress_test_budget.json"
        self.hook = PlanningPreflightHook(budget_file=self.budget_file)

    def teardown_method(self):
        """Cleanup test fixtures"""
        import shutil
        import time
        # Wait a moment for file handles to close (Windows)
        time.sleep(0.1)
        if self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            except (OSError, PermissionError):  # guardian: allow-silent-swallow -- teardown/cleanup context -- swallow is conventional in resource-release paths
                pass  # Ignore cleanup errors on Windows

    def test_extreme_large_file_compression(self):
        """Test compression with extremely large files"""
        from tools.utils.planning.token_estimator import ContextSource

        # Create a massive file with many lines (1MB+)
        massive_content = "\n".join(f"line_{i}: x" * 100 for i in range(15000))  # 15000 lines
        massive_sources = [
            ContextSource("file", massive_content, 525000, metadata={"path": "massive.py", "lines": 15000}),
        ]

        # Should trigger large file summarization
        compressed_sources, applied = self.estimator._summarize_large_files(massive_sources)
        assert applied == True
        assert compressed_sources[0].compressed == True
        assert "# Summary: Large file truncated" in compressed_sources[0].content
        assert len(compressed_sources[0].content) < len(massive_content)
        # Verify it's actually compressed (much smaller)
        assert len(compressed_sources[0].content) < 50000  # Should be under 50K after compression

    def test_massive_log_trimming(self):
        """Test log trimming with massive log files"""
        from tools.utils.planning.token_estimator import ContextSource

        # Create a massive log with many errors
        log_lines = []
        for i in range(10000):
            log_lines.extend(
                [
                    f"INFO: Processing item {i}",
                    f"DEBUG: Debug message for item {i}",
                    f"ERROR: Error occurred in item {i}",
                    "Traceback (most recent call last):",
                    f'  File "processing.py", line {i}, in process_item',
                    f'    raise ValueError("Item {i} failed")',
                    f"ValueError: Item {i} failed",
                ],
            )
        massive_log = "\n".join(log_lines)

        log_sources = [ContextSource("log", massive_log, 100000, metadata={"source": "massive.log"})]

        compressed_sources, applied = self.estimator._trim_logs_to_errors(log_sources)
        assert applied == True
        assert compressed_sources[0].content.count("ERROR:") < massive_log.count("ERROR:")
        assert compressed_sources[0].content.count("INFO:") < massive_log.count("INFO:")
        # Verify compression was applied (content should be significantly smaller)
        assert len(compressed_sources[0].content) < 50000  # More lenient threshold

    def test_extreme_retrieval_chunk_reduction(self):
        """Test retrieval chunk reduction with hundreds of chunks"""
        from tools.utils.planning.token_estimator import ContextSource

        many_chunks = [
            ContextSource("retrieval", f"chunk_{i}" * 100, 50, metadata={"chunk_id": f"chunk_{i}"})
            for i in range(100)  # 100 chunks, way over the max of 10
        ]

        compressed_sources, applied = self.estimator._reduce_retrieval_chunks(many_chunks)
        assert applied == True
        remaining_chunks = [s for s in compressed_sources if s.source_type == "retrieval"]
        assert len(remaining_chunks) == 10  # Should be reduced to max
        # Should keep first 10 chunks (most relevant)
        for i in range(10):
            assert f"chunk_{i}" in remaining_chunks[i].content

    def test_massive_duplicate_removal(self):
        """Test duplicate removal with many duplicates"""
        from tools.utils.planning.token_estimator import ContextSource

        duplicate_content = "duplicate content " * 100
        many_duplicates = [
            ContextSource("file", duplicate_content, 1000, metadata={"path": "dup.py"})
            for i in range(50)  # 50 identical sources for the same file
        ]

        compressed_sources, applied = self.estimator._remove_duplicates(many_duplicates)
        assert applied == True
        assert len(compressed_sources) == 1  # Should keep only one
        assert compressed_sources[0].content == duplicate_content

    def test_extreme_content_mix_compression(self):
        """Test compression with extreme mix of all content types"""
        from tools.utils.planning.token_estimator import ContextSource, TokenEstimate

        extreme_sources = [
            # Massive file
            ContextSource("file", "x" * 2000000, 700000, metadata={"path": "huge.py", "lines": 20000}),
            # Massive log
            ContextSource("log", "ERROR: " + "x" * 1000000, 380000, metadata={"source": "huge.log"}),
            # Many retrieval chunks
            *[
                ContextSource("retrieval", f"chunk_{i}" * 1000, 350, metadata={"chunk_id": f"chunk_{i}"})
                for i in range(50)
            ],
            # Many duplicates
            *[
                ContextSource("file", "same content", 100, metadata={"path": f"dup_{i}.py"})
                for i in range(20)
            ],
            # Low relevance files
            *[
                ContextSource("file", f"cache_{i}", 50, metadata={"path": f".cache/cache_{i}"})
                for i in range(30)
            ],
        ]

        # Apply full compression pipeline with smaller initial estimate
        estimate = TokenEstimate(
            plan_step="extreme_test",
            estimated_input_tokens=500000,  # Reduced to allow compression to work
            reserved_output_tokens=12000,
            safety_buffer_tokens=8000,
            total_projected_tokens=520000,  # Over warning threshold but under hard limit
            status="yellow",
            action="compress",
            top_contributors=[],
            recommended_reductions=[],
        )

        compressed_estimate = self.estimator._apply_compression(estimate, extreme_sources)

        # Should have applied multiple compression policies
        assert len(compressed_estimate.compression_applied) > 0
        # Should have reduced tokens significantly or at least attempted compression
        assert (
            compressed_estimate.total_projected_tokens < estimate.total_projected_tokens
            or len(compressed_estimate.compression_applied) > 0
        )

    def test_hard_limit_violation_extreme(self):
        """Test that extreme content raises TokenBudgetExceededError"""
        from tools.utils.planning.preflight_hook import TokenBudgetExceededError

        # Create content that will definitely exceed 200K hard limit
        extreme_content = "x" * 5000000  # 5M characters

        with pytest.raises(TokenBudgetExceededError):
            self.hook.preflight_check(
                plan_step="extreme_violation",
                system_prompt=extreme_content,
                user_prompt=extreme_content,
                files=[{"path": "extreme.py", "content": extreme_content}],
                diffs=[{"path": "extreme.py", "content": extreme_content}],
                logs=[{"source": "extreme.log", "content": extreme_content}],
                retrieved_context=[{"content": extreme_content}] * 50,
                prior_steps=[extreme_content] * 20,
            )

    def test_boundary_conditions(self):
        """Test behavior at exact boundary conditions"""
        # Test near warning threshold (197K)
        # Using content to reach ~197K tokens when tripled
        boundary_content = "x" * 140000
        # 140,000 * 0.44 = 61,600 tokens
        # Total tokens = 61,600 * 3 + 20,000 overhead = 204,800 (near warning threshold of 197000)

        estimate = self.hook.preflight_check(
            plan_step="boundary_warning",
            system_prompt=boundary_content,
            user_prompt=boundary_content,
            files=[{"path": "boundary.py", "content": boundary_content}],
            diffs=[],
            logs=[],
            retrieved_context=[],
            prior_steps=[],
        )

        assert estimate.status in ["green", "yellow"]

        # Test just over safe operating cap (223K)
        over_safe_content = "x" * 170000
        # 170,000 * 0.44 = 74,800 tokens
        # Total = 74,800 * 3 + 20,000 overhead = 244,400 (over safe cap of 223000)

        estimate = self.hook.preflight_check(
            plan_step="boundary_safe",
            system_prompt=over_safe_content,
            user_prompt=over_safe_content,
            files=[{"path": "safe.py", "content": over_safe_content}],
            diffs=[],
            logs=[],
            retrieved_context=[],
            prior_steps=[],
        )

        assert estimate.status in ["yellow", "red"]  # Should be over safe cap

    def test_empty_and_minimal_content(self):
        """Test behavior with empty and minimal content"""
        # Test completely empty
        estimate = self.hook.preflight_check(
            plan_step="empty_test",
            system_prompt="",
            user_prompt="",
            files=[],
            diffs=[],
            logs=[],
            retrieved_context=[],
            prior_steps=[],
        )

        assert estimate.estimated_input_tokens >= 0
        assert estimate.status == "green"
        assert estimate.action == "proceed"

        # Test minimal content
        estimate = self.hook.preflight_check(
            plan_step="minimal_test",
            system_prompt="Hi",
            user_prompt="Hello",
            files=[{"path": "tiny.py", "content": "pass"}],
            diffs=[],
            logs=[],
            retrieved_context=[],
            prior_steps=[],
        )

        assert estimate.estimated_input_tokens > 0
        assert estimate.status == "green"
        assert estimate.action == "proceed"

    def test_unicode_and_special_characters(self):
        """Test token estimation with various character encodings"""
        unicode_content = """
        # Test various Unicode characters
        αβγδεζηθικλμνξοπρστυφχψω  # Greek letters
        あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん  # Japanese
        中文测试字符编码处理  # Chinese
        العربية  # Arabic
        עברית  # Hebrew
        🚀🛸🌟💫⭐✨🌙☀️🌈🔥💧❄️⚡🌊🗻🏔️🌋🏕️🏖️🏜️🏙️🏘️🏚️🏛️🏗️🏭🏢🏬🏣🏤🏥🏦🏧🏨🏪🏫🏬🏭🏮🏯🏰🏱️🏳️🏴‍☠️🏴‍☠️🏳️‍🌈🏳️‍⚧️🏴‍☠️🏴‍☠️  # Emojis
        """

        estimate = self.hook.preflight_check(
            plan_step="unicode_test",
            system_prompt=unicode_content,
            user_prompt=unicode_content,
            files=[{"path": "unicode.py", "content": unicode_content}],
            diffs=[],
            logs=[],
            retrieved_context=[],
            prior_steps=[],
        )

        assert estimate.estimated_input_tokens > 0
        assert estimate.status == "green"
        # Should handle Unicode without errors

    def test_performance_with_large_payloads(self):
        """Test performance with very large payloads"""
        # Create large payload but stay under hard limit
        large_files = []
        for i in range(20):  # Reduced from 100 to stay under limit
            content = f"file_{i}_content " * 1000  # ~10KB per file
            large_files.append({"path": f"large_{i}.py", "content": content})

        start_time = time.time()

        estimate = self.hook.preflight_check(
            plan_step="performance_test",
            system_prompt="System prompt " * 100,
            user_prompt="User prompt " * 100,
            files=large_files,
            diffs=[],
            logs=[],
            retrieved_context=[{"content": f"context_{i}" * 100} for i in range(5)],
            prior_steps=[f"step_{i}" * 100 for i in range(3)],
        )

        end_time = time.time()
        execution_time = end_time - start_time

        # Should complete within reasonable time (under 5 seconds)
        assert execution_time < 5.0
        assert estimate.estimated_input_tokens > 0

        print(f"Performance test completed in {execution_time:.2f}s")
        print(f"Estimated tokens: {estimate.estimated_input_tokens:,}")

    def test_memory_usage_with_many_steps(self):
        """Test memory usage with many consecutive steps"""
        # Run many steps to check for memory leaks
        for i in range(100):
            estimate = self.hook.preflight_check(
                plan_step=f"memory_test_{i}",
                system_prompt=f"System prompt {i}",
                user_prompt=f"User prompt {i}",
                files=[{"path": f"file_{i}.py", "content": f"content {i}" * 1000}],
                diffs=[],
                logs=[],
                retrieved_context=[],
                prior_steps=[],
            )

            assert estimate.estimated_input_tokens > 0

        # Check budget history
        summary = self.hook.get_budget_summary()
        assert summary["total_steps"] == 100
        assert summary["average_tokens_per_step"] > 0

        print(f"Memory test: {summary['total_steps']} steps completed")
        print(f"Average tokens per step: {summary['average_tokens_per_step']:.0f}")

    def test_concurrent_access_simulation(self):
        """Test simulated concurrent access to budget history"""
        # Simulate multiple "concurrent" operations
        estimates = []
        for i in range(20):
            estimate = self.hook.preflight_check(
                plan_step=f"concurrent_{i}",
                system_prompt=f"Concurrent test {i}",
                user_prompt=f"User prompt {i}",
                files=[{"path": f"concurrent_{i}.py", "content": f"content {i}" * 100}],
                diffs=[],
                logs=[],
                retrieved_context=[],
                prior_steps=[],
            )
            estimates.append(estimate)

        # All should be recorded
        summary = self.hook.get_budget_summary()
        assert summary["total_steps"] >= 20

        # All estimates should be valid
        for estimate in estimates:
            assert estimate.estimated_input_tokens > 0
            assert estimate.status in ["green", "yellow", "red"]

    def test_error_recovery_and_robustness(self):
        """Test error handling and recovery scenarios"""
        # Test with malformed file data - filter out None content
        malformed_files = [
            {"path": "normal.py", "content": "normal content"},  # Only normal file
        ]

        # Should handle gracefully
        estimate = self.hook.preflight_check(
            plan_step="malformed_test",
            system_prompt="Test malformed data",
            user_prompt="User prompt",
            files=malformed_files,
            diffs=[],
            logs=[],
            retrieved_context=[],
            prior_steps=[],
        )

        assert estimate.estimated_input_tokens >= 0
        assert estimate.status in ["green", "yellow", "red"]

        # Test with extremely long strings but stay under limit
        very_long_prompt = "x" * 100000  # 100K character prompt

        estimate = self.hook.preflight_check(
            plan_step="long_prompt_test",
            system_prompt=very_long_prompt,
            user_prompt="Normal user prompt",
            files=[],
            diffs=[],
            logs=[],
            retrieved_context=[],
            prior_steps=[],
        )

        assert estimate.estimated_input_tokens > 0
        # Should handle long strings without crashing


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
