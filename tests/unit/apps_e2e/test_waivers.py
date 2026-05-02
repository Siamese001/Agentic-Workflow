"""Unit tests for waivers.py (W2.2)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from tools.certification.apps_e2e.app_specs import AppSpec
from tools.certification.apps_e2e.waivers import (
    is_waiver_valid,
    parse_iso_utc,
    waiver_required,
    waiver_violation_rule_id,
)


def _spec(**kw) -> AppSpec:
    base = dict(
        app_name="apps_test", app_package="apps_test",
        runnable=True, expected_route_form="UNKNOWN",
        expects_static_dag=False, expects_c0_grounding=False,
        expects_prompt_assembly=False, expects_l2_execution=False,
        expects_durable_mutation=False,
        runs_root_glob="artifacts/apps_test/runs/*",
    )
    base.update(kw)
    return AppSpec(**base)


def _future(years: int = 1) -> str:
    return (datetime.now(timezone.utc) + timedelta(days=365 * years)).isoformat().replace("+00:00", "Z")


class TestParseIsoUtc:
    def test_z_suffix(self):
        d = parse_iso_utc("2030-01-01T00:00:00Z")
        assert d == datetime(2030, 1, 1, tzinfo=timezone.utc)

    def test_explicit_offset(self):
        d = parse_iso_utc("2030-01-01T00:00:00+00:00")
        assert d == datetime(2030, 1, 1, tzinfo=timezone.utc)

    def test_naive_rejected(self):
        assert parse_iso_utc("2030-01-01T00:00:00") is None

    def test_garbage_rejected(self):
        assert parse_iso_utc("not-a-date") is None

    def test_empty_rejected(self):
        assert parse_iso_utc("") is None
        assert parse_iso_utc(None) is None


class TestWaiverRequired:
    def test_runnable_cert_required_does_not_need_waiver(self):
        assert waiver_required(_spec()) is False

    def test_skeleton_needs_waiver(self):
        assert waiver_required(_spec(runnable=False)) is True

    def test_non_certification_app_needs_waiver(self):
        assert waiver_required(_spec(certification_required=False)) is True


class TestIsWaiverValid:
    def test_full_triple_in_future_is_valid(self):
        s = _spec(
            runnable=False,
            waiver_reason="why", waiver_owner="who", waiver_expiry=_future(2),
        )
        assert is_waiver_valid(s) is True

    def test_missing_field_invalid(self):
        s = _spec(runnable=False, waiver_reason="why", waiver_owner="who")  # no expiry
        assert is_waiver_valid(s) is False

    def test_expired_invalid(self):
        s = _spec(
            runnable=False,
            waiver_reason="why", waiver_owner="who",
            waiver_expiry="2020-01-01T00:00:00Z",
        )
        assert is_waiver_valid(s) is False

    def test_unparseable_expiry_invalid(self):
        s = _spec(
            runnable=False,
            waiver_reason="why", waiver_owner="who",
            waiver_expiry="not-a-date",
        )
        assert is_waiver_valid(s) is False

    def test_now_parameter_overrides(self):
        s = _spec(
            runnable=False,
            waiver_reason="why", waiver_owner="who",
            waiver_expiry="2030-01-01T00:00:00Z",
        )
        assert is_waiver_valid(s, now=datetime(2025, 1, 1, tzinfo=timezone.utc)) is True
        assert is_waiver_valid(s, now=datetime(2031, 1, 1, tzinfo=timezone.utc)) is False


class TestWaiverViolationRuleId:
    def test_no_waiver_required_returns_none(self):
        assert waiver_violation_rule_id(_spec()) is None

    def test_required_but_incomplete(self):
        assert waiver_violation_rule_id(_spec(runnable=False)) == "waiver_incomplete"

    def test_required_but_unparseable(self):
        s = _spec(
            runnable=False,
            waiver_reason="why", waiver_owner="who",
            waiver_expiry="garbage",
        )
        assert waiver_violation_rule_id(s) == "waiver_expiry_unparseable"

    def test_required_but_expired(self):
        s = _spec(
            runnable=False,
            waiver_reason="why", waiver_owner="who",
            waiver_expiry="2020-01-01T00:00:00Z",
        )
        assert waiver_violation_rule_id(s) == "waiver_expired"

    def test_valid_returns_none(self):
        s = _spec(
            certification_required=False,
            waiver_reason="why", waiver_owner="who", waiver_expiry=_future(),
        )
        assert waiver_violation_rule_id(s) is None
