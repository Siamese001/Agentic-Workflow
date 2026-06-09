"""W7 generic-vs-AIG validation profile scoping."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_lic.engines.generation_engine import GenerationEngine
from apps_lic.engines.validation_engine import ValidationEngine
from apps_lic.runtime.dispatch.canonical_dispatch import (
    build_cli_ingress_raw,
    run_canonical_apps_lic_spine,
)
from tests.apps_lic.canonical_readiness_fixtures import (
    company_governed_opportunity_facts,
)


def _validation_report(
    *,
    company: str,
    message_text: str,
    validation_profile_id: str = "",
    profile_company: str | None = None,
    evidence_items: list[dict[str, object]] | None = None,
) -> dict:
    context = {
        "validation_profile_id": validation_profile_id,
        "profile_features": {
            "target_contact": {
                "verified_name": "Maya Patel",
                "title": "VP Product",
                "company_name": company if profile_company is None else profile_company,
            }
        },
        "draft_message": {
            "channel": "linkedin",
            "recipient_class": "executive",
            "target_contact_company": company,
            "message_text": message_text,
            "unsupported_claims": [],
        },
        "evidence_bundle": {
            "support_status": "PASS",
            "count": len(evidence_items or ()),
            "items": evidence_items or [],
        },
        "reasoning_policy": {
            "fail_closed_on_empty_evidence": False,
            "max_candidates": 1,
        },
    }
    return ValidationEngine().execute(context)["validation_report"]


def test_generic_non_aig_profile_does_not_require_aig_operating_terms() -> None:
    report = _validation_report(
        company="Neo4j",
        message_text=(
            "Hi Maya, your graph data platform leadership maps well to senior "
            "engineering work in production AI. Open to a brief chat about "
            "the product leadership role?"
        ),
    )

    assert report["passed"] is True
    assert report["validation_profile_id"] == "generic_company"
    assert "aig_operating_insight_missing" not in report["issues"]


def test_aig_profile_requires_aig_operating_insight_terms() -> None:
    report = _validation_report(
        company="AIG",
        validation_profile_id="aig_operating_insight",
        message_text=(
            "Hi Maya, your product leadership maps well to senior engineering "
            "work in production AI. Open to a brief chat about the role?"
        ),
    )

    assert report["passed"] is False
    assert report["validation_profile_id"] == "aig_operating_insight"
    assert "aig_operating_insight_missing" in report["issues"]


def test_aig_profile_auto_selects_full_name_with_acronym() -> None:
    report = _validation_report(
        company="American International Group (AIG)",
        message_text=(
            "Hi Maya, AIG's Agentic AI role spans claims, underwriting, "
            "governance, and operating-model change. I have built governed "
            "agent workflows with evals and telemetry. Open to a brief chat?"
        ),
    )

    assert report["passed"] is True
    assert report["validation_profile_id"] == "aig_operating_insight"
    assert "profile_forbidden_term:underwriting" not in report["issues"]
    assert "profile_forbidden_term:claims" not in report["issues"]


def test_aig_profile_ignores_unknown_placeholder_before_draft_company() -> None:
    report = _validation_report(
        company="AIG",
        profile_company="Unknown",
        message_text=(
            "Hi Maya, AIG's Agentic AI role spans claims, underwriting, "
            "governance, and operating-model change. I have built governed "
            "agent workflows with evals and telemetry. Open to a brief chat?"
        ),
    )

    assert report["passed"] is True
    assert report["validation_profile_id"] == "aig_operating_insight"


def test_non_aig_profile_blocks_aig_only_terms_without_evidence() -> None:
    unsupported = _validation_report(
        company="Citi",
        message_text=(
            "Hi Maya, Citi's AI work across underwriting and claims maps to "
            "my governed agent workflows with evals. Open to a brief chat?"
        ),
    )
    assert unsupported["passed"] is False
    assert "profile_forbidden_term:underwriting" in unsupported["issues"]
    assert "profile_forbidden_term:claims" in unsupported["issues"]

    supported = _validation_report(
        company="Citi",
        message_text=(
            "Hi Maya, Citi's AI work across underwriting and claims maps to "
            "my governed agent workflows with evals. Open to a brief chat?"
        ),
        evidence_items=[
            {
                "id": "ev-citi",
                "text": "Citi public briefing independently mentions underwriting and claims.",
            }
        ],
    )
    assert "profile_forbidden_term:underwriting" not in supported["issues"]
    assert "profile_forbidden_term:claims" not in supported["issues"]


def test_trigger_like_company_claim_requires_supporting_evidence() -> None:
    unsupported = _validation_report(
        company="Neo4j",
        message_text=(
            "Hi Maya, Neo4j recently launched a graph AI platform that maps "
            "to my senior engineering work in production AI. Open to a brief chat?"
        ),
    )
    assert unsupported["passed"] is False
    assert "unsupported_company_trigger_claim" in unsupported["issues"]

    supported = _validation_report(
        company="Neo4j",
        message_text=(
            "Hi Maya, Neo4j recently launched a graph AI platform that maps "
            "to my senior engineering work in production AI. Open to a brief chat?"
        ),
        evidence_items=[
            {
                "id": "ev-neo4j-trigger",
                "text": "Neo4j recently launched graph AI platform capabilities.",
            }
        ],
    )
    assert "unsupported_company_trigger_claim" not in supported["issues"]


def test_deterministic_stub_does_not_leak_aig_terms_for_neo4j(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APPS_LIC_TEST_PROVIDER_STUB", "1")
    draft = GenerationEngine().execute(
        {
            "generation_prompt": "Target contact: Maya Patel | VP Product | Neo4j",
            "sender_persona": {
                "recipient_class": "EXECUTIVE",
                "target_contact": {
                    "verified_name": "Maya Patel",
                    "title": "VP Product",
                    "company_name": "Neo4j",
                },
            },
        }
    )["draft_message"]

    message = draft["message_text"].lower()
    assert "neo4j" in message
    assert "graph" in message
    for forbidden in ("underwriting", "claims", "insurance", "aig assist"):
        assert forbidden not in message


@pytest.mark.parametrize(
    ("company", "trigger_text", "expected_term"),
    [
        (
            "Citi",
            "Citi published regulated finance AI governance priorities.",
            "regulated finance",
        ),
        (
            "Neo4j",
            "Neo4j published graph data platform and agentic AI priorities.",
            "graph",
        ),
    ],
)
def test_canonical_non_aig_trigger_backed_runs_do_not_leak_aig_terms(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    company: str,
    trigger_text: str,
    expected_term: str,
) -> None:
    monkeypatch.setenv("APPS_LIC_TEST_PROVIDER_STUB", "1")
    lead_profile = {
        "verified_name": "Maya Patel",
        "title": "Technical Recruiter",
        "seniority_class": "RECRUITER",
        "company_name": company,
        "industry": "Technology",
        "consent_attested": True,
    }
    raw = build_cli_ingress_raw(
        run_id=f"run_w7_{company.lower()}",
        request_id=f"req_w7_{company.lower()}",
        manual_brief=f"{company} source-backed trigger outreach context.",
        lead_profile=lead_profile,
        campaign_objective=f"Draft a concise LinkedIn message for {company} AI roles.",
        message_type_hint="trigger_based_insight",
        desired_next_step="a quick resume review",
        governed_opportunity_facts=company_governed_opportunity_facts(
            company=company,
            contact_name="Maya Patel",
            contact_title="Technical Recruiter",
            company_context=trigger_text,
            trigger_text=trigger_text,
        ),
    )

    result = run_canonical_apps_lic_spine(raw, artifact_root=tmp_path / company.lower())

    assert result.terminal_r5 is False
    assert result.exit_status == "success"
    assert result.outcome_authorized is True
    manifest = json.loads((result.artifact_dir / "spine_run_manifest.json").read_text())
    assert manifest["no_send_assertion"] is True
    assert manifest["no_l4_write_assertion"] is True

    l2 = json.loads((result.artifact_dir / "l2_execution_receipt.json").read_text())
    draft = json.loads(l2["payload"]["generated_content"])
    message = draft["message_text"].lower()
    assert company.lower() in message
    assert expected_term in message
    for forbidden in ("underwriting", "claims", "insurance", "aig assist"):
        assert forbidden not in message
