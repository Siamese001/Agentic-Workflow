#!/usr/bin/env python3
"""Requirements ↔ ADG ↔ test crosswalk CI gate.

W4.2 of plan ``assurance-p1-gates-ab4758``. Builds the crosswalk artifact
from ``config/crosswalk/obligations.yaml`` and fails closed when:

  - The registry has duplicate ``id`` values.
  - Any obligation's ``gate_script`` does not exist on disk.
  - Any obligation's ``test_ids`` reference a non-existent file.

Exit codes:
    0  All obligations resolved cleanly.
    1  Unresolved references — registry-vs-disk drift.
    2  Infrastructure error (missing registry, malformed YAML, etc).
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.crosswalk.build_requirements_crosswalk import (  # noqa: E402
    DEFAULT_OUTPUT,
    DEFAULT_REGISTRY,
    build_crosswalk,
    write_crosswalk,
)


def main() -> int:
    print("🔍 Requirements ↔ ADG ↔ Test crosswalk gate")
    try:
        crosswalk = build_crosswalk(registry_path=DEFAULT_REGISTRY)
    except (FileNotFoundError, ValueError) as exc:
        print(f"❌ crosswalk build failed: {exc}", file=sys.stderr)
        return 2

    write_crosswalk(crosswalk, DEFAULT_OUTPUT)
    print(f"📄 artifact: {DEFAULT_OUTPUT.relative_to(REPO_ROOT)}")
    print(
        f"  total: {crosswalk['total_obligations']}, "
        f"resolved: {crosswalk['resolved_count']}, "
        f"unresolved: {crosswalk['unresolved_count']}"
    )

    rc = 0
    if crosswalk["ids_with_duplicates"]:
        print("❌ duplicate obligation ids:")
        for dup in crosswalk["ids_with_duplicates"]:
            print(f"  - {dup}")
        rc = 1

    unresolved = [
        o for o in crosswalk["obligations"]
        if not o["gate_script_resolved"] or o["unresolved_test_ids"]
    ]
    if unresolved:
        print("❌ unresolved obligations:")
        for o in unresolved:
            line = f"  - {o['id']}: source={o['source']}"
            if not o["gate_script_resolved"]:
                line += f"  ⚠ gate_script_missing={o['gate_script']!r}"
            if o["unresolved_test_ids"]:
                line += f"  ⚠ unresolved_tests={o['unresolved_test_ids']}"
            print(line)
        rc = 1

    if rc == 0:
        print("✅ all obligations resolve to a gate + at least one test")
    return rc


if __name__ == "__main__":
    sys.exit(main())
