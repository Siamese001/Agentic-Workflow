"""Behavioral tests for ``agentic_core.L0_routing.enforcement.deterministic_replay_guard``.

Covers P0/L0 routing replay enforcement:
- DeterminismViolation inherits from RuntimeError.
- ReplayVerificationResult.mismatch_summary returns "PASS" or MISMATCH string.
- verify_routing_replay: passes through when gateway reports replay OK.
- fail_closed + replay_mode + failed replay → DeterminismViolation raised.
- fail_closed=False or replay_mode=False → no raise, returns result only.
- get_replay_guard singleton pattern; reset_replay_guard clears it.
"""

from __future__ import annotations

from collections.abc import Generator
from dataclasses import replace
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L0_routing.enforcement import deterministic_replay_guard as mod
from agentic_core.L0_routing.enforcement.deterministic_replay_guard import (
    DeterminismViolation,
    DeterministicReplayGuard,
    ReplayVerificationResult,
    get_replay_guard,
    reset_replay_guard,
)
from agentic_core.L0_routing.reasoning.deterministic_routing_gateway import (
    RoutingArtifact,
)


def _artifact(
    *,
    trace_id: str = "t-1",
    route_path: str = "D3",
    policy_config_hash: str = "ph-1",
    replay_key: str = "rk-1",
) -> RoutingArtifact:
    return RoutingArtifact(
        trace_id=trace_id,
        replay_key=replay_key,
        determinism_digest="dd-1",
        route_path=route_path,
        policy_config_hash=policy_config_hash,
        timestamp_monotonic=1000.0,
        metadata={},
    )


@pytest.fixture(autouse=True)
def _reset_singleton() -> Generator[None, None, None]:
    reset_replay_guard()
    yield
    reset_replay_guard()


# ---- Exception hierarchy ------------------------------------------------


class TestDeterminismViolation:
    def test_is_runtime_error(self) -> None:
        assert issubclass(DeterminismViolation, RuntimeError)

    def test_raise_and_catch(self) -> None:
        with pytest.raises(DeterminismViolation, match="diverge"):
            raise DeterminismViolation("replay diverged")


# ---- ReplayVerificationResult -------------------------------------------


class TestReplayVerificationResult:
    def test_pass_summary(self) -> None:
        r = ReplayVerificationResult(
            artifact=_artifact(),
            expected_replay_key="abc",
            actual_replay_key="abc",
            passed=True,
        )
        assert r.mismatch_summary == "PASS"

    def test_mismatch_summary_contains_keys(self) -> None:
        r = ReplayVerificationResult(
            artifact=_artifact(),
            expected_replay_key="expected-hash-long-value",
            actual_replay_key="actual-hash-long-value",
            passed=False,
        )
        summary = r.mismatch_summary
        # Source truncates each key to first 16 chars
        assert "MISMATCH" in summary
        assert "expected=expected-hash-lo" in summary
        assert "actual=actual-hash-long" in summary

    def test_is_frozen(self) -> None:
        r = ReplayVerificationResult(
            artifact=_artifact(),
            expected_replay_key="a",
            actual_replay_key="b",
            passed=False,
        )
        with pytest.raises(AttributeError):
            r.passed = True  # type: ignore[misc]


# ---- verify_routing_replay ----------------------------------------------


def _mock_gateway(verify_result: bool) -> MagicMock:
    gw = MagicMock()
    gw.verify_replay.return_value = verify_result
    gw.stamp_decision.return_value = None
    return gw


class TestVerifyRoutingReplay:
    def test_pass_through_when_gateway_reports_ok(self) -> None:
        guard = DeterministicReplayGuard(replay_mode=True)
        with patch.object(mod, "get_routing_gateway", return_value=_mock_gateway(True)):
            result = guard.verify_routing_replay(_artifact())
        assert result.passed is True
        assert result.actual_replay_key == "rk-1"

    def test_fail_closed_and_replay_mode_raises(self) -> None:
        guard = DeterministicReplayGuard(replay_mode=True)
        with patch.object(mod, "get_routing_gateway", return_value=_mock_gateway(False)):
            with pytest.raises(DeterminismViolation, match="trace_id=t-1"):
                guard.verify_routing_replay(_artifact(), fail_closed=True)

    def test_fail_closed_false_no_raise(self) -> None:
        guard = DeterministicReplayGuard(replay_mode=True)
        with patch.object(mod, "get_routing_gateway", return_value=_mock_gateway(False)):
            result = guard.verify_routing_replay(_artifact(), fail_closed=False)
        assert result.passed is False
        # No raise — caller can inspect and decide

    def test_replay_mode_false_no_raise_even_on_fail(self) -> None:
        guard = DeterministicReplayGuard(replay_mode=False)
        with patch.object(mod, "get_routing_gateway", return_value=_mock_gateway(False)):
            result = guard.verify_routing_replay(_artifact(), fail_closed=True)
        assert result.passed is False

    def test_gateway_stamp_called_with_metadata(self) -> None:
        guard = DeterministicReplayGuard(replay_mode=True)
        gw = _mock_gateway(True)
        with patch.object(mod, "get_routing_gateway", return_value=gw):
            guard.verify_routing_replay(_artifact(trace_id="T42", route_path="D2"))
        gw.stamp_decision.assert_called_once()
        call = gw.stamp_decision.call_args
        assert call.args[0] == "D2"
        assert call.kwargs["metadata"]["guard"] == "replay_verify"
        assert call.kwargs["metadata"]["trace_id"] == "T42"

    def test_get_routing_gateway_called_with_policy_hash(self) -> None:
        guard = DeterministicReplayGuard(replay_mode=False)
        with patch.object(
            mod,
            "get_routing_gateway",
            return_value=_mock_gateway(True),
        ) as mock_gw:
            guard.verify_routing_replay(_artifact(policy_config_hash="policy-xyz"))
        mock_gw.assert_called_once_with("policy-xyz")

    def test_expected_key_computed_from_artifact_fields(self) -> None:
        """expected_replay_key is sha256(route_path:policy:trace) — deterministic."""
        import hashlib

        a = _artifact(
            trace_id="trace-abc",
            route_path="D1",
            policy_config_hash="ph-42",
            replay_key="rk-custom",
        )
        expected = hashlib.sha256("D1:ph-42:trace-abc".encode()).hexdigest()
        guard = DeterministicReplayGuard(replay_mode=False)
        with patch.object(mod, "get_routing_gateway", return_value=_mock_gateway(True)):
            result = guard.verify_routing_replay(a)
        assert result.expected_replay_key == expected


# ---- get_replay_guard / reset_replay_guard ------------------------------


class TestSingleton:
    def test_returns_same_instance(self) -> None:
        g1 = get_replay_guard()
        g2 = get_replay_guard()
        assert g1 is g2
        assert isinstance(g1, DeterministicReplayGuard)

    def test_default_replay_mode_false(self) -> None:
        g = get_replay_guard()
        assert g.replay_mode is False

    def test_replay_mode_passed_on_first_call_only(self) -> None:
        # First call sets replay_mode; subsequent calls return same instance
        # regardless of the arg (documented singleton semantic).
        g1 = get_replay_guard(replay_mode=True)
        assert g1.replay_mode is True
        g2 = get_replay_guard(replay_mode=False)
        assert g2 is g1
        assert g2.replay_mode is True  # still the first value

    def test_reset_clears_singleton(self) -> None:
        g1 = get_replay_guard(replay_mode=True)
        reset_replay_guard()
        g2 = get_replay_guard(replay_mode=False)
        assert g2 is not g1
        assert g2.replay_mode is False
