"""Hermetic R1B test fixtures for current apps_rg cache contracts."""

from __future__ import annotations

import json
from pathlib import Path

from apps_rg.cache.r1b_constants import (
    CACHE_GRAIN_ROLE_TARGET_RUN,
    CHUNK_TYPE_EXEC_SUMMARY,
    CHUNK_TYPE_FINAL_RESUME,
    CHUNK_TYPE_SECTION_PROOF,
)
from apps_rg.cache.r1b_intent_vector import (
    intent_text_from_request,
    normalized_intent_digest,
    vector_ref_relative,
)
from apps_rg.cache.r1b_models import HistoricalIntentRecord, HistoricalOutputChunk
from apps_rg.cache.r1b_store import R1BSemanticCacheStore

PROMPT_PROFILE_HASH = "prompt_profile_w7_v1"
GATE_PROFILE_HASH = "gate_profile_w7_v1"
GENERATED_AT_UTC = "2026-05-20T00:00:00+00:00"


def r1b_match_request() -> dict[str, str]:
    return {
        "target_company": "Synthetic Enterprise Corp.",
        "target_role": "SVP Engineering",
        "generation_mode": "strategic_tailor",
        "resume_hash": "fixture_resume_digest",
        "jd_hash": "fixture_jd_digest",
        "brief_hash": "fixture_brief_digest",
    }


def build_admissible_intent_record(
    *,
    record_id: str = "hir_w7_admissible_001",
    source_run_id: str = "run_w7_admissible",
    raw_request: dict[str, str] | None = None,
    prompt_profile_hash: str = PROMPT_PROFILE_HASH,
    gate_profile_hash: str = GATE_PROFILE_HASH,
) -> HistoricalIntentRecord:
    request = raw_request or r1b_match_request()
    intent_text = intent_text_from_request(request)
    digest = normalized_intent_digest(intent_text)
    return HistoricalIntentRecord.from_dict(
        {
            "record_id": record_id,
            "app_id": "apps_rg",
            "cache_grain": CACHE_GRAIN_ROLE_TARGET_RUN,
            "request_intent_text": intent_text,
            "normalized_intent_digest": digest,
            "request_intent_vector_ref": vector_ref_relative(record_id),
            "source_run_id": source_run_id,
            "target_company": request["target_company"],
            "target_role": request["target_role"],
            "job_family": "",
            "jd_digest": request["jd_hash"],
            "briefing_digest": request["brief_hash"],
            "srfs_digest": "",
            "proof_pool_digest": "",
            "skills_ledger_digest": "",
            "base_resume_digest": request["resume_hash"],
            "final_resume_digest": "fixture_final_resume_digest",
            "prompt_profile_hash": prompt_profile_hash,
            "model_profile_hash": "",
            "gate_profile_hash": gate_profile_hash,
            "x3_disposition": "X3_ALLOW",
            "proof_eligible": True,
            "cache_admissible": True,
            "generated_at_utc": GENERATED_AT_UTC,
        }
    )


def build_admissible_output_chunks(parent_intent_record_id: str) -> list[HistoricalOutputChunk]:
    base = {
        "parent_intent_record_id": parent_intent_record_id,
        "chunk_digest": "",
        "chunk_vector_ref": "",
        "artifact_digest": "",
        "source_fact_ids": ["fact_fixture_001"],
        "proof_pool_refs": [],
        "support_status": "SUPPORTED",
        "x2_status": "PASS",
        "x1d_status": "PASS",
        "section_prompt_hash": PROMPT_PROFILE_HASH,
        "section_model_profile_hash": "",
        "generated_at_utc": GENERATED_AT_UTC,
    }
    rows = [
        {
            **base,
            "chunk_id": "final_resume",
            "chunk_type": CHUNK_TYPE_FINAL_RESUME,
            "section_id": "assembly",
            "chunk_text": json.dumps({"sections": ["executive_summary"]}),
            "artifact_ref": "outputs/generated_resume.json",
        },
        {
            **base,
            "chunk_id": "sec_executive_summary",
            "chunk_type": CHUNK_TYPE_EXEC_SUMMARY,
            "section_id": "executive_summary",
            "chunk_text": "Fixture executive summary with proof-bound platform leadership evidence.",
            "artifact_ref": "lanes/executive_summary/resume_display_text.txt",
        },
        {
            **base,
            "chunk_id": "sec_executive_summary_proof",
            "chunk_type": CHUNK_TYPE_SECTION_PROOF,
            "section_id": "executive_summary",
            "chunk_text": json.dumps(
                {
                    "proof_eligible": True,
                    "runtime_generation_status": "REAL_LLM",
                    "ingestion_phase": "post_exit_only",
                },
                sort_keys=True,
            ),
            "artifact_ref": "lanes/executive_summary",
        },
    ]
    return [HistoricalOutputChunk.from_dict(row) for row in rows]


def seed_admissible_r1b_store(
    store: R1BSemanticCacheStore,
    *,
    record_id: str = "hir_w7_admissible_001",
) -> tuple[HistoricalIntentRecord, list[HistoricalOutputChunk]]:
    record = build_admissible_intent_record(record_id=record_id)
    chunks = build_admissible_output_chunks(record.record_id)
    store.write_intent(record)
    for chunk in chunks:
        store.write_chunk(chunk)
    return record, chunks


def write_post_exit_artifacts(run_dir: Path, record: HistoricalIntentRecord) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "x3_disposition.json").write_text(
        json.dumps(
            {
                "x3_code": "X3_ALLOW",
                "proof_eligible": True,
                "runtime_generation_status": "REAL_LLM",
                "proceed_to_runtime": True,
                "pass": True,
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "run_manifest.json").write_text(
        json.dumps(
            {
                "run_id": record.source_run_id,
                "section_id": "integrated_whole_run",
                "proof_eligible": True,
                "runtime_generation_status": "REAL_LLM",
                "prompt_profile_hash": record.prompt_profile_hash,
                "gate_profile_hash": record.gate_profile_hash,
            }
        ),
        encoding="utf-8",
    )


def build_post_exit_eligibility(
    record: HistoricalIntentRecord,
    chunks: list[HistoricalOutputChunk],
) -> dict[str, object]:
    return {
        "admissible": True,
        "cache_admissible": True,
        "non_admissible_reason": "",
        "record": record.to_dict(),
        "chunks": [chunk.to_dict() for chunk in chunks],
        "exit_metadata": {
            "source_run_id": record.source_run_id,
            "x3_disposition": "X3_ALLOW",
            "proof_eligible": True,
            "runtime_generation_status": "REAL_LLM",
            "exit_artifact_present": True,
        },
    }
