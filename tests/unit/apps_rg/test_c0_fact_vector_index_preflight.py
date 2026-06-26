from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from agentic_core.config.model_catalog import BGE_M3_MODEL_ID
from apps_rg.runtime.c0 import fact_vector_index_preflight as fvip
from apps_rg.runtime.c0.section_authority_profile import direct_vector_section_ids
from apps_rg.runtime.chroma_precomputed_collection import EXPECTED_BGE_DIMENSION
from apps_rg.runtime.fact_vectors_bootstrap import GENERATED_LANES, MANIFEST_REL


class _FakeFactVectorCollection:
    def __init__(self, metas: list[dict[str, Any]]) -> None:
        self._metas = metas
        self.metadata = {"source": "unit-test"}

    def count(self) -> int:
        return len(self._metas)

    def get(self, *, limit: int, include: list[str]) -> dict[str, Any]:
        assert include == ["metadatas"]
        return {"metadatas": self._metas[:limit]}


def _write_manifest(root: Path, *, section_count: int = 2) -> None:
    path = root / MANIFEST_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": "apps_rg.fact_vectors_bootstrap_manifest.v1",
                "generated_at_utc": "2026-06-23T00:00:00Z",
                "manifest_checksum": "a" * 64,
                "source": (
                    "candidate_fact_ledger + base_resume_employment_bullets "
                    "(tracked first-principles sources); generated output is never a live fact source"
                ),
                "dry_run": False,
                "upserted_count": section_count,
                "collection_count_after": section_count,
                "sparse_sidecar_built": True,
                "per_section_target_counts": {
                    lane: section_count for lane in GENERATED_LANES
                },
                "locked_deterministic_lanes": [],
                "required_lanes": list(GENERATED_LANES),
                "missing_required_lane_targets": [],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def _bge_meta(
    *,
    section_targets: str = "competencies,headline",
    source_document_id: str = "fact_unit_001",
) -> dict[str, Any]:
    return {
        "source_document_id": source_document_id,
        "section_targets": section_targets,
        "embedding_model_id": BGE_M3_MODEL_ID,
        "embedding_dim": EXPECTED_BGE_DIMENSION,
        "source_class": "candidate_profile",
        "tier": "PRIMARY",
    }


def test_fact_vector_index_preflight_passes_with_bootstrap_and_bge_metadata(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_manifest(tmp_path)
    monkeypatch.setattr(
        fvip,
        "_open_fact_vectors_collection",
        lambda _path: _FakeFactVectorCollection([_bge_meta(), _bge_meta()]),
    )

    artifact_dir = tmp_path / "run"
    receipt = fvip.build_fact_vector_index_preflight(
        section_id="competencies",
        artifact_dir=artifact_dir,
        repo_root=tmp_path,
        chroma_path=str(tmp_path / "chromadb"),
        product_hybrid_required=True,
    )

    assert receipt["status"] == fvip.STATUS_PASS
    assert receipt["section_coverage_present"] is True
    assert receipt["comparison_authority"] is True
    assert receipt["write_authority"] is False
    assert receipt["same_run_write_policy"] == "forbidden_for_product_retrieval"
    assert receipt["collection"]["collection_count"] == 2
    assert receipt["section_sufficiency"]["status"] == fvip.STATUS_PASS
    assert receipt["section_sufficiency"]["pre_run_hydration_present"] is True
    assert (artifact_dir / fvip.FACT_VECTOR_INDEX_PREFLIGHT_ARTIFACT).is_file()


def test_fact_vector_index_preflight_missing_when_manifest_absent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        fvip,
        "_open_fact_vectors_collection",
        lambda _path: _FakeFactVectorCollection([]),
    )

    receipt = fvip.build_fact_vector_index_preflight(
        section_id="competencies",
        repo_root=tmp_path,
        chroma_path=str(tmp_path / "chromadb"),
        product_hybrid_required=True,
    )

    assert receipt["status"] == fvip.STATUS_MISSING
    assert "bootstrap_manifest_missing" in receipt["reasons"]
    assert "fact_vectors_collection_empty" in receipt["reasons"]


def test_fact_vector_index_preflight_stale_on_non_bge_or_wrong_dim(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_manifest(tmp_path)
    stale_meta = _bge_meta()
    stale_meta["embedding_model_id"] = "legacy/model"
    stale_meta["embedding_dim"] = 384
    monkeypatch.setattr(
        fvip,
        "_open_fact_vectors_collection",
        lambda _path: _FakeFactVectorCollection([stale_meta]),
    )

    receipt = fvip.build_fact_vector_index_preflight(
        section_id="competencies",
        repo_root=tmp_path,
        chroma_path=str(tmp_path / "chromadb"),
        product_hybrid_required=True,
    )

    assert receipt["status"] == fvip.STATUS_STALE
    assert "fact_vectors_embedding_model_not_fully_bge_m3" in receipt["reasons"]
    assert "fact_vectors_embedding_dim_not_fully_1024" in receipt["reasons"]
    assert receipt["section_sufficiency"]["model_dim_pass"] is False


@pytest.mark.parametrize("section_id", direct_vector_section_ids())
def test_each_direct_vector_lane_has_common_section_sufficiency_gate(
    section_id: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_manifest(tmp_path)
    slot_requirements = {
        "unify_bullets": ("bul_unify", 6),
        "ibm_bullets": ("bul_ibm", 5),
        "insurtech_bullets": ("bul_insurtech", 3),
        "ey_bullets": ("bul_ey", 3),
    }
    prefix, count = slot_requirements.get(section_id, (f"fact_{section_id}", 1))
    metas = [
        _bge_meta(
            section_targets=section_id,
            source_document_id=f"{prefix}_{i:03d}",
        )
        for i in range(1, count + 1)
    ]
    monkeypatch.setattr(
        fvip,
        "_open_fact_vectors_collection",
        lambda _path: _FakeFactVectorCollection(metas),
    )

    receipt = fvip.build_fact_vector_index_preflight(
        section_id=section_id,
        repo_root=tmp_path,
        chroma_path=str(tmp_path / "chromadb"),
        product_hybrid_required=True,
    )

    sufficiency = receipt["section_sufficiency"]
    assert sufficiency["section_id"] == section_id
    assert sufficiency["known_generated_lane"] is True
    assert sufficiency["status"] == fvip.STATUS_PASS
    assert sufficiency["pre_run_hydration_present"] is True
    assert sufficiency["model_dim_pass"] is True


def test_narrative_preflight_uses_inherited_bullet_authority_without_chroma(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _unexpected_chroma_open(_path: str) -> Any:
        raise AssertionError("narrative preflight must not open fact_vectors")

    monkeypatch.setattr(fvip, "_open_fact_vectors_collection", _unexpected_chroma_open)

    receipt = fvip.build_fact_vector_index_preflight(
        section_id="unify_narrative",
        repo_root=tmp_path,
        chroma_path=str(tmp_path / "chromadb"),
        product_hybrid_required=False,
    )

    sufficiency = receipt["section_sufficiency"]
    assert receipt["status"] == fvip.STATUS_PASS
    assert receipt["reasons"] == []
    assert receipt["product_hybrid_required"] is False
    assert receipt["direct_fact_vector_required"] is False
    assert receipt["authority_mode"] == "inherited_bullet_proof"
    assert receipt["collection"]["skipped"] is True
    assert receipt["delayed_loop_policy"]["pre_run_fact_vector_index_required"] is False
    assert sufficiency["status"] == fvip.STATUS_PASS
    assert sufficiency["direct_fact_vector_required"] is False
    assert sufficiency["upstream_sections"] == ["unify_bullets"]


def test_unify_bullets_preflight_requires_all_six_source_slots_and_metric_graph(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_manifest(tmp_path)
    metas = [
        _bge_meta(
            section_targets="unify_bullets,unify_narrative",
            source_document_id=f"bul_unify_{i:03d}",
        )
        for i in range(1, 7)
    ]
    monkeypatch.setattr(
        fvip,
        "_open_fact_vectors_collection",
        lambda _path: _FakeFactVectorCollection(metas),
    )

    receipt = fvip.build_fact_vector_index_preflight(
        section_id="unify_bullets",
        repo_root=fvip.REPO_ROOT,
        chroma_path=str(tmp_path / "chromadb"),
        product_hybrid_required=True,
        role_family_key="PARTNER_APPLIED_AI_ARCHITECTURE",
    )

    unify = receipt["unify_bullets_sufficiency"]
    assert receipt["status"] == fvip.STATUS_PASS
    assert unify["status"] == fvip.STATUS_PASS
    assert unify["missing_source_fact_slots"] == []
    assert len(unify["slot_metric_outcome_ids"]) == 6
    assert unify["metric_distribution_pass"] is True
    assert unify["graph_traversal_pass"] is True
    assert unify["graph_granularity_pass"] is True


def test_unify_bullets_preflight_fails_when_any_slot_fact_vector_is_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_manifest(tmp_path)
    metas = [
        _bge_meta(
            section_targets="unify_bullets,unify_narrative",
            source_document_id=f"bul_unify_{i:03d}",
        )
        for i in range(1, 6)
    ]
    monkeypatch.setattr(
        fvip,
        "_open_fact_vectors_collection",
        lambda _path: _FakeFactVectorCollection(metas),
    )

    receipt = fvip.build_fact_vector_index_preflight(
        section_id="unify_bullets",
        repo_root=fvip.REPO_ROOT,
        chroma_path=str(tmp_path / "chromadb"),
        product_hybrid_required=True,
        role_family_key="PARTNER_APPLIED_AI_ARCHITECTURE",
    )

    unify = receipt["unify_bullets_sufficiency"]
    assert receipt["status"] == fvip.STATUS_MISSING
    assert "unify_bullets_fact_vector_sufficiency_missing" in receipt["reasons"]
    assert unify["status"] == fvip.STATUS_MISSING
    assert unify["missing_source_fact_slots"] == ["bul_unify_006"]


@pytest.mark.parametrize(
    ("section_id", "prefix", "expected_count"),
    [
        ("ibm_bullets", "bul_ibm", 5),
        ("insurtech_bullets", "bul_insurtech", 3),
        ("ey_bullets", "bul_ey", 5),
    ],
)
def test_role_episode_bullet_preflight_proves_selected_slots_and_rejected_frontier(
    section_id: str,
    prefix: str,
    expected_count: int,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    metas = [
        _bge_meta(
            section_targets=section_id,
            source_document_id=f"{prefix}_{i:03d}",
        )
        for i in range(1, expected_count + 1)
    ]
    monkeypatch.setattr(
        fvip,
        "_open_fact_vectors_collection",
        lambda _path: _FakeFactVectorCollection(metas),
    )

    receipt = fvip.build_fact_vector_index_preflight(
        section_id=section_id,
        repo_root=fvip.REPO_ROOT,
        chroma_path=str(tmp_path / "chromadb"),
        product_hybrid_required=True,
    )

    sufficiency = receipt["role_episode_bullets_sufficiency"]
    traversal = sufficiency["graph_traversal_receipt"]
    assert receipt["status"] == fvip.STATUS_PASS
    assert sufficiency["status"] == fvip.STATUS_PASS
    assert sufficiency["missing_source_fact_slots"] == []
    expected_slots = 5 if section_id == "ibm_bullets" else 3
    assert sufficiency["expected_slot_ids"] == [
        f"{prefix}_{i:03d}" for i in range(1, expected_slots + 1)
    ]
    assert len(sufficiency["slot_metric_outcome_ids"]) == expected_slots
    assert sufficiency["metric_distribution_pass"] is True
    assert sufficiency["graph_traversal_pass"] is True
    assert sufficiency["graph_granularity_pass"] is True
    assert traversal["selected_role_episode_root_count"] == expected_slots
    assert traversal["rejected_sibling_skill_count"] > 0
    assert traversal["rejected_sibling_metric_count"] > 0
    if section_id == "ey_bullets":
        assert sufficiency["extra_source_fact_slots"] == ["bul_ey_004", "bul_ey_005"]
        assert len(traversal["rejected_sibling_role_episode_bundle_ids"]) == 2
    else:
        assert sufficiency["extra_source_fact_slots"] == []
        expected_rejected = 5 if section_id == "ibm_bullets" else 9
        assert len(traversal["rejected_sibling_role_episode_bundle_ids"]) == expected_rejected


def test_role_episode_bullet_preflight_fails_when_expected_slot_vector_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    metas = [
        _bge_meta(section_targets="ey_bullets", source_document_id="bul_ey_001"),
        _bge_meta(section_targets="ey_bullets", source_document_id="bul_ey_002"),
        _bge_meta(section_targets="ey_bullets", source_document_id="bul_ey_004"),
        _bge_meta(section_targets="ey_bullets", source_document_id="bul_ey_005"),
    ]
    monkeypatch.setattr(
        fvip,
        "_open_fact_vectors_collection",
        lambda _path: _FakeFactVectorCollection(metas),
    )

    receipt = fvip.build_fact_vector_index_preflight(
        section_id="ey_bullets",
        repo_root=fvip.REPO_ROOT,
        chroma_path=str(tmp_path / "chromadb"),
        product_hybrid_required=True,
    )

    sufficiency = receipt["role_episode_bullets_sufficiency"]
    assert receipt["status"] == fvip.STATUS_MISSING
    assert "ey_bullets_fact_vector_sufficiency_missing" in receipt["reasons"]
    assert sufficiency["status"] == fvip.STATUS_MISSING
    assert sufficiency["missing_source_fact_slots"] == ["bul_ey_003"]
    assert sufficiency["extra_source_fact_slots"] == ["bul_ey_004", "bul_ey_005"]
