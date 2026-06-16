"""Step 8: Retrieval service proof — call VectorRetrievalService directly."""

from agentic_core.config.model_catalog import (
    BGE_M3_MODEL_ID,
)

import os
import sys
import time

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TQDM_DISABLE"] = "1"
os.environ["VECTOR_DB_EMBEDDING_MODEL"] = BGE_M3_MODEL_ID
os.environ["VECTOR_DB_CHROMA_PATH"] = "data/cache/chromadb"
os.environ["VECTOR_DB_ALLOW_MODEL_DOWNLOAD"] = "0"

# Ensure repo root is on path
sys.path.insert(0, os.getcwd())

QUERY = "How do AI systems implement deterministic response caching with policy-key short-circuit routing to avoid redundant LLM inference?"

print("Importing VectorRetrievalService...", flush=True)
t0 = time.perf_counter()
from tools.retrieval.vector_service import VectorRetrievalService

t_import = time.perf_counter() - t0
print(f"Import time: {t_import:.2f}s")

print("\nCreating service instance...", flush=True)
t1 = time.perf_counter()
svc = VectorRetrievalService()
t_init = time.perf_counter() - t1
print(f"Service init time: {t_init:.2f}s")

print(f"\nCalling svc.query_collection('ext_authority', query)...", flush=True)
t2 = time.perf_counter()
report = svc.query_collection("ext_authority", QUERY, n_results=5)
t_total_query = time.perf_counter() - t2

print(f"\n--- Timings ---")
print(f"Embedding time: {report.embedding_time_s:.3f}s")
print(f"Query time: {report.query_time_s:.3f}s")
print(f"Total service call: {t_total_query:.3f}s")
print(f"Results: {len(report.hits)}")

for i, hit in enumerate(report.hits):
    m = hit.metadata or {}
    print(f"\n  [{i + 1}] dist={hit.distance:.4f}" if hit.distance else f"\n  [{i + 1}] dist=N/A")
    print(f"      collection={hit.collection}")
    print(f"      source_collection={m.get('source_collection', '?')}")
    print(f"      authority_tier={m.get('authority_tier', '?')}")
    print(f"      doc_family={m.get('doc_family', '?')}")
    print(f"      title={m.get('title', '?')[:80]}")

print(f"\n{'PASS' if len(report.hits) > 0 else 'FAIL: no results'}")
