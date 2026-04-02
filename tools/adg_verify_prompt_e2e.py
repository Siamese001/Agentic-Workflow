"""ADG Prompt Template E2E Verification Script"""
import sqlite3
import sys

def main():
    conn = sqlite3.connect('artifacts/adg/adg_indexed_03272026_2037.sqlite')
    cursor = conn.cursor()

    print("=" * 70)
    print("ADG PROMPT TEMPLATE WIRING VERIFICATION")
    print("=" * 70)

    # 1. Find prompt template related nodes
    print("\n=== PROMPT TEMPLATE NODES ===")
    cursor.execute("""
        SELECT id, label, layer, entity_type, file_path
        FROM nodes
        WHERE id LIKE '%prompt%' OR label LIKE '%prompt%'
           OR id LIKE '%template%' OR label LIKE '%template%'
           OR id LIKE '%sovereign%'
        ORDER BY layer, id
    """)
    rows = cursor.fetchall()
    for row in rows[:30]:
        print(f"  L{row[2]:<2} | {row[0][:50]:<50} | {row[4]}")

    if len(rows) > 30:
        print(f"  ... and {len(rows) - 30} more")

    # 2. Find edges connecting prompt governance to apps
    print("\n=== CROSS-LAYER PROMPT EDGES ===")
    cursor.execute("""
        SELECT e.id, e.src_id, e.dst_id, e.relation_type, e.edge_kind
        FROM edges e
        JOIN nodes src ON e.src_id = src.id
        JOIN nodes dst ON e.dst_id = dst.id
        WHERE (e.src_id LIKE '%prompt%' OR e.src_id LIKE '%template%')
           OR (e.dst_id LIKE '%prompt%' OR e.dst_id LIKE '%template%')
           OR (e.src_id LIKE '%sovereign%')
        ORDER BY e.relation_type
        LIMIT 40
    """)
    edges = cursor.fetchall()
    for e in edges:
        print(f"  {e[3]:<20} | {e[1][:40]:<40} -> {e[2][:40]}")

    # 3. Find apps_rg connections
    print("\n=== APPS_RG PROMPT CONNECTIONS ===")
    cursor.execute("""
        SELECT e.id, e.src_id, e.dst_id, e.relation_type
        FROM edges e
        WHERE e.src_id LIKE '%apps_rg%' OR e.dst_id LIKE '%apps_rg%'
           OR e.src_id LIKE '%base_rg_engine%' OR e.dst_id LIKE '%base_rg_engine%'
        ORDER BY e.relation_type
        LIMIT 30
    """)
    edges = cursor.fetchall()
    for e in edges:
        print(f"  {e[3]:<20} | {e[1][:50]:<50} -> {e[2][:40]}")

    # 4. Summary stats
    print("\n=== SUMMARY STATS ===")
    cursor.execute("SELECT COUNT(*) FROM nodes WHERE id LIKE '%prompt%' OR id LIKE '%template%'")
    print(f"  Prompt/Template nodes: {cursor.fetchone()[0]}")

    cursor.execute("SELECT COUNT(*) FROM nodes WHERE id LIKE '%sovereign%'")
    print(f"  Sovereign nodes: {cursor.fetchone()[0]}")

    cursor.execute("SELECT COUNT(*) FROM nodes WHERE id LIKE '%apps_rg%'")
    print(f"  apps_rg nodes: {cursor.fetchone()[0]}")

    conn.close()
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
