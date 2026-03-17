"""Check if reads_from +538 increase is from new files or existing files."""
import glob
import os
import sqlite3

ADG_DIR = r"C:\Git\Agentic-Workflow\artifacts\adg"

# Pre-rollback DB
pre_db = r"C:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_03162026_1654.sqlite"
# Post-rollback DB (latest)
files = sorted(glob.glob(os.path.join(ADG_DIR, "adg_indexed_*.sqlite")))
post_db = files[-1]

pre_conn = sqlite3.connect(pre_db)
post_conn = sqlite3.connect(post_db)

# Get reads_from source_files in each
pre_files = set(r[0] for r in pre_conn.execute(
    "SELECT DISTINCT source_file FROM edges WHERE relation_type='reads_from'"
).fetchall())
post_files = set(r[0] for r in post_conn.execute(
    "SELECT DISTINCT source_file FROM edges WHERE relation_type='reads_from'"
).fetchall())

new_files = post_files - pre_files
removed_files = pre_files - post_files

print(f"Pre reads_from files: {len(pre_files)}")
print(f"Post reads_from files: {len(post_files)}")
print(f"New files with reads_from: {len(new_files)}")
print(f"Removed files: {len(removed_files)}")

if new_files:
    # Count edges from new files
    placeholders = ",".join(["?"] * len(new_files))
    new_edges = post_conn.execute(
        f"SELECT COUNT(*) FROM edges WHERE relation_type='reads_from' AND source_file IN ({placeholders})",
        list(new_files)
    ).fetchone()[0]
    print(f"Edges from new files: {new_edges}")
    print("New files (first 10):")
    for f in sorted(new_files)[:10]:
        cnt = post_conn.execute(
            "SELECT COUNT(*) FROM edges WHERE relation_type='reads_from' AND source_file=?", (f,)
        ).fetchone()[0]
        print(f"  {f}: {cnt} edges")

# Module count comparison
pre_mods = pre_conn.execute("SELECT COUNT(DISTINCT source_file) FROM edges").fetchone()[0]
post_mods = post_conn.execute("SELECT COUNT(DISTINCT source_file) FROM edges").fetchone()[0]
print(f"\nTotal source files: {pre_mods} -> {post_mods} ({post_mods - pre_mods:+d})")

pre_conn.close()
post_conn.close()
