"""
Run the six batch test suites and summarize the pass rate.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

TEST_SUITES = [
    "tests/apps_rg/test_batch_1_foundation.py",
    "tests/apps_rg/test_batch_2_hops.py",
    "tests/apps_rg/test_batch_3_generation.py",
    "tests/apps_rg/test_batch_4_refinement_part1.py",
    "tests/apps_rg/test_batch_5_refinement_part2.py",
    "tests/apps_rg/test_batch_6_safety.py",
]


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


def run_test_suite(test_file: str, repo_root: Path, timeout: int) -> tuple[bool, str]:
    print(f"\n{'=' * 60}")
    print(f"Running: {test_file}")
    print("=" * 60)
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"],
            capture_output=True,
            text=True,
            cwd=repo_root,
            timeout=timeout,
            check=False,
        )
        output = (result.stdout or "") + (result.stderr or "")
        return (result.returncode == 0, output)
    except subprocess.TimeoutExpired as exc:
        partial_output = (exc.stdout or "") + (exc.stderr or "")
        return (False, f"TIMEOUT after {timeout}s\n{partial_output}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run all batch test suites.")
    parser.add_argument("--repo-root", help="Override automatic repository root detection.")
    parser.add_argument("--timeout", type=int, default=600, help="Per-suite timeout in seconds.")
    args = parser.parse_args(argv)

    repo_root = _resolve_repo_root(args.repo_root)
    results: dict[str, bool] = {}

    for test_suite in TEST_SUITES:
        success, output = run_test_suite(test_suite, repo_root, args.timeout)
        results[test_suite] = success
        if success:
            print(f"\n✅ PASSED: {test_suite}")
        else:
            print(f"\n❌ FAILED: {test_suite}")
            print(output[-1000:])

    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    passed = sum(1 for success in results.values() if success)
    total = len(results)

    for suite, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {Path(suite).name}")

    print(f"\nTotal: {passed}/{total} passed ({100 * passed / total:.0f}%)")
    if passed == total:
        print("\n🎉 ALL BATCH TESTS PASSED!")
        return 0

    print(f"\n⚠️ {total - passed} test suites failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
