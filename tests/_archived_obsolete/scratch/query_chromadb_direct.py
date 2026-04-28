"""Direct ChromaDB queries — bypasses MCP server entirely."""

import json
import os
import sys
import time

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TQDM_DISABLE"] = "1"

REPO_ROOT = r"C:\Git\Agentic-Workflow"
CHROMA_PATH = os.path.join(REPO_ROOT, "data", "cache", "chromadb")
MODEL_NAME = "BAAI/bge-m3"

sys.path.insert(0, REPO_ROOT)

import chromadb
from chromadb.config import Settings

print(f"Loading ChromaDB from {CHROMA_PATH}...")
t0 = time.monotonic()
client = chromadb.PersistentClient(path=CHROMA_PATH, settings=Settings(anonymized_telemetry=False))
print(f"ChromaDB ready in {time.monotonic() - t0:.1f}s")

cols = client.list_collections()
print(f"Collections: {[c.name for c in cols]}\n")

print("Loading embedding model...")
t0 = time.monotonic()
from sentence_transformers import SentenceTransformer

model = SentenceTransformer(MODEL_NAME, local_files_only=True)
print(f"Model ready in {time.monotonic() - t0:.1f}s\n")

QUERIES = [
    (
        "ext_knowledge",
        "agentic architecture multi-agent orchestration wiring integration patterns LangGraph LangChain supervisor routing coordinator",
    ),
    (
        "ext_knowledge",
        "agent memory persistence state management durable execution checkpointing long-running workflow graph state",
    ),
    (
        "ext_knowledge",
        "agent guardrails safety layer input validation output filtering trust boundary security",
    ),
    (
        "ext_knowledge",
        "MCP model context protocol tool server implementation structured output JSON-RPC error handling",
    ),
    (
        "ext_knowledge",
        "vector database embedding RAG retrieval augmented generation indexing chunking semantic search",
    ),
    ("ext_knowledge", "agent observability tracing telemetry monitoring production debugging LangSmith"),
    ("ext_knowledge", "agent error handling retry circuit breaker resilience fallback graceful degradation"),
    (
        "arch_docs",
        "agent orchestration wiring integration coordinator message passing multi-agent collaboration",
    ),
    ("arch_docs", "error handling retry resilience fallback observability telemetry tracing"),
    ("arch_docs", "memory persistence state management checkpointing durable execution"),
]

for collection_name, query_text in QUERIES:
    print(f"=== {collection_name}: {query_text[:70]}... ===")
    try:
        col = client.get_collection(collection_name)
        t0 = time.monotonic()
        emb = model.encode([query_text])
        enc_time = time.monotonic() - t0

        t1 = time.monotonic()
        results = col.query(
            query_embeddings=emb.tolist(),
            n_results=8,
            include=["documents", "metadatas", "distances"],
        )
        q_time = time.monotonic() - t1

        docs = results.get("documents", [[]])[0]
        dists = results.get("distances", [[]])[0]
        metas = results.get("metadatas", [[]])[0]

        print(f"  Encode: {enc_time:.3f}s | Query: {q_time:.3f}s | Results: {len(docs)}")
        for i, (doc, dist, meta) in enumerate(zip(docs, dists, metas)):
            source = (meta or {}).get("source_url", "") or (meta or {}).get("file_path", "")
            title = (meta or {}).get("document_title", "")
            print(f"  [{i + 1}] dist={dist:.4f} | {title[:60]} | {source[:80]}")
            print(f"      {doc[:150]}...")
        print()
    except (RuntimeError, ValueError, OSError) as exc:
        print(f"  ERROR: {exc}\n")

print("=== ALL QUERIES DONE ===")
