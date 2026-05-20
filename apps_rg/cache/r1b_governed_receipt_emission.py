"""W6B — governed R1B semantic-cache receipt chain in section run folders (apps_rg only).

Emits Exit-sourced CommitRequest → UWG validation → commit/blocked receipts and L4
namespace refs into the section ``artifact_dir``. Does not upsert Chroma; read-surface
refresh remains deferred until W6C.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from apps_rg.cache.r1b_constants import R1B_UWG_TARGET_SURFACE, X3_FINISH_ALLOWED
from apps_rg.cache.r1b_post_exit_ingest import evaluate_post_exit_ingestion
from apps_rg.cache.r1b_uwg_promotion import (
    R1BCachePromotionCandidate,
    R1BPromotionOutcome,
    build_r1b_commit_bundle,
    build_r1b_promotion_candidate,
)

SCHEMA_GOVERNED_CHAIN = "r1b_governed_receipt_chain_v1"
SCHEMA_RECEIPT_ENVELOPE = "apps_rg_r1b_governed_receipt_envelope_v1"
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
REASON_W6C_DEFERRED = "w6c_chroma_read_surface_projection_deferred"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
        return doc if isinstance(doc, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _record_payload(obj: Any) -> dict[str, Any]:
    if is_dataclass(obj):
        raw = asdict(obj)
        return {
            k: (list(v) if isinstance(v, tuple) else v)
            for k, v in raw.items()
        }
    if isinstance(obj, Mapping):
        return dict(obj)
    return {"value": obj}


def _write_envelope(
    path: Path,
    payload: Mapping[str, Any],
    *,
    artifact_name: str,
    section_id: str,
    run_id: str,
) -> None:
    doc = {
        "schema_version": SCHEMA_RECEIPT_ENVELOPE,
        "generated_at_utc": _utc_now(),
        "producer": PRODUCER_MODULE,
        "artifact_name": artifact_name,
        "section_id": section_id,
        "run_id": run_id,
        "payload": dict(payload),
    }
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _load_x3_code(artifact_dir: Path) -> str:
    x3 = _read_json(artifact_dir / "x3_disposition.json")
    return str(x3.get("x3_code") or x3.get("disposition") or "").strip().upper()


def _raw_request_from_run_dir(artifact_dir: Path) -> dict[str, Any]:
    manifest = _read_json(artifact_dir / "run_manifest.json")
    return {
        "target_company": str(manifest.get("target_company") or ""),
        "target_role": str(manifest.get("target_role") or ""),
        "section_id": str(manifest.get("section_id") or ""),
        "jd_hash": str(manifest.get("jd_hash") or manifest.get("jd_digest") or ""),
        "resume_hash": str(manifest.get("resume_hash") or manifest.get("base_resume_digest") or ""),
        "run_id": str(manifest.get("run_id") or artifact_dir.name),
    }


def _registry_digest_set(manifest: Mapping[str, Any]) -> list[str]:
    digests: list[str] = []
    for key in (
        "tool_registry_digest",
        "model_registry_digest",
        "provider_lane_digest",
        "registry_digest_set",
    ):
        val = manifest.get(key)
        if isinstance(val, (list, tuple)):
            digests.extend(str(x) for x in val if x)
        elif val:
            digests.append(str(val))
    return digests


@dataclass
class R1BGovernedReceiptChainOutcome:
    """Summary of W6B receipt emission for one section run folder."""

    commit_request_status: str  # EMITTED | NOT_EMITTED
    semantic_cache_persistence_status: str  # NOT_APPLICABLE | NOT_PROVEN | PROVEN_UWG_CHAIN_ONLY | ...
    uwg_validation_status: str  # NOT_RUN | PASS | FAIL
    uwg_commit_or_block_status: str  # NOT_RUN | ADMITTED | BLOCKED
    l4_object_ref_status: str  # NOT_RUN | PRESENT | MISSING
    read_surface_refresh_status: str  # NOT_APPLICABLE | MISSING
    chroma_projection_status: str  # MISSING | NOT_APPLICABLE
    reason: str = ""
    x3_code: str = ""
    section_id: str = ""
    run_id: str = ""
    whole_run_id: str = ""
    trace_root: str = ""
    promotion_outcome: R1BPromotionOutcome | None = None
    artifacts_written: list[str] = field(default_factory=list)

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
            "reason": self.reason,
            "promotion_outcome": self.promotion_outcome.to_dict() if self.promotion_outcome else None,
            "artifacts_written": list(self.artifacts_written),
            "explicit_non_claims": [
                "no Chroma upsert on W6B path",
                "read_surface_refresh canonical receipt deferred until W6C",
                "chroma_collection_index_ref deferred until W6C",
                "vector persistence not claimed without full governed refresh chain",
            ],
        }


def _write_deferred_surface_status(
    artifact_dir: Path,
    *,
    section_id: str,
    run_id: str,
    chain: R1BGovernedReceiptChainOutcome,
) -> None:
    _write_envelope(
        artifact_dir / READ_SURFACE_DEFERRED_ARTIFACT,
        {
            "status": "NOT_APPLICABLE",
            "reason": REASON_W6C_DEFERRED,
            "canonical_artifact": "read_surface_refresh_receipt.json",
            "notes": (
                "W6B emits UWG/L4 admission receipts only; governed Chroma read-surface "
                "projection is W6C"
            ),
        },
        artifact_name=READ_SURFACE_DEFERRED_ARTIFACT,
        section_id=section_id,
        run_id=run_id,
    )
    chain.artifacts_written.append(READ_SURFACE_DEFERRED_ARTIFACT)
    _write_envelope(
        artifact_dir / CHROMA_PROJECTION_DEFERRED_ARTIFACT,
        {
            "status": "MISSING",
            "reason": REASON_W6C_DEFERRED,
            "canonical_artifact": "chroma_collection_index_ref.json",
            "notes": "Chroma collection/index ref not materialized until W6C",
        },
        artifact_name=CHROMA_PROJECTION_DEFERRED_ARTIFACT,
        section_id=section_id,
        run_id=run_id,
    )
    chain.artifacts_written.append(CHROMA_PROJECTION_DEFERRED_ARTIFACT)
    chain.read_surface_refresh_status = "NOT_APPLICABLE"
    chain.chroma_projection_status = "MISSING"


def _materialize_uwg_receipts(
    artifact_dir: Path,
    *,
    candidate: R1BCachePromotionCandidate,
    section_id: str,
    run_id: str,
    manifest: Mapping[str, Any],
    gateway: Any | None,
) -> R1BGovernedReceiptChainOutcome:
    from apps_rg.cache.r1b_uwg_gateway_shim import default_r1b_promotion_gateway
    from apps_rg.cache.r1b_uwg_receipt_contract import validate_commit_request_governance

    gw = gateway or default_r1b_promotion_gateway()
    cr, state_diffs, rollback, refresh = build_r1b_commit_bundle(candidate)
    sd = state_diffs[0] if state_diffs else None
    trace_root = str(candidate.trace_root)
    whole_run_id = str(candidate.source_run_id)
    registry_digests = _registry_digest_set(manifest)

    chain = R1BGovernedReceiptChainOutcome(
        commit_request_status="EMITTED",
        semantic_cache_persistence_status="NOT_PROVEN",
        uwg_validation_status="NOT_RUN",
        uwg_commit_or_block_status="NOT_RUN",
        l4_object_ref_status="MISSING",
        read_surface_refresh_status="NOT_APPLICABLE",
        chroma_projection_status="MISSING",
        x3_code=str(
            (candidate.post_exit_eligibility.get("exit_metadata") or {}).get("x3_disposition")
            or ""
        ),
        section_id=section_id,
        run_id=run_id,
        whole_run_id=whole_run_id,
        trace_root=trace_root,
    )

    cr_payload = _record_payload(cr)
    cr_payload["section_id"] = section_id
    cr_payload["whole_run_id"] = whole_run_id
    cr_payload["x3_disposition_ref"] = candidate.x3_disposition_ref
    cr_payload["proposed_state_diff_ref"] = sd.state_diff_id if sd else ""
    cr_payload["target_l4_namespace"] = R1B_UWG_TARGET_SURFACE
    cr_payload["target_state_object"] = str(sd.after_candidate) if sd else ""
    cr_payload["registry_digest_set"] = registry_digests
    cr_payload["audit_manifest_ref"] = f"governance_receipt:{candidate.record.record_id}"
    cr_payload["idempotency_key"] = str(cr.replay_key)

    _write_envelope(
        artifact_dir / COMMIT_REQUEST_ARTIFACT,
        cr_payload,
        artifact_name=COMMIT_REQUEST_ARTIFACT,
        section_id=section_id,
        run_id=run_id,
    )
    chain.artifacts_written.append(COMMIT_REQUEST_ARTIFACT)

    if sd is not None:
        _write_envelope(
            artifact_dir / PROPOSED_STATE_DIFF_REF_ARTIFACT,
            {
                "state_diff_id": sd.state_diff_id,
                "target_surface": sd.target_surface,
                "operation_type": sd.operation_type,
                "after_candidate": sd.after_candidate,
                "schema_ref": sd.schema_ref,
                "replay_key": str(cr.replay_key),
                "idempotency_key": str(cr.replay_key),
            },
            artifact_name=PROPOSED_STATE_DIFF_REF_ARTIFACT,
            section_id=section_id,
            run_id=run_id,
        )
        chain.artifacts_written.append(PROPOSED_STATE_DIFF_REF_ARTIFACT)

    validation = gw._validate(cr, state_diffs, rollback, refresh)
    val_status = str(validation.validation_status or "FAIL")
    chain.uwg_validation_status = val_status
    _write_envelope(
        artifact_dir / STATE_DIFF_VALIDATION_ARTIFACT,
        _record_payload(validation),
        artifact_name=STATE_DIFF_VALIDATION_ARTIFACT,
        section_id=section_id,
        run_id=run_id,
    )
    chain.artifacts_written.append(STATE_DIFF_VALIDATION_ARTIFACT)

    gov_check = validate_commit_request_governance(cr)
    if not gov_check.valid:
        outcome = R1BPromotionOutcome(
            status="BLOCKED",
            record_id=candidate.record.record_id,
            durable_write_path="none",
            commit_request_id=cr.commit_request_id,
            blocked_reason_codes=gov_check.reason_codes,
            missing_contract_fields=gov_check.missing_fields,
        )
        chain.promotion_outcome = outcome
        chain.uwg_commit_or_block_status = "BLOCKED"
        _write_envelope(
            artifact_dir / BLOCKED_WRITE_RECEIPT_ARTIFACT,
            {
                "blocked_commit_receipt_id": "",
                "commit_request_ref": cr.commit_request_id,
                "blocked_reason_codes": list(gov_check.reason_codes),
                "validation_status": val_status,
                "governance_pre_uwg": True,
            },
            artifact_name=BLOCKED_WRITE_RECEIPT_ARTIFACT,
            section_id=section_id,
            run_id=run_id,
        )
        chain.artifacts_written.append(BLOCKED_WRITE_RECEIPT_ARTIFACT)
        chain.semantic_cache_persistence_status = "PARTIAL_UWG_ARTIFACTS_ONLY"
        _write_deferred_surface_status(
            artifact_dir, section_id=section_id, run_id=run_id, chain=chain
        )
        return chain

    try:
        commit_receipt, blocked_receipt, _refresh = gw.commit(
            commit_request=cr,
            state_diffs=state_diffs,
            rollback_plan=rollback,
            refresh_plan=refresh,
        )
    except ValueError as exc:
        msg = str(exc)
        missing = ("UWGCommitReceipt.l5_certification_ref",) if "l5_certification_ref" in msg else (msg,)
        outcome = R1BPromotionOutcome(
            status="BLOCKED",
            record_id=candidate.record.record_id,
            durable_write_path="none",
            commit_request_id=cr.commit_request_id,
            blocked_reason_codes=(msg,),
            missing_contract_fields=missing,
        )
        chain.promotion_outcome = outcome
        chain.uwg_commit_or_block_status = "BLOCKED"
        _write_envelope(
            artifact_dir / BLOCKED_WRITE_RECEIPT_ARTIFACT,
            {
                "commit_request_ref": cr.commit_request_id,
                "blocked_reason_codes": [msg],
                "validation_status": val_status,
            },
            artifact_name=BLOCKED_WRITE_RECEIPT_ARTIFACT,
            section_id=section_id,
            run_id=run_id,
        )
        chain.artifacts_written.append(BLOCKED_WRITE_RECEIPT_ARTIFACT)
        chain.semantic_cache_persistence_status = "PARTIAL_UWG_ARTIFACTS_ONLY"
        _write_deferred_surface_status(
            artifact_dir, section_id=section_id, run_id=run_id, chain=chain
        )
        return chain

    from apps_rg.cache.r1b_uwg_receipt_contract import build_governance_receipt_bundle

    if commit_receipt is not None:
        gov_bundle = build_governance_receipt_bundle(
            commit_request=cr,
            state_diffs=state_diffs,
            commit_receipt=commit_receipt,
        )
        outcome = R1BPromotionOutcome(
            status="ADMITTED",
            record_id=candidate.record.record_id,
            durable_write_path="UWG→L4",
            commit_request_id=cr.commit_request_id,
            uwg_commit_receipt_id=commit_receipt.commit_receipt_id,
            governance_receipt=gov_bundle.to_dict(),
        )
        chain.promotion_outcome = outcome
        chain.uwg_commit_or_block_status = "ADMITTED"
        _write_envelope(
            artifact_dir / UWG_COMMIT_RECEIPT_ARTIFACT,
            _record_payload(commit_receipt),
            artifact_name=UWG_COMMIT_RECEIPT_ARTIFACT,
            section_id=section_id,
            run_id=run_id,
        )
        chain.artifacts_written.append(UWG_COMMIT_RECEIPT_ARTIFACT)
        chain.l4_object_ref_status = "PRESENT"
        chain.semantic_cache_persistence_status = "PROVEN_UWG_CHAIN_ONLY"
    else:
        blocked_codes: tuple[str, ...] = ()
        blocked_id = ""
        missing: list[str] = []
        if blocked_receipt is not None:
            blocked_codes = tuple(blocked_receipt.blocked_reason_codes)
            blocked_id = blocked_receipt.blocked_commit_receipt_id
            if any(c.startswith("missing::") for c in blocked_codes):
                missing.extend(c for c in blocked_codes if c.startswith("missing::"))
        gov_bundle = build_governance_receipt_bundle(
            commit_request=cr,
            state_diffs=state_diffs,
            blocked_receipt=blocked_receipt,
        )
        outcome = R1BPromotionOutcome(
            status="BLOCKED",
            record_id=candidate.record.record_id,
            durable_write_path="none",
            commit_request_id=cr.commit_request_id,
            blocked_commit_receipt_id=blocked_id,
            blocked_reason_codes=blocked_codes,
            missing_contract_fields=tuple(missing),
            governance_receipt=gov_bundle.to_dict(),
        )
        chain.promotion_outcome = outcome
        chain.uwg_commit_or_block_status = "BLOCKED"
        blocked_payload: dict[str, Any] = {
            "commit_request_ref": outcome.commit_request_id,
            "blocked_commit_receipt_id": outcome.blocked_commit_receipt_id,
            "blocked_reason_codes": list(outcome.blocked_reason_codes),
            "missing_contract_fields": list(outcome.missing_contract_fields),
            "validation_status": val_status,
        }
        if blocked_receipt is not None:
            blocked_payload["uwg_blocked_commit_receipt"] = _record_payload(blocked_receipt)
        if outcome.governance_receipt:
            blocked_payload["governance_receipt"] = outcome.governance_receipt
        _write_envelope(
            artifact_dir / BLOCKED_WRITE_RECEIPT_ARTIFACT,
            blocked_payload,
            artifact_name=BLOCKED_WRITE_RECEIPT_ARTIFACT,
            section_id=section_id,
            run_id=run_id,
        )
        chain.artifacts_written.append(BLOCKED_WRITE_RECEIPT_ARTIFACT)
        chain.semantic_cache_persistence_status = "PARTIAL_UWG_ARTIFACTS_ONLY"

    _write_envelope(
        artifact_dir / L4_NAMESPACE_OBJECT_REF_ARTIFACT,
        {
            "target_l4_namespace": R1B_UWG_TARGET_SURFACE,
            "target_state_object": str(sd.after_candidate) if sd else "",
            "affected_state_surfaces": list(cr.affected_state_surfaces),
            "state_diff_refs": list(cr.state_diff_refs),
            "commit_request_ref": cr.commit_request_id,
            "uwg_commit_receipt_id": outcome.uwg_commit_receipt_id or None,
            "blocked_commit_receipt_id": outcome.blocked_commit_receipt_id or None,
        },
        artifact_name=L4_NAMESPACE_OBJECT_REF_ARTIFACT,
        section_id=section_id,
        run_id=run_id,
    )
    chain.artifacts_written.append(L4_NAMESPACE_OBJECT_REF_ARTIFACT)
    if outcome.status == "ADMITTED":
        chain.l4_object_ref_status = "PRESENT"

    _write_deferred_surface_status(
        artifact_dir, section_id=section_id, run_id=run_id, chain=chain
    )
    return chain


def emit_section_r1b_governed_receipt_chain(
    *,
    artifact_dir: Path,
    section_id: str,
    run_id: str,
    raw_request: dict[str, Any] | None = None,
    gateway: Any | None = None,
    attempt_uwg_promotion: bool = True,
) -> R1BGovernedReceiptChainOutcome:
    """Emit governed R1B receipt chain into ``artifact_dir`` (no Chroma, no store projection)."""
    x3_code = _load_x3_code(artifact_dir)
    manifest = _read_json(artifact_dir / "run_manifest.json")
    req = dict(raw_request or _raw_request_from_run_dir(artifact_dir))
    trace_root = f"trace:{run_id}"

    if x3_code not in X3_FINISH_ALLOWED:
        chain = R1BGovernedReceiptChainOutcome(
            commit_request_status="NOT_EMITTED",
            semantic_cache_persistence_status="NOT_APPLICABLE",
            uwg_validation_status="NOT_RUN",
            uwg_commit_or_block_status="NOT_RUN",
            l4_object_ref_status="NOT_RUN",
            read_surface_refresh_status="NOT_APPLICABLE",
            chroma_projection_status="MISSING",
            reason=REASON_X3_NOT_X3C,
            x3_code=x3_code,
            section_id=section_id,
            run_id=run_id,
            whole_run_id=str(manifest.get("run_id") or run_id),
            trace_root=trace_root,
        )
        (artifact_dir / GOVERNED_CHAIN_MANIFEST).write_text(
            json.dumps(chain.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return chain

    assessment = evaluate_post_exit_ingestion(
        run_dir=artifact_dir,
        raw_request=req,
    )
    if not assessment.get("admissible") and not assessment.get("cache_admissible"):
        reason = str(assessment.get("non_admissible_reason") or REASON_ROUTE_NOT_ELIGIBLE)
        chain = R1BGovernedReceiptChainOutcome(
            commit_request_status="NOT_EMITTED",
            semantic_cache_persistence_status="NOT_APPLICABLE",
            uwg_validation_status="NOT_RUN",
            uwg_commit_or_block_status="NOT_RUN",
            l4_object_ref_status="NOT_RUN",
            read_surface_refresh_status="NOT_APPLICABLE",
            chroma_projection_status="MISSING",
            reason=reason,
            x3_code=x3_code,
            section_id=section_id,
            run_id=run_id,
            whole_run_id=str(manifest.get("run_id") or run_id),
            trace_root=trace_root,
        )
        (artifact_dir / GOVERNED_CHAIN_MANIFEST).write_text(
            json.dumps(chain.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return chain

    if not attempt_uwg_promotion:
        chain = R1BGovernedReceiptChainOutcome(
            commit_request_status="NOT_EMITTED",
            semantic_cache_persistence_status="NOT_PROVEN",
            uwg_validation_status="NOT_RUN",
            uwg_commit_or_block_status="NOT_RUN",
            l4_object_ref_status="NOT_RUN",
            read_surface_refresh_status="NOT_APPLICABLE",
            chroma_projection_status="MISSING",
            reason="uwg_promotion_skipped",
            x3_code=x3_code,
            section_id=section_id,
            run_id=run_id,
        )
        (artifact_dir / GOVERNED_CHAIN_MANIFEST).write_text(
            json.dumps(chain.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return chain

    from apps_rg.cache.r1b_models import HistoricalIntentRecord, HistoricalOutputChunk

    record = HistoricalIntentRecord.from_dict(assessment["record"])
    chunks = [HistoricalOutputChunk.from_dict(c) for c in assessment.get("chunks") or []]
    candidate = build_r1b_promotion_candidate(
        record=record,
        chunks=chunks,
        post_exit_eligibility=assessment,
        run_dir=artifact_dir,
    )
    chain = _materialize_uwg_receipts(
        artifact_dir,
        candidate=candidate,
        section_id=section_id,
        run_id=run_id,
        manifest=manifest,
        gateway=gateway,
    )
    (artifact_dir / GOVERNED_CHAIN_MANIFEST).write_text(
        json.dumps(chain.to_dict(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return chain


__all__ = [
    "CHROMA_PROJECTION_DEFERRED_ARTIFACT",
    "COMMIT_REQUEST_ARTIFACT",
    "GOVERNED_CHAIN_MANIFEST",
    "R1BGovernedReceiptChainOutcome",
    "READ_SURFACE_DEFERRED_ARTIFACT",
    "REASON_X3_NOT_X3C",
    "emit_section_r1b_governed_receipt_chain",
]
