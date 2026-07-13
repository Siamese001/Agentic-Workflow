#!/usr/bin/env python3
"""Run all skill-contract gates in deterministic order."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
GATES = (
    "ops_scripts/ci/check_skill_frontmatter.py",
    "ops_scripts/ci/check_skill_description_quality.py",
    "ops_scripts/ci/check_skill_catalog_integrity.py",
    "ops_scripts/ci/check_skill_eval_coverage.py",
)
TIMEOUT_SECONDS = 90


def main() -> int:
    for relative_path in GATES:
        command = [sys.executable, str(REPO_ROOT / relative_path)]
        print(f"[skill_contract] RUN {' '.join(command)}", flush=True)
        try:
            completed = subprocess.run(
                command,
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
                timeout=TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            print(f"[skill_contract] FAIL: {relative_path} timed out", flush=True)
            return 1
        if completed.stdout:
            print(completed.stdout.rstrip(), flush=True)
        if completed.stderr:
            print(completed.stderr.rstrip(), file=sys.stderr, flush=True)
        if completed.returncode != 0:
            print(f"[skill_contract] FAIL: {relative_path}", flush=True)
            return completed.returncode
    print("[skill_contract] PASS: all skill-contract gates passed.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
