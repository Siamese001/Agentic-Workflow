"""faiss_startup_integrity — Boot-time FAISS index integrity sweep.

Provides ``verify_all_indexes_in_dir()`` — a fail-closed sweep that walks a
base directory, finds all persisted 3-file FAISS artifacts
(``<index_id>/index.json``, ``<index_id>/meta.json``, ``<index_id>/manifest.json``),
and verifies each one by loading it through SHA-256 verification.

Any integrity violation (missing file, SHA-256 mismatch, parse error) raises
``StartupIntegrityError`` immediately — no partial loading, no silent skip.

Usage (at process boot)::

    from system_learning.engines.faiss_startup_integrity import (
        verify_all_indexes_in_dir,
    )

    verify_all_indexes_in_dir(Path("/data/faiss"), expected_embedder_id="hash-fallback")
    # Returns dict[index_id -> digest] on success.
    # Raises StartupIntegrityError on any mismatch.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path


class StartupIntegrityError(RuntimeError):
    """Raised when boot-time FAISS integrity sweep detects a violation.

    Fail-closed: any error during ``verify_all_indexes_in_dir()`` raises this
    immediately with no fallback.  The process should refuse to start.
    """


@dataclass
class IndexVerificationResult:
    """Result of verifying a single persisted FAISS index.

    Attributes:
        index_id: The logical index identifier (subdirectory name).
        vector_count: Number of vectors confirmed in the index.
        digest: W-A-DETERMINISM-DIGEST (sha256 of manifest + index + meta binding).
        embedder_id: Embedder ID confirmed from the manifest.
        model_version: Model version confirmed from the manifest.
    """

    index_id: str
    vector_count: int
    digest: str
    embedder_id: str
    model_version: str


def _verify_single_index(
    index_id: str,
    index_dir: Path,
    *,
    expected_embedder_id: str | None,
) -> IndexVerificationResult:
    """Verify one 3-file FAISS artifact and return its verification result.

    Raises:
        StartupIntegrityError: On any integrity violation.
    """
    manifest_path = index_dir / "manifest.json"
    index_path = index_dir / "index.json"
    meta_path = index_dir / "meta.json"
    for p in (manifest_path, index_path, meta_path):
        if not p.exists():
            raise StartupIntegrityError(f"[{index_id}] Missing required file: {p.name} in {index_dir}")
    try:
        manifest_bytes = manifest_path.read_bytes()
        manifest = json.loads(manifest_bytes.decode("ascii"))
    except (
        json.JSONDecodeError,
        UnicodeDecodeError,
        OSError,
    ) as exc:  # guardian: File operations with encoding need error-specific handling
        raise StartupIntegrityError(f"[{index_id}] manifest.json parse error: {exc}") from exc
    required_fields = {
        "schema_version",
        "embedder_id",
        "model_version",
        "dims",
        "vector_count",
        "sha256_index",
        "sha256_meta_canonical",
    }
    missing = required_fields - manifest.keys()
    if missing:
        raise StartupIntegrityError(f"[{index_id}] manifest.json missing required fields: {sorted(missing)}")
    if expected_embedder_id is not None and manifest["embedder_id"] != expected_embedder_id:
        raise StartupIntegrityError(
            f"[{index_id}] embedder_id mismatch: manifest has '{manifest['embedder_id']}' but runtime expects '{expected_embedder_id}'",
        )
    try:
        index_bytes = index_path.read_bytes()
    except OSError as exc:  # guardian: Add error context logging
        raise StartupIntegrityError(f"[{index_id}] Cannot read index.json: {exc}") from exc
    actual_sha_index = hashlib.sha256(index_bytes).hexdigest()
    if actual_sha_index != manifest["sha256_index"]:
        raise StartupIntegrityError(
            f"[{index_id}] index.json SHA-256 mismatch: expected {manifest['sha256_index']!r}, got {actual_sha_index!r}",
        )
    try:
        meta_bytes = meta_path.read_bytes()
    except OSError as exc:  # guardian: Add error context logging
        raise StartupIntegrityError(f"[{index_id}] Cannot read meta.json: {exc}") from exc
    actual_sha_meta = hashlib.sha256(meta_bytes).hexdigest()
    if actual_sha_meta != manifest["sha256_meta_canonical"]:
        raise StartupIntegrityError(
            f"[{index_id}] meta.json SHA-256 mismatch: expected {manifest['sha256_meta_canonical']!r}, got {actual_sha_meta!r}",
        )
    sha256_manifest = hashlib.sha256(manifest_bytes).hexdigest()
    digest_input = f"{manifest['embedder_id']}|{manifest['model_version']}|{manifest['dims']}|{manifest['vector_count']}|{manifest['sha256_index']}|{manifest['sha256_meta_canonical']}|{sha256_manifest}"
    digest = hashlib.sha256(digest_input.encode("ascii")).hexdigest()
    return IndexVerificationResult(
        index_id=index_id,
        vector_count=int(manifest["vector_count"]),
        digest=digest,
        embedder_id=manifest["embedder_id"],
        model_version=manifest["model_version"],
    )


def verify_all_indexes_in_dir(base_dir: Path, *, expected_embedder_id: str | None = None) -> dict[str, str]:
    """Sweep ``base_dir`` for all persisted FAISS index subdirectories and verify each.

    A subdirectory is treated as a FAISS index artifact if it contains at least
    a ``manifest.json`` file.

    Args:
        base_dir: Root directory under which per-index subdirectories live.
        expected_embedder_id: If provided, every manifest must match this
            embedder ID exactly; mismatch raises ``StartupIntegrityError``.

    Returns:
        ``dict[index_id -> digest]`` mapping each verified index to its
        W-A-DETERMINISM-DIGEST.  Empty dict if no indexes are present.

    Raises:
        StartupIntegrityError: On any integrity violation across any index.
            The first violation raises immediately (fail-closed).
        ValueError: If ``base_dir`` does not exist.
    """
    base = Path(base_dir)
    if not base.exists():
        raise ValueError(f"base_dir does not exist: {base}")
    results: dict[str, str] = {}
    candidate_dirs = sorted(d for d in base.iterdir() if d.is_dir())
    for candidate in candidate_dirs:
        if not (candidate / "manifest.json").exists():
            continue
        index_id = candidate.name
        result = _verify_single_index(index_id, candidate, expected_embedder_id=expected_embedder_id)
        results[index_id] = result.digest
    return results


__all__ = ["StartupIntegrityError", "IndexVerificationResult", "verify_all_indexes_in_dir"]
