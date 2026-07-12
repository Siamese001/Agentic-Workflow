"""W8 — post-Exit R1B ingestion eligibility (apps_rg only)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.cache.r1b_adapter import AppsRgR1BCacheAdapter
from apps_rg.cache.r1b_constants import (
    CHUNK_TYPE_EXEC_SUMMARY,
    CHUNK_TYPE_FINAL_RESUME,
    CHUNK_TYPE_SECTION_PROOF,
)
from apps_rg.cache.r1b_post_exit_eligibility import (
    POST_EXIT_INGESTION_PHASE,
    assess_post_exit_ingestion_eligibility,
    load_post_exit_metadata,
)
from apps_rg.cache.r1b_post_exit_ingest import (
    evaluate_post_exit_ingestion,
    ingest_post_exit_from_run_dir,
)
from apps_rg.cache.r1b_store import R1BSemanticCacheStore


def _raw_request() -> dict:
    return {
        "target_company": "Acme",
        "target_role": "VP Engineering",
        "generation_mode": "strategic_tailor",
        "resume_hash": "resume_digest_w8",
        "jd_hash": "jd_digest_w8",
        "brief_hash": "brief_digest_w8",
    }


def _write_exit_bundle(
    run_dir: Path,
    *,
    x3_code: str = "X3C",
    proof_eligible: bool = True,
    runtime_status: str = "REAL_LLM",
    include_final_resume: bool = True,
    include_section_output: bool = True,
    include_proof_chunk: bool = True,
    prompt_hash: str = "prompt_w8",
    gate_hash: str = "gate_w8",
    write_x3: bool = True,
) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "run_manifest.json").write_text(
        json.dumps(
            {
                "run_id": "run_w8_fixture",
                "section_id": "executive_summary",
                "proof_eligible": proof_eligible,
                "runtime_generation_status": runtime_status,
                "prompt_profile_hash": prompt_hash,
                "gate_profile_hash": gate_hash,
            }
        ),
        encoding="utf-8",
    )
    if write_x3:
        (run_dir / "x3_disposition.json").write_text(
            json.dumps(
                {
                    "x3_code": x3_code,
                    "proof_eligible": proof_eligible,
                    "runtime_generation_status": runtime_status,
                    "proceed_to_runtime": True,
                    "pass": x3_code in ("X3_ALLOW", "X3C", "X3D", "EXIT_OK"),
                }
            ),
            encoding="utf-8",
        )
    if include_final_resume:
        (run_dir / "generated_resume.json").write_text('{"sections": []}', encoding="utf-8")
    if include_section_output:
        (run_dir / "resume_display_text.txt").write_text(
            "Executive summary display text for R1B semantic cache ingest.\n",
            encoding="utf-8",
        )
        (run_dir / "l2_output.json").write_text(
            '{"display_text": "Executive summary display text for R1B semantic cache ingest."}',
            encoding="utf-8",
        )
        (run_dir / "x2_gate_outputs.json").write_text('{"x2_failed": 0}', encoding="utf-8")
    if include_proof_chunk:
        pass  # proof chunk synthesized by build_chunk_rows_from_run_dir


def test_post_exit_ingestion_requires_x3_artifact(tmp_path: Path) -> None:
    run_dir = tmp_path / "run_no_x3"
    _write_exit_bundle(run_dir, write_x3=False)
    result = evaluate_post_exit_ingestion(run_dir=run_dir, raw_request=_raw_request())
    assert result["admissible"] is False
    assert "missing_exit_x3_disposition" in result["non_admissible_reason"]


def test_mock_runtime_never_cache_admissible(tmp_path: Path) -> None:
    run_dir = tmp_path / "run_mock"
    _write_exit_bundle(run_dir, runtime_status="OFFLINE_CONTRACT_STUB", proof_eligible=True)
    result = evaluate_post_exit_ingestion(run_dir=run_dir, raw_request=_raw_request())
    assert result["admissible"] is False
    assert "not_mock_runtime" in result["non_admissible_reason"]


def test_missing_proof_chunks_rejected(tmp_path: Path) -> None:
    run_dir = tmp_path / "run_no_proof"
    _write_exit_bundle(
        run_dir,
        include_final_resume=False,
        include_section_output=False,
    )
    result = evaluate_post_exit_ingestion(run_dir=run_dir, raw_request=_raw_request())
    assert result["admissible"] is False
    reason = result["non_admissible_reason"]
    assert (
        "section_proof_summary_present" in reason
        or "final_resume_chunk_present" in reason
        or "at_least_one_section_output" in reason
    )


def test_missing_digest_rejected(tmp_path: Path) -> None:
    run_dir = tmp_path / "run_no_digest"
    _write_exit_bundle(run_dir)
    bad_request = {"target_company": "Acme", "target_role": "VP"}
    result = evaluate_post_exit_ingestion(run_dir=run_dir, raw_request=bad_request)
    assert result["admissible"] is False
    assert "jd_digest_present" in result["non_admissible_reason"] or "base_resume_digest_present" in result[
        "non_admissible_reason"
    ]


def test_accepted_post_exit_ingestion(tmp_path: Path) -> None:
    run_dir = tmp_path / "run_ok"
    _write_exit_bundle(run_dir)
    result = evaluate_post_exit_ingestion(run_dir=run_dir, raw_request=_raw_request())
    assert result["admissible"] is True
    assert result["ingestion_phase"] == POST_EXIT_INGESTION_PHASE
    assert result["record"]["cache_admissible"] is True
    for ch in result["chunks"]:
        assert ch["parent_intent_record_id"] == result["record"]["record_id"]
        assert ch["independent_cache_identity"] is False


def test_adapter_blocks_pre_exit_store(tmp_path: Path) -> None:
    adapter = AppsRgR1BCacheAdapter(runs_dir=str(tmp_path))
    rid = adapter.store_intent_and_output(
        intent=_raw_request(),
        chunks=[{"chunk_type": CHUNK_TYPE_FINAL_RESUME, "chunk_text": "{}"}],
        run_context={"x3_disposition": "X3_ALLOW", "proof_eligible": True},
    )
    assert rid is None


def test_adapter_allows_post_exit_with_x3c_artifact_dir(tmp_path: Path) -> None:
    run_dir = tmp_path / "artifact"
    _write_exit_bundle(run_dir, x3_code="X3C")
    store_root = tmp_path / "store"
    adapter = AppsRgR1BCacheAdapter(runs_dir=str(store_root))
    rid = adapter.store_intent_and_output(
        intent=_raw_request(),
        chunks=[
            {"chunk_type": CHUNK_TYPE_FINAL_RESUME, "chunk_text": "{}"},
            {
                "chunk_type": CHUNK_TYPE_EXEC_SUMMARY,
                "section_id": "executive_summary",
                "chunk_text": "Executive summary display text for adapter post-exit ingest.",
                "x2_status": "PASS",
            },
            {"chunk_type": CHUNK_TYPE_SECTION_PROOF, "section_id": "executive_summary", "chunk_text": "{}"},
        ],
        run_context={
            "post_exit_ingestion": True,
            "artifact_dir": str(run_dir),
            "record_id": "hir_w8_live",
            "x3_disposition": "X3C",
            "proof_eligible": True,
            "runtime_generation_status": "REAL_LLM",
            "prompt_profile_hash": "prompt_w8",
            "gate_profile_hash": "gate_w8",
        },
    )
    assert rid == "hir_w8_live"
    assert (
        store_root
        / "durable"
        / "uwg_admitted"
        / "intents"
        / "hir_w8_live.json"
    ).is_file()
    assert not (store_root / "intents" / "hir_w8_live.json").exists()


def test_adapter_rejects_finish_only_disposition_for_durable_write(tmp_path: Path) -> None:
    run_dir = tmp_path / "artifact_finish_only"
    _write_exit_bundle(run_dir, x3_code="X3D")
    store_root = tmp_path / "store"
    adapter = AppsRgR1BCacheAdapter(runs_dir=str(store_root))

    rid = adapter.store_intent_and_output(
        intent=_raw_request(),
        chunks=[{"chunk_type": CHUNK_TYPE_FINAL_RESUME, "chunk_text": "{}"}],
        run_context={
            "post_exit_ingestion": True,
            "artifact_dir": str(run_dir),
            "record_id": "hir_finish_only",
            "x3_disposition": "X3D",
            "proof_eligible": True,
            "runtime_generation_status": "REAL_LLM",
            "prompt_profile_hash": "prompt_w8",
            "gate_profile_hash": "gate_w8",
        },
    )

    assert rid is None
    assert not (store_root / "durable" / "uwg_admitted").exists()


def test_ingest_post_exit_from_run_dir_after_x3c(tmp_path: Path) -> None:
    run_dir = tmp_path / "run_ingest"
    store_root = tmp_path / "store"
    _write_exit_bundle(run_dir, x3_code="X3C")
    rid = ingest_post_exit_from_run_dir(
        run_dir=run_dir,
        raw_request=_raw_request(),
        projection_root=store_root,
    )
    assert rid is not None
    assert (store_root / "durable" / "uwg_admitted" / "intents").is_dir()
    exit_meta = load_post_exit_metadata(run_dir)
    assert exit_meta.exit_metadata_present is True


def test_ingest_rejects_x3_allow_without_x3c_authority(tmp_path: Path) -> None:
    run_dir = tmp_path / "run_finish_only"
    store_root = tmp_path / "store"
    _write_exit_bundle(run_dir, x3_code="X3_ALLOW")

    rid = ingest_post_exit_from_run_dir(
        run_dir=run_dir,
        raw_request=_raw_request(),
        projection_root=store_root,
        store=R1BSemanticCacheStore(store_root / "fixture"),
    )

    assert rid is None
    assert not (store_root / "durable" / "uwg_admitted").exists()
