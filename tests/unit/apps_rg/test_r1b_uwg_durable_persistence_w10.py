"""W10 — R1B UWG durable promotion and direct-write guards."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.cache.r1b_uwg_promotion import AppsRgR1BUwgGateway
from apps_rg.cache.r1b_constants import (
    C0_FACT_VECTORS_COLLECTION,
    FILE_BACKED_SSOT_NOTE,
    R1B_UWG_TARGET_SURFACE,
    STORAGE_TIER_FIXTURE_MIRROR,
)
from apps_rg.cache.r1b_durable_write_guard import (
    R1BDirectDurableWriteForbidden,
    assert_r1b_durable_write_authority,
    record_blocked_direct_r1b_write,
)
from apps_rg.cache.r1b_models import HistoricalIntentRecord, HistoricalOutputChunk
from apps_rg.cache.r1b_store import R1BSemanticCacheStore
from apps_rg.cache.r1b_uwg_promotion import (
    build_r1b_commit_bundle,
    build_r1b_promotion_candidate,
    promote_and_project_r1b_cache,
    promote_r1b_cache_via_uwg,
)
from tests.unit.apps_rg.l5_uwg_fixture import write_verified_l5_sealed_artifact


def _record() -> HistoricalIntentRecord:
    w7 = (
        Path(__file__).resolve().parents[3]
        / "artifacts"
        / "apps_rg"
        / "r1b_semantic_cache"
        / "w7_fixtures"
    )
    if (w7 / "historical_intent_record_admissible.json").is_file():
        data = json.loads(
            (w7 / "historical_intent_record_admissible.json").read_text(
                encoding="utf-8"
            )
        )
        data["record_id"] = "hir_w10_001"
        data["source_run_id"] = "run_w10"
        data["normalized_intent_digest"] = "1" * 64
        return HistoricalIntentRecord.from_dict(data)
    return HistoricalIntentRecord.from_dict(
        {
            "record_id": "hir_w10_001",
            "normalized_intent_digest": "1" * 64,
            "request_intent_text": "apps_rg|role_target_run|acme|vp",
            "request_intent_vector_ref": "vectors/hir_w10_001.json",
            "target_company": "Acme",
            "target_role": "VP",
            "cache_admissible": True,
            "prompt_profile_hash": "prompt_profile_w7_v1",
            "gate_profile_hash": "gate_profile_w7_v1",
            "source_run_id": "run_w10",
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


def _chunks(parent: str) -> list[HistoricalOutputChunk]:
    return [
        HistoricalOutputChunk.from_dict(
            {
                "chunk_id": "hoc_w10_1",
                "parent_intent_record_id": parent,
                "chunk_type": "final_resume",
                "section_id": "",
                "chunk_text": "{}",
                "chunk_digest": "",
                "chunk_vector_ref": "",
                "artifact_ref": "",
                "artifact_digest": "",
                "source_fact_ids": [],
                "proof_pool_refs": [],
                "support_status": "",
                "x2_status": "PASS",
                "x1d_status": "",
                "section_prompt_hash": "",
                "section_model_profile_hash": "",
                "generated_at_utc": "2026-05-18T00:00:00+00:00",
            }
        )
    ]


def _candidate(tmp_path: Path) -> object:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "x3_disposition.json").write_text(
        json.dumps({"x3_code": "X3_ALLOW", "proof_eligible": True}),
        encoding="utf-8",
    )
    (run_dir / "run_manifest.json").write_text(
        json.dumps({"run_id": "run_w10", "proof_eligible": True}),
        encoding="utf-8",
    )
    rec = _record()
    l5_metadata = write_verified_l5_sealed_artifact(
        run_dir,
        request_id=rec.record_id,
        run_id="run_w10",
        trace_id="trace:run_w10",
    )
    ch = _chunks(rec.record_id)
    assessment = {
        "admissible": True,
        "record": rec.to_dict(),
        "chunks": [c.to_dict() for c in ch],
        "exit_metadata": {
            "source_run_id": "run_w10",
            "x3_disposition": "X3_ALLOW",
            **l5_metadata,
        },
    }
    return build_r1b_promotion_candidate(
        record=rec,
        chunks=ch,
        post_exit_eligibility=assessment,
        run_dir=run_dir,
    )


def test_file_store_not_durable_production_truth(tmp_path: Path) -> None:
    store = R1BSemanticCacheStore(tmp_path)
    manifest = store.store_manifest()
    assert manifest["is_durable_production_truth"] is False
    assert manifest["storage_tier"] == STORAGE_TIER_FIXTURE_MIRROR
    assert "fixture" in FILE_BACKED_SSOT_NOTE.lower()


def test_l2_direct_durable_write_blocked() -> None:
    with pytest.raises(R1BDirectDurableWriteForbidden):
        assert_r1b_durable_write_authority(attempting_surface="L2")


def test_l6_direct_durable_write_blocked() -> None:
    with pytest.raises(R1BDirectDurableWriteForbidden):
        assert_r1b_durable_write_authority(attempting_surface="L6")


def test_uwg_reject_direct_write_receipt() -> None:
    payload = record_blocked_direct_r1b_write(
        attempting_surface="L2",
        reason="r1b_durable_write_forbidden",
        run_id="run_w10",
    )
    assert payload["target_surface"] == R1B_UWG_TARGET_SURFACE
    assert "UWG_AUTHORITY_REQUIRED" in payload["failed_rule_ids"]


def test_commit_request_fields(tmp_path: Path) -> None:
    cand = _candidate(tmp_path)
    cr, sds, _rb, _rf = build_r1b_commit_bundle(cand)
    assert cr.source_surface == "Exit"
    assert cr.gate_verdict_refs
    assert cr.l5_certification_ref == cand.l5_certification_packet_ref
    assert cr.l5_certification_refs
    assert sds[0].target_surface == R1B_UWG_TARGET_SURFACE
    assert sds[0].operation_type == "memory_promotion"


def test_uwg_admitted_promotion(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("APPS_RG_R1B_SKIP_UWG", raising=False)
    cand = _candidate(tmp_path)
    store = R1BSemanticCacheStore(tmp_path / "fixture")
    outcome = promote_and_project_r1b_cache(
        candidate=cand,
        projection_root=store.root,
        fixture_store=store,
        gateway=AppsRgR1BUwgGateway(),
    )
    assert outcome.status == "ADMITTED"
    assert outcome.uwg_commit_receipt_id
    assert outcome.c0_fact_vectors_consulted is False
    durable = (
        store.root
        / "durable"
        / "uwg_admitted"
        / "intents"
        / f"{cand.record.record_id}.json"
    )
    assert durable.is_file()
    bundle = json.loads(durable.read_text(encoding="utf-8"))
    assert bundle["storage_tier"] == "uwg_admitted_durable_projection"
    assert bundle["parent_intent_record"]["record_id"] == cand.record.record_id
    assert bundle["governance_receipt"]["l5_certification_verified"] is True


def test_blocked_when_not_cache_admissible(tmp_path: Path) -> None:
    cand = _candidate(tmp_path)
    rec = HistoricalIntentRecord.from_dict(
        {**cand.record.to_dict(), "cache_admissible": False}
    )
    cand = build_r1b_promotion_candidate(
        record=rec,
        chunks=cand.chunks,
        post_exit_eligibility=cand.post_exit_eligibility,
    )
    outcome = promote_r1b_cache_via_uwg(cand, gateway=AppsRgR1BUwgGateway())
    assert outcome.status == "BLOCKED"
    assert "cache_not_admissible" in outcome.blocked_reason_codes


def test_blocked_uwg_when_skip_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APPS_RG_R1B_SKIP_UWG", "1")
    cand = _candidate(tmp_path)
    outcome = promote_r1b_cache_via_uwg(cand, gateway=AppsRgR1BUwgGateway())
    assert outcome.status == "BLOCKED"
    assert "APPS_RG_R1B_SKIP_UWG" in outcome.blocked_reason_codes


def test_r1b_not_c0_fact_vectors() -> None:
    assert C0_FACT_VECTORS_COLLECTION == "fact_vectors"
