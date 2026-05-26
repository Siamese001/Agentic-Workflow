"""W3.1 — targeting binding digests (generation vs judge capsule parity)."""

from __future__ import annotations

import os

import pytest

from apps_rg.runtime.c0.exec_summary_graph_targeting_capsule import build_graph_targeting_capsule
from apps_rg.runtime.judges.executive_summary_judge_packet import build_executive_summary_judge_packet
from apps_rg.runtime.sections.executive_summary_targeting_publish import (
    enforce_targeting_parity_before_judge_panel,
    targeting_parity_strict_enforcement_enabled,
)
from apps_rg.runtime.targeting_context_authority import (
    GenerationMaterialContext,
    JudgeMaterialContext,
    MaterialTargetingBundle,
    build_targeting_binding_digest,
    evaluate_targeting_parity,
    material_targeting_digest,
)


def _capsule_a() -> dict:
    return build_graph_targeting_capsule(
        {"c03_selected_skill_ids": ["skill_platform_001", "skill_governance_002"], "selected_skills": []},
        role_family_key="platform_governance",
    )


def _capsule_b() -> dict:
    return build_graph_targeting_capsule(
        {"c03_selected_skill_ids": ["skill_other_999"], "selected_skills": []},
        role_family_key="other_family",
    )


def test_binding_digest_changes_when_capsule_differs() -> None:
    jd, br = "jd line", "brief line"
    d_a = build_targeting_binding_digest(
        target_title="SVP",
        target_company="Acme",
        jd_text=jd,
        briefing_text=br,
        graph_targeting_capsule=_capsule_a(),
    )
    d_b = build_targeting_binding_digest(
        target_title="SVP",
        target_company="Acme",
        jd_text=jd,
        briefing_text=br,
        graph_targeting_capsule=_capsule_b(),
    )
    assert d_a != d_b


def test_evaluate_targeting_parity_emits_w3_fields() -> None:
    jd, br = "same-jd", "same-brief"
    digest = material_targeting_digest(jd, br)
    gen = GenerationMaterialContext(jd, br, digest)
    judge = JudgeMaterialContext(jd, br, digest)
    cap = _capsule_a()
    bundle = MaterialTargetingBundle(
        authority_source_refs={},
        jd_text_frozen=jd,
        briefing_text_frozen=br,
        target_title="SVP",
        target_company="Acme",
        bundle_digest=digest,
    )
    receipt = evaluate_targeting_parity(
        generation=gen,
        judge=judge,
        bundle=bundle,
        graph_targeting_capsule_generation=cap,
        graph_targeting_capsule_judge=cap,
    )
    assert receipt["targeting_parity_status"] == "match"
    assert receipt["generation_targeting_digest"] == receipt["judge_targeting_digest"]
    assert receipt["target_title"] == "SVP"
    assert receipt["target_company"] == "Acme"


def test_capsule_mismatch_sets_targeting_parity_status_mismatch() -> None:
    jd, br = "jd", "br"
    digest = material_targeting_digest(jd, br)
    gen = GenerationMaterialContext(jd, br, digest)
    judge = JudgeMaterialContext(jd, br, digest)
    receipt = evaluate_targeting_parity(
        generation=gen,
        judge=judge,
        bundle=None,
        graph_targeting_capsule_generation=_capsule_a(),
        graph_targeting_capsule_judge=_capsule_b(),
    )
    assert receipt["targeting_parity_status"] == "mismatch"
    assert receipt["parity_match"] is False


def test_judge_packet_includes_graph_targeting_capsule() -> None:
    cap = _capsule_a()
    packet = build_executive_summary_judge_packet(
        resume_display_text="One sentence summary.",
        claim_ledger=[],
        allowed_fact_packet=[],
        allowed_fact_ids=set(),
        target_title="SVP",
        target_company="Acme",
        jd_text="jd",
        briefing_text="brief",
        parsed_output={},
        graph_targeting_capsule=cap,
    )
    stored = packet["targeting_context"]["graph_targeting_capsule"]
    assert stored["role_family_key"] == cap["role_family_key"]


def test_strict_mode_blocks_judge_panel_on_mismatch(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_TARGETING_PARITY_STRICT", "1")
    assert targeting_parity_strict_enforcement_enabled() is True
    ok, reason = enforce_targeting_parity_before_judge_panel(
        {"targeting_parity_status": "mismatch", "parity_match": False},
    )
    assert not ok
    assert "mismatch" in reason


def test_warn_only_when_strict_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_TARGETING_PARITY_STRICT", "0")
    ok, reason = enforce_targeting_parity_before_judge_panel(
        {"targeting_parity_status": "mismatch", "parity_match": False},
    )
    assert ok
    assert reason == "targeting_parity_warn_only"
