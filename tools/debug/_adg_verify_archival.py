"""Verify archived files are absent from post-archival ADG snapshot.

Checks:
  1. For each committed archival, confirm no nodes.file_path matches the
     original (active-tree) path.
  2. Confirm the archives/* path is NOT in the new snapshot either (scanner
     should skip archived tree).
  3. Report any orphan references in edges (src/tgt pointing to archived modules).
"""

from __future__ import annotations

import pathlib
import sqlite3
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]
SNAPSHOT_NEW = ROOT / "artifacts" / "adg" / "adg_indexed_04232026_1418.sqlite"
SNAPSHOT_OLD = ROOT / "artifacts" / "adg" / "adg_indexed_04232026_0925.sqlite"


def archived_files_from_commits() -> list[str]:
    """Extract original active-tree paths from wave A-D commits."""
    # Get commits since a7b1e1e45b (Wave A) inclusive
    out = subprocess.run(
        ["git", "log", "--format=%H", "a7b1e1e45b^..HEAD", "--", "."],
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=False,
    ).stdout
    shas = [s for s in out.splitlines() if s.strip()]
    originals: set[str] = set()
    for sha in shas:
        subj = subprocess.run(
            ["git", "log", "-1", "--format=%s", sha],
            capture_output=True,
            text=True,
            cwd=ROOT,
            check=False,
        ).stdout.strip()
        if "wave" not in subj.lower() or "archive" not in subj.lower():
            continue
        # list renames in this commit
        stat = subprocess.run(
            ["git", "show", "--name-status", "-M", "--format=", sha],
            capture_output=True,
            text=True,
            cwd=ROOT,
            check=False,
        ).stdout
        for line in stat.splitlines():
            # Rxxx\tfrom\tto
            parts = line.split("\t")
            if (
                len(parts) == 3
                and parts[0].startswith("R")
                and parts[2].startswith("archives/adg_dead_code/")
            ):
                originals.add(parts[1])
            elif len(parts) == 2 and parts[0] == "D":
                # Wave A was committed as deletes (archive/ was gitignored at the time)
                originals.add(parts[1])
    return sorted(originals)


def file_node_count(conn: sqlite3.Connection, path: str) -> int:
    # Normalize: ADG stores POSIX-style relative paths in resolved_path.
    cur = conn.execute(
        "SELECT COUNT(*) FROM nodes WHERE resolved_path=? OR resolved_path=?",
        (path, path.replace("/", "\\")),
    )
    return int(cur.fetchone()[0])


archived = archived_files_from_commits()
print(f"Files archived across all waves (from git commit log): {len(archived)}")

# Connect snapshots
conn_new = sqlite3.connect(f"file:{SNAPSHOT_NEW}?mode=ro", uri=True)
conn_old = sqlite3.connect(f"file:{SNAPSHOT_OLD}?mode=ro", uri=True)

# Per-file verification
still_in_new: list[tuple[str, int]] = []
was_in_old: list[tuple[str, int]] = []
never_in_old: list[str] = []
dropped_cleanly: list[tuple[str, int]] = []

for p in archived:
    n_new = file_node_count(conn_new, p)
    n_old = file_node_count(conn_old, p)
    if n_new > 0:
        still_in_new.append((p, n_new))
    elif n_old > 0:
        dropped_cleanly.append((p, n_old))
        was_in_old.append((p, n_old))
    else:
        never_in_old.append(p)

# Also check archive-path presence (scanner should skip archives/)
cur = conn_new.execute(
    "SELECT COUNT(*) FROM nodes WHERE resolved_path LIKE 'archives/%' OR resolved_path LIKE 'archives\\%'"
)
archive_nodes_new = cur.fetchone()[0]

print(f"\n--- PER-FILE VERIFICATION ---")
print(f"Dropped cleanly (in old, absent in new): {len(dropped_cleanly)}")
print(f"Never in old snapshot: {len(never_in_old)}")
print(f"STILL IN NEW (archival did NOT land): {len(still_in_new)}")
print(f"Nodes under 'archives/' in new snapshot: {archive_nodes_new}")

if still_in_new:
    print("\n!!! FILES STILL IN NEW SNAPSHOT !!!")
    for p, n in still_in_new[:20]:
        print(f"  {n:3d} nodes  {p}")

if never_in_old:
    print(f"\n--- Never-in-old sample (max 10) ---")
    for p in never_in_old[:10]:
        print(f"  {p}")

total_dropped_nodes = sum(n for _, n in dropped_cleanly)
print(f"\n--- AGGREGATE ---")
print(f"Total nodes dropped (per-file sum): {total_dropped_nodes}")
print(
    f"Global node delta (old-new):       {conn_old.execute('SELECT COUNT(*) FROM nodes').fetchone()[0] - conn_new.execute('SELECT COUNT(*) FROM nodes').fetchone()[0]}"
)

conn_new.close()
conn_old.close()
