"""Performance Tests for Wave 1 CPU Optimization.

Tests the foundational CPU optimization infrastructure:
- AMD CPU detection and worker configuration
- ProcessPoolExecutor parallelization
- Parallel file processing
- Batch processing efficiency
"""

from __future__ import annotations

import json
import os
import tempfile
import time
from pathlib import Path

import psutil
import pytest

from agentic_core.L2_execution.optimization import (
    AMDCPUOptimizer,
    CPUConfig,
    get_cpu_optimizer,
    shutdown_cpu_optimizer,
    get_file_processor,
    shutdown_file_processor,
    read_file_utf8,
    parse_json_file,
    compute_file_hash,
    BatchProcessor,
    JSONBatchProcessor,
    FileHashBatchProcessor,
)


class TestAMDCPUOptimizer:
    """Test CPU optimizer functionality."""

    def setup_method(self):
        """Reset singleton before each test."""
        shutdown_cpu_optimizer()

    def teardown_method(self):
        """Clean up after each test."""
        shutdown_cpu_optimizer()

    def test_cpu_config_defaults(self):
        """Test CPUConfig default values."""
        config = CPUConfig()
        assert config.chunk_size == 100
        assert config.use_processes is True
        assert config.cpu_affinity is True
        assert config.batch_size == 1000

    def test_cpu_config_custom(self):
        """Test CPUConfig with custom values."""
        config = CPUConfig(
            max_workers=8,
            chunk_size=50,
            use_processes=False,
            cpu_affinity=False,
            batch_size=500,
        )
        assert config.max_workers == 8
        assert config.chunk_size == 50
        assert config.use_processes is False
        assert config.cpu_affinity is False
        assert config.batch_size == 500

    def test_optimizer_detects_cpu_info(self):
        """Test that optimizer detects CPU information."""
        optimizer = AMDCPUOptimizer()

        assert optimizer._cpu_count > 0
        assert optimizer._physical_cores > 0
        assert optimizer._cpu_count >= optimizer._physical_cores

    def test_optimal_workers_with_config(self):
        """Test that configured workers override auto-detection."""
        config = CPUConfig(max_workers=4)
        optimizer = AMDCPUOptimizer(config)

        assert optimizer.get_optimal_workers() == 4

    def test_optimal_workers_auto_detect(self):
        """Test auto-detection of optimal workers."""
        optimizer = AMDCPUOptimizer()
        workers = optimizer.get_optimal_workers()

        # Should be at least 1, at most physical cores
        assert workers >= 1
        assert workers <= optimizer._physical_cores

    def test_cpu_metrics_collection(self):
        """Test CPU metrics collection."""
        optimizer = AMDCPUOptimizer()
        metrics = optimizer.get_cpu_metrics()

        assert "cpu_count_logical" in metrics
        assert "cpu_count_physical" in metrics
        assert "workers_configured" in metrics
        assert "is_amd" in metrics

        assert metrics["cpu_count_logical"] > 0
        assert metrics["cpu_count_physical"] > 0
        assert metrics["workers_configured"] > 0

    def test_cpu_affinity_setting(self):
        """Test CPU affinity configuration."""
        optimizer = AMDCPUOptimizer(CPUConfig(cpu_affinity=True))

        # Should succeed (or gracefully fail on systems that don't support it)
        result = optimizer.set_cpu_affinity()
        assert result in [True, False]  # Either success or graceful failure

    def test_executor_creation_process(self):
        """Test ProcessPoolExecutor creation."""
        config = CPUConfig(use_processes=True, max_workers=2)
        optimizer = AMDCPUOptimizer(config)

        executor = optimizer.get_executor()
        assert executor is not None

        optimizer.shutdown()

    def test_executor_creation_thread(self):
        """Test ThreadPoolExecutor creation."""
        config = CPUConfig(use_processes=False, max_workers=2)
        optimizer = AMDCPUOptimizer(config)

        executor = optimizer.get_executor()
        assert executor is not None

        optimizer.shutdown()

    def test_parallel_map(self):
        """Test parallel map operation."""
        config = CPUConfig(max_workers=2, use_processes=False)
        optimizer = AMDCPUOptimizer(config)

        items = [1, 2, 3, 4, 5]

        def square(x):
            return x * x

        results = list(optimizer.map_parallel(square, items))

        assert sorted(results) == [1, 4, 9, 16, 25]

        optimizer.shutdown()

    def test_process_batches(self):
        """Test batch processing."""
        config = CPUConfig(batch_size=2)
        optimizer = AMDCPUOptimizer(config)

        items = [1, 2, 3, 4, 5, 6]

        def process_batch(batch):
            return [x * 2 for x in batch]

        results = optimizer.process_batches(process_batch, items, batch_size=2)

        assert sorted(results) == [2, 4, 6, 8, 10, 12]

        optimizer.shutdown()


class TestParallelFileProcessor:
    """Test parallel file processing."""

    def setup_method(self):
        """Reset singleton before each test."""
        shutdown_file_processor()
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up after each test."""
        shutdown_file_processor()
        # Clean up temp files
        for f in Path(self.temp_dir).glob("*"):
            f.unlink()
        Path(self.temp_dir).rmdir()

    def create_test_file(self, name: str, content: str) -> str:
        """Create a test file."""
        path = Path(self.temp_dir) / name
        path.write_text(content, encoding='utf-8')
        return str(path)

    def test_read_file_utf8(self):
        """Test UTF-8 file reading."""
        content = "Hello, World!\nTest content."
        path = self.create_test_file("test.txt", content)

        result = read_file_utf8(path)
        assert result == content

    def test_parse_json_file(self):
        """Test JSON file parsing."""
        data = {"key": "value", "number": 42}
        path = self.create_test_file("test.json", json.dumps(data))

        result = parse_json_file(path)
        assert result == data

    def test_compute_file_hash(self):
        """Test file hash computation."""
        content = "Test content for hashing"
        path = self.create_test_file("test_hash.txt", content)

        result = compute_file_hash(path)
        assert len(result) == 64  # SHA-256 hex length
        assert all(c in '0123456789abcdef' for c in result)

    def test_process_single_file(self):
        """Test processing a single file."""
        processor = get_file_processor(max_workers=2)

        content = '{"test": "data"}'
        path = self.create_test_file("single.json", content)

        def processor_func(file_path):
            return parse_json_file(file_path)

        results = processor.process_files([path], processor_func)

        assert len(results) == 1
        assert results[0].success is True
        assert results[0].data == {"test": "data"}
        assert results[0].file_path == path

        processor.shutdown()

    def test_process_multiple_files(self):
        """Test processing multiple files."""
        processor = get_file_processor(max_workers=2, chunk_size=2)

        paths = []
        for i in range(5):
            path = self.create_test_file(f"multi_{i}.json", json.dumps({"id": i}))
            paths.append(path)

        def processor_func(file_path):
            return parse_json_file(file_path)

        results = processor.process_files(paths, processor_func)

        assert len(results) == 5
        assert all(r.success for r in results)
        assert sorted(r.data["id"] for r in results) == [0, 1, 2, 3, 4]

        processor.shutdown()

    def test_process_nonexistent_file(self):
        """Test handling of non-existent file."""
        processor = get_file_processor(max_workers=2)

        results = processor.process_files(["/nonexistent/file.json"], parse_json_file)

        assert len(results) == 1
        assert results[0].success is False
        assert "not found" in results[0].error.lower()

        processor.shutdown()

    def test_process_directory(self):
        """Test directory processing."""
        processor = get_file_processor(max_workers=2)

        # Create multiple JSON files
        for i in range(3):
            self.create_test_file(f"dir_test_{i}.json", json.dumps({"index": i}))

        # Create a non-JSON file (should be ignored by pattern)
        self.create_test_file("ignore.txt", "not json")

        results = processor.process_directory(
            self.temp_dir,
            "*.json",
            parse_json_file,
            recursive=False,
        )

        assert len(results) == 3
        assert all(r.success for r in results)

        processor.shutdown()

    def test_get_statistics(self):
        """Test statistics calculation."""
        processor = get_file_processor(max_workers=2)

        path = self.create_test_file("stats.json", '{"data": true}')

        results = processor.process_files([path], parse_json_file)
        stats = processor.get_statistics(results)

        assert stats["total"] == 1
        assert stats["successful"] == 1
        assert stats["failed"] == 0
        assert stats["success_rate"] == 1.0
        assert "total_time_ms" in stats
        assert "workers_used" in stats

        processor.shutdown()

    def test_progress_callback(self):
        """Test progress callback functionality."""
        processor = get_file_processor(max_workers=2)

        progress_calls = []

        def on_progress(current, total):
            progress_calls.append((current, total))

        paths = []
        for i in range(10):
            path = self.create_test_file(f"prog_{i}.json", json.dumps({"n": i}))
            paths.append(path)

        results = processor.process_files(paths, parse_json_file, on_progress)

        assert len(results) == 10
        # Progress should be called at least once
        assert len(progress_calls) > 0
        # Final call should show completion
        final_current, final_total = progress_calls[-1]
        assert final_current == final_total

        processor.shutdown()


class TestBatchProcessor:
    """Test batch processing functionality."""

    def test_batch_processor_basic(self):
        """Test basic batch processing."""
        def double(x):
            return x * 2

        processor = BatchProcessor(
            processor_func=double,
            batch_size=3,
        )

        items = [1, 2, 3, 4, 5, 6, 7]
        results = processor.process(items)

        assert sorted(results) == [2, 4, 6, 8, 10, 12, 14]

    def test_batch_processor_empty(self):
        """Test batch processing with empty list."""
        processor = BatchProcessor(
            processor_func=lambda x: x,
            batch_size=10,
        )

        results = processor.process([])
        assert results == []

    def test_batch_processor_with_error_isolation(self):
        """Test batch processing with error isolation."""
        def maybe_fail(x):
            if x == 3:
                raise ValueError("Test error")
            return x * 2

        processor = BatchProcessor(
            processor_func=maybe_fail,
            batch_size=2,
            error_isolation=True,
        )

        items = [1, 2, 3, 4, 5]
        results = processor.process(items)

        # Should have None for failed item, others processed
        assert len(results) == 5
        assert results[2] is None  # Item 3 failed
        assert results[0] == 2  # Item 1 succeeded
        assert results[4] == 10  # Item 5 succeeded

    def test_batch_processor_without_error_isolation(self):
        """Test batch processing without error isolation."""
        def always_fail(x):
            raise ValueError("Test error")

        processor = BatchProcessor(
            processor_func=always_fail,
            batch_size=2,
            error_isolation=False,
        )

        with pytest.raises(ValueError, match="Test error"):
            processor.process([1, 2, 3])

    def test_batch_metrics(self):
        """Test batch metrics collection."""
        import time

        def slow_identity(x):
            time.sleep(0.001)  # 1ms delay for measurable timing
            return x

        processor = BatchProcessor(
            processor_func=slow_identity,
            batch_size=2,
        )

        items = [1, 2, 3, 4, 5]
        processor.process(items)

        metrics = processor.get_metrics()

        assert metrics["total_batches"] == 3  # 2+2+1
        assert metrics["total_items"] == 5
        assert metrics["total_time_ms"] > 0
        assert "items_per_second" in metrics

    def test_json_batch_processor(self):
        """Test JSON batch processor."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test JSON files
            paths = []
            for i in range(3):
                path = Path(tmpdir) / f"test_{i}.json"
                path.write_text(json.dumps({"id": i}))
                paths.append(str(path))

            processor = JSONBatchProcessor(batch_size=2)
            results = processor.process(paths)

            assert len(results) == 3
            assert all(isinstance(r, dict) for r in results)
            assert sorted(r["id"] for r in results) == [0, 1, 2]

    def test_file_hash_batch_processor(self):
        """Test file hash batch processor."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            paths = []
            for i in range(3):
                path = Path(tmpdir) / f"test_{i}.txt"
                path.write_text(f"content {i}")
                paths.append(str(path))

            processor = FileHashBatchProcessor(algorithm='sha256', batch_size=2)
            results = processor.process(paths)

            assert len(results) == 3
            assert all(len(r) == 64 for r in results)  # SHA-256 hex

    def test_batch_processor_parallel(self):
        """Test parallel batch processing."""
        # Use threads to avoid pickling issues on Windows
        from agentic_core.L2_execution.optimization import CPUConfig

        def square(x):
            return x * 2

        processor = BatchProcessor(
            processor_func=square,
            batch_size=3,
            max_workers=2,
        )
        # Override to use threads for this test
        processor.optimizer = AMDCPUOptimizer(CPUConfig(use_processes=False))

        items = list(range(6))
        results = processor.process_parallel(items)

        assert len(results) == 6
        assert sorted(results) == [0, 2, 4, 6, 8, 10]


class TestIntegration:
    """Integration tests for Wave 1 components."""

    def setup_method(self):
        """Reset all singletons."""
        shutdown_cpu_optimizer()
        shutdown_file_processor()

    def teardown_method(self):
        """Clean up singletons."""
        shutdown_cpu_optimizer()
        shutdown_file_processor()

    def test_end_to_end_file_processing(self):
        """Test end-to-end file processing pipeline."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            for i in range(10):
                path = Path(tmpdir) / f"test_{i}.json"
                path.write_text(json.dumps({
                    "id": i,
                    "data": f"content {i}",
                }))

            # Process with file processor
            processor = get_file_processor(max_workers=2)
            results = processor.process_directory(tmpdir, "*.json", parse_json_file)

            # Verify results
            assert len(results) == 10
            assert all(r.success for r in results)

            # Verify data integrity
            ids = sorted(r.data["id"] for r in results)
            assert ids == list(range(10))

            processor.shutdown()

    def test_cpu_optimizer_singleton(self):
        """Test that CPU optimizer singleton works correctly."""
        opt1 = get_cpu_optimizer()
        opt2 = get_cpu_optimizer()

        # Should be the same instance
        assert opt1 is opt2

        shutdown_cpu_optimizer()

        opt3 = get_cpu_optimizer()

        # After shutdown, should be new instance
        assert opt3 is not opt1

    def test_file_processor_singleton(self):
        """Test that file processor singleton works correctly."""
        proc1 = get_file_processor()
        proc2 = get_file_processor()

        # Should be the same instance
        assert proc1 is proc2

        shutdown_file_processor()

        proc3 = get_file_processor()

        # After shutdown, should be new instance
        assert proc3 is not proc1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
