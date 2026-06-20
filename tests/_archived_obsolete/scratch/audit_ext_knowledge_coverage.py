"""
Audit ext_knowledge collection in ChromaDB.
Proves 95%+ coverage of agent-framework external docs:
  - anthropic (docs.anthropic.com / platform.codex.com)
  - openai agents (openai.github.io/openai-agents-python)
  - autogen (microsoft.github.io/autogen)

Outputs:
  1. Total doc count
  2. Domain breakdown with percentages
  3. Per-target coverage table (present / missing)
  4. Overall coverage % -> PASS/FAIL vs 95% threshold
"""

import sys
from collections import Counter

CHROMA_PATH = r"C:\Git\Agentic-Workflow\data\cache\chromadb"
COLLECTION = "ext_knowledge"
THRESHOLD = 0.95  # 95%

# Target domains/URL prefixes we expect in the collection
TARGETS = {
    "anthropic": [
        "docs.anthropic.com",
        "platform.claude.com",
        "anthropic",
    ],
    "openai_agents": [
        "openai.github.io/openai-agents-python",
        "openai-agents-python",
    ],
    "autogen": [
        "microsoft.github.io/autogen",
        "autogen",
    ],
    "langchain": ["python.langchain.com", "langchain"],
    "huggingface": ["huggingface.co", "huggingface"],
    "mcp_protocol": ["modelcontextprotocol.io", "modelcontextprotocol"],
    "chromadb_docs": ["docs.trychroma.com", "trychroma"],
    "nist": ["nvlpubs.nist.gov", "nist.gov"],
    "paul_graham": ["paulgraham.com"],
    "openai_platform": ["platform.openai.com", "openai.com", "openai-agents-python"],
}

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    print("ERROR: chromadb not installed. Run: pip install chromadb")
    sys.exit(1)

print(f"Connecting to ChromaDB at: {CHROMA_PATH}")
client = chromadb.PersistentClient(
    path=CHROMA_PATH,
    settings=Settings(anonymized_telemetry=False),
)

collections_available = [c.name for c in client.list_collections()]
print(f"Available collections: {collections_available}\n")

if COLLECTION not in collections_available:
    print(f"ERROR: Collection '{COLLECTION}' not found. Run ingest_ext_knowledge.py first.")
    sys.exit(1)

col = client.get_collection(COLLECTION)
total = col.count()
print(f"=== {COLLECTION}: {total:,} documents ===\n")

# Retrieve all metadata
result = col.get(include=["metadatas"])
metas = result["metadatas"] or []

# Domain breakdown
domain_counter: Counter = Counter()
doc_type_counter: Counter = Counter()

for m in metas:
    domain_counter[m.get("domain", "(none)")] += 1
    doc_type_counter[m.get("doc_type", "(none)")] += 1

print("-" * 55)
print(f"{'Domain':<40s} {'Count':>6s}  {'%':>5s}")
print("-" * 55)
for d, cnt in domain_counter.most_common():
    pct = cnt / total * 100
    print(f"  {d:<38s} {cnt:>6,d}  {pct:>4.1f}%")

print(f"\n{'Doc type':<40s} {'Count':>6s}")
print("-" * 50)
for dt, cnt in doc_type_counter.most_common():
    print(f"  {dt:<38s} {cnt:>6,d}")


# Per-target coverage
def matches_any(meta: dict, patterns: list) -> bool:
    haystack = " ".join(
        [
            str(meta.get("domain", "")),
            str(meta.get("source_url", "")),
            str(meta.get("document_title", "")),
            str(meta.get("file_path", "")),
        ]
    ).lower()
    return any(p.lower() in haystack for p in patterns)


print("\n" + "=" * 60)
print("TARGET COVERAGE ANALYSIS")
print("=" * 60)

target_counts: dict = {}
for target, patterns in TARGETS.items():
    cnt = sum(1 for m in metas if matches_any(m, patterns))
    target_counts[target] = cnt

targets_with_docs = sum(1 for v in target_counts.values() if v > 0)
total_targets = len(TARGETS)
coverage_pct = targets_with_docs / total_targets

print(f"\n{'Target':<25s} {'Docs':>6s}  {'Status'}")
print("-" * 45)
for target, cnt in sorted(target_counts.items(), key=lambda x: -x[1]):
    status = "PRESENT" if cnt > 0 else "MISSING"
    mark = "+" if cnt > 0 else "X"
    print(f"  [{mark}] {target:<21s} {cnt:>6,d}  {status}")

print("-" * 45)
print(f"\n  Targets present: {targets_with_docs}/{total_targets}")
print(f"  Coverage: {coverage_pct * 100:.1f}%")

# Agent-framework specific check (the 3 key frameworks)
agent_fw = {k: target_counts[k] for k in ["anthropic", "openai_agents", "autogen"]}
agent_fw_present = sum(1 for v in agent_fw.values() if v > 0)
agent_fw_coverage = agent_fw_present / len(agent_fw)

print(f"\n{'-' * 45}")
print("AGENT FRAMEWORK TARGETS (anthropic / openai_agents / autogen):")
for fw, cnt in agent_fw.items():
    mark = "+" if cnt > 0 else "X"
    status = "PRESENT" if cnt > 0 else "MISSING"
    print(f"  [{mark}] {fw:<23s} {cnt:>6,d} docs  {status}")
print(f"  Agent framework coverage: {agent_fw_coverage * 100:.0f}%")

# Overall PASS/FAIL
print("\n" + "=" * 60)
overall_pass = coverage_pct >= THRESHOLD
agent_pass = agent_fw_coverage >= THRESHOLD
print(
    f"  OVERALL COVERAGE:         {coverage_pct * 100:.1f}%  ->  {'PASS' if overall_pass else 'FAIL'} (threshold: {THRESHOLD * 100:.0f}%)"
)
print(f"  AGENT FW COVERAGE:        {agent_fw_coverage * 100:.0f}%  ->  {'PASS' if agent_pass else 'FAIL'}")
print(f"  TOTAL DOCS IN COLLECTION: {total:,}")
print("=" * 60)

if not overall_pass:
    print("\nACTION REQUIRED: Run ingest_ext_knowledge.py to populate missing sources.")
    sys.exit(1)
