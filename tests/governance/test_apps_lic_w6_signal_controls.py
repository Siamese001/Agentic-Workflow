"""W6 sentinel tests for apps_lic signal control engines.

Covers SE-P0b, SE-P0c, SE-P1a:
- SE-P0b: ChannelLengthEnforcer — ceilings, tolerance, hard-fail, advisory, from_plan_rules.
- SE-P0c: ScopeCalibratedAskEngine — friction scores, reciprocity-first, bound-fail,
          forbidden CTA patterns, override.
- SE-P1a: RecipientTriggerEngine — sufficiency by recipient_class, downgrade, HITL,
          fail-closed, never invents triggers, verified-only counts.

Plan: apps-lic-canonical-spine-wireup-e7c2a5 W6.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
PLAN_RULES = REPO_ROOT / "apps_lic" / "config" / "lic_plan_rules.yaml"


# ===========================================================================
# SE-P0b — ChannelLengthEnforcer
# ===========================================================================

def test_channel_enforcer_module_exists():
    """SE-P0b: channel_length_enforcer.py must exist."""
    assert (REPO_ROOT / "apps_lic" / "engines" / "channel_length_enforcer.py").exists()


def test_channel_enforcer_email_exec_cold_ceiling():
    """SE-P0b: email+EXECUTIVE+cold ceiling=100."""
    from apps_lic.engines.channel_length_enforcer import ChannelLengthEnforcer
    e = ChannelLengthEnforcer()
    assert e.resolve_ceiling("email", "EXECUTIVE", "cold") == 100


def test_channel_enforcer_email_exec_warm_ceiling():
    """SE-P0b: email+EXECUTIVE+warm ceiling=120."""
    from apps_lic.engines.channel_length_enforcer import ChannelLengthEnforcer
    e = ChannelLengthEnforcer()
    assert e.resolve_ceiling("email", "EXECUTIVE", "warm") == 120


def test_channel_enforcer_email_recruiter_cold_ceiling():
    """SE-P0b: email+RECRUITER+cold ceiling=150."""
    from apps_lic.engines.channel_length_enforcer import ChannelLengthEnforcer
    e = ChannelLengthEnforcer()
    assert e.resolve_ceiling("email", "RECRUITER", "cold") == 150


def test_channel_enforcer_email_recruiter_warm_ceiling():
    """SE-P0b: email+RECRUITER+warm ceiling=200."""
    from apps_lic.engines.channel_length_enforcer import ChannelLengthEnforcer
    e = ChannelLengthEnforcer()
    assert e.resolve_ceiling("email", "RECRUITER", "warm") == 200


def test_channel_enforcer_linkedin_any_cold_ceiling():
    """SE-P0b: linkedin+any+cold ceiling=60."""
    from apps_lic.engines.channel_length_enforcer import ChannelLengthEnforcer
    e = ChannelLengthEnforcer()
    assert e.resolve_ceiling("linkedin", "EXECUTIVE", "cold") == 60


def test_channel_enforcer_linkedin_any_warm_ceiling():
    """SE-P0b: linkedin+any+warm ceiling=80."""
    from apps_lic.engines.channel_length_enforcer import ChannelLengthEnforcer
    e = ChannelLengthEnforcer()
    assert e.resolve_ceiling("linkedin", "RECRUITER", "warm") == 80


def test_channel_enforcer_referral_intro_ceiling():
    """SE-P0b: referral_intro channel ceiling=80."""
    from apps_lic.engines.channel_length_enforcer import ChannelLengthEnforcer
    e = ChannelLengthEnforcer()
    assert e.resolve_ceiling("referral_intro", "any", "any") == 80


def test_channel_enforcer_pass_within_ceiling():
    """SE-P0b: draft under ceiling → is_compliant=True, is_hard_fail=False."""
    from apps_lic.engines.channel_length_enforcer import ChannelLengthEnforcer
    e = ChannelLengthEnforcer()
    # 50 words — well under 100-word exec-cold ceiling
    draft = " ".join(["word"] * 50)
    result = e.check(draft, channel="email", recipient_class="EXECUTIVE", outreach_mode="cold")
    assert result.is_compliant is True
    assert result.is_hard_fail is False
    assert result.word_count == 50
    assert result.ceiling == 100


def test_channel_enforcer_advisory_between_ceiling_and_threshold():
    """SE-P0b: draft between ceiling and ceiling×tolerance → is_compliant=False, is_hard_fail=False."""
    from apps_lic.engines.channel_length_enforcer import ChannelLengthEnforcer
    e = ChannelLengthEnforcer()
    # 105 words — over 100-word ceiling but under 110 (100×1.10)
    draft = " ".join(["word"] * 105)
    result = e.check(draft, channel="email", recipient_class="EXECUTIVE", outreach_mode="cold")
    assert result.is_compliant is False
    assert result.is_hard_fail is False


def test_channel_enforcer_hard_fail_above_tolerance():
    """SE-P0b: draft above ceiling×tolerance → is_hard_fail=True."""
    from apps_lic.engines.channel_length_enforcer import ChannelLengthEnforcer
    e = ChannelLengthEnforcer()
    # 115 words — over 110 (100×1.10)
    draft = " ".join(["word"] * 115)
    result = e.check(draft, channel="email", recipient_class="EXECUTIVE", outreach_mode="cold")
    assert result.is_hard_fail is True


def test_channel_enforcer_hard_fail_threshold_is_ceiling_times_tolerance():
    """SE-P0b: hard_fail_threshold = int(ceiling × tolerance)."""
    from apps_lic.engines.channel_length_enforcer import ChannelLengthEnforcer
    e = ChannelLengthEnforcer()
    result = e.check("x", channel="email", recipient_class="EXECUTIVE", outreach_mode="cold")
    assert result.hard_fail_threshold == int(100 * 1.10)


def test_channel_enforcer_evidence_ref_populated():
    """SE-P0b: evidence_ref must contain channel, recipient_class, word_count, ceiling."""
    from apps_lic.engines.channel_length_enforcer import ChannelLengthEnforcer
    e = ChannelLengthEnforcer()
    draft = " ".join(["word"] * 50)
    result = e.check(draft, channel="email", recipient_class="EXECUTIVE", outreach_mode="cold")
    ref = result.evidence_ref
    assert "channel=email" in ref
    assert "recipient_class=EXECUTIVE" in ref
    assert "word_count=50" in ref
    assert "ceiling=100" in ref


def test_channel_enforcer_from_plan_rules():
    """SE-P0b: from_plan_rules() builds enforcer from lic_plan_rules.yaml."""
    from apps_lic.engines.channel_length_enforcer import ChannelLengthEnforcer
    with PLAN_RULES.open(encoding="utf-8") as fh:
        plan_rules = yaml.safe_load(fh)
    e = ChannelLengthEnforcer.from_plan_rules(plan_rules)
    assert e is not None
    # Verify at least one known ceiling resolves correctly after merge
    ceiling = e.resolve_ceiling("linkedin", "any", "cold")
    assert ceiling == 60


def test_channel_enforcer_no_provider_imports():
    """SE-P0b: channel_length_enforcer.py must not import providers."""
    src = (REPO_ROOT / "apps_lic" / "engines" / "channel_length_enforcer.py").read_text(encoding="utf-8")
    for forbidden in ("openai", "anthropic", "boto3", "google.generativeai"):
        assert forbidden not in src


def test_channel_enforcer_cto_and_vp_eng_ceilings():
    """SE-P0b: CTO and VP_ENG must have same ceiling as EXECUTIVE for cold."""
    from apps_lic.engines.channel_length_enforcer import ChannelLengthEnforcer
    e = ChannelLengthEnforcer()
    assert e.resolve_ceiling("email", "CTO", "cold") == 100
    assert e.resolve_ceiling("email", "VP_ENG", "cold") == 100


# ===========================================================================
# SE-P0c — ScopeCalibratedAskEngine
# ===========================================================================

def test_ask_engine_module_exists():
    """SE-P0c: scope_calibrated_ask_engine.py must exist."""
    assert (REPO_ROOT / "apps_lic" / "engines" / "scope_calibrated_ask_engine.py").exists()


def test_ask_engine_exec_cold_low_friction():
    """SE-P0c: EXECUTIVE+cold → ask_friction_score < 0.5 (low friction)."""
    from apps_lic.engines.scope_calibrated_ask_engine import ScopeCalibratedAskEngine
    e = ScopeCalibratedAskEngine()
    result = e.calibrate(
        recipient_class="EXECUTIVE",
        outreach_mode="cold",
        channel="email",
        relationship_distance="cold",
        hiring_posture="unknown",
    )
    assert result.ask_friction_score < 0.5
    assert result.is_bound_fail is False


def test_ask_engine_exec_cold_reciprocity_first():
    """SE-P0c: EXECUTIVE+cold → reciprocity_first=True."""
    from apps_lic.engines.scope_calibrated_ask_engine import ScopeCalibratedAskEngine
    e = ScopeCalibratedAskEngine()
    result = e.calibrate(
        recipient_class="EXECUTIVE",
        outreach_mode="cold",
        channel="email",
        relationship_distance="cold",
        hiring_posture="unknown",
    )
    assert result.reciprocity_first is True


def test_ask_engine_recruiter_direct_cta_style():
    """SE-P0c: RECRUITER+cold → cta_style=direct_concise (or equiv); no bound fail."""
    from apps_lic.engines.scope_calibrated_ask_engine import (
        ScopeCalibratedAskEngine, CTA_STYLE_DIRECT_CONCISE
    )
    e = ScopeCalibratedAskEngine()
    result = e.calibrate(
        recipient_class="RECRUITER",
        outreach_mode="cold",
        channel="email",
        relationship_distance="cold",
        hiring_posture="unknown",
    )
    assert result.cta_style == CTA_STYLE_DIRECT_CONCISE
    assert result.is_bound_fail is False


def test_ask_engine_referral_forwardable():
    """SE-P0c: referral mode → cta_style=forwardable_light."""
    from apps_lic.engines.scope_calibrated_ask_engine import (
        ScopeCalibratedAskEngine, CTA_STYLE_FORWARDABLE
    )
    e = ScopeCalibratedAskEngine()
    result = e.calibrate(
        recipient_class="REFERRAL_CONTACT",
        outreach_mode="referral",
        channel="email",
        relationship_distance="referral",
        hiring_posture="unknown",
    )
    assert result.cta_style == CTA_STYLE_FORWARDABLE


def test_ask_engine_followup_light_nudge():
    """SE-P0c: followup mode → cta_style=light_nudge."""
    from apps_lic.engines.scope_calibrated_ask_engine import (
        ScopeCalibratedAskEngine, CTA_STYLE_LIGHT_NUDGE
    )
    e = ScopeCalibratedAskEngine()
    result = e.calibrate(
        recipient_class="RECRUITER",
        outreach_mode="followup",
        channel="email",
        relationship_distance="warm",
        hiring_posture="unknown",
    )
    assert result.cta_style == CTA_STYLE_LIGHT_NUDGE


def test_ask_engine_actively_hiring_lowers_friction():
    """SE-P0c: actively_hiring posture reduces ask_friction_score."""
    from apps_lic.engines.scope_calibrated_ask_engine import ScopeCalibratedAskEngine
    e = ScopeCalibratedAskEngine()
    cold = e.calibrate(
        recipient_class="HIRING_MANAGER",
        outreach_mode="cold",
        channel="email",
        relationship_distance="cold",
        hiring_posture="cold",
    )
    hiring = e.calibrate(
        recipient_class="HIRING_MANAGER",
        outreach_mode="cold",
        channel="email",
        relationship_distance="cold",
        hiring_posture="actively_hiring",
    )
    assert hiring.ask_friction_score < cold.ask_friction_score


def test_ask_engine_friction_score_in_range():
    """SE-P0c: ask_friction_score must be 0.0–1.0 for all inputs."""
    from apps_lic.engines.scope_calibrated_ask_engine import ScopeCalibratedAskEngine
    e = ScopeCalibratedAskEngine()
    combos = [
        ("EXECUTIVE", "cold", "email", "cold", "unknown"),
        ("RECRUITER", "warm", "linkedin", "warm", "actively_hiring"),
        ("C_LEVEL", "referral", "email", "referral", "warm"),
        ("HIRING_MANAGER", "followup", "email", "known", "cold"),
    ]
    for rc, mode, ch, rd, hp in combos:
        r = e.calibrate(recipient_class=rc, outreach_mode=mode, channel=ch,
                        relationship_distance=rd, hiring_posture=hp)
        assert 0.0 <= r.ask_friction_score <= 1.0, (
            f"ask_friction_score={r.ask_friction_score} out of range for {rc}/{mode}"
        )


def test_ask_engine_override_suppresses_bound_fail():
    """SE-P0c: override_high_friction=True suppresses is_bound_fail even if score>0.5."""
    from apps_lic.engines.scope_calibrated_ask_engine import ScopeCalibratedAskEngine
    e = ScopeCalibratedAskEngine()
    # Force high friction by using unusual combo
    result = e.calibrate(
        recipient_class="EXECUTIVE",
        outreach_mode="cold",
        channel="email",
        relationship_distance="cold",
        hiring_posture="cold",
        override_high_friction=True,
    )
    assert result.override_configured is True
    assert result.is_bound_fail is False  # suppressed


def test_ask_engine_evidence_ref_populated():
    """SE-P0c: evidence_ref must contain key fields."""
    from apps_lic.engines.scope_calibrated_ask_engine import ScopeCalibratedAskEngine
    e = ScopeCalibratedAskEngine()
    result = e.calibrate(
        recipient_class="EXECUTIVE",
        outreach_mode="cold",
        channel="email",
        relationship_distance="cold",
        hiring_posture="unknown",
    )
    assert "ask_friction_score=" in result.evidence_ref
    assert "recipient_class=EXECUTIVE" in result.evidence_ref
    assert "cta_style=" in result.evidence_ref


def test_ask_engine_no_provider_imports():
    """SE-P0c: scope_calibrated_ask_engine.py must not import providers."""
    src = (REPO_ROOT / "apps_lic" / "engines" / "scope_calibrated_ask_engine.py").read_text(encoding="utf-8")
    for forbidden in ("openai", "anthropic", "boto3", "google.generativeai"):
        assert forbidden not in src


def test_ask_engine_recommended_cta_not_forbidden():
    """SE-P0c: recommended_cta must not contain forbidden patterns like 'discuss opportunities'."""
    from apps_lic.engines.scope_calibrated_ask_engine import (
        ScopeCalibratedAskEngine, FORBIDDEN_CTA_PATTERNS
    )
    e = ScopeCalibratedAskEngine()
    for rc in ("EXECUTIVE", "RECRUITER", "HIRING_MANAGER", "REFERRAL_CONTACT"):
        for mode in ("cold", "warm", "referral", "followup"):
            result = e.calibrate(
                recipient_class=rc, outreach_mode=mode,
                channel="email", relationship_distance="cold",
                hiring_posture="unknown",
            )
            for forbidden in FORBIDDEN_CTA_PATTERNS:
                assert forbidden not in result.recommended_cta.lower(), (
                    f"Forbidden CTA pattern {forbidden!r} found for {rc}/{mode}"
                )


# ===========================================================================
# SE-P1a — RecipientTriggerEngine
# ===========================================================================

def test_trigger_engine_module_exists():
    """SE-P1a: recipient_trigger_engine.py must exist."""
    assert (REPO_ROOT / "apps_lic" / "engines" / "recipient_trigger_engine.py").exists()


def test_trigger_engine_exec_cold_satisfied_with_person_level_trigger():
    """SE-P1a: EXECUTIVE+cold satisfied when ≥1 person_level trigger provided."""
    from apps_lic.engines.recipient_trigger_engine import (
        RecipientTriggerEngine, RecipientTrigger
    )
    e = RecipientTriggerEngine()
    result = e.evaluate(
        triggers=[RecipientTrigger(
            trigger_type="person_level",
            description="Recent KubeCon talk",
            source_ref="sha256:abc",
            confidence=0.9,
        )],
        recipient_class="EXECUTIVE",
        outreach_mode="cold",
    )
    assert result.is_satisfied is True
    assert result.is_fail_closed is False
    assert result.hitl_required is False


def test_trigger_engine_exec_cold_satisfied_with_company_strategy_trigger():
    """SE-P1a: EXECUTIVE+cold satisfied with company_strategy trigger."""
    from apps_lic.engines.recipient_trigger_engine import (
        RecipientTriggerEngine, RecipientTrigger
    )
    e = RecipientTriggerEngine()
    result = e.evaluate(
        triggers=[RecipientTrigger(
            trigger_type="company_strategy",
            description="Series B announcement",
            source_ref="sha256:def",
            confidence=0.8,
        )],
        recipient_class="EXECUTIVE",
        outreach_mode="cold",
    )
    assert result.is_satisfied is True
    assert result.recommended_personalization_mode == "company"


def test_trigger_engine_exec_cold_unsatisfied_no_triggers_omit_policy():
    """SE-P1a: EXECUTIVE+cold with no triggers + omit_unsupported → not satisfied, no hard-fail."""
    from apps_lic.engines.recipient_trigger_engine import RecipientTriggerEngine
    e = RecipientTriggerEngine()
    result = e.evaluate(
        triggers=[],
        recipient_class="EXECUTIVE",
        outreach_mode="cold",
        omission_policy="omit_unsupported",
    )
    assert result.is_satisfied is False
    assert result.is_fail_closed is False
    assert result.hitl_required is False


def test_trigger_engine_exec_cold_unsatisfied_fail_closed():
    """SE-P1a: EXECUTIVE+cold + fail_closed policy → is_fail_closed=True."""
    from apps_lic.engines.recipient_trigger_engine import RecipientTriggerEngine
    e = RecipientTriggerEngine()
    result = e.evaluate(
        triggers=[],
        recipient_class="EXECUTIVE",
        outreach_mode="cold",
        omission_policy="fail_closed",
    )
    assert result.is_fail_closed is True


def test_trigger_engine_exec_cold_unsatisfied_hitl_policy():
    """SE-P1a: EXECUTIVE+cold + hitl_required policy → hitl_required=True."""
    from apps_lic.engines.recipient_trigger_engine import RecipientTriggerEngine
    e = RecipientTriggerEngine()
    result = e.evaluate(
        triggers=[],
        recipient_class="EXECUTIVE",
        outreach_mode="cold",
        omission_policy="hitl_required",
    )
    assert result.hitl_required is True
    assert result.is_fail_closed is False


def test_trigger_engine_recruiter_satisfied_without_person_level():
    """SE-P1a: RECRUITER+cold satisfied even without person_level trigger."""
    from apps_lic.engines.recipient_trigger_engine import RecipientTriggerEngine
    e = RecipientTriggerEngine()
    result = e.evaluate(
        triggers=[],
        recipient_class="RECRUITER",
        outreach_mode="cold",
        omission_policy="fail_closed",  # even strict policy — recruiter doesn't need triggers
    )
    assert result.is_satisfied is True
    assert result.is_fail_closed is False


def test_trigger_engine_recruiter_any_trigger_accepted():
    """SE-P1a: RECRUITER accepts role_context trigger (not person_level)."""
    from apps_lic.engines.recipient_trigger_engine import (
        RecipientTriggerEngine, RecipientTrigger
    )
    e = RecipientTriggerEngine()
    result = e.evaluate(
        triggers=[RecipientTrigger(
            trigger_type="role_context",
            description="Backend engineer JD posted",
            source_ref="sha256:xyz",
            confidence=0.85,
        )],
        recipient_class="RECRUITER",
        outreach_mode="cold",
    )
    assert result.is_satisfied is True
    assert result.recommended_personalization_mode == "company"


def test_trigger_engine_unverified_trigger_downgraded():
    """SE-P1a: trigger with empty source_ref is downgraded, not used."""
    from apps_lic.engines.recipient_trigger_engine import (
        RecipientTriggerEngine, RecipientTrigger
    )
    e = RecipientTriggerEngine()
    result = e.evaluate(
        triggers=[RecipientTrigger(
            trigger_type="person_level",
            description="Scraped talk title",
            source_ref="",          # no source_ref → downgraded
            confidence=0.9,
        )],
        recipient_class="EXECUTIVE",
        outreach_mode="cold",
        omission_policy="omit_unsupported",
    )
    # The trigger is downgraded, so exec cold is not satisfied
    assert result.is_satisfied is False
    # All decisions should be "downgrade" for this trigger
    assert any(d.verdict == "downgrade" for d in result.trigger_decisions)


def test_trigger_engine_low_confidence_trigger_omitted():
    """SE-P1a: trigger with confidence < 0.3 is omitted (not counted)."""
    from apps_lic.engines.recipient_trigger_engine import (
        RecipientTriggerEngine, RecipientTrigger
    )
    e = RecipientTriggerEngine()
    result = e.evaluate(
        triggers=[RecipientTrigger(
            trigger_type="person_level",
            description="Weak signal",
            source_ref="sha256:abc",
            confidence=0.1,         # below 0.3 threshold
        )],
        recipient_class="EXECUTIVE",
        outreach_mode="cold",
        omission_policy="omit_unsupported",
    )
    assert result.is_satisfied is False
    assert any(d.verdict == "omit" for d in result.trigger_decisions)


def test_trigger_engine_followup_always_satisfied():
    """SE-P1a: followup mode never requires triggers."""
    from apps_lic.engines.recipient_trigger_engine import RecipientTriggerEngine
    e = RecipientTriggerEngine()
    result = e.evaluate(
        triggers=[],
        recipient_class="EXECUTIVE",
        outreach_mode="followup",
        omission_policy="fail_closed",
    )
    assert result.is_satisfied is True
    assert result.is_fail_closed is False


def test_trigger_engine_referral_satisfied_with_relationship_trigger():
    """SE-P1a: REFERRAL_CONTACT+referral satisfied with relationship_context trigger."""
    from apps_lic.engines.recipient_trigger_engine import (
        RecipientTriggerEngine, RecipientTrigger
    )
    e = RecipientTriggerEngine()
    result = e.evaluate(
        triggers=[RecipientTrigger(
            trigger_type="relationship_context",
            description="Worked together at Acme",
            source_ref="sha256:rel",
            confidence=1.0,
        )],
        recipient_class="REFERRAL_CONTACT",
        outreach_mode="referral",
    )
    assert result.is_satisfied is True
    assert result.recommended_personalization_mode == "relationship"


def test_trigger_engine_evidence_ref_populated():
    """SE-P1a: evidence_ref must contain key fields."""
    from apps_lic.engines.recipient_trigger_engine import (
        RecipientTriggerEngine, RecipientTrigger
    )
    e = RecipientTriggerEngine()
    result = e.evaluate(
        triggers=[RecipientTrigger("person_level", "talk", "sha256:x", 0.9)],
        recipient_class="EXECUTIVE",
        outreach_mode="cold",
    )
    ref = result.evidence_ref
    assert "recipient_class=EXECUTIVE" in ref
    assert "outreach_mode=cold" in ref
    assert "is_satisfied=" in ref
    assert "recommended_mode=" in ref


def test_trigger_engine_does_not_invent_triggers():
    """SE-P1a: engine produces zero use-verdicts when zero triggers supplied."""
    from apps_lic.engines.recipient_trigger_engine import RecipientTriggerEngine
    e = RecipientTriggerEngine()
    result = e.evaluate(
        triggers=[],
        recipient_class="EXECUTIVE",
        outreach_mode="cold",
    )
    used = [d for d in result.trigger_decisions if d.verdict == "use"]
    assert len(used) == 0, "Engine must not invent triggers — no use-verdicts from empty input"


def test_trigger_engine_no_provider_imports():
    """SE-P1a: recipient_trigger_engine.py must not import providers."""
    src = (REPO_ROOT / "apps_lic" / "engines" / "recipient_trigger_engine.py").read_text(encoding="utf-8")
    for forbidden in ("openai", "anthropic", "boto3", "google.generativeai"):
        assert forbidden not in src


def test_trigger_engine_unknown_trigger_type_omitted():
    """SE-P1a: trigger with unknown type gets verdict=omit and a warning."""
    from apps_lic.engines.recipient_trigger_engine import (
        RecipientTriggerEngine, RecipientTrigger
    )
    e = RecipientTriggerEngine()
    result = e.evaluate(
        triggers=[RecipientTrigger(
            trigger_type="made_up_type",
            description="some trigger",
            source_ref="sha256:abc",
            confidence=0.9,
        )],
        recipient_class="RECRUITER",
        outreach_mode="cold",
    )
    assert any(d.verdict == "omit" for d in result.trigger_decisions)
    assert any("made_up_type" in w for w in result.warnings)


def test_trigger_engine_hiring_manager_cold_needs_company_or_role():
    """SE-P1a: HIRING_MANAGER+cold satisfied with role_context trigger."""
    from apps_lic.engines.recipient_trigger_engine import (
        RecipientTriggerEngine, RecipientTrigger
    )
    e = RecipientTriggerEngine()
    result = e.evaluate(
        triggers=[RecipientTrigger(
            trigger_type="role_context",
            description="Backend JD posted 2 weeks ago",
            source_ref="sha256:jd",
            confidence=0.95,
        )],
        recipient_class="HIRING_MANAGER",
        outreach_mode="cold",
    )
    assert result.is_satisfied is True


def test_trigger_engine_hiring_manager_cold_no_triggers_fail_closed():
    """SE-P1a: HIRING_MANAGER+cold + fail_closed + no triggers → is_fail_closed=True."""
    from apps_lic.engines.recipient_trigger_engine import RecipientTriggerEngine
    e = RecipientTriggerEngine()
    result = e.evaluate(
        triggers=[],
        recipient_class="HIRING_MANAGER",
        outreach_mode="cold",
        omission_policy="fail_closed",
    )
    assert result.is_fail_closed is True
