"""Unit tests for :mod:`system_learning.engines.eval_freshness_gate`."""

from __future__ import annotations

from pathlib import Path

import pytest

from system_learning.engines.eval_freshness_gate import (
    EvalFreshnessGate,
    FreshnessPolicy,
)


REPO_ROOT = Path(__file__).resolve().parents[4]


def _policy(**overrides) -> dict:
    base = {
        "version": 1,
        "schema": "test",
        "ttl_seconds": {
            "prompt": 3600.0,
            "documentation": None,
        },
        "default_on_unknown_class": "block",
        "fail_open": False,
        "fail_open_adr_ref": None,
    }
    base.update(overrides)
    return base


def test_fresh_within_ttl_not_blocked() -> None:
    gate = EvalFreshnessGate.from_mapping(_policy())
    decision = gate.check(change_class="prompt", eval_record_timestamp=1000.0, now=1500.0)
    assert decision.blocked is False
    assert decision.age_seconds == 500.0
    assert decision.ttl_seconds == 3600.0


def test_stale_beyond_ttl_blocked() -> None:
    gate = EvalFreshnessGate.from_mapping(_policy())
    decision = gate.check(change_class="prompt", eval_record_timestamp=1000.0, now=5000.0)
    assert decision.blocked is True
    assert decision.age_seconds == 4000.0
    assert "exceeds TTL" in decision.reason


def test_missing_eval_record_blocks_when_ttl_required() -> None:
    gate = EvalFreshnessGate.from_mapping(_policy())
    decision = gate.check(change_class="prompt", eval_record_timestamp=None, now=1000.0)
    assert decision.blocked is True
    assert "requires an eval record" in decision.reason


def test_null_ttl_class_is_exempt() -> None:
    gate = EvalFreshnessGate.from_mapping(_policy())
    decision = gate.check(change_class="documentation", eval_record_timestamp=None, now=1000.0)
    assert decision.blocked is False
    assert "exempt" in decision.reason


def test_unknown_class_default_block() -> None:
    gate = EvalFreshnessGate.from_mapping(_policy(default_on_unknown_class="block"))
    decision = gate.check(change_class="unknown_class", eval_record_timestamp=1000.0, now=1500.0)
    assert decision.blocked is True


def test_unknown_class_default_allow() -> None:
    gate = EvalFreshnessGate.from_mapping(_policy(default_on_unknown_class="allow"))
    decision = gate.check(change_class="unknown_class", eval_record_timestamp=1000.0, now=1500.0)
    assert decision.blocked is False


def test_unknown_class_default_warn_does_not_block() -> None:
    gate = EvalFreshnessGate.from_mapping(_policy(default_on_unknown_class="warn"))
    decision = gate.check(change_class="unknown_class", eval_record_timestamp=1000.0, now=1500.0)
    assert decision.blocked is False
    assert "warn" in decision.reason


def test_fail_open_overrides_block() -> None:
    gate = EvalFreshnessGate.from_mapping(_policy(fail_open=True, fail_open_adr_ref="ADR-999"))
    # Even with stale eval, fail_open lets the write through (with audit string).
    decision = gate.check(change_class="prompt", eval_record_timestamp=1.0, now=1e9)
    assert decision.blocked is False
    assert "fail_open" in decision.reason


def test_future_dated_eval_not_blocked() -> None:
    gate = EvalFreshnessGate.from_mapping(_policy())
    decision = gate.check(change_class="prompt", eval_record_timestamp=2000.0, now=1000.0)
    assert decision.blocked is False
    assert decision.age_seconds is not None and decision.age_seconds < 0


def test_load_real_policy_from_repo() -> None:
    gate = EvalFreshnessGate.from_repo(REPO_ROOT)
    # Smoke test: policy loads, canonical classes present.
    for change_class in ("prompt", "policy", "rubric", "documentation"):
        assert change_class in gate.policy.ttl_seconds


def test_invalid_default_raises() -> None:
    with pytest.raises(ValueError, match="default_on_unknown_class"):
        FreshnessPolicy.from_mapping(_policy(default_on_unknown_class="nonsense"))
