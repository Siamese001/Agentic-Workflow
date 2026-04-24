"""Invoke phase2 disposition processor against current snapshot and report delta."""
from pathlib import Path
import sqlite3
import sys

import glob
import os
DB = Path(sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"), key=os.path.getmtime)[-1])
print(f"Using latest snapshot: {DB}")


def main() -> int:
    con = sqlite3.connect(str(DB))
    before = con.execute(
        "SELECT id, file_path, disposition, severity FROM violations WHERE severity='HIGH'"
    ).fetchall()
    print("BEFORE:")
    for r in before:
        print(f"  {r}")
    con.close()

    from agentic_core.adg.processing.phase2_disposition_processor import (
        run_phase2_disposition_processing,
    )
    result = run_phase2_disposition_processing(DB)
    print(f"\nphase2 result: {result}")

    con = sqlite3.connect(str(DB))
    after = con.execute(
        "SELECT id, file_path, disposition, disposition_source, severity FROM violations WHERE severity='HIGH'"
    ).fetchall()
    print("\nAFTER:")
    for r in after:
        print(f"  {r}")

    # Total dispositions now
    counts = con.execute(
        "SELECT disposition, COUNT(*) FROM violations WHERE category='antipattern' "
        "GROUP BY disposition ORDER BY COUNT(*) DESC"
    ).fetchall()
    print("\nAll antipattern disposition counts:")
    for d, n in counts:
        print(f"  {n:>6}  {d}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
