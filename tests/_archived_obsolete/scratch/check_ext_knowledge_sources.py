"""Audit ext_knowledge collection — what external sources do we have?"""

import chromadb
from chromadb.config import Settings
from collections import Counter

c = chromadb.PersistentClient(
    path=r"C:\Git\Agentic-Workflow\data\cache\chromadb",
    settings=Settings(anonymized_telemetry=False),
)

# ext_knowledge audit
col = c.get_collection("ext_knowledge")
meta = col.get(include=["metadatas"])
print(f"=== ext_knowledge: {len(meta['ids'])} docs ===\n")

domains = Counter()
doc_types = Counter()
sources = Counter()
titles = Counter()

for m in meta["metadatas"]:
    domains[m.get("domain", "")] += 1
    doc_types[m.get("doc_type", "")] += 1
    sources[m.get("source", "")] += 1
    titles[m.get("document_title", "")] += 1

print("By domain:")
for d, cnt in domains.most_common():
    print(f"  {cnt:>5d}  {d}")

print(f"\nBy source:")
for s, cnt in sources.most_common():
    print(f"  {cnt:>5d}  {s}")

print(f"\nBy doc_type:")
for dt, cnt in doc_types.most_common():
    print(f"  {cnt:>5d}  {dt}")

print(f"\nBy document_title (top 40):")
for t, cnt in titles.most_common(40):
    print(f"  {cnt:>5d}  {t}")

# Also check arch_docs — what's actually architecture vs noise
print(f"\n\n=== arch_docs noise analysis ===")
col2 = c.get_collection("arch_docs")
meta2 = col2.get(include=["metadatas"])

windsurf = 0
archive_versions = 0
actual_arch = 0
plans = 0
other = 0

for m in meta2["metadatas"]:
    fp = m.get("file_path", "")
    if "docs/windsurf/" in fp:
        windsurf += 1
    elif "_archive/" in fp:
        archive_versions += 1
    elif "docs/reports/plans/" in fp:
        plans += 1
    elif any(
        x in fp for x in ["docs/reference/", "docs/architecture/", "docs/specs/", "docs/reports/design/"]
    ):
        actual_arch += 1
    else:
        other += 1

total = len(meta2["ids"])
print(f"Total: {total}")
print(f"  Windsurf IDE docs:    {windsurf:>5d}  ({windsurf / total * 100:.0f}%)")
print(f"  Archive versions:     {archive_versions:>5d}  ({archive_versions / total * 100:.0f}%)")
print(f"  Plans:                {plans:>5d}  ({plans / total * 100:.0f}%)")
print(f"  Actual architecture:  {actual_arch:>5d}  ({actual_arch / total * 100:.0f}%)")
print(f"  Other:                {other:>5d}  ({other / total * 100:.0f}%)")
