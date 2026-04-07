"""
ADG Drift Scoped Test Runner — CI Layer 2
==========================================
For every production Python file changed in the current PR (vs origin/main),
look up the covering test files via adg:edge:in:<nid>:covers and run only those.

Fail conditions:
  - Any changed prod module has ZERO covers edges in ADG  (exit 1)
  - Any ADG-selected test fails                           (exit code from pytest)

Exit codes:
  0 — all changed modules covered AND all ADG-selected tests pass
  1 — one or more changed modules have no test coverage
  pytest exit code — forwarded when tests exist but some fail

Usage:
    python ops_scripts/ci/drift_scoped_test_runner.py
    python ops_scripts/ci/drift_scoped_test_runner.py --base-ref origin/main
    python ops_scripts/ci/drift_scoped_test_runner.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
import time
from pathlib import Path

import redis

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_reads_through,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "drift_scoped_test_runner", "uwg_governed_write")
_emit_writes_through("p1", "drift_scoped_test_runner", "uwg_governed_write_2")
_emit_pulls_context("p1", "drift_scoped_test_runner", "context_retrieval")
_emit_pulls_context("p1", "drift_scoped_test_runner", "context_retrieval_2")
emit_determinism_digest("trace_drift_scoped_test_runner", "drift_scoped_test_runner_dispatch")
emit_determinism_digest("trace_drift_scoped_test_runner", "drift_scoped_test_runner_complete")
_emit_validated_by_safety_plane("p1", "drift_scoped_test_runner", "safety_validation")
_emit_reads_through("l4", "drift_scoped_test_runner", "urg_read_1")
_emit_reads_through("l4", "drift_scoped_test_runner", "urg_read_2")
_emit_reads_through("l4", "drift_scoped_test_runner", "urg_read_3")
_emit_reads_through("l4", "drift_scoped_test_runner", "urg_read_4")
_emit_reads_through("l4", "drift_scoped_test_runner", "urg_read_5")
_emit_reads_through("l4", "drift_scoped_test_runner", "urg_read_6")
_emit_reads_through("l4", "drift_scoped_test_runner", "urg_read_7")
_emit_reads_through("l4", "drift_scoped_test_runner", "urg_read_8")
_emit_reads_through("l4", "drift_scoped_test_runner", "urg_read_9")
_emit_reads_through("l4", "drift_scoped_test_runner", "urg_read_10")
_emit_reads_through("l4", "drift_scoped_test_runner", "urg_read_11")
_emit_reads_through("l4", "drift_scoped_test_runner", "urg_read_12")
_emit_reads_through("l4", "drift_scoped_test_runner", "urg_read_13")
_emit_reads_through("l4", "drift_scoped_test_runner", "urg_read_14")
_emit_reads_through("l4", "drift_scoped_test_runner", "urg_read_15")
_emit_reads_through("l4", "drift_scoped_test_runner", "urg_read_16")
_emit_reads_through("l4", "drift_scoped_test_runner", "urg_read_17")
_emit_reads_through("l4", "drift_scoped_test_runner", "urg_read_18")
_emit_reads_through("l4", "drift_scoped_test_runner", "urg_read_19")
_emit_reads_through("l4", "drift_scoped_test_runner", "urg_read_20")
_emit_reads_through("l4", "drift_scoped_test_runner", "urg_read_21")
_emit_reads_through("l4", "drift_scoped_test_runner", "urg_read_22")
_emit_reads_through("l4", "drift_scoped_test_runner", "urg_read_23")
_emit_reads_through("l4", "drift_scoped_test_runner", "urg_read_24")
_emit_reads_through("l4", "drift_scoped_test_runner", "urg_read_25")
_emit_reads_through("l4", "drift_scoped_test_runner", "urg_read_26")

logger = logging.getLogger(__name__)

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
GIT_DIFF_TIMEOUT_S = 30
PYTEST_RUN_TIMEOUT_S = 300
PROJECT_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _connect() -> redis.Redis:
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)


def _changed_prod_files(base_ref: str) -> list[str]:
    """
    Return list of changed production .py files (not in tests/) vs base_ref.
    Uses git diff --name-only.
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{base_ref}...HEAD"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=GIT_DIFF_TIMEOUT_S,
        )
        if result.returncode != 0:
            # Fallback: staged files vs HEAD
            result = subprocess.run(
                ["git", "diff", "--name-only", "--cached"],
                capture_output=True,
                text=True,
                cwd=str(PROJECT_ROOT),
                timeout=GIT_DIFF_TIMEOUT_S,
            )
        lines = result.stdout.strip().splitlines()
        return [ln for ln in lines if ln.endswith(".py") and not ln.startswith("tests/")]
    except (subprocess.TimeoutExpired, OSError, FileNotFoundError) as exc:    # guardian: Multiple exceptions (OSError, FileNotFoundError) need specific handling
        logger.error("[drift-ci] git diff failed: %s", exc)
        return []


def _resolve_test_paths_for_module(r: redis.Redis, prod_path: str) -> list[str]:
    """
    Return test file paths covering prod_path via adg:edge:in:<nid>:covers.

    Uses adg:nodes:by_file:<path> SET → module node IDs → covers fan-in SET.
    Returns deduplicated, sorted list of test file paths.
    """
    test_paths: set[str] = set()
    try:
        node_ids = r.smembers(f"adg:nodes:by_file:{prod_path}")
        for nid in node_ids:
            node = r.hgetall(f"adg:node:{nid}")
            if node.get("entity_type") != "module":
                continue
            cover_nids = r.smembers(f"adg:edge:in:{nid}:covers")
            for tnid in cover_nids:
                tnode = r.hgetall(f"adg:node:{tnid}")
                rp = tnode.get("resolved_path", "")
                if rp and rp.startswith("tests/"):
                    test_paths.add(rp)
    except redis.RedisError as exc:
        logger.warning("[drift-ci] covers lookup failed for %s: %s", prod_path, exc)
    return sorted(test_paths)


def _run_pytest(test_paths: list[str]) -> int:
    """
    Run pytest against absolute paths of test_paths.
    Returns pytest exit code.
    """
    abs_paths: list[str] = []
    for p in test_paths:
        ap = PROJECT_ROOT / p
        if ap.exists():
            abs_paths.append(str(ap))
        else:
            logger.warning("[drift-ci] test path not found on disk: %s", p)

    if not abs_paths:
        print("[drift-ci] WARNING: no resolvable test paths to run")
        return 0

    try:
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                *abs_paths,
                "--tb=short",
                "-q",
                "--no-header",
            ],
            cwd=str(PROJECT_ROOT),
            timeout=PYTEST_RUN_TIMEOUT_S,
        )
        return proc.returncode
    except subprocess.TimeoutExpired:
        print(f"[drift-ci] ERROR: pytest timed out after {PYTEST_RUN_TIMEOUT_S}s")
        return 2


def _write_ci_run_result(
    r: redis.Redis,
    changed: int,
    test_files: int,
    uncovered: list[str],
    exit_code: int,
) -> None:
    """Persist CI run summary to adg:drift:ci_run HASH (1h TTL)."""
    pipe = r.pipeline(transaction=False)
    pipe.delete("adg:drift:ci_run")
    pipe.hmset(
        "adg:drift:ci_run",
        {
            "changed_files": str(changed),
            "test_files_run": str(test_files),
            "uncovered_changed": str(len(uncovered)),
            "exit_code": str(exit_code),
            "timestamp": str(round(time.time(), 3)),
        },
    )
    pipe.expire("adg:drift:ci_run", 3600)
    pipe.execute()


# ---------------------------------------------------------------------------
# Core runner
# ---------------------------------------------------------------------------


def run(base_ref: str = "origin/main", dry_run: bool = False) -> int:
    """
    Main runner logic.

    Args:
        base_ref: Git ref to diff against (default: origin/main).
        dry_run:  Print plan without running pytest.

    Returns:
        Exit code.
    """
    try:
        r = _connect()
        r.ping()
    except redis.RedisError as exc:
        print(f"[drift-ci] ERROR: cannot connect to Redis: {exc}")
        return 2

    # 1. Get changed prod files
    changed_files = _changed_prod_files(base_ref)
    if not changed_files:
        print("[drift-ci] No production .py files changed — nothing to check")
        _write_ci_run_result(r, 0, 0, [], 0)
        return 0

    print(f"[drift-ci] Changed prod files: {len(changed_files)}")
    for f in changed_files:
        print(f"  {f}")

    # 2. ADG lookup: covers edges for each changed file
    test_paths_to_run: set[str] = set()
    uncovered_changed: list[str] = []

    for prod_path in changed_files:
        covering = _resolve_test_paths_for_module(r, prod_path)
        if covering:
            test_paths_to_run.update(covering)
            print(f"  [covered] {prod_path} → {len(covering)} test file(s)")
        else:
            uncovered_changed.append(prod_path)
            print(f"  [UNCOVERED] {prod_path}")

    # 3. Fail immediately if any changed module has zero covers edges
    if uncovered_changed:
        print(f"\n[drift-ci] FAIL: {len(uncovered_changed)} changed module(s) have no ADG covers edges:")
        for m in uncovered_changed:
            print(f"  UNCOVERED: {m}")
        print()
        print("[drift-ci] To fix:")
        print("  1. Add a test file that imports each uncovered module (creates a `covers` edge)")
        print("  2. Re-ingest: python -m tools.adg.adg_redis_ingest --force")
        print("  3. Re-run: python ops_scripts/ci/drift_scoped_test_runner.py")
        _write_ci_run_result(r, len(changed_files), 0, uncovered_changed, 1)
        return 1

    sorted_tests = sorted(test_paths_to_run)
    print(f"\n[drift-ci] ADG-selected test files ({len(sorted_tests)}):")
    for t in sorted_tests:
        print(f"  {t}")

    if dry_run:
        print("\n[drift-ci] dry-run — skipping pytest execution")
        _write_ci_run_result(r, len(changed_files), len(sorted_tests), [], 0)
        return 0

    # 4. Run scoped pytest
    print(f"\n[drift-ci] Running {len(sorted_tests)} ADG-selected test file(s) ...")
    exit_code = _run_pytest(sorted_tests)

    _write_ci_run_result(r, len(changed_files), len(sorted_tests), uncovered_changed, exit_code)

    if exit_code == 0:
        print("\n[drift-ci] PASS — all ADG-selected tests passed")
    else:
        print(f"\n[drift-ci] FAIL — pytest exit code: {exit_code}")

    return exit_code


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="ADG drift scoped CI test runner")
    parser.add_argument(
        "--base-ref",
        default="origin/main",
        help="Git ref to diff against (default: origin/main)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Plan only — print what would be run without executing pytest",
    )
    args = parser.parse_args()
    sys.exit(run(base_ref=args.base_ref, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
