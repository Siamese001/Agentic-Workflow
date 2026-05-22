"""W6C — governed Chroma read-surface projection after UWG-admitted R1B commit (apps_rg only).

Upserts only into an apps_rg-owned Chroma collection under the run or R1B cache root.
Core D2 ``l2_semantic_cache`` / ``promote_to_long_term`` paths are never used here.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from apps_rg.cache.r1b_constants import R1B_STORAGE_SUBSYSTEM, R1B_UWG_TARGET_SURFACE
from apps_rg.cache.r1b_bge_embedding import chunk_vector_payload, intent_vector_payload
from apps_rg.cache.r1b_intent_vector import intent_text_from_request, normalized_intent_digest
from apps_rg.cache.r1b_models import HistoricalIntentRecord, HistoricalOutputChunk

READ_SURFACE_NAME = "r1b_semantic_cache_projection"
CHROMA_COLLECTION_NAME = "apps_rg_r1b_semantic_cache_projection"
SCHEMA_READ_SURFACE_REFRESH = "read_surface_refresh_receipt_v1"
SCHEMA_CHROMA_COLLECTION_INDEX = "chroma_collection_index_ref_v1"
SCHEMA_CHROMA_READ_AFTER_WRITE = "chroma_read_after_write_receipt_v1"
SCHEMA_EMBEDDING_MAPPING = "request_intent_embedding_ref_mapping_receipt_v1"
PRODUCER_MODULE = "apps_rg.cache.r1b_chroma_read_surface_projection"

READ_SURFACE_REFRESH_ARTIFACT = "read_surface_refresh_receipt.json"
CHROMA_COLLECTION_INDEX_ARTIFACT = "chroma_collection_index_ref.json"
CHROMA_READ_AFTER_WRITE_ARTIFACT = "chroma_read_after_write_receipt.json"
REQUEST_INTENT_EMBEDDING_REF_ARTIFACT = "request_intent_embedding_ref.json"
EMBEDDING_MAPPING_RECEIPT_ARTIFACT = "request_intent_embedding_ref_mapping_receipt.json"
COMPATIBILITY_PROOF_ARTIFACT = "r1b_compatibility_proof.json"
UWG_ADMITTED_BUNDLE_ARTIFACT = "r1b_uwg_admitted_projection_bundle.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_file(path: Path) -> str:
    if not path.is_file():
        return ""
    h = hashlib.sha256()
    try:
        h.update(path.read_bytes())
    except OSError:
        return ""
    return h.hexdigest()


def _chroma_projection_enabled() -> bool:
    return os.environ.get("APPS_RG_R1B_SKIP_CHROMA_PROJECTION", "").strip().lower() not in (
        "1",
        "true",
        "yes",
    )


def _resolve_chroma_persist_dir(artifact_dir: Path) -> Path:
    env = os.environ.get("APPS_RG_R1B_CHROMA_READ_SURFACE_ROOT", "").strip()
    if env:
        root = Path(env)
        if not root.is_absolute():
            root = (Path.cwd() / root).resolve()
        return root
    chroma = os.environ.get("CHROMA_PERSIST_DIR", "").strip()
    if chroma:
        return Path(chroma) / "r1b_semantic_cache_projection"
    return artifact_dir / "r1b_chroma_read_surface"


@dataclass
class GovernedChromaProjectionOutcome:
    refresh_status: str
    read_surface_refresh_status: str
    chroma_projection_status: str
    read_surface_refresh_complete: bool = False
    chroma_projection_complete: bool = False
    reason: str = ""
    artifacts_written: list[str] = field(default_factory=list)
    collection_name: str = CHROMA_COLLECTION_NAME
    chroma_persist_path: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "refresh_status": self.refresh_status,
            "read_surface_refresh_status": self.read_surface_refresh_status,
            "chroma_projection_status": self.chroma_projection_status,
            "read_surface_refresh_complete": self.read_surface_refresh_complete,
            "chroma_projection_complete": self.chroma_projection_complete,
            "reason": self.reason,
            "artifacts_written": list(self.artifacts_written),
            "collection_name": self.collection_name,
            "chroma_persist_path": self.chroma_persist_path,
            "read_surface": READ_SURFACE_NAME,
            "governed_uwg_admitted_projection": True,
            "explicit_non_claims": [
                "not core D2 l2_semantic_cache shadow promote",
                "Chroma upsert on this path counts only with full UWG receipt chain",
            ],
        }


def _write_envelope(
    path: Path,
    payload: Mapping[str, Any],
    *,
    artifact_name: str,
    section_id: str,
    run_id: str,
) -> None:
    doc = {
        "schema_version": "apps_rg_r1b_governed_receipt_envelope_v1",
        "generated_at_utc": _utc_now(),
        "producer": PRODUCER_MODULE,
        "artifact_name": artifact_name,
        "section_id": section_id,
        "run_id": run_id,
        "payload": dict(payload),
    }
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _chain_artifact_refs(artifact_dir: Path) -> dict[str, str]:
    refs: dict[str, str] = {}
    for name in (
        "commit_request.json",
        "state_diff_validation_result.json",
        "uwg_commit_receipt.json",
        "l4_namespace_object_ref.json",
        "proposed_state_diff_ref.json",
    ):
        if (artifact_dir / name).is_file():
            refs[name.replace(".json", "_ref")] = name
    return refs


def _assert_bge_vector_for_chroma_upsert(payload: Mapping[str, Any], *, context: str) -> None:
    """Block 32-dim pseudo_digest upserts into BGE-governed Chroma collections on product paths."""
    from apps_rg.runtime.product_output_policy import require_live_bge_embeddings

    if not require_live_bge_embeddings():
        return
    dims = int(payload.get("dimensions") or len(payload.get("values") or []))
    model = str(payload.get("embedding_model") or payload.get("query_vector_source") or "")
    if dims != 1024 or "pseudo_digest" in model:
        raise RuntimeError(
            f"R1B Chroma upsert forbidden ({context}): dimensions={dims} embedding_model={model!r}; "
            "require BAAI/bge-m3 (1024d) on product path"
        )


def _refresh_digest(artifact_dir: Path, record_id: str, commit_request_id: str) -> str:
    parts = [
        record_id,
        commit_request_id,
        _sha256_file(artifact_dir / "commit_request.json"),
        _sha256_file(artifact_dir / "uwg_commit_receipt.json"),
        _sha256_file(artifact_dir / "l4_namespace_object_ref.json"),
    ]
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


def _upsert_governed_chroma(
    *,
    persist_dir: Path,
    record: HistoricalIntentRecord,
    chunks: list[HistoricalOutputChunk],
    raw_request: dict[str, Any],
    commit_request_id: str,
    uwg_commit_receipt_id: str,
) -> dict[str, Any]:
    from agentic_core.L4_state.utils.client.chroma_client import chromadb_module as chromadb

    persist_dir.mkdir(parents=True, exist_ok=True)
    from apps_rg.runtime.chroma_precomputed_collection import (
        get_precomputed_embeddings_collection,
    )
    from apps_rg.runtime.embedding_settings import apply_apps_rg_embedding_env_guards

    apply_apps_rg_embedding_env_guards(chroma_persist_dir=str(persist_dir))
    client = chromadb.PersistentClient(path=str(persist_dir))
    collection = get_precomputed_embeddings_collection(
        client,
        CHROMA_COLLECTION_NAME,
        metadata={
            "subsystem": R1B_STORAGE_SUBSYSTEM,
            "read_surface": READ_SURFACE_NAME,
            "governed_projection": "true",
            "not_core_d2_l2_semantic_cache": "true",
            "embedding_model": "BAAI/bge-m3",
            "chroma_default_ef_forbidden": "true",
        },
    )
    digest = record.normalized_intent_digest or normalized_intent_digest(
        intent_text_from_request(raw_request)
    )
    intent_text = record.request_intent_text or intent_text_from_request(raw_request)
    intent_payload = intent_vector_payload(intent_text=intent_text, digest=digest)
    embedding = [float(x) for x in intent_payload["values"]]
    _assert_bge_vector_for_chroma_upsert(intent_payload, context="r1b_intent_parent")
    ids = [record.record_id]
    embeddings = [embedding]
    documents = [intent_text]
    metadatas = [
        {
            "record_id": record.record_id,
            "chunk_role": "parent_intent",
            "normalized_intent_digest": digest,
            "commit_request_id": commit_request_id,
            "uwg_commit_receipt_id": uwg_commit_receipt_id,
            "cache_grain": record.cache_grain,
            "source_run_id": record.source_run_id,
            "governed_read_surface": READ_SURFACE_NAME,
            "embedding_model": str(intent_payload.get("embedding_model") or ""),
            "target_l4_namespace": R1B_UWG_TARGET_SURFACE,
        }
    ]
    for ch in chunks:
        chunk_text = (ch.chunk_text or ch.chunk_type or ch.chunk_id).strip()
        if not chunk_text:
            continue
        cp = chunk_vector_payload(chunk_text=chunk_text, chunk_id=ch.chunk_id)
        _assert_bge_vector_for_chroma_upsert(cp, context=f"r1b_chunk:{ch.chunk_id}")
        cid = f"{record.record_id}:{ch.chunk_id}"
        ids.append(cid)
        embeddings.append([float(x) for x in cp["values"]])
        documents.append(chunk_text[:8000])
        metadatas.append(
            {
                "record_id": record.record_id,
                "chunk_id": ch.chunk_id,
                "chunk_role": "output_chunk",
                "chunk_type": ch.chunk_type,
                "section_id": ch.section_id,
                "parent_intent_record_id": ch.parent_intent_record_id,
                "commit_request_id": commit_request_id,
                "uwg_commit_receipt_id": uwg_commit_receipt_id,
                "governed_read_surface": READ_SURFACE_NAME,
                "embedding_model": str(cp.get("embedding_model") or ""),
            }
        )
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )
    result = collection.query(
        query_embeddings=[embedding],
        n_results=min(3, len(ids)),
        include=["metadatas", "distances"],
    )
    hit_ids = (result.get("ids") or [[]])[0]
    return {
        "collection_name": CHROMA_COLLECTION_NAME,
        "chroma_persist_path": str(persist_dir),
        "upserted_parent_id": record.record_id,
        "upserted_chunk_count": max(0, len(ids) - 1),
        "query_ids": list(hit_ids),
        "read_after_write_ok": record.record_id in hit_ids,
        "embedding_model": intent_payload.get("embedding_model"),
        "embedding_dimensions": intent_payload.get("dimensions"),
    }


def project_governed_chroma_read_surface(
    *,
    artifact_dir: Path,
    section_id: str,
    run_id: str,
    record: HistoricalIntentRecord,
    chunks: list[HistoricalOutputChunk],
    commit_request_id: str,
    uwg_commit_receipt_id: str,
    raw_request: dict[str, Any] | None = None,
) -> GovernedChromaProjectionOutcome:
    """Emit canonical read-surface + Chroma index refs after UWG admission."""
    req = dict(raw_request or {})
    l4_path = artifact_dir / "l4_namespace_object_ref.json"
    if not l4_path.is_file():
        return GovernedChromaProjectionOutcome(
            refresh_status="SKIPPED",
            read_surface_refresh_status="MISSING",
            chroma_projection_status="MISSING",
            reason="missing_l4_namespace_object_ref",
        )
    if not (artifact_dir / "commit_request.json").is_file():
        return GovernedChromaProjectionOutcome(
            refresh_status="SKIPPED",
            read_surface_refresh_status="MISSING",
            chroma_projection_status="MISSING",
            reason="missing_commit_request",
        )

    bundle = {
        "schema_version": "r1b_uwg_admitted_projection_bundle_v1",
        "storage_subsystem": R1B_STORAGE_SUBSYSTEM,
        "read_surface": READ_SURFACE_NAME,
        "parent_intent_record": record.to_dict(),
        "child_chunks": [c.to_dict() for c in chunks],
        "commit_request_id": commit_request_id,
        "uwg_commit_receipt_id": uwg_commit_receipt_id,
        "target_l4_namespace": R1B_UWG_TARGET_SURFACE,
    }
    (artifact_dir / UWG_ADMITTED_BUNDLE_ARTIFACT).write_text(
        json.dumps(bundle, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    written: list[str] = [UWG_ADMITTED_BUNDLE_ARTIFACT]

    intent_text = record.request_intent_text or intent_text_from_request(req)
    digest = record.normalized_intent_digest or normalized_intent_digest(intent_text)
    intent_payload = intent_vector_payload(intent_text=intent_text, digest=digest)
    _write_envelope(
        artifact_dir / REQUEST_INTENT_EMBEDDING_REF_ARTIFACT,
        {
            "record_id": record.record_id,
            "request_intent_embedding_ref": f"embeddings/{record.record_id}.json",
            "embedding": intent_payload,
            "not_c0_fact_vectors": True,
        },
        artifact_name=REQUEST_INTENT_EMBEDDING_REF_ARTIFACT,
        section_id=section_id,
        run_id=run_id,
    )
    written.append(REQUEST_INTENT_EMBEDDING_REF_ARTIFACT)

    _write_envelope(
        artifact_dir / EMBEDDING_MAPPING_RECEIPT_ARTIFACT,
        {
            "source_field": "request_intent_vector_ref",
            "canonical_field": "request_intent_embedding_ref",
            "source_ref": record.request_intent_vector_ref,
            "canonical_ref": f"embeddings/{record.record_id}.json",
            "mapping_policy": "bge_m3_explicit_only_on_product",
            "query_vector_source": str(
                intent_payload.get("query_vector_source")
                or intent_payload.get("embedding_model")
                or "unknown"
            ),
            "record_id": record.record_id,
        },
        artifact_name=EMBEDDING_MAPPING_RECEIPT_ARTIFACT,
        section_id=section_id,
        run_id=run_id,
    )
    written.append(EMBEDDING_MAPPING_RECEIPT_ARTIFACT)

    from apps_rg.cache.r1b_compatibility import assess_intent_record_admissibility

    compat = assess_intent_record_admissibility(record, chunks=chunks)
    (artifact_dir / COMPATIBILITY_PROOF_ARTIFACT).write_text(
        json.dumps(
            {
                "schema_version": "r1b_compatibility_proof_v1",
                "admissible": compat.admissible,
                "reason": compat.reason,
                "checks": compat.checks,
                "record_id": record.record_id,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    written.append(COMPATIBILITY_PROOF_ARTIFACT)

    refresh_digest = _refresh_digest(artifact_dir, record.record_id, commit_request_id)
    refreshed_at = _utc_now()
    chain_refs = _chain_artifact_refs(artifact_dir)

    chroma_meta: dict[str, Any] = {}
    if _chroma_projection_enabled():
        try:
            chroma_meta = _upsert_governed_chroma(
                persist_dir=_resolve_chroma_persist_dir(artifact_dir),
                record=record,
                chunks=chunks,
                raw_request=req,
                commit_request_id=commit_request_id,
                uwg_commit_receipt_id=uwg_commit_receipt_id,
            )
        except Exception as exc:  # guardian: allow-default-fallback -- Chroma optional in CI; receipts record failure  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
            return GovernedChromaProjectionOutcome(
                refresh_status="FAILED",
                read_surface_refresh_status="MISSING",
                chroma_projection_status="MISSING",
                reason=f"chroma_upsert_failed:{exc}",
                artifacts_written=written,
            )
    else:
        return GovernedChromaProjectionOutcome(
            refresh_status="SKIPPED",
            read_surface_refresh_status="NOT_APPLICABLE",
            chroma_projection_status="NOT_APPLICABLE",
            reason="APPS_RG_R1B_SKIP_CHROMA_PROJECTION",
            artifacts_written=written,
        )

    _write_envelope(
        artifact_dir / READ_SURFACE_REFRESH_ARTIFACT,
        {
            "schema_version": SCHEMA_READ_SURFACE_REFRESH,
            "read_surface": READ_SURFACE_NAME,
            "refresh_status": "COMPLETE",
            "refresh_digest": refresh_digest,
            "refreshed_at": refreshed_at,
            "commit_request_ref": chain_refs.get("commit_request_ref", "commit_request.json"),
            "state_diff_validation_result_ref": chain_refs.get(
                "state_diff_validation_result_ref", "state_diff_validation_result.json"
            ),
            "uwg_commit_receipt_ref": chain_refs.get(
                "uwg_commit_receipt_ref", "uwg_commit_receipt.json"
            ),
            "l4_namespace_object_ref": chain_refs.get(
                "l4_namespace_object_ref_ref", "l4_namespace_object_ref.json"
            ),
            "proposed_state_diff_ref": chain_refs.get(
                "proposed_state_diff_ref_ref", "proposed_state_diff_ref.json"
            ),
            "uwg_commit_receipt_id": uwg_commit_receipt_id,
            "commit_request_id": commit_request_id,
            "governed_projection": True,
            "non_durable_shadow_path": False,
        },
        artifact_name=READ_SURFACE_REFRESH_ARTIFACT,
        section_id=section_id,
        run_id=run_id,
    )
    written.append(READ_SURFACE_REFRESH_ARTIFACT)

    _write_envelope(
        artifact_dir / CHROMA_COLLECTION_INDEX_ARTIFACT,
        {
            "schema_version": SCHEMA_CHROMA_COLLECTION_INDEX,
            "collection_name": chroma_meta["collection_name"],
            "chroma_persist_path": chroma_meta["chroma_persist_path"],
            "read_surface": READ_SURFACE_NAME,
            "record_id": record.record_id,
            "commit_request_ref": "commit_request.json",
            "uwg_commit_receipt_ref": "uwg_commit_receipt.json",
            "indexed_id": chroma_meta.get("upserted_parent_id") or chroma_meta.get("upserted_id"),
            "not_core_d2_collection": True,
            "core_d2_collection_name": "l2_semantic_cache",
        },
        artifact_name=CHROMA_COLLECTION_INDEX_ARTIFACT,
        section_id=section_id,
        run_id=run_id,
    )
    written.append(CHROMA_COLLECTION_INDEX_ARTIFACT)

    _write_envelope(
        artifact_dir / CHROMA_READ_AFTER_WRITE_ARTIFACT,
        {
            "schema_version": SCHEMA_CHROMA_READ_AFTER_WRITE,
            "read_after_write_status": "PASS" if chroma_meta.get("read_after_write_ok") else "FAIL",
            "queried_record_id": record.record_id,
            "ids_returned": chroma_meta.get("query_ids") or [],
            "collection_ref": CHROMA_COLLECTION_INDEX_ARTIFACT,
            "read_surface_refresh_ref": READ_SURFACE_REFRESH_ARTIFACT,
            "commit_request_id": commit_request_id,
            "governed_read_surface_only": True,
        },
        artifact_name=CHROMA_READ_AFTER_WRITE_ARTIFACT,
        section_id=section_id,
        run_id=run_id,
    )
    written.append(CHROMA_READ_AFTER_WRITE_ARTIFACT)

    return GovernedChromaProjectionOutcome(
        refresh_status="COMPLETE",
        read_surface_refresh_status="COMPLETE",
        chroma_projection_status="COMPLETE",
        read_surface_refresh_complete=True,
        chroma_projection_complete=chroma_meta.get("read_after_write_ok", False),
        artifacts_written=written,
        chroma_persist_path=str(chroma_meta.get("chroma_persist_path") or ""),
    )


__all__ = [
    "CHROMA_COLLECTION_INDEX_ARTIFACT",
    "CHROMA_READ_AFTER_WRITE_ARTIFACT",
    "GovernedChromaProjectionOutcome",
    "READ_SURFACE_NAME",
    "READ_SURFACE_REFRESH_ARTIFACT",
    "project_governed_chroma_read_surface",
]
