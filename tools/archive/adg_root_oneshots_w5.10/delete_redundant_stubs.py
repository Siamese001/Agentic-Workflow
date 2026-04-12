"""
Delete redundant ADG stubs and generate stubs for uncovered modules.

Default: Execute deletions (heal mode)
Use --report for report-only mode (CI-friendly)

Phase 1: Delete _adg stub files whose covered modules are ALL also covered
         by at least one non-_adg behavioral test.
Phase 2: Report uncovered modules that need new stubs.
"""

from __future__ import annotations

import glob
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def main(dry_run: bool = True) -> None:
    db = sorted(glob.glob(str(PROJECT_ROOT / "artifacts/adg/adg_indexed_*.sqlite")))[-1]
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row

    src_mods = {
        r["resolved_path"]
        for r in conn.execute(
            "SELECT resolved_path FROM nodes "
            "WHERE entity_type='module' "
            "AND resolved_path LIKE 'agentic_core/%' "
            "AND resolved_path NOT LIKE '%__pycache__%' ",
        )
    }

    cov_rows = list(
        conn.execute(
            "SELECT DISTINCT n1.resolved_path as test_file, n2.resolved_path as src_file "
            "FROM edges e "
            "JOIN nodes n1 ON e.src_id=n1.id "
            "JOIN nodes n2 ON e.dst_id=n2.id "
            "WHERE e.relation_type='imports' "
            "AND n1.resolved_path LIKE 'tests/%' "
            "AND n2.resolved_path LIKE 'agentic_core/%' "
            "AND n2.resolved_path NOT LIKE '%__pycache__%' ",
        ),
    )

    test_to_covered: dict[str, set[str]] = defaultdict(set)
    for r in cov_rows:
        sf = r["src_file"].split("::")[0]
        if sf in src_mods:
            test_to_covered[r["test_file"]].add(sf)

    stub_files = [tf for tf in test_to_covered if Path(tf).stem.endswith("_adg")]
    non_stub_files = [tf for tf in test_to_covered if not Path(tf).stem.endswith("_adg")]

    non_stub_covered: set[str] = set()
    for tf in non_stub_files:
        non_stub_covered |= test_to_covered[tf]

    # Redundant: stub covers nothing that behavioral tests don't already cover
    redundant = sorted(tf for tf in stub_files if test_to_covered[tf] <= non_stub_covered)
    useful = sorted(tf for tf in stub_files if test_to_covered[tf] - non_stub_covered)

    print(f"Total _adg stubs with coverage edges: {len(stub_files)}")
    print(f"  Redundant (safe to delete):   {len(redundant)}")
    print(f"  Useful (provide unique coverage): {len(useful)}")
    print()

    deleted = 0
    missing = 0
    for rel_path in redundant:
        abs_path = PROJECT_ROOT / rel_path
        if abs_path.exists():
            if dry_run:
                print(f"  [DRY] would delete: {rel_path}")
            else:
                abs_path.unlink()
                # Remove empty parent dirs
                for parent in abs_path.parents:
                    try:
                        if parent == PROJECT_ROOT:
                            break
                        parent.rmdir()
                    except OSError:  # guardian: Add error context logging
                        break
                deleted += 1
        else:
            missing += 1

    if dry_run:
        print(f"\nDRY RUN complete. Would delete {len(redundant)} files.")
    else:
        print(f"\nDeleted {deleted} redundant stubs. ({missing} not found on disk)")

    # Also report stubs that exist on disk but have NO coverage edges at all
    # (they import nothing from agentic_core, so ADG never registered them)
    all_adg_test_files_on_disk = set()
    for p in (PROJECT_ROOT / "tests").rglob("*_adg.py"):
        rel = p.relative_to(PROJECT_ROOT).as_posix()
        all_adg_test_files_on_disk.add(rel)

    known_in_adg = set(stub_files)
    ghosts = all_adg_test_files_on_disk - known_in_adg
    print(f"\nADG stub files on disk with NO coverage edges registered: {len(ghosts)}")
    if ghosts and dry_run:
        print("  (sample of 10):")
        for f in sorted(ghosts)[:10]:
            print(f"    {f}")

    conn.close()
    return redundant, useful, ghosts


if __name__ == "__main__":
    report_only = "--report" in sys.argv or "-r" in sys.argv
    main(dry_run=report_only)


def find_redundant():
    return []
