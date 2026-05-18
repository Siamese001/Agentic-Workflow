"""Build ROLE_TARGET_RUN R1B records from whole-run / section artifacts."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dataclasses import replace

from apps_rg.cache.r1b_compatibility import CompatibilityVerdict, assess_intent_record_admissibility
from apps_rg.cache.r1b_constants import (
    APP_ID_APPS_RG,
    CACHE_GRAIN_ROLE_TARGET_RUN,
    CHUNK_TYPE_CLAIM_LEDGER,
    CHUNK_TYPE_FINAL_RESUME,
    CHUNK_TYPE_SECTION_PROOF,
    NON_ADMISSIBLE_RUNTIME_STATUSES,
)
from apps_rg.cache.r1b_intent_vector import intent_text_from_request, normalized_intent_digest, vector_ref_relative
from apps_rg.cache.r1b_models import HistoricalIntentRecord, HistoricalOutputChunk
from apps_rg.cache.r1b_store import R1BSemanticCacheStore


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_hex(text: str | bytes) -> str:
    data = text.encode("utf-8") if isinstance(text, str) else text
    return hashlib.sha256(data).hexdigest()


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return raw if isinstance(raw, dict) else None


def _section_chunk_type(section_id: str) -> str:
    return f"{section_id}_output"


def build_intent_record_from_run(
    *,
    raw_request: dict[str, Any],
    run_context: dict[str, Any],
    metadata: dict[str, Any] | None = None,
) -> HistoricalIntentRecord:
    meta = metadata or {}
    intent_text = intent_text_from_request(raw_request)
    digest = normalized_intent_digest(intent_text)
    record_id = str(run_context.get("record_id") or f"hir_{uuid.uuid4().hex[:16]}")
    x3 = str(run_context.get("x3_disposition") or meta.get("x3_disposition") or "").strip()
    proof_eligible = bool(run_context.get("proof_eligible", meta.get("proof_eligible", False)))
    runtime_status = str(
        run_context.get("runtime_generation_status") or meta.get("runtime_generation_status") or ""
    ).strip()
    provisional = HistoricalIntentRecord(
        record_id=record_id,
        app_id=APP_ID_APPS_RG,
        cache_grain=CACHE_GRAIN_ROLE_TARGET_RUN,
        request_intent_text=intent_text,
        normalized_intent_digest=digest,
        request_intent_vector_ref=vector_ref_relative(record_id),
        source_run_id=str(run_context.get("run_id") or record_id),
        target_company=str(raw_request.get("target_company") or ""),
        target_role=str(raw_request.get("target_role") or ""),
        job_family=str(meta.get("job_family") or ""),
        jd_digest=str(raw_request.get("jd_hash") or meta.get("jd_digest") or ""),
        briefing_digest=str(raw_request.get("brief_hash") or meta.get("briefing_digest") or ""),
        srfs_digest=str(meta.get("srfs_digest") or ""),
        proof_pool_digest=str(meta.get("proof_pool_digest") or ""),
        skills_ledger_digest=str(meta.get("skills_ledger_digest") or ""),
        base_resume_digest=str(raw_request.get("resume_hash") or meta.get("base_resume_digest") or ""),
        final_resume_digest=str(meta.get("final_resume_digest") or ""),
        prompt_profile_hash=str(meta.get("prompt_profile_hash") or ""),
        model_profile_hash=str(meta.get("model_profile_hash") or ""),
        gate_profile_hash=str(meta.get("gate_profile_hash") or ""),
        x3_disposition=x3,
        proof_eligible=proof_eligible,
        cache_admissible=False,
        generated_at_utc=str(run_context.get("generated_at_utc") or _utc_now()),
        non_admissible_reason="pending_chunk_assessment",
    )
    return provisional


def finalize_intent_admissibility(
    record: HistoricalIntentRecord,
    chunks: list[HistoricalOutputChunk],
    *,
    runtime_generation_status: str = "",
) -> HistoricalIntentRecord:
    """Set cache_admissible after child chunks are attached."""
    verdict = assess_intent_record_admissibility(
        record,
        chunks=chunks,
        runtime_generation_status=runtime_generation_status,
    )
    if runtime_generation_status in NON_ADMISSIBLE_RUNTIME_STATUSES:
        verdict = CompatibilityVerdict(
            admissible=False,
            reason=f"runtime_status={runtime_generation_status}",
            checks=verdict.checks,
        )
    if not record.proof_eligible:
        verdict = CompatibilityVerdict(admissible=False, reason="proof_eligible=false", checks=verdict.checks)
    return replace(
        record,
        cache_admissible=verdict.admissible,
        non_admissible_reason="" if verdict.admissible else verdict.reason,
    )


def build_intent_record_complete(
    *,
    raw_request: dict[str, Any],
    run_context: dict[str, Any],
    metadata: dict[str, Any] | None,
    chunks: list[HistoricalOutputChunk],
) -> HistoricalIntentRecord:
    provisional = build_intent_record_from_run(
        raw_request=raw_request,
        run_context=run_context,
        metadata=metadata,
    )
    runtime_status = str(
        run_context.get("runtime_generation_status") or (metadata or {}).get("runtime_generation_status") or ""
    )
    return finalize_intent_admissibility(
        provisional,
        chunks,
        runtime_generation_status=runtime_status,
    )


def chunks_from_output_list(
    *,
    parent_intent_record_id: str,
    output_chunks: list[dict[str, Any]],
    generated_at_utc: str | None = None,
) -> list[HistoricalOutputChunk]:
    ts = generated_at_utc or _utc_now()
    out: list[HistoricalOutputChunk] = []
    for i, raw in enumerate(output_chunks):
        if not isinstance(raw, dict):
            continue
        chunk_type = str(raw.get("chunk_type") or raw.get("type") or "section_proof_summary")
        section_id = str(raw.get("section_id") or "")
        text = str(raw.get("chunk_text") or raw.get("text") or "")
        digest = str(raw.get("chunk_digest") or _sha256_hex(text or json.dumps(raw, sort_keys=True)))
        cid = str(raw.get("chunk_id") or f"hoc_{parent_intent_record_id[:8]}_{i:03d}")
        out.append(
            HistoricalOutputChunk(
                chunk_id=cid,
                parent_intent_record_id=parent_intent_record_id,
                chunk_type=chunk_type,
                section_id=section_id,
                chunk_text=text[:8000] if text else "",
                chunk_digest=digest,
                chunk_vector_ref=str(raw.get("chunk_vector_ref") or ""),
                artifact_ref=str(raw.get("artifact_ref") or ""),
                artifact_digest=str(raw.get("artifact_digest") or ""),
                source_fact_ids=list(raw.get("source_fact_ids") or []),
                proof_pool_refs=list(raw.get("proof_pool_refs") or []),
                support_status=str(raw.get("support_status") or "UNKNOWN"),
                x2_status=str(raw.get("x2_status") or ""),
                x1d_status=str(raw.get("x1d_status") or ""),
                section_prompt_hash=str(raw.get("section_prompt_hash") or ""),
                section_model_profile_hash=str(raw.get("section_model_profile_hash") or ""),
                generated_at_utc=ts,
            )
        )
    return out


def ingest_run_artifact_dir(
    *,
    run_dir: Path,
    raw_request: dict[str, Any],
    store: R1BSemanticCacheStore,
) -> str | None:
    """Ingest only after Exit metadata exists (W8 post-Exit gate)."""
    from apps_rg.cache.r1b_post_exit_ingest import ingest_post_exit_from_run_dir

    return ingest_post_exit_from_run_dir(
        run_dir=run_dir,
        raw_request=raw_request,
        store=store,
    )


__all__ = [
    "build_intent_record_complete",
    "build_intent_record_from_run",
    "chunks_from_output_list",
    "finalize_intent_admissibility",
    "ingest_run_artifact_dir",
]
