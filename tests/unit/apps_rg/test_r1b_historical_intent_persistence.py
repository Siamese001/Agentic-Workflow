"""W7 — R1B ROLE_TARGET_RUN persistence, retrieval, compatibility (apps_rg only)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.cache.r1b_adapter import AppsRgR1BCacheAdapter, check_r1b_for_apps_rg
from apps_rg.cache.r1b_constants import (
    CACHE_GRAIN_ROLE_TARGET_RUN,
    CHUNK_TYPE_EXEC_SUMMARY,
    CHUNK_TYPE_FINAL_RESUME,
    CHUNK_TYPE_SECTION_PROOF,
    C0_FACT_VECTORS_COLLECTION,
    R1B_STORAGE_SUBSYSTEM,
)
from apps_rg.cache.r1b_intent_vector import intent_text_from_request, normalized_intent_digest
from apps_rg.cache.r1b_models import HistoricalOutputChunk
from apps_rg.cache.r1b_retrieval import lookup_r1b_role_target_run
from apps_rg.cache.r1b_store import R1BSemanticCacheStore


def _raw_request(company: str = "Acme Corp", role: str = "SVP Engineering") -> dict:
    return {
        "target_company": company,
        "target_role": role,
        "generation_mode": "strategic_tailor",
        "resume_hash": "abc123resume",
        "jd_hash": "jd_digest_001",
        "brief_hash": "brief_digest_001",
    }


def _admissible_chunks(parent_id: str) -> list[dict]:
    return [
        {
            "chunk_type": CHUNK_TYPE_FINAL_RESUME,
            "chunk_text": '{"sections": []}',
            "artifact_ref": "artifacts/run/generated_resume.json",
        },
        {
            "chunk_type": CHUNK_TYPE_EXEC_SUMMARY,
            "section_id": "executive_summary",
            "chunk_text": "Executive summary text.",
            "x2_status": "PASS",
        },
        {
            "chunk_type": CHUNK_TYPE_SECTION_PROOF,
            "section_id": "executive_summary",
            "chunk_text": '{"proof_eligible": true}',
        },
    ]


def _write_post_exit_artifacts(
    artifact_dir: Path,
    *,
    x3_code: str = "X3_ALLOW",
    proof_eligible: bool = True,
    runtime_status: str = "REAL_LLM",
) -> None:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    (artifact_dir / "x3_disposition.json").write_text(
        json.dumps(
            {
                "x3_code": x3_code,
                "proof_eligible": proof_eligible,
                "runtime_generation_status": runtime_status,
                "proceed_to_runtime": True,
            }
        ),
        encoding="utf-8",
    )
    (artifact_dir / "run_manifest.json").write_text(
        json.dumps(
            {
                "run_id": "run_admissible_001",
                "proof_eligible": proof_eligible,
                "runtime_generation_status": runtime_status,
            }
        ),
        encoding="utf-8",
    )


def _post_exit_ctx(
    tmp_path: Path,
    record_id: str,
    *,
    proof_eligible: bool = True,
    runtime_status: str = "REAL_LLM",
    prompt_hash: str = "prompt_hash_v1",
    gate_hash: str = "gate_hash_v1",
) -> dict:
    artifact_dir = tmp_path / f"exit_{record_id}"
    _write_post_exit_artifacts(
        artifact_dir,
        proof_eligible=proof_eligible,
        runtime_status=runtime_status,
    )
    return {
        "record_id": record_id,
        "run_id": f"run_{record_id}",
        "post_exit_ingestion": True,
        "artifact_dir": str(artifact_dir),
        "x3_disposition": "X3_ALLOW",
        "proof_eligible": proof_eligible,
        "runtime_generation_status": runtime_status,
        "prompt_profile_hash": prompt_hash,
        "gate_profile_hash": gate_hash,
    }


def test_intent_vector_lookup_not_c0_fact_vectors(tmp_path: Path) -> None:
    store = R1BSemanticCacheStore(tmp_path)
    raw = _raw_request()
    adapter = AppsRgR1BCacheAdapter(runs_dir=str(tmp_path))
    rid = adapter.store_intent_and_output(
        intent=raw,
        chunks=_admissible_chunks("hir_test001"),
        run_context=_post_exit_ctx(tmp_path, "hir_test001"),
    )
    assert rid == "hir_test001"
    vec_path = tmp_path / "vectors" / "hir_test001.json"
    assert vec_path.is_file()
    vec = json.loads(vec_path.read_text(encoding="utf-8"))
    assert vec.get("not_c0_fact_vectors") is True
    assert vec.get("subsystem") == R1B_STORAGE_SUBSYSTEM
    assert C0_FACT_VECTORS_COLLECTION == "fact_vectors"
    assert vec.get("collection") != C0_FACT_VECTORS_COLLECTION
    assert vec.get("storage_subsystem") != C0_FACT_VECTORS_COLLECTION


def test_lookup_uses_intent_record_not_chunk_identity(tmp_path: Path) -> None:
    store = R1BSemanticCacheStore(tmp_path)
    raw = _raw_request()
    adapter = AppsRgR1BCacheAdapter(runs_dir=str(tmp_path))
    adapter.store_intent_and_output(
        intent=raw,
        chunks=_admissible_chunks("hir_parent_a"),
        run_context=_post_exit_ctx(tmp_path, "hir_parent_a"),
    )
    hit = lookup_r1b_role_target_run(raw, store=store, similarity_threshold=0.5)
    assert hit is not None
    assert hit.record.cache_grain == CACHE_GRAIN_ROLE_TARGET_RUN
    assert hit.record.record_id == "hir_parent_a"
    for ch in hit.chunks:
        assert ch.parent_intent_record_id == "hir_parent_a"
        assert ch.to_dict()["independent_cache_identity"] is False


def test_offline_stub_not_admissible(tmp_path: Path) -> None:
    adapter = AppsRgR1BCacheAdapter(runs_dir=str(tmp_path))
    raw = _raw_request(company="StubCo", role="Engineer")
    rid = adapter.store_intent_and_output(
        intent=raw,
        chunks=_admissible_chunks("hir_stub"),
        run_context=_post_exit_ctx(
            tmp_path,
            "hir_stub",
            runtime_status="OFFLINE_CONTRACT_STUB",
            prompt_hash="p1",
            gate_hash="g1",
        ),
    )
    assert rid is None
    store = R1BSemanticCacheStore(tmp_path)
    assert store.load_intent("hir_stub") is None
    hit = lookup_r1b_role_target_run(raw, store=store, similarity_threshold=0.5)
    assert hit is None


def test_proof_ineligible_not_retrieved(tmp_path: Path) -> None:
    store = R1BSemanticCacheStore(tmp_path)
    adapter = AppsRgR1BCacheAdapter(runs_dir=str(tmp_path))
    adapter.store_intent_and_output(
        intent=_raw_request(company="NoProof", role="Role"),
        chunks=_admissible_chunks("hir_noproof"),
        run_context=_post_exit_ctx(
            tmp_path,
            "hir_noproof",
            proof_eligible=False,
            prompt_hash="p1",
            gate_hash="g1",
        ),
    )
    hit = lookup_r1b_role_target_run(
        _raw_request(company="NoProof", role="Role"),
        store=store,
        similarity_threshold=0.5,
    )
    assert hit is None


def test_check_r1b_probe_on_hit(tmp_path: Path) -> None:
    adapter = AppsRgR1BCacheAdapter(runs_dir=str(tmp_path))
    raw = _raw_request()
    adapter.store_intent_and_output(
        intent=raw,
        chunks=_admissible_chunks("hir_probe"),
        run_context=_post_exit_ctx(tmp_path, "hir_probe", prompt_hash="p1", gate_hash="g1"),
    )
    probe = check_r1b_for_apps_rg(raw_request=raw, runs_dir=tmp_path, similarity_threshold=0.5)
    assert probe is not None
    assert probe.get("cached") is True
    assert probe.get("lookup_anchor") == "HistoricalIntentRecord.request_intent_vector"
    assert probe.get("not_c0_fact_vectors") is True


def test_miss_continues_generation(tmp_path: Path) -> None:
    probe = check_r1b_for_apps_rg(
        raw_request=_raw_request(company="UnknownCo", role="Unknown Role"),
        runs_dir=tmp_path,
    )
    assert probe is None


def test_digest_mismatch_rejects_candidate(tmp_path: Path) -> None:
    store = R1BSemanticCacheStore(tmp_path)
    raw_a = _raw_request(company="DigestCo", role="RoleA")
    adapter = AppsRgR1BCacheAdapter(runs_dir=str(tmp_path))
    adapter.store_intent_and_output(
        intent=raw_a,
        chunks=_admissible_chunks("hir_digest"),
        run_context=_post_exit_ctx(
            tmp_path,
            "hir_digest",
            prompt_hash="profile_a",
            gate_hash="gate_a",
        ),
    )
    raw_b = _raw_request(company="DigestCo", role="RoleB")
    assert normalized_intent_digest(intent_text_from_request(raw_a)) != normalized_intent_digest(
        intent_text_from_request(raw_b)
    )
    hit = lookup_r1b_role_target_run(raw_b, store=store, similarity_threshold=0.99)
    assert hit is None
