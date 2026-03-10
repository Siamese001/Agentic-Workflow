#!/usr/bin/env python3
"""MRO New Diamond Check — CI Gate (Entry-Level Prevention).

Prevents reintroduction of MRO diamonds at the *entry level*.
Unlike mro_contract_check.py (which enforces a total-count ceiling),
this gate fails if ANY diamond exists that is NOT already in the
committed baseline entries.

Policy:
  1. Every current diamond must have a matching entry in the baseline JSON.
  2. A "new" diamond (not in baseline) → HARD FAIL.
  3. Override: commit tag MRO_BASELINE_BUMP:<reason> allows pass,
     but ONLY if the baseline JSON has been updated in the same PR
     (i.e., the new diamond appears in the updated baseline).

Exit 0 = pass, exit 1 = new diamond(s) detected.
"""

from __future__ import annotations

import json
import os
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

# Re-use scan logic from mro_contract_check
BASELINE_PATH = "artifacts/consolidation/mro_diamond_baseline.json"


def _diamond_key(entry: dict) -> str:
    """Canonical key: file:class."""
    return entry["file"] + ":" + entry["class"]


def main() -> int:
    project_root = Path(__file__).resolve().parents[2]

    if str(project_root) not in sys.path:
        # guardian: allow-global-mutation
        sys.path.insert(0, str(project_root))

    from ops_scripts.ci.mro_contract_check import scan_diamonds

    baseline_file = project_root / BASELINE_PATH
    if not baseline_file.is_file():
        print(f"FAIL: baseline not found: {BASELINE_PATH}", file=sys.stderr)
        return 1

    baseline = json.loads(baseline_file.read_text(encoding="utf-8"))
    baseline_keys = {_diamond_key(e) for e in baseline.get("entries", [])}

    current_diamonds = scan_diamonds(project_root)
    current_keys = {_diamond_key(d) for d in current_diamonds}

    new_diamonds = [d for d in current_diamonds if _diamond_key(d) not in baseline_keys]

    print("MRO New Diamond Check (entry-level prevention):")
    print(f"  baseline_entries={len(baseline_keys)}  current_entries={len(current_keys)}")
    print(f"  new_diamonds={len(new_diamonds)}")

    if not new_diamonds:
        print("PASS: no new MRO diamonds introduced")
        return 0

    # New diamonds detected — check for bump tag
    commit_msg = os.environ.get("COMMIT_MESSAGE", "")
    if "MRO_BASELINE_BUMP:" in commit_msg:
        # Verify each new diamond is in the baseline (i.e., baseline was updated)
        still_missing = [d for d in new_diamonds if _diamond_key(d) not in baseline_keys]
        if still_missing:
            print(
                f"FAIL: MRO_BASELINE_BUMP tag present but {len(still_missing)} "
                "new diamond(s) not added to baseline JSON:",
            )
            for d in still_missing:
                print(f"  - {d['file']}:{d['line']} class {d['class']} {d['redundant_mixins']}")
            return 1
        print(
            f"WARN: {len(new_diamonds)} new diamond(s) allowed via MRO_BASELINE_BUMP tag",
        )
        return 0

    # Hard fail
    print(f"FAIL: {len(new_diamonds)} new MRO diamond(s) introduced:")
    for d in new_diamonds:
        print(
            f"  - {d['file']}:{d['line']} class {d['class']} "
            f"redundant={d['redundant_mixins']} carriers={d['carriers']}",
        )
    print("  To fix:")
    print(f"    1. Edit {BASELINE_PATH} — add new entries + set total={len(current_keys)}")
    print("    2. Commit with tag: MRO_BASELINE_BUMP:<reason>")
    print("    3. Verify: PYTHONPATH=. python ops_scripts/ci/mro_new_diamond_check.py")
    return 1


if __name__ == "__main__":
    sys.exit(main())
