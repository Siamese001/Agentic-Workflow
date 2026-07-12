"""apps-test-model: APP CONTRACT.

P0 closure tests for apps_rg L1 planning integrity, readiness, and C0 wiring.
"""

from __future__ import annotations

import ast
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from agentic_core.L0_routing.u0_intake_validator import AuthorityValidationReceipt
from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.final_evidence_contract import (
    FinalEvidenceContract,
    SUPPORT_STATUS_PASS,
)
from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from apps_rg.runtime.bindings.c0_binding import C0EvidenceGapError
from apps_rg.runtime.bindings.c0_planned_binding import c0_retrieve_apps_rg_planned
from apps_rg.runtime.bindings.l0_binding import l0_route_apps_rg
from apps_rg.runtime.bindings.l0_route_evidence import L1PlanNotReadyError
from apps_rg.runtime.bindings.l1_binding import l1_plan_apps_rg
from apps_rg.runtime.bindings.pa_planned_binding import pa_compose_apps_rg_planned
from apps_rg.runtime.bindings.l1_plan_evidence import build_validation_receipt_id
from apps_rg.runtime.bindings.l1_planning_capsule import (
    PlanningCapsuleIntegrityError,
    PlanningProfileIntegrityError,
    build_apps_rg_l1_planning_capsule,
    stable_capsule_digest,
    verify_apps_rg_l1_planning_capsule,
)
from apps_rg.runtime.bindings.u0_profile_manifest import (
    l1_planning_profile_digest,
    l1_planning_profile_ref,
)

REPO_ROOT = Path(__file__).resolve().parents[3]


def _auth() -> AuthorityValidationReceipt:
    return AuthorityValidationReceipt(
        validation_timestamp=datetime.now(timezone.utc).isoformat(),
    )


def _profile_manifest() -> dict[str, str]:
    return {
        "l1_planning_profile_ref": l1_planning_profile_ref(),
        "l1_planning_profile_digest": l1_planning_profile_digest(
            allow_missing=False
        ),
        "manifest_digest": "f" * 64,
    }


def _app_payload(
    *,
    generation_mode: str = "strategic_tailor",
    target_role: str = "VP Engineering",
    job_description_text: str = "Lead AI platform strategy.",
    source_resume_text: str = "Built governed AI infrastructure.",
    section_id: str = "",
) -> dict[str, Any]:
    task_spec: dict[str, Any] = {
        "generation_mode": generation_mode,
        "task_class": "resume_generation",
        "capability_requirements": ["needs_strong_narrative"],
    }
    constraints: dict[str, Any] = {}
    if section_id:
        task_spec["section_id"] = section_id
        constraints["section_id"] = section_id
    return {
        "non_product_certified": True,
        "target_company": "Acme Corp",
        "target_role": target_role,
        "target_level": "EXECUTIVE",
        "job_description_text": job_description_text,
        "source_resume_text": source_resume_text,
        "generation_mode": generation_mode,
        "task_spec": task_spec,
        "query_spec": {
            "jd_hash": "a" * 64,
            "resume_hash": "b" * 64,
            "target": {
                "company": "Acme Corp",
                "role": target_role,
                "level": "EXECUTIVE",
            },
        },
        "support_expectation": {
            "provenance_required": True,
            "fact_checked_required": True,
            "per_bullet_required": True,
            "source_quote_required": True,
        },
        "output_expectation": {
            "formats": ["json", "markdown"],
            "provenance_required": True,
            "fact_checked_required": True,
        },
        "user_constraints": constraints,
        "profile_manifest": _profile_manifest(),
    }


def _validated(**payload_kwargs: Any) -> ValidatedRequest:
    mode = str(payload_kwargs.get("generation_mode") or "strategic_tailor")
    return ValidatedRequest(
        request_id=f"req-p0-{mode}",
        run_id="run-l1-p0",
        app_id="apps_rg",
        task_class="resume_generation",
        payload_digest="e" * 64,
        authority_validation_receipt=_auth(),
        trace_id="trace-l1-p0",
        tenant_id="tenant-l1",
        replay_key="replay-l1-p0",
        l5_certification_ref="test:valid:w6",
        app_payload=_app_payload(**payload_kwargs),
    )


def _thaw(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_thaw(item) for item in value]
    return value


def test_capsule_and_contract_projections_are_recursively_immutable() -> None:
    plan = l1_plan_apps_rg(_validated())
    capsule = plan.task_spec["apps_rg_planning_capsule"]

    with pytest.raises(TypeError):
        plan.task_spec["new"] = "value"  # type: ignore[index]
    with pytest.raises(TypeError):
        capsule["intent_frame"]["target_role"] = "tampered"  # type: ignore[index]
    with pytest.raises(TypeError):
        capsule["completion_criteria"].append("tampered")


def test_contract_rejects_tampered_capsule_even_when_declared_ref_is_unchanged() -> None:
    good = l1_plan_apps_rg(_validated())
    tampered = _thaw(good.task_spec["apps_rg_planning_capsule"])
    tampered["intent_frame"]["target_role"] = "Tampered Role"
    task_spec = dict(good.task_spec)
    task_spec["apps_rg_planning_capsule"] = tampered

    with pytest.raises(ValueError, match="planning capsule digest mismatch"):
        L1PlanContract(
            request_id=good.request_id,
            run_id=good.run_id,
            app_id=good.app_id,
            trace_id=good.trace_id,
            task_spec=task_spec,
            l5_certification_ref="test:valid:w6",
        )


def test_capsule_verifier_rejects_tampered_copy() -> None:
    plan = l1_plan_apps_rg(_validated())
    tampered = _thaw(plan.task_spec["apps_rg_planning_capsule"])
    tampered["planning_status"] = "BLOCKED"

    with pytest.raises(PlanningCapsuleIntegrityError):
        verify_apps_rg_l1_planning_capsule(tampered)


def test_capsule_verifier_rechecks_exact_profile_bytes() -> None:
    plan = l1_plan_apps_rg(_validated())
    tampered = _thaw(plan.task_spec["apps_rg_planning_capsule"])
    tampered["planning_prior_refs"][0]["digest"] = "0" * 64
    tampered["capsule_digest"] = stable_capsule_digest(tampered)

    with pytest.raises(PlanningCapsuleIntegrityError, match="planning prior ref/digest"):
        verify_apps_rg_l1_planning_capsule(tampered)


def _planned_fec(plan: L1PlanContract) -> FinalEvidenceContract:
    capsule_ref = str(plan.task_spec["apps_rg_planning_capsule_ref"])
    return FinalEvidenceContract(
        request_id=plan.request_id,
        run_id=plan.run_id,
        app_id=plan.app_id,
        trace_id=plan.trace_id,
        l5_certification_ref=plan.l5_certification_ref,
        support_status=SUPPORT_STATUS_PASS,
        support_target_met=True,
        final_evidence_digest="d" * 64,
        retrieval_plan_ref=f"l1_evidence_plan:1234567890abcdef:capsule:{capsule_ref[:24]}",
        audit_refs=(f"l1_capsule_digest:{capsule_ref[:24]}",),
    )


def test_planned_c0_wrapper_threads_verified_plan(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    plan = l1_plan_apps_rg(_validated())
    route = l0_route_apps_rg(plan)
    observed: dict[str, Any] = {}

    def _fake_c0(route_arg, request_arg, *, l1_plan, **kwargs):
        observed["route"] = route_arg
        observed["request"] = request_arg
        observed["plan"] = l1_plan
        observed["kwargs"] = kwargs
        return _planned_fec(l1_plan)

    monkeypatch.setattr(
        "apps_rg.runtime.bindings.c0_planned_binding.c0_retrieve_apps_rg",
        _fake_c0,
    )
    request = _validated()
    fec = c0_retrieve_apps_rg_planned(
        route,
        request,
        l1_plan=plan,
        chroma_path=None,
    )

    assert observed["plan"] is plan
    assert observed["route"] is route
    assert observed["request"] is request
    assert fec.retrieval_plan_ref


def test_planned_c0_wrapper_rejects_missing_capsule_lineage(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    plan = l1_plan_apps_rg(_validated())
    route = l0_route_apps_rg(plan)

    def _fake_c0(*_args, **_kwargs):
        return FinalEvidenceContract(
            request_id=plan.request_id,
            run_id=plan.run_id,
            app_id=plan.app_id,
            trace_id=plan.trace_id,
            l5_certification_ref=plan.l5_certification_ref,
            support_status=SUPPORT_STATUS_PASS,
            support_target_met=True,
            final_evidence_digest="e" * 64,
        )

    monkeypatch.setattr(
        "apps_rg.runtime.bindings.c0_planned_binding.c0_retrieve_apps_rg",
        _fake_c0,
    )
    with pytest.raises(C0EvidenceGapError, match="retrieval_plan_ref"):
        c0_retrieve_apps_rg_planned(route, _validated(), l1_plan=plan)


def test_planned_pa_wrapper_rejects_missing_capsule_consumption(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    plan = l1_plan_apps_rg(_validated())
    route = l0_route_apps_rg(plan)
    fec = _planned_fec(plan)

    monkeypatch.setattr(
        "apps_rg.runtime.bindings.pa_planned_binding.pa_compose_apps_rg",
        lambda *_args, **_kwargs: SimpleNamespace(
            component_hash_map={},
            slot_lineage_map={},
        ),
    )
    with pytest.raises(PlanningCapsuleIntegrityError, match="component hashes"):
        pa_compose_apps_rg_planned(route, plan, fec, _validated())


def test_profile_ref_is_bound_to_exact_loaded_bytes() -> None:
    payload = _app_payload()
    with pytest.raises(PlanningProfileIntegrityError, match="ref/digest mismatch"):
        build_apps_rg_l1_planning_capsule(
            app_payload=payload,
            request_id="req-stale",
            run_id="run-stale",
            trace_id="trace-stale",
            replay_key="replay-stale",
            planning_profile_ref=l1_planning_profile_ref(),
            planning_profile_digest="0" * 64,
        )


def test_profile_ref_cannot_escape_approved_apps_rg_profiles_root() -> None:
    with pytest.raises(PlanningProfileIntegrityError, match="apps_rg/profiles"):
        build_apps_rg_l1_planning_capsule(
            app_payload=_app_payload(),
            request_id="req-path",
            run_id="run-path",
            trace_id="trace-path",
            replay_key="replay-path",
            planning_profile_ref="AGENTS.md",
            planning_profile_digest="0" * 64,
        )


def test_l0_route_digest_and_signature_bind_the_exact_capsule(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APPS_RG_ROUTE_HMAC_SECRET", "p0-test-secret")
    first_plan = l1_plan_apps_rg(_validated(target_role="VP Engineering"))
    second_plan = l1_plan_apps_rg(_validated(target_role="Chief Architect"))

    first_route = l0_route_apps_rg(first_plan)
    second_route = l0_route_apps_rg(second_plan)

    assert first_route.route_id == second_route.route_id
    assert first_route.route_digest != second_route.route_digest
    assert first_route.hmac_sig != second_route.hmac_sig
    first_capsule_digest = first_plan.task_spec["apps_rg_planning_capsule_ref"]
    assert f"l1_capsule_digest:{first_capsule_digest}" in first_route.snapshot_refs
    assert any(
        ref.startswith("l1_plan_binding_digest:")
        for ref in first_route.snapshot_refs
    )


def test_ready_plan_emits_l0_owned_readiness_gate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APPS_RG_ROUTE_HMAC_SECRET", "p0-test-secret")
    route = l0_route_apps_rg(l1_plan_apps_rg(_validated()))
    receipts = {receipt.gate_id: receipt for receipt in route.route_gate_receipts}

    assert receipts["G_L1_PLAN_READY"].verdict == "PASS"
    assert "l1_plan_ready=PASS" in route.reason_codes


def test_blocking_ambiguity_sets_required_hitl_and_cannot_leave_l0(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APPS_RG_ROUTE_HMAC_SECRET", "p0-test-secret")
    plan = l1_plan_apps_rg(
        _validated(
            generation_mode="strategic_tailor",
            job_description_text="",
        )
    )
    capsule = plan.task_spec["apps_rg_planning_capsule"]

    assert capsule["planning_status"] == "BLOCKED"
    assert capsule["ambiguity_register"]["blocks_progress"] is True
    assert capsule["route_feature_hints"]["hitl_risk_hint"] == "required"
    assert plan.route_hints["hitl_posture"] == "required"
    with pytest.raises(L1PlanNotReadyError) as exc:
        l0_route_apps_rg(plan)
    assert exc.value.receipt.gate_id == "G_L1_PLAN_READY"
    assert exc.value.receipt.verdict == "FAIL"


def test_generate_scratch_does_not_block_only_because_source_resume_is_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APPS_RG_ROUTE_HMAC_SECRET", "p0-test-secret")
    plan = l1_plan_apps_rg(
        _validated(
            generation_mode="generate_scratch",
            source_resume_text="",
        )
    )
    capsule = plan.task_spec["apps_rg_planning_capsule"]
    codes = {
        entry["code"] for entry in capsule["ambiguity_register"]["entries"]
    }

    assert "SOURCE_RESUME_EMPTY" not in codes
    assert capsule["planning_status"] == "READY"
    assert l0_route_apps_rg(plan).route_digest


def test_validation_receipt_is_bound_to_capsule_digest() -> None:
    first = build_validation_receipt_id(
        request_id="req",
        profile_manifest_digest="manifest",
        planning_profile_digest="profile",
        capsule_digest="sha256:first",
    )
    second = build_validation_receipt_id(
        request_id="req",
        profile_manifest_digest="manifest",
        planning_profile_digest="profile",
        capsule_digest="sha256:second",
    )
    assert first != second


def _find_call(tree: ast.AST, function_name: str) -> ast.Call:
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = func.id if isinstance(func, ast.Name) else (
            func.attr if isinstance(func, ast.Attribute) else ""
        )
        if name == function_name:
            return node
    raise AssertionError(f"call {function_name!r} not found")


def test_canonical_ag2_threads_plan_into_verified_c0_boundary() -> None:
    path = REPO_ROOT / "agentic_core/runtime/entry/apps_rg_dispatch.py"
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    call = _find_call(tree, "c0_retrieve_apps_rg")

    assert "apps_rg.runtime.bindings.c0_planned_binding" in source
    assert "apps_rg.runtime.bindings.pa_planned_binding" in source
    _find_call(tree, "pa_compose_apps_rg")
    assert any(
        keyword.arg == "l1_plan"
        and isinstance(keyword.value, ast.Name)
        and keyword.value.id == "plan"
        for keyword in call.keywords
    )


def test_section_spine_threads_front_plan_into_verified_c0_boundary() -> None:
    path = REPO_ROOT / "apps_rg/runtime/spine/section_c0_retrieve.py"
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    call = _find_call(tree, "c0_retrieve_apps_rg")

    assert "c0_retrieve_apps_rg = c0_retrieve_apps_rg_planned" in source
    assert any(
        keyword.arg == "l1_plan"
        and isinstance(keyword.value, ast.Attribute)
        and keyword.value.attr == "l1_plan"
        for keyword in call.keywords
    )
