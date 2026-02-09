#!/usr/bin/env python3
"""Agent Count Hard Cap — CI Gate.

Asserts that the ACTIVE agent count does not exceed the hard cap.

Uses the shared ``active_set_helper`` — the single canonical import
point for the ACTIVE set.  This guarantees convergence with
``discovery_registry_consistency_check.py`` and all future gates.

Exit 0 = pass, exit 1 = violations found.

Merge-ready gate.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

HARD_CAP = 149


def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(project_root))  # guardian: allow-global_mutation

    from ops_scripts.ci.active_set_helper import get_active_set

    try:
        result = get_active_set(project_root)
    except Exception as exc:  # guardian: allow-silent_swallower
        print(f"FAIL: could not enumerate active agents: {exc}", file=sys.stderr)
        return 1

    print("Agent Count Cap (discovery-aligned):")
    print(f"  active={result.count}  cap={HARD_CAP}  delta={result.count - HARD_CAP}")
    print(f"  fingerprint: {result.fingerprint}")
    print(f"  first_10: {list(result.agent_ids[:10])}")
    print(f"  last_10:  {list(result.agent_ids[-10:])}")

    if result.count > HARD_CAP:
        commit_msg = os.environ.get("COMMIT_MESSAGE", "")
        if "AGENT_COUNT_BUMP:" in commit_msg:
            print(f"PASS: count {result.count} > cap {HARD_CAP} but AGENT_COUNT_BUMP tag present")
            return 0
        print(
            f"FAIL: active agent count {result.count} exceeds hard cap {HARD_CAP}\n"
            f"  To increase, add AGENT_COUNT_BUMP:<reason> to commit message",
        )
        return 1

    print(f"PASS: {result.count} active agents within cap {HARD_CAP}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
