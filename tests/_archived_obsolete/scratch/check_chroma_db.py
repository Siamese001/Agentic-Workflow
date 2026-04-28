"""Check ChromaDB SQLite metadata and HNSW index sizes on disk."""

import os
import sqlite3

DB = r"C:\Git\Agentic-Workflow\data\cache\chromadb\chroma.sqlite3"
CHROMA_DIR = r"C:\Git\Agentic-Workflow\data\cache\chromadb"

conn = sqlite3.connect(DB)
cur = conn.cursor()

# List tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in cur.fetchall()]
print(f"Tables: {tables}\n")

# Collection info
cur.execute("SELECT id, name, dimension FROM collections ORDER BY name")
collections = cur.fetchall()
print(f"{'Collection':30s} {'Dim':>5s} {'Segments':>10s}")
print("-" * 50)

for cid, cname, cdim in collections:
    cur.execute("SELECT COUNT(*) FROM segments WHERE collection = ?", (cid,))
    seg_count = cur.fetchone()[0]
    print(f"{cname:30s} {cdim:>5d} {seg_count:>10d}")

# Check segment types
print(f"\nSegment details:")
cur.execute("""
    SELECT c.name, s.type, s.scope, s.id
    FROM segments s
    JOIN collections c ON s.collection = c.id
    ORDER BY c.name, s.type
""")
for row in cur.fetchall():
    print(f"  {row[0]:30s} type={row[1]:40s} scope={row[2]} id={row[3]}")

# Check HNSW file sizes per collection
print(f"\nHNSW index file sizes:")
for cid, cname, cdim in collections:
    col_dir = os.path.join(CHROMA_DIR, cid)
    if os.path.isdir(col_dir):
        total = sum(f.stat().st_size for f in (os.scandir(col_dir)) if f.is_file())
        # Check subdirs too
        for root, dirs, files in os.walk(col_dir):
            for fname in files:
                fp = os.path.join(root, fname)
                pass  # already counted above only top-level
        # Actually walk properly
        total = 0
        for root, dirs, files in os.walk(col_dir):
            for fname in files:
                total += os.path.getsize(os.path.join(root, fname))
        print(f"  {cname:30s} {total:>12,d} bytes ({total / 1024 / 1024:.1f} MB)")
    else:
        print(f"  {cname:30s} DIR NOT FOUND at {col_dir}")

# Check embedding_metadata table for doc counts
print(f"\nDoc counts (from embedding_metadata):")
for cid, cname, cdim in collections:
    cur.execute(
        """
        SELECT COUNT(*)
        FROM embeddings e
        JOIN segments s ON e.segment_id = s.id
        WHERE s.collection = ?
    """,
        (cid,),
    )
    count = cur.fetchone()[0]
    print(f"  {cname:30s} {count:>8d} docs")

conn.close()
print("\nDone.")
