"""W3 — graph-weighted recipient-fit proof weighting.

Plan: apps-lic-completeness-graph-grounding-ssot-e7b2c4 (W3.1). Skipped when the
apps_rg shared graph artifact is unavailable (the bridge is fail-soft).
"""

from __future__ import annotations

import pytest

from apps_lic.engines.sender_proof_graph import (
    STATUS_PROOF_GRAPH_READY,
    build_sender_proof_graph_packet_from_store,
)
from apps_lic.engines.standing_sender_knowledge import load_standing_sender_corpus
from apps_lic.integrations.apps_rg_proof_bridge import (
    graph_weighted_skill_ids,
    load_apps_rg_proof_index,
    recipient_fit_weight,
)
from apps_lic.types.competitor_recon_agent_types import graph_weighted_candidate_skills
from tests.apps_lic.test_w5_sender_proof_graph import _gate, _store_for


def _require_shared_ssot():
    index = load_apps_rg_proof_index()
    if not index.available:
        pytest.skip(f"apps_rg shared proof SSOT unavailable: {index.load_error}")
    return index


def test_recipient_fit_weight_differs_technical_vs_executive() -> None:
    _require_shared_ssot()
    by_id = load_standing_sender_corpus().proof_by_id()
    commercial = by_id["sp_platform_commercialization"].apps_rg_skill_ids
    agentic = by_id["sp_agentic_platform"].apps_rg_skill_ids

    # Executive: business-outcome proof (commercialization) outweighs platform.
    ceo_commercial = recipient_fit_weight(apps_rg_skill_ids=commercial, recipient_class="CEO")
    ceo_agentic = recipient_fit_weight(apps_rg_skill_ids=agentic, recipient_class="CEO")
    assert ceo_commercial["weight"] > ceo_agentic["weight"]
    assert ceo_commercial["matched_family"] in {"PARTNERSHIPS_GTM", "REVENUE_OPERATIONS"}

    # Recruiter: technical role-fit proof; GTM commercialization does not fit.
    rec_commercial = recipient_fit_weight(apps_rg_skill_ids=commercial, recipient_class="RECRUITER")
    rec_agentic = recipient_fit_weight(apps_rg_skill_ids=agentic, recipient_class="RECRUITER")
    assert rec_agentic["weight"] > rec_commercial["weight"]
    assert rec_commercial["weight"] == 0.0


def test_unknown_recipient_class_yields_zero_fit() -> None:
    _require_shared_ssot()
    fit = recipient_fit_weight(apps_rg_skill_ids=["skill_partner_gtm_enablement"], recipient_class="??")
    assert fit["weight"] == 0.0


def test_graph_weighted_skill_ids_are_recipient_specific() -> None:
    _require_shared_ssot()
    recruiter = set(graph_weighted_skill_ids(recipient_class="RECRUITER", top_n=12))
    ceo = set(graph_weighted_skill_ids(recipient_class="CEO", top_n=12))
    assert recruiter and ceo
    # the two recipient lenses surface different top skills.
    assert recruiter != ceo


def test_live_packet_carries_graph_recipient_fit_signal() -> None:
    _require_shared_ssot()
    store = _store_for(
        title="Chief Executive Officer",
        company={"company": "AIG", "context": "Enterprise value creation from AI platform productization."},
        company_trigger={
            "trigger_text": "AIG announced an enterprise AI operating model.",
            "url": "https://example.com/aig-ai",
        },
    )
    derivation, gate = _gate(store, message_type_hint="trigger_based_insight")
    packet = build_sender_proof_graph_packet_from_store(
        store=store,
        recipient_derivation=derivation,
        message_gate_result=gate,
        campaign_objective="Enterprise AI operating-model insight.",
        company_context="AIG enterprise AI value creation.",
    )
    assert packet.status == STATUS_PROOF_GRAPH_READY and packet.ready
    reason_codes = {
        signal.reason_code
        for decision in packet.permission_decisions
        for signal in decision.relevance_signals
    }
    assert any(rc.startswith("graph_recipient_fit:") for rc in reason_codes)


def test_competitor_recon_candidate_skills_are_graph_weighted() -> None:
    _require_shared_ssot()
    recruiter = graph_weighted_candidate_skills(recipient_class="RECRUITER", top_n=6)
    ceo = graph_weighted_candidate_skills(recipient_class="CEO", top_n=6)
    assert recruiter, "expected graph-derived candidate skills (not an empty flat list)"
    assert ceo
    assert recruiter != ceo
