#!/usr/bin/env python3
"""Benchmark import time for test files with emitters."""

import time
import subprocess
import sys
from pathlib import Path

def benchmark_import(file_path):
    """Benchmark import time for a single test file."""
    print(f"=== Benchmark Import Time: {file_path} ===")

    # Create a temporary script to import the test file
    script = f"""
import sys
import time
start = time.time()
try:
    import {file_path.replace('/', '.').replace('.py', '')}
    end = time.time()
    print(f"SUCCESS: {{end - start:.4f}} seconds")
except Exception as e:
    end = time.time()
    print(f"ERROR: {{e}}")
    print(f"TIME: {{end - start:.4f}} seconds")
"""

    script_path = Path("temp_import_test.py")
    script_path.write_text(script)

    try:
        start = time.time()
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd="."
        )
        end = time.time()

        print(f"Total time: {end - start:.4f} seconds")
        print(f"Output: {result.stdout.strip()}")
        if result.stderr:
            print(f"Stderr: {result.stderr.strip()}")

    finally:
        script_path.unlink(missing_ok=True)

def main():
    # Test a few files with different emitter counts
    test_files = [
        "tests/unit_min_deps/test_vllm_replay.py",  # 77 emitters
        "tests/unit_min_deps/test_unsafe_io_enforcement.py",  # 90 emitters
        "tests/unit_min_deps/test_three_tier_convergence.py",  # 77 emitters
    ]

    print("=== Phase 0.1: Import Time Benchmark (Before) ===")
    print()

    total_time = 0
    for file_path in test_files:
        if Path(file_path).exists():
            benchmark_import(file_path)
            print()
        else:
            print(f"File not found: {file_path}")
            print()

    print(f"Expected: Each file should take ~1-2 seconds due to emitter calls")
    print(f"After stripping: Should be <0.1 seconds per file")

if __name__ == "__main__":
    main()
