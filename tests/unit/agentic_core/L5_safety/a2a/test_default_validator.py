"""Behavior tests for G05 DefaultA2AHandoffValidator (Wave A impl)."""

from __future__ import annotations

import pytest

from agentic_core.L5_safety.a2a import (
    DefaultA2AHandoffValidator,
    HandoffContext,
    default_validator,
)


def _ctx(**overrides) -> HandoffContext:
    base = {
        "source_agent": "planner",
        "target_agent": "executor",
        "user_identity": "user-42",
        "capability_token": "tok-abc",
        "risk_tier": "low",
        "payload_summary": "draft plan",
    }
    base.update(overrides)
    return HandoffContext(**base)


def test_validates_when_all_invariants_satisfied() -> None:
    v = DefaultA2AHandoffValidator(allowlist={"planner": frozenset({"executor"})})
    verdict = v.validate(_ctx())
    assert verdict.allowed is True
    assert verdict.reason_code == "ok"


def test_rejects_empty_user_identity() -> None:
    v = DefaultA2AHandoffValidator(allowlist={"planner": frozenset({"executor"})})
    verdict = v.validate(_ctx(user_identity=""))
    assert verdict.allowed is False
    assert verdict.reason_code == "identity_mismatch"


def test_rejects_empty_capability_token() -> None:
    v = DefaultA2AHandoffValidator(allowlist={"planner": frozenset({"executor"})})
    verdict = v.validate(_ctx(capability_token=""))
    assert verdict.allowed is False
    assert verdict.reason_code == "token_invalid"


def test_rejects_unknown_risk_tier() -> None:
    v = DefaultA2AHandoffValidator(allowlist={"planner": frozenset({"executor"})})
    verdict = v.validate(_ctx(risk_tier="bogus"))
    assert verdict.allowed is False
    assert verdict.reason_code == "tier_uplift"


def test_rejects_target_not_in_allowlist() -> None:
    v = DefaultA2AHandoffValidator(allowlist={"planner": frozenset({"executor"})})
    verdict = v.validate(_ctx(target_agent="rogue-agent"))
    assert verdict.allowed is False
    assert verdict.reason_code == "target_not_allowlisted"


def test_default_validator_is_fail_closed() -> None:
    """default_validator() with no allowlist denies everything."""
    v = default_validator()
    verdict = v.validate(_ctx())
    assert verdict.allowed is False
    assert verdict.reason_code == "target_not_allowlisted"


def test_unknown_source_agent_fails_closed() -> None:
    """Source not in allowlist → no targets → reject."""
    v = DefaultA2AHandoffValidator(allowlist={"planner": frozenset({"executor"})})
    verdict = v.validate(_ctx(source_agent="unknown-agent"))
    assert verdict.allowed is False
    assert verdict.reason_code == "target_not_allowlisted"


@pytest.mark.parametrize("tier", ["low", "medium", "high", "critical", "LOW", "Medium"])
def test_accepts_known_risk_tiers_case_insensitive(tier: str) -> None:
    v = DefaultA2AHandoffValidator(allowlist={"planner": frozenset({"executor"})})
    verdict = v.validate(_ctx(risk_tier=tier))
    assert verdict.allowed is True
