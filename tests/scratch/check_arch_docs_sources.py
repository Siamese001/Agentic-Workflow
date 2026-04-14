"""Show sources/file_paths in arch_docs collection."""

import chromadb
from chromadb.config import Settings
from collections import Counter

c = chromadb.PersistentClient(
    path=r"C:\Git\Agentic-Workflow\data\cache\chromadb",
    settings=Settings(anonymized_telemetry=False),
)
col = c.get_collection("arch_docs")
meta = col.get(include=["metadatas"])

print(f"Total docs: {len(meta['ids'])}")

sources = Counter()
doc_types = Counter()
paths = Counter()

for m in meta["metadatas"]:
    sources[m.get("source", "")] += 1
    doc_types[m.get("doc_type", "")] += 1
    paths[m.get("file_path", "")] += 1

print(f"\nSources:")
for s, cnt in sources.most_common():
    print(f"  {cnt:>5d}  {s}")

print(f"\nDoc types:")
for d, cnt in doc_types.most_common():
    print(f"  {cnt:>5d}  {d}")

print(f"\nTop 60 file paths (by chunk count):")
for p, cnt in paths.most_common(60):
    print(f"  {cnt:>5d}  {p}")

print(f"\n... {len(paths)} unique file paths total")
