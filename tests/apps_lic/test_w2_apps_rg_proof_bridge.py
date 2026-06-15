"""W2 — apps_rg shared-SSOT proof bridge + live LicGraphAdapter + provenance.

Plan: apps-lic-completeness-graph-grounding-ssot-e7b2c4 (W2.1 + W2.2).

These tests are skipped when the apps_rg shared graph artifact is unavailable in
the environment (the bridge is fail-soft by design); they assert the live,
grounded path when it is present.
"""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.adapter_registry import (
    AdapterResolutionStatus,
    resolve_graph_adapter,
)
from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.contracts import (
    AnchorCandidate,
    AnchorType,
)
from apps_lic.engines.sender_proof_graph import (
    STATUS_CLAIMS_PASS,
    STATUS_PROOF_GRAPH_READY,
    build_pa_sender_proof_envelope,
    build_sender_proof_graph_packet_from_store,
    validate_l2_sender_claims_against_packet,
)
from apps_lic.integrations.apps_rg_proof_bridge import (
    PERMISSION_ALLOW,
    load_apps_rg_proof_index,
    proof_provenance_for,
)
from apps_lic.integrations.c0_graph_adapter import LicGraphAdapter
from tests.apps_lic.test_w5_sender_proof_graph import _gate, _store_for


def _require_shared_ssot():
    index = load_apps_rg_proof_index()
    if not index.available:
        pytest.skip(f"apps_rg shared proof SSOT unavailable: {index.load_error}")
    return index


# --------------------------------------------------------------------------
# W2: bridge projects the apps_rg shared SSOT
# --------------------------------------------------------------------------


def test_bridge_projects_approved_proof_points_with_lineage() -> None:
    index = _require_shared_ssot()
    assert index.graph_source == "apps_rg.augmented_skills_graph.v1"
    assert index.graph_version and index.graph_version != "unavailable"
    approved = [p for p in index.skills_by_id.values() if p.permission == PERMISSION_ALLOW]
    assert approved, "expected at least one approved (allow) apps_rg skill proof"
    # every approved skill carries fact lineage we can cite as provenance.
    assert any(p.fact_id_links for p in approved)


# --------------------------------------------------------------------------
# W2.1: LicGraphAdapter is live over the shared SSOT (no agentic_core edit)
# --------------------------------------------------------------------------


def test_generic_registry_resolves_lic_adapter_without_core_edit() -> None:
    result = resolve_graph_adapter("apps_lic.integrations.c0_graph_adapter")
    assert result.status == AdapterResolutionStatus.RESOLVED
    assert isinstance(result.adapter, LicGraphAdapter)


def test_lic_adapter_returns_real_neighbors_with_lineage_and_permission() -> None:
    index = _require_shared_ssot()
    adapter = LicGraphAdapter()
    assert adapter.health_check().healthy is True
    assert adapter.get_projection_manifest().is_stale is False

    skill_id = next(
        sid
        for sid, p in index.skills_by_id.items()
        if p.fact_id_links and p.permission == PERMISSION_ALLOW
    )
    resolved = adapter.resolve_anchor(
        AnchorCandidate(anchor_value=skill_id, anchor_type=AnchorType.UNKNOWN, original_evidence_id="ev"),
        {},
    )
    # ResolvedGraphAnchor (not Unresolved) for a real skill node.
    assert getattr(resolved, "resolved_node_id", "") == skill_id

    neighbors = adapter.get_neighbors(skill_id, (), {}, 5)
    assert neighbors, "expected real fact-lineage neighbors, not an empty stub"
    fact_neighbor = neighbors[0]
    assert fact_neighbor.relation_type == "EVIDENCE"
    assert fact_neighbor.lineage_refs  # source lineage present
    # apps_lic projection identity; apps_rg is the underlying source.
    assert fact_neighbor.graph_source == "apps_lic.knowledge_graph.v1"
    assert fact_neighbor.source_type == index.graph_source


# --------------------------------------------------------------------------
# W2.2: live proof packet carries grounded apps_rg provenance + gate passes
# --------------------------------------------------------------------------


def test_grounded_lane_carries_apps_rg_provenance_and_gate_passes() -> None:
    _require_shared_ssot()
    store = _store_for(
        title="Senior Technical Recruiter",
        company={"company": "AIG", "context": "Regulated insurer expanding agentic AI governance."},
        jd={
            "title": "Director, AI Platforms",
            "requisition_number": "JR-12345",
            "company": "AIG",
            "description": "Build production agentic AI platforms for regulated workflows.",
        },
    )
    derivation, gate = _gate(store, message_type_hint="role_specific")
    packet = build_sender_proof_graph_packet_from_store(
        store=store,
        recipient_derivation=derivation,
        message_gate_result=gate,
        campaign_objective="Ask for resume review for the Director AI Platforms role.",
        company_context="AIG regulated insurance AI platform work.",
        desired_next_step="resume review",
    )
    assert packet.status == STATUS_PROOF_GRAPH_READY and packet.ready

    # Every selected outbound proof claim carries grounded apps_rg SSOT provenance.
    assert packet.proof_ids
    for proof_id in packet.proof_ids:
        prov = packet.apps_rg_provenance[proof_id]
        assert prov["ssot_available"] is True
        assert prov["ssot_grounded"] is True
        assert prov["permission"] == PERMISSION_ALLOW
        assert prov["resolved_skill_ids"], "expected resolved apps_rg skill ids"

    envelope = build_pa_sender_proof_envelope(packet)
    assert envelope["apps_rg_provenance"]
    assert set(envelope["apps_rg_provenance"]) == set(packet.proof_ids)

    # The evidence-support gate now passes on this grounded lane.
    validation = validate_l2_sender_claims_against_packet(packet.proof_ids, packet=packet)
    assert validation.status == STATUS_CLAIMS_PASS
    assert set(validation.allowed_claim_ids) == set(packet.proof_ids)
    assert not validation.blocked_claims


def test_provenance_is_failsoft_for_unknown_references() -> None:
    # Unknown references never claim grounding even when the SSOT is present.
    prov = proof_provenance_for(source_ids=["not_a_real_fact"], skill_tags=["nope"])
    assert prov["ssot_available"] in (True, False)
    if prov["ssot_available"]:
        assert prov["ssot_grounded"] is False
    assert prov["permission"] != PERMISSION_ALLOW
