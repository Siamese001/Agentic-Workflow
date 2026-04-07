"""Apply guardian exemptions to has_reraise broad_exception_catch entries.

HITL-approved (SVP Engineering, Option 1):
- 426 log_then_reraise + transform_then_reraise: guardian-exempt as intentional error boundary
- 3 pure_reraise: handler removed entirely (adds zero value)

Usage:
    python tools/evidence/_apply_reraise_exemptions.py           # dry-run
    python tools/evidence/_apply_reraise_exemptions.py --apply   # write
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

ENRICHED_PATH = Path("artifacts/adg_analysis/has_reraise_enriched.json")
JUSTIFICATION = "intentional error boundary, re-raises all caught exceptions to caller"
GUARDIAN_COMMENT = f"  # guardian: allow-broad-exception -- {JUSTIFICATION}"


def _find_handler_lines(src: str, target_lineno: int) -> tuple[int, int]:
    """Return (handler_start_0idx, handler_end_0idx) for except block at target_lineno."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return (-1, -1)
    lines = src.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and node.lineno == target_lineno:
            end = getattr(node, "end_lineno", node.lineno)
            return (node.lineno - 1, end - 1)
    return (-1, -1)


def apply_exemptions(dry_run: bool = True) -> None:
    entries = json.loads(ENRICHED_PATH.read_text())
    reraise_types = {"log_then_reraise", "transform_then_reraise", "pure_reraise"}
    candidates = [e for e in entries if e.get("reraise_type") in reraise_types]
    print(f"has_reraise candidates: {len(candidates)}  (dry_run={dry_run})")

    applied_exempt = 0
    removed_handlers = 0
    skipped: list[str] = []

    for entry in candidates:
        fpath = Path(entry["source_file"])
        line_no = int(entry["line_no"]) - 1  # 0-indexed
        reraise_type = entry.get("reraise_type", "")

        if not fpath.exists():
            skipped.append(f"MISSING: {entry['source_file']}")
            continue

        lines = fpath.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)

        if line_no >= len(lines):
            skipped.append(f"LINE_OOB: {entry['source_file']}:{entry['line_no']}")
            continue

        original_line = lines[line_no]
        stripped = original_line.rstrip("\n\r")

        if "except" not in stripped:
            skipped.append(f"NOT_EXCEPT: {entry['source_file']}:{entry['line_no']} => {stripped!r}")
            continue

        if reraise_type == "pure_reraise":
            # Remove the entire handler block
            src = "".join(lines)
            start_0, end_0 = _find_handler_lines(src, int(entry["line_no"]))
            if start_0 < 0:
                skipped.append(f"HANDLER_NOT_FOUND: {entry['source_file']}:{entry['line_no']}")
                continue
            print(f"  {'DRY' if dry_run else 'REMOVE'} pure_reraise  {entry['source_file']}:{entry['line_no']}")
            for i in range(start_0, min(end_0 + 1, len(lines))):
                print(f"    - {lines[i].rstrip()}")
            if not dry_run:
                del lines[start_0:end_0 + 1]
                fpath.write_text("".join(lines), encoding="utf-8")
            removed_handlers += 1
            continue

        # log_then_reraise or transform_then_reraise — add guardian comment
        if "guardian:" in stripped:
            skipped.append(f"ALREADY_EXEMPT: {entry['source_file']}:{entry['line_no']}")
            continue

        ending = original_line[len(stripped):]
        new_line = f"{stripped}{GUARDIAN_COMMENT}{ending}"

        print(f"  {'DRY' if dry_run else 'APPLY'}  [{reraise_type}]  {entry['source_file']}:{entry['line_no']}")
        print(f"    before: {stripped!r}")
        print(f"    after:  {new_line.rstrip()!r}")

        if not dry_run:
            lines[line_no] = new_line
            fpath.write_text("".join(lines), encoding="utf-8")
        applied_exempt += 1

    print(f"\nExemptions applied: {applied_exempt}")
    print(f"Pure-reraise handlers removed: {removed_handlers}")
    print(f"Skipped: {len(skipped)}")
    for s in skipped[:20]:
        print(f"  {s}")
    if len(skipped) > 20:
        print(f"  ... and {len(skipped) - 20} more")


if __name__ == "__main__":
    dry_run = "--apply" not in sys.argv
    apply_exemptions(dry_run=dry_run)
