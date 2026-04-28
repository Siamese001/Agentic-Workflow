"""Check HNSW index sizes using segment IDs (not collection IDs)."""

import os
import sqlite3

DB = r"C:\Git\Agentic-Workflow\data\cache\chromadb\chroma.sqlite3"
CHROMA_DIR = r"C:\Git\Agentic-Workflow\data\cache\chromadb"

conn = sqlite3.connect(DB)
cur = conn.cursor()

cur.execute("""
    SELECT c.name, c.dimension, s.id as segment_id
    FROM segments s
    JOIN collections c ON s.collection = c.id
    WHERE s.type LIKE '%hnsw%'
    ORDER BY c.name
""")
segments = cur.fetchall()

# Doc counts
cur.execute("""
    SELECT c.name, COUNT(e.id)
    FROM embeddings e
    JOIN segments s ON e.segment_id = s.id
    JOIN collections c ON s.collection = c.id
    WHERE s.type LIKE '%hnsw%'
    GROUP BY c.name
    ORDER BY c.name
""")
doc_counts = dict(cur.fetchall())

print(f"{'Collection':25s} {'Docs':>8s} {'Dim':>5s} {'HNSW Size':>12s} {'Files':>6s} {'Est Cold (s)':>12s}")
print("-" * 75)

for cname, cdim, seg_id in segments:
    seg_dir = os.path.join(CHROMA_DIR, seg_id)
    docs = doc_counts.get(cname, 0)
    if os.path.isdir(seg_dir):
        total = 0
        fcount = 0
        for root, dirs, files in os.walk(seg_dir):
            for fname in files:
                total += os.path.getsize(os.path.join(root, fname))
                fcount += 1
        mb = total / 1024 / 1024
        # Rough estimate: cold start ~ docs * dim * 4 bytes / (100 MB/s disk read) + overhead
        est_cold = (docs * cdim * 4) / (100 * 1024 * 1024) + (total / (100 * 1024 * 1024))
        est_cold = max(est_cold, 0.1)
        # More realistic: observed 8.7s for 2510 docs, scale linearly
        if docs > 0:
            est_cold_real = 8.7 * (docs / 2510)
        else:
            est_cold_real = 0
        print(f"{cname:25s} {docs:>8d} {cdim:>5d} {mb:>9.1f} MB {fcount:>6d} {est_cold_real:>9.1f}s")
    else:
        print(f"{cname:25s} {docs:>8d} {cdim:>5d}  DIR MISSING         -")

conn.close()
print("\nKey: Est Cold = estimated HNSW cold-start based on ext_knowledge baseline (8.7s / 2510 docs)")
