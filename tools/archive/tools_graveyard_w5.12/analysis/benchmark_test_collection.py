#!/usr/bin/env python3
"""Benchmark test collection time for Phase 0 performance measurement."""

import subprocess
import time


def run_command(cmd, cwd=None):
    """Run command and return stdout, stderr, returncode."""
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=300,  # 5 minute timeout
    )
    return result.stdout, result.stderr, result.returncode


def benchmark_collection():
    """Benchmark pytest --collect-only timing."""
    print("=== Benchmark: Test Collection Time (Before Changes) ===")
    print()

    # Run pytest --collect-only with timing
    start_time = time.time()
    stdout, stderr, returncode = run_command(
        "python -m pytest --collect-only -q tests/",
        cwd=".",
    )
    end_time = time.time()

    collection_time = end_time - start_time

    # Count collected tests
    test_count = 0
    if returncode == 0:
        lines = stdout.strip().split("\n")
        for line in lines:
            if "::test_" in line:
                test_count += 1

    print(f"Collection time: {collection_time:.2f} seconds")
    print(f"Tests collected: {test_count}")
    print(f"Return code: {returncode}")

    if stderr:
        print(f"Stderr (first 500 chars): {stderr[:500]}")

    # Save results
    results = {
        "collection_time_seconds": collection_time,
        "test_count": test_count,
        "return_code": returncode,
        "timestamp": time.time(),
    }

    with open("test_collection_before.json", "w") as f:
        import json

        json.dump(results, f, indent=2)

    print()
    print("Results saved to: test_collection_before.json")
    print("Expected improvement: ~30s (based on 60,457 emitter calls)")

    return collection_time, test_count


if __name__ == "__main__":
    benchmark_collection()
