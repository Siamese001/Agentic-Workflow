"""Tests for Wave 2 - ADG Scanner Parallelization.

Tests parallel scanning, batch operations, and file batching.
"""

from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

import pytest
import redis

from agentic_core.adg.extraction.parallel_scanner import (
    ParallelADGScanner,
    ADGFileBatcher,
    ModuleScanResult,
    get_parallel_scanner,
    shutdown_parallel_scanner,
)
from agentic_core.adg.extraction.batch_operations import (
    ADGSQLiteBatchInserter,
    ADGEdgeBatchProcessor,
    EdgeBatch,
)


class TestADGFileBatcher:
    """Test ADG file batching logic."""
    
    def test_create_batches_empty(self):
        """Test batching with empty list."""
        batcher = ADGFileBatcher(target_batch_size=10)
        batches = batcher.create_batches([])
        assert batches == []
    
    def test_create_batches_single(self):
        """Test batching with single file."""
        batcher = ADGFileBatcher(target_batch_size=10)
        batches = batcher.create_batches(["/path/to/file.py"])
        assert len(batches) == 1
        assert batches[0] == ["/path/to/file.py"]
    
    def test_create_batches_multiple(self):
        """Test batching with multiple files."""
        batcher = ADGFileBatcher(target_batch_size=5)
        
        # Create 20 files
        files = [f"/path/to/file_{i}.py" for i in range(20)]
        batches = batcher.create_batches(files)
        
        # Should create ~4 batches of 5 files each
        assert len(batches) == 4
        assert sum(len(b) for b in batches) == 20
    
    def test_estimate_complexity_small(self):
        """Test complexity estimation for small file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("x = 1")  # Very small
            path = f.name
        
        batcher = ADGFileBatcher()
        complexity = batcher.estimate_complexity(path)
        
        assert complexity == 1  # Small files = 1 point
        
        Path(path).unlink()
    
    def test_estimate_complexity_large(self):
        """Test complexity estimation for large file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            # Write ~15KB of content
            for i in range(300):
                f.write(f"def function_{i}():\n    return {i}\n\n")
            path = f.name
        
        batcher = ADGFileBatcher()
        complexity = batcher.estimate_complexity(path)
        
        assert complexity >= 3  # Large files >= 3 points
        
        Path(path).unlink()


class TestADGSQLiteBatchInserter:
    """Test SQLite batch insertion."""
    
    def test_batch_inserter_context_manager(self):
        """Test batch inserter as context manager."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            
            # Create schema
            conn = sqlite3.connect(str(db_path))
            conn.execute("""
                CREATE TABLE edges (
                    id INTEGER PRIMARY KEY,
                    src_id TEXT,
                    dst_id TEXT,
                    relation_type TEXT,
                    edge_kind TEXT,
                    source_file TEXT,
                    line_no INTEGER,
                    symbol TEXT
                )
            """)
            conn.commit()
            conn.close()
            
            # Use batch inserter
            with ADGSQLiteBatchInserter(str(db_path), batch_size=10) as inserter:
                for i in range(25):
                    inserter.add_edge({
                        "src_id": f"src_{i}",
                        "dst_id": f"dst_{i}",
                        "relation_type": "calls",
                        "edge_kind": "static",
                        "source_file": f"file_{i}.py",
                        "line_no": i,
                        "symbol": f"func_{i}",
                    })
            
            # Verify insertion
            conn = sqlite3.connect(str(db_path))
            cursor = conn.execute("SELECT COUNT(*) FROM edges")
            count = cursor.fetchone()[0]
            assert count == 25
            conn.close()
    
    def test_batch_buffering(self):
        """Test that buffering works correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            
            conn = sqlite3.connect(str(db_path))
            conn.execute("""
                CREATE TABLE edges (
                    id INTEGER PRIMARY KEY,
                    src_id TEXT,
                    dst_id TEXT,
                    relation_type TEXT,
                    edge_kind TEXT,
                    source_file TEXT,
                    line_no INTEGER,
                    symbol TEXT
                )
            """)
            conn.commit()
            conn.close()
            
            with ADGSQLiteBatchInserter(str(db_path), batch_size=5) as inserter:
                # Add 3 edges (below batch size)
                for i in range(3):
                    inserter.add_edge({
                        "src_id": f"src_{i}",
                        "dst_id": f"dst_{i}",
                        "relation_type": "calls",
                        "edge_kind": "static",
                        "source_file": f"file_{i}.py",
                        "line_no": i,
                        "symbol": f"func_{i}",
                    })
                
                # Should be buffered, not yet inserted
                stats = inserter.get_stats()
                assert stats["edge_buffer_size"] == 3
                
                # Add 2 more (triggers flush)
                for i in range(3, 5):
                    inserter.add_edge({
                        "src_id": f"src_{i}",
                        "dst_id": f"dst_{i}",
                        "relation_type": "calls",
                        "edge_kind": "static",
                        "source_file": f"file_{i}.py",
                        "line_no": i,
                        "symbol": f"func_{i}",
                    })
                
                stats = inserter.get_stats()
                assert stats["total_inserted"] == 5
    
    def test_batch_add_multiple(self):
        """Test adding multiple edges at once."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            
            conn = sqlite3.connect(str(db_path))
            conn.execute("""
                CREATE TABLE edges (
                    id INTEGER PRIMARY KEY,
                    src_id TEXT,
                    dst_id TEXT,
                    relation_type TEXT,
                    edge_kind TEXT,
                    source_file TEXT,
                    line_no INTEGER,
                    symbol TEXT
                )
            """)
            conn.commit()
            conn.close()
            
            edges = [
                {
                    "src_id": f"src_{i}",
                    "dst_id": f"dst_{i}",
                    "relation_type": "calls",
                    "edge_kind": "static",
                    "source_file": f"file_{i}.py",
                    "line_no": i,
                    "symbol": f"func_{i}",
                }
                for i in range(100)
            ]
            
            with ADGSQLiteBatchInserter(str(db_path), batch_size=25) as inserter:
                inserter.add_edges_batch(edges)
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.execute("SELECT COUNT(*) FROM edges")
            count = cursor.fetchone()[0]
            assert count == 100
            conn.close()
    
    def test_batch_insert_failure_path(self):
        """Test batch insert failure with invalid data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            
            conn = sqlite3.connect(str(db_path))
            conn.execute("""
                CREATE TABLE edges (
                    id INTEGER PRIMARY KEY,
                    src_id TEXT NOT NULL,
                    dst_id TEXT NOT NULL,
                    relation_type TEXT,
                    edge_kind TEXT,
                    source_file TEXT,
                    line_no INTEGER,
                    symbol TEXT
                )
            """)
            conn.commit()
            conn.close()
            
            # Test with invalid data (NULL constraint violation)
            with pytest.raises(Exception):
                with ADGSQLiteBatchInserter(str(db_path), batch_size=5) as inserter:
                    inserter.add_edge({
                        "src_id": None,  # Invalid: NOT NULL constraint
                        "dst_id": "valid_dst",
                        "relation_type": "calls",
                        "edge_kind": "static",
                        "source_file": "test.py",
                        "line_no": 1,
                        "symbol": "test_func",
                    })
                    # Force flush by adding more edges
                    for i in range(5):
                        inserter.add_edge({
                            "src_id": f"src_{i}",
                            "dst_id": f"dst_{i}",
                            "relation_type": "calls",
                            "edge_kind": "static",
                            "source_file": f"file_{i}.py",
                            "line_no": i,
                            "symbol": f"func_{i}",
                        })
    
    def test_edge_validation_boundary_cases(self):
        """Test edge validation with boundary cases."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            
            conn = sqlite3.connect(str(db_path))
            conn.execute("""
                CREATE TABLE edges (
                    id INTEGER PRIMARY KEY,
                    src_id TEXT,
                    dst_id TEXT,
                    relation_type TEXT,
                    edge_kind TEXT,
                    source_file TEXT,
                    line_no INTEGER,
                    symbol TEXT
                )
            """)
            conn.commit()
            conn.close()
            
            with ADGSQLiteBatchInserter(str(db_path), batch_size=3) as inserter:
                # Test empty strings
                inserter.add_edge({
                    "src_id": "",
                    "dst_id": "",
                    "relation_type": "",
                    "edge_kind": "",
                    "source_file": "",
                    "line_no": 0,
                    "symbol": "",
                })
                
                # Test very long strings
                long_str = "x" * 1000
                inserter.add_edge({
                    "src_id": long_str,
                    "dst_id": long_str,
                    "relation_type": long_str,
                    "edge_kind": long_str,
                    "source_file": long_str,
                    "line_no": 999999,
                    "symbol": long_str,
                })
                
                # Test negative line numbers
                inserter.add_edge({
                    "src_id": "test",
                    "dst_id": "test2",
                    "relation_type": "calls",
                    "edge_kind": "static",
                    "source_file": "test.py",
                    "line_no": -1,
                    "symbol": "func",
                })
            
            # Verify all were inserted
            conn = sqlite3.connect(str(db_path))
            cursor = conn.execute("SELECT COUNT(*) FROM edges")
            count = cursor.fetchone()[0]
            assert count == 3
            conn.close()


class TestADGEdgeBatchProcessor:
    """Test ADG edge batch processing."""
    
    def test_process_edges(self):
        """Test batch processing of edges."""
        processor = ADGEdgeBatchProcessor(batch_size=10)
        
        edges = [{"src_id": f"src_{i}", "dst_id": f"dst_{i}"} for i in range(50)]
        results = processor.process(edges)
        
        assert len(results) == 50
        
        metrics = processor.get_metrics()
        assert metrics["total_items"] == 50
        assert metrics["total_batches"] == 5  # 50 / 10 = 5 batches
    
    def test_process_edges_boundary_cases(self):
        """Test edge processing with boundary cases."""
        processor = ADGEdgeBatchProcessor(batch_size=3)
        
        # Test empty edge list
        results = processor.process([])
        assert results == []
        
        # Test single edge
        results = processor.process([{"src_id": "a", "dst_id": "b"}])
        assert len(results) == 1
        
        # Test edges with missing fields
        edges = [
            {"src_id": "a"},  # Missing dst_id
            {"dst_id": "b"},  # Missing src_id
            {},  # Empty edge
            {"src_id": "c", "dst_id": "d", "extra": "field"},  # Extra field
        ]
        results = processor.process(edges)
        assert len(results) == 4
        
        # Verify metrics
        metrics = processor.get_metrics()
        assert metrics["total_items"] == 5  # 1 + 4 from boundary tests
    
    def test_parallel_processing(self):
        """Test parallel edge processing."""
        import time
        
        def slow_process(edges):
            time.sleep(0.01)  # Simulate work
            return edges
        
        processor = ADGEdgeBatchProcessor(batch_size=5, max_workers=2)
        processor.processor_func = slow_process
        
        edges = [{"id": i} for i in range(20)]
        results = processor.process_parallel(edges)
        
        assert len(results) == 20


class TestParallelADGScanner:
    """Test parallel ADG scanner."""
    
    def setup_method(self):
        """Reset singleton."""
        shutdown_parallel_scanner()
    
    def teardown_method(self):
        """Clean up."""
        shutdown_parallel_scanner()
    
    def test_scanner_initialization(self):
        """Test scanner initialization."""
        scanner = ParallelADGScanner(max_workers=4)
        
        assert scanner.config.max_workers == 4
        assert scanner.use_cache is True
        
        scanner.shutdown()
    
    def test_is_valid_module(self):
        """Test module validation."""
        scanner = ParallelADGScanner()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("pass")
            path = f.name
        
        assert scanner._is_valid_module(path) is True
        assert scanner._is_valid_module("/nonexistent.py") is False
        assert scanner._is_valid_module("/path/file.txt") is False
        
        Path(path).unlink()
    
    def test_scan_empty_list(self):
        """Test scanning empty list."""
        scanner = ParallelADGScanner()
        
        results = scanner.scan_modules_parallel([])
        
        assert results == []
        assert scanner.metrics.total_modules == 0
        
        scanner.shutdown()
    
    def test_scan_directory(self):
        """Test directory scanning."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create some Python files
            for i in range(5):
                path = Path(tmpdir) / f"module_{i}.py"
                path.write_text(f"def func_{i}(): pass")
            
            scanner = ParallelADGScanner(max_workers=2)
            
            # Note: Actual scan logic is placeholder - this tests the orchestration
            results = scanner.scan_directory_parallel(tmpdir, "*.py")
            
            # Should find 5 files
            assert len(results) == 5
            
            scanner.shutdown()
    
    def test_merge_results(self):
        """Test result merging."""
        scanner = ParallelADGScanner()
        
        results = [
            ModuleScanResult(
                file_path="/a.py",
                success=True,
                edges=[{"src": "a", "dst": "b"}],
                nodes=[{"id": "a"}],
            ),
            ModuleScanResult(
                file_path="/b.py",
                success=True,
                edges=[{"src": "b", "dst": "c"}],
                nodes=[{"id": "b"}],
            ),
            ModuleScanResult(
                file_path="/c.py",
                success=False,
                error="parse error",
            ),
        ]
        
        merged = scanner.merge_results(results)
        
        assert len(merged["edges"]) == 2
        assert len(merged["nodes"]) == 2
        assert len(merged["errors"]) == 1
        assert "parse error" in merged["errors"][0]
    
    def test_progress_callback(self):
        """Test progress callback."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create files
            for i in range(10):
                path = Path(tmpdir) / f"mod_{i}.py"
                path.write_text("pass")
            
            progress_calls = []
            
            def on_progress(current, total):
                progress_calls.append((current, total))
            
            scanner = ParallelADGScanner(max_workers=2)
            scanner.scan_directory_parallel(tmpdir, "*.py", on_progress)
            
            # Should have been called
            assert len(progress_calls) > 0
            
            # Final call should show completion
            final_current, final_total = progress_calls[-1]
            assert final_current == final_total
            
            scanner.shutdown()
    
    def test_singleton(self):
        """Test singleton pattern."""
        scanner1 = get_parallel_scanner(max_workers=2)
        scanner2 = get_parallel_scanner()
        
        assert scanner1 is scanner2
        
        shutdown_parallel_scanner()
        
        scanner3 = get_parallel_scanner()
        assert scanner3 is not scanner1


class TestIntegration:
    """Integration tests for Wave 2."""
    
    def test_end_to_end_batch_pipeline(self):
        """Test complete batch processing pipeline."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "adg.db"
            
            # Create schema
            conn = sqlite3.connect(str(db_path))
            conn.execute("""
                CREATE TABLE edges (
                    id INTEGER PRIMARY KEY,
                    src_id TEXT,
                    dst_id TEXT,
                    relation_type TEXT,
                    edge_kind TEXT,
                    source_file TEXT,
                    line_no INTEGER,
                    symbol TEXT
                )
            """)
            conn.commit()
            conn.close()
            
            # Create batch processor
            processor = ADGEdgeBatchProcessor(batch_size=100)
            
            # Generate test edges
            edges = [
                {
                    "src_id": f"module_{i % 10}",
                    "dst_id": f"target_{i}",
                    "relation_type": "calls",
                    "edge_kind": "static",
                    "source_file": f"module_{i % 10}.py",
                    "line_no": i,
                    "symbol": f"func_{i}",
                }
                for i in range(500)
            ]
            
            # Process in batches
            processed = processor.process(edges)
            
            # Insert to SQLite
            with ADGSQLiteBatchInserter(str(db_path), batch_size=50) as inserter:
                for edge in processed:
                    inserter.add_edge(edge)
            
            # Verify
            conn = sqlite3.connect(str(db_path))
            cursor = conn.execute("SELECT COUNT(*) FROM edges")
            count = cursor.fetchone()[0]
            assert count == 500
            conn.close()
            
            # Verify metrics
            metrics = processor.get_metrics()
            assert metrics["total_items"] == 500


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
