# Check what relation_types these edges actually have
import sqlite3

conn = sqlite3.connect("artifacts/adg/adg_indexed_03272026_2018.sqlite")

problem_kinds = ["reads_runtime_state", "reads_policy_state", "layer_membership"]

for kind in problem_kinds:
    print(f"\n=== {kind} ===")
    cursor = conn.execute(
        "SELECT DISTINCT relation_type, COUNT(*) FROM edges WHERE edge_kind = ? GROUP BY relation_type",
        (kind,),
    )
    rel_types = cursor.fetchall()
    for rel_type, count in rel_types:
        print(f"  relation_type: {rel_type}, count: {count}")

    # Check if relation_type is in our fallback map
    cursor = conn.execute(
        "SELECT COUNT(*) FROM edges WHERE edge_kind = ? AND semantic_type = edge_kind", (kind,)
    )
    raw_count = cursor.fetchone()[0]
    print(f"  raw fallbacks: {raw_count}")

conn.close()
