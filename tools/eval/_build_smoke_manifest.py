"""Build a smoke-scale calibration manifest from the 4 smoke collections.

Picks 8 queries whose answers are obviously in specific files in
agentic_core/knowledge/retrieval/, then enumerates every chunk_id whose
metadata.source_path points at the expected file and pins that set as
``relevant_doc_ids``. This gives the harness a real ground-truth mapping
to measure against.
"""

from __future__ import annotations
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
os.environ.setdefault("PYTHONPATH", str(Path(__file__).resolve().parents[2]))

from agentic_core.L4_state.config.chroma_paths import canonical_persist_dir_str
from agentic_core.L4_state.utils.client.chroma_client import SovereignChromaClient

# Query -> expected source_path substring. A chunk is relevant if its
# metadata.source_path contains the expected substring.
QUERIES: list[tuple[str, str, str]] = [
    ("How does Late Chunking pool token embeddings into chunk vectors?", "late_chunking.py", "semantic"),
    ("bge_reranker_adapter cross encoder wrapper", "bge_reranker_adapter.py", "exact"),
    ("Two-stage reranker with heuristic pre-filter", "cross_encoder_reranker.py", "semantic"),
    ("reranker factory env driven selection", "reranker_factory.py", "semantic"),
    ("SeniorLibrarianReranker relevance coverage authority", "senior_librarian_reranker.py", "exact"),
    ("anthropic prompt cache control marker", "anthropic_cache_control.py", "exact"),
    ("hybrid recall stage", "hybrid_recall_stage.py", "exact"),
    ("parent child chunk hydration", "parent_child_hydrator.py", "semantic"),
]


def main() -> int:
    client = SovereignChromaClient(persist_dir=canonical_persist_dir_str())
    col = client.client.get_collection("smoke_baseline")
    all_docs = col.get(include=["metadatas"])
    metas = all_docs["metadatas"] or []
    ids = all_docs["ids"] or []
    print(f"Loaded {len(ids)} chunks from smoke_baseline")

    # Build substring -> relevant_doc_ids index.
    manifest_queries = []
    for query, expected_file, category in QUERIES:
        relevant = [ids[i] for i, m in enumerate(metas) if expected_file in (m or {}).get("source_path", "")]
        if not relevant:
            print(f"  SKIP: no relevant chunks found for {expected_file}")
            continue
        manifest_queries.append(
            {
                "query": query,
                "relevant_doc_ids": relevant,
                "category": category,
            }
        )
        print(f"  '{query[:50]}...' -> {len(relevant)} relevant chunks in {expected_file}")

    out_path = Path("artifacts/retrieval_baseline/smoke_calibration_manifest.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps({"queries": manifest_queries}, indent=2),
        encoding="utf-8",
    )
    print(f"\nWrote {out_path} with {len(manifest_queries)} queries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
