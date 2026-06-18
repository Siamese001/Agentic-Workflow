"""Pre–proof-pool targeting ingress for executive_summary."""

from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.runtime.sections.executive_summary_briefing import extract_briefing_signal_packet
from apps_rg.runtime.sections import executive_summary_briefing as briefing_mod
from apps_rg.runtime.ingress.executive_summary_targeting_ingress import (
    prepare_executive_summary_targeting_ingress,
)

REPO = Path(__file__).resolve().parents[5]


def test_ingress_bounds_briefing_before_pool_consumption() -> None:
    jd = "SVP engineering platform leadership"
    brief = (REPO / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md").read_text(
        encoding="utf-8"
    )
    ingress = prepare_executive_summary_targeting_ingress(
        jd_text=jd,
        briefing_raw=brief,
        target_title="SVP IT Strategy",
        repo_root=REPO,
    )
    assert len(ingress.briefing_text_bounded) <= len(brief)
    assert ingress.briefing_text_bounded
    assert ingress.role_family_key
    assert ingress.ingress_digest


def test_brown_briefing_passes_through_when_under_ingress_budget() -> None:
    """Compact Brown SSOT must not be section-trimmed at default ingress."""
    brief = (REPO / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md").read_text(
        encoding="utf-8"
    )
    assert len(brief) > 3_000
    ingress = prepare_executive_summary_targeting_ingress(
        jd_text="SVP IT Strategy",
        briefing_raw=brief,
        target_title="SVP IT Strategy",
        repo_root=REPO,
    )
    receipt = ingress.briefing_selection_receipt
    assert receipt is None or int(receipt.get("briefing_excluded_chars") or 0) == 0
    assert len(ingress.briefing_text_bounded) >= len(brief.strip()) - 32
    assert "integration" in ingress.briefing_text_bounded.lower()
    assert "R26_0000001653" in ingress.briefing_text_bounded


def test_ingress_exposes_briefing_signal_packet_for_prospective_lens() -> None:
    brief = (
        "## Company Strategy & Operating Pressure\n"
        "- The role must solve operating-model friction and clarify decision rights.\n\n"
        "## Leadership & Stakeholder Map\n"
        "- CEO, CIO, and business leaders need a tighter delivery cadence.\n\n"
        "## AI, Data, Platform, Architecture Signals\n"
        "- Platform modernization and architecture governance are forward-looking priorities.\n\n"
        "## Recent Events & Urgency\n"
        "- Recent integration pressure and roadmap changes create urgency.\n"
    )
    ingress = prepare_executive_summary_targeting_ingress(
        jd_text="SVP IT Strategy",
        briefing_raw=brief,
        target_title="SVP IT Strategy",
        repo_root=REPO,
    )
    packet = ingress.briefing_signal_packet
    assert packet["schema"] == "briefing_signal_packet_v1"
    assert packet["theme_counts"]["strategy"] >= 1
    assert packet["theme_counts"]["operating_model"] >= 1
    assert packet["theme_counts"]["leadership"] >= 1
    assert packet["theme_counts"]["forward_looking"] >= 1
    assert packet["theme_counts"]["urgency"] >= 1
    assert packet["dominant_themes"][0] in {"strategy", "operating_model"}


def test_ingress_preserves_raw_briefing_signal_packet_when_bounded_text_trims_tail(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(briefing_mod, "_max_chars", lambda: 180)
    brief = (
        "## Strategy\n"
        "- Strategy, mandate, pressure, operating model, and governance are the core themes "
        "for the first section and should consume most of the budget.\n\n"
        "## Operating Model\n"
        "- Decision rights and cadence need clarity.\n\n"
        "## Forward View\n"
        "- Roadmap and future-state operating model changes matter.\n"
    )
    ingress = prepare_executive_summary_targeting_ingress(
        jd_text="SVP IT Strategy",
        briefing_raw=brief,
        target_title="SVP IT Strategy",
        repo_root=REPO,
    )
    raw_packet = ingress.briefing_signal_packet
    bounded_packet = extract_briefing_signal_packet(ingress.briefing_text_bounded)
    assert raw_packet["theme_counts"]["strategy"] == 1
    assert bounded_packet["theme_counts"]["strategy"] == 0
    assert raw_packet["theme_counts"]["strategy"] > bounded_packet["theme_counts"]["strategy"]


def test_section_proof_loader_uses_briefing_override(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, str] = {}

    def _fake_resolve(**kwargs):  # type: ignore[no-untyped-def]
        captured["briefing_text"] = str(kwargs.get("briefing_text") or "")
        captured["jd_text"] = str(kwargs.get("jd_text") or "")
        from apps_rg.runtime.proof_pool_resolver import SectionProofPool

        return SectionProofPool(
            section="executive_summary",
            proof_source="augmented_skills_graph",
            proof_pool_ref="test",
            proof_pool_digest="test",
            selected_fact_plan={"facts": []},
            allowed_fact_ids_ordered=[],
            allowed_fact_ids=set(),
            bullet_rows=[],
            proof_pool_metadata={"graph_skills_proof_pool": True},
            fallback_used=False,
            base_resume_fallback_used=False,
            broad_skills_ledger_present=False,
            srfs_present=False,
            base_resume_json_ref="",
            base_resume_json_hash="",
            broad_skills_ledger_ref="",
            broad_skills_ledger_digest="",
            srfs_ref="",
            base_resume_override_used=False,
        )

    def _fake_front_spine(**kwargs):  # type: ignore[no-untyped-def]
        captured["front_briefing"] = str(kwargs.get("briefing_text_override") or "")
        from apps_rg.runtime.spine.front_contracts import SectionFrontSpineBridge

        return SectionFrontSpineBridge(
            section_id="executive_summary",
            validated_request=object(),
            l1_plan=object(),
            route=object(),
        )

    monkeypatch.setattr(
        "apps_rg.runtime.c0.section_proof_loader.resolve_section_proof_pool",
        _fake_resolve,
    )
    monkeypatch.setattr(
        "apps_rg.runtime.c0.section_proof_loader.build_section_front_spine_from_args",
        _fake_front_spine,
    )
    monkeypatch.setattr(
        "apps_rg.runtime.product_evidence_authority.enforce_product_evidence_authority_for_cli",
        lambda pool: pool,
    )
    monkeypatch.setattr(
        "apps_rg.runtime.c0.graph_story_authority.require_augmented_skills_graph_pool",
        lambda *a, **k: None,
    )
    monkeypatch.setattr(
        "apps_rg.runtime.c0.section_proof_loader.load_lane_base_resume_json",
        lambda **k: ({}, Path("."), "hash"),
    )

    from argparse import Namespace

    from apps_rg.runtime.c0.section_proof_loader import load_section_proof_for_lane

    args = Namespace(
        briefing="RAW-BRIEFING-15k" + ("z" * 15000),
        jd_text="jd-raw",
        target_company="Acme",
        target_title="SVP",
    )
    bounded = "BOUNDED-BRIEF"
    load_section_proof_for_lane(
        section_id="executive_summary",
        args=args,
        repo_root=REPO,
        briefing_text_override=bounded,
        jd_text_override="jd-bounded",
    )
    assert captured["briefing_text"] == bounded
    assert captured["jd_text"] == "jd-bounded"
    assert captured["front_briefing"] == bounded
