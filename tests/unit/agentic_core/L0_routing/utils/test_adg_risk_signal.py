"""Unit tests for agentic_core.L0_routing.utils.adg_risk_signal."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from unittest.mock import patch

import pytest

# Reuse the test fixture builder from the runtime_query tests.
from tests.unit.tools.adg.test_runtime_query import _build_fixture_db
from tools.adg.runtime_query import RuntimeADGQuery


@pytest.fixture()
def fake_default_query(tmp_path: Path):
    db = tmp_path / "adg_indexed_fixture.sqlite"
    _build_fixture_db(db)
    q = RuntimeADGQuery(sqlite_path=db)
    with patch(
        "agentic_core.L0_routing.utils.adg_risk_signal.get_default_query",
        return_value=q,
    ):
        yield q


def test_risk_signal_for_known_safety(fake_default_query):
    from agentic_core.L0_routing.utils.adg_risk_signal import risk_signal_for

    env = risk_signal_for("agentic_core.L5_safety.guardrail")
    assert env["available"] is True
    assert env["archetype"] == "SAFETY_GATEKEEPER"
    assert env["layer"] == "L5"


def test_risk_signal_for_unknown(fake_default_query):
    from agentic_core.L0_routing.utils.adg_risk_signal import risk_signal_for

    env = risk_signal_for("nothing.at.all")
    assert env["available"] is False
    assert env["risk_band"] == "LOW"


def test_risk_signal_returns_neutral_when_adg_unavailable(tmp_path):
    with patch(
        "agentic_core.L0_routing.utils.adg_risk_signal.get_default_query",
        return_value=None,
    ):
        from agentic_core.L0_routing.utils.adg_risk_signal import risk_signal_for

        env = risk_signal_for("anything")
        assert env["available"] is False
        assert env["archetype"] == "UNKNOWN"


def test_is_safety_critical(fake_default_query):
    from agentic_core.L0_routing.utils.adg_risk_signal import is_safety_critical

    assert is_safety_critical("agentic_core.L5_safety.guardrail") is True
    assert is_safety_critical("apps_shared.leaf_util") is False


def test_is_central_dependency(fake_default_query):
    from agentic_core.L0_routing.utils.adg_risk_signal import is_central_dependency

    assert is_central_dependency("n_central", min_fan_in=20) is True
    assert is_central_dependency("n_leaf", min_fan_in=20) is False
    # Missing node returns False, not an exception.
    assert is_central_dependency("does.not.exist") is False


def test_route_policy_hint_for_central(fake_default_query):
    from agentic_core.L0_routing.utils.adg_risk_signal import route_policy_hint

    hint = route_policy_hint("n_central")
    # With 25 fan-in and L0 multiplier 2.0, impact > RISK_BAND_HIGH (50) → HIGH band.
    assert hint["prefer_canary"] is True
    assert hint["require_hitl"] is True
    assert hint["circuit_breaker_armed"] is True
    assert "envelope" in hint


def test_route_policy_hint_for_leaf(fake_default_query):
    from agentic_core.L0_routing.utils.adg_risk_signal import route_policy_hint

    hint = route_policy_hint("n_leaf")
    assert hint["prefer_canary"] is False
    assert hint["require_hitl"] is False
    assert hint["circuit_breaker_armed"] is False


def test_route_policy_hint_for_safety(fake_default_query):
    from agentic_core.L0_routing.utils.adg_risk_signal import route_policy_hint

    hint = route_policy_hint("n_safety")
    # Safety gatekeeper always requires HITL regardless of fan-in.
    assert hint["require_hitl"] is True


def test_route_policy_hint_unavailable_falls_back():
    with patch(
        "agentic_core.L0_routing.utils.adg_risk_signal.get_default_query",
        return_value=None,
    ):
        from agentic_core.L0_routing.utils.adg_risk_signal import route_policy_hint

        hint = route_policy_hint("anything")
        assert hint["prefer_canary"] is False
        assert hint["require_hitl"] is False
        assert "ADG unavailable" in hint["rationale"]
