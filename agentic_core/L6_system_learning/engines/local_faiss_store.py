from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

import numpy as np

from agentic_core.L6_system_learning.types.index_build_metadata_types import IndexBuildMetadata


class LocalFAISSStore:
    """Deterministic in-memory vector store with disk persistence.

    Compatibility shim for callers that expect a LocalFAISSStore API. Uses a
    float32 matrix plus JSONL metadata and writes a stable three-file artifact.
    """

    def __init__(self, base_path: Path) -> None:
        self._base_path = Path(base_path)
        self._memory_indexes: dict[str, dict[str, Any]] = {}
        self._builds: dict[str, dict[str, Any]] = {}

    def begin_build(self, index_id: str, dimension: int, build_seed: int) -> None:
        if dimension <= 0:
            raise ValueError(f"dimension must be > 0, got {dimension}")
        self._builds[index_id] = {
            "dimension": int(dimension),
            "build_seed": int(build_seed),
            "vectors": [],
            "metadatas": [],
        }

    def discard_build(self, index_id: str) -> None:
        self._builds.pop(index_id, None)

    def add_vectors(self, index_id: str, vectors: list[list[float]], metadatas: list[dict[str, Any]]) -> None:
        if index_id not in self._builds:
            raise KeyError(f"index {index_id!r} has no active build")
        if len(vectors) != len(metadatas):
            raise ValueError("vectors and metadatas length mismatch")
        build = self._builds[index_id]
        dim = build["dimension"]
        for vector, metadata in zip(vectors, metadatas):
            if len(vector) != dim:
                raise ValueError(
                    f"vector dimension mismatch for {index_id}: expected {dim}, got {len(vector)}"
                )
            build["vectors"].append([float(x) for x in vector])
            build["metadatas"].append(dict(metadata))

    def finalize_build(
        self,
        index_id: str,
        *,
        built_at_utc: int,
        canonicalization_version: str,
        embedding_model_version: str,
        embedding_model_checksum: str,
    ) -> IndexBuildMetadata:
        if index_id not in self._builds:
            raise KeyError(f"index {index_id!r} has no active build")
        build = self._builds.pop(index_id)
        matrix = np.asarray(build["vectors"], dtype=np.float32)
        if matrix.ndim == 1 and matrix.size:
            matrix = matrix.reshape(1, -1)
        metadata_rows = tuple(build["metadatas"])
        index_version_hash = self._compute_index_version_hash(index_id, matrix, metadata_rows)
        metadata = IndexBuildMetadata(
            index_id=index_id,
            faiss_version="numpy-fallback",
            build_seed=build["build_seed"],
            canonicalization_version=canonicalization_version,
            embedding_model_version=embedding_model_version,
            embedding_model_checksum=embedding_model_checksum,
            built_at_utc=int(built_at_utc),
            index_version_hash=index_version_hash,
            vector_count=int(matrix.shape[0]) if matrix.size else 0,
            dimension=int(build["dimension"]),
        )
        self._memory_indexes[index_id] = {
            "vectors": matrix,
            "metadatas": metadata_rows,
            "metadata": metadata,
        }
        return metadata

    def open(self, index_id: str):
        if index_id not in self._memory_indexes:
            raise KeyError(f"index {index_id!r} is not loaded")
        data = self._memory_indexes[index_id]
        return data["vectors"], data["metadatas"], data["metadata"]

    def prune(self, index_id: str, predicate: Callable[[dict[str, Any]], bool]) -> int:
        vectors, metadatas, metadata = self.open(index_id)
        keep_mask = [not bool(predicate(m)) for m in metadatas]
        removed = len(keep_mask) - sum(keep_mask)
        if removed <= 0:
            return 0
        mask = np.asarray(keep_mask, dtype=bool)
        self._memory_indexes[index_id] = {
            "vectors": vectors[mask],
            "metadatas": tuple(m for m, keep in zip(metadatas, keep_mask) if keep),
            "metadata": metadata,
        }
        return removed

    def rebuild(
        self,
        index_id: str,
        *,
        built_at_utc: int,
        canonicalization_version: str,
        embedding_model_version: str,
        embedding_model_checksum: str,
    ) -> IndexBuildMetadata:
        vectors, metadatas, old_metadata = self.open(index_id)
        index_version_hash = self._compute_index_version_hash(index_id, vectors, metadatas)
        new_metadata = IndexBuildMetadata(
            index_id=index_id,
            faiss_version=old_metadata.faiss_version,
            build_seed=old_metadata.build_seed,
            canonicalization_version=canonicalization_version,
            embedding_model_version=embedding_model_version,
            embedding_model_checksum=embedding_model_checksum,
            built_at_utc=int(built_at_utc),
            index_version_hash=index_version_hash,
            vector_count=int(vectors.shape[0]) if getattr(vectors, "size", 0) else 0,
            dimension=old_metadata.dimension,
        )
        self._memory_indexes[index_id]["metadata"] = new_metadata
        return new_metadata

    def persist_to_disk(self, index_id: str, dest_dir: Path, *, embedder_id: str, model_version: str) -> str:
        vectors, metadatas, metadata = self.open(index_id)
        dest = Path(dest_dir)
        dest.mkdir(parents=True, exist_ok=True)
        faiss_path = dest / "current.faiss"
        meta_path = dest / "current.meta.json"
        rows_path = dest / "metadata.jsonl"
        faiss_path.write_bytes(np.asarray(vectors, dtype=np.float32).tobytes(order="C"))
        with rows_path.open("w", encoding="utf-8", newline="\n") as handle:
            for row in metadatas:
                handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")))
                handle.write("\n")
        meta_payload = {
            "index_build_metadata": json.loads(metadata.to_canonical_json_bytes().decode("ascii")),
            "embedder_id": embedder_id,
            "model_version": model_version,
        }
        meta_path.write_text(
            json.dumps(meta_payload, sort_keys=True, separators=(",", ":")),
            encoding="utf-8",
            newline="\n",
        )
        return self._digest_files(faiss_path, meta_path, rows_path)

    def _compute_index_version_hash(
        self, index_id: str, vectors: np.ndarray, metadatas: tuple[dict[str, Any], ...]
    ) -> str:
        hasher = hashlib.sha256()
        hasher.update(index_id.encode("utf-8"))
        hasher.update(np.asarray(vectors, dtype=np.float32).tobytes(order="C"))
        for row in metadatas:
            hasher.update(json.dumps(row, sort_keys=True, separators=(",", ":")).encode("utf-8"))
        return hasher.hexdigest()

    @staticmethod
    def _digest_files(*paths: Path) -> str:
        hasher = hashlib.sha256()
        for path in sorted(paths, key=lambda p: str(p)):
            hasher.update(path.name.encode("utf-8"))
            hasher.update(path.read_bytes())
        return hasher.hexdigest()
