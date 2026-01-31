#!/usr/bin/env python3
"""Run tests with progress bars and colored output."""

import subprocess
import sys
import time


def run_with_progress(cmd, description):
    """Run command with progress indicator."""
    print(f"\n🔥 {description}")
    print("=" * 60)

    process = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True,
    )

    # Show spinner while running
    spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    i = 0
    start_time = time.time()

    while True:
        output = process.stdout.readline()
        if output == "" and process.poll() is not None:
            break
        if output:
            # Print the actual output
            print(output.strip())
        else:
            # Show spinner when no output
            elapsed = time.time() - start_time
            print(f"\r{spinner[i % len(spinner)]} Running... {elapsed:.1f}s", end="", flush=True)
            i += 1
            time.sleep(0.1)

    # Clear spinner line
    print("\r" + " " * 50 + "\r", end="")

    return_code = process.poll()
    elapsed = time.time() - start_time

    if return_code == 0:
        print(f"✅ {description} - PASSED ({elapsed:.1f}s)")
    else:
        print(f"❌ {description} - FAILED ({elapsed:.1f}s) - Exit code: {return_code}")

    return return_code


def main():
    """Run test phases with progress tracking."""
    print("\n🚀 Starting Test Execution with Progress Tracking")
    print("=" * 60)

    phases = [
        ("python -m pytest tests/guardian --tb=no -q", "Phase 5.1: Guardian Tests"),
        ("python NuclearAuditAgent.py", "Phase 6.1: Nuclear Audit"),
    ]

    results = []

    for cmd, desc in phases:
        result = run_with_progress(cmd, desc)
        results.append((desc, result))

        if result != 0:
            print(f"\n⚠️  {desc} failed - continuing with next phase...")

    # Summary
    print("\n" + "=" * 60)
    print("📊 EXECUTION SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, r in results if r == 0)
    total = len(results)

    for desc, result in results:
        status = "✅ PASS" if result == 0 else "❌ FAIL"
        print(f"{status:<8} {desc}")

    print(f"\n🎯 Overall: {passed}/{total} phases passed ({passed / total * 100:.0f}%)")

    if passed == total:
        print("\n🎉 All phases completed successfully!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} phase(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
