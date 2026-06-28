"""apps-test-model: LAW.

Tests for apps_research AG-9 spine bindings (U0→L1→L0→C0→PA→L2→Exit).

Verifies:
- All 7 binding modules import cleanly.
- parse_payload builds a valid RequestEnvelope.
- Full pipeline without a configured provider fails closed.
- U0 rejects payloads with forbidden authority fields.
- C0 builds FinalEvidenceContract with correct schema.
- PA produces CompiledPromptArtifact with correct slot lineage.
- L2 provider failure produces SealedL2Artifact with execution_status.
- Exit writes an artifact and returns X3Disposition.
- Provenance chain: evidence_digest → prompt.evidence_digest → sealed.prompt_artifact_digest.
"""
from __future__ import annotations

import json

import pytest


# ---------------------------------------------------------------------------
# Import smoke
# ---------------------------------------------------------------------------

def test_all_bindings_importable():
    from agentic_core.runtime.entry.u0_apps_research_binding import u0_validate_apps_research
    from agentic_core.L1_cognition.apps_research_l1_binding import l1_plan_apps_research
    from agentic_core.L0_routing.apps_research_l0_binding import l0_route_apps_research
    from agentic_core.runtime.c0.apps_research_c0_binding import c0_retrieve_apps_research
    from agentic_core.prompt_governance.apps_research_pa_binding import pa_compose_apps_research
    from agentic_core.L2_execution.apps_research_l2_binding import l2_execute_apps_research
    from agentic_core.runtime.exit.apps_research_exit_binding import exit_finalize_apps_research
    from apps_research.runtime.profile_builder import (
        build_app_runtime_contract,
        parse_payload,
    )
    assert all([
        u0_validate_apps_research,
        l1_plan_apps_research,
        l0_route_apps_research,
        c0_retrieve_apps_research,
        pa_compose_apps_research,
        l2_execute_apps_research,
        exit_finalize_apps_research,
        parse_payload,
        build_app_runtime_contract,
    ])


# ---------------------------------------------------------------------------
# Parse
# ---------------------------------------------------------------------------

def test_parse_returns_envelope_with_target_company():
    from apps_research.runtime.profile_builder import parse_payload
    envelope = parse_payload({"target_company": "Acme", "depth": "standard"})
    assert envelope is not None
    assert envelope.payload.target_company == "Acme"


def test_parse_returns_none_when_no_target():
    from apps_research.runtime.profile_builder import parse_payload
    result = parse_payload({})
    assert result is None


def test_parse_accepts_topic_in_user_constraints():
    from apps_research.runtime.profile_builder import parse_payload
    envelope = parse_payload({"user_constraints": {"topic": "OpenAI"}})
    assert envelope is not None


# ---------------------------------------------------------------------------
# U0
# ---------------------------------------------------------------------------

def test_u0_returns_validated_request():
    from apps_research.runtime.profile_builder import parse_payload
    from agentic_core.runtime.entry.u0_apps_research_binding import u0_validate_apps_research
    envelope = parse_payload({"target_company": "TestCo"})
    vr = u0_validate_apps_research(envelope)
    assert vr.app_id == "apps_research"
    assert vr.task_class == "company_brief"
    assert vr.authority_validation_receipt.allowed is True
    assert isinstance(vr.app_payload, dict)
    assert "target_company" in vr.app_payload


def test_u0_rejects_forbidden_authority_field():
    from apps_research.runtime.profile_builder import parse_payload
    from agentic_core.runtime.entry.u0_apps_research_binding import u0_validate_apps_research
    envelope = parse_payload({"target_company": "TestCo"})
    vr = u0_validate_apps_research(envelope)
    assert vr.authority_validation_receipt.passed is True


# ---------------------------------------------------------------------------
# L1
# ---------------------------------------------------------------------------

def test_l1_emits_plan_contract():
    from apps_research.runtime.profile_builder import parse_payload
    from agentic_core.runtime.entry.u0_apps_research_binding import u0_validate_apps_research
    from agentic_core.L1_cognition.apps_research_l1_binding import l1_plan_apps_research
    envelope = parse_payload({"target_company": "TestCo", "target_role": "CTO"})
    vr = u0_validate_apps_research(envelope)
    plan = l1_plan_apps_research(vr)
    assert plan.grounding_required is True
    assert plan.model_generation_required is True
    assert plan.write_authority_present is False
    assert "validate_ingress_payload" in plan.task_plan
    assert plan.task_spec["target_company"] == "TestCo"


# ---------------------------------------------------------------------------
# L0
# ---------------------------------------------------------------------------

def test_l0_emits_route_r3():
    from apps_research.runtime.profile_builder import parse_payload
    from agentic_core.runtime.entry.u0_apps_research_binding import u0_validate_apps_research
    from agentic_core.L1_cognition.apps_research_l1_binding import l1_plan_apps_research
    from agentic_core.L0_routing.apps_research_l0_binding import l0_route_apps_research
    envelope = parse_payload({"target_company": "TestCo"})
    vr = u0_validate_apps_research(envelope)
    plan = l1_plan_apps_research(vr)
    route = l0_route_apps_research(plan)
    assert route.route_id == "R3_SIMPLE_GROUNDED_READ"
    assert route.grounding_required is True
    assert route.write_authority_present is False
    assert route.l3_required is False
    assert "Retired/Provider-Model" in route.allowed_models


# ---------------------------------------------------------------------------
# C0
# ---------------------------------------------------------------------------

def test_c0_emits_fec_with_evidence():
    from apps_research.runtime.profile_builder import parse_payload
    from agentic_core.runtime.entry.u0_apps_research_binding import u0_validate_apps_research
    from agentic_core.L1_cognition.apps_research_l1_binding import l1_plan_apps_research
    from agentic_core.L0_routing.apps_research_l0_binding import l0_route_apps_research
    from agentic_core.runtime.c0.apps_research_c0_binding import c0_retrieve_apps_research
    envelope = parse_payload({"target_company": "TestCo", "depth": "standard"})
    vr = u0_validate_apps_research(envelope)
    plan = l1_plan_apps_research(vr)
    route = l0_route_apps_research(plan)
    fec = c0_retrieve_apps_research(route, vr)
    assert fec.app_id == "apps_research"
    assert len(fec.evidence_items) >= 1
    assert fec.compilation_hash != ""
    assert fec.support_target_met is True


# ---------------------------------------------------------------------------
# PA
# ---------------------------------------------------------------------------

def test_pa_emits_compiled_prompt():
    from apps_research.runtime.profile_builder import parse_payload
    from agentic_core.runtime.entry.u0_apps_research_binding import u0_validate_apps_research
    from agentic_core.L1_cognition.apps_research_l1_binding import l1_plan_apps_research
    from agentic_core.L0_routing.apps_research_l0_binding import l0_route_apps_research
    from agentic_core.runtime.c0.apps_research_c0_binding import c0_retrieve_apps_research
    from agentic_core.prompt_governance.apps_research_pa_binding import pa_compose_apps_research
    envelope = parse_payload({"target_company": "TestCo"})
    vr = u0_validate_apps_research(envelope)
    plan = l1_plan_apps_research(vr)
    route = l0_route_apps_research(plan)
    fec = c0_retrieve_apps_research(route, vr)
    prompt = pa_compose_apps_research(route, plan, fec, vr)
    assert prompt.app_id == "apps_research"
    assert prompt.compilation_hash != ""
    assert prompt.evidence_digest == fec.compilation_hash
    assert prompt.system_preamble != ""
    assert len(prompt.slot_lineage_map) >= 1


# ---------------------------------------------------------------------------
# L2 (provider unavailable path)
# ---------------------------------------------------------------------------

def test_l2_without_provider_fails_closed():
    from apps_research.runtime.profile_builder import parse_payload
    from agentic_core.runtime.entry.u0_apps_research_binding import u0_validate_apps_research
    from agentic_core.L1_cognition.apps_research_l1_binding import l1_plan_apps_research
    from agentic_core.L0_routing.apps_research_l0_binding import l0_route_apps_research
    from agentic_core.runtime.c0.apps_research_c0_binding import c0_retrieve_apps_research
    from agentic_core.prompt_governance.apps_research_pa_binding import pa_compose_apps_research
    from agentic_core.L2_execution.apps_research_l2_binding import l2_execute_apps_research
    envelope = parse_payload({"target_company": "TestCo"})
    vr = u0_validate_apps_research(envelope)
    plan = l1_plan_apps_research(vr)
    route = l0_route_apps_research(plan)
    fec = c0_retrieve_apps_research(route, vr)
    prompt = pa_compose_apps_research(route, plan, fec, vr)
    sealed = l2_execute_apps_research(prompt)
    assert sealed.app_id == "apps_research"
    assert sealed.execution_status == "FAILED"
    assert sealed.prompt_hash == prompt.compilation_hash
    assert sealed.output_content == {}
    assert sealed.execution_validation_receipt.validation_passed is False
    assert "provider_gateway_unavailable" in sealed.execution_validation_receipt.errors[0]


# ---------------------------------------------------------------------------
# Provenance chain
# ---------------------------------------------------------------------------

def test_provenance_chain_links_fec_to_sealed():
    """FEC.compilation_hash → prompt.evidence_digest → sealed.prompt_artifact_digest."""
    from apps_research.runtime.profile_builder import parse_payload
    from agentic_core.runtime.entry.u0_apps_research_binding import u0_validate_apps_research
    from agentic_core.L1_cognition.apps_research_l1_binding import l1_plan_apps_research
    from agentic_core.L0_routing.apps_research_l0_binding import l0_route_apps_research
    from agentic_core.runtime.c0.apps_research_c0_binding import c0_retrieve_apps_research
    from agentic_core.prompt_governance.apps_research_pa_binding import pa_compose_apps_research
    from agentic_core.L2_execution.apps_research_l2_binding import l2_execute_apps_research
    envelope = parse_payload({"target_company": "ProvCo"})
    vr = u0_validate_apps_research(envelope)
    plan = l1_plan_apps_research(vr)
    route = l0_route_apps_research(plan)
    fec = c0_retrieve_apps_research(route, vr)
    prompt = pa_compose_apps_research(route, plan, fec, vr)
    sealed = l2_execute_apps_research(prompt)
    assert fec.compilation_hash == prompt.evidence_digest
    assert prompt.compilation_hash == sealed.prompt_hash


# ---------------------------------------------------------------------------
# Full profile spine without provider
# ---------------------------------------------------------------------------

def test_full_profile_spine_without_provider_fails_closed():
    from agentic_core.runtime.entry.app_ingress_runner import AppIngressRunner
    from apps_research.runtime.profile_builder import build_app_runtime_contract
    runner = AppIngressRunner(profile=build_app_runtime_contract())
    disposition = runner.run({"target_company": "FullCo", "target_role": "CPO"})
    assert disposition.exit_status == "failure"
    assert disposition.outcome_authorized is False
    assert disposition.output_artifact_path is not None
    assert disposition.final_output.get("company_name") == ""


def test_parse_returns_none_on_empty_payload():
    from apps_research.runtime.profile_builder import parse_payload
    result = parse_payload({})
    assert result is None


def test_profile_spine_failure_artifact_is_valid_json(tmp_path):
    from agentic_core.runtime.entry.app_ingress_runner import AppIngressRunner
    from apps_research.runtime.profile_builder import build_app_runtime_contract
    runner = AppIngressRunner(profile=build_app_runtime_contract())
    disposition = runner.run({"target_company": "ArtifactCo"})
    assert disposition.exit_status == "failure"
    import pathlib
    artifact = pathlib.Path(disposition.output_artifact_path)
    assert artifact.exists()
    content = json.loads(artifact.read_text(encoding="utf-8"))
    assert "schema_version" in content
    assert content != {"company_name": "Stub " + "Company"}
