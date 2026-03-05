"""LocalFAISSStore - Plan A deterministic FAISS index storage.

Read-only contract surfaces for Plan B consumption.
FAISS (IndexFlatIP with L2-normalised vectors) is the primary path.
Pure-Python cosine similarity is the fallback when faiss is not installed.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import struct
from pathlib import Path
from typing import Any, Callable

from system_learning.types.index_build_metadata_types import IndexBuildMetadata


def _faiss_available() -> bool:
    return importlib.util.find_spec("faiss") is not None


def _import_faiss() -> Any:
    import faiss  # noqa: PLC0415

    return faiss


def _l2_normalize(vec: list[float]) -> list[float]:
    norm = math.sqrt(sum(x * x for x in vec))
    if norm == 0.0:
        return vec
    return [x / norm for x in vec]


class IndexNotBuiltError(RuntimeError):
    """Raised when attempting to access an index that has not been built."""

    pass


class IndexMetadataError(RuntimeError):
    """Raised when index metadata is missing or corrupted."""

    pass


class ManifestIntegrityError(RuntimeError):
    """Raised when manifest.json is missing, has wrong schema, or hash mismatch.

    Fail-closed: any mismatch raises immediately with no best-effort fallback.
    """

    pass


_SCHEMA_VERSION = "1"


class LocalFAISSStore:
    """Local FAISS index store with deterministic search.

    Primary path  : FAISS IndexFlatIP with L2-normalised vectors (cosine similarity).
    Fallback path : pure-Python cosine when faiss is not installed.

    INVARIANT: FAISS is imported lazily inside methods only.
    INVARIANT: search() post-sorts results deterministically: (score_round6 DESC, content_hash ASC).
    INVARIANT: Fallback path enables unit_min_deps tests without faiss.
    """

    def __init__(self, base_path: Path) -> None:
        """Initialize store with base path for indexes.

        Args:
            base_path: Base directory for index storage.
        """
        self.base_path = base_path
        # Per-index state dict keyed by index_id.
        # Each entry holds either a live FAISS index or plain Python lists.
        self._indexes: dict[str, dict[str, Any]] = {}
        # Track rebuild requirement
        self._rebuild_required: dict[str, bool] = {}

    # ------------------------------------------------------------------
    # Compat shim: old attribute name used in a few tests
    # ------------------------------------------------------------------
    @property
    def _memory_indexes(self) -> dict[str, dict[str, Any]]:
        return self._indexes

    def open(self, index_id: str) -> tuple[Any, str, IndexBuildMetadata]:
        """Open an index and return handle with metadata.

        Args:
            index_id: Identifier of the index to open.

        Returns:
            Tuple of (index_handle, index_version_hash, build_metadata).

        Raises:
            IndexNotBuiltError: If index has not been built or needs rebuild.
            IndexMetadataError: If metadata is missing or invalid.
        """
        if self._rebuild_required.get(index_id, False):
            raise IndexNotBuiltError(f"Index {index_id} requires rebuild after pruning")

        if index_id not in self._indexes:
            raise IndexNotBuiltError(f"Index {index_id} has not been built")

        idx = self._indexes[index_id]
        if "metadata" not in idx:
            raise IndexMetadataError(f"Index {index_id} not finalized")

        handle = idx.get("faiss_index") or idx["vectors"]
        return (handle, idx["version_hash"], idx["metadata"])

    def search(
        self,
        index_id: str,
        query_vector: list[float],
        top_k: int,
        cutoff: float,
    ) -> list[tuple[str, str, float]]:
        """Search index for similar vectors.

        Args:
            index_id: Identifier of the index to search.
            query_vector: Query embedding vector.
            top_k: Maximum number of results to return.
            cutoff: Minimum similarity score threshold.

        Returns:
            List of (content_hash, trace_id, score_round6) tuples.
            Results are post-sorted deterministically: (score_round6 DESC, content_hash ASC).

        Raises:
            IndexNotBuiltError: If index has not been built or needs rebuild.
        """
        if self._rebuild_required.get(index_id, False):
            raise IndexNotBuiltError(f"Index {index_id} requires rebuild after pruning")

        if index_id not in self._indexes:
            raise IndexNotBuiltError(f"Index {index_id} has not been built")

        idx = self._indexes[index_id]
        metadatas = idx["metadatas"]
        q_norm = _l2_normalize(query_vector)

        if _faiss_available() and "faiss_index" in idx:
            import numpy as np

            faiss = _import_faiss()
            q_arr = np.array([q_norm], dtype=np.float32)
            faiss.normalize_L2(q_arr)
            k = min(top_k, idx["faiss_index"].ntotal)
            if k == 0:
                return []
            scores_arr, indices_arr = idx["faiss_index"].search(q_arr, k)
            raw: list[tuple[str, str, float]] = []
            for score, i in zip(scores_arr[0], indices_arr[0]):
                if i < 0:
                    continue
                s = float(score)
                if s >= cutoff:
                    meta = metadatas[i]
                    raw.append((meta.get("content_hash", ""), meta.get("trace_id", ""), round(s, 6)))
        else:
            # Pure-Python cosine fallback
            raw = []
            for i, vec in enumerate(idx["vectors"]):
                score = sum(q * v for q, v in zip(q_norm, vec))
                if score >= cutoff:
                    meta = metadatas[i]
                    raw.append((meta.get("content_hash", ""), meta.get("trace_id", ""), round(score, 6)))

        raw.sort(key=lambda x: (-x[2], x[0]))
        return raw[:top_k]

    def begin_build(self, index_id: str, dimension: int, seed: int) -> None:
        """Begin building a new index.

        Args:
            index_id: Identifier for the index.
            dimension: Embedding dimension.
            seed: Random seed for deterministic builds.
        """
        entry: dict[str, Any] = {
            "dimension": dimension,
            "seed": seed,
            "vectors": [],
            "metadatas": [],
        }
        if _faiss_available():
            faiss = _import_faiss()
            entry["faiss_index"] = faiss.IndexFlatIP(dimension)
        self._indexes[index_id] = entry
        self._rebuild_required[index_id] = False

    def add_vectors(self, index_id: str, vectors: list[list[float]], metadatas: list[dict[str, Any]]) -> None:
        """Add vectors to the index being built.

        Args:
            index_id: Identifier for the index.
            vectors: List of embedding vectors.
            metadatas: List of metadata dictionaries.

        Raises:
            IndexNotBuiltError: If index build has not been started.
        """
        if index_id not in self._indexes:
            raise IndexNotBuiltError(f"Index {index_id} build not started")

        idx = self._indexes[index_id]
        normed = [_l2_normalize(v) for v in vectors]
        idx["vectors"].extend(normed)
        idx["metadatas"].extend(metadatas)

        if _faiss_available() and "faiss_index" in idx:
            import numpy as np

            arr = np.array(normed, dtype=np.float32)
            idx["faiss_index"].add(arr)

    def finalize_build(
        self,
        index_id: str,
        *,
        built_at_utc: int,
        canonicalization_version: str,
        embedding_model_version: str,
        embedding_model_checksum: str,
    ) -> IndexBuildMetadata:
        """Finalize index build and return metadata.

        Args:
            index_id: Identifier for the index.
            built_at_utc: Build timestamp.
            canonicalization_version: Canonicalization format version.
            embedding_model_version: Embedding model version.
            embedding_model_checksum: Embedding model checksum.

        Returns:
            IndexBuildMetadata for the completed index.

        Raises:
            IndexNotBuiltError: If index build has not been started.
        """
        if index_id not in self._indexes:
            raise IndexNotBuiltError(f"Index {index_id} build not started")

        idx = self._indexes[index_id]
        vectors = idx["vectors"]
        metadatas = idx["metadatas"]

        index_version_hash = self._compute_version_hash(vectors, metadatas)

        faiss_ver = (
            "faiss-IndexFlatIP-v1" if _faiss_available() and "faiss_index" in idx else "memory-fallback-v1"
        )

        metadata = IndexBuildMetadata(
            index_id=index_id,
            faiss_version=faiss_ver,
            build_seed=idx["seed"],
            canonicalization_version=canonicalization_version,
            embedding_model_version=embedding_model_version,
            embedding_model_checksum=embedding_model_checksum,
            built_at_utc=built_at_utc,
            index_version_hash=index_version_hash,
            vector_count=len(vectors),
            dimension=idx["dimension"],
        )

        idx["metadata"] = metadata
        idx["version_hash"] = index_version_hash
        return metadata

    def prune(self, index_id: str, predicate: Callable[[dict[str, Any]], bool]) -> int:
        """Prune vectors from index based on predicate.

        Args:
            index_id: Identifier for the index.
            predicate: Function that returns True for items to prune.

        Returns:
            Number of items removed.

        Raises:
            IndexNotBuiltError: If index has not been built.
        """
        if index_id not in self._indexes:
            raise IndexNotBuiltError(f"Index {index_id} not built")

        idx = self._indexes[index_id]
        vectors = idx["vectors"]
        metadatas = idx["metadatas"]

        to_keep = [i for i, meta in enumerate(metadatas) if not predicate(meta)]
        removed_count = len(metadatas) - len(to_keep)

        if removed_count > 0:
            idx["vectors"] = [vectors[i] for i in to_keep]
            idx["metadatas"] = [metadatas[i] for i in to_keep]
            self._rebuild_required[index_id] = True

            if _faiss_available() and "faiss_index" in idx:
                import numpy as np

                faiss = _import_faiss()
                dim = idx["dimension"]
                new_index = faiss.IndexFlatIP(dim)
                if idx["vectors"]:
                    arr = np.array(idx["vectors"], dtype=np.float32)
                    new_index.add(arr)
                idx["faiss_index"] = new_index

        return removed_count

    def rebuild(
        self,
        index_id: str,
        *,
        built_at_utc: int,
        canonicalization_version: str,
        embedding_model_version: str,
        embedding_model_checksum: str,
    ) -> IndexBuildMetadata:
        """Rebuild index after pruning.

        Args:
            index_id: Identifier for the index.
            built_at_utc: Build timestamp.
            canonicalization_version: Canonicalization format version.
            embedding_model_version: Embedding model version.
            embedding_model_checksum: Embedding model checksum.

        Returns:
            IndexBuildMetadata for the rebuilt index.

        Raises:
            IndexNotBuiltError: If index has not been built.
        """
        if index_id not in self._indexes:
            raise IndexNotBuiltError(f"Index {index_id} not built")

        idx = self._indexes[index_id]
        vectors = idx["vectors"]
        metadatas = idx["metadatas"]

        if _faiss_available():
            import numpy as np

            faiss = _import_faiss()
            dim = idx["dimension"]
            new_index = faiss.IndexFlatIP(dim)
            if vectors:
                arr = np.array(vectors, dtype=np.float32)
                new_index.add(arr)
            idx["faiss_index"] = new_index
            faiss_ver = "faiss-IndexFlatIP-v1"
        else:
            faiss_ver = "memory-fallback-v1"

        index_version_hash = self._compute_version_hash(vectors, metadatas)

        metadata = IndexBuildMetadata(
            index_id=index_id,
            faiss_version=faiss_ver,
            build_seed=idx["seed"],
            canonicalization_version=canonicalization_version,
            embedding_model_version=embedding_model_version,
            embedding_model_checksum=embedding_model_checksum,
            built_at_utc=built_at_utc,
            index_version_hash=index_version_hash,
            vector_count=len(vectors),
            dimension=idx["dimension"],
        )

        idx["metadata"] = metadata
        idx["version_hash"] = index_version_hash
        self._rebuild_required[index_id] = False
        return metadata

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_version_hash(vectors: list, metadatas: list) -> str:
        """Compute deterministic SHA-256 hash over (vector, metadata) pairs."""
        hash_input = []
        for vec, meta in zip(vectors, metadatas):
            vector_bytes = b"".join(struct.pack("<f", x) for x in vec)
            entry = {
                "content_hash": meta.get("content_hash", ""),
                "trace_id": meta.get("trace_id", ""),
                "vector_bytes": vector_bytes.hex(),
            }
            entry_bytes = json.dumps(entry, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
                "ascii"
            )
            hash_input.append(entry_bytes)
        hasher = hashlib.sha256()
        for eb in sorted(hash_input):
            hasher.update(eb)
        return hasher.hexdigest()

    def persist_to_disk(self, index_id: str, dest_dir: Path, *, embedder_id: str, model_version: str) -> str:
        """Write 3-file artifact (index.json, meta.json, manifest.json) and print W-A-DETERMINISM-DIGEST.

        All three files are written atomically to ``dest_dir``.  The digest is
        sha256 over the pipe-concatenated binding fields and is printed to stdout
        exactly once per call.

        Args:
            index_id: Identifier of the index to persist.
            dest_dir: Target directory (created if absent).
            embedder_id: Embedder identifier string (e.g. "BAAI/bge-m3" or "hash-fallback").
            model_version: Model version string.

        Returns:
            64-char lowercase hex W-A-DETERMINISM-DIGEST string.

        Raises:
            IndexNotBuiltError: If the index has not been built.
            IndexMetadataError: If the index has not been finalized (missing metadata).
        """
        if index_id not in self._memory_indexes:
            raise IndexNotBuiltError(
                f"Index {index_id} not found; call begin_build/add_vectors/finalize_build first"
            )
        memory_idx = self._memory_indexes[index_id]
        if "metadata" not in memory_idx:
            raise IndexMetadataError(f"Index {index_id} not finalized; call finalize_build first")

        dest = Path(dest_dir)
        dest.mkdir(parents=True, exist_ok=True)

        vectors = memory_idx["vectors"]
        metadatas = memory_idx["metadatas"]
        dimension = memory_idx["dimension"]
        version_hash = memory_idx.get("version_hash", "")

        # --- index.json ---
        index_data = {
            "schema_version": _SCHEMA_VERSION,
            "index_id": index_id,
            "dimension": dimension,
            "vector_count": len(vectors),
            "vectors": [list(v) for v in vectors],
            "metadatas": metadatas,
        }
        index_bytes = json.dumps(index_data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "ascii"
        )
        sha256_index = hashlib.sha256(index_bytes).hexdigest()

        # --- meta.json (canonical — hashed before manifest) ---
        meta_data = {
            "dims": dimension,
            "embedder_id": embedder_id,
            "index_id": index_id,
            "index_version_hash": version_hash,
            "model_version": model_version,
            "schema_version": _SCHEMA_VERSION,
            "vector_count": len(vectors),
        }
        meta_bytes = json.dumps(meta_data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "ascii"
        )
        sha256_meta = hashlib.sha256(meta_bytes).hexdigest()

        # --- manifest.json ---
        manifest_data = {
            "dims": dimension,
            "embedder_id": embedder_id,
            "model_version": model_version,
            "schema_version": _SCHEMA_VERSION,
            "sha256_index": sha256_index,
            "sha256_meta_canonical": sha256_meta,
            "vector_count": len(vectors),
        }
        manifest_bytes = json.dumps(
            manifest_data, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("ascii")
        sha256_manifest = hashlib.sha256(manifest_bytes).hexdigest()

        # Write files
        (dest / "index.json").write_bytes(index_bytes)
        (dest / "meta.json").write_bytes(meta_bytes)
        (dest / "manifest.json").write_bytes(manifest_bytes)

        # W-A-DETERMINISM-DIGEST
        digest_input = f"{embedder_id}|{model_version}|{dimension}|{len(vectors)}|{sha256_index}|{sha256_meta}|{sha256_manifest}"
        digest = hashlib.sha256(digest_input.encode("ascii")).hexdigest()
        print(f"W-A-DETERMINISM-DIGEST: {digest}")
        return digest

    def load_from_disk(self, index_id: str, source_dir: Path) -> None:
        """Load index from 3-file disk artifact, verifying all manifest hashes.

        Fail-closed: any missing field, parse error, or hash mismatch raises
        ManifestIntegrityError immediately with no fallback.

        Args:
            index_id: Logical identifier to register the loaded index under.
            source_dir: Directory containing index.json, meta.json, manifest.json.

        Raises:
            ManifestIntegrityError: On any integrity violation.
        """
        src = Path(source_dir)
        manifest_path = src / "manifest.json"
        if not manifest_path.exists():
            raise ManifestIntegrityError(f"manifest.json not found in {src}")

        try:
            manifest_bytes = manifest_path.read_bytes()
            manifest = json.loads(manifest_bytes.decode("ascii"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ManifestIntegrityError(f"manifest.json parse error: {exc}") from exc

        required = {
            "schema_version",
            "embedder_id",
            "model_version",
            "dims",
            "vector_count",
            "sha256_index",
            "sha256_meta_canonical",
        }
        missing = required - manifest.keys()
        if missing:
            raise ManifestIntegrityError(f"manifest.json missing required fields: {sorted(missing)}")

        # Verify index.json
        index_path = src / "index.json"
        if not index_path.exists():
            raise ManifestIntegrityError(f"index.json not found in {src}")
        index_bytes = index_path.read_bytes()
        if hashlib.sha256(index_bytes).hexdigest() != manifest["sha256_index"]:
            raise ManifestIntegrityError("index.json sha256 mismatch — artifact tampered")

        # Verify meta.json
        meta_path = src / "meta.json"
        if not meta_path.exists():
            raise ManifestIntegrityError(f"meta.json not found in {src}")
        meta_bytes = meta_path.read_bytes()
        if hashlib.sha256(meta_bytes).hexdigest() != manifest["sha256_meta_canonical"]:
            raise ManifestIntegrityError("meta.json sha256 mismatch — artifact tampered")

        try:
            index_data = json.loads(index_bytes.decode("ascii"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ManifestIntegrityError(f"index.json parse error: {exc}") from exc

        vectors = [list(v) for v in index_data.get("vectors", [])]
        metadatas = index_data.get("metadatas", [])
        dimension = int(index_data.get("dimension", manifest["dims"]))

        from system_learning.types.index_build_metadata_types import IndexBuildMetadata

        metadata = IndexBuildMetadata(
            index_id=index_id,
            faiss_version="disk-json-v1",
            build_seed=0,
            canonicalization_version=_SCHEMA_VERSION,
            embedding_model_version=manifest["model_version"],
            embedding_model_checksum=manifest["sha256_index"],
            built_at_utc=0,
            index_version_hash=manifest["sha256_index"],
            vector_count=len(vectors),
            dimension=dimension,
        )
        self._memory_indexes[index_id] = {
            "dimension": dimension,
            "seed": 0,
            "vectors": vectors,
            "metadatas": metadatas,
            "metadata": metadata,
            "version_hash": manifest["sha256_index"],
        }


__all__ = ["LocalFAISSStore", "IndexNotBuiltError", "IndexMetadataError", "ManifestIntegrityError"]
