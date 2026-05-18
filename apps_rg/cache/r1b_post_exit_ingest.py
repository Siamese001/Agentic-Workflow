"""W8 — post-Exit-only R1B ingestion orchestration (after x3_disposition is materialized)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps_rg.cache.r1b_ingest import (
    build_intent_record_from_run,
    chunks_from_output_list,
)
from apps_rg.cache.r1b_post_exit_eligibility import (
    POST_EXIT_INGESTION_PHASE,
    apply_post_exit_verdict_to_record,
    assess_post_exit_ingestion_eligibility,
    load_post_exit_metadata,
)
from apps_rg.cache.r1b_store import R1BSemanticCacheStore, default_store_root


def build_chunk_rows_from_run_dir(run_dir: Path, *, manifest: dict[str, Any]) -> list[dict[str, Any]]:
    from apps_rg.cache.r1b_constants import (
        CHUNK_TYPE_CLAIM_LEDGER,
        CHUNK_TYPE_FINAL_RESUME,
        CHUNK_TYPE_SECTION_PROOF,
    )
    from apps_rg.cache.r1b_ingest import _read_json, _section_chunk_type

    chunk_rows: list[dict[str, Any]] = []
    section_id = str(manifest.get("section_id") or "")
    if (run_dir / "generated_resume.json").is_file():
        text = (run_dir / "generated_resume.json").read_text(encoding="utf-8")[:8000]
        chunk_rows.append(
            {
                "chunk_type": CHUNK_TYPE_FINAL_RESUME,
                "chunk_text": text,
                "artifact_ref": str(run_dir / "generated_resume.json"),
            }
        )
    if (run_dir / "l2_output.json").is_file():
        chunk_rows.append(
            {
                "chunk_type": _section_chunk_type(section_id) if section_id else CHUNK_TYPE_SECTION_PROOF,
                "section_id": section_id,
                "artifact_ref": str(run_dir / "l2_output.json"),
                "x2_status": "PASS"
                if (_read_json(run_dir / "x2_gate_outputs.json") or {}).get("x2_failed", 1) == 0
                else "FAIL",
            }
        )
    if (run_dir / "canonical_claim_ledger_v2.json").is_file():
        chunk_rows.append(
            {
                "chunk_type": CHUNK_TYPE_CLAIM_LEDGER,
                "section_id": section_id,
                "artifact_ref": str(run_dir / "canonical_claim_ledger_v2.json"),
            }
        )
    proof_eligible = bool(manifest.get("proof_eligible", False))
    runtime_status = str(manifest.get("runtime_generation_status") or "")
    if chunk_rows:
        chunk_rows.append(
            {
                "chunk_type": CHUNK_TYPE_SECTION_PROOF,
                "section_id": section_id,
                "artifact_ref": str(run_dir),
                "chunk_text": json.dumps(
                    {
                        "run_id": manifest.get("run_id"),
                        "proof_eligible": proof_eligible,
                        "runtime_generation_status": runtime_status,
                        "ingestion_phase": POST_EXIT_INGESTION_PHASE,
                    },
                    sort_keys=True,
                ),
            }
        )
    return chunk_rows


def evaluate_post_exit_ingestion(
    *,
    run_dir: Path,
    raw_request: dict[str, Any],
    record_id: str | None = None,
) -> dict[str, Any]:
    """Assess eligibility without persisting (for fixtures and tests)."""
    from apps_rg.cache.r1b_ingest import _read_json

    exit_meta = load_post_exit_metadata(run_dir)
    manifest = _read_json(run_dir / "run_manifest.json") or {}
    run_context = {
        "record_id": record_id or f"hir_{exit_meta.source_run_id}",
        "run_id": exit_meta.source_run_id,
        "post_exit_ingestion": True,
        "x3_disposition": exit_meta.x3_disposition,
        "proof_eligible": exit_meta.proof_eligible if exit_meta.proof_eligible is not None else False,
        "runtime_generation_status": exit_meta.runtime_generation_status,
    }
    meta = {
        "x3_disposition": exit_meta.x3_disposition,
        "proof_eligible": run_context["proof_eligible"],
        "runtime_generation_status": exit_meta.runtime_generation_status,
        "prompt_profile_hash": str(manifest.get("prompt_profile_hash") or "unknown"),
        "gate_profile_hash": str(manifest.get("gate_profile_hash") or "unknown"),
        "jd_digest": str(raw_request.get("jd_hash") or ""),
        "base_resume_digest": str(raw_request.get("resume_hash") or ""),
    }
    record = build_intent_record_from_run(
        raw_request=raw_request,
        run_context=run_context,
        metadata=meta,
    )
    chunk_rows = build_chunk_rows_from_run_dir(run_dir, manifest=manifest)
    chunks = chunks_from_output_list(
        parent_intent_record_id=record.record_id,
        output_chunks=chunk_rows,
    )
    verdict = assess_post_exit_ingestion_eligibility(record, chunks, exit_meta=exit_meta)
    record = apply_post_exit_verdict_to_record(record, verdict)
    return {
        **verdict.to_dict(),
        "record": record.to_dict(),
        "chunk_count": len(chunks),
        "chunks": [c.to_dict() for c in chunks],
        "exit_metadata": {
            "x3_disposition": exit_meta.x3_disposition,
            "proof_eligible": exit_meta.proof_eligible,
            "runtime_generation_status": exit_meta.runtime_generation_status,
            "exit_artifact_present": exit_meta.exit_artifact_present,
        },
    }


def ingest_post_exit_from_run_dir(
    *,
    run_dir: Path,
    raw_request: dict[str, Any],
    store: R1BSemanticCacheStore | None = None,
    record_id: str | None = None,
    gateway: Any | None = None,
) -> str | None:
    """Persist R1B via UWG admission after Exit; fixture mirror optional for tests."""
    if not (run_dir / "x3_disposition.json").is_file():
        return None
    assessment = evaluate_post_exit_ingestion(
        run_dir=run_dir,
        raw_request=raw_request,
        record_id=record_id,
    )
    st = store or R1BSemanticCacheStore(default_store_root())
    record_dict = assessment["record"]
    from apps_rg.cache.r1b_models import HistoricalIntentRecord, HistoricalOutputChunk
    from apps_rg.cache.r1b_uwg_promotion import (
        build_r1b_promotion_candidate,
        promote_and_project_r1b_cache,
    )

    record = HistoricalIntentRecord.from_dict(record_dict)
    chunks = [HistoricalOutputChunk.from_dict(c) for c in assessment.get("chunks") or []]
    if not record.cache_admissible:
        st.write_intent(record)
        return None

    candidate = build_r1b_promotion_candidate(
        record=record,
        chunks=chunks,
        post_exit_eligibility=assessment,
        run_dir=run_dir,
    )
    if gateway is None:
        from apps_rg.cache.r1b_uwg_gateway_shim import default_r1b_promotion_gateway

        gateway = default_r1b_promotion_gateway()
    outcome = promote_and_project_r1b_cache(
        candidate=candidate,
        projection_root=st.root,
        fixture_store=st,
        gateway=gateway,
        mirror_fixture_on_blocked=True,
    )
    if outcome.status == "ADMITTED":
        return record.record_id
    return record.record_id if outcome.fixture_mirror_written else None


def ingest_post_exit_after_run(
    *,
    artifact_dir: Path,
    raw_request: dict[str, Any],
    runs_dir: Path | str,
    record_id: str | None = None,
) -> str | None:
    """Entry point for CLI / pipeline — requires x3_disposition.json in artifact_dir."""
    store = R1BSemanticCacheStore(Path(runs_dir) if runs_dir else default_store_root())
    return ingest_post_exit_from_run_dir(
        run_dir=artifact_dir,
        raw_request=raw_request,
        store=store,
        record_id=record_id,
    )


__all__ = [
    "evaluate_post_exit_ingestion",
    "ingest_post_exit_after_run",
    "ingest_post_exit_from_run_dir",
]
