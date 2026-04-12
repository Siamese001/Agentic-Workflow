"""Apply teardown guardian exemptions approved in HITL gate (Option C).

For each teardown entry in hitl_guardian_candidates.json:
- Reads the source file
- Finds the except clause at the given line_no
- Appends guardian comment to that line if not already present
- Writes the file back

Only touches lines that match 'except' and don't already have a guardian comment.
Dry-run by default; pass --apply to write.

Usage:
    python tools/evidence/_apply_teardown_exemptions.py           # dry-run
    python tools/evidence/_apply_teardown_exemptions.py --apply   # write changes
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

CANDIDATES_PATH = Path("artifacts/adg_analysis/hitl_guardian_candidates.json")

KIND_TO_GUARDIAN = {
    "log_and_swallow": "allow-log-and-swallow",
    "silent_exception_swallow": "allow-silent-swallow",
    "return_none_swallow": "allow-return-none-swallow",
    "broad_exception_catch": "allow-broad-exception",
}

TEARDOWN_JUSTIFICATION = "teardown/cleanup context -- swallow is conventional in resource-release paths"


def apply_exemptions(dry_run: bool = True) -> None:
    candidates = json.loads(CANDIDATES_PATH.read_text())
    teardowns = [c for c in candidates if c["sub_category"] == "teardown"]
    print(f"Teardown candidates: {len(teardowns)}  (dry_run={dry_run})")

    changed_files: set[str] = set()
    skipped: list[str] = []
    applied: list[str] = []

    for entry in teardowns:
        fpath = Path(entry["source_file"])
        line_no = int(entry["line_no"]) - 1  # 0-indexed
        kind = entry["kind"]
        guardian_type = KIND_TO_GUARDIAN.get(kind, "allow-exception")

        if not fpath.exists():
            skipped.append(f"MISSING: {entry['source_file']}")
            continue

        lines = fpath.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)

        if line_no >= len(lines):
            skipped.append(f"LINE_OOB: {entry['source_file']}:{entry['line_no']}")
            continue

        original_line = lines[line_no]
        stripped = original_line.rstrip("\n\r")

        # Verify the line is an except clause
        if "except" not in stripped:
            skipped.append(f"NOT_EXCEPT: {entry['source_file']}:{entry['line_no']} => {stripped!r}")
            continue

        # Skip if guardian comment already present
        if "guardian:" in stripped:
            skipped.append(f"ALREADY_EXEMPT: {entry['source_file']}:{entry['line_no']}")
            continue

        # Build new line
        ending = original_line[len(stripped) :]  # preserve \n
        new_line = f"{stripped}  # guardian: {guardian_type} -- {TEARDOWN_JUSTIFICATION}{ending}"

        print(f"  {'DRY' if dry_run else 'APPLY'}  {entry['source_file']}:{entry['line_no']}")
        print(f"    before: {stripped!r}")
        print(f"    after:  {new_line.rstrip()!r}")

        if not dry_run:
            lines[line_no] = new_line
            fpath.write_text("".join(lines), encoding="utf-8")
            changed_files.add(str(fpath))

        applied.append(f"{entry['source_file']}:{entry['line_no']}")

    print(f"\nApplied: {len(applied)}")
    print(f"Skipped: {len(skipped)}")
    for s in skipped:
        print(f"  {s}")
    if not dry_run:
        print(f"\nFiles modified: {len(changed_files)}")


if __name__ == "__main__":
    dry_run = "--apply" not in sys.argv
    apply_exemptions(dry_run=dry_run)
