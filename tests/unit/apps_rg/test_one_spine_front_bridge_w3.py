"""Wave 3: section front-spine bridge must precede proof_pool (product-visible kill switch)."""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from apps_rg.runtime.proof_pool_resolver import resolve_section_proof_pool
from apps_rg.runtime.spine.front_contracts import (
    SectionFrontSpineBridge,
    SectionFrontSpinePreconditionError,
    activate_fixture_dev_bypass,
    build_section_front_spine_from_args,
    deactivate_fixture_dev_bypass,
    product_visible_kill_switch_enabled,
)

REPO = Path(__file__).resolve().parents[3]


def _args(**overrides: object) -> SimpleNamespace:
    base = {
        "target_company": "Acme Corp",
        "target_title": "VP Engineering",
        "target_role": "VP Engineering",
        "jd_text": "Lead platform engineering and agentic systems.",
        "briefing": "Emphasize regulated delivery.",
        "base_resume_ref": "",
        "selected_role_fact_set": "",
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_kill_switch_enabled_by_default():
    assert product_visible_kill_switch_enabled() is True


def test_proof_pool_blocked_without_front_spine_product_visible():
    with pytest.raises(SectionFrontSpinePreconditionError, match="missing SectionFrontSpineBridge"):
        resolve_section_proof_pool(
            section="competencies",
            repo_root=REPO,
            target_company="Acme",
            target_title="VP",
            product_visible=True,
        )


def test_proof_pool_blocked_without_validated_request_contract():
    bridge = build_section_front_spine_from_args(
        section_id="competencies",
        args=_args(),
        repo_root=REPO,
    )
    broken = SectionFrontSpineBridge(
        section_id="competencies",
        validated_request=None,
        l1_plan=bridge.l1_plan,
        route=bridge.route,
    )
    with pytest.raises(SectionFrontSpinePreconditionError, match="incomplete front spine"):
        resolve_section_proof_pool(
            section="competencies",
            repo_root=REPO,
            front_spine=broken,
            product_visible=True,
        )


def test_proof_pool_blocked_without_l1_plan():
    bridge = build_section_front_spine_from_args(
        section_id="competencies",
        args=_args(),
        repo_root=REPO,
    )
    broken = SectionFrontSpineBridge(
        section_id="competencies",
        validated_request=bridge.validated_request,
        l1_plan=None,
        route=bridge.route,
    )
    with pytest.raises(SectionFrontSpinePreconditionError, match="incomplete front spine"):
        resolve_section_proof_pool(
            section="competencies",
            repo_root=REPO,
            front_spine=broken,
            product_visible=True,
        )


def test_proof_pool_blocked_without_route_contract():
    bridge = build_section_front_spine_from_args(
        section_id="competencies",
        args=_args(),
        repo_root=REPO,
    )
    broken = SectionFrontSpineBridge(
        section_id="competencies",
        validated_request=bridge.validated_request,
        l1_plan=bridge.l1_plan,
        route=None,
    )
    with pytest.raises(SectionFrontSpinePreconditionError, match="incomplete front spine"):
        resolve_section_proof_pool(
            section="competencies",
            repo_root=REPO,
            front_spine=broken,
            product_visible=True,
        )


def test_fixture_bypass_requires_non_product_certified_kwarg():
    with pytest.raises(SectionFrontSpinePreconditionError, match="non_product_certified"):
        resolve_section_proof_pool(
            section="competencies",
            repo_root=REPO,
            product_visible=True,
            fixture_dev_only_bypass=True,
            non_product_certified=False,
        )


def test_fixture_dev_bypass_allows_resolve_without_front_spine():
    activate_fixture_dev_bypass(non_product_certified=True)
    try:
        pool = resolve_section_proof_pool(
            section="competencies",
            repo_root=REPO,
            product_visible=True,
        )
        assert pool.section == "competencies"
    finally:
        deactivate_fixture_dev_bypass()


def test_bridge_emits_three_contracts():
    bridge = build_section_front_spine_from_args(
        section_id="executive_summary",
        args=_args(),
        repo_root=REPO,
    )
    assert bridge.contracts_emitted() == {
        "ValidatedRequest": True,
        "L1PlanContract": True,
        "RouteContract": True,
    }
    assert bridge.is_canonical_c0_path is False
    assert "FinalEvidenceContract" in bridge.missing_downstream_contracts


def test_receipt_records_observed_chain_and_missing_downstream(tmp_path: Path):
    from apps_rg.runtime.spine.front_contracts import (
        build_section_front_spine_receipt,
        emit_section_front_spine_receipts,
    )

    bridge = build_section_front_spine_from_args(
        section_id="competencies",
        args=_args(),
        repo_root=REPO,
    )
    emit_section_front_spine_receipts(tmp_path, bridge)
    receipt = build_section_front_spine_receipt(bridge)
    assert receipt["contracts_emitted"]["ValidatedRequest"] is True
    assert receipt["fixture_dev_only"] is False
    assert receipt["canonical_c0_claimed"] is False
    assert receipt["canonical_exit_claimed"] is False
    assert receipt["proof_pool_entry_allowed"] is True
    assert receipt["precondition_status"] == "PASS"
    assert "section_front_spine_bridge" in receipt["observed_chain"]
    assert "FinalEvidenceContract" in receipt["missing_downstream_canonical_contracts"]
    vr = json.loads((tmp_path / "validated_request.json").read_text(encoding="utf-8"))
    assert vr["validation_status"] == "PASS"
    l1 = json.loads((tmp_path / "l1_plan_contract.json").read_text(encoding="utf-8"))
    assert l1["validated_request_ref"] == "validated_request.json"
    route = json.loads((tmp_path / "route_contract.json").read_text(encoding="utf-8"))
    assert route["l1_plan_contract_ref"] == "l1_plan_contract.json"
    assert route.get("execution_form")
