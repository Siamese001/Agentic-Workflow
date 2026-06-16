"""C2.2 F25-int validation probe: TS-20-equivalent validation for the new ADR.

Runs the F25-int acceptance query end-to-end and verifies G4/G5/G6 for the
new ADR chunks. Temporary — delete after C2.2 closeout.
"""

from __future__ import annotations

from agentic_core.config.model_catalog import (
    BGE_M3_MODEL_ID,
)

import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_PATH = REPO_ROOT / "data" / "cache" / "chromadb"
COLLECTION = "repo_evidence"
MODEL = BGE_M3_MODEL_ID
QUERY = "confidence-scored tiered healing dispatch routing tiers local rules model retry human escalation"
NEW_DOC_PATH = "docs/architecture/healing_dispatch_routing_adr.md"

REQUIRED = [
    "source_collection",
    "source_band",
    "authority_tier",
    "normative_scope",
    "invalid_for_normative_use",
    "source_type",
    "topic_bucket",
    "doc_family",
    "source_url",
    "heading_path",
    "collapse_group",
    "title",
    "chunk_index",
    "canonical_digest",
    "file_path",
]


def section(label: str) -> None:
    print(f"\n===== {label} =====")


def main() -> None:
    section("1. LOAD MODEL + CLIENT")
    t0 = time.perf_counter()
    model = SentenceTransformer(MODEL)
    print(f"model_load_s={round(time.perf_counter() - t0, 3)}")

    t0 = time.perf_counter()
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    col = client.get_collection(COLLECTION)
    count = col.count()
    print(f"get_collection_s={round(time.perf_counter() - t0, 3)} collection_count={count}")

    section("2. F25-INT QUERY")
    t0 = time.perf_counter()
    emb = model.encode([QUERY], normalize_embeddings=True).tolist()
    print(f"embed_s={round(time.perf_counter() - t0, 3)}")

    t0 = time.perf_counter()
    res = col.query(
        query_embeddings=emb,
        n_results=5,
        include=["distances", "metadatas", "documents"],
    )
    print(f"query_s={round(time.perf_counter() - t0, 3)}")

    print("\ntop_5:")
    for i, (dist, meta) in enumerate(zip(res["distances"][0], res["metadatas"][0])):
        path = meta.get("file_path") or meta.get("source_url") or "?"
        heading = meta.get("heading_path", "?")
        mark = " <-- NEW ADR" if path == NEW_DOC_PATH and i == 0 else ""
        print(f"  [{i + 1}] dist={dist:.4f} path={path}{mark}")
        print(f"       heading={heading}")

    top_dist = res["distances"][0][0]
    top_path = res["metadatas"][0][0].get("file_path", "?")
    rank1_is_adr = top_path == NEW_DOC_PATH
    below_050 = top_dist < 0.50

    section("3. ACCEPTANCE")
    print(f"dist@1={top_dist:.4f}")
    print(f"new_adr_is_rank1={rank1_is_adr}")
    print(f"dist@1_below_0.50={below_050}")
    print(f"acceptance={'PASS' if (rank1_is_adr and below_050) else 'FAIL'}")

    section("4. G4/G5/G6 ON NEW ADR CHUNKS")
    new_chunks = col.get(
        where={"file_path": NEW_DOC_PATH},
        limit=100,
        include=["metadatas"],
    )
    n = len(new_chunks["ids"])
    print(f"new_adr_chunks={n}")
    if n == 0:
        print("FAIL: no chunks found for new ADR")
        return

    metas = new_chunks["metadatas"]
    m0 = metas[0]

    missing = [k for k in REQUIRED if k not in m0]
    g6 = not missing
    print(f"G6_all_required_fields_present={g6} missing={missing}")

    invalids = [m for m in metas if m.get("invalid_for_normative_use") is not True]
    g4 = len(invalids) == 0
    print(f"G4_invalid_for_normative_use_True_on_all={g4} violations={len(invalids)}")

    with_https = [m for m in metas if str(m.get("source_url", "")).startswith("https://")]
    g5 = len(with_https) == 0
    print(f"G5_no_https_source_url={g5} violations={len(with_https)}")

    print("\nsample_metadata:")
    print(f"  source_band={m0['source_band']}")
    print(f"  authority_tier={m0['authority_tier']}")
    print(f"  source_collection={m0['source_collection']}")
    print(f"  invalid_for_normative_use={m0['invalid_for_normative_use']}")
    print(f"  source_url={m0['source_url']}")
    print(f"  doc_family={m0['doc_family']}")
    print(f"  topic_bucket={m0['topic_bucket']}")
    print(f"  collapse_group={m0['collapse_group']}")

    section("5. SUMMARY")
    print(f"f25_int_acceptance={'PASS' if (rank1_is_adr and below_050 and g4 and g5 and g6) else 'FAIL'}")


if __name__ == "__main__":
    main()
