"""Corrected ADG archival verification.

Nodes counted per file:
  - module node:   resolved_path = <filepath>
  - symbol node:   adg_name LIKE 'ADG::Symbol::<filepath>::%'
"""

from __future__ import annotations

import pathlib
import sqlite3
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]
SNAPSHOT_NEW = ROOT / "artifacts" / "adg" / "adg_indexed_04232026_1442.sqlite"
SNAPSHOT_OLD = ROOT / "artifacts" / "adg" / "adg_indexed_04232026_0925.sqlite"


def archived_from_commits() -> list[str]:
    out = subprocess.run(
        ["git", "log", "--format=%H", "a7b1e1e45b^..HEAD", "--", "."],
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=False,
    ).stdout
    originals: set[str] = set()
    for sha in (s for s in out.splitlines() if s.strip()):
        subj = subprocess.run(
            ["git", "log", "-1", "--format=%s", sha],
            capture_output=True,
            text=True,
            cwd=ROOT,
            check=False,
        ).stdout.strip()
        if "wave" not in subj.lower() or "archive" not in subj.lower():
            continue
        stat = subprocess.run(
            ["git", "show", "--name-status", "-M", "--format=", sha],
            capture_output=True,
            text=True,
            cwd=ROOT,
            check=False,
        ).stdout
        for line in stat.splitlines():
            parts = line.split("\t")
            if (
                len(parts) == 3
                and parts[0].startswith("R")
                and parts[2].startswith("archives/adg_dead_code/")
            ):
                originals.add(parts[1])
            elif len(parts) == 2 and parts[0] == "D":
                originals.add(parts[1])
    return sorted(originals)


def file_total(conn: sqlite3.Connection, path: str) -> tuple[int, int]:
    """Return (module_nodes, symbol_nodes) for a file."""
    mod = conn.execute(
        "SELECT COUNT(*) FROM nodes WHERE resolved_path=? AND entity_type='module'",
        (path,),
    ).fetchone()[0]
    sym = conn.execute(
        "SELECT COUNT(*) FROM nodes WHERE entity_type='symbol' AND adg_name LIKE ?",
        (f"ADG::Symbol::{path}::%",),
    ).fetchone()[0]
    return int(mod), int(sym)


archived = archived_from_commits()
print(f"Archived files (from commits): {len(archived)}")

conn_old = sqlite3.connect(f"file:{SNAPSHOT_OLD}?mode=ro", uri=True)
conn_new = sqlite3.connect(f"file:{SNAPSHOT_NEW}?mode=ro", uri=True)

still_in_new: list[tuple[str, int, int]] = []
dropped: list[tuple[str, int, int]] = []
never: list[str] = []
total_old_mod = 0
total_old_sym = 0
total_new_mod = 0
total_new_sym = 0

for p in archived:
    o_mod, o_sym = file_total(conn_old, p)
    n_mod, n_sym = file_total(conn_new, p)
    total_old_mod += o_mod
    total_old_sym += o_sym
    total_new_mod += n_mod
    total_new_sym += n_sym
    if n_mod + n_sym > 0:
        still_in_new.append((p, n_mod, n_sym))
    elif o_mod + o_sym > 0:
        dropped.append((p, o_mod, o_sym))
    else:
        never.append(p)

print(f"\n--- SUMMARY ---")
print(f"Cleanly dropped (old>0, new=0): {len(dropped)}")
print(f"Still in new snapshot:          {len(still_in_new)}")
print(f"Never in old snapshot:          {len(never)}")

print(f"\n--- NODE ACCOUNTING (archived files only) ---")
print(f"Old snapshot: {total_old_mod} modules + {total_old_sym} symbols = {total_old_mod + total_old_sym}")
print(f"New snapshot: {total_new_mod} modules + {total_new_sym} symbols = {total_new_mod + total_new_sym}")
print(
    f"Delta:        {total_old_mod - total_new_mod} modules + {total_old_sym - total_new_sym} symbols = {(total_old_mod - total_new_mod) + (total_old_sym - total_new_sym)}"
)

# Global stats for sanity
g_old = conn_old.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
g_new = conn_new.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
print(f"\nGlobal node delta: {g_old} -> {g_new} = {g_old - g_new}")

if still_in_new:
    print(f"\n--- FILES STILL PRESENT (first 10, expected for post-regen Wave D+C.3) ---")
    for p, m, s in still_in_new[:10]:
        print(f"  {m:3d}+{s:3d}  {p}")

# Archive-path leakage check
arch_mod = conn_new.execute(
    "SELECT COUNT(*) FROM nodes WHERE resolved_path LIKE 'archives/%' OR resolved_path LIKE 'archives\\%'"
).fetchone()[0]
arch_sym = conn_new.execute(
    "SELECT COUNT(*) FROM nodes WHERE entity_type='symbol' AND "
    "(adg_name LIKE 'ADG::Symbol::archives/%' OR adg_name LIKE 'ADG::Symbol::archives\\%')"
).fetchone()[0]
print(f"\nArchive-path leakage in new snapshot: {arch_mod} modules + {arch_sym} symbols")
