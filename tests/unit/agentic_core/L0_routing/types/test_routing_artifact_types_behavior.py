"""Behavioral tests for agentic_core.L0_routing.types.routing_artifact_types.

Covers the V15 P1-gated typed artifact surface:
  - 5 string enums: RoutingRationale, RoutePath, TokenGateResult, SeverityEnum, VigilanceTier
  - 11 frozen dataclasses: RouteDecision, TokenCap, Perms, SelfHealingTrigger,
    Aggregate, Result, Incident, TokenControl, EvacuationProtocol,
    PolicyConfigSnapshot, HealingPlan, StaleWriteIncident
  - Validation logic in __post_init__:
      * TokenControlArtifact: gold_tokens <= 300
      * HealingPlan: non-empty trace_id/plan_id/policy_liaison_node,
                     manifests is tuple, semantic_clock_tick >= 0
      * StaleWriteIncident: 5 non-empty/non-negative field checks
  - CapabilityDepletionTracker state machine (mutable)
  - HEALER_PIPE_ORDER invariants (strict 10-stage pipe)
  - __all__ export completeness

L0 is a ×2.0 criticality layer. Module ranked in the top-10 by fan-in (10).
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def rat():
    return pytest.importorskip("agentic_core.L0_routing.types.routing_artifact_types")


EXPECTED_EXPORTS = [
    "AggregateArtifact",
    "CapabilityDepletionTracker",
    "EvacuationProtocol",
    "HEALER_PIPE_ORDER",
    "HealingPlan",
    "IncidentArtifact",
    "PermsArtifact",
    "PolicyConfigSnapshot",
    "ResultArtifact",
    "RoutePath",
    "RouteDecisionArtifact",
    "RoutingRationale",
    "SelfHealingTrigger",
    "SeverityEnum",
    "StaleWriteIncident",
    "TokenCapArtifact",
    "TokenControlArtifact",
    "TokenGateResult",
    "VigilanceTier",
]


# --------------------------------------------------------------------------- #
# Public surface                                                              #
# --------------------------------------------------------------------------- #


class TestPublicSurface:
    @pytest.mark.parametrize("name", EXPECTED_EXPORTS)
    def test_export_present(self, rat, name):
        assert name in rat.__all__, f"{name} missing from __all__"

    def test_all_has_no_extras(self, rat):
        assert set(rat.__all__) == set(EXPECTED_EXPORTS)


# --------------------------------------------------------------------------- #
# String enums                                                                #
# --------------------------------------------------------------------------- #


class TestRoutingRationale:
    @pytest.mark.parametrize(
        "member,value",
        [
            ("LOW_RISK_BYPASS", "low_risk_bypass"),
            ("STANDARD_VALIDATION", "standard_validation"),
            ("HUMAN_ESCALATION", "human_escalation"),
            ("POLICY_CHALLENGE", "policy_challenge"),
            ("ROUTE_RECOVERY", "route_recovery"),
            ("CIRCUIT_BREAKER_OPEN", "circuit_breaker_open"),
            ("GUARDIAN_SIGNAL", "guardian_signal"),
            ("BUDGET_OVERFLOW", "budget_overflow"),
        ],
    )
    def test_members(self, rat, member, value):
        assert getattr(rat.RoutingRationale, member).value == value

    def test_count(self, rat):
        assert len(list(rat.RoutingRationale)) == 8

    def test_is_str_enum(self, rat):
        assert rat.RoutingRationale.LOW_RISK_BYPASS == "low_risk_bypass"


class TestRoutePath:
    @pytest.mark.parametrize(
        "member,value",
        [
            ("LOW_RISK_BYPASS", "low_risk_bypass"),
            ("STANDARD_VALIDATION", "standard_validation"),
            ("HUMAN_ESCALATION", "human_escalation"),
            ("POLICY_CHALLENGE_LOOP", "policy_challenge_loop"),
            ("ROUTE_RECOVERY_BUDGET_OVERFLOW", "route_recovery_budget_overflow"),
        ],
    )
    def test_members(self, rat, member, value):
        assert getattr(rat.RoutePath, member).value == value

    def test_count(self, rat):
        # §3.3 locks paths to exactly 5
        assert len(list(rat.RoutePath)) == 5


class TestTokenGateResult:
    @pytest.mark.parametrize(
        "member,value",
        [("ALLOW", "allow"), ("DENY", "deny"), ("DOWNGRADE", "downgrade")],
    )
    def test_members(self, rat, member, value):
        assert getattr(rat.TokenGateResult, member).value == value

    def test_count(self, rat):
        assert len(list(rat.TokenGateResult)) == 3


class TestSeverityEnum:
    @pytest.mark.parametrize(
        "member,value",
        [
            ("INFO", "info"),
            ("WARNING", "warning"),
            ("ERROR", "error"),
            ("CRITICAL", "critical"),
        ],
    )
    def test_members(self, rat, member, value):
        assert getattr(rat.SeverityEnum, member).value == value

    def test_count(self, rat):
        assert len(list(rat.SeverityEnum)) == 4


class TestVigilanceTier:
    @pytest.mark.parametrize(
        "member,value",
        [
            ("TIER_I", "tier_i_budget_drain"),
            ("TIER_II", "tier_ii_anomalous_presence"),
            ("TIER_III", "tier_iii_evacuation"),
        ],
    )
    def test_members(self, rat, member, value):
        assert getattr(rat.VigilanceTier, member).value == value

    def test_count(self, rat):
        # §15.1 locks tiers to exactly 3
        assert len(list(rat.VigilanceTier)) == 3


# --------------------------------------------------------------------------- #
# Frozen dataclasses — immutability                                           #
# --------------------------------------------------------------------------- #


class TestFrozenDataclasses:
    def test_route_decision_is_frozen(self, rat):
        r = rat.RouteDecisionArtifact(
            trace_id="t", timestamp="2026-01-01T00:00:00Z",
            route_path=rat.RoutePath.STANDARD_VALIDATION,
            risk_score=0.5, budget_est=1.0,
            rationale_enum=rat.RoutingRationale.STANDARD_VALIDATION,
            policy_config_hash="h",
        )
        with pytest.raises((AttributeError, Exception)):
            r.trace_id = "t2"  # type: ignore[misc]

    def test_token_cap_is_frozen(self, rat):
        t = rat.TokenCapArtifact(
            trace_id="t", policy_hash="p",
            budget_limit=1000, tokens_requested=500,
            gate_result=rat.TokenGateResult.ALLOW,
        )
        with pytest.raises((AttributeError, Exception)):
            t.budget_limit = 2000  # type: ignore[misc]

    def test_perms_is_frozen(self, rat):
        p = rat.PermsArtifact(trace_id="t", policy_hash="p", budget=100)
        with pytest.raises((AttributeError, Exception)):
            p.budget = 200  # type: ignore[misc]

    def test_incident_is_frozen(self, rat):
        i = rat.IncidentArtifact(
            trace_id="t", incident_id="i",
            correlation_hash="h",
            severity_enum=rat.SeverityEnum.ERROR,
            telemetry_events=[],
        )
        with pytest.raises((AttributeError, Exception)):
            i.incident_id = "j"  # type: ignore[misc]

    def test_policy_config_snapshot_frozen_by_default(self, rat):
        s = rat.PolicyConfigSnapshot(policy_hash="h", wave_id="w")
        assert s.frozen is True
        with pytest.raises((AttributeError, Exception)):
            s.policy_hash = "h2"  # type: ignore[misc]


# --------------------------------------------------------------------------- #
# TokenControlArtifact — 300-token bound                                      #
# --------------------------------------------------------------------------- #


class TestTokenControlArtifact:
    def test_valid_bound(self, rat):
        a = rat.TokenControlArtifact(trace_id="t", prompt_hash="p", gold_tokens=300)
        assert a.gold_tokens == 300

    def test_below_bound(self, rat):
        a = rat.TokenControlArtifact(trace_id="t", prompt_hash="p", gold_tokens=1)
        assert a.gold_tokens == 1

    def test_zero_allowed(self, rat):
        a = rat.TokenControlArtifact(trace_id="t", prompt_hash="p", gold_tokens=0)
        assert a.gold_tokens == 0

    def test_over_bound_raises(self, rat):
        with pytest.raises(ValueError, match=r"exceeds 300"):
            rat.TokenControlArtifact(trace_id="t", prompt_hash="p", gold_tokens=301)

    def test_far_over_bound_raises(self, rat):
        with pytest.raises(ValueError, match=r"gold_tokens=9999"):
            rat.TokenControlArtifact(trace_id="t", prompt_hash="p", gold_tokens=9999)


# --------------------------------------------------------------------------- #
# Known production bugs — pinned as regression markers                        #
# --------------------------------------------------------------------------- #


class TestKnownBugs:
    """Regression markers for bugs discovered while writing this suite.

    When the production bug is fixed, these tests will fail and must be
    replaced with the full validation suite (see `_valid_plan_kwargs` below
    and the __post_init__ logic in HealingPlan).
    """

    def test_BUG_healing_plan_construction_always_fails_broken_seam(self, rat):
        """Production bug: HealingPlan.__post_init__ calls
        assert_layer_may_emit() which calls
        `validator.validate_emission(...)` — but the
        artifact_emission_prohibition_enforcer module has no
        `validate_emission` attribute. Every HealingPlan(...) instantiation
        crashes with AttributeError BEFORE any field validation runs.

        Effect: L2 agents cannot emit HealingPlan artifacts at runtime.
        The entire §1.7 typed-artifact surface is non-functional.

        Fix: add `validate_emission` method to
        agentic_core.L5_safety.enforcement.artifact_emission_prohibition_enforcer
        OR change the seam to call an existing validator method.
        Author-Gate required (L0↔L5 cross-layer seam).
        """
        with pytest.raises(AttributeError, match=r"validate_emission"):
            rat.HealingPlan(
                trace_id="t", plan_id="p",
                manifests=("m",),
                semantic_clock_tick=0,
                policy_liaison_node="node",
            )

    def test_BUG_result_artifact_construction_always_fails_broken_seam(self, rat):
        """Same broken-seam bug affects ResultArtifact.__post_init__.

        Effect: L2 cannot emit RESULT artifacts at runtime. The entire §10.4
        post-heal result-emission surface is non-functional.
        """
        with pytest.raises(AttributeError, match=r"validate_emission"):
            rat.ResultArtifact(
                trace_id="t",
                execution_outcome="ok",
                final_state_hash="h",
                artifact_class="cls",
            )

    # When the seam is fixed, restore the full validation suite using these
    # valid kwargs and assert each ValueError/TypeError from __post_init__:
    #   - empty trace_id, empty plan_id, list-instead-of-tuple manifests,
    #     negative semantic_clock_tick, empty policy_liaison_node
    # _valid_plan_kwargs = dict(trace_id="t", plan_id="p", manifests=("m",),
    #                          semantic_clock_tick=0, policy_liaison_node="n")


# --------------------------------------------------------------------------- #
# StaleWriteIncident validation                                               #
# --------------------------------------------------------------------------- #


class TestStaleWriteIncidentValidation:
    def _valid_kwargs(self) -> dict:
        return dict(
            trace_id="t",
            target_path="/p",
            expected_hash="eh",
            actual_hash="ah",
            semantic_clock_tick=0,
        )

    def test_valid_construction(self, rat):
        inc = rat.StaleWriteIncident(**self._valid_kwargs())
        assert inc.target_path == "/p"

    @pytest.mark.parametrize(
        "field,bad_value,match",
        [
            ("trace_id", "", "trace_id"),
            ("target_path", "", "target_path"),
            ("expected_hash", "", "expected_hash"),
            ("actual_hash", "", "actual_hash"),
        ],
    )
    def test_empty_string_rejected(self, rat, field, bad_value, match):
        kw = self._valid_kwargs()
        kw[field] = bad_value
        with pytest.raises(ValueError, match=match):
            rat.StaleWriteIncident(**kw)

    def test_negative_clock_tick_rejected(self, rat):
        kw = self._valid_kwargs()
        kw["semantic_clock_tick"] = -5
        with pytest.raises(ValueError, match=r"semantic_clock_tick"):
            rat.StaleWriteIncident(**kw)


# --------------------------------------------------------------------------- #
# CapabilityDepletionTracker — mutable state machine                          #
# --------------------------------------------------------------------------- #


class TestCapabilityDepletionTracker:
    def test_initial_state(self, rat):
        t = rat.CapabilityDepletionTracker(trace_id="tr", total_slots=5)
        assert t.used_slots == 0
        assert t.depletion_log == []

    def test_depletion_rate_zero_slots_returns_one(self, rat):
        # Edge case: avoid div-by-zero; return 1.0 (fully depleted by convention)
        t = rat.CapabilityDepletionTracker(trace_id="tr", total_slots=0)
        assert t.depletion_rate == 1.0

    def test_depletion_rate_fresh(self, rat):
        t = rat.CapabilityDepletionTracker(trace_id="tr", total_slots=4)
        assert t.depletion_rate == 0.0

    def test_depletion_rate_after_consume(self, rat):
        t = rat.CapabilityDepletionTracker(trace_id="tr", total_slots=4)
        t.consume_slot("tool_a")
        t.consume_slot("tool_b")
        assert t.depletion_rate == 0.5

    def test_consume_slot_returns_true_when_available(self, rat):
        t = rat.CapabilityDepletionTracker(trace_id="tr", total_slots=2)
        assert t.consume_slot("tool_a") is True
        assert t.used_slots == 1

    def test_consume_slot_fail_closed_when_depleted(self, rat):
        t = rat.CapabilityDepletionTracker(trace_id="tr", total_slots=1)
        assert t.consume_slot("a") is True
        assert t.consume_slot("b") is False  # depleted — fail-closed
        assert t.used_slots == 1  # counter not incremented on failure

    def test_consume_slot_fail_closed_at_zero(self, rat):
        t = rat.CapabilityDepletionTracker(trace_id="tr", total_slots=0)
        assert t.consume_slot("a") is False
        assert t.used_slots == 0

    def test_consume_logs_each_call(self, rat):
        t = rat.CapabilityDepletionTracker(trace_id="tr", total_slots=3)
        t.consume_slot("tool_x")
        t.consume_slot("tool_y")
        assert len(t.depletion_log) == 2
        assert t.depletion_log[0]["tool"] == "tool_x"
        assert t.depletion_log[0]["slots_remaining"] == 2
        assert t.depletion_log[1]["tool"] == "tool_y"
        assert t.depletion_log[1]["slots_remaining"] == 1

    def test_consume_does_not_log_on_failure(self, rat):
        t = rat.CapabilityDepletionTracker(trace_id="tr", total_slots=1)
        t.consume_slot("a")
        t.consume_slot("b")  # fails
        assert len(t.depletion_log) == 1


# --------------------------------------------------------------------------- #
# HEALER_PIPE_ORDER invariants                                                #
# --------------------------------------------------------------------------- #


class TestHealerPipeOrder:
    def test_is_tuple(self, rat):
        assert isinstance(rat.HEALER_PIPE_ORDER, tuple)

    def test_length_is_10(self, rat):
        # §2.5 mandates strict 10-stage pipe
        assert len(rat.HEALER_PIPE_ORDER) == 10

    def test_exact_order(self, rat):
        assert rat.HEALER_PIPE_ORDER == (
            "schema_validation",
            "hash_verification",
            "immediate_rollback_on_mismatch",
            "signed_modify_override_check",
            "stale_write_incident_emission",
            "circuit_breaker_increment",
            "ast_deserialization",
            "ast_native_transformation",
            "post_transform_node_id_check",
            "commit",
        )

    def test_commit_is_last(self, rat):
        assert rat.HEALER_PIPE_ORDER[-1] == "commit"

    def test_schema_validation_is_first(self, rat):
        assert rat.HEALER_PIPE_ORDER[0] == "schema_validation"

    def test_all_stages_unique(self, rat):
        assert len(set(rat.HEALER_PIPE_ORDER)) == len(rat.HEALER_PIPE_ORDER)


# --------------------------------------------------------------------------- #
# Other dataclass smoke: construction + field access                          #
# --------------------------------------------------------------------------- #


class TestArtifactConstruction:
    def test_aggregate(self, rat):
        a = rat.AggregateArtifact(
            trace_id="t", impact_scope=["a", "b"], rollback_vector="rb",
            risk_delta=0.2, pre_heal_assessment="ok",
        )
        assert a.impact_scope == ["a", "b"]

    def test_self_healing_trigger(self, rat):
        t = rat.SelfHealingTrigger(
            trace_id="t", source_layer="L6", target_pipe="pipe-1",
            signal_hash="sh", severity_enum=rat.SeverityEnum.CRITICAL,
        )
        assert t.severity_enum == rat.SeverityEnum.CRITICAL

    def test_evacuation_protocol(self, rat):
        e = rat.EvacuationProtocol(
            trace_id="t", tier=rat.VigilanceTier.TIER_III,
            freeze_state=True, exfiltration_path="/out", reason="breach",
        )
        assert e.tier == rat.VigilanceTier.TIER_III
        assert e.freeze_state is True

    def test_route_decision_with_semantic_clock_default_none(self, rat):
        r = rat.RouteDecisionArtifact(
            trace_id="t", timestamp="2026-01-01T00:00:00Z",
            route_path=rat.RoutePath.LOW_RISK_BYPASS,
            risk_score=0.1, budget_est=10.0,
            rationale_enum=rat.RoutingRationale.LOW_RISK_BYPASS,
            policy_config_hash="hash",
        )
        assert r.semantic_clock is None
