"""W8 ADG runtime-proxy negative-path coverage for thin C0/L3/L2 bindings."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from apps_lic.engines.governed_opportunity_ingestion import STATUS_MISSING
from apps_lic.engines.message_type_requirement_gate import MESSAGE_GENERAL_INTRO
from apps_lic.runtime.dispatch import stage_receipts as sr
from apps_lic.runtime.dispatch.canonical_dispatch import (
    build_cli_ingress_raw,
    run_canonical_apps_lic_spine,
)
from tests.apps_lic.canonical_readiness_fixtures import ready_governed_opportunity_facts


def _load_json(run_dir: Path, name: str) -> dict[str, Any]:
    path = run_dir / name
    assert path.is_file(), f"missing {name}"
    return json.loads(path.read_text(encoding="utf-8"))


def _ready_general_intro_raw() -> dict[str, Any]:
    return build_cli_ingress_raw(
        manual_brief="General intro for an AIG technical recruiter.",
        message_type_hint=MESSAGE_GENERAL_INTRO,
        message_modifiers={"uses_referral_context": False},
        campaign_objective="Draft a concise general LinkedIn introduction.",
        lead_profile={
            "verified_name": "Jane Smith",
            "title": "Senior Technical Recruiter",
            "seniority_class": "",
            "company_name": "AIG",
            "industry": "Insurance",
            "consent_attested": True,
        },
        governed_opportunity_facts=ready_governed_opportunity_facts(),
    )


def test_c0_missing_readiness_keeps_pa_l3_l2_and_exit_absent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APPS_LIC_TEST_PROVIDER_STUB", "1")
    raw = build_cli_ingress_raw(
        manual_brief="A rich inline brief must not bypass governed C0 readiness.",
    )

    result = run_canonical_apps_lic_spine(raw, artifact_root=tmp_path / "c0_missing")

    manifest = _load_json(result.artifact_dir, sr.FILENAME_SPINE_MANIFEST)
    proof = _load_json(result.artifact_dir, "runtime_proof_bundle.json")

    assert result.c0_invoked is True
    assert result.pa_invoked is False
    assert result.l3_participated is False
    assert result.l2_executed is False
    assert result.outcome_authorized is False
    assert manifest["terminal_c0_block"] is True
    assert manifest["c0_readiness_status"] == STATUS_MISSING
    assert manifest["c0_recipient_class_status"] == STATUS_MISSING
    assert proof["status"] == "PASS"
    assert proof["proof_mode"] == "c0_block"
    for forbidden in (
        sr.FILENAME_PA_RECEIPT,
        sr.FILENAME_L3_WORKFLOW,
        sr.FILENAME_L2_EXECUTION,
        sr.FILENAME_EXIT_DISPOSITION,
    ):
        assert not (result.artifact_dir / forbidden).exists()


def test_l3_and_l2_receipts_preserve_no_execute_no_write_no_send_authority(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APPS_LIC_TEST_PROVIDER_STUB", "1")

    result = run_canonical_apps_lic_spine(
        _ready_general_intro_raw(),
        artifact_root=tmp_path / "ready",
    )

    assert result.l3_participated is True
    assert result.l2_executed is True
    assert result.outcome_authorized is True

    l3 = _load_json(result.artifact_dir, sr.FILENAME_L3_WORKFLOW)
    orchestration = l3["payload"]["orchestration_receipt"]
    step_contract = l3["payload"]["step_contract"]
    assert orchestration["l3_no_execute_assertion"] is True
    assert orchestration["l3_no_retrieve_assertion"] is True
    assert orchestration["l3_no_prompt_assembly_assertion"] is True
    assert orchestration["l3_no_l4_write_assertion"] is True
    assert orchestration["posture"]["read_only"] is True
    assert orchestration["posture"]["write_intent"] is False
    assert step_contract["expected_output_contract"] == "SealedL2Artifact"
    assert step_contract["no_durable_commit_authority"] is True
    assert step_contract["fallback_permission"] == "stub_fallback_only"

    l2 = _load_json(result.artifact_dir, sr.FILENAME_L2_EXECUTION)
    payload = l2["payload"]
    assert payload["execution_status"] == "completed"
    assert payload["state_diff_authorized"] is False
    assert payload["is_uwg_write_authority"] is False
    assert payload["proposed_state_diff"] == {}
    assert payload["generated_content_origin"] == "MODEL_GENERATION"
    assert payload["posture"]["read_only"] is True
    assert payload["posture"]["write_intent"] is False
    assert "no-send" in payload["egress_policy_ref"]
    forbidden_tool_terms = ("send", "post", "publish", "connector")
    assert not any(
        term in str(tool).lower()
        for tool in payload["allowed_tools"]
        for term in forbidden_tool_terms
    )

    manifest = _load_json(result.artifact_dir, sr.FILENAME_SPINE_MANIFEST)
    assert manifest["no_send_assertion"] is True
    assert manifest["no_l4_write_assertion"] is True
    assert manifest["no_connector_post_assertion"] is True
