from __future__ import annotations

from apps_rg.cache.r1b_constants import (
    APP_ID_APPS_RG,
    CACHE_GRAIN_ROLE_TARGET_RUN,
    CHUNK_TYPE_FINAL_RESUME,
    CHUNK_TYPE_HEADLINE,
    CHUNK_TYPE_SECTION_PROOF,
)
from apps_rg.cache.r1b_ingest import (
    build_intent_record_from_run,
    chunks_from_output_list,
    finalize_intent_admissibility,
)


def _raw_request() -> dict[str, str]:
    return {
        "target_company": "Brown & Brown",
        "target_role": "SVP IT Strategy",
        "generation_mode": "strategic_tailor",
        "jd_hash": "jd_digest_wave1",
        "brief_hash": "brief_digest_wave1",
        "resume_hash": "resume_digest_wave1",
    }


def _run_context(*, proof_eligible: bool = True, status: str = "REAL_LLM") -> dict[str, object]:
    return {
        "record_id": "hir_wave1_run",
        "run_id": "run_wave1",
        "x3_disposition": "X3_ALLOW",
        "proof_eligible": proof_eligible,
        "runtime_generation_status": status,
        "generated_at_utc": "2026-05-20T00:00:00+00:00",
    }


def test_build_intent_record_from_run_preserves_role_target_run_identity() -> None:
    record = build_intent_record_from_run(
        raw_request=_raw_request(),
        run_context=_run_context(),
        metadata={
            "job_family": "platform",
            "prompt_profile_hash": "prompt_hash",
            "gate_profile_hash": "gate_hash",
            "model_profile_hash": "model_hash",
            "final_resume_digest": "final_digest",
        },
    )

    assert record.record_id == "hir_wave1_run"
    assert record.app_id == APP_ID_APPS_RG
    assert record.cache_grain == CACHE_GRAIN_ROLE_TARGET_RUN
    assert record.request_intent_text == (
        "apps_rg|role_target_run|brown & brown|svp it strategy|strategic_tailor|"
        "jd_digest_wave1|brief_digest_wave1|resume_digest_wave1"
    )
    assert record.request_intent_vector_ref == "vectors/hir_wave1_run.json"
    assert record.source_run_id == "run_wave1"
    assert record.target_company == "Brown & Brown"
    assert record.target_role == "SVP IT Strategy"
    assert record.proof_eligible is True
    assert record.cache_admissible is False
    assert record.non_admissible_reason == "pending_chunk_assessment"


def test_chunks_from_output_list_skips_bad_rows_truncates_text_and_links_parent() -> None:
    chunks = chunks_from_output_list(
        parent_intent_record_id="hir_wave1_run",
        output_chunks=[
            "not a row",
            {
                "type": CHUNK_TYPE_HEADLINE,
                "section_id": "headline",
                "text": "x" * 8100,
                "source_fact_ids": ("F1", "F2"),
                "support_status": "SUPPORTED",
            },
        ],
        generated_at_utc="2026-05-20T00:00:00+00:00",
    )

    assert len(chunks) == 1
    chunk = chunks[0]
    assert chunk.chunk_id == "hoc_hir_wave_001"
    assert chunk.parent_intent_record_id == "hir_wave1_run"
    assert chunk.chunk_type == CHUNK_TYPE_HEADLINE
    assert chunk.section_id == "headline"
    assert len(chunk.chunk_text) == 8000
    assert chunk.source_fact_ids == ["F1", "F2"]
    assert chunk.independent_cache_identity is False


def test_finalize_intent_admissibility_allows_real_proof_eligible_complete_run() -> None:
    record = build_intent_record_from_run(
        raw_request=_raw_request(),
        run_context=_run_context(),
        metadata={"prompt_profile_hash": "prompt_hash", "gate_profile_hash": "gate_hash"},
    )
    chunks = chunks_from_output_list(
        parent_intent_record_id=record.record_id,
        output_chunks=[
            {"chunk_type": CHUNK_TYPE_FINAL_RESUME, "text": "final resume"},
            {"chunk_type": CHUNK_TYPE_SECTION_PROOF, "text": "section proof"},
            {"chunk_type": CHUNK_TYPE_HEADLINE, "section_id": "headline", "text": "Senior platform leader"},
        ],
        generated_at_utc=record.generated_at_utc,
    )

    finalized = finalize_intent_admissibility(
        record,
        chunks,
        runtime_generation_status="REAL_LLM",
    )

    assert finalized.cache_admissible is True
    assert finalized.non_admissible_reason == ""


def test_finalize_intent_admissibility_blocks_mocked_or_not_proof_eligible_runs() -> None:
    chunks = chunks_from_output_list(
        parent_intent_record_id="hir_wave1_run",
        output_chunks=[
            {"chunk_type": CHUNK_TYPE_FINAL_RESUME, "text": "final resume"},
            {"chunk_type": CHUNK_TYPE_SECTION_PROOF, "text": "section proof"},
            {"chunk_type": CHUNK_TYPE_HEADLINE, "section_id": "headline", "text": "Senior platform leader"},
        ],
    )
    proof_record = build_intent_record_from_run(
        raw_request=_raw_request(),
        run_context=_run_context(),
        metadata={"prompt_profile_hash": "prompt_hash", "gate_profile_hash": "gate_hash"},
    )
    not_proof_record = build_intent_record_from_run(
        raw_request=_raw_request(),
        run_context=_run_context(proof_eligible=False),
        metadata={"prompt_profile_hash": "prompt_hash", "gate_profile_hash": "gate_hash"},
    )

    mocked = finalize_intent_admissibility(proof_record, chunks, runtime_generation_status="MOCKED")
    not_proof = finalize_intent_admissibility(
        not_proof_record,
        chunks,
        runtime_generation_status="REAL_LLM",
    )

    assert mocked.cache_admissible is False
    assert mocked.non_admissible_reason == "runtime_status=MOCKED"
    assert not_proof.cache_admissible is False
    assert not_proof.non_admissible_reason == "proof_eligible=false"
