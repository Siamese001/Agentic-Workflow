"""Unit tests for upstream input contracts (PA INPUT FAMILIES 1-5)."""

from __future__ import annotations

from agentic_core.prompt_governance.prompt_assembly.input_contracts import (
    C0EvidenceContract,
    GovernanceArtifacts,
    L0RouteContract,
    L1PlanContract,
    UpstreamInputBundle,
    UserExecutionMetadata,
    upstream_bundle_from_dicts,
)


def test_l1_plan_defaults_are_empty_safe():
    p = L1PlanContract()
    assert p.plan_id == ""
    assert p.grounding_required is False
    assert p.declared_assumptions == ()


def test_l0_route_defaults():
    r = L0RouteContract()
    assert r.required_slots == ()
    assert r.fallback_chain == ()
    assert r.slo_budget == {}


def test_c0_evidence_defaults():
    e = C0EvidenceContract()
    assert e.support_score == 0.0
    assert e.evidence_classes == {}


def test_governance_defaults():
    g = GovernanceArtifacts()
    assert g.hitl_required is False
    assert g.durable_write_allowed is False


def test_user_execution_defaults_origin_user_turn():
    u = UserExecutionMetadata()
    assert u.origin_trust == "user_turn"
    assert u.executable_requested is True


def test_upstream_bundle_from_dicts_filters_unknown_keys():
    bundle = upstream_bundle_from_dicts(
        plan_contract={"plan_id": "p1", "extra_garbage_field": "x"},
        route_contract={"route_id": "R3"},
        evidence_contract={"status": "PASS", "support_score": 0.9},
        governance={"hitl_required": True},
        execution_metadata={"request_id": "rq1", "policy_hash": "ph"},
    )
    assert isinstance(bundle, UpstreamInputBundle)
    assert bundle.plan.plan_id == "p1"
    assert bundle.route.route_id == "R3"
    assert bundle.evidence.support_score == 0.9
    assert bundle.governance.hitl_required is True
    assert bundle.execution.request_id == "rq1"


def test_bundle_handles_none_inputs():
    b = upstream_bundle_from_dicts(plan_contract=None, route_contract=None)
    assert b.plan.plan_id == ""
    assert b.route.route_id == ""
