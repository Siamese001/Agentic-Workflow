"""ChunkMetadataV1 — unified metadata contract for ChromaDB chunks.

Every ingestion script (``tools/ingestion/ingest_*.py``) MUST stamp this
contract on every chunk added to ChromaDB. Every retrieval consumer MAY
rely on these fields being present and well-typed.

Background
==========
Prior to W2 of the ChromaDB/BGE retrieval-hardening plan, each ingestion
script shipped its own bespoke metadata schema (see plan §2.5 schema drift).
This prevented cross-collection filtering (for example: "show me every chunk
whose embedding_model != BAAI/bge-m3"), defeated provenance auditing, and
made re-ingest non-idempotent because no stable ``canonical_digest`` existed.

This module defines:
    * ``REQUIRED_FIELDS`` — must appear on every chunk, well-typed.
    * ``OPTIONAL_FIELDS`` — kind-specific, validated only when present.
    * ``build_canonical_digest`` — deterministic chunk-ID seed for upsert.
    * ``now_utc_iso`` — ISO 8601 UTC timestamp used for ``ingested_at``.
    * ``compute_source_sha`` — short content hash of the source file bytes.
    * ``validate(meta)`` — returns a list of human-readable error strings.

ChromaDB metadata values must be JSON-scalar-like (str/int/float/bool/None);
lists and dicts are rejected by ChromaDB itself. Keep new optional fields
scalar-typed or join-as-string.

Plan: ``docs/archive/windsurf/legacy-tree/plans/chromadb-bge-retrieval-hardening-e9aa09.md`` (W2.1).
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

from agentic_core.config.model_catalog import BGE_M3_MODEL_ID

# Stable contract version string. Bump when a new REQUIRED field is added.
CHUNK_METADATA_VERSION = "v1"

# Canonical artifact_type values — one per logical collection family.
# Keep lowercase snake_case so they can be used as ChromaDB `where={"artifact_type": ...}`
# filter values without quoting gotchas.
ARTIFACT_TYPES: frozenset[str] = frozenset(
    {
        "code_chunk",
        "doc_chunk",
        "test_chunk",
        "trace_chunk",
        "adg_chunk",
        "runtime_evidence",
        "incident_rca",
        "symbol",
        "arch_doc",
        "process_doc",
        "ext_knowledge",
    }
)

# Canonical layer tokens. "L_UNKNOWN" is permitted only as an explicit
# fallback; ingest code should prefer a real classification whenever the
# layer can be inferred from the source path (see `infer_layer`).
LAYER_TOKENS: frozenset[str] = frozenset(
    {
        "L0",
        "L1",
        "L2",
        "L3",
        "L4",
        "L5",
        "L6",
        "L_APPS",
        "L_TOOLS",
        "L_OPS",
        "L_SHARED",
        "L_SYSTEM_LEARNING",
        "L_INFRASTRUCTURE",
        "L_CONFIG",
        "L_DOCS",
        "L_TESTS",
        "L_UNKNOWN",
    }
)

# REQUIRED fields: every chunk, every collection, no exceptions.
REQUIRED_FIELDS: dict[str, type] = {
    "artifact_type": str,
    "source_path": str,
    "source_sha": str,
    "canonical_digest": str,
    "layer": str,
    "embedding_model": str,
    "embedding_dim": int,
    "ingested_at": str,
    "metadata_version": str,
}

# OPTIONAL fields: validated by type only when present. A chunk MAY omit
# any of these; a chunk MUST NOT include a key outside (REQUIRED ∪ OPTIONAL).
OPTIONAL_FIELDS: dict[str, type | tuple[type, ...]] = {
    # Code chunks
    "entity_type": str,
    "name": str,
    "line_start": int,
    "line_end": int,
    # args/methods accept list at ingest time — ``SovereignChromaClient``
    # JSON-encodes them into strings before the ChromaDB ``add`` call.
    "args": (list, str),
    "docstring": str,
    "methods": (list, str),
    "adg_node_id": (int, str, type(None)),
    "parent_id": str,
    "module": str,
    "chunk_context": str,
    # Doc chunks
    "doc_id": str,
    "doc_type": str,
    "category": str,
    "section": str,
    "subsection": str,
    "chunk_type": str,
    "created_date": str,
    # Trace / runtime / incident
    "trace_type": str,
    "trace_id": str,
    "incident_id": str,
    "rca_status": str,
    "evidence_type": str,
    # Symbols / ADG
    "symbol_name": str,
    "domain": str,
    # Legacy aliases — preserved during migration so pre-W2 retrieval
    # consumers that read metadata["file_path"] or metadata["type"] keep
    # working. New consumers MUST prefer source_path / artifact_type.
    "file_path": str,
    "type": str,
}


def now_utc_iso() -> str:
    """Return an ISO-8601 UTC timestamp suitable for ``ingested_at``."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def compute_source_sha(source: Path | str | bytes) -> str:
    """Return a short sha256 digest (16 hex chars) of the source content.

    Accepts a file path (str or Path), in which case the file is read as
    bytes; or raw ``bytes`` already in hand.
    """
    if isinstance(source, (str, Path)):
        data = Path(source).read_bytes()
    else:
        data = source
    return hashlib.sha256(data).hexdigest()[:16]


def build_canonical_digest(
    *,
    artifact_type: str,
    source_path: str,
    anchor: str,
) -> str:
    """Return a stable 16-hex digest identifying a chunk.

    ``anchor`` is the kind-specific identifier within the source — for code
    it is ``"<entity_type>:<name>:<line_start>"``; for docs it is
    ``"<section>/<subsection>:<chunk_index>"``; for traces it is the
    trace_id or event anchor. The important property is determinism:
    re-ingesting the same source at the same revision MUST produce the
    same digest so ChromaDB ``add`` upserts cleanly instead of duplicating.
    """
    payload = f"{artifact_type}\x1f{source_path}\x1f{anchor}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def infer_layer(source_path: str) -> str:
    """Best-effort layer classification from a repo-relative path.

    Returns one of :data:`LAYER_TOKENS`. Callers may override the result
    when they have stronger information (ADG node layer, explicit config).
    """
    p = source_path.replace("\\", "/").lower()
    if p.startswith("agentic_core/l0_routing/"):
        return "L0"
    if p.startswith("agentic_core/l1_cognition/"):
        return "L1"
    if p.startswith("agentic_core/l2_execution/"):
        return "L2"
    if p.startswith("agentic_core/l3_orchestration/"):
        return "L3"
    if p.startswith("agentic_core/l4_state/"):
        return "L4"
    if p.startswith("agentic_core/l5_safety/"):
        return "L5"
    if p.startswith("agentic_core/l6_observability/"):
        return "L6"
    # Non-layered agentic_core infra (embeddings, adg helpers, bridges, etc.)
    # is closest to L4 state — callers can override when ADG has a stronger
    # classification.
    if p.startswith("agentic_core/"):
        return "L4"
    if p.startswith("apps_"):
        return "L_APPS"
    if p.startswith("tools/"):
        return "L_TOOLS"
    if p.startswith("ops_scripts/"):
        return "L_OPS"
    if p.startswith("apps_shared/"):
        return "L_SHARED"
    if p.startswith("system_learning/"):
        return "L_SYSTEM_LEARNING"
    if p.startswith("infrastructure/"):
        return "L_INFRASTRUCTURE"
    if p.startswith("config/"):
        return "L_CONFIG"
    if p.startswith("docs/"):
        return "L_DOCS"
    if p.startswith("tests/") or "/tests/" in p:
        return "L_TESTS"
    return "L_UNKNOWN"


def validate(meta: dict) -> list[str]:
    """Validate a metadata dict against the contract.

    Returns a list of human-readable error strings; an empty list means
    the dict is compliant. The function never raises so callers can batch
    many chunks and surface the full error set in one shot.
    """
    errors: list[str] = []

    # Required keys + types
    for key, expected_type in REQUIRED_FIELDS.items():
        if key not in meta:
            errors.append(f"missing required field: {key!r}")
            continue
        value = meta[key]
        if not isinstance(value, expected_type):
            errors.append(f"field {key!r} has type {type(value).__name__}, expected {expected_type.__name__}")

    # Version
    if meta.get("metadata_version") not in (None, CHUNK_METADATA_VERSION):
        errors.append(f"metadata_version {meta.get('metadata_version')!r} != {CHUNK_METADATA_VERSION!r}")

    # Known artifact_type
    artifact_type = meta.get("artifact_type")
    if isinstance(artifact_type, str) and artifact_type not in ARTIFACT_TYPES:
        errors.append(
            f"artifact_type {artifact_type!r} not in canonical set "
            f"(expected one of: {sorted(ARTIFACT_TYPES)})"
        )

    # Known layer
    layer = meta.get("layer")
    if isinstance(layer, str) and layer not in LAYER_TOKENS:
        errors.append(f"layer {layer!r} not in canonical set (expected one of: {sorted(LAYER_TOKENS)})")

    # Optional-field type check + unknown-key rejection
    allowed = set(REQUIRED_FIELDS) | set(OPTIONAL_FIELDS)
    for key, value in meta.items():
        if key not in allowed:
            errors.append(f"unknown metadata key: {key!r}")
            continue
        if key in OPTIONAL_FIELDS:
            expected = OPTIONAL_FIELDS[key]
            if not isinstance(value, expected):  # type: ignore[arg-type]
                expected_name = (
                    expected.__name__
                    if isinstance(expected, type)
                    else "/".join(t.__name__ for t in expected)
                )
                errors.append(
                    f"optional field {key!r} has type {type(value).__name__}, expected {expected_name}"
                )

    return errors


def build_required(
    *,
    artifact_type: str,
    source_path: str,
    source_sha: str,
    canonical_digest: str,
    layer: str,
    embedding_model: str,
    embedding_dim: int,
    ingested_at: str | None = None,
) -> dict:
    """Return a dict containing exactly the REQUIRED fields, well-typed.

    Callers add optional fields afterwards by ``dict.update`` or
    ``| {"entity_type": ...}``; ``validate`` will then confirm the final
    shape before the chunk hits ChromaDB.
    """
    return {
        "artifact_type": artifact_type,
        "source_path": source_path,
        "source_sha": source_sha,
        "canonical_digest": canonical_digest,
        "layer": layer,
        "embedding_model": embedding_model,
        "embedding_dim": embedding_dim,
        "ingested_at": ingested_at or now_utc_iso(),
        "metadata_version": CHUNK_METADATA_VERSION,
    }


def coerce_to_v1(
    meta: dict,
    *,
    artifact_type: str,
    source_path: str | None = None,
    anchor: str,
    source_bytes: bytes | None = None,
    embedding_model: str = BGE_M3_MODEL_ID,
    embedding_dim: int = 1024,
) -> dict:
    """Mutate a legacy metadata dict in place so it satisfies the V1 contract.

    Intended for W2.2b legacy-ingester retrofits: callers pass the dict they
    were already building plus the canonical ``artifact_type`` and a stable
    per-chunk ``anchor`` (used for canonical_digest). Missing required
    fields are filled with sensible defaults; existing non-contract keys
    are preserved unless they collide with a REQUIRED key.

    The function returns the same dict instance for chaining. It does NOT
    call :func:`validate` — callers should call it separately when they
    want to surface drift warnings.
    """
    if source_path is None:
        source_path = str(meta.get("source_path") or meta.get("file_path") or meta.get("doc_id") or "unknown")
    source_path = source_path.replace("\\", "/")

    if "source_sha" not in meta:
        if source_bytes is not None:
            meta["source_sha"] = compute_source_sha(source_bytes)
        else:
            # Use a stable hash of source_path + anchor when no bytes are
            # available — it at least pins the identity of the chunk.
            meta["source_sha"] = compute_source_sha(f"{source_path}:{anchor}".encode("utf-8"))

    meta.setdefault("artifact_type", artifact_type)
    meta.setdefault("source_path", source_path)
    meta.setdefault(
        "canonical_digest",
        build_canonical_digest(
            artifact_type=artifact_type,
            source_path=source_path,
            anchor=anchor,
        ),
    )
    # Layer: accept what the caller already stamped if it's canonical,
    # otherwise re-infer.
    layer = meta.get("layer")
    if not isinstance(layer, str) or layer not in LAYER_TOKENS:
        meta["layer"] = infer_layer(source_path)
    meta.setdefault("embedding_model", embedding_model)
    meta.setdefault("embedding_dim", embedding_dim)
    meta.setdefault("ingested_at", now_utc_iso())
    meta["metadata_version"] = CHUNK_METADATA_VERSION

    # Legacy alias: keep file_path mirroring source_path.
    meta.setdefault("file_path", source_path)
    return meta


__all__ = [
    "CHUNK_METADATA_VERSION",
    "ARTIFACT_TYPES",
    "LAYER_TOKENS",
    "REQUIRED_FIELDS",
    "OPTIONAL_FIELDS",
    "now_utc_iso",
    "compute_source_sha",
    "build_canonical_digest",
    "infer_layer",
    "validate",
    "build_required",
    "coerce_to_v1",
]
