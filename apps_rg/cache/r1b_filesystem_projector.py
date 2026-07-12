"""Idempotent filesystem projector for canonical R1B L4 commits."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from agentic_core.L4_state.contracts.digests import compute_deterministic_digest
from apps_rg.cache.r1b_constants import (
    R1B_STORAGE_SUBSYSTEM,
    R1B_UWG_TARGET_SURFACE,
)


@dataclass(frozen=True)
class R1BFilesystemProjectionReceipt:
    status: str
    record_id: str
    source_commit_receipt_ref: str
    projection_root: str
    intent_path: str
    payload_digest: str
    file_hashes: dict[str, str]
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "apps_rg.r1b_filesystem_projection_receipt.v1",
            "status": self.status,
            "record_id": self.record_id,
            "source_commit_receipt_ref": self.source_commit_receipt_ref,
            "projection_root": self.projection_root,
            "intent_path": self.intent_path,
            "payload_digest": self.payload_digest,
            "file_hashes": dict(self.file_hashes),
            "reason": self.reason,
            "read_surface_role": "projection_not_truth",
        }


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _atomic_write_json(path: Path, payload: Mapping[str, Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (
        json.dumps(dict(payload), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent)
    )
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
        try:
            dir_fd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
        except OSError:
            pass
    finally:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
    return _sha256_bytes(data)


def project_r1b_filesystem_from_outbox(
    *,
    projection_root: Path | str,
    candidate: Any,
    outcome: Any,
    outbox_payload_digest: str,
) -> R1BFilesystemProjectionReceipt:
    """Materialize a recoverable projection from an already-committed outbox task."""

    if str(getattr(outcome, "status", "")) != "ADMITTED":
        return R1BFilesystemProjectionReceipt(
            status="FAILED",
            record_id=str(candidate.record.record_id),
            source_commit_receipt_ref="",
            projection_root=str(projection_root),
            intent_path="",
            payload_digest=outbox_payload_digest,
            file_hashes={},
            reason="uwg_commit_not_admitted",
        )
    receipt = dict(getattr(outcome, "uwg_commit_receipt", None) or {})
    commit_receipt_id = str(
        receipt.get("commit_receipt_id")
        or getattr(outcome, "uwg_commit_receipt_id", "")
        or ""
    )
    if not commit_receipt_id:
        raise ValueError("R1B filesystem projection requires a core commit receipt")

    root = Path(projection_root).resolve() / "durable" / "uwg_admitted"
    intents = root / "intents"
    chunks = root / "chunks" / candidate.record.record_id
    receipts = root / "receipts"
    embeddings = root / "embeddings" / candidate.record.record_id

    from apps_rg.cache.r1b_bge_embedding import (
        chunk_vector_payload,
        intent_vector_payload,
    )

    intent_embedding = intent_vector_payload(
        intent_text=candidate.record.request_intent_text,
        digest=candidate.record.normalized_intent_digest,
    )
    chunk_embeddings = [
        {
            "chunk_id": row.chunk_id,
            "chunk_type": row.chunk_type,
            "embedding": chunk_vector_payload(
                chunk_text=row.chunk_text or row.chunk_type,
                chunk_id=row.chunk_id,
            ),
        }
        for row in candidate.chunks
    ]
    bundle = {
        "schema_version": candidate.record.schema_version,
        "storage_subsystem": R1B_STORAGE_SUBSYSTEM,
        "storage_tier": "uwg_admitted_durable_projection",
        "read_surface_role": "projection_not_truth",
        "durable_write_path": str(getattr(outcome, "durable_write_path", "")),
        "uwg_commit_receipt_id": commit_receipt_id,
        "source_commit_receipt_ref": commit_receipt_id,
        "commit_request_id": str(getattr(outcome, "commit_request_id", "")),
        "core_uwg_commit_receipt": receipt,
        "governance_receipt": getattr(outcome, "governance_receipt", None),
        "policy_hash": receipt.get("policy_hash") or candidate.policy_hash,
        "blueprint_hash": receipt.get("blueprint_hash") or candidate.blueprint_hash,
        "replay_key": receipt.get("replay_key") or "",
        "registry_digest_set": receipt.get("registry_digest_set") or [],
        "gate_verdict_refs": receipt.get("gate_verdict_refs") or [],
        "l5_certification_ref": receipt.get("l5_certification_ref") or "",
        "audit_append_receipt_ref": receipt.get("audit_append_receipt_ref") or "",
        "content_hash": receipt.get("content_hash") or "",
        "chain_hash": receipt.get("chain_hash") or "",
        "snapshot_before": receipt.get("snapshot_before") or "",
        "snapshot_after": receipt.get("snapshot_after") or "",
        "parent_intent_record": candidate.record.to_dict(),
        "child_chunks": [row.to_dict() for row in candidate.chunks],
        "child_chunk_embedding_metadata": chunk_embeddings,
        "request_intent_embedding": intent_embedding,
        "target_l4_namespace": R1B_UWG_TARGET_SURFACE,
        "post_exit_eligibility_receipt": candidate.post_exit_eligibility,
        "source_run_id": candidate.source_run_id,
        "x3_disposition_ref": candidate.x3_disposition_ref,
        "proof_eligibility_ref": candidate.proof_eligibility_ref,
        "c0_fact_vectors_consulted": False,
        "outbox_payload_digest": outbox_payload_digest,
    }
    bundle_digest = compute_deterministic_digest(bundle)
    bundle["projection_payload_digest"] = bundle_digest

    file_hashes: dict[str, str] = {}
    intent_path = intents / f"{candidate.record.record_id}.json"
    file_hashes[str(intent_path)] = _atomic_write_json(intent_path, bundle)
    file_hashes[str(embeddings / "intent.json")] = _atomic_write_json(
        embeddings / "intent.json", intent_embedding
    )
    receipt_path = receipts / f"{candidate.record.record_id}_uwg_commit.json"
    file_hashes[str(receipt_path)] = _atomic_write_json(
        receipt_path,
        {
            **outcome.to_dict(),
            "projection_payload_digest": bundle_digest,
            "outbox_payload_digest": outbox_payload_digest,
        },
    )
    for row in candidate.chunks:
        path = chunks / f"{row.chunk_id}.json"
        file_hashes[str(path)] = _atomic_write_json(path, row.to_dict())

    from apps_rg.cache.r1b_derived_index import project_durable_to_derived_index

    project_durable_to_derived_index(Path(projection_root).resolve())
    check = json.loads(intent_path.read_text(encoding="utf-8"))
    if check.get("source_commit_receipt_ref") != commit_receipt_id:
        raise RuntimeError("filesystem read-after-write commit receipt mismatch")
    if check.get("projection_payload_digest") != bundle_digest:
        raise RuntimeError("filesystem read-after-write payload digest mismatch")

    return R1BFilesystemProjectionReceipt(
        status="COMPLETE",
        record_id=candidate.record.record_id,
        source_commit_receipt_ref=commit_receipt_id,
        projection_root=str(Path(projection_root).resolve()),
        intent_path=str(intent_path),
        payload_digest=outbox_payload_digest,
        file_hashes=file_hashes,
    )


__all__ = [
    "R1BFilesystemProjectionReceipt",
    "project_r1b_filesystem_from_outbox",
]
