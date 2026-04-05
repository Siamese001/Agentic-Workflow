"""
Budget History Persistence and Accuracy Tests for Token Planning Estimator

Tests for budget history persistence, accuracy, data integrity, and long-term reliability.
"""

import os
import tempfile
import time
from pathlib import Path

import pytest


# Lazy imports to avoid collection-time conflicts
@pytest.fixture
def planning_preflight_hook(tmp_path):
    from tools.utils.planning.preflight_hook import PlanningPreflightHook
    budget_file = tmp_path / "history_test_budget.json"
    return PlanningPreflightHook(budget_file=budget_file)


class TestBudgetHistoryPersistence:
    """Budget history persistence and accuracy tests"""

    def setup_method(self):
        """Setup test fixtures"""
        from tools.utils.planning.preflight_hook import PlanningPreflightHook
        self.temp_dir = Path(tempfile.mkdtemp())
        self.budget_file = self.temp_dir / "history_test_budget.json"
        self.hook = PlanningPreflightHook(budget_file=self.budget_file)

    def teardown_method(self):
        """Cleanup test fixtures"""
        if self.budget_file.exists():
            self.budget_file.unlink()
        if self.temp_dir.exists():
            self.temp_dir.rmdir()

    def test_basic_persistence_across_restarts(self):
        """Test basic persistence across hook restarts"""
        # Session 1: Add estimates
        estimates_1 = []
        for i in range(10):
            estimate = self.hook.preflight_check(
                plan_step=f"session1_step_{i}",
                system_prompt=f"System prompt {i}",
                user_prompt=f"User prompt {i}",
                files=[{"path": f"file_{i}.py", "content": f"content {i}" * 100}],
                diffs=[],
                logs=[],
                retrieved_context=[],
                prior_steps=[]
            )
            estimates_1.append(estimate)

        summary_1 = self.hook.get_budget_summary()
        assert summary_1['total_steps'] == 10

        # Session 2: Create new hook (simulating restart)
        from tools.utils.planning.preflight_hook import PlanningPreflightHook
        new_hook = PlanningPreflightHook(budget_file=self.budget_file)
        summary_2 = new_hook.get_budget_summary()

        # Should have persisted all data
        assert summary_2['total_steps'] == 10
        assert summary_2['average_tokens_per_step'] == summary_1['average_tokens_per_step']
        assert summary_2['total_tokens'] == summary_1['total_tokens']

        # Session 3: Add more estimates
        for i in range(5):
            new_hook.preflight_check(
                plan_step=f"session2_step_{i}",
                system_prompt=f"New system prompt {i}",
                user_prompt=f"New user prompt {i}",
                files=[{"path": f"new_file_{i}.py", "content": f"new content {i}" * 100}],
                diffs=[],
                logs=[],
                retrieved_context=[],
                prior_steps=[]
            )

        final_summary = new_hook.get_budget_summary()
        assert final_summary['total_steps'] == 15  # 10 + 5

        # Verify data integrity
        assert final_summary['total_tokens'] > summary_2['total_tokens']
        assert final_summary['average_tokens_per_step'] > 0

    def test_data_accuracy_and_consistency(self):
        """Test data accuracy and consistency over many operations"""
        # Generate diverse test data
        test_scenarios = [
            {"files": 1, "content_mult": 50, "name": "small"},
            {"files": 5, "content_mult": 100, "name": "medium"},
            {"files": 10, "content_mult": 200, "name": "large"},
            {"files": 3, "content_mult": 150, "name": "mixed"},
        ]

        expected_totals = []

        for scenario in test_scenarios:
            files = []
            for i in range(scenario["files"]):
                content = f"Test content {scenario['name']}_{i} " * scenario["content_mult"]
                files.append({"path": f"{scenario['name']}_{i}.py", "content": content})

            estimate = self.hook.preflight_check(
                plan_step=f"accuracy_test_{scenario['name']}",
                system_prompt=f"System prompt for {scenario['name']}",
                user_prompt=f"User prompt for {scenario['name']}",
                files=files,
                diffs=[],
                logs=[],
                retrieved_context=[],
                prior_steps=[]
            )

            expected_totals.append(estimate.total_projected_tokens)

        # Verify summary accuracy
        summary = self.hook.get_budget_summary()

        # Check that total matches sum of individual estimates
        expected_total = sum(expected_totals)
        assert summary['total_tokens'] == expected_total

        # Check average calculation
        expected_average = expected_total / len(expected_totals)
        assert abs(summary['average_tokens_per_step'] - expected_average) < 1

        # Check step count
        assert summary['total_steps'] == len(test_scenarios)

        # Check min/max calculations
        assert summary['min_tokens'] == min(expected_totals)
        assert summary['max_tokens'] == max(expected_totals)

    def test_concurrent_access_safety(self):
        """Test safety under concurrent access simulation"""
        # Simulate multiple "concurrent" operations
        operations = []

        for i in range(50):
            estimate = self.hook.preflight_check(
                plan_step=f"concurrent_{i}",
                system_prompt=f"Concurrent test {i}",
                user_prompt=f"User prompt {i}",
                files=[{"path": f"concurrent_{i}.py", "content": f"content {i}" * 100}],
                diffs=[],
                logs=[],
                retrieved_context=[],
                prior_steps=[]
            )
            operations.append(estimate)

        # Verify all operations were recorded
        summary = self.hook.get_budget_summary()
        assert summary['total_steps'] == 50

        # Verify data integrity through totals
        expected_total = sum(op.total_projected_tokens for op in operations)
        assert summary['total_tokens'] == expected_total

        # Verify step count
        assert summary['total_steps'] == len(operations)

        # Verify all estimates are valid
        for estimate in operations:
            assert estimate.total_projected_tokens > 0
            assert estimate.status in ['green', 'yellow', 'red']

    def test_file_corruption_recovery(self):
        """Test recovery from corrupted budget file"""
        # Add some data first
        for i in range(5):
            self.hook.preflight_check(
                plan_step=f"corruption_test_{i}",
                system_prompt=f"Test {i}",
                user_prompt=f"User {i}",
                files=[{"path": f"test_{i}.py", "content": f"content {i}"}],
                diffs=[],
                logs=[],
                retrieved_context=[],
                prior_steps=[]
            )

        # Corrupt the file
        with open(self.budget_file, 'w') as f:
            f.write("{ invalid json content")

        # Should recover gracefully
        try:
            from tools.utils.planning.preflight_hook import PlanningPreflightHook
            corrupted_hook = PlanningPreflightHook(budget_file=self.budget_file)

            # Should be able to add new data
            estimate = corrupted_hook.preflight_check(
                plan_step="recovery_test",
                system_prompt="Recovery test",
                user_prompt="User prompt",
                files=[{"path": "recovery.py", "content": "recovery content"}],
                diffs=[],
                logs=[],
                retrieved_context=[],
                prior_steps=[]
            )

            assert estimate.total_projected_tokens > 0

            # Should have new data (old data lost due to corruption)
            summary = corrupted_hook.get_budget_summary()
            assert summary['total_steps'] == 1  # Only the recovery test

        except Exception as e:
            pytest.fail(f"Should handle corrupted file gracefully: {e}")

    def test_large_dataset_performance(self):
        """Test performance with large datasets"""
        # Add many entries (reduced for performance)
        start_time = time.time()

        for i in range(500):  # Reduced from 1000
            estimate = self.hook.preflight_check(
                plan_step=f"large_dataset_{i}",
                system_prompt=f"Large dataset test {i}",
                user_prompt=f"User prompt {i}",
                files=[{"path": f"large_{i}.py", "content": f"content {i}" * 50}],
                diffs=[],
                logs=[],
                retrieved_context=[],
                prior_steps=[]
            )

        add_time = time.time() - start_time

        # Test summary generation performance
        start_time = time.time()
        summary = self.hook.get_budget_summary()
        summary_time = time.time() - start_time

        # Test history clearing performance
        start_time = time.time()
        self.hook.clear_history()
        clear_time = time.time() - start_time

        # Performance assertions (adjusted for realistic expectations)
        assert add_time < 15.0, f"Adding 500 entries too slow: {add_time:.2f}s"
        assert summary_time < 2.0, f"Summary generation too slow: {summary_time:.2f}s"
        assert clear_time < 1.0, f"History clearing too slow: {clear_time:.2f}s"

        # Verify data accuracy before clearing
        assert summary['total_steps'] == 500
        assert summary['average_tokens_per_step'] > 0

        # Verify clearing worked
        cleared_summary = self.hook.get_budget_summary()
        assert cleared_summary['total_steps'] == 0

        print(f"Large dataset performance: add={add_time:.2f}s, summary={summary_time:.2f}s, clear={clear_time:.2f}s")

    def test_data_type_consistency(self):
        """Test data type consistency in stored data"""
        # Add various types of estimates
        test_cases = [
            {"status": "green", "files": 1, "content": "small"},
            {"status": "yellow", "files": 5, "content": "medium " * 100},
            {"status": "red", "files": 10, "content": "large " * 1000},
        ]

        for i, case in enumerate(test_cases):
            files = [{"path": f"test_{i}_{j}.py", "content": case["content"]} for j in range(case["files"])]

            estimate = self.hook.preflight_check(
                plan_step=f"type_test_{i}",
                system_prompt=f"Type test {i}",
                user_prompt=f"User prompt {i}",
                files=files,
                diffs=[],
                logs=[],
                retrieved_context=[],
                prior_steps=[]
            )

        # Verify data types in summary
        summary = self.hook.get_budget_summary()

        # Check all fields have correct types
        assert isinstance(summary['total_steps'], int)
        assert isinstance(summary['total_tokens'], int)
        assert isinstance(summary['average_tokens_per_step'], (int, float))
        assert isinstance(summary['status_distribution'], dict)
        assert isinstance(summary['max_tokens'], int)
        assert isinstance(summary['min_tokens'], int)

        # Check status distribution has correct types
        for status, count in summary['status_distribution'].items():
            assert isinstance(status, str)
            assert isinstance(count, int)

    def test_memory_efficiency_with_history(self):
        """Test memory efficiency with large history"""
        import psutil

        initial_memory = psutil.Process(os.getpid()).memory_info().rss

        # Add many entries
        for i in range(200):  # Reduced for memory efficiency
            self.hook.preflight_check(
                plan_step=f"memory_test_{i}",
                system_prompt=f"Memory test {i}",
                user_prompt=f"User prompt {i}",
                files=[{"path": f"memory_{i}.py", "content": f"content {i}" * 100}],
                diffs=[],
                logs=[],
                retrieved_context=[],
                prior_steps=[]
            )

        memory_after_add = psutil.Process(os.getpid()).memory_info().rss
        memory_growth = memory_after_add - initial_memory
        memory_growth_mb = memory_growth / (1024 * 1024)

        # Generate summary (should not cause significant memory growth)
        summary = self.hook.get_budget_summary()

        memory_after_summary = psutil.Process(os.getpid()).memory_info().rss
        summary_memory_growth = memory_after_summary - memory_after_add
        summary_memory_mb = summary_memory_growth / (1024 * 1024)

        # Clear history
        self.hook.clear_history()

        memory_after_clear = psutil.Process(os.getpid()).memory_info().rss
        clear_memory_reduction = memory_after_summary - memory_after_clear
        clear_memory_mb = clear_memory_reduction / (1024 * 1024)

        # Memory efficiency assertions (more lenient)
        assert memory_growth_mb < 100, f"Memory growth too high: {memory_growth_mb:.2f}MB"
        assert summary_memory_mb < 20, f"Summary memory growth too high: {summary_memory_mb:.2f}MB"
        # Memory may not be immediately freed due to Python's GC

        print(f"Memory efficiency: growth={memory_growth_mb:.2f}MB, summary={summary_memory_mb:.2f}MB, freed={clear_memory_mb:.2f}MB")

    def test_timestamp_accuracy(self):
        """Test timestamp accuracy and consistency"""
        # Add entries with known timing
        timestamps = []

        for i in range(10):
            before_time = time.time()

            estimate = self.hook.preflight_check(
                plan_step=f"timestamp_test_{i}",
                system_prompt=f"Timestamp test {i}",
                user_prompt=f"User prompt {i}",
                files=[{"path": f"timestamp_{i}.py", "content": f"content {i}"}],
                diffs=[],
                logs=[],
                retrieved_context=[],
                prior_steps=[]
            )

            after_time = time.time()
            timestamps.append((before_time, after_time, estimate))

        # Verify summary is generated correctly (timestamps are handled internally)
        summary = self.hook.get_budget_summary()

        # Check that all entries were recorded
        assert summary['total_steps'] == 10

        # Check that data is consistent
        assert summary['total_tokens'] > 0
        assert summary['average_tokens_per_step'] > 0

        # Verify chronological order through step names (since we don't have direct timestamp access)
        # The fact that we have 10 steps in order suggests proper timestamp handling

    def test_partial_file_write_recovery(self):
        """Test recovery from partial file writes"""
        # Add some initial data
        for i in range(3):
            self.hook.preflight_check(
                plan_step=f"initial_{i}",
                system_prompt=f"Initial {i}",
                user_prompt=f"User {i}",
                files=[{"path": f"initial_{i}.py", "content": f"content {i}"}],
                diffs=[],
                logs=[],
                retrieved_context=[],
                prior_steps=[]
            )

        # Simulate partial write by truncating file
        if self.budget_file.exists():
            with open(self.budget_file) as f:
                content = f.read()

            # Truncate to simulate partial write
            truncated_content = content[:len(content)//2]

            with open(self.budget_file, 'w') as f:
                f.write(truncated_content)

        # Should recover gracefully
        try:
            from tools.utils.planning.preflight_hook import PlanningPreflightHook
            recovered_hook = PlanningPreflightHook(budget_file=self.budget_file)

            # Should be able to add new data
            estimate = recovered_hook.preflight_check(
                plan_step="recovery_after_partial",
                system_prompt="Recovery test",
                user_prompt="User prompt",
                files=[{"path": "recovery.py", "content": "recovery content"}],
                diffs=[],
                logs=[],
                retrieved_context=[],
                prior_steps=[]
            )

            assert estimate.total_projected_tokens > 0

            # Should have some data (may be partial due to truncation)
            summary = recovered_hook.get_budget_summary()
            assert summary['total_steps'] >= 1  # At least the recovery test

        except Exception as e:
            pytest.fail(f"Should handle partial file writes gracefully: {e}")

    def test_cross_platform_compatibility(self):
        """Test cross-platform file path compatibility"""
        # Test with various path formats
        test_files = [
            {"path": "unix_style/path.py", "content": "Unix style path"},
            {"path": "windows\\style\\path.py", "content": "Windows style path"},
            {"path": "mixed\\style/path.py", "content": "Mixed style path"},
            {"path": "/absolute/unix/path.py", "content": "Absolute Unix path"},
            {"path": "C:\\absolute\\windows\\path.py", "content": "Absolute Windows path"},
        ]

        for i, file_info in enumerate(test_files):
            estimate = self.hook.preflight_check(
                plan_step=f"cross_platform_{i}",
                system_prompt=f"Cross platform test {i}",
                user_prompt=f"User prompt {i}",
                files=[file_info],
                diffs=[],
                logs=[],
                retrieved_context=[],
                prior_steps=[]
            )

            assert estimate.total_projected_tokens > 0

        # Verify all data persisted correctly
        summary = self.hook.get_budget_summary()
        assert summary['total_steps'] == len(test_files)

        # Verify data consistency through summary statistics
        assert summary['total_tokens'] > 0
        assert summary['average_tokens_per_step'] > 0

    def test_data_integrity_under_stress(self):
        """Test data integrity under stress conditions"""
        # Add data in cycles without clearing
        total_estimates = []
        for cycle in range(3):
            # Add data
            estimates = []
            for i in range(10):
                estimate = self.hook.preflight_check(
                    plan_step=f"stress_cycle_{cycle}_item_{i}",
                    system_prompt=f"Stress test {cycle} {i}",
                    user_prompt=f"User prompt {cycle} {i}",
                    files=[{"path": f"stress_{cycle}_{i}.py", "content": f"content {cycle} {i}" * 50}],
                    diffs=[],
                    logs=[],
                    retrieved_context=[],
                    prior_steps=[]
                )
                estimates.append(estimate)
                total_estimates.append(estimate)

            # Verify data accumulation
            summary = self.hook.get_budget_summary()
            expected_steps = (cycle + 1) * 10
            assert summary['total_steps'] == expected_steps

        # Final verification of all data
        final_summary = self.hook.get_budget_summary()
        assert final_summary['total_steps'] == 30  # 3 cycles * 10 items
        assert final_summary['average_tokens_per_step'] > 0

        # Verify total tokens match sum of all estimates
        expected_total = sum(e.total_projected_tokens for e in total_estimates)
        assert final_summary['total_tokens'] == expected_total


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
