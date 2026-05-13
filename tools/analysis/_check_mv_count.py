"""One-shot: check new snapshot MV counts and query v_p0_apps_direct_infra."""
import sqlite3
from pathlib import Path

adg_dir = Path("artifacts/adg")
snaps = sorted(adg_dir.glob("adg_indexed_*.sqlite"), key=lambda p: p.stat().st_mtime, reverse=True)
if not snaps:
    print("No snapshot found")
else:
    snap = snaps[0]
    print(f"Latest snapshot: {snap.name}")
    conn = sqlite3.connect(str(snap))

    mv_objects = conn.execute(
        "SELECT name FROM sqlite_master WHERE type IN ('table','view') AND name LIKE 'mv_%'"
    ).fetchall()
    medium_count = conn.execute(
        "SELECT COUNT(*) FROM violations WHERE severity='MEDIUM' AND category='antipattern'"
    ).fetchone()[0]
    print(f"mv_* objects: {len(mv_objects)}, MEDIUM antipatterns: {medium_count}")

    # Check v_p0_apps_direct_infra
    view_check = conn.execute(
        "SELECT name FROM sqlite_master WHERE name='v_p0_apps_direct_infra'"
    ).fetchall()
    if view_check:
        rows = conn.execute("SELECT * FROM v_p0_apps_direct_infra LIMIT 10").fetchall()
        desc = conn.execute("SELECT * FROM v_p0_apps_direct_infra LIMIT 1").description
        if desc:
            print("Columns:", [d[0] for d in desc])
        print(f"v_p0_apps_direct_infra rows ({len(rows)}):")
        for r in rows:
            print(" ", r)
    else:
        print("v_p0_apps_direct_infra view not found")

    conn.close()
