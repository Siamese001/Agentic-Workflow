"""Build + ingest meaningful per-section fact vectors into the Chroma ``fact_vectors`` collection.

PURPOSE
-------
C0.2 dense retrieval reads the ``fact_vectors`` Chroma collection as NON-AUTHORITATIVE
enrichment on top of the authoritative ledger/graph proof pool. This operator tool walks the
canonical candidate-fact ledger, assigns each eligible HIGH fact to the resume sections it can
meaningfully support, and upserts one embeddable chunk per fact (BGE-M3) into ``fact_vectors``.

CANONICAL LOGIC
---------------
The section-assignment + atom-building logic is owned by the governed bootstrap module
``apps_rg.runtime.fact_vectors_bootstrap`` (``python -m apps_rg bootstrap fact-vectors``); this
script delegates to it (``assign_sections_for_fact`` / ``build_section_atoms``) so the two never
drift. Prefer the ``bootstrap`` subcommand for fresh-checkout provisioning — it emits a manifest +
checksum and supports ``--strict``. This tool remains a thin operator convenience.

BOUNDARY
--------
- Chroma ``fact_vectors`` is enrichment ONLY (ledger + graph + proof pool remain the X2 proof
  substrate). Only HIGH-confidence / proof-eligible facts are embedded. Chunk ids are stable
  (``apps_rg:fv:{fact_id}``) so re-running is idempotent. EY/InsurTech lanes are locked-deterministic
  and intentionally carry no generated atoms (see the bootstrap module).

USAGE
-----
    python tools/apps_rg/build_section_fact_vectors.py            # dry run (no writes)
    python tools/apps_rg/build_section_fact_vectors.py --execute  # embed + upsert
    python tools/apps_rg/build_section_fact_vectors.py --execute --reset  # rebuild from scratch
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from apps_rg.runtime.c0.c02_fact_vector_ingest import (  # noqa: E402
    atoms_to_fact_vector_chunks,
    upsert_fact_vector_chunks,
)

# Canonical section-assignment + atom-building logic lives in the governed bootstrap module;
# this tool delegates so the two implementations never drift.
from apps_rg.runtime.fact_vectors_bootstrap import (  # noqa: E402
    assign_sections_for_fact,
    build_section_atoms,
)


def _reset_collection(chroma_path: str, collection_name: str = "fact_vectors") -> int:
    import chromadb

    client = chromadb.PersistentClient(path=chroma_path)
    try:
        existing = client.get_collection(collection_name)
        n = existing.count()
    except Exception:  # noqa: BLE001 - collection may not exist yet
        return 0
    client.delete_collection(collection_name)
    return n


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Build per-section fact_vectors for C0 enrichment.")
    ap.add_argument("--execute", action="store_true", help="Embed + upsert (default: dry run).")
    ap.add_argument("--reset", action="store_true", help="Delete the collection before ingest.")
    ap.add_argument(
        "--chroma-path",
        default=os.environ.get("CHROMA_PERSIST_DIR", "")
        or str(REPO_ROOT / "data" / "cache" / "chromadb"),
    )
    args = ap.parse_args(argv)

    # Ensure embedding env (CHROMA dir, BGE path) is bootstrapped for the dense ingest.
    from apps_rg.runtime.embedding_settings import bootstrap_apps_rg_embedding_env

    os.environ.setdefault("CHROMA_PERSIST_DIR", args.chroma_path)
    bootstrap_apps_rg_embedding_env(repo_root=REPO_ROOT)
    chroma_path = os.environ.get("CHROMA_PERSIST_DIR", args.chroma_path)

    atoms, summary = build_section_atoms(repo_root=REPO_ROOT)
    summary["chroma_path"] = chroma_path
    summary["execute"] = bool(args.execute)

    if args.execute and args.reset:
        summary["reset_deleted_count"] = _reset_collection(chroma_path)

    if args.execute:
        # Group atoms by section so each chunk carries its section_type while
        # section_targets keeps the full union (upsert is idempotent on fact_id).
        chunks, chunk_atoms, chunk_skipped = atoms_to_fact_vector_chunks(
            atoms,
            section_id="competencies",  # primary section_type; section_targets holds the union
        )
        upserted = upsert_fact_vector_chunks(
            chunks,
            chroma_path=chroma_path,
            atoms=chunk_atoms,
        )
        summary["chunks_built"] = len(chunks)
        summary["chunk_skipped"] = chunk_skipped[:50]
        summary["upserted_count"] = upserted

        import chromadb

        client = chromadb.PersistentClient(path=chroma_path)
        try:
            summary["collection_count_after"] = client.get_collection("fact_vectors").count()
        except Exception:  # noqa: BLE001
            summary["collection_count_after"] = None

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


__all__ = ["assign_sections_for_fact", "build_section_atoms", "main"]


if __name__ == "__main__":
    raise SystemExit(main())
