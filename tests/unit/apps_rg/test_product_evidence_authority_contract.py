"""Contract: product evidence authority law — canonical CLI cannot reach forbidden authority states."""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from apps_rg.runtime.product_evidence_authority import (
    EVIDENCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
    ProductEvidenceAuthorityError,
    build_evidence_authority,
    enforce_product_evidence_authority_for_cli,
    finalize_product_section_proof_pool,
    scan_prompt_text_for_forbidden_story_authority,
    validate_compiled_prompt_story_authority,
    validate_proof_pool_metadata_product_law,
)
from apps_rg.runtime.proof_pool_resolver import (
    PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH,
    SectionProofPool,
)
from apps_rg.runtime.section_cli_defaults import SectionCliConfigError

REPO = Path(__file__).resolve().parents[3]


def _valid_pool(*, meta: dict | None = None) -> SectionProofPool:
    base_meta = {
        "proof_pool_type": "augmented_skills_graph",
        "skills_authority_status": "PASS",
        "graph_ref": "apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
        "graph_digest": "abc",
        "claim_evidence_substrate_ref": "artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger.json",
        "selection_method": "augmented_skills_graph_headline",
    }
    if meta:
        base_meta.update(meta)
    return SectionProofPool(
        section="headline",
        proof_source=PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH,
        proof_pool_ref=base_meta["graph_ref"],
        proof_pool_digest="digest",
        selected_fact_plan={"facts": [], "selection_method": base_meta["selection_method"]},
        allowed_fact_ids_ordered=[],
        allowed_fact_ids=set(),
        bullet_rows=[],
        proof_pool_metadata=base_meta,
        fallback_used=False,
        base_resume_fallback_used=False,
        broad_skills_ledger_present=False,
        srfs_present=False,
        base_resume_json_ref="apps_rg/resume/base/amit_ayer_base_resume_v1.json",
        base_resume_json_hash="hash",
        broad_skills_ledger_ref="artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger.json",
        broad_skills_ledger_digest="led",
        srfs_ref="",
        base_resume_override_used=False,
        targeting_inputs_used={"jd_title_company": True, "briefing": False},
    )


@pytest.mark.parametrize(
    "forbidden_authority",
    [
        "selected_role_fact_set",
        "base_resume_fallback",
        "broad_skills_ledger",
    ],
)
def test_validate_rejects_forbidden_evidence_authority(forbidden_authority: str) -> None:
    ea = build_evidence_authority(
        graph_ref="g.json",
        ledger_ref="l.json",
        skills_authority_status="PASS",
    )
    ea["authority"] = forbidden_authority
    with pytest.raises(ProductEvidenceAuthorityError, match="forbidden evidence_authority"):
        validate_proof_pool_metadata_product_law(
            {
                "evidence_authority": ea,
                "selection_scope": {"is_proof_authority": False},
                "layout_context": {"story_claim_authority": False},
            },
            section_id="headline",
        )


def test_validate_requires_graph_and_ledger_refs() -> None:
    with pytest.raises(ProductEvidenceAuthorityError, match="graph_ref required"):
        validate_proof_pool_metadata_product_law(
            {
                "evidence_authority": build_evidence_authority(
                    graph_ref="",
                    ledger_ref="ledger.json",
                    skills_authority_status="PASS",
                ),
                "selection_scope": {"is_proof_authority": False},
                "layout_context": {"story_claim_authority": False},
            },
            section_id="unify_bullets",
        )


def test_validate_rejects_blocked_graph() -> None:
    with pytest.raises(ProductEvidenceAuthorityError, match="BLOCKED"):
        validate_proof_pool_metadata_product_law(
            {
                "evidence_authority": build_evidence_authority(
                    graph_ref="g.json",
                    ledger_ref="l.json",
                    skills_authority_status="BLOCKED",
                    block_reason="missing_file",
                ),
                "selection_scope": {"is_proof_authority": False},
                "layout_context": {"story_claim_authority": False},
            },
            section_id="ibm_bullets",
        )


def test_finalize_attaches_three_concepts() -> None:
    pool = finalize_product_section_proof_pool(_valid_pool())
    meta = pool.proof_pool_metadata
    assert meta["evidence_authority"]["authority"] == EVIDENCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH
    assert meta["evidence_authority"]["graph_ref"]
    assert meta["evidence_authority"]["ledger_ref"]
    assert meta["selection_scope"]["is_proof_authority"] is False
    assert meta["layout_context"]["story_claim_authority"] is False
    assert meta["proof_pool_type_role"] == "receipt_label_not_authority_switch"


def test_legacy_proof_pool_type_srfs_rejected() -> None:
    pool = _valid_pool(meta={"proof_pool_type": "selected_role_fact_set", "selected_role_fact_set_used": True})
    with pytest.raises(ProductEvidenceAuthorityError, match="selected_role_fact_set"):
        finalize_product_section_proof_pool(pool)


def test_prompt_scan_detects_base_resume_story_authority() -> None:
    hits = scan_prompt_text_for_forbidden_story_authority(
        "Use base resume as claim authority for all bullets."
    )
    assert hits
    with pytest.raises(ProductEvidenceAuthorityError):
        validate_compiled_prompt_story_authority(
            "Story evidence from base resume only.",
            section_id="unify_bullets",
        )


def test_resolve_product_pool_has_evidence_authority(repo_root: Path | None = None) -> None:
    root = repo_root or REPO
    from apps_rg.runtime.proof_pool_resolver import resolve_section_proof_pool

    pool = resolve_section_proof_pool(
        section="headline",
        target_company="Acme",
        target_role="VP Engineering",
        jd_text="lead platform teams",
        briefing_text="brief",
        repo_root=root,
        product_visible=True,
        fixture_dev_only_bypass=True,
        non_product_certified=True,
    )
    ea = pool.proof_pool_metadata.get("evidence_authority") or {}
    assert ea.get("authority") == EVIDENCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH
    assert ea.get("graph_ref")
    assert ea.get("ledger_ref")
    assert ea.get("skills_authority_status") == "PASS"


def test_load_section_proof_for_lane_enforces_law(monkeypatch: pytest.MonkeyPatch) -> None:
    bad = _valid_pool(meta={"proof_pool_type": "base_resume_fallback", "fallback_used": True})
    monkeypatch.setattr(
        "apps_rg.runtime.c0.section_proof_loader.resolve_section_proof_pool",
        lambda **_kw: bad,
    )
    monkeypatch.setattr(
        "apps_rg.runtime.c0.section_proof_loader.build_section_front_spine_from_args",
        lambda **_kw: MagicMock(),
    )
    monkeypatch.setattr(
        "apps_rg.runtime.c0.section_proof_loader.load_lane_base_resume_json",
        lambda **_kw: ({}, Path("x"), "h"),
    )

    from apps_rg.runtime.c0.section_proof_loader import load_section_proof_for_lane

    args = SimpleNamespace(
        base_resume_ref="",
        target_company="Co",
        target_title="Role",
        target_role="Role",
        jd_text="jd",
        briefing="brief",
    )
    with pytest.raises(ProductEvidenceAuthorityError):
        load_section_proof_for_lane(
            section_id="headline",
            args=args,
            repo_root=REPO,
        )


def test_legacy_broad_skills_ledger_flag_raises_product_error() -> None:
    from apps_rg.runtime.proof_pool_resolver import resolve_section_proof_pool

    with pytest.raises(ProductEvidenceAuthorityError, match="legacy_broad_skills_ledger"):
        resolve_section_proof_pool(
            section="headline",
            legacy_broad_skills_ledger=True,
            product_visible=True,
            fixture_dev_only_bypass=True,
            non_product_certified=True,
            repo_root=REPO,
        )


def test_blocked_graph_raises_product_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "apps_rg.runtime.proof_pool_resolver.resolve_augmented_skills_graph_authority",
        lambda **_kw: {
            "skills_authority_status": "BLOCKED",
            "skills_authority_block_reason": "test_missing_graph",
            "graph_ref": "",
        },
    )
    from apps_rg.runtime.proof_pool_resolver import resolve_section_proof_pool

    with pytest.raises(ProductEvidenceAuthorityError, match="BLOCKED"):
        resolve_section_proof_pool(
            section="headline",
            product_visible=True,
            fixture_dev_only_bypass=True,
            non_product_certified=True,
            repo_root=REPO,
        )


def test_main_returns_2_when_proof_pool_law_violated(monkeypatch: pytest.MonkeyPatch) -> None:
    """Canonical CLI path maps ProductEvidenceAuthorityError to exit 2."""
    monkeypatch.setattr(
        "apps_rg.runtime.live_judge_only_guard.assert_production_runtime",
        lambda **_kw: None,
    )

    def _boom(**_kw: object) -> dict:
        raise ProductEvidenceAuthorityError("headline: forbidden evidence_authority 'srfs'")

    monkeypatch.setattr(
        "apps_rg.runtime.orchestration.canonical_dispatch.run_canonical_apps_rg_from_cli_primitives",
        _boom,
    )
    monkeypatch.setattr(
        "apps_rg.runtime.pre_dispatch_preflight.enforce_pre_dispatch_preflight",
        lambda **_kw: SimpleNamespace(
            dispatch_started=True,
            jd_status="PASS",
            manual_brief_status="PASS",
            qwen_health_status="PASS",
            qwen_model_ready_status="PASS",
        ),
    )
    monkeypatch.setattr(
        "apps_rg.runtime.pre_dispatch_preflight.evaluate_jd_cli_input",
        lambda _jd: ("PASS", REPO / "tests" / "_fixtures" / "ci-probe-jd.txt"),
    )
    monkeypatch.setattr(
        "apps_rg.runtime.pre_dispatch_preflight.evaluate_manual_brief_cli_input",
        lambda _b: ("PASS", REPO / "tests" / "_fixtures" / "ci-probe-briefing.txt"),
    )

    from apps_rg.__main__ import main

    rc = main(
        [
            "--section",
            "headline",
            "--target-company",
            "CI-Co",
            "--target-role",
            "Engineer",
            "--jd",
            str(REPO / "tests" / "_fixtures" / "ci-probe-jd.txt"),
            "--manual-brief",
            str(REPO / "tests" / "_fixtures" / "ci-probe-briefing.txt"),
        ]
    )
    assert rc == 2


def test_product_evidence_error_is_section_cli_config_error() -> None:
    assert issubclass(ProductEvidenceAuthorityError, SectionCliConfigError)


@pytest.mark.parametrize(
    "section_id",
    [
        "headline",
        "executive_summary",
        "competencies",
        "unify_bullets",
        "unify_narrative",
        "ibm_bullets",
        "ibm_narrative",
    ],
)
def test_all_product_sections_attach_evidence_authority(section_id: str) -> None:
    from apps_rg.runtime.proof_pool_resolver import resolve_section_proof_pool

    pool = resolve_section_proof_pool(
        section=section_id,
        target_company="Acme",
        target_role="VP Engineering",
        jd_text="platform leadership",
        briefing_text="brief",
        repo_root=REPO,
        product_visible=True,
        fixture_dev_only_bypass=True,
        non_product_certified=True,
    )
    meta = pool.proof_pool_metadata
    assert meta["evidence_authority"]["authority"] == EVIDENCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH
    assert meta["selection_scope"]["is_proof_authority"] is False
    assert meta["layout_context"]["story_claim_authority"] is False
    assert meta.get("selected_role_fact_set_used") is False


def test_proof_source_from_metadata_uses_evidence_authority() -> None:
    from apps_rg.runtime.validators.proof_pool_source_fact_validation import proof_source_from_metadata

    src = proof_source_from_metadata(
        {
            "evidence_authority": build_evidence_authority(
                graph_ref="g.json",
                ledger_ref="l.json",
                skills_authority_status="PASS",
            ),
            "proof_pool_type": "selected_role_fact_set",
        }
    )
    assert src == "augmented_skills_graph"


def test_proof_source_from_metadata_rejects_legacy_pool_type_without_ea() -> None:
    from apps_rg.runtime.validators.proof_pool_source_fact_validation import proof_source_from_metadata

    with pytest.raises(ValueError, match="not product authority"):
        proof_source_from_metadata({"proof_pool_type": "broad_skills_ledger"})


@pytest.mark.parametrize(
    "forbidden_pool_label",
    [
        "prompt_pool",
        "proof_pool",
        "legacy_pool",
        "fallback_pool",
        "base_resume",
        "unknown",
    ],
)
def test_validate_rejects_forbidden_proof_pool_type_labels(forbidden_pool_label: str) -> None:
    with pytest.raises(ProductEvidenceAuthorityError, match="not product authority"):
        validate_proof_pool_metadata_product_law(
            {
                "proof_pool_type": forbidden_pool_label,
                "evidence_authority": build_evidence_authority(
                    graph_ref="g.json",
                    ledger_ref="l.json",
                    skills_authority_status="PASS",
                ),
                "selection_scope": {"is_proof_authority": False},
                "layout_context": {"story_claim_authority": False},
            },
            section_id="unify_narrative",
        )


def test_validate_rejects_missing_ledger_ref() -> None:
    with pytest.raises(ProductEvidenceAuthorityError, match="ledger_ref required"):
        validate_proof_pool_metadata_product_law(
            {
                "evidence_authority": build_evidence_authority(
                    graph_ref="g.json",
                    ledger_ref="",
                    skills_authority_status="PASS",
                ),
                "selection_scope": {"is_proof_authority": False},
                "layout_context": {"story_claim_authority": False},
            },
            section_id="ibm_narrative",
        )


def test_validate_rejects_empty_evidence_authority_block() -> None:
    with pytest.raises(ProductEvidenceAuthorityError, match="missing evidence_authority"):
        validate_proof_pool_metadata_product_law(
            {
                "selection_scope": {"is_proof_authority": False},
                "layout_context": {"story_claim_authority": False},
            },
            section_id="competencies",
        )


def test_validate_rejects_srfs_as_proof_authority_flag() -> None:
    pool = _valid_pool(meta={"selected_role_fact_set_used": True})
    with pytest.raises(ProductEvidenceAuthorityError, match="selected_role_fact_set_used"):
        finalize_product_section_proof_pool(pool)


def test_validate_rejects_base_resume_fallback_flag() -> None:
    with pytest.raises(ProductEvidenceAuthorityError, match="base_resume_fallback"):
        validate_proof_pool_metadata_product_law(
            {
                "evidence_authority": build_evidence_authority(
                    graph_ref="g.json",
                    ledger_ref="l.json",
                    skills_authority_status="PASS",
                ),
                "selection_scope": {"is_proof_authority": False},
                "layout_context": {"story_claim_authority": False},
                "base_resume_fallback_used": True,
            },
            section_id="headline",
        )


def test_product_section_receipt_authority_shape() -> None:
    from apps_rg.runtime.product_evidence_authority import product_section_receipt_authority

    pool = finalize_product_section_proof_pool(_valid_pool())
    receipt = product_section_receipt_authority(pool.proof_pool_metadata)
    assert receipt["evidence_authority"]["type"] == EVIDENCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH
    assert receipt["evidence_authority"]["graph_ref"] == "present"
    assert receipt["evidence_authority"]["ledger_ref"] == "present"
    forbidden = {
        "selected_role_fact_set",
        "base_resume_fallback",
        "broad_skills_ledger",
        "prompt_pool",
        "proof_pool",
    }
    assert forbidden.isdisjoint(set(receipt.keys()))


def test_compiled_input_authority_requires_evidence_authority_block() -> None:
    from apps_rg.runtime.dispatch.input_authority_prompt_block import format_input_authority_block

    with pytest.raises(ValueError, match="evidence_authority"):
        format_input_authority_block(
            allowed_source_fact_ids=["f1"],
            skills_authority_metadata={"proof_pool_type": "augmented_skills_graph"},
        )


def test_legacy_broad_skills_resolver_functions_deleted() -> None:
    import apps_rg.runtime.proof_pool_resolver as ppr

    for name in (
        "_allocate_from_ledger",
        "_collect_base_resume_bullets",
        "_build_competencies_ledger_plan",
        "_ledger_company_hint_slice",
    ):
        assert not hasattr(ppr, name), name


def test_x2_gate_rejects_srfs_in_evidence_authority_not_pool_type() -> None:
    from apps_rg.runtime.c0.graph_story_authority import x2_gate_graph_only_proof_pool

    ok, obs, exp, _ = x2_gate_graph_only_proof_pool(
        {
            "evidence_authority": {
                "authority": "selected_role_fact_set",
                "graph_ref": "g.json",
                "ledger_ref": "l.json",
                "skills_authority_status": "PASS",
            },
            "proof_pool_type": "augmented_skills_graph",
        },
        section_id="ibm_bullets",
    )
    assert ok is False
    assert obs == "selected_role_fact_set"
    assert exp == EVIDENCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH


def test_x2_gate_flags_product_path_disables_srfs_slice() -> None:
    from apps_rg.runtime.product_evidence_authority import x2_proof_pool_gate_flags

    pool_active, srfs_slice = x2_proof_pool_gate_flags(
        {
            "evidence_authority": build_evidence_authority(
                graph_ref="g.json",
                ledger_ref="l.json",
                skills_authority_status="PASS",
            ),
        }
    )
    assert pool_active is True
    assert srfs_slice is False


def test_proof_pool_x2_gate_id_is_active_pool_only() -> None:
    from apps_rg.runtime.validators.proof_pool_source_fact_validation import proof_pool_x2_gate_id

    meta = {
        "evidence_authority": build_evidence_authority(
            graph_ref="g.json",
            ledger_ref="l.json",
            skills_authority_status="PASS",
        ),
        "proof_pool_type": "selected_role_fact_set",
    }
    assert (
        proof_pool_x2_gate_id(
            "headline",
            proof_pool_metadata=meta,
            srfs_slice_gate_active=True,
        )
        == "x2_headline_active_proof_pool_source_fact_ids"
    )
    assert "within_srfs_slice" not in proof_pool_x2_gate_id("competencies", srfs_slice_gate_active=True)


def test_normalized_reporting_never_marks_srfs_authority() -> None:
    from apps_rg.runtime.sections.selected_role_fact_set import normalized_srfs_section_reporting_fields

    fields = normalized_srfs_section_reporting_fields(
        section_id="headline",
        runtime_payload={
            "proof_pool_metadata": {
                "evidence_authority": build_evidence_authority(
                    graph_ref="g.json",
                    ledger_ref="l.json",
                    skills_authority_status="PASS",
                ),
                "selection_scope": {"is_proof_authority": False},
                "allowed_fact_ids_count": 3,
            }
        },
        x2_gates=[],
        selected_fact_plan={"required_fact_ids": ["f1"]},
        claim_ledger=[],
    )
    assert fields["selected_role_fact_set_used"] is False
    assert fields["proof_pool_type"] == "augmented_skills_graph"
    assert fields["x2_srfs_gate_status"] == "NOT_APPLICABLE"


def test_x2_gate_ignores_proof_pool_type_without_evidence_authority() -> None:
    from apps_rg.runtime.c0.graph_story_authority import x2_gate_graph_only_proof_pool

    ok, obs, exp, _ = x2_gate_graph_only_proof_pool(
        {
            "proof_pool_type": "selected_role_fact_set",
            "skills_authority_status": "PASS",
            "graph_ref": "g.json",
            "claim_evidence_substrate_ref": "l.json",
        },
        section_id="ibm_bullets",
    )
    assert ok is False
    assert obs == "missing"
    assert exp == EVIDENCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH
