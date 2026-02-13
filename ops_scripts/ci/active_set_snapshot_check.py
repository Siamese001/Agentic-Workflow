#!/usr/bin/env python3
"""Active Set Drift Snapshot Check — CI Gate.

Compares the current active set fingerprint against a committed snapshot.
If the fingerprint has changed, the commit must contain the tag:
    ACTIVE_SET_SNAPSHOT_BUMP:<reason>

This prevents silent active-set drift.

Exit 0 = pass, exit 1 = drift detected without acknowledgement.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

SNAPSHOT_PATH = "artifacts/consolidation/active_set_snapshot.json"


def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    snapshot_file = project_root / SNAPSHOT_PATH

    if not snapshot_file.is_file():
        print(f"FAIL: snapshot not found: {SNAPSHOT_PATH}", file=sys.stderr)
        return 1

    snapshot = json.loads(snapshot_file.read_text(encoding="utf-8"))

    # Import helper to get current active set
    if str(project_root) not in sys.path:
        # guardian: allow-global-mutation
        sys.path.insert(0, str(project_root))

    from ops_scripts.ci.active_set_helper import get_active_set

    result = get_active_set(project_root)

    print("Active Set Snapshot Check:")
    print(f"  snapshot_count={snapshot['count']}  current_count={result.count}")
    print(f"  snapshot_fingerprint={snapshot['fingerprint'][:16]}...")
    print(f"  current_fingerprint={result.fingerprint[:16]}...")

    if result.fingerprint == snapshot["fingerprint"]:
        print("PASS: active set fingerprint matches snapshot")
        return 0

    # Fingerprint changed — check for bump tag
    commit_msg = os.environ.get("COMMIT_MESSAGE", "")
    if "ACTIVE_SET_SNAPSHOT_BUMP:" in commit_msg:
        print(
            f"WARN: fingerprint changed ({snapshot['count']} → {result.count}) "
            f"but ACTIVE_SET_SNAPSHOT_BUMP tag present",
        )
        # Auto-update snapshot via atomic write helper
        from ops_scripts.ci.baseline_io import write_json_atomic

        new_snapshot = {
            "count": result.count,
            "fingerprint": result.fingerprint,
            "first_10": list(result.agent_ids[:10]),
            "last_10": list(result.agent_ids[-10:]),
        }
        write_json_atomic(snapshot_file, new_snapshot)
        print(f"  AUTO-UPDATED snapshot: {snapshot['count']} → {result.count}")
        return 0

    # Drift without acknowledgement — detailed output
    print(
        "FAIL: active set fingerprint changed without ACTIVE_SET_SNAPSHOT_BUMP tag",
    )
    print(f"  old_count={snapshot['count']}  new_count={result.count}")
    print(f"  old_fingerprint={snapshot['fingerprint']}")
    print(f"  new_fingerprint={result.fingerprint}")

    old_first = snapshot.get("first_10", [])
    old_last = snapshot.get("last_10", [])
    new_first = list(result.agent_ids[:10])
    new_last = list(result.agent_ids[-10:])

    print(f"  old_first_10={old_first}")
    print(f"  new_first_10={new_first}")
    print(f"  old_last_10={old_last}")
    print(f"  new_last_10={new_last}")

    # Deterministic diff excerpt
    old_ids = set(old_first + old_last)
    new_ids = set(new_first + new_last)
    added = sorted(new_ids - old_ids)
    removed = sorted(old_ids - new_ids)
    if added:
        print(f"  added: {added}")
    if removed:
        print(f"  removed: {removed}")

    print("  Fix: add ACTIVE_SET_SNAPSHOT_BUMP:<reason> to commit message and run:")
    print(
        "    PYTHONPATH=. COMMIT_MESSAGE='ACTIVE_SET_SNAPSHOT_BUMP:<reason>' python ops_scripts/ci/active_set_snapshot_check.py",
    )

    return 1


if __name__ == "__main__":
    sys.exit(main())
