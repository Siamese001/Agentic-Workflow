"""Tests for C0 semantic-cache payload + UWG->L4 attachment."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from apps_rg.runtime.c0.c02_semantic_cache_payload import (
    C02_SEMANTIC_CACHE_PAYLOAD_ARTIFACT,
    build_c02_semantic_cache_payload,
    read_c02_semantic_cache_payload,
    section_intent_text,
    serialize_query_output,
    write_c02_semantic_cache_payload,
)
from tests.unit.apps_rg.l5_uwg_fixture import write_verified_l5_sealed_artifact


def _atoms() -> list[dict]:
    return [
        {
            "fact_id": "fact_engineering_platform_001",
            "text_to_embed": "Architected a governed agentic AI platform with deterministic routing.",
            "confidence": "HIGH",
            "proof_status": "proof_eligible",
            "retrieval_score": 0.91,
            "source_type": "candidate_fact_ledger",
        },
        {
            "fact_id": "fact_exec_001",
            "claim_text": "Partnered with C-suite to scale platform engineering org.",
            "confidence": "HIGH",
            "proof_status": "proof_eligible",
            "retrieval_score": 0.77,
            "source_type": "candidate_fact_ledger",
        },
    ]


def test_section_intent_text_is_deterministic_and_section_scoped() -> None:
    first = section_intent_text(
        section_id="competencies",
        target_company="Brown & Brown",
        target_role="SVP",
        jd_digest="abc123",
        query_terms=["fact_x", "fact_y"],
    )
    second = section_intent_text(
        section_id="competencies",
        target_company="Brown & Brown",
        target_role="SVP",
        jd_digest="abc123",
        query_terms=["fact_x", "fact_y"],
    )
    assert first == second
    assert "competencies" in first
    other = section_intent_text(
        section_id="ibm_bullets",
        target_company="Brown & Brown",
        target_role="SVP",
        jd_digest="abc123",
        query_terms=["fact_x", "fact_y"],
    )
    assert other != first


def test_serialize_query_output_is_bounded_and_typed() -> None:
    rows = serialize_query_output(_atoms())
    assert len(rows) == 2
    assert rows[0]["fact_id"] == "fact_engineering_platform_001"
    assert isinstance(rows[0]["retrieval_score"], float)
    assert rows[1]["text"]


def test_build_payload_has_intent_vector_and_query_output() -> None:
    payload = build_c02_semantic_cache_payload(
        section_id="competencies",
        atoms=_atoms(),
        vector_query_receipt={
            "dense_search_refs": ["dense:fact_vectors:/tmp/chroma"],
            "hybrid_enrichment_item_count": 5,
        },
        target_company="Brown & Brown",
        target_role="SVP",
        jd_digest="abc123",
        run_id="run_test_1",
    )
    assert payload["schema_version"] == "c02_semantic_cache_payload_v1"
    assert payload["section_id"] == "competencies"
    assert payload["durable_write_authority"] is False
    assert payload["proposal_status"] == "PENDING_UWG"
    assert "intent_vector" in payload
    assert payload["intent_digest"]
    assert payload["query_output_count"] == 2
    assert payload["dense_search_refs"] == ["dense:fact_vectors:/tmp/chroma"]
    assert payload["hybrid_enrichment_item_count"] == 5


def test_write_and_read_roundtrip(tmp_path: Path) -> None:
    payload = build_c02_semantic_cache_payload(
        section_id="unify_bullets",
        atoms=_atoms(),
        vector_query_receipt={},
        run_id="run_rt",
    )
    out = write_c02_semantic_cache_payload(tmp_path, payload)
    assert out is not None
    assert (tmp_path / C02_SEMANTIC_CACHE_PAYLOAD_ARTIFACT).is_file()
    got = read_c02_semantic_cache_payload(tmp_path)
    assert got["section_id"] == "unify_bullets"
    assert got["query_output_count"] == 2


def test_write_returns_none_when_artifact_dir_is_a_file(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "not_a_dir"
    artifact_dir.write_text("blocking file", encoding="utf-8")
    payload = build_c02_semantic_cache_payload(
        section_id="headline",
        atoms=_atoms(),
        vector_query_receipt={},
        run_id="run_fs_error",
    )
    assert write_c02_semantic_cache_payload(artifact_dir, payload) is None


def test_write_returns_none_when_artifact_dir_parent_is_a_file(tmp_path: Path) -> None:
    parent_file = tmp_path / "parent_file"
    parent_file.write_text("blocking file", encoding="utf-8")
    artifact_dir = parent_file / "child"
    payload = build_c02_semantic_cache_payload(
        section_id="headline",
        atoms=_atoms(),
        vector_query_receipt={},
        run_id="run_fs_error_parent",
    )
    assert write_c02_semantic_cache_payload(artifact_dir, payload) is None


def test_read_missing_payload_returns_empty(tmp_path: Path) -> None:
    assert read_c02_semantic_cache_payload(tmp_path) == {}


def test_payload_never_claims_write_authority() -> None:
    payload = build_c02_semantic_cache_payload(
        section_id="headline",
        atoms=_atoms(),
        vector_query_receipt={},
    )
    assert payload["durable_write_authority"] is False
    assert "C0 proposes" in payload["spine_note"]


def test_exit_populates_cache_write_proposal_when_l5_verified() -> None:
    from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
    from apps_rg.runtime.bindings.exit_binding import _exit_finalize_apps_rg_impl
    from apps_rg.runtime.l5.packet_builder import (
        attach_l5_packet_to_sealed,
        build_l5_certification_packet,
    )

    sealed = SealedL2Artifact(
        request_id="req1",
        run_id="run_exit_1",
        app_id="apps_rg",
        trace_id="t1",
        execution_status="completed",
        generated_content="Competencies content body.",
        compilation_hash="a" * 64,
        replay_key="replay-exit-1",
        l5_certification_ref="l5:test:run_exit_1",
    )
    prompt = SimpleNamespace(
        request_id="req1",
        run_id="run_exit_1",
        app_id="apps_rg",
        trace_id="t1",
        tenant_id="apps_rg",
        replay_key="replay-exit-1",
        l5_certification_ref="l5:test:run_exit_1",
        compilation_hash="b" * 64,
        evidence_digest="c" * 64,
    )
    packet = build_l5_certification_packet(sealed=sealed, prompt_artifact=prompt)
    sealed = attach_l5_packet_to_sealed(sealed, packet, prompt_artifact=prompt)
    result = _exit_finalize_apps_rg_impl(
        sealed,
        prompt_artifact=prompt,
        fec=None,
        target_company="Brown & Brown",
        target_role="SVP",
    )
    assert result.disposition.outcome_authorized is True
    assert len(result.cache_write_proposals) == 1
    proposal = result.cache_write_proposals[0]
    assert proposal.proposal_status == "PENDING_UWG"
    assert proposal.l5_certification_verified is True
    assert proposal.l5_certification_verification_digest
    assert "run_exit_1" in proposal.metadata_ref
    assert proposal.cache_key


def test_l4_namespace_ref_attaches_c0_payload(tmp_path: Path) -> None:
    payload = build_c02_semantic_cache_payload(
        section_id="competencies",
        atoms=_atoms(),
        vector_query_receipt={"dense_search_refs": ["dense:fact_vectors:/x"]},
        run_id="run_l4",
    )
    write_c02_semantic_cache_payload(tmp_path, payload)
    got = read_c02_semantic_cache_payload(tmp_path)
    assert got["intent_vector"] is not None
    assert got["query_output"]
    assert got["intent_digest"]


def test_uwg_admitted_l4_ref_carries_c0_intent_vector_and_query_output(
    tmp_path: Path,
    monkeypatch,
) -> None:
    import json as _json

    from apps_rg.cache.r1b_governed_receipt_emission import (
        L4_NAMESPACE_OBJECT_REF_ARTIFACT,
        _materialize_uwg_receipts,
    )
    from apps_rg.cache.r1b_models import HistoricalIntentRecord, HistoricalOutputChunk
    from apps_rg.cache.r1b_uwg_promotion import build_r1b_promotion_candidate

    monkeypatch.delenv("APPS_RG_R1B_SKIP_UWG", raising=False)
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "x3_disposition.json").write_text(
        _json.dumps({"x3_code": "X3_ALLOW", "proof_eligible": True}),
        encoding="utf-8",
    )
    (run_dir / "run_manifest.json").write_text(
        _json.dumps({"run_id": "run_l4_e2e", "proof_eligible": True}),
        encoding="utf-8",
    )
    l5_metadata = write_verified_l5_sealed_artifact(
        run_dir,
        request_id="hir_l4_e2e",
        run_id="run_l4_e2e",
        trace_id="trace:run_l4_e2e",
    )
    write_c02_semantic_cache_payload(
        run_dir,
        build_c02_semantic_cache_payload(
            section_id="competencies",
            atoms=_atoms(),
            vector_query_receipt={"dense_search_refs": ["dense:fact_vectors:/x"]},
            run_id="run_l4_e2e",
        ),
    )

    record = HistoricalIntentRecord.from_dict(
        {
            "record_id": "hir_l4_e2e",
            "normalized_intent_digest": "digest_e2e",
            "request_intent_text": "apps_rg|role_target_run|acme|svp",
            "request_intent_vector_ref": "vectors/hir_l4_e2e.json",
            "target_company": "Acme",
            "target_role": "SVP",
            "cache_admissible": True,
            "prompt_profile_hash": "pp_v1",
            "gate_profile_hash": "gp_v1",
            "source_run_id": "run_l4_e2e",
            "jd_digest": "jd",
            "briefing_digest": "brief",
            "srfs_digest": "",
            "proof_pool_digest": "",
            "skills_ledger_digest": "",
            "base_resume_digest": "resume",
            "final_resume_digest": "",
            "model_profile_hash": "",
            "x3_disposition": "X3_ALLOW",
            "proof_eligible": True,
            "generated_at_utc": "2026-05-18T00:00:00+00:00",
            "job_family": "",
        }
    )
    chunks = [
        HistoricalOutputChunk.from_dict(
            {
                "chunk_id": "hoc_l4_1",
                "parent_intent_record_id": record.record_id,
                "chunk_type": "final_resume",
                "section_id": "competencies",
                "chunk_text": "competencies body",
                "chunk_digest": "",
                "chunk_vector_ref": "",
                "artifact_ref": "",
                "artifact_digest": "",
                "source_fact_ids": ["fact_engineering_platform_001"],
                "proof_pool_refs": [],
                "support_status": "PASS",
                "x2_status": "PASS",
                "x1d_status": "",
                "section_prompt_hash": "",
                "section_model_profile_hash": "",
                "generated_at_utc": "2026-05-18T00:00:00+00:00",
            }
        )
    ]
    assessment = {
        "admissible": True,
        "record": record.to_dict(),
        "chunks": [chunk.to_dict() for chunk in chunks],
        "exit_metadata": {
            "source_run_id": "run_l4_e2e",
            "x3_disposition": "X3_ALLOW",
            **l5_metadata,
        },
    }
    candidate = build_r1b_promotion_candidate(
        record=record,
        chunks=chunks,
        post_exit_eligibility=assessment,
        run_dir=run_dir,
    )
    chain = _materialize_uwg_receipts(
        run_dir,
        candidate=candidate,
        section_id="competencies",
        run_id="run_l4_e2e",
        manifest={"run_id": "run_l4_e2e"},
        gateway=None,
    )
    assert chain.uwg_commit_or_block_status == "ADMITTED", chain.to_dict()

    l4_ref = _json.loads(
        (run_dir / L4_NAMESPACE_OBJECT_REF_ARTIFACT).read_text(encoding="utf-8")
    )
    payload = l4_ref["payload"]
    assert payload["c0_section_intent_digest"]
    assert payload["c0_section_intent_vector"]
    assert payload["c0_query_output"]
    assert payload["c0_query_output_count"] >= 1
    assert payload["c0_dense_search_refs"] == ["dense:fact_vectors:/x"]
    assert payload["l5_certification_packet_digest"] == "d" * 64
    assert payload["governance_receipt"]["l5_certification_verified"] is True
