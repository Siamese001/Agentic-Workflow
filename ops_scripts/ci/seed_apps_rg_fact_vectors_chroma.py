#!/usr/bin/env python3
"""SEED-RG-FV — Idempotently seed ``fact_vectors`` at the canonical Chroma persist path.

Used by ``run_contract_gates`` immediately before ``check_apps_rg_fact_vectors_readiness``
so fresh CI checkouts satisfy RG-FV-1 without manual operator ingest.

Default behavior (no flags): skip when collection exists with >= expected doc count;
otherwise ingest from the smoke fixture. Partial counts (< expected) trigger delete + re-ingest.

``--force`` — always delete ``fact_vectors`` then re-ingest.

Bypass: ``APPS_RG_SEED_FACT_VECTORS_BYPASS=1`` (exit 0, no work).

Requires: ``chromadb``, ``sentence-transformers`` (same as ``chroma_ingest_pipeline``).
If imports fail, exits 0 with a skip message (readiness gate still runs; may ERROR).
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_DOCS = 6
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "apps_rg" / "fact_vectors_c0_smoke.chroma_input"
COLLECTION = "fact_vectors"


def _chroma_path() -> str:
    return os.environ.get("CHROMA_PERSIST_DIR", str(REPO_ROOT / "data" / "cache" / "chromadb"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Delete fact_vectors collection and re-ingest from fixture.",
    )
    args = parser.parse_args(argv)

    if os.environ.get("APPS_RG_SEED_FACT_VECTORS_BYPASS", "").lower() in ("1", "true"):
        print("[SEED-RG-FV] APPS_RG_SEED_FACT_VECTORS_BYPASS=1 — skipping")
        return 0

    if not FIXTURE.is_file():
        print(f"[SEED-RG-FV] SKIP: fixture missing: {FIXTURE}")
        return 0

    try:
        import chromadb  # type: ignore[import-not-found]
    except ImportError:
        print("[SEED-RG-FV] SKIP: chromadb not installed")
        return 0

    chroma_path = _chroma_path()
    Path(chroma_path).mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=chroma_path)
    existing = 0
    try:
        col = client.get_collection(COLLECTION)
        existing = int(col.count())
    except Exception:
        existing = 0

    if args.force:
        try:
            client.delete_collection(COLLECTION)
        except Exception:
            pass
        existing = 0
    elif existing >= EXPECTED_DOCS:
        print(
            f"[SEED-RG-FV] OK skip — {COLLECTION} count={existing} "
            f">= {EXPECTED_DOCS} at {chroma_path}",
        )
        return 0
    elif 0 < existing < EXPECTED_DOCS:
        print(
            f"[SEED-RG-FV] repair — partial count={existing}, re-ingesting from fixture",
        )
        try:
            client.delete_collection(COLLECTION)
        except Exception:
            pass

    sys.path.insert(0, str(REPO_ROOT))
    try:
        from tools.ingestion.chroma_ingest_pipeline import load_documents, run_ingestion
    except ImportError as exc:
        print(f"[SEED-RG-FV] SKIP: cannot import ingestion pipeline: {exc}")
        return 0

    try:
        docs = load_documents(FIXTURE)
    except (ValueError, OSError) as exc:
        print(f"[SEED-RG-FV] ERROR loading fixture: {exc}", file=sys.stderr)
        return 1

    try:
        n = run_ingestion(
            docs,
            chromadb_path=chroma_path,
            collection_name=COLLECTION,
        )
    except Exception as exc:
        print(f"[SEED-RG-FV] ERROR during ingestion: {exc}", file=sys.stderr)
        return 1

    print(f"[SEED-RG-FV] OK ingested {n} docs into {COLLECTION} at {chroma_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
