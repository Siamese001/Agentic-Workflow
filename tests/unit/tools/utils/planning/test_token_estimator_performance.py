"""
Performance Tests for Token Planning Estimator

Tests for performance characteristics, scalability, and efficiency
under various load conditions.
"""

import os
import time
from pathlib import Path

import psutil
import pytest


# Lazy imports to avoid collection-time conflicts
@pytest.fixture
def token_estimator_classes():
    from tools.utils.planning.token_estimator import ContextSource, ContextWindowEstimator, TokenEstimate

    return ContextWindowEstimator, ContextSource, TokenEstimate


@pytest.fixture
def planning_preflight_hook(tmp_path):
    from tools.utils.planning.preflight_hook import PlanningPreflightHook

    budget_file = tmp_path / "performance_budget.json"
    return PlanningPreflightHook(budget_file=budget_file)


class TestTokenEstimatorPerformance:
    """Performance tests for the token estimator"""

    def setup_method(self):
        """Setup test fixtures"""
        import tempfile
        import uuid

        from tools.utils.planning.preflight_hook import PlanningPreflightHook

        # Use unique temp directory per test to avoid parallel execution conflicts
        self.temp_dir = Path(tempfile.gettempdir()) / f"test_performance_{uuid.uuid4().hex[:8]}"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.budget_file = self.temp_dir / "performance_budget.json"
        self.hook = PlanningPreflightHook(budget_file=self.budget_file)

        # Get initial memory usage
        self.initial_memory = psutil.Process(os.getpid()).memory_info().rss

    def teardown_method(self):
        """Cleanup test fixtures"""
        import shutil
        import time

        # Wait a moment for file handles to close (Windows)
        time.sleep(0.1)
        if self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            except (
                OSError,
                PermissionError,
            ):  # guardian: allow-silent-swallow -- teardown/cleanup context -- swallow is conventional in resource-release paths
                pass  # Ignore cleanup errors on Windows

    def test_performance_small_payloads(self):
        """Test performance with small payloads"""
        times = []

        for i in range(100):
            start_time = time.time()

            estimate = self.hook.preflight_check(
                plan_step=f"small_test_{i}",
                system_prompt=f"Small prompt {i}",
                user_prompt=f"User prompt {i}",
                files=[{"path": f"small_{i}.py", "content": f"content {i}" * 10}],
                diffs=[],
                logs=[],
                retrieved_context=[],
                prior_steps=[],
            )

            end_time = time.time()
            times.append(end_time - start_time)

            assert estimate.total_projected_tokens < 50000  # Should be small
            assert estimate.status == "green"

        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)

        # Performance assertions
        assert avg_time < 0.01, f"Average time too high: {avg_time:.4f}s"
        assert max_time < 0.05, f"Max time too high: {max_time:.4f}s"

        print(f"Small payloads: avg={avg_time:.4f}s, min={min_time:.4f}s, max={max_time:.4f}s")

    def test_performance_medium_payloads(self):
        """Test performance with medium payloads"""
        times = []

        for i in range(50):
            # Create medium-sized payload
            files = []
            for j in range(10):
                content = f"File {i}-{j} content " * 100
                files.append({"path": f"medium_{i}_{j}.py", "content": content})

            start_time = time.time()

            estimate = self.hook.preflight_check(
                plan_step=f"medium_test_{i}",
                system_prompt=f"Medium prompt {i} " * 50,
                user_prompt=f"User prompt {i} " * 50,
                files=files,
                diffs=[],
                logs=[],
                retrieved_context=[{"content": f"Context {i} " * 100}],
                prior_steps=[f"Prior step {i} " * 50],
            )

            end_time = time.time()
            times.append(end_time - start_time)

            assert estimate.total_projected_tokens < 150000  # Should be medium

        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)

        # Performance assertions
        assert avg_time < 0.05, f"Average time too high: {avg_time:.4f}s"
        assert max_time < 0.1, f"Max time too high: {max_time:.4f}s"

        print(f"Medium payloads: avg={avg_time:.4f}s, min={min_time:.4f}s, max={max_time:.4f}s")

    def test_performance_large_payloads(self):
        """Test performance with large payloads"""
        times = []

        for i in range(20):
            # Create large-sized payload
            files = []
            for j in range(25):
                content = f"Large file {i}-{j} content " * 500
                files.append({"path": f"large_{i}_{j}.py", "content": content})

            start_time = time.time()

            estimate = self.hook.preflight_check(
                plan_step=f"large_test_{i}",
                system_prompt=f"Large prompt {i} " * 200,
                user_prompt=f"User prompt {i} " * 200,
                files=files,
                diffs=[{"path": f"diff_{i}.md", "content": f"Diff content {i} " * 1000}],
                logs=[{"source": f"log_{i}.log", "content": f"Log content {i} " * 500}],
                retrieved_context=[{"content": f"Context {i} " * 300} for _ in range(5)],
                prior_steps=[f"Prior step {i} " * 200 for _ in range(3)],
            )

            end_time = time.time()
            times.append(end_time - start_time)

            # Should handle large payloads efficiently
            assert estimate.total_projected_tokens < 200000  # Should be under hard limit

        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)

        # Performance assertions for large payloads
        assert avg_time < 0.2, f"Average time too high: {avg_time:.4f}s"
        assert max_time < 0.5, f"Max time too high: {max_time:.4f}s"

        print(f"Large payloads: avg={avg_time:.4f}s, min={min_time:.4f}s, max={max_time:.4f}s")

    def test_memory_usage_scaling(self):
        """Test memory usage scales appropriately"""
        memory_readings = []

        # Test with increasing payload sizes but stay under hard limit
        for size_factor in [1, 3, 5, 7, 10]:  # Reduced factors to stay under limit
            # Create payload based on size factor
            files = []
            for i in range(size_factor):
                content = f"Memory test file {i} " * (50 * size_factor)  # Reduced content size
                files.append({"path": f"memory_{i}.py", "content": content})

            # Measure memory before
            memory_before = psutil.Process(os.getpid()).memory_info().rss

            estimate = self.hook.preflight_check(
                plan_step=f"memory_test_{size_factor}",
                system_prompt=f"Memory test prompt {size_factor}",
                user_prompt=f"Memory test user {size_factor}",
                files=files,
                diffs=[],
                logs=[],
                retrieved_context=[],
                prior_steps=[],
            )

            # Measure memory after
            memory_after = psutil.Process(os.getpid()).memory_info().rss
            memory_used = memory_after - memory_before
            memory_readings.append((size_factor, memory_used, estimate.total_projected_tokens))

            # Memory shouldn't grow excessively
            memory_mb = memory_used / (1024 * 1024)
            assert memory_mb < 50, f"Memory usage too high: {memory_mb:.2f}MB for size factor {size_factor}"

        # Check memory scaling is reasonable
        print("Memory usage scaling:")
        for factor, memory_used, tokens in memory_readings:
            memory_mb = memory_used / (1024 * 1024)
            print(f"  Size factor {factor}: {memory_mb:.2f}MB, {tokens:,} tokens")

    def test_compression_performance(self):
        """Test compression performance with large payloads"""
        from tools.utils.planning.token_estimator import ContextSource, ContextWindowEstimator, TokenEstimate

        estimator = ContextWindowEstimator()

        # Create sources that will trigger compression
        large_sources = [
            ContextSource("file", "x" * 50000, 17500, metadata={"path": "large.py", "lines": 5000}),
            ContextSource("log", "ERROR: Error\n" * 1000, 5000, metadata={"source": "large.log"}),
            ContextSource(
                "retrieval",
                "".join(f"chunk_{i}" * 1000 for i in range(30)),
                15000,
                metadata={"chunk_id": "chunk_0"},
            ),
        ]

        estimate = TokenEstimate(
            plan_step="compression_test",
            estimated_input_tokens=37500,
            reserved_output_tokens=12000,
            safety_buffer_tokens=8000,
            total_projected_tokens=57500,
            status="yellow",
            action="compress",
            top_contributors=[],
            recommended_reductions=[],
        )

        # Test compression performance
        times = []
        for i in range(50):
            start_time = time.time()
            compressed_estimate = estimator._apply_compression(estimate, large_sources)
            end_time = time.time()
            times.append(end_time - start_time)

        avg_time = sum(times) / len(times)
        max_time = max(times)

        # Compression should be fast
        assert avg_time < 0.01, f"Compression average time too high: {avg_time:.4f}s"
        assert max_time < 0.05, f"Compression max time too high: {max_time:.4f}s"

        print(f"Compression performance: avg={avg_time:.4f}s, max={max_time:.4f}s")

    def test_budget_history_performance(self):
        """Test budget history performance with many entries"""
        # Add many entries to budget history
        times = []

        for i in range(200):
            start_time = time.time()

            estimate = self.hook.preflight_check(
                plan_step=f"history_test_{i}",
                system_prompt=f"History test {i}",
                user_prompt=f"User prompt {i}",
                files=[{"path": f"history_{i}.py", "content": f"content {i}" * 50}],
                diffs=[],
                logs=[],
                retrieved_context=[],
                prior_steps=[],
            )

            end_time = time.time()
            times.append(end_time - start_time)

        # Test summary generation performance
        start_time = time.time()
        summary = self.hook.get_budget_summary()
        end_time = time.time()
        summary_time = end_time - start_time

        # Test history clearing performance
        start_time = time.time()
        self.hook.clear_history()
        end_time = time.time()
        clear_time = end_time - start_time

        # Performance assertions
        avg_time = sum(times) / len(times)
        assert avg_time < 0.02, f"Average preflight time too high: {avg_time:.4f}s"
        assert summary_time < 0.1, f"Summary generation too slow: {summary_time:.4f}s"
        assert clear_time < 0.05, f"History clearing too slow: {clear_time:.4f}s"

        print(
            f"History performance: avg_preflight={avg_time:.4f}s, summary={summary_time:.4f}s, clear={clear_time:.4f}s"
        )
        print(f"History entries: {summary['total_steps']}")

    def test_concurrent_performance_simulation(self):
        """Test performance under simulated concurrent load"""
        # Simulate many operations happening in quick succession
        results = []
        times = []

        for i in range(100):
            start_time = time.time()

            # Vary the payload size
            file_count = (i % 10) + 1
            files = []
            for j in range(file_count):
                content = f"Concurrent test {i}-{j} " * (50 + i)
                files.append({"path": f"concurrent_{i}_{j}.py", "content": content})

            estimate = self.hook.preflight_check(
                plan_step=f"concurrent_perf_{i}",
                system_prompt=f"Concurrent test {i}",
                user_prompt=f"User prompt {i}",
                files=files,
                diffs=[],
                logs=[],
                retrieved_context=[{"content": f"Context {i}"}],
                prior_steps=[],
            )

            end_time = time.time()
            times.append(end_time - start_time)
            results.append(estimate)

        # Analyze performance
        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]

        # Performance assertions
        assert avg_time < 0.05, f"Average time too high: {avg_time:.4f}s"
        assert max_time < 0.2, f"Max time too high: {max_time:.4f}s"
        assert p95_time < 0.1, f"95th percentile time too high: {p95_time:.4f}s"

        # All estimates should be valid
        assert all(e.total_projected_tokens < 200000 for e in results)
        assert all(e.status in ["green", "yellow"] for e in results)

        print(
            f"Concurrent performance: avg={avg_time:.4f}s, min={min_time:.4f}s, max={max_time:.4f}s, p95={p95_time:.4f}s"
        )

    def test_token_estimation_performance(self):
        """Test raw token estimation performance"""
        from tools.utils.planning.token_estimator import ContextWindowEstimator

        estimator = ContextWindowEstimator()

        # Test different content types and sizes
        test_cases = [
            ("small_code", "def hello():\n    return 'world'", "code"),
            ("medium_text", "This is a medium text " * 100, "text"),
            ("large_json", '{"key": "' + "value" * 1000 + '"}', "json"),
            (
                "mixed_content",
                "Code: def test()\nText: " + "text " * 500 + '\nJSON: {"data": ' + "x" * 200 + "}",
                "auto",
            ),
        ]

        times = []

        for name, content, content_type in test_cases:
            start_time = time.time()

            for i in range(100):  # Run each test multiple times
                tokens = estimator._estimate_tokens(content, content_type)
                assert tokens > 0

            end_time = time.time()
            avg_case_time = (end_time - start_time) / 100
            times.append((name, avg_case_time))

        # Token estimation should be very fast
        for name, avg_time in times:
            assert avg_time < 0.001, f"Token estimation too slow for {name}: {avg_time:.6f}s"
            print(f"Token estimation {name}: {avg_time:.6f}s per call")

    def test_scalability_with_file_count(self):
        """Test scalability with increasing number of files"""
        file_counts = [1, 5, 10, 25, 50, 100]
        times = []

        for file_count in file_counts:
            files = []
            for i in range(file_count):
                content = f"Scalability test file {i} " * 100
                files.append({"path": f"scale_{i}.py", "content": content})

            start_time = time.time()

            estimate = self.hook.preflight_check(
                plan_step=f"scale_test_{file_count}",
                system_prompt="Scalability test",
                user_prompt="Test scalability",
                files=files,
                diffs=[],
                logs=[],
                retrieved_context=[],
                prior_steps=[],
            )

            end_time = time.time()
            elapsed = end_time - start_time
            times.append((file_count, elapsed, estimate.total_projected_tokens))

        # Check that time scales reasonably
        print("Scalability with file count:")
        for file_count, elapsed, tokens in times:
            print(f"  {file_count:3d} files: {elapsed:.4f}s, {tokens:,} tokens")

        # Time should scale sub-linearly
        time_1 = next((t for f, t, _ in times if f == 1), None)
        time_100 = next((t for f, t, _ in times if f == 100), None)

        if time_1 is not None and time_100 is not None and time_1 > 0:
            # 100x files shouldn't take 100x time (should be much better due to batching)
            scaling_factor = time_100 / time_1
            assert scaling_factor < 50, f"Poor scaling: {scaling_factor:.1f}x for 100x files"
            print(f"Scaling factor: {scaling_factor:.1f}x for 100x files")
        else:
            print("Skipping scaling test due to timing issues")

    def test_memory_leak_detection(self):
        """Test for memory leaks with repeated operations"""
        initial_memory = psutil.Process(os.getpid()).memory_info().rss
        memory_readings = [initial_memory]

        # Run many operations
        for i in range(10):
            for j in range(50):
                estimate = self.hook.preflight_check(
                    plan_step=f"leak_test_{i}_{j}",
                    system_prompt=f"Leak test {i} {j}",
                    user_prompt=f"User prompt {i} {j}",
                    files=[{"path": f"leak_{i}_{j}.py", "content": f"content {i} {j}" * 50}],
                    diffs=[],
                    logs=[],
                    retrieved_context=[],
                    prior_steps=[],
                )

            # Measure memory after each batch
            current_memory = psutil.Process(os.getpid()).memory_info().rss
            memory_readings.append(current_memory)

        # Check for memory leaks
        memory_growth = memory_readings[-1] - memory_readings[0]
        memory_growth_mb = memory_growth / (1024 * 1024)

        # Memory growth should be reasonable
        assert memory_growth_mb < 20, f"Potential memory leak: {memory_growth_mb:.2f}MB growth"

        print(f"Memory leak test: {memory_growth_mb:.2f}MB growth over 500 operations")

        # Clear history and check memory is freed
        self.hook.clear_history()
        final_memory = psutil.Process(os.getpid()).memory_info().rss
        memory_after_clear = final_memory - memory_readings[0]
        memory_after_clear_mb = memory_after_clear / (1024 * 1024)

        print(f"Memory after clear: {memory_after_clear_mb:.2f}MB from initial")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
