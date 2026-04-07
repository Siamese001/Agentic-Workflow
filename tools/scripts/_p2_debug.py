"""Debug Phase 2 reads_through detection."""
import sqlite3
from pathlib import Path

ROOT = Path(r"C:\Git\Agentic-Workflow")
db = sorted((ROOT / "artifacts" / "adg").glob("adg_indexed_*.sqlite"))[-1]
print(f"Using: {db.name}")
conn = sqlite3.connect(str(db))

# Check sovereign_severity_types specifically
print("\n--- sovereign_severity_types ---")
for rt in ["reads_from", "reads_through"]:
    c = conn.execute(
        "SELECT COUNT(*) FROM edges WHERE source_file LIKE ? AND relation_type=?",
        ("%sovereign_severity_types%", rt),
    ).fetchone()[0]
    print(f"  {rt}: {c}")

# Total reads_through breakdown
print("\n--- reads_through by source_file (top 20) ---")
for r in conn.execute(
    "SELECT source_file, COUNT(*) as c FROM edges "
    "WHERE relation_type='reads_through' GROUP BY source_file ORDER BY c DESC LIMIT 20",
).fetchall():
    print(f"  {r[0]}: {r[1]}")

# Check if reads_from decreased for patched modules
print("\n--- reads_from for patched modules ---")
patched = [
    "sovereign_severity_types", "request_type_util", "schema_type_types",
    "resume_analysis_plan_types", "metric_type_util", "scenario_runner",
]
for m in patched:
    rf = conn.execute(
        "SELECT COUNT(*) FROM edges WHERE source_file LIKE ? AND relation_type='reads_from'",
        (f"%{m}%",),
    ).fetchone()[0]
    rt = conn.execute(
        "SELECT COUNT(*) FROM edges WHERE source_file LIKE ? AND relation_type='reads_through'",
        (f"%{m}%",),
    ).fetchone()[0]
    print(f"  {m}: reads_from={rf}, reads_through={rt}")

# Check old vs new ADG for reads_from on sovereign_severity_types
old_db = ROOT / "artifacts" / "adg" / "adg_indexed_03162026_1613.sqlite"
if old_db.exists():
    conn2 = sqlite3.connect(str(old_db))
    old_rf = conn2.execute(
        "SELECT COUNT(*) FROM edges WHERE source_file LIKE ? AND relation_type='reads_from'",
        ("%sovereign_severity_types%",),
    ).fetchone()[0]
    print(f"\n--- Old ADG (1613) sovereign_severity_types reads_from: {old_rf}")
    conn2.close()

# Check edge_kind breakdown for reads_through
print("\n--- reads_through by edge_kind ---")
for r in conn.execute(
    "SELECT edge_kind, COUNT(*) FROM edges WHERE relation_type='reads_through' GROUP BY edge_kind",
).fetchall():
    print(f"  {r[0]}: {r[1]}")

conn.close()
