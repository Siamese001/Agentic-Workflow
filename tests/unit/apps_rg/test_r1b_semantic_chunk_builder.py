"""P1–P6 R1B semantic chunk builder — section display text and whole-run lane rollup."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.cache.r1b_constants import (
    CHUNK_TYPE_CLAIM_LEDGER,
    CHUNK_TYPE_FINAL_RESUME,
    CHUNK_TYPE_HEADLINE,
)
from apps_rg.cache.r1b_post_exit_ingest import evaluate_post_exit_ingestion
from apps_rg.cache.r1b_retrieval import filter_chunks_by_section, lookup_section_output_chunk
from apps_rg.cache.r1b_semantic_chunk_builder import (
    INGEST_PROFILE_INTEGRATED_WHOLE_RUN,
    INGEST_PROFILE_SECTION_LANE,
    build_chunk_rows_from_run_dir,
    build_claim_ledger_chunk_text,
    detect_ingest_profile,
    resolve_section_display_text,
)
from apps_rg.runtime.full_run_section_status import LANE_DISPLAY_TXT_CANDIDATES
from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES


def _raw_request() -> dict:
    return {
        "target_company": "Brown & Brown",
        "target_role": "SVP IT Strategy",
        "generation_mode": "strategic_tailor",
        "resume_hash": "resume_digest_p1",
        "jd_hash": "jd_digest_p1",
        "brief_hash": "brief_digest_p1",
    }


def _write_section_exit_bundle(
    run_dir: Path,
    *,
    section_id: str,
    display_name: str,
    display_text: str,
    include_final_resume: bool = False,
) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "run_manifest.json").write_text(
        json.dumps(
            {
                "run_id": f"run_{section_id}_p1",
                "section_id": section_id,
                "proof_eligible": True,
                "runtime_generation_status": "REAL_LLM",
                "prompt_profile_hash": "prompt_p1",
                "gate_profile_hash": "gate_p1",
            }
        ),
        encoding="utf-8",
    )
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
    (run_dir / display_name).write_text(display_text + "\n", encoding="utf-8")
    (run_dir / "x2_gate_outputs.json").write_text(
        json.dumps({"x2_failed": 0, "gates": []}),
        encoding="utf-8",
    )
    (run_dir / "canonical_claim_ledger_v2.json").write_text(
        json.dumps(
            {
                "claims": [
                    {"fact_id": "F001", "claim_text": "Led platform modernization."},
                ]
            }
        ),
        encoding="utf-8",
    )
    if include_final_resume:
        (run_dir / "generated_resume.json").write_text(
            '{"sections": ["headline"]}',
            encoding="utf-8",
        )


@pytest.mark.parametrize("section_id", GENERATED_LANES)
def test_each_section_lane_builds_display_text_chunk(
    tmp_path: Path,
    section_id: str,
) -> None:
    display_name = LANE_DISPLAY_TXT_CANDIDATES[section_id][0]
    text = f"Display copy for {section_id} — Brown & Brown tailored line."
    run_dir = tmp_path / section_id
    _write_section_exit_bundle(
        run_dir,
        section_id=section_id,
        display_name=display_name,
        display_text=text,
    )
    manifest = json.loads((run_dir / "run_manifest.json").read_text(encoding="utf-8"))
    assert detect_ingest_profile(run_dir, manifest) == INGEST_PROFILE_SECTION_LANE
    rows = build_chunk_rows_from_run_dir(run_dir, manifest=manifest)
    section_rows = [r for r in rows if r.get("chunk_type") == f"{section_id}_output"]
    assert len(section_rows) == 1
    assert section_rows[0]["chunk_text"].startswith("Display copy")
    assert section_rows[0]["chunk_id"] == f"sec_{section_id}"
    claim_rows = [r for r in rows if r.get("chunk_type") == CHUNK_TYPE_CLAIM_LEDGER]
    assert len(claim_rows) == 1
    assert "F001" in claim_rows[0]["chunk_text"]
    assert not any(r.get("chunk_type") == CHUNK_TYPE_FINAL_RESUME for r in rows)


@pytest.mark.parametrize("section_id", GENERATED_LANES)
def test_each_section_lane_post_exit_admissible_without_final_resume(
    tmp_path: Path,
    section_id: str,
) -> None:
    display_name = LANE_DISPLAY_TXT_CANDIDATES[section_id][0]
    run_dir = tmp_path / f"adm_{section_id}"
    _write_section_exit_bundle(
        run_dir,
        section_id=section_id,
        display_name=display_name,
        display_text=f"Admissible {section_id} prose for semantic cache.",
    )
    payload = evaluate_post_exit_ingestion(run_dir=run_dir, raw_request=_raw_request())
    assert payload["admissible"] is True, (section_id, payload.get("non_admissible_reason"))
    chunks = payload.get("chunks") or []
    assert any(c.get("chunk_type") == f"{section_id}_output" for c in chunks)
    assert any(len(str(c.get("chunk_text") or "")) > 20 for c in chunks)


def test_whole_run_ingest_collects_all_lane_display_chunks(tmp_path: Path) -> None:
    root = tmp_path / "full_resume_test001"
    root.mkdir(parents=True)
    (root / "run_manifest.json").write_text(
        json.dumps(
            {
                "run_id": "full_resume_test001",
                "section_id": "integrated_whole_run",
                "proof_eligible": True,
                "runtime_generation_status": "REAL_LLM",
                "prompt_profile_hash": "prompt_whole",
                "gate_profile_hash": "gate_whole",
            }
        ),
        encoding="utf-8",
    )
    (root / "x3_disposition.json").write_text(
        json.dumps(
            {
                "x3_code": "X3_ALLOW",
                "proof_eligible": True,
                "runtime_generation_status": "REAL_LLM",
            }
        ),
        encoding="utf-8",
    )
    out_dir = root / "outputs"
    out_dir.mkdir(parents=True)
    (out_dir / "generated_resume.json").write_text(
        '{"assembled": true, "company": "Brown & Brown"}',
        encoding="utf-8",
    )
    lanes = root / "lanes"
    lanes.mkdir()
    for lane in GENERATED_LANES:
        lane_dir = lanes / lane
        display_name = LANE_DISPLAY_TXT_CANDIDATES[lane][0]
        _write_section_exit_bundle(
            lane_dir,
            section_id=lane,
            display_name=display_name,
            display_text=f"Whole-run lane body for {lane}.",
        )

    manifest = json.loads((root / "run_manifest.json").read_text(encoding="utf-8"))
    assert detect_ingest_profile(root, manifest) == INGEST_PROFILE_INTEGRATED_WHOLE_RUN
    rows = build_chunk_rows_from_run_dir(root, manifest=manifest)
    assert any(r.get("chunk_type") == CHUNK_TYPE_FINAL_RESUME for r in rows)
    section_types = {r.get("chunk_type") for r in rows}
    for lane in GENERATED_LANES:
        assert f"{lane}_output" in section_types

    payload = evaluate_post_exit_ingestion(run_dir=root, raw_request=_raw_request())
    assert payload["admissible"] is True
    assert payload["chunk_count"] >= 9


def test_section_lookup_filter_p5() -> None:
    from apps_rg.cache.r1b_compatibility import CompatibilityVerdict
    from apps_rg.cache.r1b_models import HistoricalIntentRecord, HistoricalOutputChunk
    from apps_rg.cache.r1b_retrieval import R1BLookupHit

    def _chunk(**kwargs: str) -> HistoricalOutputChunk:
        base = {
            "chunk_digest": "",
            "chunk_vector_ref": "",
            "artifact_ref": "",
            "artifact_digest": "",
            "source_fact_ids": [],
            "proof_pool_refs": [],
            "support_status": "UNKNOWN",
            "x2_status": "PASS",
            "x1d_status": "",
            "section_prompt_hash": "",
            "section_model_profile_hash": "",
            "generated_at_utc": "2026-05-20T00:00:00+00:00",
        }
        base.update(kwargs)
        return HistoricalOutputChunk(**base)

    chunks = [
        _chunk(
            chunk_id="sec_headline",
            parent_intent_record_id="hir_parent",
            chunk_type=CHUNK_TYPE_HEADLINE,
            section_id="headline",
            chunk_text="SVP Technology Leader",
        ),
        _chunk(
            chunk_id="sec_competencies",
            parent_intent_record_id="hir_parent",
            chunk_type="competencies_output",
            section_id="competencies",
            chunk_text="Cloud | Strategy | Delivery",
        ),
    ]
    filtered = filter_chunks_by_section(chunks, section_id="headline")
    assert len(filtered) == 1
    assert filtered[0].chunk_text.startswith("SVP")

    record = HistoricalIntentRecord(
        record_id="hir_parent",
        app_id="apps_rg",
        cache_grain="ROLE_TARGET_RUN",
        request_intent_text="x",
        normalized_intent_digest="d" * 64,
        request_intent_vector_ref="v",
        source_run_id="run",
        target_company="Acme",
        target_role="VP",
        job_family="",
        jd_digest="jd",
        briefing_digest="",
        srfs_digest="",
        proof_pool_digest="",
        skills_ledger_digest="",
        base_resume_digest="resume",
        final_resume_digest="",
        prompt_profile_hash="p",
        model_profile_hash="",
        gate_profile_hash="g",
        x3_disposition="X3_ALLOW",
        proof_eligible=True,
        cache_admissible=True,
        generated_at_utc="2026-05-20T00:00:00+00:00",
    )
    hit = R1BLookupHit(
        record=record,
        chunks=chunks,
        similarity=0.99,
        verdict=CompatibilityVerdict(admissible=True, reason="", checks={}),
    )
    found = lookup_section_output_chunk(hit, "headline")
    assert found is not None
    assert "SVP" in found.chunk_text


def test_claim_ledger_compact_text() -> None:
    path = Path(__file__).parent / "_claim_fixture.json"
    path.write_text(
        json.dumps({"claims": [{"fact_id": "F9", "claim_text": "Scaled team to 40."}]}),
        encoding="utf-8",
    )
    text = build_claim_ledger_chunk_text(path)
    path.unlink(missing_ok=True)
    assert "F9" in text
    assert "Scaled team" in text
