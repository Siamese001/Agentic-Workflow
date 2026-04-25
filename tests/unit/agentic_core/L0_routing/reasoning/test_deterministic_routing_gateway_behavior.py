"""Behavioral tests for agentic_core.L0_routing.reasoning.deterministic_routing_gateway.

Covers the runtime contract of the L0 routing determinism surface:
  - `_compute_replay_key` / `_compute_determinism_digest` pure functions
  - `RoutingArtifact` shape + `verify_replay` tamper-detection
  - `DeterministicRoutingGateway.stamp_decision` ledger + key emission
  - `ledger()` returns an isolated copy
  - `clear_ledger()` empties the ledger
  - `escalate_low_confidence_route` short-circuit on sufficient confidence
  - `get_routing_gateway` / `reset_routing_gateway` singleton semantics
  - `as_route_decision` with valid + invalid route_path strings

L0 is a ×2.0 criticality layer. Module ranked #1 (fan-in 14) in the Stage 1
risk-weighted gap report after the first two top-priority files were tested.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def drg():
    return pytest.importorskip("agentic_core.L0_routing.reasoning.deterministic_routing_gateway")


@pytest.fixture(scope="module")
def rat():
    return pytest.importorskip("agentic_core.L0_routing.types.routing_artifact_types")


@pytest.fixture
def fresh_gateway(drg):
    """Reset global singleton for test isolation."""
    drg.reset_routing_gateway()
    yield
    drg.reset_routing_gateway()


# --------------------------------------------------------------------------- #
# Pure helpers: _compute_replay_key, _compute_determinism_digest              #
# --------------------------------------------------------------------------- #


class TestComputeReplayKey:
    def test_returns_64_char_sha256_hex(self, drg):
        key = drg._compute_replay_key("route", "policy", "trace")
        assert len(key) == 64
        assert all(c in "0123456789abcdef" for c in key)

    def test_is_deterministic(self, drg):
        a = drg._compute_replay_key("route", "policy", "trace")
        b = drg._compute_replay_key("route", "policy", "trace")
        assert a == b

    def test_differs_on_route_change(self, drg):
        a = drg._compute_replay_key("route_a", "policy", "trace")
        b = drg._compute_replay_key("route_b", "policy", "trace")
        assert a != b

    def test_differs_on_policy_change(self, drg):
        a = drg._compute_replay_key("route", "pol_a", "trace")
        b = drg._compute_replay_key("route", "pol_b", "trace")
        assert a != b

    def test_differs_on_trace_change(self, drg):
        a = drg._compute_replay_key("route", "policy", "trace_a")
        b = drg._compute_replay_key("route", "policy", "trace_b")
        assert a != b


class TestComputeDeterminismDigest:
    def test_returns_32_char_prefix(self, drg):
        digest = drg._compute_determinism_digest("replay-key", 123.456)
        assert len(digest) == 32
        assert all(c in "0123456789abcdef" for c in digest)

    def test_is_deterministic(self, drg):
        a = drg._compute_determinism_digest("rk", 1.0)
        b = drg._compute_determinism_digest("rk", 1.0)
        assert a == b

    def test_timestamp_sensitive(self, drg):
        a = drg._compute_determinism_digest("rk", 1.0)
        b = drg._compute_determinism_digest("rk", 1.000001)
        assert a != b

    def test_replay_key_sensitive(self, drg):
        a = drg._compute_determinism_digest("rk_a", 1.0)
        b = drg._compute_determinism_digest("rk_b", 1.0)
        assert a != b


# --------------------------------------------------------------------------- #
# RoutingArtifact                                                             #
# --------------------------------------------------------------------------- #


def _mk_artifact(drg, **overrides):
    defaults = dict(
        trace_id="t-1",
        replay_key=drg._compute_replay_key("standard_validation", "policy-hash", "t-1"),
        determinism_digest="0" * 32,
        route_path="standard_validation",
        policy_config_hash="policy-hash",
        timestamp_monotonic=1000.0,
        metadata={},
    )
    defaults.update(overrides)
    return drg.RoutingArtifact(**defaults)


class TestRoutingArtifact:
    def test_is_frozen(self, drg):
        artifact = _mk_artifact(drg)
        with pytest.raises((AttributeError, Exception)):
            artifact.trace_id = "t-2"  # type: ignore[misc]

    def test_fields_exposed(self, drg):
        a = _mk_artifact(drg, route_path="human_escalation", metadata={"k": "v"})
        assert a.route_path == "human_escalation"
        assert a.metadata == {"k": "v"}
        assert a.policy_config_hash == "policy-hash"

    def test_as_route_decision_with_valid_route(self, drg, rat):
        a = _mk_artifact(drg, route_path="standard_validation")
        decision = a.as_route_decision(risk_score=0.2, budget_est=1.5)
        assert decision.route_path == rat.RoutePath.STANDARD_VALIDATION
        assert decision.risk_score == 0.2
        assert decision.budget_est == 1.5
        assert decision.policy_config_hash == "policy-hash"
        assert decision.trace_id == "t-1"

    def test_as_route_decision_with_invalid_route_falls_back(self, drg, rat):
        a = _mk_artifact(drg, route_path="not_a_real_route")
        decision = a.as_route_decision()
        # Invalid route_path triggers the STANDARD_VALIDATION fallback.
        assert decision.route_path == rat.RoutePath.STANDARD_VALIDATION

    @pytest.mark.parametrize(
        "route",
        [
            "low_risk_bypass",
            "standard_validation",
            "human_escalation",
            "policy_challenge_loop",
            "route_recovery_budget_overflow",
        ],
    )
    def test_as_route_decision_accepts_all_route_paths(self, drg, rat, route):
        a = _mk_artifact(drg, route_path=route)
        decision = a.as_route_decision()
        assert decision.route_path == rat.RoutePath(route)


# --------------------------------------------------------------------------- #
# DeterministicRoutingGateway.stamp_decision + ledger                         #
# --------------------------------------------------------------------------- #


class TestStampDecision:
    def test_returns_routing_artifact(self, drg):
        gw = drg.DeterministicRoutingGateway(policy_hash="pol")
        artifact = gw.stamp_decision("standard_validation")
        assert isinstance(artifact, drg.RoutingArtifact)

    def test_artifact_carries_inputs(self, drg):
        gw = drg.DeterministicRoutingGateway(policy_hash="pol-abc")
        artifact = gw.stamp_decision("low_risk_bypass", metadata={"scope": "tests"})
        assert artifact.route_path == "low_risk_bypass"
        assert artifact.policy_config_hash == "pol-abc"
        assert artifact.metadata == {"scope": "tests"}

    def test_artifact_has_keyed_fields(self, drg):
        gw = drg.DeterministicRoutingGateway(policy_hash="pol")
        artifact = gw.stamp_decision("standard_validation")
        assert artifact.replay_key  # non-empty
        assert artifact.determinism_digest  # non-empty
        assert isinstance(artifact.timestamp_monotonic, float)

    def test_default_metadata_is_empty_dict(self, drg):
        gw = drg.DeterministicRoutingGateway()
        artifact = gw.stamp_decision("standard_validation")
        assert artifact.metadata == {}

    def test_ledger_grows_with_each_stamp(self, drg):
        gw = drg.DeterministicRoutingGateway(policy_hash="pol")
        assert gw.ledger() == []
        gw.stamp_decision("standard_validation")
        gw.stamp_decision("human_escalation")
        gw.stamp_decision("low_risk_bypass")
        assert len(gw.ledger()) == 3
        assert [a.route_path for a in gw.ledger()] == [
            "standard_validation",
            "human_escalation",
            "low_risk_bypass",
        ]

    def test_ledger_returns_copy_not_reference(self, drg):
        gw = drg.DeterministicRoutingGateway()
        gw.stamp_decision("standard_validation")
        snapshot = gw.ledger()
        snapshot.clear()
        assert len(gw.ledger()) == 1  # internal unaffected

    def test_clear_ledger_empties(self, drg):
        gw = drg.DeterministicRoutingGateway()
        gw.stamp_decision("standard_validation")
        gw.stamp_decision("human_escalation")
        assert len(gw.ledger()) == 2
        gw.clear_ledger()
        assert gw.ledger() == []


# --------------------------------------------------------------------------- #
# verify_replay                                                               #
# --------------------------------------------------------------------------- #


class TestVerifyReplay:
    def test_true_when_replay_key_matches_compute_formula(self, drg):
        """verify_replay recomputes via _compute_replay_key; a hand-built
        artifact whose replay_key was generated that way must verify."""
        route, policy, trace = "standard_validation", "pol", "t-xyz"
        key = drg._compute_replay_key(route, policy, trace)
        artifact = drg.RoutingArtifact(
            trace_id=trace,
            replay_key=key,
            determinism_digest="0" * 32,
            route_path=route,
            policy_config_hash=policy,
            timestamp_monotonic=0.0,
            metadata={},
        )
        gw = drg.DeterministicRoutingGateway()
        assert gw.verify_replay(artifact) is True

    def test_false_when_replay_key_tampered(self, drg):
        key = drg._compute_replay_key("standard_validation", "pol", "t-1")
        # Guarantee the first char flips to a different hex digit
        flipped = ("0" if key[0] != "0" else "1") + key[1:]
        artifact = drg.RoutingArtifact(
            trace_id="t-1",
            replay_key=flipped,
            determinism_digest="0" * 32,
            route_path="standard_validation",
            policy_config_hash="pol",
            timestamp_monotonic=0.0,
            metadata={},
        )
        gw = drg.DeterministicRoutingGateway()
        assert gw.verify_replay(artifact) is False

    def test_false_when_route_path_tampered(self, drg):
        key = drg._compute_replay_key("standard_validation", "pol", "t-1")
        artifact = drg.RoutingArtifact(
            trace_id="t-1",
            replay_key=key,
            determinism_digest="0" * 32,
            route_path="human_escalation",  # changed after key was computed
            policy_config_hash="pol",
            timestamp_monotonic=0.0,
            metadata={},
        )
        gw = drg.DeterministicRoutingGateway()
        assert gw.verify_replay(artifact) is False


# --------------------------------------------------------------------------- #
# escalate_low_confidence_route                                               #
# --------------------------------------------------------------------------- #


class TestEscalateLowConfidence:
    @pytest.mark.parametrize("confidence", [0.5, 0.75, 0.9, 1.0])
    def test_returns_false_when_confidence_at_or_above_threshold(self, drg, confidence):
        gw = drg.DeterministicRoutingGateway()
        result = gw.escalate_low_confidence_route(
            route_path="standard_validation",
            confidence=confidence,
            threshold=0.5,
        )
        assert result is False

    def test_custom_threshold_respected(self, drg):
        gw = drg.DeterministicRoutingGateway()
        # 0.6 < 0.7 threshold -> would escalate; but 0.8 >= 0.7 should short-circuit
        assert (
            gw.escalate_low_confidence_route(
                "standard_validation",
                confidence=0.8,
                threshold=0.7,
            )
            is False
        )


# --------------------------------------------------------------------------- #
# get_routing_gateway / reset_routing_gateway                                 #
# --------------------------------------------------------------------------- #


class TestGlobalGateway:
    def test_returns_singleton(self, drg, fresh_gateway):
        a = drg.get_routing_gateway(policy_hash="pol")
        b = drg.get_routing_gateway()
        assert a is b

    def test_first_call_applies_policy_hash(self, drg, fresh_gateway):
        gw = drg.get_routing_gateway(policy_hash="first-policy")
        artifact = gw.stamp_decision("standard_validation")
        assert artifact.policy_config_hash == "first-policy"

    def test_reset_returns_new_instance(self, drg, fresh_gateway):
        a = drg.get_routing_gateway(policy_hash="pol-a")
        drg.reset_routing_gateway()
        b = drg.get_routing_gateway(policy_hash="pol-b")
        assert a is not b

    def test_reset_applies_new_policy(self, drg, fresh_gateway):
        drg.get_routing_gateway(policy_hash="pol-a")
        drg.reset_routing_gateway()
        gw = drg.get_routing_gateway(policy_hash="pol-b")
        artifact = gw.stamp_decision("standard_validation")
        assert artifact.policy_config_hash == "pol-b"


# --------------------------------------------------------------------------- #
# Public surface                                                              #
# --------------------------------------------------------------------------- #


class TestPublicSurface:
    def test_exports_present(self, drg):
        for name in (
            "RoutingArtifact",
            "DeterministicRoutingGateway",
            "get_routing_gateway",
            "reset_routing_gateway",
        ):
            assert name in drg.__all__, f"missing export: {name}"
