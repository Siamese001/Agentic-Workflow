"""Headline SRFS fact-ID namespace resolution and slice enforcement."""

from __future__ import annotations

from apps_rg.runtime.sections.headline_fact_id_resolution import (
    apply_headline_claim_ledger_fact_id_resolution,
    build_unify_alias_to_canonical_map,
    resolve_single_source_fact_id,
)
from apps_rg.runtime.sections.headline_lane import sync_selected_fact_plan_required_ids
from apps_rg.runtime.validators.headline_x2 import run_headline_x2_gates

CANONICAL_HL = (
    "SVP Engineering | Agentic AI Platforms | Distributed AI Infrastructure | Governed Enterprise Systems"
)

SRFS_ALLOWED = {
    "fact_engineering_platform_001",
    "fact_engineering_platform_003",
    "fact_engineering_platform_005",
}


def _runtime_payload() -> dict:
    facts = [
        {"fact_id": f"fact_engineering_platform_{i:03d}"} for i in range(1, 7)
    ]
    return {
        "selected_fact_plan": {
            "section_id": "headline",
            "facts": facts,
            "required_fact_ids": sorted(SRFS_ALLOWED),
        },
        "allowed_fact_ids": sorted(SRFS_ALLOWED),
    }


def _proof_pool_meta() -> dict:
    from apps_rg.runtime.product_evidence_authority import build_evidence_authority

    return {
        "proof_pool_type": "augmented_skills_graph",
        "evidence_authority": build_evidence_authority(
            graph_ref="apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
            ledger_ref="artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger.json",
            skills_authority_status="PASS",
        ),
        "selection_scope": {"is_proof_authority": False},
    }


def test_build_unify_alias_map_index_parity() -> None:
    remap = build_unify_alias_to_canonical_map(
        srfs_allowed_fact_ids=SRFS_ALLOWED,
        runtime_payload=_runtime_payload(),
    )
    assert remap["bul_unify_001"] == "fact_engineering_platform_001"
    assert remap["bul_unify_003"] == "fact_engineering_platform_003"
    assert remap["bul_unify_005"] == "fact_engineering_platform_005"


def test_resolve_bul_alias_to_canonical() -> None:
    remap = build_unify_alias_to_canonical_map(
        srfs_allowed_fact_ids=SRFS_ALLOWED,
        runtime_payload=_runtime_payload(),
    )
    canon, rec = resolve_single_source_fact_id(
        "bul_unify_003",
        remap=remap,
        srfs_allowed=SRFS_ALLOWED,
    )
    assert canon == "fact_engineering_platform_003"
    assert rec["allowed_by_srfs_slice"] is True
    assert rec["namespace_from"] == "unify_bullet_alias"


def test_unresolved_bul_when_canonical_not_in_slice() -> None:
    remap = build_unify_alias_to_canonical_map(
        srfs_allowed_fact_ids=SRFS_ALLOWED,
        runtime_payload=_runtime_payload(),
    )
    canon, rec = resolve_single_source_fact_id(
        "bul_unify_002",
        remap=remap,
        srfs_allowed=SRFS_ALLOWED,
    )
    assert canon is None
    assert rec["failure_reason"] == "unmapped_unify_bullet_alias"


def test_apply_resolution_persists_canonical_and_aliases() -> None:
    parsed = {
        "headline_line": CANONICAL_HL,
        "claim_ledger": [
            {
                "claim_text": "Governed platforms",
                "source_fact_ids": ["bul_unify_001", "bul_unify_005"],
            },
            {"claim_text": "Retrieval controls", "source_fact_ids": ["bul_unify_003"]},
        ],
        "selected_fact_plan": {"required_fact_ids": ["bul_unify_001", "bul_unify_003", "bul_unify_005"]},
    }
    out, receipt = apply_headline_claim_ledger_fact_id_resolution(
        parsed,
        srfs_allowed_fact_ids=SRFS_ALLOWED,
        runtime_payload=_runtime_payload(),
        proof_pool_metadata=_proof_pool_meta(),
    )
    assert receipt is not None
    assert receipt["resolution_status"] == "PASS"
    assert receipt["unresolved_alias_count"] == 0
    row0 = out["claim_ledger"][0]
    assert row0["source_fact_ids"] == [
        "fact_engineering_platform_001",
        "fact_engineering_platform_005",
    ]
    assert "bul_unify_001" in row0["raw_source_fact_aliases"]
    assert "bul_unify_005" in row0["raw_source_fact_aliases"]


def test_srfs_slice_gate_passes_after_alias_resolution() -> None:
    parsed = {
        "headline_line": CANONICAL_HL,
        "selected_fact_plan": {"section_id": "headline", "required_fact_ids": []},
        "claim_ledger": [
            {"claim_text": "Governed platforms", "source_fact_ids": ["bul_unify_001"]},
            {"claim_text": "Distributed infra", "source_fact_ids": ["bul_unify_005"]},
            {"claim_text": "Retrieval governance", "source_fact_ids": ["bul_unify_003"]},
        ],
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
        },
        "gap_notes": [],
        "change_log": [],
        "self_check": {"word_count": 10, "pipe_count": 3},
    }
    out, _receipt = apply_headline_claim_ledger_fact_id_resolution(
        parsed,
        srfs_allowed_fact_ids=SRFS_ALLOWED,
        runtime_payload=_runtime_payload(),
        proof_pool_metadata=_proof_pool_meta(),
    )
    sync_selected_fact_plan_required_ids(out, _runtime_payload(), SRFS_ALLOWED)
    gates = run_headline_x2_gates(
        headline_line=CANONICAL_HL,
        parsed_output=out,
        claim_ledger=list(out["claim_ledger"]),
        jd_text="enterprise platform",
        target_company="",
        target_title="SVP Engineering",
        resume_support_blob="{}",
        employer_names_lower=[],
        allowed_fact_ids=SRFS_ALLOWED,
        runtime_generation_status="REAL_LLM",
        srfs_source_fact_slice_gate_active=True,
        proof_pool_metadata=_proof_pool_meta(),
    )
    failed = [g.gate_id for g in gates if not g.pass_]
    assert "x2_headline_active_proof_pool_source_fact_ids" not in failed
    assert "x2_headline_source_fact_ids_within_srfs_slice" not in failed
    assert "x2_headline_source_supported" not in failed


def test_srfs_slice_gate_fails_on_unresolved_bul_without_crosswalk() -> None:
    """bul_unify_002 is not in SRFS slice — must not pass slice gate without mapping."""
    parsed = {
        "headline_line": CANONICAL_HL,
        "claim_ledger": [{"claim_text": "x", "source_fact_ids": ["bul_unify_002"]}],
        "selected_fact_plan": {"required_fact_ids": ["bul_unify_002"]},
    }
    out, receipt = apply_headline_claim_ledger_fact_id_resolution(
        parsed,
        srfs_allowed_fact_ids=SRFS_ALLOWED,
        runtime_payload=_runtime_payload(),
        proof_pool_metadata=_proof_pool_meta(),
    )
    assert receipt is not None
    assert receipt["unresolved_alias_count"] >= 1
    assert out["claim_ledger"] == []
    gates = run_headline_x2_gates(
        headline_line=CANONICAL_HL,
        parsed_output=out,
        claim_ledger=[],
        jd_text="",
        target_company="",
        resume_support_blob="{}",
        employer_names_lower=[],
        allowed_fact_ids=SRFS_ALLOWED,
        runtime_generation_status="REAL_LLM",
        srfs_source_fact_slice_gate_active=True,
        proof_pool_metadata=_proof_pool_meta(),
    )
    failed = [g.gate_id for g in gates if not g.pass_]
    assert (
        "x2_headline_claim_ledger_rows_present" in failed
        or "x2_headline_active_proof_pool_source_fact_ids" in failed
        or "x2_headline_source_fact_ids_within_srfs_slice" in failed
    )
