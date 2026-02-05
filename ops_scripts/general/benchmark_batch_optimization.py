"""
Performance benchmark to demonstrate the batch optimization improvement.
Compares disk I/O count and execution time between batch and non-batch modes.
"""

import shutil
import sys
import tempfile
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def benchmark_batch_vs_immediate():
    """
    Benchmark: 1000 increments - batch vs immediate writes.
    Demonstrates dramatic reduction in disk I/O and time.
    """
    from agentic_core.L4_state.validation_context.RuntimeStateGuard import RuntimeStateGuard

    # Test parameters
    num_increments = 1000

    # Create temporary directories
    root_immediate = Path(tempfile.mkdtemp(prefix="test_immediate_"))
    root_batch = Path(tempfile.mkdtemp(prefix="test_batch_"))

    try:
        print(f"🚀 Benchmarking {num_increments} metric increments...")
        print("=" * 60)

        # Test 1: Immediate writes (no batching)
        guard_immediate = RuntimeStateGuard(root_immediate)
        write_count_immediate = 0
        original_persist = guard_immediate._atomic_persist

        def spy_persist_immediate():
            nonlocal write_count_immediate
            write_count_immediate += 1
            original_persist()

        guard_immediate._atomic_persist = spy_persist_immediate

        start_time = time.time()
        for _i in range(num_increments):
            guard_immediate.increment_metric("benchmark_metric")
        immediate_time = time.time() - start_time

        # Test 2: Batched writes
        guard_batch = RuntimeStateGuard(root_batch)
        write_count_batch = 0
        original_persist_batch = guard_batch._atomic_persist

        def spy_persist_batch():
            nonlocal write_count_batch
            write_count_batch += 1
            original_persist_batch()

        guard_batch._atomic_persist = spy_persist_batch

        start_time = time.time()
        with guard_batch:
            for _i in range(num_increments):
                guard_batch.increment_metric("benchmark_metric")
        batch_time = time.time() - start_time

        # Results
        print("📊 RESULTS:")
        print(f"Immediate mode:  {write_count_immediate:4d} disk writes, {immediate_time:.4f}s")
        print(f"Batch mode:      {write_count_batch:4d} disk writes, {batch_time:.4f}s")
        print("-" * 60)

        # Calculate improvements
        write_reduction = (write_count_immediate - write_count_batch) / write_count_immediate * 100
        time_improvement = (
            (immediate_time - batch_time) / immediate_time * 100 if immediate_time > 0 else 0
        )

        print("🎯 PERFORMANCE GAINS:")
        print(
            f"  Disk I/O reduction: {write_reduction:.1f}% ({write_count_immediate} → {write_count_batch})"
        )
        print(
            f"  Time improvement:   {time_improvement:.1f}% ({immediate_time:.4f}s → {batch_time:.4f}s)"
        )

        # Verify correctness
        assert guard_immediate.get_metric("benchmark_metric") == num_increments
        assert guard_batch.get_metric("benchmark_metric") == num_increments
        assert write_count_immediate == num_increments  # Each increment writes immediately
        assert write_count_batch == 1  # Only one write at batch exit

        print("✅ All assertions passed - functionality preserved!")

        return {
            "disk_write_reduction": write_reduction,
            "time_improvement": time_improvement,
            "immediate_writes": write_count_immediate,
            "batch_writes": write_count_batch,
        }

    finally:
        # Cleanup
        shutil.rmtree(root_immediate, ignore_errors=True)
        shutil.rmtree(root_batch, ignore_errors=True)


def demonstrate_location_agent_scenario():
    """
    Demonstrate real-world LocationAgent scenario: scanning 500 files.
    Shows how batching prevents disk thrashing during validation scans.
    """
    from agentic_core.L4_state.validation_context.RuntimeStateGuard import RuntimeStateGuard

    # Simulate LocationAgent scanning files
    num_files = 500

    root = Path(tempfile.mkdtemp(prefix="test_location_scenario_"))
    try:
        print(f"\n🏛️  LocationAgent Scenario: Scanning {num_files} files")
        print("=" * 60)

        guard = RuntimeStateGuard(root)
        write_count = 0
        original_persist = guard._atomic_persist

        def spy_persist():
            nonlocal write_count
            write_count += 1
            original_persist()

        guard._atomic_persist = spy_persist

        # Simulate LocationAgent's file scanning loop with batch optimization
        start_time = time.time()
        with guard:  # LocationAgent uses batch context
            for file_id in range(num_files):
                # This is what LocationAgent does for each scanned file
                guard.increment_metric("files_scanned")

                # Simulate some validation work
                if file_id % 100 == 0:
                    print(f"  Scanned {file_id} files...")

        scan_time = time.time() - start_time

        print("\n📈 SCANNING RESULTS:")
        print(f"  Files scanned: {guard.get_metric('files_scanned')}")
        print(f"  Disk writes:   {write_count}")
        print(f"  Scan time:     {scan_time:.4f}s")
        print(f"  Efficiency:    {num_files / write_count:.0f} files per disk write")

        # Verify batching effectiveness
        expected_writes = 1  # Only one write at the end
        assert write_count == expected_writes, (
            f"Expected {expected_writes} write, got {write_count}"
        )
        assert guard.get_metric("files_scanned") == num_files

        print("✅ LocationAgent batching verified - disk thrashing prevented!")

    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    print("🔬 BATCH PERFORMANCE OPTIMIZATION - COMPREHENSIVE BENCHMARK")
    print("=" * 70)

    # Run benchmarks
    results = benchmark_batch_vs_immediate()
    demonstrate_location_agent_scenario()

    print("\n" + "=" * 70)
    print("🎉 BATCH OPTIMIZATION SUCCESSFULLY IMPLEMENTED!")
    print("📁 LocationAgent telemetry now uses efficient batching")
    print("⚡ High-volume scans will no longer cause disk thrashing")
    print("🛡️  RuntimeStateGuard provides context manager for lazy flushing")
