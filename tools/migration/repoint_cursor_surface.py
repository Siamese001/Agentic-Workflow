#!/usr/bin/env python3
"""Repoint a .cursor/<surface> mirror to its .claude SSOT across consumers.

Reads the consumer file list from artifacts/migration/cursor_reference_map.json
(consumer_files_by_subpath) for a given surface, then replaces the literal
``.cursor/<surface>`` with ``.claude/<target>`` in each consumer, EXCEPT files on
the denylist (which intentionally keep .cursor refs or need bespoke handling).

For .py files: py_compile after rewrite; auto-revert that file on failure.
Idempotent: re-running is a no-op once refs are repointed.

Usage:
    python tools/migration/repoint_cursor_surface.py --surface skills --target skills --dry-run
    python tools/migration/repoint_cursor_surface.py --surface rules  --target rules  --apply
"""
from __future__ import annotations

import argparse
import json
import py_compile
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MAP = REPO_ROOT / "artifacts/migration/cursor_reference_map.json"

# Files that MUST keep their .cursor/<surface> references (intentional/historical)
# or require bespoke handling outside this mechanical rewrite.
DENYLIST = {
    "agentic_core/L0_routing/config/path_constants.py",      # intentional CURSOR_* constants (W0)
    "tools/migration/cursor_reference_map.py",               # the reporter scans .cursor by design
    "tools/migration/repoint_cursor_surface.py",             # this tool
    "ops_scripts/maintenance/rewrite_windsurf_refs_to_cursor.py",  # historical migration tool
    "tools/migration/deprecate_windsurf_refs.py",            # historical migration tool
    "ops_scripts/ci/check_cursor_governance_mirror_health.py",     # obsolete gate (separate removal)
    "ops_scripts/ci/governance_w2_dedupe_report.py",         # obsolete one-time report
    "scripts/governance/verify_codex_backup.py",             # untracked peer work — do not touch
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--surface", required=True, help="e.g. skills (matches .cursor/<surface>)")
    ap.add_argument("--target", required=True, help="e.g. skills (becomes .claude/<target>)")
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    old = f".cursor/{args.surface}"
    new = f".claude/{args.target}"
    report = json.loads(MAP.read_text(encoding="utf-8"))
    consumers = report.get("consumer_files_by_subpath", {}).get(old, [])

    changed, skipped, reverted = [], [], []
    for rel in consumers:
        if rel in DENYLIST:
            skipped.append(rel)
            continue
        p = REPO_ROOT / rel
        if not p.is_file():
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            skipped.append(rel + " (unreadable)")
            continue
        if old not in text:
            continue
        new_text = text.replace(old, new)
        if not args.apply:
            changed.append(f"{rel} ({text.count(old)} refs)")
            continue
        p.write_text(new_text, encoding="utf-8")
        if p.suffix == ".py":
            try:
                py_compile.compile(str(p), doraise=True)
            except py_compile.PyCompileError as exc:
                p.write_text(text, encoding="utf-8")  # auto-revert
                reverted.append(f"{rel}: {exc}")
                continue
        changed.append(f"{rel} ({text.count(old)} refs)")

    verb = "WOULD CHANGE" if args.dry_run else "CHANGED"
    print(f"surface {old} -> {new}")
    print(f"{verb}: {len(changed)}  | denylist-skipped: {len(skipped)}  | reverted: {len(reverted)}")
    for c in changed:
        print(f"  ~ {c}")
    if skipped:
        print("  denylist/skipped:")
        for s in skipped:
            print(f"    - {s}")
    if reverted:
        print("  REVERTED (compile fail):")
        for r in reverted:
            print(f"    ! {r}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
