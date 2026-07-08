"""W8 — post-Exit-only R1B ingestion orchestration (after x3_disposition is materialized)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from apps_rg.cache.r1b_ingest import (
    build_intent_record_from_run,
    chunks_from_output_list,
)
from apps_rg.cache.r1b_post_exit_eligibility import (
    apply_post_exit_verdict_to_record,
    assess_post_exit_ingestion_eligibility,
    load_post_exit_metadata,
)
from apps_rg.cache.r1b_semantic_chunk_builder import (
    build_chunk_rows_from_run_dir,
    detect_ingest_profile,
)
from apps_rg.cache.r1b_store import R1BSemanticCacheStore, default_store_root


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
    write_fixture_mirror: bool = False,
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
    from apps_rg.cache.r1b_ingest import _read_json
    from apps_rg.cache.r1b_models import HistoricalIntentRecord, HistoricalOutputChunk
    from apps_rg.cache.r1b_uwg_promotion import build_r1b_promotion_candidate

    record = HistoricalIntentRecord.from_dict(record_dict)
    chunks = [HistoricalOutputChunk.from_dict(c) for c in assessment.get("chunks") or []]
    if not record.cache_admissible:
        if write_fixture_mirror:
            st.write_intent(record)
        return None

    manifest = _read_json(run_dir / "run_manifest.json") or {}
    section_id = str(manifest.get("section_id") or "integrated_whole_run")
    run_id = str(manifest.get("run_id") or run_dir.name)

    from apps_rg.cache.r1b_governed_receipt_emission import emit_section_r1b_governed_receipt_chain

    chain = emit_section_r1b_governed_receipt_chain(
        artifact_dir=run_dir,
        section_id=section_id,
        run_id=run_id,
        raw_request=raw_request,
        gateway=gateway,
    )
    if chain.promotion_outcome and chain.promotion_outcome.status == "ADMITTED":
        from apps_rg.cache.r1b_derived_index import project_durable_to_derived_index
        from apps_rg.cache.r1b_uwg_promotion import write_uwg_admitted_projection

        candidate = build_r1b_promotion_candidate(
            record=record,
            chunks=chunks,
            post_exit_eligibility=assessment,
            run_dir=run_dir,
        )
        write_uwg_admitted_projection(
            projection_root=st.root,
            candidate=candidate,
            outcome=chain.promotion_outcome,
        )
        project_durable_to_derived_index(st.root)
        if write_fixture_mirror:
            st.write_intent(record)
            for ch in chunks:
                st.write_chunk(ch)
        return record.record_id
    if write_fixture_mirror:
        st.write_intent(record)
    return record.record_id


def ingest_post_exit_after_run(
    *,
    artifact_dir: Path,
    raw_request: dict[str, Any],
    runs_dir: Path | str,
    record_id: str | None = None,
    write_fixture_mirror: bool = False,
) -> str | None:
    """Entry point for CLI / pipeline — requires x3_disposition.json in artifact_dir."""
    store = R1BSemanticCacheStore(Path(runs_dir) if runs_dir else default_store_root())
    return ingest_post_exit_from_run_dir(
        run_dir=artifact_dir,
        raw_request=raw_request,
        store=store,
        record_id=record_id,
        write_fixture_mirror=write_fixture_mirror,
    )


__all__ = [
    "build_chunk_rows_from_run_dir",
    "detect_ingest_profile",
    "evaluate_post_exit_ingestion",
    "ingest_post_exit_after_run",
    "ingest_post_exit_from_run_dir",
]
