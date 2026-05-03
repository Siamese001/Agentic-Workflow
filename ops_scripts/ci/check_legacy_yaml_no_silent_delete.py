"""CI gate: no silent deletion of legacy YAML files.

Plan: `.windsurf/plans/legacy-yaml-deletion-audit-c8e3a4.md`.
Author-Gate: `dec_19dedcd1c109ebf25` (option_a_lock_in_doctrine).

Enforces: any of the 13 enumerated legacy YAML files MUST exist on
disk OR be accompanied by an `AUTHOR_GATE_PACKET:` marker referencing
`legacy-yaml-deletion-audit-c8e3a4` in the recent capture queue.

This catches the failure mode where the file is deleted without going
through the per-file Author-Gate that the plan requires for each
MIGRATION_CANDIDATE.

The 13 enumerated files come from the canonical DISPOSITIONS table in
`ops_scripts/maintenance/legacy_yaml_disposition.py`. If the table
shrinks (a file is legitimately deleted via Author-Gate), the gate
re-tightens to the new shorter list automatically.

Bypass: `LEGACY_YAML_DELETION_BYPASS=1` (logged).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MARKERS_FILE = REPO_ROOT / "artifacts" / "capture" / "markers.jsonl"
PLAN_SLUG = "legacy-yaml-deletion-audit-c8e3a4"


def _enumerated_files() -> list[str]:
    """Return rel_paths from the canonical DISPOSITIONS table."""
    sys.path.insert(0, str(REPO_ROOT))
    from ops_scripts.maintenance.legacy_yaml_disposition import (  # noqa: PLC0415
        DISPOSITIONS,
    )

    return [d.rel_path for d in DISPOSITIONS]


def _author_gate_authorizes_deletion(rel_path: str) -> bool:
    """Scan recent markers for an AG packet authorizing deletion of rel_path."""
    if not MARKERS_FILE.is_file():
        return False
    for line in MARKERS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        text = row.get("raw") or row.get("text") or ""
        if PLAN_SLUG in text and rel_path in text:
            return True
    return False


def check(repo_root: Path = REPO_ROOT) -> int:
    if os.getenv("LEGACY_YAML_DELETION_BYPASS") == "1":
        print("[check_legacy_yaml_no_silent_delete] BYPASS=1 — gate disabled", file=sys.stderr)
        return 0

    enumerated = _enumerated_files()
    missing: list[str] = []
    authorized: list[str] = []
    for rel_path in enumerated:
        path = repo_root / rel_path
        if not path.is_file():
            if _author_gate_authorizes_deletion(rel_path):
                authorized.append(rel_path)
            else:
                missing.append(rel_path)

    if missing:
        print(
            f"[check_legacy_yaml_no_silent_delete] FAIL — {len(missing)} file(s) missing without Author-Gate authorization:",
            file=sys.stderr,
        )
        for m in missing:
            print(f"  - {m}", file=sys.stderr)
        print(
            "\nFix: either restore the file, OR run an Author-Gate referencing "
            f"plan {PLAN_SLUG} + the file path before deleting.\n"
            f"Plan: .windsurf/plans/{PLAN_SLUG}.md.\n"
            "Bypass: LEGACY_YAML_DELETION_BYPASS=1 (logged).",
            file=sys.stderr,
        )
        return 1

    msg = f"[check_legacy_yaml_no_silent_delete] OK — {len(enumerated)} files enumerated"
    if authorized:
        msg += f"; {len(authorized)} authorized-for-deletion via Author-Gate"
    print(msg)
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Legacy YAML no-silent-delete gate")
    p.add_argument("--root", type=Path, default=REPO_ROOT)
    args = p.parse_args(argv)
    return check(args.root)


if __name__ == "__main__":
    sys.exit(main())
