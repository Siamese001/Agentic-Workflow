"""apps-test-model: APP CONTRACT."""

from __future__ import annotations

import ast
import re
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from agentic_core.L0_routing.u0_intake_validator import AuthorityValidationReceipt
from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.final_evidence_contract import (
    EvidenceItem,
    FinalEvidenceContract,
    SUPPORT_STATUS_PASS,
)
from apps_rg.runtime.bindings.l0_binding import l0_route_apps_rg
from apps_rg.runtime.bindings.l1_binding import l1_plan_apps_rg
from apps_rg.runtime.bindings.l1_planning_capsule import (
    build_apps_rg_l1_planning_capsule,
)
from apps_rg.runtime.bindings.c0_binding import c0_retrieve_apps_rg
from apps_rg.runtime.bindings.pa_binding import pa_compose_apps_rg
from apps_rg.runtime.bindings.u0_profile_manifest import (
    l1_planning_profile_digest,
    l1_planning_profile_ref,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
FORBIDDEN_ROUTE_AUTHORITY_KEYS = {
    "route_id",
    "route_family",
    "execution_form",
    "selected_route_reason",
    "route_digest",
}


def _auth() -> AuthorityValidationReceipt:
    return AuthorityValidationReceipt(
        validation_timestamp=datetime.now(timezone.utc).isoformat(),
    )


def _profile_manifest() -> dict[str, str]:
    return {
        "l1_planning_profile_ref": l1_planning_profile_ref(),
        "l1_planning_profile_digest": l1_planning_profile_digest(allow_missing=False),
        "manifest_digest": "f" * 64,
    }


def _app_payload(*, generation_mode: str = "strategic_tailor", section_id: str = "") -> dict[str, Any]:
    constraints: dict[str, Any] = {}
    task_spec: dict[str, Any] = {
        "generation_mode": generation_mode,
        "task_class": "resume_generation",
        "capability_requirements": ["needs_strong_narrative"],
    }
    if section_id:
        constraints["section_id"] = section_id
        task_spec["section_id"] = section_id
    return {
        "non_product_certified": True,
        "target_company": "Acme Corp",
        "target_role": "VP Engineering",
        "target_level": "EXECUTIVE",
        "job_description_text": "Lead AI platform strategy.",
        "source_resume_text": "Built governed AI infrastructure.",
        "generation_mode": generation_mode,
        "task_spec": task_spec,
        "query_spec": {
            "jd_hash": "a" * 64,
            "resume_hash": "b" * 64,
            "target": {
                "company": "Acme Corp",
                "role": "VP Engineering",
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


def _validated(*, generation_mode: str = "strategic_tailor", section_id: str = "") -> ValidatedRequest:
    return ValidatedRequest(
        request_id=f"req-{generation_mode}-{section_id or 'all'}",
        run_id="run-l1-capsule",
        app_id="apps_rg",
        task_class="resume_generation",
        payload_digest="e" * 64,
        authority_validation_receipt=_auth(),
        trace_id="trace-l1-capsule",
        tenant_id="tenant-l1",
        replay_key="replay-l1-capsule",
        l5_certification_ref="test:valid:w6",
        app_payload=_app_payload(generation_mode=generation_mode, section_id=section_id),
    )


def _fec() -> FinalEvidenceContract:
    return FinalEvidenceContract(
        request_id="req-strategic_tailor-all",
        run_id="run-l1-capsule",
        app_id="apps_rg",
        trace_id="trace-l1-capsule",
        l5_certification_ref="test:valid:w6",
        support_status=SUPPORT_STATUS_PASS,
        support_target_met=True,
        final_evidence_digest="d" * 64,
        evidence_items=(
            EvidenceItem(
                source="fact:one",
                content="Built governed AI infrastructure.",
                source_type="fixture",
                support_status=SUPPORT_STATUS_PASS,
            ),
        ),
    )


def _walk_keys(payload: Any) -> set[str]:
    if isinstance(payload, dict):
        keys = set(payload)
        for value in payload.values():
            keys.update(_walk_keys(value))
        return keys
    if isinstance(payload, list):
        keys: set[str] = set()
        for value in payload:
            keys.update(_walk_keys(value))
        return keys
    return set()


def test_l1_planning_capsule_digest_is_stable_for_same_input() -> None:
    payload = _app_payload()
    kwargs = {
        "app_payload": payload,
        "request_id": "req-stable",
        "run_id": "run-stable",
        "trace_id": "trace-stable",
        "replay_key": "replay-stable",
        "planning_profile_ref": l1_planning_profile_ref(),
        "planning_profile_digest": l1_planning_profile_digest(allow_missing=False),
    }

    first = build_apps_rg_l1_planning_capsule(**kwargs)
    second = build_apps_rg_l1_planning_capsule(**kwargs)

    assert first == second
    assert first["capsule_digest"].startswith("sha256:")
    assert first["capsule_digest"] == second["capsule_digest"]


def test_l1_ambiguity_register_has_no_random_id() -> None:
    plan_a = l1_plan_apps_rg(_validated())
    plan_b = l1_plan_apps_rg(_validated())
    register = dict(plan_a.ambiguity_register)

    assert plan_a.ambiguity_register == plan_b.ambiguity_register
    assert not re.match(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        str(register["register_id"]),
    )
    assert register["register_digest"].startswith("sha256:")


def test_l1_capsule_contains_no_route_authority_keys() -> None:
    plan = l1_plan_apps_rg(_validated())
    capsule = plan.task_spec["apps_rg_planning_capsule"]

    assert not (FORBIDDEN_ROUTE_AUTHORITY_KEYS & _walk_keys(capsule))
    assert not (FORBIDDEN_ROUTE_AUTHORITY_KEYS & set(plan.route_hints))


def test_l1_binding_and_capsule_do_not_import_downstream_authority_modules() -> None:
    forbidden = {
        "c0_binding",
        "pa_binding",
        "l2_binding",
        "ManagedWorkflowRunner",
        "provider_gateway",
        "openai",
        "anthropic",
        "httpx",
        "requests",
    }
    for rel in (
        "apps_rg/runtime/bindings/l1_binding.py",
        "apps_rg/runtime/bindings/l1_planning_capsule.py",
    ):
        tree = ast.parse((REPO_ROOT / rel).read_text(encoding="utf-8"), filename=rel)
        imports: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module or "")
        offenders = [name for name in imports if any(part in name for part in forbidden)]
        assert offenders == []


@pytest.mark.parametrize("mode", ["strategic_tailor", "tailor_existing", "generate_scratch"])
def test_l1_capsule_full_resume_modes_emit_work_units_and_completion_criteria(mode: str) -> None:
    plan = l1_plan_apps_rg(_validated(generation_mode=mode))
    capsule = plan.task_spec["apps_rg_planning_capsule"]

    assert len(capsule["work_units"]) >= 5
    assert capsule["completion_criteria"]
    assert capsule["route_feature_hints"]["multi_work_unit"] is True
    assert plan.route_hints["multi_work_unit_hint"] == "true"


def test_l1_capsule_section_regen_emits_narrow_work_unit() -> None:
    plan = l1_plan_apps_rg(
        _validated(generation_mode="section_regen", section_id="executive_summary")
    )
    capsule = plan.task_spec["apps_rg_planning_capsule"]

    assert [unit["unit_id"] for unit in capsule["work_units"]] == ["executive_summary"]
    assert capsule["route_feature_hints"]["multi_work_unit"] is False
    assert plan.route_hints["multi_work_unit_hint"] == "false"


def test_l1_cognition_plan_is_requested_not_executed() -> None:
    plan = l1_plan_apps_rg(_validated())
    cognition_plan = plan.task_spec["apps_rg_planning_capsule"]["cognition_plan"]

    assert cognition_plan
    for row in cognition_plan:
        assert row["controls_applied"] is False
        assert row["execution_provability"] == "ADVISORY_ONLY_UNTIL_L2_RECEIPT"
        assert row["authority_class"] == "L2_OR_L3_MUST_PROVE_EXECUTION"


def test_l0_route_receipt_references_l1_capsule_digest() -> None:
    plan = l1_plan_apps_rg(_validated())
    route = l0_route_apps_rg(plan)
    capsule_ref = plan.task_spec["apps_rg_planning_capsule_ref"][:24]

    assert f"l1_capsule_digest:{capsule_ref}" in route.reason_codes
    assert any(ref.startswith("l1_route_features:") for ref in route.reason_codes)
    assert any(ref.startswith("l1_completion_criteria:") for ref in route.reason_codes)
    assert any(ref.startswith("l1_work_units:") for ref in route.reason_codes)
    assert any(ref.startswith("l1_evidence_plan_ref:") for ref in route.reason_codes)


def test_c0_receipt_references_l1_evidence_plan_when_supplied(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APPS_RG_TEST_HARNESS", "1")
    monkeypatch.setenv("APPS_RG_C0_DENSE_SPARSE_MANDATORY", "0")
    monkeypatch.setenv("APPS_RG_C0_SPARSE_ENABLED", "0")
    monkeypatch.setenv("CHROMA_PERSIST_DIR", "")
    vr = _validated()
    plan = l1_plan_apps_rg(vr)
    route = l0_route_apps_rg(plan)

    fec = c0_retrieve_apps_rg(route, vr, chroma_path=None, l1_plan=plan)

    assert fec.retrieval_plan_ref.startswith("l1_evidence_plan:")
    assert plan.task_spec["apps_rg_planning_capsule_ref"][:24] in fec.retrieval_plan_ref
    assert any(ref.startswith("l1_capsule_digest:") for ref in fec.audit_refs)
    assert any(ref.startswith("l1_evidence_plan_digest:") for ref in fec.audit_refs)


def test_pa_component_hash_map_references_l1_capsule_and_prompt_plan(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APPS_RG_GOVERNED_PA_SKIP", "1")
    vr = _validated()
    plan = l1_plan_apps_rg(vr)
    route = l0_route_apps_rg(plan)
    artifact = pa_compose_apps_rg(route, plan, _fec(), vr)

    for key in (
        "l1_planning_capsule",
        "l1_prompt_plan",
        "l1_completion_criteria",
        "l1_cognition_plan_requested",
    ):
        assert key in artifact.component_hash_map
        assert len(artifact.component_hash_map[key]) == 64
    assert "L1_PLAN_PROJECTIONS" in artifact.slot_lineage_map["l1_planning_capsule"]


def test_governed_pa_component_hash_map_references_l1_capsule(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("APPS_RG_GOVERNED_PA_SKIP", raising=False)
    vr = _validated()
    plan = l1_plan_apps_rg(vr)
    route = l0_route_apps_rg(plan)
    artifact = pa_compose_apps_rg(route, plan, _fec(), vr)

    assert "l1_planning_capsule" in artifact.component_hash_map
    assert "l1_prompt_plan" in artifact.component_hash_map
    assert "L1_PLAN_PROJECTIONS" in artifact.slot_lineage_map["l1_planning_capsule"]
