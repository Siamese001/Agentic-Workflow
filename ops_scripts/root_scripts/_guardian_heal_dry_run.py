"""
Guardian-Heal Pipeline Dry-Run Wrapper.

Runs the L3 guardian-dispatcher-healer pipeline in dry-run mode
and emits JSON results to stdout.

Mirrors _ssot_dry_run.py conventions (arg parsing, exit codes).

Usage:
    python ops_scripts/root_scripts/_guardian_heal_dry_run.py
    python ops_scripts/root_scripts/_guardian_heal_dry_run.py --mode scan
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

PROJECT_ROOT = Path(__file__).resolve().parents[2]
# guardian: allow-global-mutation
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L3_orchestration.scripts.guardian_heal_orchestrator import (
    run_pipeline,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Guardian-Heal Pipeline dry-run wrapper",
    )
    parser.add_argument(
        "--mode",
        choices=["scan", "dry-run"],
        default="dry-run",
        help="Pipeline mode (default: dry-run).",
    )
    parser.add_argument(
        "--artifacts",
        default=None,
        help="Artifact output directory (repo-relative).",
    )
    parser.add_argument(
        "--timestamp",
        default=None,
        help="Injectable ISO-8601 timestamp.",
    )
    parser.add_argument(
        "--format",
        choices=["json", "summary"],
        default="json",
        help="Output format (default: json).",
    )
    args = parser.parse_args()

    try:
        result = run_pipeline(
            mode=args.mode,
            repo_root=PROJECT_ROOT,
            write_artifacts_dir=args.artifacts,
            timestamp=args.timestamp,
        )
    # guardian: allow-silent-swallow
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    guardian = result.get("guardian_result", {})

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        status = guardian.get("status", "?")
        summary = guardian.get("summary", "N/A")
        print(f"Mode: {result['mode']} | Status: {status}")
        print(f"Summary: {summary}")
        for check in guardian.get("checks", []):
            cid = check.get("check_id", "?")
            cst = check.get("status", "?")
            det = check.get("details", "")
            print(f"  [{cst}] {cid}: {det}")

    if guardian.get("status") == "ERROR":
        return 2
    if args.mode != "scan" and guardian.get("status") == "FAIL":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
