"""Contract: all seven canonical sections declare augmented skills graph as skills authority."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.fact_inventory.augmented_skills_graph import (
    SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
    SKILLS_SOURCE_TYPE_AUGMENTED_SKILLS_GRAPH,
    default_augmented_skills_graph_path,
    resolve_augmented_skills_graph_authority,
)
from apps_rg.fact_inventory.candidate_fact_ledger import default_ledger_path
from apps_rg.runtime.dispatch.input_authority_prompt_block import (
    format_input_authority_block,
    proof_pool_mode_from_metadata,
)
from apps_rg.runtime.proof_pool_resolver import (
    resolve_section_proof_pool,
    proof_pool_usage_ledger_extension,
)
from tests._apps_contract.graph_authority_test_support import product_proof_pool_metadata

REPO = Path(__file__).resolve().parents[2]
GRAPH_PATH = default_augmented_skills_graph_path(REPO)
CANDIDATE_LEDGER_PATH = default_ledger_path(REPO)

SECTION_IDS = (
    "headline",
    "executive_summary",
    "competencies",
    "unify_bullets",
    "unify_narrative",
    "ibm_bullets",
    "ibm_narrative",
)

FORBIDDEN_SKILLS_AUTHORITY_LABELS = (
    "broad skills ledger",
    "broad_skills_ledger as skills",
    "skills ledger as source of truth",
    "claim support pool (broad skills ledger)",
    "master_skills_arsenal as sole substrate for factual claims",
)


def _high_row(candidate_fact_id: str) -> dict:
    return {
        "candidate_fact_id": candidate_fact_id,
        "confidence": "HIGH",
        "claim_text": "Fixture claim for SRFS.",
        "metric_values": [],
        "capability_tags": ["platform"],
    }


def _srfs_doc(sections: dict[str, list[dict]]) -> dict:
    from apps_rg.fact_inventory.selected_role_fact_set import SECTION_KEYS

    out = {
        "selection_id": "augmented_skills_graph_contract",
        "selected_facts_by_section": {k: [] for k in SECTION_KEYS},
        "blocked_facts": [],
        "facts_requiring_human_confirmation": [],
        "unsupported_jd_needs": [],
    }
    for k, rows in sections.items():
        out["selected_facts_by_section"][k] = rows
    return out


def _assert_augmented_skills_authority(meta: dict) -> None:
    assert meta.get("source_authority") == SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH
    assert meta.get("skills_source_type") == SKILLS_SOURCE_TYPE_AUGMENTED_SKILLS_GRAPH
    assert meta.get("skills_authority_source_type") == SKILLS_SOURCE_TYPE_AUGMENTED_SKILLS_GRAPH
    assert meta.get("skills_authority_status") == "PASS"
    assert meta.get("claim_evidence_source_type")
    assert meta.get("claim_evidence_source_ref")
    assert meta.get("augmented_skills_graph_present") is True
    assert meta.get("graph_ref")
    assert meta.get("graph_digest")
    assert meta.get("graph_version")
    assert meta.get("skills_authority_graph_ref")
    assert meta.get("skills_authority_graph_digest")
    assert meta.get("legacy_broad_skills_ledger_skills_authority") is False
    assert meta.get("legacy_skills_ledger_role") == "deprecated_reference"


@pytest.mark.parametrize("section_id", SECTION_IDS)
def test_proof_pool_metadata_includes_augmented_skills_graph_authority(section_id: str) -> None:
    if not CANDIDATE_LEDGER_PATH.is_file():
        pytest.skip(f"candidate ledger missing: {CANDIDATE_LEDGER_PATH}")
    if not GRAPH_PATH.is_file():
        pytest.skip(f"augmented skills graph missing: {GRAPH_PATH}")
    pool = resolve_section_proof_pool(section=section_id, repo_root=REPO)
    meta = pool.proof_pool_metadata
    _assert_augmented_skills_authority(meta)
    if pool.proof_source == "broad_skills_ledger":
        assert meta.get("broad_skills_ledger_skills_authority") is False
        assert meta.get("broad_skills_ledger_claim_evidence_only") is True


@pytest.mark.parametrize("section_id", SECTION_IDS)
def test_usage_ledger_extension_skills_authority(section_id: str) -> None:
    if not CANDIDATE_LEDGER_PATH.is_file():
        pytest.skip(f"candidate ledger missing: {CANDIDATE_LEDGER_PATH}")
    pool = resolve_section_proof_pool(section=section_id, repo_root=REPO)
    ext = proof_pool_usage_ledger_extension(pool)
    assert ext.get("source_authority") == SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH
    ia = ext.get("input_authority") or {}
    assert ia.get("augmented_skills_graph") == "SKILLS_COMPETENCY_AUTHORITY"
    if pool.broad_skills_ledger_present:
        assert ia.get("broad_skills_ledger") == "CLAIM_EVIDENCE_ONLY_DEPRECATED_SKILLS_LABEL"
    eb = ext.get("evidence_boundary") or {}
    assert eb.get("skills_competency_authority") == "augmented_skills_graph"


@pytest.mark.parametrize("section_id", SECTION_IDS)
def test_prompt_input_authority_names_augmented_graph_not_ledger_ssot(section_id: str) -> None:
    if not CANDIDATE_LEDGER_PATH.is_file():
        pytest.skip(f"candidate ledger missing: {CANDIDATE_LEDGER_PATH}")
    pool = resolve_section_proof_pool(section=section_id, repo_root=REPO)
    meta = product_proof_pool_metadata(pool)
    assert proof_pool_mode_from_metadata(meta) == SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH
    block = format_input_authority_block(
        allowed_source_fact_ids=["bul_fixture_001"],
        skills_authority_metadata=meta,
    )
    lower = block.lower()
    assert "augmented skills graph" in lower
    assert "deprecated_reference" in lower or "deprecated" in lower
    for forbidden in FORBIDDEN_SKILLS_AUTHORITY_LABELS:
        assert forbidden not in lower


def test_negative_control_missing_graph_blocks_skills_authority(tmp_path: Path) -> None:
    missing = tmp_path / "no_augmented_graph.json"
    meta = resolve_augmented_skills_graph_authority(
        repo_root=REPO,
        graph_path=str(missing),
    )
    assert meta.get("skills_authority_status") == "BLOCKED"
    assert meta.get("augmented_skills_graph_present") is False
    assert meta.get("legacy_broad_skills_ledger_skills_authority") is False
    with pytest.raises(ValueError, match="evidence_authority"):
        format_input_authority_block(
            allowed_source_fact_ids=[],
            skills_authority_metadata=meta,
        )


def test_negative_control_resolver_does_not_fallback_skills_to_candidate_ledger(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Missing graph → BLOCKED skills metadata even when candidate fact ledger resolves."""
    if not CANDIDATE_LEDGER_PATH.is_file():
        pytest.skip(f"candidate ledger missing: {CANDIDATE_LEDGER_PATH}")
    missing_graph = tmp_path / "missing_augmented_graph.json"
    monkeypatch.setenv("APPS_RG_AUGMENTED_SKILLS_GRAPH_PATH", str(missing_graph))
    with pytest.raises(ValueError, match="graph-skills proof pool BLOCKED"):
        resolve_section_proof_pool(section="headline", repo_root=REPO)


def test_all_seven_sections_pass_same_source_authority_contract() -> None:
    if not CANDIDATE_LEDGER_PATH.is_file() or not GRAPH_PATH.is_file():
        pytest.skip("ledger or augmented skills graph artifact missing")
    failures: list[str] = []
    for section_id in SECTION_IDS:
        pool = resolve_section_proof_pool(section=section_id, repo_root=REPO)
        try:
            _assert_augmented_skills_authority(pool.proof_pool_metadata)
        except AssertionError as exc:
            failures.append(f"{section_id}: {exc}")
    assert not failures, "; ".join(failures)
