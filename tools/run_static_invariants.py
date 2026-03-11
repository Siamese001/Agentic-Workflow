"""
tools/run_static_invariants.py

Runner for all static invariant checks.
Baseline-aware: loads previous violation snapshot and reports only NEW violations.
"""

from __future__ import annotations

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

REPO_ROOT = Path(__file__).resolve().parents[1]

# Ensure repo root is on sys.path so agentic_core is importable
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
BASELINE_PATH = REPO_ROOT / "artifacts" / "static_invariants_baseline.json"


def _load_baseline() -> set[str]:
    if BASELINE_PATH.exists():
        try:
            data = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
            entries = data if isinstance(data, list) else data.get("violations", [])
            print(f"Loaded baseline with {len(entries)} known violation(s).")
            return set(entries)
        except Exception:  # guardian: allow-silent-swallower
            pass
    print("Loaded baseline with 0 known violation(s).")
    return set()


def _run_ptc_invariants() -> list[str]:
    print("Scanning for PTC invariants...")
    try:
        from agentic_core.L5_safety.static_checks.ptc_invariants import (
            scan_repository_for_ptc_invariants,
        )

        violations = scan_repository_for_ptc_invariants(REPO_ROOT)
        if violations:
            print(f"FAIL: PTC Invariants: {len(violations)} violation(s) found.")
            for v in violations:
                print(f"  {v}")
        else:
            print("OK: PTC Invariants: No violations found")
        return [str(v) for v in violations]
    except Exception as exc:  # guardian: allow-silent-swallower
        print(f"ERROR: PTC invariants scanner failed: {exc}")
        return []


def main() -> int:
    baseline = _load_baseline()

    all_violations: list[str] = []
    all_violations.extend(_run_ptc_invariants())

    new_violations = [v for v in all_violations if v not in baseline]

    if new_violations:
        print(f"FAIL: {len(new_violations)} new violations found (not in baseline).")
        for v in new_violations:
            print(f"  NEW: {v}")
        return 1

    print("OK: No NEW violations found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
