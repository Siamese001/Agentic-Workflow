"""W3A canonical C0.3 sender proof packet wire-up for apps_lic."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_lic.engines.governed_opportunity_ingestion import (
    NAMESPACE_COMPANY,
    NAMESPACE_CONTACT,
    NAMESPACE_ROLE_OWNERSHIP,
)
from apps_lic.engines.message_type_requirement_gate import (
    MESSAGE_FOLLOW_UP,
    MESSAGE_REFERRAL_ASK,
    MESSAGE_ROLE_SPECIFIC,
    MISSING_JD_FACTS,
    MISSING_PRIOR_THREAD,
    MISSING_REFERRER_CONTEXT,
    MISSING_REQUISITION_NUMBER,
    STATUS_REQUIREMENTS_BLOCKED,
    STATUS_REQUIREMENTS_PASS,
)
from apps_lic.engines.sender_proof_graph import (
    PA_INSTRUCTION_DATA_BOUNDARY_RECEIPT,
    STATUS_PROOF_GRAPH_READY,
)
from apps_lic.runtime.dispatch.canonical_dispatch import (
    build_cli_ingress_raw,
    run_canonical_apps_lic_spine,
)
from tests.apps_lic.canonical_readiness_fixtures import (
    fact_packet,
    ready_governed_opportunity_facts,
)


def _load_json(run_dir: Path, name: str) -> dict:
    path = run_dir / name
    assert path.is_file(), f"missing {name}"
    return json.loads(path.read_text(encoding="utf-8"))


def _facts_without_jd() -> list[dict]:
    return [
        fact_packet(
            namespace=NAMESPACE_CONTACT,
            document_id="contact-recruiter",
            fact_text="Jane Smith | Senior Technical Recruiter | AIG",
            metadata={
                "title": "Senior Technical Recruiter",
                "company": "AIG",
                "conflict_key": "contact_identity",
                "canonical_value": "Jane Smith|Senior Technical Recruiter|AIG",
            },
        ),
        fact_packet(
            namespace=NAMESPACE_COMPANY,
            document_id="company-aig",
            fact_text="AIG enterprise AI operating context.",
            metadata={"company": "AIG"},
        ),
        fact_packet(
            namespace=NAMESPACE_ROLE_OWNERSHIP,
            document_id="role-owner-jane",
            fact_text="Owns recruiting for AI platform leadership roles.",
            metadata={
                "ownership_signal": "Owns recruiting for AI platform leadership roles.",
                "conflict_key": "role_ownership",
                "canonical_value": "Jane owns AI platform recruiting.",
            },
        ),
    ]


def _facts_with_jd_missing_requisition() -> list[dict]:
    facts = ready_governed_opportunity_facts()
    for fact in facts:
        if fact["namespace"] == "apps_lic_jd_facts":
            fact["metadata"] = {
                key: value
                for key, value in dict(fact["metadata"]).items()
                if key != "requisition_number"
            }
    return facts


def test_w3a_ready_role_specific_builds_c03_packet_and_pa_envelope(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APPS_LIC_TEST_PROVIDER_STUB", "1")
    raw = build_cli_ingress_raw(
        manual_brief="Role-specific recruiter note for the AIG Agentic AI role.",
        message_type_hint=MESSAGE_ROLE_SPECIFIC,
        governed_opportunity_facts=ready_governed_opportunity_facts(),
    )

    result = run_canonical_apps_lic_spine(raw, artifact_root=tmp_path / "ready")

    assert result.pa_invoked is True
    assert result.l2_executed is True
    manifest = _load_json(result.artifact_dir, "spine_run_manifest.json")
    c03 = _load_json(result.artifact_dir, "c03_sender_proof_packet.json")
    pa = _load_json(result.artifact_dir, "pa_receipt.json")
    proof_bundle = _load_json(result.artifact_dir, "runtime_proof_bundle.json")

    packet = c03["payload"]["sender_proof_packet"]
    envelope = c03["payload"]["pa_sender_proof_envelope"]
    allowed_claim_ids = packet["proof_ids"]

    assert manifest["c03_invoked"] is True
    assert manifest["c03_status"] == "C03_READY"
    assert manifest["c03_message_type"] == MESSAGE_ROLE_SPECIFIC
    assert manifest["c03_message_requirements_status"] == STATUS_REQUIREMENTS_PASS
    assert manifest["c03_sender_proof_status"] == STATUS_PROOF_GRAPH_READY
    assert manifest["c03_proof_packet_id"] == packet["proof_packet_id"]
    assert manifest["c03_allowed_claim_ids"] == allowed_claim_ids
    assert proof_bundle["canonical_stage_order"] == [
        "INGRESS",
        "U0",
        "L1",
        "L0",
        "C0",
        "C0.3",
        "PA",
        "L3",
        "L2",
        "W4.CANDIDATES",
        "C0.3.POSTGEN",
        "W5.VALIDATION_EXIT",
        "EXIT",
    ]

    assert 1 <= len(allowed_claim_ids) <= 3
    assert envelope["proof_packet_id"] == packet["proof_packet_id"]
    assert envelope["allowed_claim_ids"] == allowed_claim_ids
    assert (
        envelope["instruction_data_boundary_receipt"]
        == PA_INSTRUCTION_DATA_BOUNDARY_RECEIPT
    )
    assert "c03_sender_proof_envelope" in pa["payload"]["component_hash_map"]
    assert "C0_3_PROOF_GRAPH" in pa["payload"]["slot_lineage_map"]["C03"]
    assert any(
        ref == f"c03_sender_proof_packet:{packet['proof_packet_id']}"
        for ref in pa["payload"]["audit_refs"]
    )

    prompt_text = "\n".join(
        str(block.get("content") or "")
        for block in pa["payload"]["prompt_blocks"]
    )
    assert "C0.3 SENDER PROOF ENVELOPE" in prompt_text
    assert packet["proof_packet_id"] in prompt_text
    for proof_id in allowed_claim_ids:
        assert proof_id in prompt_text


@pytest.mark.parametrize(
    ("facts", "expected_missing"),
    [
        (_facts_without_jd(), MISSING_JD_FACTS),
        (_facts_with_jd_missing_requisition(), MISSING_REQUISITION_NUMBER),
    ],
)
def test_w3a_role_specific_recruiter_missing_jd_or_requisition_blocks_before_pa(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    facts: list[dict],
    expected_missing: str,
) -> None:
    monkeypatch.setenv("APPS_LIC_TEST_PROVIDER_STUB", "1")
    raw = build_cli_ingress_raw(
        manual_brief="Role-specific recruiter note must have role evidence.",
        message_type_hint=MESSAGE_ROLE_SPECIFIC,
        governed_opportunity_facts=facts,
        c0_required_namespaces=(
            NAMESPACE_CONTACT,
            NAMESPACE_COMPANY,
            NAMESPACE_ROLE_OWNERSHIP,
        )
        if expected_missing == MISSING_JD_FACTS
        else None,
    )

    result = run_canonical_apps_lic_spine(
        raw,
        artifact_root=tmp_path / expected_missing,
    )

    assert result.pa_invoked is False
    assert result.l2_executed is False
    manifest = _load_json(result.artifact_dir, "spine_run_manifest.json")
    c03 = _load_json(result.artifact_dir, "c03_sender_proof_packet.json")
    proof_bundle = _load_json(result.artifact_dir, "runtime_proof_bundle.json")

    assert manifest["terminal_c03_block"] is True
    assert manifest["c03_message_requirements_status"] == STATUS_REQUIREMENTS_BLOCKED
    assert expected_missing in manifest["c03_missing_fields"]
    assert manifest["pa_invoked"] is False
    assert proof_bundle["proof_mode"] == "c03_block"
    assert not (result.artifact_dir / "pa_receipt.json").exists()
    assert not (result.artifact_dir / "l2_execution_receipt.json").exists()
    assert expected_missing in c03["payload"]["message_requirement_gate"]["missing_fields"]


@pytest.mark.parametrize(
    ("message_type", "expected_missing"),
    [
        (MESSAGE_REFERRAL_ASK, MISSING_REFERRER_CONTEXT),
        (MESSAGE_FOLLOW_UP, MISSING_PRIOR_THREAD),
    ],
)
def test_w3a_referral_and_follow_up_without_required_context_block_before_pa(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    message_type: str,
    expected_missing: str,
) -> None:
    monkeypatch.setenv("APPS_LIC_TEST_PROVIDER_STUB", "1")
    raw = build_cli_ingress_raw(
        manual_brief="Context-specific message should require its source facts.",
        message_type_hint=message_type,
        governed_opportunity_facts=ready_governed_opportunity_facts(),
    )

    result = run_canonical_apps_lic_spine(
        raw,
        artifact_root=tmp_path / message_type,
    )

    manifest = _load_json(result.artifact_dir, "spine_run_manifest.json")

    assert result.pa_invoked is False
    assert result.l2_executed is False
    assert manifest["terminal_c03_block"] is True
    assert manifest["c03_message_type"] == message_type
    assert manifest["c03_message_requirements_status"] == STATUS_REQUIREMENTS_BLOCKED
    assert expected_missing in manifest["c03_missing_fields"]
