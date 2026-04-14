"""
Benchmark the difference between immediate persistence and batched persistence.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "benchmark_batch_optimization", "write_through")
_emit_writes_through("p1", "benchmark_batch_optimization", "write_through_2")
_emit_pulls_context("p1", "benchmark_batch_optimization", "context_pull")
_emit_pulls_context("p1", "benchmark_batch_optimization", "context_pull_2")
emit_determinism_digest("trace_benchmark_batch_optimization", "dispatch")
emit_determinism_digest("trace_benchmark_batch_optimization", "complete")
_emit_validated_by_safety_plane("p1", "benchmark_batch_optimization", "safety_validation")


def _resolve_repo_root(explicit_root: str | None = None) -> Path:
    if explicit_root:
        return Path(explicit_root).expanduser().resolve()
    env_root = os.getenv("AGENTIC_WORKFLOW_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    for candidate in Path(__file__).resolve().parents:
        if (candidate / ".git").exists():
            return candidate
    return Path.cwd().resolve()


def _bootstrap_imports(repo_root: Path) -> None:
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))  # guardian: allow-global-mutation -- benchmark bootstrap


def benchmark_batch_vs_immediate(num_increments: int) -> dict[str, float]:
    from agentic_core.L4_state.utils.memory.runtime_state_guard import RuntimeStateGuard

    root_immediate = Path(tempfile.mkdtemp(prefix="test_immediate_"))
    root_batch = Path(tempfile.mkdtemp(prefix="test_batch_"))
    try:
        print(f"🚀 Benchmarking {num_increments} metric increments...")
        print("=" * 60)

        guard_immediate = RuntimeStateGuard(root_immediate)
        write_count_immediate = 0
        original_persist = guard_immediate._atomic_persist

        def spy_persist_immediate() -> None:
            nonlocal write_count_immediate
            write_count_immediate += 1
            original_persist()

        guard_immediate._atomic_persist = spy_persist_immediate
        start_time = time.perf_counter()
        for _ in range(num_increments):
            guard_immediate.increment_metric("benchmark_metric")
        immediate_time = time.perf_counter() - start_time

        guard_batch = RuntimeStateGuard(root_batch)
        write_count_batch = 0
        original_persist_batch = guard_batch._atomic_persist

        def spy_persist_batch() -> None:
            nonlocal write_count_batch
            write_count_batch += 1
            original_persist_batch()

        guard_batch._atomic_persist = spy_persist_batch
        start_time = time.perf_counter()
        with guard_batch:
            for _ in range(num_increments):
                guard_batch.increment_metric("benchmark_metric")
        batch_time = time.perf_counter() - start_time

        print("📊 RESULTS:")
        print(f"Immediate mode:  {write_count_immediate:4d} disk writes, {immediate_time:.4f}s")
        print(f"Batch mode:      {write_count_batch:4d} disk writes, {batch_time:.4f}s")
        print("-" * 60)

        write_reduction = (
            (write_count_immediate - write_count_batch) / write_count_immediate * 100
            if write_count_immediate
            else 0.0
        )
        time_improvement = (immediate_time - batch_time) / immediate_time * 100 if immediate_time > 0 else 0.0

        print("🎯 PERFORMANCE GAINS:")
        print(f"  Disk I/O reduction: {write_reduction:.1f}% ({write_count_immediate} → {write_count_batch})")
        print(f"  Time improvement:   {time_improvement:.1f}% ({immediate_time:.4f}s → {batch_time:.4f}s)")

        assert guard_immediate.get_metric("benchmark_metric") == num_increments
        assert guard_batch.get_metric("benchmark_metric") == num_increments
        assert write_count_immediate == num_increments
        assert write_count_batch == 1
        print("✅ All assertions passed - functionality preserved!")

        return {
            "disk_write_reduction": write_reduction,
            "time_improvement": time_improvement,
            "immediate_writes": float(write_count_immediate),
            "batch_writes": float(write_count_batch),
        }
    finally:
        shutil.rmtree(root_immediate, ignore_errors=True)
        shutil.rmtree(root_batch, ignore_errors=True)


def demonstrate_location_agent_scenario(num_files: int) -> None:
    from agentic_core.L4_state.utils.memory.runtime_state_guard import RuntimeStateGuard

    root = Path(tempfile.mkdtemp(prefix="test_location_scenario_"))
    try:
        print(f"\n🏛️  LocationAgent Scenario: Scanning {num_files} files")
        print("=" * 60)

        guard = RuntimeStateGuard(root)
        write_count = 0
        original_persist = guard._atomic_persist

        def spy_persist() -> None:
            nonlocal write_count
            write_count += 1
            original_persist()

        guard._atomic_persist = spy_persist
        start_time = time.perf_counter()
        with guard:
            for file_id in range(num_files):
                guard.increment_metric("files_scanned")
                if file_id and file_id % 100 == 0:
                    print(f"  Scanned {file_id} files...")
        scan_time = time.perf_counter() - start_time

        print("\n📈 SCANNING RESULTS:")
        print(f"  Files scanned: {guard.get_metric('files_scanned')}")
        print(f"  Disk writes:   {write_count}")
        print(f"  Scan time:     {scan_time:.4f}s")
        print(f"  Efficiency:    {num_files / write_count:.0f} files per disk write")

        assert write_count == 1, f"Expected 1 write, got {write_count}"
        assert guard.get_metric("files_scanned") == num_files
        print("✅ LocationAgent batching verified - disk thrashing prevented!")
    finally:
        shutil.rmtree(root, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Benchmark batched RuntimeStateGuard persistence.")
    parser.add_argument("--repo-root", help="Override automatic repository root detection.")
    parser.add_argument(
        "--increments", type=int, default=1000, help="Number of metric increments to benchmark."
    )
    parser.add_argument("--files", type=int, default=500, help="Number of files for the scanning scenario.")
    args = parser.parse_args(argv)

    repo_root = _resolve_repo_root(args.repo_root)
    _bootstrap_imports(repo_root)

    print("🔬 BATCH PERFORMANCE OPTIMIZATION - COMPREHENSIVE BENCHMARK")
    print("=" * 70)
    benchmark_batch_vs_immediate(args.increments)
    demonstrate_location_agent_scenario(args.files)
    print("\n" + "=" * 70)
    print("🎉 BATCH OPTIMIZATION SUCCESSFULLY IMPLEMENTED!")
    print("📁 LocationAgent telemetry now uses efficient batching")
    print("⚡ High-volume scans will no longer cause disk thrashing")
    print("🛡️  RuntimeStateGuard provides context manager for lazy flushing")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
