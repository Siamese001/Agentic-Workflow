"""W5 app-specific validation Exit wire-up in canonical apps_lic dispatch."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
from apps_lic.engines.message_type_requirement_gate import (
    MESSAGE_GENERAL_INTRO,
    MESSAGE_ROLE_SPECIFIC,
)
from apps_lic.engines.validation_exit import (
    ANTHROPIC_MESSAGES_API,
    DEFAULT_X1D_JUDGE_MODEL,
    DEFAULT_X1D_JUDGE_PROVIDER,
    JUDGE_AVAILABLE,
    LIVE_CLAUDE_API_CALL,
)
from apps_lic.engines.whole_message_generation import (
    GENERATOR_MODEL_ID,
    GENERATOR_PROVIDER_ID,
    NO_DURABLE_WRITE_RECEIPT,
    WholeMessageCandidate,
)
from apps_lic.engines.x1d_judge_feedback_regeneration import (
    STOP_REPAIR_CANDIDATE_CLEAR,
)
from apps_lic.engines.x1d_claude_judge_adapter import AnthropicClaudeX1DTransport
import apps_lic.engines.x1d_judge_feedback_regeneration as x1d_regen
from apps_lic.runtime.bindings.exit_binding import _build_exit_review_packet
from apps_lic.runtime.bindings.l2_binding import APPS_LIC_L2_CERT_REF
from apps_lic.runtime.dispatch import stage_receipts as sr
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


def test_w5_clear_path_uses_validation_exit_before_shared_exit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APPS_LIC_TEST_PROVIDER_STUB", "1")
    raw = build_cli_ingress_raw(
        manual_brief="Friendly intro for a technical recruiter.",
        message_type_hint=MESSAGE_GENERAL_INTRO,
        message_modifiers={"uses_referral_context": False},
        campaign_objective="Draft a concise general LinkedIn introduction.",
        governed_opportunity_facts=ready_governed_opportunity_facts(),
    )

    result = run_canonical_apps_lic_spine(raw, artifact_root=tmp_path / "clear")

    w5 = _load_json(result.artifact_dir, sr.FILENAME_W5_VALIDATION_EXIT)
    exit_receipt = _load_json(result.artifact_dir, sr.FILENAME_EXIT_DISPOSITION)
    manifest = _load_json(result.artifact_dir, sr.FILENAME_SPINE_MANIFEST)
    proof_bundle = _load_json(result.artifact_dir, "runtime_proof_bundle.json")

    assert result.x3_disposition == "X3D"
    assert result.exit_status == "success"
    assert w5["stage"] == "W5.VALIDATION_EXIT"
    assert w5["upstream_receipt_refs"] == [sr.FILENAME_C03_POSTGEN_VALIDATION]
    assert exit_receipt["upstream_receipt_refs"] == [sr.FILENAME_W5_VALIDATION_EXIT]
    assert w5["payload"]["x2_status"] == "X2_VALIDATION_PASS"
    assert w5["payload"]["x1d_status"] == "X1D_NOT_REQUIRED"
    assert manifest["terminal_w5_validation_exit_block"] is False
    assert manifest["w5_validation_exit_status"] == "EXIT_CLEAR_DRAFT"
    assert proof_bundle["proof_mode"] == "r4"
    assert "W5.VALIDATION_EXIT" in proof_bundle["canonical_stage_order"]
    assert exit_receipt["payload"]["final_output"]["validation_exit_proof"]["status"] == (
        "EXIT_CLEAR_DRAFT"
    )


def test_w5_role_specific_missing_x1d_becomes_review_required(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APPS_LIC_TEST_PROVIDER_STUB", "1")
    raw = build_cli_ingress_raw(
        manual_brief="Role-specific recruiter note for the AIG Agentic AI role.",
        message_type_hint=MESSAGE_ROLE_SPECIFIC,
        governed_opportunity_facts=ready_governed_opportunity_facts(),
    )

    result = run_canonical_apps_lic_spine(raw, artifact_root=tmp_path / "role")

    w5 = _load_json(result.artifact_dir, sr.FILENAME_W5_VALIDATION_EXIT)
    manifest = _load_json(result.artifact_dir, sr.FILENAME_SPINE_MANIFEST)
    proof_bundle = _load_json(result.artifact_dir, "runtime_proof_bundle.json")

    assert result.x3_disposition == "X3B"
    assert result.exit_status == "review_required"
    assert result.outcome_authorized is False
    assert w5["payload"]["x2_status"] == "X2_VALIDATION_PASS"
    assert w5["payload"]["x1d_status"] == "X1D_BLOCKED"
    assert w5["payload"]["x1d_missing_judge_ids"] == ["evidence_claim_support_x1d"]
    assert manifest["terminal_w5_validation_exit_block"] is True
    assert manifest["w5_validation_exit_disposition"] == "blocked"
    assert proof_bundle["proof_mode"] == "w5_validation_exit_block"
    assert proof_bundle["status"] == "PASS"


def test_w5_live_x1d_runner_executes_required_judge_when_enabled(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[dict[str, Any]] = []

    def _passing_live_call(self: AnthropicClaudeX1DTransport, payload: dict[str, Any]) -> dict[str, Any]:
        _ = self
        calls.append(dict(payload))
        return {
            "score": 0.99,
            "passed": True,
            "issues": [],
            "required_repairs": [],
            "model": DEFAULT_X1D_JUDGE_MODEL,
            "provider": DEFAULT_X1D_JUDGE_PROVIDER,
            "availability_status": JUDGE_AVAILABLE,
            "transport_provenance": LIVE_CLAUDE_API_CALL,
            "transport_provider": ANTHROPIC_MESSAGES_API,
            "transport_call_id": "test-live-claude-x1d-call",
        }

    monkeypatch.setenv("APPS_LIC_TEST_PROVIDER_STUB", "1")
    monkeypatch.setenv("APPS_LIC_RUN_LIVE_CLAUDE_X1D", "1")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-live-x1d")
    monkeypatch.setattr(AnthropicClaudeX1DTransport, "__call__", _passing_live_call)

    raw = build_cli_ingress_raw(
        manual_brief="Role-specific recruiter note for the AIG Agentic AI role.",
        message_type_hint=MESSAGE_ROLE_SPECIFIC,
        governed_opportunity_facts=ready_governed_opportunity_facts(),
    )

    result = run_canonical_apps_lic_spine(raw, artifact_root=tmp_path / "live-x1d")

    w5 = _load_json(result.artifact_dir, sr.FILENAME_W5_VALIDATION_EXIT)
    manifest = _load_json(result.artifact_dir, sr.FILENAME_SPINE_MANIFEST)

    assert calls
    assert result.x3_disposition == "X3D"
    assert result.exit_status == "success"
    assert w5["payload"]["x1d_status"] == "X1D_VALIDATION_PASS"
    assert w5["payload"]["x1d_missing_judge_ids"] == []
    assert w5["payload"]["x1d_judge_result_count"] == 1
    assert manifest["w5_x1d_status"] == "X1D_VALIDATION_PASS"


def test_w5_live_x1d_review_failure_runs_bounded_qwen_feedback_repair(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    judge_calls: list[dict[str, Any]] = []
    repair_calls: list[dict[str, Any]] = []

    def _fail_then_pass_live_call(
        self: AnthropicClaudeX1DTransport,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        _ = self
        judge_calls.append(dict(payload))
        if len(judge_calls) == 1:
            return {
                "score": 0.40,
                "passed": False,
                "issues": ["generic_role_fit"],
                "required_repairs": ["anchor_to_aig_agentic_ai_role"],
                "model": DEFAULT_X1D_JUDGE_MODEL,
                "provider": DEFAULT_X1D_JUDGE_PROVIDER,
                "availability_status": JUDGE_AVAILABLE,
                "transport_provenance": LIVE_CLAUDE_API_CALL,
                "transport_provider": ANTHROPIC_MESSAGES_API,
                "transport_call_id": "test-live-claude-x1d-fail",
            }
        return {
            "score": 0.96,
            "passed": True,
            "issues": [],
            "required_repairs": [],
            "model": DEFAULT_X1D_JUDGE_MODEL,
            "provider": DEFAULT_X1D_JUDGE_PROVIDER,
            "availability_status": JUDGE_AVAILABLE,
            "transport_provenance": LIVE_CLAUDE_API_CALL,
            "transport_provider": ANTHROPIC_MESSAGES_API,
            "transport_call_id": "test-live-claude-x1d-pass",
        }

    def _repair_candidate(request, parent, failed, iteration):
        repair_calls.append(
            {
                "parent_candidate_id": parent.candidate_id,
                "failed_judge_ids": [result.judge_id for result in failed],
                "iteration": iteration,
            }
        )
        text = (
            "Hi Jane, AIG's VP, Global Head of Agentic AI Solutions role needs "
            "regulated agentic AI delivery across governance and platform execution. "
            "I designed and operationalized a governed agentic AI platform for "
            "regulated enterprise workflows. Would a quick resume review for "
            "JR2601998 be useful?\n\nAmit"
        )
        return WholeMessageCandidate(
            candidate_id="repair_candidate_1",
            subject_line="AIG Agentic AI fit",
            draft_text=text,
            attempt_seed="sha256:" + "c" * 64,
            model_id=GENERATOR_MODEL_ID,
            provider_id=GENERATOR_PROVIDER_ID,
            temperature=request.reasoning_policy.repair_temperature,
            top_p=request.reasoning_policy.top_p,
            word_count=len(text.split()),
            sentence_count=3,
            char_count=len(text),
            claims_used=parent.claims_used,
            is_whole_message=True,
            no_durable_write_receipt=NO_DURABLE_WRITE_RECEIPT,
            generation_receipt="x1d_feedback_repair:prov:test:mref:test",
        )

    monkeypatch.setenv("APPS_LIC_TEST_PROVIDER_STUB", "1")
    monkeypatch.setenv("APPS_LIC_RUN_LIVE_CLAUDE_X1D", "1")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-live-x1d")
    monkeypatch.setattr(AnthropicClaudeX1DTransport, "__call__", _fail_then_pass_live_call)
    monkeypatch.setattr(x1d_regen, "qwen_judge_feedback_repair_candidate", _repair_candidate)

    raw = build_cli_ingress_raw(
        manual_brief="Role-specific recruiter note for the AIG Agentic AI role.",
        message_type_hint=MESSAGE_ROLE_SPECIFIC,
        governed_opportunity_facts=ready_governed_opportunity_facts(),
    )

    result = run_canonical_apps_lic_spine(raw, artifact_root=tmp_path / "live-x1d-repair")

    w5 = _load_json(result.artifact_dir, sr.FILENAME_W5_VALIDATION_EXIT)
    manifest = _load_json(result.artifact_dir, sr.FILENAME_SPINE_MANIFEST)

    assert len(judge_calls) == 2
    assert len(repair_calls) == 1
    assert result.x3_disposition == "X3D"
    assert result.exit_status == "success"
    assert w5["payload"]["selected_candidate_id"] == "repair_candidate_1"
    assert w5["payload"]["x1d_regeneration_attempted"] is True
    assert w5["payload"]["x1d_regeneration_iteration_count"] == 1
    assert w5["payload"]["x1d_regeneration_stop_reason"] == STOP_REPAIR_CANDIDATE_CLEAR
    assert w5["payload"]["x1d_regeneration"]["attempts"][0]["failed_judge_ids"] == [
        "evidence_claim_support_x1d"
    ]
    assert manifest["w5_x1d_regeneration_attempted"] is True
    assert manifest["w5_x1d_regeneration_stop_reason"] == STOP_REPAIR_CANDIDATE_CLEAR
    assert manifest["w5_x1d_status"] == "X1D_VALIDATION_PASS"


def test_w5_ceo_missing_x1d_becomes_review_required(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APPS_LIC_TEST_PROVIDER_STUB", "1")
    raw = build_cli_ingress_raw(
        manual_brief="CEO-level AIG AI transformation outreach note.",
        lead_profile={
            "verified_name": "Pat Riley",
            "title": "Chief Executive Officer",
            "seniority_class": "",
            "company_name": "AIG",
            "industry": "Insurance",
            "consent_attested": True,
        },
        governed_opportunity_facts=ready_governed_opportunity_facts(
            contact_text="Pat Riley | Chief Executive Officer | AIG",
            role_ownership_text="Chief executive sponsor for enterprise AI transformation.",
        ),
    )

    result = run_canonical_apps_lic_spine(raw, artifact_root=tmp_path / "ceo")

    manifest = _load_json(result.artifact_dir, sr.FILENAME_SPINE_MANIFEST)

    assert manifest["derived_recipient_class"] == "CEO"
    assert result.x3_disposition == "X3B"
    assert result.exit_status == "review_required"
    assert manifest["w5_x2_status"] == "X2_VALIDATION_PASS"
    assert manifest["w5_x1d_status"] == "X1D_BLOCKED"
    assert manifest["w5_x1d_missing_judge_ids"] == [
        "ceo_attention_originality_x1d",
        "ceo_evidence_overclaim_risk_x1d",
    ]


def test_generic_exit_packet_no_longer_fabricates_perfect_grounding_or_c0_pass() -> None:
    packet = _build_exit_review_packet(
        SealedL2Artifact(
            request_id="req_exit_generic",
            run_id="run_exit_generic",
            app_id="apps_lic",
            trace_id="trace_exit_generic",
            execution_status="completed",
            generated_content="Draft text.",
            prompt_artifact_digest="sha256:" + "a" * 64,
            compilation_hash="sha256:" + "b" * 64,
            l5_certification_ref=APPS_LIC_L2_CERT_REF,
        )
    )

    assert packet.output["groundedness"] == 0.0
    assert packet.output["faithfulness"] == 0.0
    assert packet.output["citation_precision"] == 0.0
    assert packet.final_evidence_contract["c0_status"] == "UNKNOWN"
