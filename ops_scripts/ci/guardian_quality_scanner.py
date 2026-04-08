"""
Guardian Quality Scanner — W3.7

Ratchet gate for guardian comment quality. Tracks the count of:
  1. Lines with duplicate guardian annotations (zero-tolerance)
  2. Lines with missing/weak justifications (ratchet ceiling)

Used as a CI gate. Ratchet file: artifacts/guardian_quality_ratchet.json

Exit codes:
  0 — all checks pass
  1 — ratchet exceeded or duplicates found

Environment:
  GUARDIAN_INIT=1    — initialise ratchet from current state, exit 0
  GUARDIAN_DRY_RUN=1 — report without updating ratchet
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RATCHET_FILE = ROOT / "artifacts" / "guardian_quality_ratchet.json"

PRODUCTION_DIRS = ["agentic_core", "apps_eval", "apps_exec", "apps_lic",
                   "apps_research", "apps_rfp", "apps_rg", "apps_shared", "system_learning"]


def _run_scan() -> tuple[int, int]:
    """Run idempotency scan. Returns (duplicate_count, weak_justification_count)."""
    sys.path.insert(0, str(ROOT))
    from tools.guardian.idempotency_check import scan_paths

    targets = []
    for dirname in PRODUCTION_DIRS:
        p = ROOT / dirname
        if p.exists():
            targets.append(p)

    issues = scan_paths(targets)
    duplicates = sum(1 for i in issues if i["issue"].startswith("DUPLICATE"))
    weak = sum(1 for i in issues if i["issue"].startswith("WEAK"))

    if duplicates > 0:
        print(f"[guardian-quality] DUPLICATE guardian annotations: {duplicates} lines", file=sys.stderr)
        for i in issues:
            if i["issue"].startswith("DUPLICATE"):
                print(f"  {i['file']}:{i['line_no']}  {i['issue']}", file=sys.stderr)

    print(f"[guardian-quality] Weak justifications: {weak} lines (duplicates: {duplicates})")
    return duplicates, weak


def _load_ratchet() -> dict:
    if RATCHET_FILE.exists():
        try:
            return json.loads(RATCHET_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(
                f"[guardian-quality] WARNING: ratchet file corrupt ({exc}); treating as empty — "
                "run with GUARDIAN_INIT=1 to reinitialise",
                file=sys.stderr,
            )
        except OSError as exc:
            print(
                f"[guardian-quality] WARNING: cannot read ratchet file ({exc})",
                file=sys.stderr,
            )
    return {}


def _save_ratchet(data: dict) -> None:
    RATCHET_FILE.parent.mkdir(parents=True, exist_ok=True)
    RATCHET_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def main() -> int:
    init_mode = os.environ.get("GUARDIAN_INIT") == "1"
    dry_run = os.environ.get("GUARDIAN_DRY_RUN") == "1"

    duplicates, weak = _run_scan()

    if init_mode:
        ratchet = {"duplicate_ceiling": 0, "weak_justification_ceiling": weak}
        _save_ratchet(ratchet)
        print(f"[guardian-quality] Ratchet initialised: duplicate_ceiling=0, weak_ceiling={weak}")
        return 0

    ratchet = _load_ratchet()
    dup_ceiling = ratchet.get("duplicate_ceiling", 0)
    weak_ceiling = ratchet.get("weak_justification_ceiling", weak)

    failed = False

    if duplicates > dup_ceiling:
        print(
            f"[guardian-quality] BLOCKED: duplicate guardian annotations {duplicates} > ceiling {dup_ceiling}",
            file=sys.stderr,
        )
        failed = True

    if weak > weak_ceiling:
        print(
            f"[guardian-quality] BLOCKED: weak justifications {weak} > ceiling {weak_ceiling} (regression detected)",
            file=sys.stderr,
        )
        failed = True
    elif weak < weak_ceiling and not dry_run:
        new_ceiling = weak
        ratchet["weak_justification_ceiling"] = new_ceiling
        _save_ratchet(ratchet)
        print(f"[guardian-quality] Ratchet tightened: weak_ceiling {weak_ceiling} → {new_ceiling}")

    if failed:
        return 1

    print(f"[guardian-quality] PASS — duplicates={duplicates}/{dup_ceiling}, weak={weak}/{weak_ceiling}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
