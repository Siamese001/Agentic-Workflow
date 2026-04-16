"""C2.1 TS-20 isolation probe: direct PersistentClient + query_embeddings.

Isolates embed-time from query-time for the TS-20 validation query.
Temporary diagnostic script — safe to delete after C2.1 closeout.
"""

from __future__ import annotations

import time
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_PATH = Path(r"C:\Git\Agentic-Workflow\data\cache\chromadb")
COLLECTION = "repo_evidence"
MODEL = "BAAI/bge-m3"
QUERY = "normative requirements specification for the agentic routing system"


def main() -> None:
    t0 = time.perf_counter()
    model = SentenceTransformer(MODEL)
    print(f"model_load_s={round(time.perf_counter() - t0, 3)}")

    t0 = time.perf_counter()
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    col = client.get_collection(COLLECTION)
    count = col.count()
    print(f"get_collection_s={round(time.perf_counter() - t0, 3)} count={count}")

    t0 = time.perf_counter()
    emb = model.encode([QUERY], normalize_embeddings=True).tolist()
    print(f"embed_s={round(time.perf_counter() - t0, 3)} dim={len(emb[0])}")

    t0 = time.perf_counter()
    res = col.query(query_embeddings=emb, n_results=5, include=["distances"])
    print(f"query_dist_only_s={round(time.perf_counter() - t0, 3)}")
    print(f"distances={res['distances'][0]}")

    t0 = time.perf_counter()
    res = col.query(
        query_embeddings=emb,
        n_results=5,
        include=["distances", "metadatas", "documents"],
    )
    print(f"query_full_s={round(time.perf_counter() - t0, 3)}")
    print("top_5_hits:")
    for i, (dist, meta) in enumerate(zip(res["distances"][0], res["metadatas"][0])):
        path = meta.get("file_path") or meta.get("source_url") or "?"
        title = meta.get("title", "?")
        heading = meta.get("heading_path", "?")
        print(f"  [{i + 1}] dist={dist:.4f} path={path}")
        print(f"       title={title}")
        print(f"       heading={heading}")


if __name__ == "__main__":
    main()
