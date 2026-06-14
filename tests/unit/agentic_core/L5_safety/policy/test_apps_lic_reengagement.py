"""Unit tests for agentic_core.L5_safety.policy.apps_lic_reengagement.

Wave 6.1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — untested P2 L5 surface.
Defines the HITL re-engagement policy schema: four string-enums (HITLTrigger,
HITLReviewType, HITLResolution, HITLUrgency), the frozen HITLPolicyRule, the
ReengagementHITLPolicy with auto-populated default rules + to_dict/from_dict
round-trip, the HITLReviewRequest/Result records, and the HITLPolicyRegistry
class-level cache. Covers enum member sets, dataclass defaults/frozen, the
__post_init__ default-rule population, serialization round-trip, and registry
get/register/get_or_default behaviour.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.L5_safety.policy.apps_lic_reengagement import (
    HITLPolicyRegistry,
    HITLPolicyRule,
    HITLResolution,
    HITLReviewRequest,
    HITLReviewResult,
    HITLReviewType,
    HITLTrigger,
    HITLUrgency,
    ReengagementHITLPolicy,
)


class TestEnums:
    def test_trigger_members(self) -> None:
        assert {t.value for t in HITLTrigger} == {
            "first_touch", "reengagement_sequence", "high_sequence_number",
            "high_confidence_signal", "signal_type_sensitive", "signal_conflict",
            "executive_recipient", "prior_negative_reply", "prior_opt_out_attempt",
            "tone_calibration_fail", "high_risk_content", "compound_risk",
            "manual_review_flag",
        }

    def test_review_type_members(self) -> None:
        assert {r.value for r in HITLReviewType} == {
            "pre_send", "post_send", "real_time", "batch_review",
        }

    def test_resolution_members(self) -> None:
        assert {r.value for r in HITLResolution} == {
            "approved", "approved_with_edits", "rejected", "deferred", "escalated",
        }

    def test_urgency_members(self) -> None:
        assert {u.value for u in HITLUrgency} == {
            "critical", "high", "normal", "low",
        }

    @pytest.mark.parametrize("enum_cls", [HITLTrigger, HITLReviewType, HITLResolution, HITLUrgency])
    def test_enums_are_str_enums(self, enum_cls: type) -> None:
        member = next(iter(enum_cls))
        assert isinstance(member, str)


class TestHITLPolicyRule:
    def test_defaults(self) -> None:
        rule = HITLPolicyRule(
            rule_id="R1",
            trigger=HITLTrigger.FIRST_TOUCH,
            review_type=HITLReviewType.PRE_SEND,
            urgency=HITLUrgency.NORMAL,
        )
        assert rule.conditions == {}
        assert rule.rationale == ""
        assert rule.enabled is True

    def test_frozen(self) -> None:
        rule = HITLPolicyRule(
            rule_id="R1",
            trigger=HITLTrigger.FIRST_TOUCH,
            review_type=HITLReviewType.PRE_SEND,
            urgency=HITLUrgency.NORMAL,
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            rule.enabled = False  # type: ignore[misc]


class TestReengagementHITLPolicy:
    def test_default_identity_fields(self) -> None:
        policy = ReengagementHITLPolicy()
        assert policy.policy_id == "apps_lic.reengagement"
        assert policy.version == "1.0.0"
        assert policy.enabled is True
        assert policy.default_urgency == HITLUrgency.NORMAL
        assert policy.compound_risk_threshold == 2

    def test_empty_rules_autopopulate_defaults(self) -> None:
        policy = ReengagementHITLPolicy()
        assert len(policy.rules) == 6
        assert {r.rule_id for r in policy.rules} == {"R001", "R002", "R003", "R004", "R005", "R006"}

    def test_default_rules_are_policy_rules(self) -> None:
        policy = ReengagementHITLPolicy()
        assert all(isinstance(r, HITLPolicyRule) for r in policy.rules)

    def test_explicit_rules_preserved(self) -> None:
        custom = [
            HITLPolicyRule(
                rule_id="CUSTOM",
                trigger=HITLTrigger.MANUAL_REVIEW_FLAG,
                review_type=HITLReviewType.REAL_TIME,
                urgency=HITLUrgency.CRITICAL,
            )
        ]
        policy = ReengagementHITLPolicy(rules=custom)
        assert [r.rule_id for r in policy.rules] == ["CUSTOM"]

    def test_frozen(self) -> None:
        policy = ReengagementHITLPolicy()
        with pytest.raises(dataclasses.FrozenInstanceError):
            policy.version = "2.0.0"  # type: ignore[misc]

    def test_to_dict_shape(self) -> None:
        policy = ReengagementHITLPolicy()
        d = policy.to_dict()
        assert d["policy_id"] == "apps_lic.reengagement"
        assert d["default_urgency"] == "normal"
        assert isinstance(d["rules"], list)
        first = d["rules"][0]
        assert set(first) == {
            "rule_id", "trigger", "review_type", "urgency",
            "conditions", "rationale", "enabled",
        }
        # Enums serialized to their string values.
        assert first["trigger"] == "high_sequence_number"
        assert first["urgency"] == "high"

    def test_round_trip_dict(self) -> None:
        original = ReengagementHITLPolicy()
        restored = ReengagementHITLPolicy.from_dict(original.to_dict())
        assert restored.policy_id == original.policy_id
        assert restored.version == original.version
        assert restored.default_urgency == original.default_urgency
        assert restored.compound_risk_threshold == original.compound_risk_threshold
        assert [r.rule_id for r in restored.rules] == [r.rule_id for r in original.rules]

    def test_from_dict_reconstructs_enum_fields(self) -> None:
        policy = ReengagementHITLPolicy.from_dict(ReengagementHITLPolicy().to_dict())
        first = policy.rules[0]
        assert isinstance(first.trigger, HITLTrigger)
        assert isinstance(first.review_type, HITLReviewType)
        assert isinstance(first.urgency, HITLUrgency)

    def test_from_dict_minimal_payload_uses_defaults(self) -> None:
        # No rules in payload → from_dict produces empty list → __post_init__
        # re-populates the defaults.
        policy = ReengagementHITLPolicy.from_dict({})
        assert policy.policy_id == "apps_lic.reengagement"
        assert len(policy.rules) == 6


class TestReviewRecords:
    def test_review_request_defaults_and_timestamp(self) -> None:
        req = HITLReviewRequest(
            review_id="rev-1",
            touch_id="touch-1",
            recipient_hash="hash-1",
            campaign_id="camp-1",
            triggered_rules=["R001"],
            review_type=HITLReviewType.PRE_SEND,
            urgency=HITLUrgency.HIGH,
        )
        assert req.context == {}
        # Auto-generated ISO-8601 UTC timestamp.
        assert req.created_at.endswith("+00:00")

    def test_review_result_defaults(self) -> None:
        result = HITLReviewResult(
            review_id="rev-1",
            touch_id="touch-1",
            resolution=HITLResolution.APPROVED,
            resolved_by="reviewer-1",
            resolved_at="2026-01-01T00:00:00+00:00",
        )
        assert result.notes == ""
        assert result.modifications == {}

    def test_review_result_frozen(self) -> None:
        result = HITLReviewResult(
            review_id="rev-1",
            touch_id="touch-1",
            resolution=HITLResolution.REJECTED,
            resolved_by="r",
            resolved_at="t",
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            result.notes = "x"  # type: ignore[misc]


class TestHITLPolicyRegistry:
    def setup_method(self) -> None:
        # Isolate the class-level cache between tests.
        HITLPolicyRegistry._policies.clear()

    def teardown_method(self) -> None:
        HITLPolicyRegistry._policies.clear()

    def test_register_and_get(self) -> None:
        policy = ReengagementHITLPolicy()
        HITLPolicyRegistry.register(policy)
        assert HITLPolicyRegistry.get("apps_lic.reengagement") is policy

    def test_get_missing_returns_none(self) -> None:
        assert HITLPolicyRegistry.get("does.not.exist") is None

    def test_get_or_default_registers_apps_lic_default(self) -> None:
        result = HITLPolicyRegistry.get_or_default("apps_lic.reengagement")
        assert isinstance(result, ReengagementHITLPolicy)
        # The default was cached on first lookup.
        assert HITLPolicyRegistry.get("apps_lic.reengagement") is result

    def test_get_or_default_unknown_id_returns_fresh_default(self) -> None:
        result = HITLPolicyRegistry.get_or_default("other.policy")
        assert isinstance(result, ReengagementHITLPolicy)
        # Unknown id is NOT cached (only the apps_lic id is auto-registered).
        assert HITLPolicyRegistry.get("other.policy") is None
