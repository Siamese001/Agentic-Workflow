# Test if the fix worked
import sqlite3

conn = sqlite3.connect("artifacts/adg/adg_indexed_03272026_2022.sqlite")

# Check if raw edge kind fallbacks are fixed
cursor = conn.execute("SELECT COUNT(*) FROM edges WHERE semantic_type == edge_kind")
raw_count = cursor.fetchone()[0]
print(f"Raw edge kind fallbacks: {raw_count}")

# Check specific problematic edge kinds
problem_kinds = ["reads_runtime_state", "reads_policy_state", "layer_membership"]
for kind in problem_kinds:
    cursor = conn.execute(
        "SELECT COUNT(*) FROM edges WHERE edge_kind = ? AND semantic_type = ?", (kind, kind)
    )
    count = cursor.fetchone()[0]
    print(f"  {kind}: {count} raw fallbacks")

# Check if they now have proper semantic types
for kind in problem_kinds:
    cursor = conn.execute("SELECT DISTINCT semantic_type FROM edges WHERE edge_kind = ? LIMIT 5", (kind,))
    types = [row[0] for row in cursor.fetchall()]
    print(f"  {kind} semantic types: {types}")

conn.close()
