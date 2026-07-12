"""Governed R1B receipt chain backed by transactional L4 and projection outbox."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from agentic_core.L2_execution.utils import write_gateway as _wg
from apps_rg.cache.r1b_commit_authority import X3C_COMMIT_AUTHORITY
from apps_rg.cache.r1b_post_exit_ingest import evaluate_post_exit_ingestion
from apps_rg.cache.r1b_strict_gateway import get_r1b_strict_gateway
from apps_rg.cache.r1b_transactional_promotion import promote_r1b_transactionally
from apps_rg.cache.r1b_uwg_promotion import (
    R1BCachePromotionCandidate,
    R1BPromotionOutcome,
    build_r1b_promotion_candidate,
)

SCHEMA_GOVERNED_CHAIN = "r1b_governed_receipt_chain_v2"
SCHEMA_RECEIPT_ENVELOPE = "apps_rg_r1b_governed_receipt_envelope_v2"
PRODUCER_MODULE = "apps_rg.cache.r1b_governed_receipt_emission"

GOVERNED_CHAIN_MANIFEST = "r1b_governed_receipt_chain.json"
COMMIT_REQUEST_ARTIFACT = "commit_request.json"
STATE_DIFF_VALIDATION_ARTIFACT = "state_diff_validation_result.json"
UWG_COMMIT_RECEIPT_ARTIFACT = "uwg_commit_receipt.json"
BLOCKED_WRITE_RECEIPT_ARTIFACT = "blocked_write_receipt.json"
L4_NAMESPACE_OBJECT_REF_ARTIFACT = "l4_namespace_object_ref.json"
PROPOSED_STATE_DIFF_REF_ARTIFACT = "proposed_state_diff_ref.json"
READ_SURFACE_DEFERRED_ARTIFACT = "read_surface_refresh_receipt_w6b_status.json"
CHROMA_PROJECTION_DEFERRED_ARTIFACT = "chroma_collection_index_ref_w6b_status.json"

REASON_X3_NOT_X3C = "x3_disposition_not_X3C"
REASON_ROUTE_NOT_ELIGIBLE = "route_not_r1b_promotion_eligible"
REASON_PROJECTION_PENDING = "transactional_projection_not_complete"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return value if isinstance(value, dict) else {}


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    _wg.write_text(
        path,
        json.dumps(dict(payload), ensure_ascii=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )


def _write_envelope(
    path: Path,
    payload: Mapping[str, Any],
    *,
    artifact_name: str,
    section_id: str,
    run_id: str,
) -> None:
    _write_json(
        path,
        {
            "schema_version": SCHEMA_RECEIPT_ENVELOPE,
            "generated_at_utc": _utc_now(),
            "producer": PRODUCER_MODULE,
            "artifact_name": artifact_name,
            "section_id": section_id,
            "run_id": run_id,
            "payload": dict(payload),
        },
    )


def _load_x3_code(artifact_dir: Path) -> str:
    payload = _read_json(artifact_dir / "x3_disposition.json")
    return str(
        payload.get("x3_code") or payload.get("disposition") or ""
    ).strip().upper()


def _raw_request_from_run_dir(artifact_dir: Path) -> dict[str, Any]:
    manifest = _read_json(artifact_dir / "run_manifest.json")
    return {
        "target_company": str(manifest.get("target_company") or ""),
        "target_role": str(manifest.get("target_role") or ""),
        "section_id": str(manifest.get("section_id") or ""),
        "jd_hash": str(manifest.get("jd_hash") or manifest.get("jd_digest") or ""),
        "resume_hash": str(
            manifest.get("resume_hash")
            or manifest.get("base_resume_digest")
            or ""
        ),
        "run_id": str(manifest.get("run_id") or artifact_dir.name),
    }


def _enrich_l4_namespace_ref_with_c0_payload(
    artifact_dir: Path,
    *,
    candidate: R1BCachePromotionCandidate,
    outcome: R1BPromotionOutcome,
) -> None:
    path = artifact_dir / L4_NAMESPACE_OBJECT_REF_ARTIFACT
    envelope = _read_json(path)
    payload = envelope.get("payload") if isinstance(envelope, dict) else None
    if not isinstance(payload, dict):
        return

    from apps_rg.cache.r1b_bge_embedding import intent_vector_payload
    from apps_rg.runtime.c0.c02_semantic_cache_payload import (
        C02_SEMANTIC_CACHE_PAYLOAD_ARTIFACT,
        read_c02_semantic_cache_payload,
    )

    payload.setdefault("parent_intent_record", candidate.record.to_dict())
    payload.setdefault(
        "child_output_chunks",
        [chunk.to_dict() for chunk in candidate.chunks],
    )
    payload.setdefault(
        "request_intent_embedding_ref",
        intent_vector_payload(
            intent_text=candidate.record.request_intent_text,
            digest=candidate.record.normalized_intent_digest,
        ),
    )
    if candidate.l5_certification_packet_digest:
        payload.setdefault(
            "l5_certification_packet_digest",
            candidate.l5_certification_packet_digest,
        )
    if outcome.governance_receipt:
        payload.setdefault("governance_receipt", outcome.governance_receipt)
    c0_payload = read_c02_semantic_cache_payload(artifact_dir)
    if not c0_payload:
        c0_payload = _read_json(artifact_dir / C02_SEMANTIC_CACHE_PAYLOAD_ARTIFACT)
    if c0_payload:
        payload["c0_section_intent_vector"] = c0_payload.get("intent_vector") or {}
        payload["c0_section_intent_digest"] = c0_payload.get("intent_digest") or ""
        payload["c0_query_output"] = c0_payload.get("query_output") or []
        payload["c0_query_output_count"] = c0_payload.get("query_output_count") or 0
        payload["c0_dense_search_refs"] = c0_payload.get("dense_search_refs") or []
    envelope["payload"] = payload
    _atomic_rewrite_json(path, envelope)


def _atomic_rewrite_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (
        json.dumps(dict(payload), ensure_ascii=False, indent=2, sort_keys=True)
        + "\n"
    ).encode("utf-8")
    fd, tmp = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=str(path.parent),
    )
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass


@dataclass
class R1BGovernedReceiptChainOutcome:
    commit_request_status: str
    semantic_cache_persistence_status: str
    uwg_validation_status: str
    uwg_commit_or_block_status: str
    l4_object_ref_status: str
    read_surface_refresh_status: str
    chroma_projection_status: str
    read_surface_refresh_complete: bool = False
    chroma_projection_complete: bool = False
    durable_vector_persistence_proven: bool = False
    reason: str = ""
    x3_code: str = ""
    section_id: str = ""
    run_id: str = ""
    whole_run_id: str = ""
    trace_root: str = ""
    promotion_outcome: R1BPromotionOutcome | None = None
    artifacts_written: list[str] = field(default_factory=list)
    reconciliation: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_GOVERNED_CHAIN,
            "generated_at_utc": _utc_now(),
            "producer": PRODUCER_MODULE,
            "section_id": self.section_id,
            "run_id": self.run_id,
            "whole_run_id": self.whole_run_id,
            "trace_root": self.trace_root,
            "x3_disposition_ref": "x3_disposition.json",
            "x3_code": self.x3_code,
            "commit_request_status": self.commit_request_status,
            "semantic_cache_persistence_status": self.semantic_cache_persistence_status,
            "uwg_validation_status": self.uwg_validation_status,
            "uwg_commit_or_block_status": self.uwg_commit_or_block_status,
            "l4_object_ref_status": self.l4_object_ref_status,
            "read_surface_refresh_status": self.read_surface_refresh_status,
            "chroma_projection_status": self.chroma_projection_status,
            "read_surface_refresh_complete": self.read_surface_refresh_complete,
            "chroma_projection_complete": self.chroma_projection_complete,
            "durable_vector_persistence_proven": self.durable_vector_persistence_proven,
            "reason": self.reason,
            "promotion_outcome": (
                self.promotion_outcome.to_dict() if self.promotion_outcome else None
            ),
            "artifacts_written": list(self.artifacts_written),
            "reconciliation": self.reconciliation,
            "canonical_commit_backend": "sqlite",
            "projection_delivery": "durable_outbox",
            "explicit_non_claims": [
                "core D2 Chroma promote path is not durable persistence proof",
                "projection completion is not claimed until read-after-write succeeds",
            ],
        }


def _base_outcome(
    *, artifact_dir: Path, section_id: str, run_id: str, x3_code: str
) -> R1BGovernedReceiptChainOutcome:
    manifest = _read_json(artifact_dir / "run_manifest.json")
    return R1BGovernedReceiptChainOutcome(
        commit_request_status="NOT_EMITTED",
        semantic_cache_persistence_status="NOT_APPLICABLE",
        uwg_validation_status="NOT_RUN",
        uwg_commit_or_block_status="NOT_RUN",
        l4_object_ref_status="NOT_RUN",
        read_surface_refresh_status="NOT_APPLICABLE",
        chroma_projection_status="NOT_APPLICABLE",
        x3_code=x3_code,
        section_id=section_id,
        run_id=run_id,
        whole_run_id=str(manifest.get("run_id") or run_id),
        trace_root=f"trace:{run_id}",
    )


def _existing_artifacts(artifact_dir: Path) -> list[str]:
    names = (
        COMMIT_REQUEST_ARTIFACT,
        STATE_DIFF_VALIDATION_ARTIFACT,
        UWG_COMMIT_RECEIPT_ARTIFACT,
        BLOCKED_WRITE_RECEIPT_ARTIFACT,
        L4_NAMESPACE_OBJECT_REF_ARTIFACT,
        PROPOSED_STATE_DIFF_REF_ARTIFACT,
        "read_surface_refresh_receipt.json",
        "chroma_collection_index_ref.json",
        "chroma_read_after_write_receipt.json",
        "request_intent_embedding_ref.json",
        "request_intent_embedding_ref_mapping_receipt.json",
        "r1b_compatibility_proof.json",
        "r1b_uwg_admitted_projection_bundle.json",
    )
    return [name for name in names if (artifact_dir / name).is_file()]


def emit_section_r1b_governed_receipt_chain(
    *,
    artifact_dir: Path,
    section_id: str,
    run_id: str,
    raw_request: dict[str, Any] | None = None,
    gateway: Any | None = None,
    attempt_uwg_promotion: bool = True,
) -> R1BGovernedReceiptChainOutcome:
    """Emit evidence for one X3C-authorized transactional R1B promotion."""

    artifact_dir = Path(artifact_dir).resolve()
    x3_code = _load_x3_code(artifact_dir)
    chain = _base_outcome(
        artifact_dir=artifact_dir,
        section_id=section_id,
        run_id=run_id,
        x3_code=x3_code,
    )
    if x3_code != X3C_COMMIT_AUTHORITY:
        chain.reason = REASON_X3_NOT_X3C
        _write_json(artifact_dir / GOVERNED_CHAIN_MANIFEST, chain.to_dict())
        return chain
    if not attempt_uwg_promotion:
        chain.semantic_cache_persistence_status = "NOT_PROVEN"
        chain.chroma_projection_status = "MISSING"
        chain.reason = "uwg_promotion_skipped"
        _write_json(artifact_dir / GOVERNED_CHAIN_MANIFEST, chain.to_dict())
        return chain

    request = dict(raw_request or _raw_request_from_run_dir(artifact_dir))
    assessment = evaluate_post_exit_ingestion(
        run_dir=artifact_dir,
        raw_request=request,
    )
    if not assessment.get("admissible") and not assessment.get("cache_admissible"):
        chain.reason = str(
            assessment.get("non_admissible_reason") or REASON_ROUTE_NOT_ELIGIBLE
        )
        _write_json(artifact_dir / GOVERNED_CHAIN_MANIFEST, chain.to_dict())
        return chain
    assessment["exit_metadata"] = {
        **dict(assessment.get("exit_metadata") or {}),
        "x3_commit_authorized": True,
        "x3_disposition": X3C_COMMIT_AUTHORITY,
    }

    from apps_rg.cache.r1b_models import HistoricalIntentRecord, HistoricalOutputChunk

    record = HistoricalIntentRecord.from_dict(assessment["record"])
    chunks = [
        HistoricalOutputChunk.from_dict(row)
        for row in assessment.get("chunks") or []
    ]
    candidate = build_r1b_promotion_candidate(
        record=record,
        chunks=chunks,
        post_exit_eligibility=assessment,
        run_dir=artifact_dir,
    )
    effective_gateway = (
        gateway
        if gateway is not None and hasattr(gateway, "register_candidate")
        else get_r1b_strict_gateway()
    )
    result = promote_r1b_transactionally(
        candidate=candidate,
        projection_root=artifact_dir,
        artifact_dir=artifact_dir,
        section_id=section_id,
        run_id=run_id,
        raw_request=request,
        gateway=effective_gateway,
    )
    chain.commit_request_status = "EMITTED"
    chain.promotion_outcome = result.promotion
    chain.artifacts_written = _existing_artifacts(artifact_dir)
    if result.promotion.status != "ADMITTED":
        chain.uwg_validation_status = "FAIL"
        chain.uwg_commit_or_block_status = "BLOCKED"
        chain.l4_object_ref_status = "MISSING"
        chain.semantic_cache_persistence_status = "BLOCKED"
        chain.reason = ";".join(result.promotion.blocked_reason_codes)
        _write_envelope(
            artifact_dir / BLOCKED_WRITE_RECEIPT_ARTIFACT,
            result.promotion.to_dict(),
            artifact_name=BLOCKED_WRITE_RECEIPT_ARTIFACT,
            section_id=section_id,
            run_id=run_id,
        )
        chain.artifacts_written = _existing_artifacts(artifact_dir)
        _write_json(artifact_dir / GOVERNED_CHAIN_MANIFEST, chain.to_dict())
        return chain

    chain.uwg_validation_status = "PASS"
    chain.uwg_commit_or_block_status = "ADMITTED"
    chain.l4_object_ref_status = "PRESENT"
    chain.semantic_cache_persistence_status = "PROVEN_UWG_CHAIN_ONLY"
    if result.projection is not None:
        chain.reconciliation = result.projection.reconciliation
        if result.projection.status == "COMPLETE":
            chain.read_surface_refresh_status = "COMPLETE"
            chain.chroma_projection_status = (
                "COMPLETE"
                if result.projection.chroma_receipt is not None
                else "NOT_APPLICABLE"
            )
            chain.read_surface_refresh_complete = True
            chain.chroma_projection_complete = (
                result.projection.chroma_receipt is None
                or bool(
                    result.projection.chroma_receipt.get(
                        "chroma_projection_complete"
                    )
                )
            )
            chain.durable_vector_persistence_proven = (
                chain.chroma_projection_complete
            )
            chain.semantic_cache_persistence_status = (
                "PROVEN_GOVERNED_VECTOR_CHAIN"
                if chain.durable_vector_persistence_proven
                else "PROVEN_TRANSACTIONAL_FILESYSTEM_CHAIN"
            )
        else:
            chain.read_surface_refresh_status = "PENDING"
            chain.chroma_projection_status = "PENDING"
            chain.reason = result.projection.reason or REASON_PROJECTION_PENDING
    chain.artifacts_written = _existing_artifacts(artifact_dir)
    _write_json(artifact_dir / GOVERNED_CHAIN_MANIFEST, chain.to_dict())
    return chain


def _materialize_uwg_receipts(
    artifact_dir: Path,
    *,
    candidate: R1BCachePromotionCandidate,
    section_id: str,
    run_id: str,
    manifest: Mapping[str, Any],
    gateway: Any | None,
) -> R1BGovernedReceiptChainOutcome:
    """Compatibility materializer for older receipt-level tests.

    The public chain entry point remains X3C-gated. This helper accepts an
    already assembled promotion candidate from tests and routes it through the
    current transactional promotion path, preserving the legacy L4 namespace
    artifact payload shape.
    """

    artifact_dir = Path(artifact_dir).resolve()
    exit_metadata = {
        **dict(candidate.post_exit_eligibility.get("exit_metadata") or {}),
        "x3_disposition": X3C_COMMIT_AUTHORITY,
    }
    record = replace(candidate.record, x3_disposition=X3C_COMMIT_AUTHORITY)
    promoted_candidate = replace(
        candidate,
        record=record,
        post_exit_eligibility={
            **candidate.post_exit_eligibility,
            "exit_metadata": exit_metadata,
        },
    )
    effective_gateway = (
        gateway
        if gateway is not None and hasattr(gateway, "register_candidate")
        else get_r1b_strict_gateway()
    )
    result = promote_r1b_transactionally(
        candidate=promoted_candidate,
        projection_root=artifact_dir,
        artifact_dir=artifact_dir,
        section_id=section_id,
        run_id=run_id or str(manifest.get("run_id") or candidate.source_run_id),
        raw_request=_raw_request_from_run_dir(artifact_dir),
        gateway=effective_gateway,
    )
    chain = _base_outcome(
        artifact_dir=artifact_dir,
        section_id=section_id,
        run_id=run_id,
        x3_code=X3C_COMMIT_AUTHORITY,
    )
    chain.commit_request_status = "EMITTED"
    chain.promotion_outcome = result.promotion
    chain.artifacts_written = _existing_artifacts(artifact_dir)
    if result.promotion.status != "ADMITTED":
        chain.uwg_validation_status = "FAIL"
        chain.uwg_commit_or_block_status = "BLOCKED"
        chain.semantic_cache_persistence_status = "BLOCKED"
        chain.reason = ";".join(result.promotion.blocked_reason_codes)
        _write_json(artifact_dir / GOVERNED_CHAIN_MANIFEST, chain.to_dict())
        return chain

    _enrich_l4_namespace_ref_with_c0_payload(
        artifact_dir,
        candidate=promoted_candidate,
        outcome=result.promotion,
    )
    chain.uwg_validation_status = "PASS"
    chain.uwg_commit_or_block_status = "ADMITTED"
    chain.l4_object_ref_status = "PRESENT"
    chain.semantic_cache_persistence_status = "PROVEN_TRANSACTIONAL_FILESYSTEM_CHAIN"
    if result.projection is not None:
        chain.reconciliation = result.projection.reconciliation
        chain.read_surface_refresh_status = result.projection.status
        chain.read_surface_refresh_complete = result.projection.status == "COMPLETE"
        chain.chroma_projection_status = (
            "COMPLETE"
            if result.projection.chroma_receipt is not None
            else "NOT_APPLICABLE"
        )
        chain.chroma_projection_complete = (
            result.projection.chroma_receipt is None
            or bool(
                result.projection.chroma_receipt.get("chroma_projection_complete")
            )
        )
        chain.durable_vector_persistence_proven = chain.chroma_projection_complete
    chain.artifacts_written = _existing_artifacts(artifact_dir)
    _write_json(artifact_dir / GOVERNED_CHAIN_MANIFEST, chain.to_dict())
    return chain


__all__ = [
    "BLOCKED_WRITE_RECEIPT_ARTIFACT",
    "CHROMA_PROJECTION_DEFERRED_ARTIFACT",
    "COMMIT_REQUEST_ARTIFACT",
    "GOVERNED_CHAIN_MANIFEST",
    "L4_NAMESPACE_OBJECT_REF_ARTIFACT",
    "PROPOSED_STATE_DIFF_REF_ARTIFACT",
    "R1BGovernedReceiptChainOutcome",
    "READ_SURFACE_DEFERRED_ARTIFACT",
    "REASON_X3_NOT_X3C",
    "STATE_DIFF_VALIDATION_ARTIFACT",
    "UWG_COMMIT_RECEIPT_ARTIFACT",
    "_materialize_uwg_receipts",
    "emit_section_r1b_governed_receipt_chain",
]
