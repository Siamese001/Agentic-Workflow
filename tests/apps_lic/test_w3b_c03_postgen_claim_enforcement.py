"""W3B post-generation C0.3 sender-claim enforcement."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from apps_lic.engines.generation_engine import GenerationEngine
from apps_lic.engines.message_type_requirement_gate import MESSAGE_ROLE_SPECIFIC
from apps_lic.engines.sender_proof_graph import REASON_CLAIM_NOT_IN_PACKET
from apps_lic.runtime.bindings.c03_postgen_binding import (
    C03_POSTGEN_STATUS_BLOCKED,
    C03_POSTGEN_STATUS_PASS,
    REASON_PROOF_LIKE_TEXT_WITHOUT_CLAIM_ID,
)
from apps_lic.runtime.dispatch.canonical_dispatch import (
    build_cli_ingress_raw,
    run_canonical_apps_lic_spine,
)
from tests.apps_lic.canonical_readiness_fixtures import (
    ready_governed_opportunity_facts,
)


def _load_json(run_dir: Path, name: str) -> dict[str, Any]:
    path = run_dir / name
    assert path.is_file(), f"missing {name}"
    return json.loads(path.read_text(encoding="utf-8"))


def _ready_raw() -> dict[str, Any]:
    return build_cli_ingress_raw(
        manual_brief="Role-specific recruiter note for the AIG Agentic AI role.",
        message_type_hint=MESSAGE_ROLE_SPECIFIC,
        governed_opportunity_facts=ready_governed_opportunity_facts(),
    )


def _passing_draft(**overrides: Any) -> dict[str, Any]:
    candidate_id = str(overrides.pop("selected_candidate_id", "draft_candidate_1"))
    claims_used = list(overrides.get("claims_used", []))
    message_text = (
        "Hi Jane, AIG's Agentic AI role spans claims, underwriting, GenAI "
        "standards, and governance. I have built governed agent workflows "
        "with evals and telemetry. Worth a brief call on where that proof "
        "fits the rollout?"
    )
    candidate_two_text = (
        "Hi Jane, the AIG Agentic AI role looks like governed delivery across "
        "claims, underwriting, GenAI standards, and change adoption. I have built "
        "agent workflows with evals and telemetry. Open to a quick fit discussion?"
    )
    candidate_three_text = (
        "Hi Jane, AIG's Agentic AI brief looks centered on governed execution "
        "across claims, underwriting, GenAI standards, and adoption. I have built "
        "agent workflows with evals and telemetry. Worth a short screen?"
    )
    draft = {
        "message_text": message_text,
        "body": "",
        "channel": "linkedin",
        "recipient_class": "recruiter",
        "target_contact_name": "Jane Smith",
        "target_contact_title": "Senior Technical Recruiter",
        "target_contact_company": "AIG",
        "intended_next_step": "brief call",
        "claims_used": claims_used,
        "unsupported_claims": [],
        "omitted_claims": [],
        "qa_notes": [],
        "selected_candidate_id": candidate_id,
        "candidate_count": 3,
        "candidates": [
            {
                "candidate_id": candidate_id,
                "draft_text": message_text,
                "claims_used": claims_used,
                "model_call_ref": "mref:w3b:test_candidate_1",
                "provider_receipt": "prov:w3b:test_candidate_1",
            },
            {
                "candidate_id": "draft_candidate_2",
                "draft_text": candidate_two_text,
                "claims_used": claims_used,
                "model_call_ref": "mref:w3b:test_candidate_2",
                "provider_receipt": "prov:w3b:test_candidate_2",
            },
            {
                "candidate_id": "draft_candidate_3",
                "draft_text": candidate_three_text,
                "claims_used": claims_used,
                "model_call_ref": "mref:w3b:test_candidate_3",
                "provider_receipt": "prov:w3b:test_candidate_3",
            },
        ],
    }
    draft.update(overrides)
    if "claims_used" in overrides:
        for candidate in draft["candidates"]:
            candidate["claims_used"] = list(overrides["claims_used"])
    if "message_text" in overrides:
        draft["candidates"][0]["draft_text"] = str(overrides["message_text"])
    return draft


def test_w3b_postgen_pass_receipt_links_claims_to_c03_packet(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APPS_LIC_TEST_PROVIDER_STUB", "1")

    result = run_canonical_apps_lic_spine(_ready_raw(), artifact_root=tmp_path / "pass")

    c03 = _load_json(result.artifact_dir, "c03_sender_proof_packet.json")
    postgen = _load_json(result.artifact_dir, "c03_postgen_claim_validation.json")
    manifest = _load_json(result.artifact_dir, "spine_run_manifest.json")
    proof_bundle = _load_json(result.artifact_dir, "runtime_proof_bundle.json")

    allowed_claim_ids = c03["payload"]["sender_proof_packet"]["proof_ids"]
    payload = postgen["payload"]

    assert result.exit_status == "review_required"
    assert result.outcome_authorized is False
    assert payload["status"] == C03_POSTGEN_STATUS_PASS
    assert payload["proof_packet_id"] == c03["payload"]["proof_packet_id"]
    assert payload["claims_used"]
    assert set(payload["claims_used"]) <= set(allowed_claim_ids)
    assert payload["selected_candidate_id"].startswith("draft_candidate_")
    assert payload["blocked_claims"] == []
    assert payload["x2_report"]["proof_packet_id"] == payload["proof_packet_id"]
    assert payload["x2_report"]["selected_candidate_id"] == payload["selected_candidate_id"]
    assert payload["x2_report"]["source_snapshot_lineage"]
    assert manifest["c03_postgen_status"] == C03_POSTGEN_STATUS_PASS
    assert manifest["c03_postgen_blocked_claims"] == []
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
    assert proof_bundle["proof_mode"] == "w5_validation_exit_block"


def test_w3b_unknown_claim_id_blocks_before_exit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _execute(self: GenerationEngine, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        return {
            "draft_message": _passing_draft(
                claims_used=["sender_claim_not_in_packet"],
            )
        }

    monkeypatch.setattr(GenerationEngine, "execute", _execute)

    result = run_canonical_apps_lic_spine(
        _ready_raw(),
        artifact_root=tmp_path / "unknown_claim",
    )

    postgen = _load_json(result.artifact_dir, "c03_postgen_claim_validation.json")
    manifest = _load_json(result.artifact_dir, "spine_run_manifest.json")
    proof_bundle = _load_json(result.artifact_dir, "runtime_proof_bundle.json")

    assert result.exit_status == "blocked"
    assert result.outcome_authorized is False
    assert postgen["payload"]["status"] == C03_POSTGEN_STATUS_BLOCKED
    assert postgen["payload"]["selected_candidate_id"] == "draft_candidate_1"
    assert REASON_CLAIM_NOT_IN_PACKET in postgen["payload"]["blocking_reasons"]
    assert manifest["terminal_c03_postgen_block"] is True
    assert manifest["c03_postgen_proof_packet_id"] == postgen["payload"]["proof_packet_id"]
    assert proof_bundle["proof_mode"] == "c03_postgen_block"
    assert not (result.artifact_dir / "exit_disposition_receipt.json").exists()


def test_w3b_empty_claims_used_with_proof_like_text_blocks_even_if_unsupported_empty(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _execute(self: GenerationEngine, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        return {"draft_message": _passing_draft(claims_used=[], unsupported_claims=[])}

    monkeypatch.setattr(GenerationEngine, "execute", _execute)

    result = run_canonical_apps_lic_spine(
        _ready_raw(),
        artifact_root=tmp_path / "empty_claims",
    )

    postgen = _load_json(result.artifact_dir, "c03_postgen_claim_validation.json")
    manifest = _load_json(result.artifact_dir, "spine_run_manifest.json")
    proof_bundle = _load_json(result.artifact_dir, "runtime_proof_bundle.json")

    assert result.exit_status == "blocked"
    assert postgen["payload"]["claims_used"] == []
    assert postgen["payload"]["status"] == C03_POSTGEN_STATUS_BLOCKED
    assert REASON_PROOF_LIKE_TEXT_WITHOUT_CLAIM_ID in postgen["payload"]["blocking_reasons"]
    assert postgen["payload"]["proof_like_claims_detected"]
    assert manifest["c03_postgen_selected_candidate_id"] == "draft_candidate_1"
    assert manifest["c03_postgen_blocked_claims"]
    assert proof_bundle["proof_mode"] == "c03_postgen_block"
    assert not (result.artifact_dir / "exit_disposition_receipt.json").exists()
