"""Migrate the apps_qna flat C0 index into canonical Chroma.

Reads the existing external flat index from ``C:/AgenticEmbeddings`` and writes
the canonical C0 retrieval collection under ``data/cache/chromadb``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from agentic_core.L4_state.config.chroma_paths import canonical_persist_dir
from agentic_core.L4_state.utils.client.chroma_client import chromadb_module as chromadb

COLLECTION_NAME = "apps_qna_interview_cards"
DEFAULT_INDEX_DIR = Path("C:/AgenticEmbeddings/indexes/apps_qna_interview_cards")
EXPECTED_MODEL = "BAAI/bge-m3"
EXPECTED_DIMS = 1024
EXPECTED_DISTANCE = "cosine"
DEFAULT_BATCH_SIZE = 32


def _collection_reset_error_types() -> tuple[type[BaseException], ...]:
    error_types: list[type[BaseException]] = [ValueError, RuntimeError, KeyError, LookupError]
    not_found_error = getattr(getattr(chromadb, "errors", None), "NotFoundError", None)
    if isinstance(not_found_error, type) and issubclass(not_found_error, BaseException):
        error_types.append(not_found_error)
    return tuple(error_types)


_COLLECTION_RESET_ERROR_TYPES = _collection_reset_error_types()


@dataclass(frozen=True)
class MigrationSummary:
    source_index: Path
    persist_dir: Path
    collection_name: str
    vector_count: int
    dimension: int
    index_sha256: str
    dry_run: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_index": str(self.source_index),
            "persist_dir": str(self.persist_dir),
            "collection_name": self.collection_name,
            "vector_count": self.vector_count,
            "dimension": self.dimension,
            "index_sha256": self.index_sha256,
            "dry_run": self.dry_run,
        }


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_and_validate(index_dir: Path) -> tuple[dict[str, Any], dict[str, Any], str]:
    index_file = index_dir / "index.json"
    manifest_file = index_dir / "manifest.json"
    meta_file = index_dir / "meta.json"
    missing = [str(p) for p in (index_file, manifest_file, meta_file) if not p.is_file()]
    if missing:
        raise FileNotFoundError(f"apps_qna flat index missing required files: {missing}")

    index_sha = _sha256_file(index_file)
    index = _load_json(index_file)
    manifest = _load_json(manifest_file)
    meta = _load_json(meta_file)

    if index.get("index_type") != "flat":
        raise ValueError(f"index_type must be flat, got {index.get('index_type')!r}")
    if index.get("distance_metric") != EXPECTED_DISTANCE:
        raise ValueError(f"distance_metric must be cosine, got {index.get('distance_metric')!r}")
    if manifest.get("embedder_id") != EXPECTED_MODEL or manifest.get("model_version") != EXPECTED_MODEL:
        raise ValueError("manifest embedding model must be BAAI/bge-m3")
    if meta.get("embedder_id") != EXPECTED_MODEL or meta.get("model_version") != EXPECTED_MODEL:
        raise ValueError("meta embedding model must be BAAI/bge-m3")
    if int(manifest.get("dims", 0)) != EXPECTED_DIMS or int(meta.get("dims", 0)) != EXPECTED_DIMS:
        raise ValueError("manifest/meta dimensions must be 1024")

    vectors = index.get("vectors")
    if not isinstance(vectors, list) or not vectors:
        raise ValueError("index.json must contain a non-empty vectors list")
    expected_count = int(manifest.get("vector_count", 0))
    if len(vectors) != expected_count or int(meta.get("vector_count", 0)) != expected_count:
        raise ValueError(
            f"vector_count mismatch: index={len(vectors)} manifest={expected_count} meta={meta.get('vector_count')}"
        )

    seen: set[str] = set()
    for pos, entry in enumerate(vectors):
        row_id = entry.get("id")
        embedding = entry.get("embedding")
        metadata = entry.get("metadata")
        if not isinstance(row_id, str) or not row_id:
            raise ValueError(f"vectors[{pos}].id must be a non-empty string")
        if row_id in seen:
            raise ValueError(f"duplicate vector id: {row_id}")
        seen.add(row_id)
        if not isinstance(embedding, list) or len(embedding) != EXPECTED_DIMS:
            raise ValueError(f"vectors[{pos}] embedding must be {EXPECTED_DIMS}-dim")
        if not isinstance(metadata, dict):
            raise ValueError(f"vectors[{pos}].metadata must be a dict")

    return index, manifest, index_sha


def _document_for_entry(entry: dict[str, Any]) -> str:
    metadata = entry.get("metadata") or {}
    evidence = metadata.get("expected_evidence") or []
    if isinstance(evidence, list):
        evidence_text = " ".join(str(item) for item in evidence)
    else:
        evidence_text = str(evidence)
    return " ".join(
        part
        for part in [
            str(entry.get("id", "")),
            str(metadata.get("card_id", "")),
            str(metadata.get("base_card_type", "")),
            str(metadata.get("archetype", "")),
            evidence_text,
        ]
        if part
    )


def _metadata_for_entry(entry: dict[str, Any], *, index_sha: str, manifest: dict[str, Any]) -> dict[str, Any]:
    metadata = dict(entry.get("metadata") or {})
    evidence = metadata.get("expected_evidence")
    if isinstance(evidence, (list, tuple, dict)):
        metadata["expected_evidence"] = json.dumps(evidence, sort_keys=True)
    metadata.update(
        {
            "source_index": "C:/AgenticEmbeddings/indexes/apps_qna_interview_cards",
            "source_index_sha256": index_sha,
            "embedding_model": EXPECTED_MODEL,
            "embedding_dim": EXPECTED_DIMS,
            "schema_version": str(manifest.get("schema_version", "")),
            "migration_plan": "bge-review-apps-qna-c0-chroma-migration-f9a3b2",
        }
    )
    return metadata


def _batched(items: list[Any], batch_size: int) -> list[list[Any]]:
    return [items[i : i + batch_size] for i in range(0, len(items), batch_size)]


def migrate_flat_index_to_chroma(
    *,
    index_dir: Path = DEFAULT_INDEX_DIR,
    persist_dir: Path | None = None,
    collection_name: str = COLLECTION_NAME,
    batch_size: int = DEFAULT_BATCH_SIZE,
    reset: bool = False,
    dry_run: bool = False,
) -> MigrationSummary:
    if batch_size < 1:
        raise ValueError("batch_size must be >= 1")
    index, manifest, index_sha = _load_and_validate(index_dir)
    target_dir = persist_dir or canonical_persist_dir()
    vectors: list[dict[str, Any]] = index["vectors"]
    summary = MigrationSummary(
        source_index=index_dir,
        persist_dir=target_dir,
        collection_name=collection_name,
        vector_count=len(vectors),
        dimension=EXPECTED_DIMS,
        index_sha256=index_sha,
        dry_run=dry_run,
    )
    if dry_run:
        return summary

    target_dir.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(target_dir))
    if reset:
        try:
            client.delete_collection(collection_name)
        except _COLLECTION_RESET_ERROR_TYPES as exc:
            if "not found" not in str(exc).lower() and "does not exist" not in str(exc).lower():
                raise

    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={
            "hnsw:space": EXPECTED_DISTANCE,
            "embedding_model": EXPECTED_MODEL,
            "embedding_dim": EXPECTED_DIMS,
            "source_index_sha256": index_sha,
            "migration_plan": "bge-review-apps-qna-c0-chroma-migration-f9a3b2",
        },
    )

    ids = [str(entry["id"]) for entry in vectors]
    documents = [_document_for_entry(entry) for entry in vectors]
    metadatas = [_metadata_for_entry(entry, index_sha=index_sha, manifest=manifest) for entry in vectors]
    embeddings = [entry["embedding"] for entry in vectors]

    for id_batch, doc_batch, meta_batch, embedding_batch in zip(
        _batched(ids, batch_size),
        _batched(documents, batch_size),
        _batched(metadatas, batch_size),
        _batched(embeddings, batch_size),
    ):
        collection.upsert(
            ids=id_batch,
            documents=doc_batch,
            metadatas=meta_batch,
            embeddings=embedding_batch,
        )
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Migrate apps_qna flat C0 index to canonical Chroma")
    parser.add_argument("--index-dir", type=Path, default=DEFAULT_INDEX_DIR)
    parser.add_argument("--persist-dir", type=Path, default=None)
    parser.add_argument("--collection", default=COLLECTION_NAME)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--reset", action="store_true", help="Delete the target collection before ingest")
    parser.add_argument("--dry-run", action="store_true", help="Validate inputs and print summary without writing")
    args = parser.parse_args(argv)

    summary = migrate_flat_index_to_chroma(
        index_dir=args.index_dir,
        persist_dir=args.persist_dir,
        collection_name=args.collection,
        batch_size=args.batch_size,
        reset=args.reset,
        dry_run=args.dry_run,
    )
    print(json.dumps(summary.to_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
