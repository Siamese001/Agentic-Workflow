"""Phase 0.2: Session-scoped ADG fixture implementation.

Provides a shared ADG scan result across all test modules to eliminate
redundant scans and improve test performance.
"""

import pytest
from pathlib import Path
from typing import Optional

# Store session-level cache
_session_adg_cache: Optional[dict] = None


@pytest.fixture(scope="session")
def session_adg_cache_dir(tmp_path_factory) -> Path:
    """Create a session-scoped cache directory for ADG scans."""
    cache_dir = tmp_path_factory.mktemp("adg_session_cache")
    return cache_dir


@pytest.fixture(scope="session")
def session_adg_scan(session_adg_cache_dir: Path) -> dict:
    """Session-scoped ADG scan result shared across all tests.
    
    This fixture performs a single ADG scan per pytest session and
    shares the result across all test modules, eliminating redundant scans.
    
    Returns:
        dict: ADG scan result with edges, nodes, and metadata
    """
    global _session_adg_cache
    
    if _session_adg_cache is not None:
        return _session_adg_cache
    
    from agentic_core.adg.extraction.static_scanner import ADGStaticScanner
    import time
    
    cache_path = session_adg_cache_dir / "session_scan_cache.json"
    
    print(f"\n=== SESSION ADG SCAN START ===")
    print(f"Cache path: {cache_path}")
    
    start_time = time.time()
    
    # Create scanner with session cache
    scanner = ADGStaticScanner(
        repo_root=Path.cwd(),
        cache_path=cache_path,
        include_tests=True
    )
    
    # Perform scan
    result = scanner.scan(commit_sha="pytest-session")
    
    scan_time = time.time() - start_time
    
    # Cache the result
    _session_adg_cache = {
        "result": result,
        "scan_time": scan_time,
        "edge_count": len(result.edges),
        "node_count": len(result.modules),
        "digest": result.digest
    }
    
    print(f"SESSION ADG SCAN COMPLETE:")
    print(f"  Scan time: {scan_time:.2f}s")
    print(f"  Edges: {len(result.edges):,}")
    print(f"  Modules: {len(result.modules):,}")
    print(f"  Digest: {result.digest}")
    print(f"=== SESSION ADG SCAN END ===\n")
    
    return _session_adg_cache


@pytest.fixture(scope="session")
def fast_adg_scan(session_adg_cache_dir: Path) -> dict:
    """Fast ADG scan with structural-only mode for performance-critical tests.
    
    This fixture uses a lightweight scan mode that only extracts structural
    relationships (imports, inheritance) from test files, skipping expensive
    semantic analysis.
    
    Returns:
        dict: Lightweight ADG scan result
    """
    from agentic_core.adg.extraction.static_scanner import ADGStaticScanner
    import time
    
    cache_path = session_adg_cache_dir / "fast_scan_cache.json"
    
    print(f"\n=== FAST ADG SCAN START ===")
    start_time = time.time()
    
    # Create scanner for fast mode
    scanner = ADGStaticScanner(
        repo_root=Path.cwd(),
        cache_path=cache_path,
        include_tests=True
    )
    
    # TODO: Implement scan_mode="structural_only" in scanner
    # For now, use regular scan but this will be updated in Phase 1
    result = scanner.scan(commit_sha="pytest-fast")
    
    scan_time = time.time() - start_time
    
    fast_result = {
        "result": result,
        "scan_time": scan_time,
        "edge_count": len(result.edges),
        "node_count": len(result.modules),
        "digest": result.digest,
        "mode": "structural_only"  # Will be actual in Phase 1
    }
    
    print(f"FAST ADG SCAN COMPLETE:")
    print(f"  Scan time: {scan_time:.2f}s")
    print(f"  Edges: {len(result.edges):,}")
    print(f"  Modules: {len(result.modules):,}")
    print(f"=== FAST ADG SCAN END ===\n")
    
    return fast_result


@pytest.fixture
def mock_adg():
    """Mock ADG for unit tests that don't need real graph data.
    
    Returns a lightweight mock that provides the ADG interface
    without performing any actual scanning.
    
    Returns:
        dict: Mock ADG with empty edges and minimal structure
    """
    class MockScanResult:
        def __init__(self):
            self.edges = []
            self.modules = []
            self.digest = "mock-digest-1234567890abcdef"
            self.manifest = None
        
        def canonical_edge_text(self) -> str:
            return "# Mock ADG - no edges"
    
    return {
        "result": MockScanResult(),
        "scan_time": 0.001,
        "edge_count": 0,
        "node_count": 0,
        "digest": "mock-digest-1234567890abcdef",
        "mode": "mock"
    }


# Performance monitoring fixtures
@pytest.fixture
def adg_performance_logger():
    """Fixture for logging ADG performance metrics during tests."""
    import time
    from collections import defaultdict
    
    class PerformanceLogger:
        def __init__(self):
            self.timings = defaultdict(list)
            self.counts = defaultdict(int)
        
        def time(self, operation: str):
            """Context manager for timing operations."""
            class Timer:
                def __init__(self, logger, op):
                    self.logger = logger
                    self.op = op
                    self.start = None
                
                def __enter__(self):
                    self.start = time.time()
                    return self
                
                def __exit__(self, *args):
                    duration = time.time() - self.start
                    self.logger.timings[self.op].append(duration)
                    self.logger.counts[self.op] += 1
                    print(f"  {self.op}: {duration:.3f}s")
            
            return Timer(self, operation)
        
        def summary(self):
            """Print performance summary."""
            print("\n=== ADG PERFORMANCE SUMMARY ===")
            for op, times in self.timings.items():
                avg = sum(times) / len(times)
                total = sum(times)
                count = self.counts[op]
                print(f"  {op}:")
                print(f"    Count: {count}")
                print(f"    Total: {total:.3f}s")
                print(f"    Average: {avg:.3f}s")
                print(f"    Max: {max(times):.3f}s")
            print("=" * 30)
    
    return PerformanceLogger()


# Test markers for different ADG requirements
slow_adg = pytest.mark.slow_adg
fast_adg = pytest.mark.fast_adg
mock_adg_only = pytest.mark.mock_adg_only
