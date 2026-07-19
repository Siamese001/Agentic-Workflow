"""Immutable exact-vector projection and candidate-only C0.3 search."""

from __future__ import annotations

import hashlib
import json
import math
import os
import sqlite3
import struct
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.c03_skill_assertion_corpus import canonical_sha256

PROJECTION_SCHEMA_VERSION = "apps_rg.graph_skill_embedding_projection.v1"


class GraphSkillEmbeddingContractError(RuntimeError):
    """Raised when vector or authority parity fails closed."""


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _vector_bytes(values: Sequence[float], dimension: int) -> bytes:
    if len(values) != dimension:
        raise GraphSkillEmbeddingContractError(
            f"vector dimension mismatch: expected {dimension}, observed {len(values)}"
        )
    floats = [float(value) for value in values]
    if not all(math.isfinite(value) for value in floats):
        raise GraphSkillEmbeddingContractError("vector values must be finite")
    norm = math.sqrt(math.fsum(value * value for value in floats))
    if not math.isclose(norm, 1.0, rel_tol=0.0, abs_tol=1e-5):
        raise GraphSkillEmbeddingContractError(
            f"vector must be L2 normalized; observed norm={norm:.9f}"
        )
    return struct.pack(f"<{dimension}f", *floats)


def _decode_vector(blob: bytes, dimension: int) -> tuple[float, ...]:
    expected = dimension * 4
    if len(blob) != expected:
        raise GraphSkillEmbeddingContractError(
            f"stored vector byte length mismatch: expected {expected}, observed {len(blob)}"
        )
    return struct.unpack(f"<{dimension}f", blob)


def _open_read_only(path: Path) -> sqlite3.Connection:
    uri = f"file:{path.resolve().as_posix()}?mode=ro&immutable=1"
    return sqlite3.connect(uri, uri=True)


def build_embedding_projection(
    output_path: Path | str,
    corpus: Mapping[str, Any],
    vectors_by_assertion: Mapping[str, Sequence[float]],
    model_manifest: Mapping[str, Any],
) -> dict[str, Any]:
    """Stage and atomically publish a deterministic immutable SQLite generation."""
    path = Path(output_path)
    if path.exists():
        raise GraphSkillEmbeddingContractError(f"immutable projection already exists: {path}")
    dimension = int(model_manifest.get("dimension") or 0)
    if dimension <= 0:
        raise GraphSkillEmbeddingContractError("model dimension must be positive")

    assertions = {
        str(row.get("assertion_id") or ""): row
        for row in corpus.get("assertions") or []
        if isinstance(row, dict)
    }
    expected_ids = set(assertions)
    observed_ids = {str(value) for value in vectors_by_assertion}
    if expected_ids != observed_ids:
        raise GraphSkillEmbeddingContractError(
            "assertion/vector parity mismatch: "
            f"missing={sorted(expected_ids - observed_ids)}, "
            f"orphaned={sorted(observed_ids - expected_ids)}"
        )

    encoded: dict[str, bytes] = {}
    vector_bindings: list[dict[str, str]] = []
    for assertion_id in sorted(expected_ids):
        blob = _vector_bytes(vectors_by_assertion[assertion_id], dimension)
        encoded[assertion_id] = blob
        vector_bindings.append(
            {
                "assertion_id": assertion_id,
                "assertion_document_sha256": str(
                    assertions[assertion_id].get("assertion_document_sha256") or ""
                ),
                "vector_sha256": hashlib.sha256(blob).hexdigest(),
            }
        )

    generation_payload = {
        "schema_version": PROJECTION_SCHEMA_VERSION,
        "corpus_sha256": str(corpus.get("corpus_sha256") or ""),
        "model": dict(model_manifest),
        "vectors": vector_bindings,
    }
    generation_sha256 = canonical_sha256(generation_payload)
    metadata = {
        "schema_version": PROJECTION_SCHEMA_VERSION,
        "generation_sha256": generation_sha256,
        "corpus_sha256": generation_payload["corpus_sha256"],
        "graph_sha256": str((corpus.get("source_digests") or {}).get("graph_sha256") or ""),
        "model_id": str(model_manifest.get("model_id") or ""),
        "model_revision": str(model_manifest.get("revision") or ""),
        "model_artifact_sha256": str(model_manifest.get("artifact_sha256") or ""),
        "dimension": str(dimension),
        "normalization": str(model_manifest.get("normalization") or ""),
        "vector_count": str(len(encoded)),
    }
    if any(not value for key, value in metadata.items() if key != "vector_count"):
        raise GraphSkillEmbeddingContractError("projection metadata is incomplete")

    path.parent.mkdir(parents=True, exist_ok=True)
    staging = path.with_name(f".{path.name}.staging-{os.getpid()}")
    if staging.exists():
        staging.unlink()
    try:
        conn = sqlite3.connect(staging)
        try:
            conn.execute("PRAGMA page_size=4096")
            conn.execute("PRAGMA journal_mode=OFF")
            conn.execute("PRAGMA synchronous=OFF")
            conn.execute("PRAGMA locking_mode=EXCLUSIVE")
            conn.execute("PRAGMA auto_vacuum=NONE")
            conn.execute("PRAGMA application_id=1095911250")
            conn.execute("PRAGMA user_version=1")
            conn.execute(
                "CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL) WITHOUT ROWID"
            )
            conn.execute(
                "CREATE TABLE assertion_vectors ("
                "assertion_id TEXT PRIMARY KEY, "
                "skill_id TEXT NOT NULL, "
                "assertion_document_sha256 TEXT NOT NULL, "
                "authority_envelope_sha256 TEXT NOT NULL, "
                "allowed_sections_json TEXT NOT NULL, "
                "vector_sha256 TEXT NOT NULL, "
                "vector BLOB NOT NULL"
                ") WITHOUT ROWID"
            )
            conn.executemany(
                "INSERT INTO metadata(key, value) VALUES (?, ?)",
                sorted(metadata.items()),
            )
            for assertion_id in sorted(assertions):
                assertion = assertions[assertion_id]
                blob = encoded[assertion_id]
                conn.execute(
                    "INSERT INTO assertion_vectors VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        assertion_id,
                        str(assertion.get("skill_id") or ""),
                        str(assertion.get("assertion_document_sha256") or ""),
                        str(assertion.get("authority_envelope_sha256") or ""),
                        _canonical_json(sorted(assertion.get("allowed_sections") or [])),
                        hashlib.sha256(blob).hexdigest(),
                        blob,
                    ),
                )
            conn.commit()
            conn.execute("VACUUM")
            conn.commit()
        finally:
            conn.close()
        os.replace(staging, path)
    except BaseException:
        if staging.exists():
            staging.unlink()
        raise

    sqlite_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
    return {
        "schema_version": PROJECTION_SCHEMA_VERSION,
        "generation_sha256": generation_sha256,
        "sqlite_sha256": sqlite_sha256,
        "vector_count": len(encoded),
        "dimension": dimension,
    }


def validate_embedding_projection(
    path: Path | str,
    *,
    corpus: Mapping[str, Any],
) -> list[str]:
    issues: list[str] = []
    db_path = Path(path)
    if not db_path.is_file():
        return ["PROJECTION_MISSING"]
    expected = {
        str(row.get("assertion_id") or ""): row
        for row in corpus.get("assertions") or []
        if isinstance(row, dict)
    }
    try:
        with _open_read_only(db_path) as conn:
            metadata = dict(conn.execute("SELECT key, value FROM metadata ORDER BY key"))
            rows = conn.execute(
                "SELECT assertion_id, assertion_document_sha256, vector_sha256, vector "
                "FROM assertion_vectors ORDER BY assertion_id"
            ).fetchall()
    except sqlite3.Error as exc:
        return [f"PROJECTION_SQLITE_ERROR:{type(exc).__name__}"]
    if metadata.get("corpus_sha256") != str(corpus.get("corpus_sha256") or ""):
        issues.append("CORPUS_DIGEST_MISMATCH")
    dimension = int(metadata.get("dimension") or 0)
    observed_ids = {str(row[0]) for row in rows}
    if observed_ids != set(expected):
        issues.append("ASSERTION_VECTOR_PARITY_MISMATCH")
    if int(metadata.get("vector_count") or -1) != len(rows):
        issues.append("VECTOR_COUNT_MISMATCH")
    for assertion_id, document_digest, vector_digest, blob in rows:
        assertion = expected.get(str(assertion_id))
        if assertion is None:
            continue
        if document_digest != assertion.get("assertion_document_sha256"):
            issues.append(f"ASSERTION_DOCUMENT_DIGEST_MISMATCH:{assertion_id}")
        if hashlib.sha256(blob).hexdigest() != vector_digest:
            issues.append(f"VECTOR_DIGEST_MISMATCH:{assertion_id}")
        try:
            _vector_bytes(_decode_vector(blob, dimension), dimension)
        except GraphSkillEmbeddingContractError:
            issues.append(f"VECTOR_CONTRACT_MISMATCH:{assertion_id}")
    return issues


class GraphSkillEmbeddingIndex:
    """Read-only exact normalized-dot-product assertion candidate index."""

    def __init__(
        self,
        path: Path | str,
        *,
        expected_corpus_sha256: str,
        expected_model_artifact_sha256: str | None = None,
    ) -> None:
        self.path = Path(path)
        self._conn = _open_read_only(self.path)
        self.metadata = dict(self._conn.execute("SELECT key, value FROM metadata ORDER BY key"))
        if self.metadata.get("corpus_sha256") != expected_corpus_sha256:
            self.close()
            raise GraphSkillEmbeddingContractError("corpus digest mismatch")
        if (
            expected_model_artifact_sha256 is not None
            and self.metadata.get("model_artifact_sha256") != expected_model_artifact_sha256
        ):
            self.close()
            raise GraphSkillEmbeddingContractError("model artifact digest mismatch")
        self.dimension = int(self.metadata["dimension"])

    def __enter__(self) -> GraphSkillEmbeddingIndex:
        return self

    def __exit__(self, *_args: Any) -> None:
        self.close()

    def close(self) -> None:
        conn = getattr(self, "_conn", None)
        if conn is not None:
            conn.close()
            self._conn = None

    def query(
        self,
        query_vector: Sequence[float],
        *,
        k: int,
        section_id: str | None = None,
    ) -> list[dict[str, Any]]:
        if self._conn is None:
            raise GraphSkillEmbeddingContractError("embedding index is closed")
        if k <= 0:
            return []
        query_blob = _vector_bytes(query_vector, self.dimension)
        query = _decode_vector(query_blob, self.dimension)
        rows = self._conn.execute(
            "SELECT assertion_id, allowed_sections_json, vector "
            "FROM assertion_vectors ORDER BY assertion_id"
        ).fetchall()
        ranked: list[tuple[float, str]] = []
        for assertion_id, allowed_json, blob in rows:
            allowed = json.loads(allowed_json)
            if section_id and section_id not in allowed:
                continue
            vector = _decode_vector(blob, self.dimension)
            score = math.fsum(left * right for left, right in zip(query, vector, strict=True))
            ranked.append((score, str(assertion_id)))
        ranked.sort(key=lambda item: (-item[0], item[1]))
        return [
            {"assertion_id": assertion_id, "similarity": score}
            for score, assertion_id in ranked[:k]
        ]


def rehydrate_assertion_candidates(
    candidates: Sequence[Mapping[str, Any]],
    *,
    corpus: Mapping[str, Any],
    graph_payload: Mapping[str, Any],
    section_id: str,
) -> list[dict[str, Any]]:
    """Resolve candidate IDs through exact current graph and assertion authority."""
    if (corpus.get("source_digests") or {}).get("graph_sha256") != canonical_sha256(
        graph_payload
    ):
        raise GraphSkillEmbeddingContractError("stale graph digest")
    assertions = {
        str(row.get("assertion_id") or ""): row
        for row in corpus.get("assertions") or []
        if isinstance(row, dict)
    }
    graph_rows = {
        str(row.get("skill_id") or ""): row
        for row in graph_payload.get("skill_rows") or []
        if isinstance(row, dict)
    }
    hydrated: list[dict[str, Any]] = []
    for candidate in candidates:
        if set(candidate) != {"assertion_id", "similarity"}:
            raise GraphSkillEmbeddingContractError("candidate payload exposes forbidden fields")
        assertion_id = str(candidate.get("assertion_id") or "")
        assertion = assertions.get(assertion_id)
        graph_row = graph_rows.get(assertion_id)
        if assertion is None or graph_row is None:
            raise GraphSkillEmbeddingContractError(f"orphan assertion candidate: {assertion_id}")
        if graph_row.get("retrieval_eligible") is not True:
            raise GraphSkillEmbeddingContractError(f"unauthorized assertion: {assertion_id}")
        if assertion.get("skill_row_sha256") != canonical_sha256(graph_row):
            raise GraphSkillEmbeddingContractError(f"stale skill row: {assertion_id}")
        if section_id not in assertion.get("allowed_sections", []):
            raise GraphSkillEmbeddingContractError(
                f"assertion not allowed in section {section_id}: {assertion_id}"
            )
        if sorted(assertion.get("fact_links") or []) != sorted(graph_row.get("fact_id_links") or []):
            raise GraphSkillEmbeddingContractError(f"fact binding drift: {assertion_id}")
        row = dict(assertion)
        row["similarity"] = float(candidate["similarity"])
        hydrated.append(row)
    return hydrated


__all__ = [
    "GraphSkillEmbeddingContractError",
    "GraphSkillEmbeddingIndex",
    "PROJECTION_SCHEMA_VERSION",
    "build_embedding_projection",
    "rehydrate_assertion_candidates",
    "validate_embedding_projection",
]
