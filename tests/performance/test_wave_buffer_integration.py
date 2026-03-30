"""Integration Tests for CPU Optimization Waves 1-5.

End-to-end tests validating the complete CPU optimization stack.
"""

from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

import pytest

from agentic_core.L2_execution.optimization import (
    get_cpu_optimizer,
    get_file_processor,
    BatchProcessor,
    shutdown_cpu_optimizer,
    shutdown_file_processor,
)
from agentic_core.adg.extraction.parallel_scanner import (
    get_parallel_scanner,
    shutdown_parallel_scanner,
)
from agentic_core.adg.extraction.batch_operations import ADGSQLiteBatchInserter
from agentic_core.adg.extraction.parallel_report_generator import (
    get_report_generator,
    shutdown_report_generator,
    create_report_tasks,
)


class TestCPUOptimizationIntegration:
    """Integration tests for full CPU optimization stack."""
    
    def setup_method(self):
        """Reset all singletons."""
        shutdown_cpu_optimizer()
        shutdown_file_processor()
        shutdown_parallel_scanner()
        shutdown_report_generator()
    
    def teardown_method(self):
        """Clean up."""
        shutdown_cpu_optimizer()
        shutdown_file_processor()
        shutdown_parallel_scanner()
        shutdown_report_generator()
    
    def test_end_to_end_parallel_pipeline(self):
        """Test complete parallel processing pipeline."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 1. Create test files
            test_dir = Path(tmpdir) / "modules"
            test_dir.mkdir()
            
            for i in range(20):
                path = test_dir / f"module_{i}.py"
                path.write_text(f"def func_{i}(): pass")
            
            # 2. Process files in parallel
            processor = get_file_processor(max_workers=4)
            
            def count_lines(file_path: str) -> int:
                with open(file_path) as f:
                    return len(f.readlines())
            
            results = processor.process_directory(str(test_dir), "*.py", count_lines)
            
            assert len(results) == 20
            assert all(r.success for r in results)
            
            # 3. Batch process results
            batch_proc = BatchProcessor(
                processor_func=lambda x: x * 2,
                batch_size=5,
                max_workers=2,
            )
            
            line_counts = [r.data for r in results if r.success]
            doubled = batch_proc.process(line_counts)
            
            assert len(doubled) == 20
            
            # 4. Write to SQLite
            db_path = Path(tmpdir) / "results.db"
            conn = sqlite3.connect(str(db_path))
            conn.execute("""
                CREATE TABLE results (id INTEGER PRIMARY KEY, line_count INTEGER, doubled INTEGER)
            """)
            conn.commit()
            conn.close()
            
            with ADGSQLiteBatchInserter(str(db_path), batch_size=10) as inserter:
                for i, (count, dbl) in enumerate(zip(line_counts, doubled)):
                    inserter.add_node({
                        "adg_name": f"result_{i}",
                        "entity_type": "test_result",
                        "layer": "L0",
                        "identity_kind": "result",
                        "confidence": 1.0,
                        "resolved_path": str(test_dir / f"module_{i}.py"),
                    })
            
            # Verify
            conn = sqlite3.connect(str(db_path))
            cursor = conn.execute("SELECT COUNT(*) FROM nodes")
            count = cursor.fetchone()[0]
            conn.close()
            
            assert count == 20
    
    def test_cpu_optimizer_metrics(self):
        """Test CPU optimizer provides accurate metrics."""
        optimizer = get_cpu_optimizer()
        metrics = optimizer.get_cpu_metrics()
        
        assert "cpu_count_logical" in metrics
        assert "cpu_count_physical" in metrics
        assert "workers_configured" in metrics
        assert "is_amd" in metrics
        
        assert metrics["cpu_count_logical"] > 0
        assert metrics["cpu_count_physical"] > 0
        assert metrics["workers_configured"] > 0
    
    def test_parallel_scanner_integration(self):
        """Test parallel scanner with real files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create Python files
            for i in range(10):
                path = Path(tmpdir) / f"test_{i}.py"
                path.write_text(f"# Module {i}\nclass Class{i}:\n    pass")
            
            scanner = get_parallel_scanner(max_workers=2)
            
            # Scan directory
            results = scanner.scan_directory_parallel(tmpdir, "*.py")
            
            assert len(results) == 10
            
            # Get metrics
            metrics = scanner.get_metrics()
            assert metrics["total_modules"] == 10
            
            scanner.shutdown()
    
    def test_report_generation_pipeline(self):
        """Test report generation pipeline."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test database
            db_path = Path(tmpdir) / "test.db"
            conn = sqlite3.connect(str(db_path))
            conn.executescript("""
                CREATE TABLE nodes (id INTEGER PRIMARY KEY, adg_name TEXT, layer TEXT);
                CREATE TABLE edges (id INTEGER PRIMARY KEY, src_id TEXT, dst_id TEXT);
                INSERT INTO nodes VALUES (1, 'node1', 'L0'), (2, 'node2', 'L1');
                INSERT INTO edges VALUES (1, 'node1', 'node2');
            """)
            conn.commit()
            conn.close()
            
            # Create report tasks
            reports_dir = Path(tmpdir) / "reports"
            tasks = create_report_tasks(
                db_path=str(db_path),
                reports_dir=reports_dir,
                timestamp="20260330",
            )
            
            assert len(tasks) >= 2  # layer_coverage + edge_density
            
            # Generate reports
            generator = get_report_generator(max_workers=2)
            results = generator.generate_reports_parallel(tasks)
            
            assert len(results) == len(tasks)
            assert all(r.success for r in results)
            
            # Verify files created
            for result in results:
                assert result.output_path.exists()
            
            generator.shutdown()


class TestPerformanceBenchmarks:
    """Performance benchmark tests."""
    
    def test_batch_processing_throughput(self):
        """Measure batch processing throughput."""
        import time
        
        def process_item(x):
            # Simulate work
            total = 0
            for i in range(100):
                total += i * x
            return total
        
        processor = BatchProcessor(
            processor_func=process_item,
            batch_size=100,
            max_workers=4,
        )
        
        items = list(range(1000))
        
        start = time.time()
        results = processor.process(items)
        elapsed = time.time() - start
        
        assert len(results) == 1000
        
        # Should complete in reasonable time (< 5 seconds)
        assert elapsed < 5.0
        
        metrics = processor.get_metrics()
        assert metrics["items_per_second"] > 100  # At least 100 items/sec
    
    def test_file_processing_throughput(self):
        """Measure file processing throughput."""
        import time
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create many small files
            for i in range(100):
                path = Path(tmpdir) / f"file_{i}.txt"
                path.write_text(f"Content {i}")
            
            processor = get_file_processor(max_workers=4)
            
            def read_and_hash(file_path: str) -> str:
                import hashlib
                content = Path(file_path).read_bytes()
                return hashlib.sha256(content).hexdigest()[:16]
            
            file_paths = [str(Path(tmpdir) / f"file_{i}.txt") for i in range(100)]
            
            start = time.time()
            results = processor.process_files(file_paths, read_and_hash)
            elapsed = time.time() - start
            
            assert len(results) == 100
            assert all(r.success for r in results)
            
            # Should be fast with parallel processing
            assert elapsed < 3.0
            
            stats = processor.get_statistics(results)
            assert stats["success_rate"] == 1.0


class TestErrorHandling:
    """Test error handling in optimized components."""
    
    def test_batch_processor_error_isolation(self):
        """Test that batch processor isolates errors."""
        def flaky_process(x):
            if x == 5:
                raise ValueError("Intentional error")
            return x * 2
        
        processor = BatchProcessor(
            processor_func=flaky_process,
            batch_size=3,
            error_isolation=True,
        )
        
        items = list(range(10))
        results = processor.process(items)
        
        # All items should have results
        assert len(results) == 10
        
        # Item 5 should be None (failed)
        assert results[5] is None
        
        # Others should be processed
        assert results[0] == 0
        assert results[9] == 18
    
    def test_file_processor_error_handling(self):
        """Test file processor handles errors gracefully."""
        processor = get_file_processor()
        
        # Mix of valid and invalid files
        with tempfile.TemporaryDirectory() as tmpdir:
            valid_path = str(Path(tmpdir) / "valid.txt")
            Path(valid_path).write_text("valid")
            
            invalid_path = "/nonexistent/file.txt"
            
            def read_content(file_path: str) -> str:
                return Path(file_path).read_text()
            
            results = processor.process_files(
                [valid_path, invalid_path],
                read_content,
            )
            
            assert len(results) == 2
            assert results[0].success is True
            assert results[1].success is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
