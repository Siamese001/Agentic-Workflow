"""W8 ADG runtime-proxy coverage for generation, quality, and X1D fail-closed gates."""

from __future__ import annotations

import json

import pytest

from apps_lic.engines import generation_engine as generation_engine_module
from apps_lic.engines.generation_engine import GenerationEngine
from apps_lic.engines.message_quality import (
    EXIT_CLEAR_DRAFT,
    REASON_MISSING_CLAIMS_USED,
    validate_message_quality,
)
from apps_lic.engines.validation_exit import JUDGE_UNAVAILABLE
from apps_lic.engines.whole_message_generation import generate_whole_message_candidates
from apps_lic.engines.x1d_claude_judge_adapter import run_claude_x1d_judges
from apps_lic.policy.reasoning_intensity import (
    R3_STRICT,
    SC_3,
    STRICT_JUDGES,
    default_reasoning_policy,
)
from tests.apps_lic.test_w6_x1d_judge_policy import _request, _store_for


def _strict_policy() -> dict[str, object]:
    policy = default_reasoning_policy()
    policy.update(
        {
            "sc_level": SC_3,
            "reasoning_intensity": R3_STRICT,
            "judge_profile": "high_risk_strict",
            "judges": list(STRICT_JUDGES),
            "max_candidates": 3,
        }
    )
    return policy


def _generation_context(company: str) -> dict[str, object]:
    return {
        "generation_prompt": (
            f"Target contact: Jane Smith | Senior Technical Recruiter | {company}\n"
            "Sender proof allowed claim IDs: sp_agentic_platform\n"
            "[recipient_class=RECRUITER]\n"
            "Draft a concise LinkedIn note grounded only in the supplied company context."
        ),
        "sender_persona": {
            "voice_register": "professional",
            "recipient_class": "RECRUITER",
            "target_contact": {
                "verified_name": "Jane Smith",
                "title": "Senior Technical Recruiter",
                "company_name": company,
            },
        },
        "c03_allowed_claim_ids": ["sp_agentic_platform"],
        "reasoning_policy": _strict_policy(),
    }


@pytest.mark.parametrize(
    ("company", "expected_terms"),
    [
        ("Citi", ("Citi", "regulated finance")),
        ("Neo4j", ("Neo4j", "graph")),
    ],
)
def test_stub_materializes_sc3_candidates_without_aig_texture_for_non_aig_companies(
    company: str,
    expected_terms: tuple[str, ...],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APPS_LIC_TEST_PROVIDER_STUB", "1")

    draft = GenerationEngine().execute(_generation_context(company))["draft_message"]

    assert draft["candidate_count"] == 3
    assert len(draft["candidates"]) == 3
    assert draft["selected_candidate_id"] in {
        candidate["candidate_id"] for candidate in draft["candidates"]
    }
    assert draft["claims_used"] == ["sp_agentic_platform"]
    assert all(
        candidate["claims_used"] == ["sp_agentic_platform"]
        for candidate in draft["candidates"]
    )
    combined_text = " ".join(
        [draft["message_text"]]
        + [candidate["draft_text"] for candidate in draft["candidates"]]
    )
    for term in expected_terms:
        assert term.lower() in combined_text.lower()
    for forbidden in ("AIG Assist", "underwriting", "claims", "insurance"):
        assert forbidden.lower() not in combined_text.lower()


def test_provider_shortfall_emits_non_passing_no_candidate_draft(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("APPS_LIC_TEST_PROVIDER_STUB", raising=False)
    monkeypatch.setenv("APPS_LIC_VLLM_BASE_URL", "http://127.0.0.1:9/v1")
    monkeypatch.setenv("APPS_LIC_QWEN_TIMEOUT_SECONDS", "0.1")
    monkeypatch.setenv("APPS_LIC_VLLM_HEALTHCHECK_ENABLED", "1")
    monkeypatch.setenv("APPS_LIC_REQUIRE_QWEN_VLLM", "0")

    draft = GenerationEngine().execute(_generation_context("Citi"))["draft_message"]

    assert draft["message_text"] == ""
    assert draft["body"] == ""
    assert draft["intended_next_step"] == ""
    assert draft["candidate_count"] == 0
    assert draft["candidate_selection_strategy"] == "none_provider_unavailable"
    assert draft["claims_used"] == []
    assert draft["unsupported_claims"] == ["qwen_vllm_unavailable"]
    assert draft["generator"] == "qwen_vllm_unavailable"


def test_inmail_generation_expands_short_provider_body_to_budget_and_role_subject(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    short_body = (
        "Hi Nina, AIG's VP, Global Head of Agentic AI Solutions role sits in regulated "
        "insurance AI across claims, underwriting, GenAI standards, and governance. "
        "I designed and operationalized a governed agentic AI platform for regulated "
        "enterprise workflows, combining GraphRAG retrieval, policy gating, validation "
        "controls, and replayable traces. Would a quick screen on fit for the claims, "
        "underwriting, and GenAI governance scope be useful?"
    )
    provider_payload = {
        "message_text": short_body,
        "subject_line": "Strategic Technical Recruiter and Sourcer fit at AIG",
        "selected_candidate_id": "1",
        "candidates": [
            {
                "candidate_id": "1",
                "draft_text": short_body,
                "subject_line": "Strategic Technical Recruiter and Sourcer fit at AIG",
                "claims_used": ["sp_agentic_platform"],
            }
        ],
        "claims_used": ["sp_agentic_platform"],
    }

    def fake_qwen_generation(**_kwargs: object) -> str:
        return json.dumps(provider_payload)

    monkeypatch.delenv("APPS_LIC_TEST_PROVIDER_STUB", raising=False)
    monkeypatch.setattr(
        GenerationEngine,
        "_try_qwen_generation",
        staticmethod(fake_qwen_generation),
    )
    context = _generation_context("AIG")
    context["jd_fields"] = {
        "position_name": "VP, Global Head of Agentic AI Solutions",
        "requisition_number": "JR2601998",
    }
    context["c03_length_budget"] = {
        "budget_key": "recruiter_role_specific_inmail",
        "min_words": 95,
        "max_words": 145,
        "min_sentences": 5,
        "max_sentences": 7,
        "hard_cap_chars": 1900,
    }

    draft = GenerationEngine().execute(context)["draft_message"]

    assert draft["subject_line"] == "VP, Global Head of Agentic AI Solutions fit at AIG"
    assert "Recruiter" not in draft["subject_line"]
    assert generation_engine_module._sentence_count_text(draft["message_text"]) >= 5
    assert generation_engine_module._word_count_text(draft["message_text"]) >= 95
    assert len(draft["message_text"]) <= 1900
    assert draft["message_text"].strip().endswith("?")
    lowered = draft["message_text"].lower()
    for forbidden in (
        "is it worth 15 minutes",
        "release gate",
        "release-gate",
        "compare where",
        "$22m",
        "20% margin",
    ):
        assert forbidden not in lowered


def test_connection_request_repairs_pitchy_provider_body_without_signature(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pitchy_body = (
        "Hi Scott, Since AIG is putting agentic AI under the Global CDO, the hard call "
        "is not demo quality; it is how claims and underwriting agents get policy-gated, "
        "traceable approval before rollout. I designed and operationalized a governed "
        "agentic AI platform for regulated enterprise workflows, combining multi-agent "
        "orchestration, GraphRAG retrieval, policy gating, validation controls, and "
        "replayable traces; I also productized agentic AI primitives into reusable "
        "services, generating $22M in IP-led revenue and 20% margin expansion. Is it "
        "worth 15 minutes to compare where AIG should set that claims-and-underwriting "
        "release gate?\n\nAmit"
    )
    provider_payload = {
        "message_text": pitchy_body,
        "subject_line": "AIG release gate",
        "selected_candidate_id": "1",
        "candidates": [
            {
                "candidate_id": "1",
                "draft_text": pitchy_body,
                "subject_line": "AIG release gate",
                "claims_used": [
                    "sp_agentic_platform",
                    "sp_runtime_reliability",
                    "sp_platform_commercialization",
                ],
            }
        ],
        "claims_used": [
            "sp_agentic_platform",
            "sp_runtime_reliability",
            "sp_platform_commercialization",
        ],
    }

    def fake_qwen_generation(**_kwargs: object) -> str:
        return json.dumps(provider_payload)

    monkeypatch.delenv("APPS_LIC_TEST_PROVIDER_STUB", raising=False)
    monkeypatch.setattr(
        GenerationEngine,
        "_try_qwen_generation",
        staticmethod(fake_qwen_generation),
    )
    context = {
        "generation_prompt": (
            "Target contact: Scott Hallworth | Global Chief Data Officer | AIG\n"
            "Sender proof allowed claim IDs: sp_agentic_platform, sp_runtime_reliability, "
            "sp_platform_commercialization\n"
            "[recipient_class=C_LEVEL]\n"
            "Draft a LinkedIn connection request grounded only in the supplied company context."
        ),
        "sender_persona": {
            "voice_register": "professional",
            "recipient_class": "C_LEVEL",
            "target_contact": {
                "verified_name": "Scott Hallworth",
                "title": "Global Chief Data Officer",
                "company_name": "AIG",
            },
        },
        "c03_allowed_claim_ids": [
            "sp_agentic_platform",
            "sp_runtime_reliability",
            "sp_platform_commercialization",
        ],
        "reasoning_policy": _strict_policy(),
        "c03_length_budget": {
            "budget_key": "linkedin_chat_connection_request",
            "hard_cap_chars": 300,
            "max_sentences": 2,
            "channel": "linkedin_chat",
            "route_family": "CONNECTION_REQ",
            "subject_required": False,
        },
    }

    draft = GenerationEngine().execute(context)["draft_message"]
    text = draft["message_text"]
    lowered = text.lower()

    assert draft["channel"] == "linkedin_chat"
    assert draft["subject_line"] == ""
    assert len(text) <= 300
    assert text.strip().endswith("?")
    assert not text.lower().endswith("amit")
    assert "open to connecting?" in lowered
    assert "governed agentic ai platform" in lowered
    for forbidden in (
        "hard call",
        "15 minutes",
        "release gate",
        "release-gate",
        "compare where",
        "$22m",
        "20% margin",
    ):
        assert forbidden not in lowered


def test_message_quality_blocks_clear_draft_without_claim_ids() -> None:
    report = validate_message_quality(
        [
            {
                "profile_id": "profile_1",
                "exit_disposition": EXIT_CLEAR_DRAFT,
                "derived_class": "RECRUITER",
                "message_type": "role_specific",
                "jd_position_name": "Director, AI Platforms",
                "jd_requisition_number": "JR-12345",
                "draft_text": (
                    "Hi Jane, the Director, AI Platforms role JR-12345 appears "
                    "to need governed AI platform delivery. Worth a focused resume review?"
                ),
                "claims_used": [],
            }
        ]
    )

    assert report.passed is False
    assert REASON_MISSING_CLAIMS_USED in {
        violation.reason_code for violation in report.violations
    }


def test_non_live_x1d_transport_cannot_clear_required_judges() -> None:
    class FakePassingTransport:
        def __call__(self, payload: dict[str, object]) -> dict[str, object]:
            return {
                "score": 0.99,
                "passed": True,
                "issues": [],
                "required_repairs": [],
            }

    request = _request(
        _store_for(
            title="Director of Engineering",
            jd={
                "title": "Director, AI Platforms",
                "requisition_number": "JR-12345",
                "company": "AIG",
                "description": "Build production AI platforms.",
            },
        ),
        message_type_hint="role_specific",
        campaign_objective="Ask for a role-specific screen.",
    )
    batch = generate_whole_message_candidates(request)

    results = run_claude_x1d_judges(
        request,
        batch.candidates[0],
        transport=FakePassingTransport(),
    )

    assert results
    assert all(result.availability_status == JUDGE_UNAVAILABLE for result in results)
    assert all(
        "non_live_claude_transport_rejected" in result.issues
        for result in results
    )
