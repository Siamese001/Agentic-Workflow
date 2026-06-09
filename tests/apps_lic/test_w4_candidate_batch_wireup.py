"""W4 candidate-batch materialization in canonical apps_lic dispatch."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from apps_lic.engines.generation_engine import GenerationEngine
from apps_lic.engines.governed_opportunity_ingestion import NAMESPACE_CONTACT
from apps_lic.engines.message_type_requirement_gate import MESSAGE_ROLE_SPECIFIC
from apps_lic.engines.validation_exit import _length_gate_passes
from apps_lic.engines.whole_message_generation import (
    LengthBudget,
    NO_DURABLE_WRITE_RECEIPT,
    WholeMessageCandidate,
)
from apps_lic.runtime.bindings.w4_candidate_batch_binding import (
    REASON_CANDIDATE_COUNT_MISMATCH,
    SELECTION_STRATEGY_LENGTH_POLICY_OVERRIDE,
    W4_STATUS_BLOCKED,
    W4_STATUS_READY,
    _within_c03_length_budget,
)
from apps_lic.runtime.dispatch import stage_receipts as sr
from apps_lic.runtime.dispatch.canonical_dispatch import (
    build_cli_ingress_raw,
    run_canonical_apps_lic_spine,
)
from tests.apps_lic.canonical_readiness_fixtures import (
    minimal_recruiter_readiness_facts,
    ready_governed_opportunity_facts,
)


def _load_json(run_dir: Path, name: str) -> dict[str, Any]:
    path = run_dir / name
    assert path.is_file(), f"missing {name}"
    return json.loads(path.read_text(encoding="utf-8"))


def _ready_sc2_recruiter_raw(**route_kwargs: Any) -> dict[str, Any]:
    return build_cli_ingress_raw(
        manual_brief="Recruiting context for an AI engineering search.",
        campaign_objective="Draft a concise note about AI engineering hiring.",
        lead_profile={
            "verified_name": "Nina K.",
            "title": "Strategic technical recruiter and Sourcer",
            "seniority_class": "",
            "company_name": "AIG",
            "industry": "Insurance",
            "consent_attested": True,
        },
        governed_opportunity_facts=minimal_recruiter_readiness_facts(),
        c0_required_namespaces=(NAMESPACE_CONTACT,),
        **route_kwargs,
    )


def _ready_role_specific_raw() -> dict[str, Any]:
    return build_cli_ingress_raw(
        manual_brief="Role-specific recruiter note for the AIG Agentic AI role.",
        message_type_hint=MESSAGE_ROLE_SPECIFIC,
        governed_opportunity_facts=ready_governed_opportunity_facts(),
    )


def _ready_executive_raw() -> dict[str, Any]:
    return build_cli_ingress_raw(
        manual_brief="AIG VP Global Head of Agentic AI Solutions briefing.",
        campaign_objective=(
            "Draft a concise LinkedIn message about AIG's VP Global Head of "
            "Agentic AI Solutions opportunity."
        ),
        lead_profile={
            "verified_name": "Scott Hallworth",
            "title": "Executive Vice President and Chief Digital Officer",
            "seniority_class": "",
            "company_name": "AIG",
            "industry": "Insurance",
            "consent_attested": True,
        },
        governed_opportunity_facts=ready_governed_opportunity_facts(
            contact_text=(
                "Scott Hallworth | Executive Vice President and Chief Digital "
                "Officer | AIG"
            ),
            role_ownership_text="Executive sponsor for digital and AI transformation.",
        ),
    )


def _assert_candidate_receipts(payload: dict[str, Any]) -> None:
    candidates = payload["whole_message_candidate_batch"]["candidates"]
    selected_id = payload["selected_candidate_id"]
    candidate_ids = {candidate["candidate_id"] for candidate in candidates}

    assert selected_id in candidate_ids
    assert set(payload["rejected_candidate_ids"]) == candidate_ids - {selected_id}
    for candidate in candidates:
        receipt = str(candidate["generation_receipt"])
        assert receipt.startswith(("model_call_ref:", "provider_receipt:"))


def test_word_band_is_advisory_for_w4_and_validation_exit_length_gates() -> None:
    budget = LengthBudget(
        budget_key="unit_advisory_word_band",
        min_words=5,
        max_words=10,
        min_sentences=1,
        max_sentences=3,
        hard_cap_chars=250,
    )
    candidate = WholeMessageCandidate(
        candidate_id="wordy_but_hard_bounds_clean",
        draft_text="Hi Jane, this is deliberately compact but counted as many words.",
        attempt_seed="seed",
        model_id="model",
        provider_id="provider",
        temperature=0.9,
        top_p=0.95,
        word_count=25,
        sentence_count=2,
        char_count=120,
        claims_used=(),
        is_whole_message=True,
        no_durable_write_receipt=NO_DURABLE_WRITE_RECEIPT,
        generation_receipt="test",
    )

    assert _within_c03_length_budget(
        candidate,
        SimpleNamespace(length_budget=budget),
    )
    length_ok, reason = _length_gate_passes(
        candidate,
        SimpleNamespace(length_budget=budget),
    )
    assert length_ok is True
    assert reason == "candidate_above_recommended_word_band_but_within_hard_bounds"


def test_w4_materializes_exact_two_candidates_for_sc2_role_specific(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APPS_LIC_TEST_PROVIDER_STUB", "1")

    result = run_canonical_apps_lic_spine(
        _ready_sc2_recruiter_raw(),
        artifact_root=tmp_path / "sc2",
    )

    w4 = _load_json(result.artifact_dir, sr.FILENAME_W4_CANDIDATE_BATCH)
    manifest = _load_json(result.artifact_dir, sr.FILENAME_SPINE_MANIFEST)
    proof_bundle = _load_json(result.artifact_dir, "runtime_proof_bundle.json")

    payload = w4["payload"]
    assert result.exit_status == "success"
    assert manifest["sc_level"] == "SC-2"
    assert payload["status"] == W4_STATUS_READY
    assert payload["expected_candidate_count"] == 2
    assert payload["candidate_count_materialized"] == 2
    assert len(payload["whole_message_candidate_batch"]["candidates"]) == 2
    assert len(payload["rejected_candidate_ids"]) == 1
    assert manifest["w4_candidate_status"] == W4_STATUS_READY
    assert manifest["w4_candidate_count_materialized"] == 2
    assert payload["selected_candidate"]["subject_line"]
    assert "W4.CANDIDATES" in proof_bundle["canonical_stage_order"]
    _assert_candidate_receipts(payload)


def test_w4_materializes_exact_three_candidates_for_sc3_executive(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APPS_LIC_TEST_PROVIDER_STUB", "1")

    result = run_canonical_apps_lic_spine(
        _ready_executive_raw(),
        artifact_root=tmp_path / "sc3",
    )

    w4 = _load_json(result.artifact_dir, sr.FILENAME_W4_CANDIDATE_BATCH)
    manifest = _load_json(result.artifact_dir, sr.FILENAME_SPINE_MANIFEST)

    payload = w4["payload"]
    assert result.exit_status == "review_required"
    assert result.outcome_authorized is False
    assert manifest["sc_level"] == "SC-3"
    assert manifest["w5_x2_status"] == "X2_VALIDATION_PASS"
    assert manifest["w5_x1d_missing_judge_ids"]
    assert payload["status"] == W4_STATUS_READY
    assert payload["expected_candidate_count"] == 3
    assert payload["candidate_count_materialized"] == 3
    assert len(payload["whole_message_candidate_batch"]["candidates"]) == 3
    assert len(payload["rejected_candidate_ids"]) == 2
    _assert_candidate_receipts(payload)


def test_w4_blocks_short_candidate_batch_before_c03_postgen_and_exit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _execute(
        self: GenerationEngine,
        context: dict[str, Any],
        **kwargs: Any,
    ) -> dict[str, Any]:
        _ = (self, context, kwargs)
        message_text = (
            "Hi Jane, AIG's Agentic AI role spans claims, underwriting, GenAI "
            "standards, and governance. I have built governed agent workflows "
            "with evals and telemetry. Worth a brief call on where that proof fits?"
        )
        return {
            "draft_message": {
                "message_text": message_text,
                "body": message_text,
                "channel": "linkedin",
                "recipient_class": "recruiter",
                "claims_used": [],
                "unsupported_claims": [],
                "selected_candidate_id": "short_candidate_1",
                "candidate_count": 2,
                "candidates": [
                    {
                        "candidate_id": "short_candidate_1",
                        "draft_text": message_text,
                        "claims_used": [],
                        "model_call_ref": "mref:w4_shortfall:candidate1",
                    }
                ],
            }
        }

    monkeypatch.setattr(GenerationEngine, "execute", _execute)

    result = run_canonical_apps_lic_spine(
        _ready_sc2_recruiter_raw(),
        artifact_root=tmp_path / "shortfall",
    )

    w4 = _load_json(result.artifact_dir, sr.FILENAME_W4_CANDIDATE_BATCH)
    manifest = _load_json(result.artifact_dir, sr.FILENAME_SPINE_MANIFEST)
    proof_bundle = _load_json(result.artifact_dir, "runtime_proof_bundle.json")

    assert result.exit_status == "blocked"
    assert result.outcome_authorized is False
    assert w4["payload"]["status"] == W4_STATUS_BLOCKED
    assert REASON_CANDIDATE_COUNT_MISMATCH in w4["payload"]["blocking_reasons"]
    assert manifest["terminal_w4_candidate_block"] is True
    assert manifest["c03_postgen_invoked"] is False
    assert proof_bundle["proof_mode"] == "w4_candidate_block"
    assert not (result.artifact_dir / sr.FILENAME_C03_POSTGEN_VALIDATION).exists()
    assert not (result.artifact_dir / sr.FILENAME_EXIT_DISPOSITION).exists()


def test_w4_selects_length_compliant_candidate_when_model_pick_exceeds_budget(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _execute(
        self: GenerationEngine,
        context: dict[str, Any],
        **kwargs: Any,
    ) -> dict[str, Any]:
        _ = (self, context, kwargs)
        long_text = (
            "Hi Jane, I am Amit. I build governed agent workflows. "
            "Your AIG search spans claims and underwriting. "
            "I can help with GenAI governance, validation design, telemetry, "
            "policy controls, replayable traces, cross-functional delivery, "
            "platform rollout, operating-model adoption, and production AI "
            "systems across regulated insurance workflows. Best, Amit."
        )
        short_text = (
            "Hi Jane, AIG's search spans claims, underwriting, and GenAI governance. "
            "I build governed agent workflows with evals and telemetry; open to a quick resume review?"
        )
        return {
            "draft_message": {
                "message_text": long_text,
                "body": long_text,
                "channel": "linkedin",
                "recipient_class": "recruiter",
                "claims_used": ["sp_agentic_platform"],
                "selected_candidate_id": "too_long",
                "candidate_count": 2,
                "candidates": [
                    {
                        "candidate_id": "too_long",
                        "draft_text": long_text,
                        "claims_used": ["sp_agentic_platform"],
                        "model_call_ref": "mref:length:candidate1",
                    },
                    {
                        "candidate_id": "fits_budget",
                        "draft_text": short_text,
                        "claims_used": ["sp_agentic_platform"],
                        "model_call_ref": "mref:length:candidate2",
                    },
                ],
            }
        }

    monkeypatch.setattr(GenerationEngine, "execute", _execute)

    result = run_canonical_apps_lic_spine(
        _ready_sc2_recruiter_raw(
            premium_available=False,
            route_override="CONNECTION_REQ",
        ),
        artifact_root=tmp_path / "length-policy",
    )

    w4 = _load_json(result.artifact_dir, sr.FILENAME_W4_CANDIDATE_BATCH)

    assert w4["payload"]["status"] == W4_STATUS_READY
    assert w4["payload"]["selected_candidate_id"] == "fits_budget"
    assert w4["payload"]["selection_strategy"] == SELECTION_STRATEGY_LENGTH_POLICY_OVERRIDE
    assert w4["payload"]["blocking_reasons"] == []
