"""Step 7: Direct Chroma query with pre-computed embedding — no query_texts."""

from agentic_core.config.model_catalog import (
    BGE_M3_MODEL_ID,
)

import os
import time

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TQDM_DISABLE"] = "1"

CHROMA_PATH = "data/cache/chromadb"
MODEL_NAME = BGE_M3_MODEL_ID
QUERY = "How do AI systems implement deterministic response caching with policy-key short-circuit routing to avoid redundant LLM inference?"

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# Load model
print(f"Loading {MODEL_NAME}...", flush=True)
model = SentenceTransformer(MODEL_NAME, local_files_only=True)

# Encode
print("Encoding query...", flush=True)
emb = model.encode([QUERY], normalize_embeddings=True, show_progress_bar=False).tolist()
print(f"Embedding dim: {len(emb[0])}")

# Open Chroma
print(f"\nOpening Chroma at {CHROMA_PATH}...", flush=True)
client = chromadb.PersistentClient(
    path=CHROMA_PATH,
    settings=Settings(anonymized_telemetry=False),
)
col = client.get_collection("ext_authority")
print(f"ext_authority count: {col.count()}")

# Query with query_embeddings
print("\nQuerying ext_authority with query_embeddings (n=5)...", flush=True)
t0 = time.perf_counter()
results = col.query(
    query_embeddings=emb,
    n_results=5,
    include=["metadatas", "distances", "documents"],
)
t_query = time.perf_counter() - t0

ids = results.get("ids", [[]])[0]
dists = results.get("distances", [[]])[0]
metas = results.get("metadatas", [[]])[0]
docs = results.get("documents", [[]])[0]

print(f"Query time: {t_query:.3f}s")
print(f"Results returned: {len(ids)}")

for i in range(len(ids)):
    d = dists[i] if i < len(dists) else None
    m = metas[i] if i < len(metas) else {}
    doc_snip = (docs[i] or "")[:100] if i < len(docs) else ""
    print(f"\n  [{i + 1}] id={ids[i]}")
    print(f"      dist={d:.4f}" if d is not None else "      dist=N/A")
    print(f"      source_collection={m.get('source_collection', '?')}")
    print(f"      authority_tier={m.get('authority_tier', '?')}")
    print(f"      doc_family={m.get('doc_family', '?')}")
    print(f"      title={m.get('title', '?')[:80]}")
    print(f"      doc: {doc_snip}...")

print("\nPASS" if len(ids) > 0 else "\nFAIL: no results returned")
