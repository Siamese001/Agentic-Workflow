"""Step 4: Collection dimension proof."""

import chromadb
from chromadb.config import Settings

client = chromadb.PersistentClient(
    path="data/cache/chromadb",
    settings=Settings(anonymized_telemetry=False),
)
col = client.get_collection("ext_authority")
m = col.metadata or {}
print(f"metadata: {m}")
print(f"embedding_dim: {m.get('embedding_dim')}")
print(f"embedding_model: {m.get('embedding_model')}")
print(f"hnsw:space: {m.get('hnsw:space')}")
print(f"wave: {m.get('wave')}")

# Verify by peeking at one stored embedding
sample = col.get(limit=1, include=["embeddings"])
if sample and sample.get("embeddings") and len(sample["embeddings"]) > 0:
    dim = len(sample["embeddings"][0])
    print(f"actual_stored_dim: {dim}")
    print(f"dim_match: {dim == int(m.get('embedding_dim', 0))}")
else:
    print("actual_stored_dim: COULD NOT RETRIEVE")
