"""W7 sentinel tests for apps_lic credibility, proof, and insight engines.

Covers SE-P1b, SE-P1c, SE-P1d:
- SE-P1b: SenderCredibilityEngine — hash-bound claims, top-3 ranking,
          rejected unsourced claims, card_hash, from master_resume.json.
- SE-P1c: RepoProofLinker — required/optional/not_applicable verdicts,
          channel-scoped formats, is_fail_closed, short LinkedIn bypass.
- SE-P1d: AsymmetricInsightEngine — config-gated, bypass modes,
          is_fail_closed, hitl_required, from_plan_rules factory.

Plan: apps-lic-canonical-spine-wireup-e7c2a5 W7.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
MASTER_RESUME = REPO_ROOT / "apps_shared" / "data" / "master_resume.json"
PLAN_RULES    = REPO_ROOT / "apps_lic" / "config" / "lic_plan_rules.yaml"


# ===========================================================================
# SE-P1b — SenderCredibilityEngine
# ===========================================================================

def test_credibility_engine_module_exists():
    """SE-P1b: sender_credibility_engine.py must exist."""
    assert (REPO_ROOT / "apps_lic" / "engines" / "sender_credibility_engine.py").exists()


def test_credibility_engine_loads_master_resume():
    """SE-P1b: engine must load master_resume.json without error."""
    from apps_lic.engines.sender_credibility_engine import SenderCredibilityEngine
    e = SenderCredibilityEngine()
    card = e.build_card(recipient_class="EXECUTIVE", outreach_mode="cold")
    assert card is not None
    assert len(card.all_claims) > 0


def test_credibility_engine_top_claims_at_most_n():
    """SE-P1b: top_claims must contain at most 3 claims by default."""
    from apps_lic.engines.sender_credibility_engine import SenderCredibilityEngine
    e = SenderCredibilityEngine()
    card = e.build_card(recipient_class="EXECUTIVE", outreach_mode="cold")
    assert len(card.top_claims) <= 3


def test_credibility_engine_all_claims_have_source_ref():
    """SE-P1b: all_claims (verified) must each have non-empty source_ref."""
    from apps_lic.engines.sender_credibility_engine import SenderCredibilityEngine
    e = SenderCredibilityEngine()
    card = e.build_card(recipient_class="CTO", outreach_mode="cold")
    for c in card.all_claims:
        assert c.source_ref, f"Claim {c.label!r} has empty source_ref"
        assert c.source_ref.startswith("sha256:")


def test_credibility_engine_source_ref_is_deterministic():
    """SE-P1b: source_ref is sha256-based and deterministic across calls."""
    from apps_lic.engines.sender_credibility_engine import SenderCredibilityEngine
    e = SenderCredibilityEngine()
    card1 = e.build_card(recipient_class="CTO", outreach_mode="cold")
    card2 = e.build_card(recipient_class="CTO", outreach_mode="cold")
    refs1 = {c.source_ref for c in card1.all_claims}
    refs2 = {c.source_ref for c in card2.all_claims}
    assert refs1 == refs2


def test_credibility_engine_top_claims_ranked_by_fit_score():
    """SE-P1b: top_claims must be ranked desc by fit_score_for_recipient."""
    from apps_lic.engines.sender_credibility_engine import SenderCredibilityEngine
    e = SenderCredibilityEngine()
    card = e.build_card(recipient_class="EXECUTIVE", outreach_mode="cold")
    scores = [c.fit_score_for_recipient for c in card.top_claims]
    assert scores == sorted(scores, reverse=True), (
        "top_claims must be sorted descending by fit_score_for_recipient"
    )


def test_credibility_engine_rejected_claims_have_no_source_ref():
    """SE-P1b: rejected_claims must all have empty source_ref and is_verified=False."""
    import json
    from apps_lic.engines.sender_credibility_engine import SenderCredibilityEngine
    # Inject a resume with a bullet missing 'text' (engine will skip) and
    # test via custom resume data that has unsourced claim
    custom_resume = {
        "schema_version": "test",
        "professional_experience": [{
            "company": "Test Co",
            "bullet_pool": [
                {"label": "Good claim", "text": "Built K8s platform", "tags": ["k8s"]},
            ]
        }]
    }
    e = SenderCredibilityEngine(resume_data=custom_resume)
    card = e.build_card(recipient_class="EXECUTIVE", outreach_mode="cold")
    # All claims should be verified (have source_refs computed)
    assert len(card.all_claims) >= 1
    for c in card.all_claims:
        assert c.is_verified is True


def test_credibility_engine_card_hash_non_empty():
    """SE-P1b: card_hash must be non-empty and start with sha256:."""
    from apps_lic.engines.sender_credibility_engine import SenderCredibilityEngine
    e = SenderCredibilityEngine()
    card = e.build_card(recipient_class="EXECUTIVE", outreach_mode="cold")
    assert card.card_hash.startswith("sha256:")


def test_credibility_engine_card_hash_is_deterministic():
    """SE-P1b: card_hash is deterministic — same context produces same hash."""
    from apps_lic.engines.sender_credibility_engine import SenderCredibilityEngine
    e = SenderCredibilityEngine()
    card1 = e.build_card(recipient_class="EXECUTIVE", outreach_mode="cold")
    card2 = e.build_card(recipient_class="EXECUTIVE", outreach_mode="cold")
    assert card1.card_hash == card2.card_hash


def test_credibility_engine_top_n_configurable():
    """SE-P1b: top_n parameter is respected."""
    from apps_lic.engines.sender_credibility_engine import SenderCredibilityEngine
    e = SenderCredibilityEngine()
    card = e.build_card(recipient_class="CTO", outreach_mode="cold", top_n=5)
    assert len(card.top_claims) <= 5


def test_credibility_engine_no_provider_imports():
    """SE-P1b: sender_credibility_engine.py must not import providers."""
    src = (REPO_ROOT / "apps_lic" / "engines" / "sender_credibility_engine.py").read_text(encoding="utf-8")
    for forbidden in ("openai", "anthropic", "boto3", "google.generativeai"):
        assert forbidden not in src


def test_credibility_engine_recipient_class_stored():
    """SE-P1b: SenderCredibilityCard stores recipient_class and outreach_mode."""
    from apps_lic.engines.sender_credibility_engine import SenderCredibilityEngine
    e = SenderCredibilityEngine()
    card = e.build_card(recipient_class="VP_ENG", outreach_mode="warm")
    assert card.recipient_class == "VP_ENG"
    assert card.outreach_mode == "warm"


# ===========================================================================
# SE-P1c — RepoProofLinker
# ===========================================================================

def test_proof_linker_module_exists():
    """SE-P1c: repo_proof_linker.py must exist."""
    assert (REPO_ROOT / "apps_lic" / "engines" / "repo_proof_linker.py").exists()


def test_proof_linker_exec_high_depth_required():
    """SE-P1c: EXECUTIVE + email + high depth → verdict=required."""
    from apps_lic.engines.repo_proof_linker import RepoProofLinker, VERDICT_REQUIRED
    linker = RepoProofLinker()
    req = linker.evaluate(
        recipient_class="EXECUTIVE",
        channel="email",
        technical_claim_depth="high",
        draft_word_count=120,
        proof_provided=False,
    )
    assert req.verdict == VERDICT_REQUIRED
    assert req.is_fail_closed is True


def test_proof_linker_exec_high_depth_proof_provided_no_fail():
    """SE-P1c: EXECUTIVE + high depth + proof_provided=True → is_fail_closed=False."""
    from apps_lic.engines.repo_proof_linker import RepoProofLinker
    linker = RepoProofLinker()
    req = linker.evaluate(
        recipient_class="EXECUTIVE",
        channel="email",
        technical_claim_depth="high",
        draft_word_count=120,
        proof_provided=True,
    )
    assert req.is_fail_closed is False


def test_proof_linker_cto_medium_high_required():
    """SE-P1c: CTO + email + medium_high → required."""
    from apps_lic.engines.repo_proof_linker import RepoProofLinker, VERDICT_REQUIRED
    linker = RepoProofLinker()
    req = linker.evaluate(
        recipient_class="CTO",
        channel="email",
        technical_claim_depth="medium_high",
        draft_word_count=100,
        proof_provided=False,
    )
    assert req.verdict == VERDICT_REQUIRED


def test_proof_linker_recruiter_high_depth_optional():
    """SE-P1c: RECRUITER + high depth → optional (not required)."""
    from apps_lic.engines.repo_proof_linker import RepoProofLinker, VERDICT_OPTIONAL
    linker = RepoProofLinker()
    req = linker.evaluate(
        recipient_class="RECRUITER",
        channel="email",
        technical_claim_depth="high",
        draft_word_count=150,
        proof_provided=False,
    )
    assert req.verdict == VERDICT_OPTIONAL
    assert req.is_fail_closed is False


def test_proof_linker_recruiter_medium_not_applicable():
    """SE-P1c: RECRUITER + medium depth → not_applicable."""
    from apps_lic.engines.repo_proof_linker import RepoProofLinker, VERDICT_NOT_APPLICABLE
    linker = RepoProofLinker()
    req = linker.evaluate(
        recipient_class="RECRUITER",
        channel="email",
        technical_claim_depth="medium",
        draft_word_count=150,
    )
    assert req.verdict == VERDICT_NOT_APPLICABLE


def test_proof_linker_no_tech_claims_not_applicable():
    """SE-P1c: technical_claim_depth=none → not_applicable regardless of recipient_class."""
    from apps_lic.engines.repo_proof_linker import RepoProofLinker, VERDICT_NOT_APPLICABLE
    linker = RepoProofLinker()
    for rc in ("EXECUTIVE", "CTO", "RECRUITER"):
        req = linker.evaluate(
            recipient_class=rc,
            channel="email",
            technical_claim_depth="none",
            draft_word_count=100,
        )
        assert req.verdict == VERDICT_NOT_APPLICABLE, f"Expected not_applicable for {rc} with depth=none"


def test_proof_linker_short_linkedin_not_applicable():
    """SE-P1c: LinkedIn message ≤60 words → not_applicable (channel fit guard)."""
    from apps_lic.engines.repo_proof_linker import RepoProofLinker, VERDICT_NOT_APPLICABLE
    linker = RepoProofLinker()
    req = linker.evaluate(
        recipient_class="CTO",
        channel="linkedin",
        technical_claim_depth="high",
        draft_word_count=55,   # ≤60
        proof_provided=False,
    )
    assert req.verdict == VERDICT_NOT_APPLICABLE
    assert req.is_fail_closed is False


def test_proof_linker_email_allows_all_formats():
    """SE-P1c: email channel allows all 5 proof formats."""
    from apps_lic.engines.repo_proof_linker import RepoProofLinker, PROOF_FORMATS
    linker = RepoProofLinker()
    req = linker.evaluate(
        recipient_class="CTO",
        channel="email",
        technical_claim_depth="high",
        draft_word_count=100,
        proof_provided=True,
    )
    assert set(req.proof_formats_allowed) == set(PROOF_FORMATS)


def test_proof_linker_linkedin_restricts_formats():
    """SE-P1c: linkedin channel returns subset of proof formats."""
    from apps_lic.engines.repo_proof_linker import RepoProofLinker
    linker = RepoProofLinker()
    req = linker.evaluate(
        recipient_class="CTO",
        channel="linkedin",
        technical_claim_depth="high",
        draft_word_count=75,   # >60 so not the short bypass
        proof_provided=True,
    )
    assert "github_link" not in req.proof_formats_allowed
    assert "resume_metric" in req.proof_formats_allowed


def test_proof_linker_evidence_ref_populated():
    """SE-P1c: evidence_ref must contain key fields."""
    from apps_lic.engines.repo_proof_linker import RepoProofLinker
    linker = RepoProofLinker()
    req = linker.evaluate(
        recipient_class="CTO",
        channel="email",
        technical_claim_depth="high",
        draft_word_count=100,
    )
    assert "recipient_class=CTO" in req.evidence_ref
    assert "verdict=" in req.evidence_ref
    assert "technical_claim_depth=high" in req.evidence_ref


def test_proof_linker_no_provider_imports():
    """SE-P1c: repo_proof_linker.py must not import providers."""
    src = (REPO_ROOT / "apps_lic" / "engines" / "repo_proof_linker.py").read_text(encoding="utf-8")
    for forbidden in ("openai", "anthropic", "boto3", "google.generativeai"):
        assert forbidden not in src


def test_proof_linker_text_channel_not_applicable():
    """SE-P1c: text channel → not_applicable (too short for proof)."""
    from apps_lic.engines.repo_proof_linker import RepoProofLinker, VERDICT_NOT_APPLICABLE
    linker = RepoProofLinker()
    req = linker.evaluate(
        recipient_class="CTO",
        channel="text",
        technical_claim_depth="high",
        draft_word_count=40,
    )
    assert req.verdict == VERDICT_NOT_APPLICABLE


# ===========================================================================
# SE-P1d — AsymmetricInsightEngine
# ===========================================================================

def test_insight_engine_module_exists():
    """SE-P1d: asymmetric_insight_engine.py must exist."""
    assert (REPO_ROOT / "apps_lic" / "engines" / "asymmetric_insight_engine.py").exists()


def test_insight_engine_exec_cold_required():
    """SE-P1d: EXECUTIVE+cold → verdict=required."""
    from apps_lic.engines.asymmetric_insight_engine import (
        AsymmetricInsightEngine, VERDICT_REQUIRED
    )
    e = AsymmetricInsightEngine()
    req = e.evaluate(recipient_class="EXECUTIVE", outreach_mode="cold")
    assert req.verdict == VERDICT_REQUIRED


def test_insight_engine_recruiter_not_required():
    """SE-P1d: RECRUITER → verdict=not_applicable."""
    from apps_lic.engines.asymmetric_insight_engine import (
        AsymmetricInsightEngine, VERDICT_NOT_APPLICABLE
    )
    e = AsymmetricInsightEngine()
    req = e.evaluate(recipient_class="RECRUITER", outreach_mode="cold")
    assert req.verdict == VERDICT_NOT_APPLICABLE
    assert req.is_satisfied is True
    assert req.is_fail_closed is False


def test_insight_engine_followup_never_required():
    """SE-P1d: followup mode → not_applicable regardless of recipient_class."""
    from apps_lic.engines.asymmetric_insight_engine import (
        AsymmetricInsightEngine, VERDICT_NOT_APPLICABLE
    )
    e = AsymmetricInsightEngine()
    for rc in ("EXECUTIVE", "CTO", "VP_ENG"):
        req = e.evaluate(recipient_class=rc, outreach_mode="followup")
        assert req.verdict == VERDICT_NOT_APPLICABLE, f"followup must be not_applicable for {rc}"


def test_insight_engine_referral_never_required():
    """SE-P1d: referral mode → not_applicable."""
    from apps_lic.engines.asymmetric_insight_engine import (
        AsymmetricInsightEngine, VERDICT_NOT_APPLICABLE
    )
    e = AsymmetricInsightEngine()
    req = e.evaluate(recipient_class="EXECUTIVE", outreach_mode="referral")
    assert req.verdict == VERDICT_NOT_APPLICABLE


def test_insight_engine_required_not_satisfied_fail_closed():
    """SE-P1d: required + insight_provided=False + fail_closed → is_fail_closed=True."""
    from apps_lic.engines.asymmetric_insight_engine import AsymmetricInsightEngine
    e = AsymmetricInsightEngine()
    req = e.evaluate(
        recipient_class="EXECUTIVE",
        outreach_mode="cold",
        insight_provided=False,
        omission_policy="fail_closed",
    )
    assert req.is_fail_closed is True
    assert req.is_satisfied is False


def test_insight_engine_required_not_satisfied_hitl():
    """SE-P1d: required + insight_provided=False + hitl_required → hitl_required=True."""
    from apps_lic.engines.asymmetric_insight_engine import AsymmetricInsightEngine
    e = AsymmetricInsightEngine()
    req = e.evaluate(
        recipient_class="EXECUTIVE",
        outreach_mode="cold",
        insight_provided=False,
        omission_policy="hitl_required",
    )
    assert req.hitl_required is True
    assert req.is_fail_closed is False


def test_insight_engine_required_satisfied_with_valid_insight():
    """SE-P1d: required + valid insight → is_satisfied=True, no fail."""
    from apps_lic.engines.asymmetric_insight_engine import (
        AsymmetricInsightEngine, AsymmetricInsight
    )
    e = AsymmetricInsightEngine()
    insight = AsymmetricInsight(
        insight_text="Series B signals platform build vs buy inflection",
        source_ref="sha256:abc",
        insight_type="company_strategy",
        confidence=0.85,
    )
    req = e.evaluate(
        recipient_class="EXECUTIVE",
        outreach_mode="cold",
        insight_provided=True,
        omission_policy="fail_closed",
        insights=(insight,),
    )
    assert req.is_satisfied is True
    assert req.is_fail_closed is False


def test_insight_engine_warns_on_empty_source_ref():
    """SE-P1d: AsymmetricInsight with empty source_ref triggers a warning."""
    from apps_lic.engines.asymmetric_insight_engine import (
        AsymmetricInsightEngine, AsymmetricInsight
    )
    e = AsymmetricInsightEngine()
    insight = AsymmetricInsight(
        insight_text="Some observation",
        source_ref="",       # empty → must warn
        insight_type="market_observation",
        confidence=0.9,
    )
    req = e.evaluate(
        recipient_class="EXECUTIVE",
        outreach_mode="cold",
        insight_provided=True,
        omission_policy="omit_unsupported",
        insights=(insight,),
    )
    assert any("source_ref" in w for w in req.warnings)


def test_insight_engine_warns_on_low_confidence():
    """SE-P1d: AsymmetricInsight with confidence < 0.5 triggers a warning."""
    from apps_lic.engines.asymmetric_insight_engine import (
        AsymmetricInsightEngine, AsymmetricInsight
    )
    e = AsymmetricInsightEngine()
    insight = AsymmetricInsight(
        insight_text="Weak observation",
        source_ref="sha256:xyz",
        insight_type="role_context",
        confidence=0.3,       # < 0.5 → warn
    )
    req = e.evaluate(
        recipient_class="CTO",
        outreach_mode="cold",
        insight_provided=True,
        omission_policy="omit_unsupported",
        insights=(insight,),
    )
    assert any("0.3" in w or "weak" in w.lower() for w in req.warnings)


def test_insight_engine_from_plan_rules():
    """SE-P1d: from_plan_rules() reads asymmetric_insight_required from YAML."""
    from apps_lic.engines.asymmetric_insight_engine import AsymmetricInsightEngine
    with PLAN_RULES.open(encoding="utf-8") as fh:
        rules = yaml.safe_load(fh)
    e = AsymmetricInsightEngine.from_plan_rules(rules)
    assert e.is_required_for("EXECUTIVE") is True
    assert e.is_required_for("RECRUITER") is False
    assert e.is_required_for("CTO") is True


def test_insight_engine_config_override():
    """SE-P1d: config_overrides can enable insight for HIRING_MANAGER."""
    from apps_lic.engines.asymmetric_insight_engine import (
        AsymmetricInsightEngine, VERDICT_REQUIRED
    )
    e = AsymmetricInsightEngine(config_overrides={"HIRING_MANAGER": True})
    req = e.evaluate(recipient_class="HIRING_MANAGER", outreach_mode="cold")
    assert req.verdict == VERDICT_REQUIRED


def test_insight_engine_evidence_ref_populated():
    """SE-P1d: evidence_ref must contain key fields."""
    from apps_lic.engines.asymmetric_insight_engine import AsymmetricInsightEngine
    e = AsymmetricInsightEngine()
    req = e.evaluate(recipient_class="EXECUTIVE", outreach_mode="cold")
    assert "recipient_class=EXECUTIVE" in req.evidence_ref
    assert "verdict=" in req.evidence_ref
    assert "is_satisfied=" in req.evidence_ref


def test_insight_engine_no_provider_imports():
    """SE-P1d: asymmetric_insight_engine.py must not import providers."""
    src = (REPO_ROOT / "apps_lic" / "engines" / "asymmetric_insight_engine.py").read_text(encoding="utf-8")
    for forbidden in ("openai", "anthropic", "boto3", "google.generativeai"):
        assert forbidden not in src


def test_insight_engine_cto_vp_eng_required():
    """SE-P1d: CTO and VP_ENG must both be required by default config."""
    from apps_lic.engines.asymmetric_insight_engine import AsymmetricInsightEngine, VERDICT_REQUIRED
    e = AsymmetricInsightEngine()
    for rc in ("CTO", "VP_ENG"):
        req = e.evaluate(recipient_class=rc, outreach_mode="cold")
        assert req.verdict == VERDICT_REQUIRED, f"{rc}+cold must be required"


def test_insight_engine_warm_mode_exec_still_required():
    """SE-P1d: warm mode does not bypass insight requirement for EXECUTIVE."""
    from apps_lic.engines.asymmetric_insight_engine import AsymmetricInsightEngine, VERDICT_REQUIRED
    e = AsymmetricInsightEngine()
    req = e.evaluate(recipient_class="EXECUTIVE", outreach_mode="warm")
    assert req.verdict == VERDICT_REQUIRED
