from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.c0.graph_skill_embedding_allocation import (
    ALL_EMBEDDING_LANES,
    GraphSkillEmbeddingAllocationError,
    build_lane_embedding_allowlists,
    graph_skill_embeddings_required,
    load_graph_skill_embedding_authority,
    load_lane_embedding_allowlists,
    write_graph_skill_embedding_runtime_bundle,
)
from apps_rg.runtime.c0.resume_graph_allocation import (
    ALLOCATION_PLAN_ENV,
    SECTION_EVIDENCE_CONTRACTS_ENV,
    build_whole_resume_graph_allocation,
    write_whole_resume_graph_allocation_bundle,
)
from apps_rg.runtime.c0.resume_graph_proof_pool import (
    bind_proof_pool_to_resume_graph_allocation,
)
from apps_rg.runtime.proof_pool_resolver import SectionProofPool


def _candidate(
    assertion_id: str,
    skill_id: str,
    *,
    similarity: float,
    authority_section_id: str,
) -> dict[str, object]:
    return {
        "assertion_id": assertion_id,
        "skill_id": skill_id,
        "fact_links": [f"lineage_{skill_id}"],
        "similarity": similarity,
        "authority_section_id": authority_section_id,
        "assertion_document_sha256": "1" * 64,
        "authority_envelope_sha256": "2" * 64,
        "skill_row_sha256": "3" * 64,
    }


def _allocation(*assignments: dict[str, object]) -> dict[str, object]:
    return {
        "allocation_plan_digest": "a" * 64,
        "assignments": list(assignments),
    }


def test_requirement_flag_is_explicit_and_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("APPS_RG_GRAPH_SKILL_EMBEDDINGS_REQUIRED", raising=False)
    assert graph_skill_embeddings_required() is False
    monkeypatch.setenv("APPS_RG_GRAPH_SKILL_EMBEDDINGS_REQUIRED", "1")
    assert graph_skill_embeddings_required() is True
    monkeypatch.setenv("APPS_RG_GRAPH_SKILL_EMBEDDINGS_REQUIRED", "sometimes")
    with pytest.raises(GraphSkillEmbeddingAllocationError, match="boolean"):
        graph_skill_embeddings_required()


def test_current_embedding_authority_is_exact_and_qualified() -> None:
    repo = Path(__file__).resolve().parents[5]
    authority = load_graph_skill_embedding_authority(repo)

    assert authority["status"] == "PASS"
    assert authority["graph_sha256"] == (
        "d622c689984798ae7aa0dba83a0ab3571996c92b7ffc2f94f5d52bc67568a739"
    )
    assert authority["corpus_sha256"] == (
        "efd9e01bf82df9324c9b5485bf93b7f5595e9260c60f848a4b1241411a9c2ca6"
    )
    assert authority["embedding_generation_sha256"] == (
        "68dc2043a5f7296259ec0de5878de4930093d4f30e602dd4adb96d6aa3e6c6e6"
    )
    assert authority["model_artifact_sha256"] == (
        "38ccc2e093252ab0416eee16837c75c641f055b4f3def12091fba8ed94e2b263"
    )
    assert authority["qualification_status"] == "PASS"
    assert authority["assertion_count"] == 198
    assert authority["projection_read_only"] is True


def test_embedding_candidates_narrow_the_frozen_allocation() -> None:
    repo = Path(__file__).resolve().parents[5]
    authority = load_graph_skill_embedding_authority(repo)
    corpus = authority["_corpus_payload"]
    narrative_source = {
        "unify_narrative": "unify_bullets",
        "ibm_narrative": "ibm_bullets",
        "insurtech_narrative": "insurtech_bullets",
        "ey_narrative": "ey_bullets",
    }
    scores = {
        section_id: {
            str(row["skill_id"]): 0.5
            for row in corpus["assertions"]
            if narrative_source.get(section_id, section_id) in row["allowed_sections"]
        }
        for section_id in ALL_EMBEDDING_LANES
    }
    jd_text = (
        repo
        / "artifacts/apps_rg/fixtures/gtm_presales_targeting/exec_summary_gtm_presales_jd.txt"
    ).read_text(encoding="utf-8")
    briefing_text = (
        repo
        / "artifacts/apps_rg/fixtures/gtm_presales_targeting/exec_summary_gtm_presales_brief.txt"
    ).read_text(encoding="utf-8")

    bundle = build_whole_resume_graph_allocation(
        repo_root=repo,
        target_role="SVP Technical Pre-Sales, Enterprise Cloud & AI Solutions",
        jd_text=jd_text,
        briefing_text=briefing_text,
        embedding_skill_scores_by_section=scores,
    )

    assignments = bundle["allocation_plan"]["assignments"]
    assert {row["section_id"] for row in assignments} == set(ALL_EMBEDDING_LANES)
    assert all(row["skill_id"] in scores[row["section_id"]] for row in assignments)
    assert all("embedding_similarity" in row for row in assignments)
    assert bundle["allocation_plan"]["embedding_candidate_authority"]["pass"] is True


def test_lane_proof_pool_consumes_exact_embedding_allowlists(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = Path(__file__).resolve().parents[5]
    authority = load_graph_skill_embedding_authority(repo)
    corpus = authority["_corpus_payload"]
    narrative_source = {
        "unify_narrative": "unify_bullets",
        "ibm_narrative": "ibm_bullets",
        "insurtech_narrative": "insurtech_bullets",
        "ey_narrative": "ey_bullets",
    }
    candidates = {
        section_id: [
            {
                **row,
                "similarity": 0.5,
                "authority_section_id": narrative_source.get(section_id, section_id),
            }
            for row in corpus["assertions"]
            if narrative_source.get(section_id, section_id) in row["allowed_sections"]
        ]
        for section_id in ALL_EMBEDDING_LANES
    }
    scores = {
        section_id: {str(row["skill_id"]): 0.5 for row in rows}
        for section_id, rows in candidates.items()
    }
    jd_text = (
        repo
        / "artifacts/apps_rg/fixtures/gtm_presales_targeting/exec_summary_gtm_presales_jd.txt"
    ).read_text(encoding="utf-8")
    briefing_text = (
        repo
        / "artifacts/apps_rg/fixtures/gtm_presales_targeting/exec_summary_gtm_presales_brief.txt"
    ).read_text(encoding="utf-8")
    graph_bundle = build_whole_resume_graph_allocation(
        repo_root=repo,
        target_role="SVP Technical Pre-Sales, Enterprise Cloud & AI Solutions",
        jd_text=jd_text,
        briefing_text=briefing_text,
        embedding_skill_scores_by_section=scores,
    )
    graph_refs = write_whole_resume_graph_allocation_bundle(
        graph_bundle,
        output_dir=tmp_path / "graph",
    )
    allowlists = build_lane_embedding_allowlists(
        allocation_plan=graph_bundle["allocation_plan"],
        candidates_by_section=candidates,
        authority_pins={"manifest_sha256": authority["manifest_sha256"]},
    )
    embedding_refs = write_graph_skill_embedding_runtime_bundle(
        {
            "lane_allowlists": allowlists,
            "runtime_receipt": {
                "schema_version": "apps_rg.graph_skill_embedding_runtime_receipt.v1",
                "status": "PASS",
                "pass": True,
            },
        },
        output_dir=tmp_path / "embeddings",
    )
    monkeypatch.setenv("APPS_RG_GRAPH_SKILL_EMBEDDINGS_REQUIRED", "1")
    monkeypatch.setenv(ALLOCATION_PLAN_ENV, graph_refs["allocation_plan"])
    monkeypatch.setenv(
        SECTION_EVIDENCE_CONTRACTS_ENV,
        graph_refs["section_final_evidence_contracts"],
    )
    monkeypatch.setenv(
        "APPS_RG_GRAPH_SKILL_EMBEDDING_ALLOWLISTS",
        embedding_refs["lane_allowlists"],
    )
    source_plan = graph_bundle["section_plans"]["headline"]
    pool = SectionProofPool(
        section="headline",
        proof_source="augmented_skills_graph",
        proof_pool_ref="test",
        proof_pool_digest=str(source_plan["plan_digest"]),
        selected_fact_plan=source_plan,
        allowed_fact_ids_ordered=[],
        allowed_fact_ids=set(),
        bullet_rows=[],
        proof_pool_metadata={},
        fallback_used=False,
        base_resume_fallback_used=False,
        broad_skills_ledger_present=False,
        srfs_present=False,
        base_resume_json_ref="test",
        base_resume_json_hash="0" * 64,
        broad_skills_ledger_ref="",
        broad_skills_ledger_digest="",
        srfs_ref="",
        base_resume_override_used=False,
    )

    bound = bind_proof_pool_to_resume_graph_allocation(pool)

    metadata = bound.proof_pool_metadata
    assert metadata["graph_skill_embeddings_required"] is True
    assert metadata["graph_skill_embeddings_enabled"] is True
    assert metadata["graph_skill_embedding_exact_rehydration_pass"] is True
    assert metadata["graph_skill_embedding_allocation_intersection_pass"] is True
    assert metadata["graph_skill_embedding_skill_ids"] == sorted(
        {
            row["skill_id"]
            for row in graph_bundle["allocation_plan"]["assignments"]
            if row["section_id"] == "headline"
        }
    )


def test_allocation_is_narrowed_to_exact_rehydrated_assertions() -> None:
    allocation = _allocation(
        {
            "section_id": "competencies",
            "skill_id": "skill_b",
            "fact_id": "fact_allocated",
            "metric_outcome_id": "metric_1",
        }
    )
    candidates = {
        "competencies": [
            _candidate(
                "assertion_a",
                "skill_a",
                similarity=0.95,
                authority_section_id="competencies",
            ),
            _candidate(
                "assertion_b",
                "skill_b",
                similarity=0.80,
                authority_section_id="competencies",
            ),
        ]
    }

    bundle = build_lane_embedding_allowlists(
        allocation_plan=allocation,
        candidates_by_section=candidates,
        section_order=("competencies",),
        authority_pins={"manifest_sha256": "b" * 64},
    )
    lane = bundle["lanes"]["competencies"]

    assert lane["candidate_assertions"] == [
        {"assertion_id": "assertion_a", "similarity": 0.95},
        {"assertion_id": "assertion_b", "similarity": 0.8},
    ]
    assert lane["allowlists"] == {
        "assertion_ids": ["assertion_b"],
        "skill_ids": ["skill_b"],
        "fact_ids": ["fact_allocated"],
        "metric_ids": ["metric_1"],
    }
    assert lane["accepted_assertion_bindings"][0]["fact_links"] == [
        "lineage_skill_b"
    ]
    assert "embedding_text" not in json.dumps(lane["candidate_assertions"])
    assert bundle["similarity_is_claim_authority"] is False
    assert bundle["durable_graph_state_mutated"] is False
    assert bundle["pass"] is True


def test_derived_narrative_binds_to_frozen_source_section_authority() -> None:
    allocation = _allocation(
        {
            "section_id": "ibm_narrative",
            "skill_id": "skill_ibm",
            "fact_id": "fact_ibm",
            "metric_outcome_id": "",
            "derived_from_section_id": "ibm_bullets",
        }
    )
    candidates = {
        "ibm_narrative": [
            _candidate(
                "assertion_ibm",
                "skill_ibm",
                similarity=0.72,
                authority_section_id="ibm_bullets",
            )
        ]
    }

    bundle = build_lane_embedding_allowlists(
        allocation_plan=allocation,
        candidates_by_section=candidates,
        section_order=("ibm_narrative",),
        authority_pins={"manifest_sha256": "b" * 64},
    )

    lane = bundle["lanes"]["ibm_narrative"]
    assert lane["derived_from_section_id"] == "ibm_bullets"
    assert lane["assertion_authority_section_id"] == "ibm_bullets"
    assert lane["allowlists"]["assertion_ids"] == ["assertion_ibm"]


def test_missing_allocated_skill_assertion_fails_closed() -> None:
    allocation = _allocation(
        {
            "section_id": "headline",
            "skill_id": "skill_missing",
            "fact_id": "fact_1",
            "metric_outcome_id": "",
        }
    )
    with pytest.raises(
        GraphSkillEmbeddingAllocationError,
        match="allocated skills lack exact assertion candidates",
    ):
        build_lane_embedding_allowlists(
            allocation_plan=allocation,
            candidates_by_section={"headline": []},
            section_order=("headline",),
            authority_pins={"manifest_sha256": "b" * 64},
        )


def test_runtime_bundle_round_trip_is_digest_bound(tmp_path: Path) -> None:
    candidates = {
        lane: [
            _candidate(
                f"assertion_{lane}",
                f"skill_{lane}",
                similarity=0.5,
                authority_section_id=(
                    lane.replace("_narrative", "_bullets")
                    if lane.endswith("_narrative")
                    else lane
                ),
            )
        ]
        for lane in ALL_EMBEDDING_LANES
    }
    assignments = [
        {
            "section_id": lane,
            "skill_id": f"skill_{lane}",
            "fact_id": f"fact_{lane}",
            "metric_outcome_id": "",
            **(
                {"derived_from_section_id": lane.replace("_narrative", "_bullets")}
                if lane.endswith("_narrative")
                else {}
            ),
        }
        for lane in ALL_EMBEDDING_LANES
    ]
    allowlists = build_lane_embedding_allowlists(
        allocation_plan=_allocation(*assignments),
        candidates_by_section=candidates,
        authority_pins={"manifest_sha256": "b" * 64},
    )
    runtime_receipt = {
        "schema_version": "apps_rg.graph_skill_embedding_runtime_receipt.v1",
        "status": "PASS",
        "authority": {"manifest_sha256": "b" * 64},
        "allowlists_digest": allowlists["allowlists_digest"],
        "projection_sha256_before": "c" * 64,
        "projection_sha256_after": "c" * 64,
        "pass": True,
    }

    refs = write_graph_skill_embedding_runtime_bundle(
        {"lane_allowlists": allowlists, "runtime_receipt": runtime_receipt},
        output_dir=tmp_path,
    )
    loaded = load_lane_embedding_allowlists(Path(refs["lane_allowlists"]))

    assert loaded == allowlists
    assert Path(refs["runtime_receipt"]).is_file()


def test_allowlist_loader_rejects_digest_drift(tmp_path: Path) -> None:
    path = tmp_path / "lane_graph_skill_embedding_allowlists.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "apps_rg.lane_graph_skill_embedding_allowlists.v1",
                "lanes": {},
                "allowlists_digest": "0" * 64,
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(GraphSkillEmbeddingAllocationError, match="digest mismatch"):
        load_lane_embedding_allowlists(path)
